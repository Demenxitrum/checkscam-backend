# crawl_news.py
import json
import re
import time
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

# ============================================================
# CẤU HÌNH THƯ MỤC LƯU DATA
# ============================================================
DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)

GLOBAL_SEEN_FILE = DATA_DIR / "global_seen.json"
OUTPUT_FILE = DATA_DIR / "news_records.jsonl"

SOURCE_NAME = "news_vn"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CheckScamCrawler/1.0"
}

# ============================================================
# TĂNG GIỚI HẠN BFS CHO BẢN B (~1000 RECORD)
# ============================================================
MAX_PAGES_VISITED = 900
MAX_ARTICLES_COLLECTED = 3500

# ============================================================
# TỪ KHÓA LIÊN QUAN LỪA ĐẢO (MỞ RỘNG)
# ============================================================
SCAM_KEYWORDS = [
    "lừa đảo", "lừa gạt", "giả mạo", "giả danh", "mạo danh",
    "cảnh báo", "chiếm đoạt", "tín dụng đen", "đe dọa", "tống tiền",
    "tài khoản", "ngân hàng", "số điện thoại", "cuộc gọi",
    "chuyển khoản", "hack", "đánh cắp", "gọi điện",
    "mất tiền", "đa cấp", "đầu tư", "forex",
    "lừa qua mạng", "chiếm đoạt tài sản"
]

BANK_KEYWORDS = [
    "tài khoản", "số tài khoản", "stk", "ngân hàng",
    "chủ tài khoản", "tk ngân hàng"
]

PHONE_KEYWORDS = [
    "số điện thoại", "điện thoại", "đầu số",
    "cuộc gọi", "tin nhắn", "hotline", "tổng đài"
]

TRUSTED_SECTION_DOMAINS = {
    "ncsc.gov.vn",
    "bocongan.gov.vn",
    "cand.com.vn",
    "mic.gov.vn",
    "ais.gov.vn",
}

# ============================================================
# REGEX TỐI ƯU BẮT BANK / PHONE / URL
# ============================================================
GENERIC_NUMBER_REGEX = re.compile(r"\b\d{7,16}\b")
INT_PHONE_REGEX = re.compile(r"\+\d{7,15}")

URL_REGEX = re.compile(
    r"\b((?:https?://)?(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})(/[^\s]*)?\b"
)

# ============================================================
# TIỆN ÍCH
# ============================================================
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def load_seen() -> Set[str]:
    if GLOBAL_SEEN_FILE.exists():
        try:
            return set(json.loads(GLOBAL_SEEN_FILE.read_text(encoding="utf-8")))
        except Exception:
            return set()
    return set()

def save_seen(seen: Set[str]) -> None:
    GLOBAL_SEEN_FILE.write_text(
        json.dumps(sorted(list(seen)), ensure_ascii=False),
        encoding="utf-8",
    )

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def contains_any(text: str, keywords: List[str]) -> bool:
    lower = text.lower()
    return any(k in lower for k in keywords)

# ============================================================
# PHÂN LOẠI SỐ DỰA TRÊN CONTEXT
# ============================================================
def classify_number(num: str, context: str) -> str:
    ctx = context.lower()

    if contains_any(ctx, BANK_KEYWORDS):
        return "BANK"

    if contains_any(ctx, PHONE_KEYWORDS):
        return "PHONE"

    if num.startswith(("1900", "1800")):
        return "PHONE"

    if num.startswith("02"):
        return "PHONE"

    if num.startswith(("03", "05", "07", "08", "09")) and len(num) >= 9:
        return "PHONE"

    if len(num) >= 12:
        return "BANK"

    if 9 <= len(num) <= 11:
        return "PHONE"

    return "PHONE"

# ============================================================
# TRÍCH XUẤT THỰC THỂ TỪ BÀI BÁO
# ============================================================
def extract_entities(text: str, url: str) -> List[Dict]:
    records: List[Dict] = []

    # URL
    for m in URL_REGEX.finditer(text):
        val = m.group(0)
        records.append({
            "source": SOURCE_NAME,
            "url": url,
            "type": "URL",
            "value": val,
            "context": val,
            "country": "VN",
            "risk_level": "HIGH",
            "created_at": now_iso(),
        })

    # Số điện thoại quốc tế
    for m in INT_PHONE_REGEX.finditer(text):
        val = m.group(0)
        records.append({
            "source": SOURCE_NAME,
            "url": url,
            "type": "PHONE",
            "value": val,
            "context": val,
            "country": "INT",
            "risk_level": "HIGH",
            "created_at": now_iso(),
        })

    # BANK / PHONE theo context
    paragraphs = re.split(r"\n+", text)

    for para in paragraphs:
        para_norm = normalize(para)
        if not para_norm:
            continue

        nums = GENERIC_NUMBER_REGEX.findall(para_norm)
        for num in nums:
            t = classify_number(num, para_norm)
            records.append({
                "source": SOURCE_NAME,
                "url": url,
                "type": t,
                "value": num,
                "context": para_norm[:500],
                "country": "VN",
                "risk_level": "HIGH" if contains_any(para_norm, SCAM_KEYWORDS) else "MEDIUM",
                "created_at": now_iso(),
            })

    return records

# ============================================================
# TẢI TRANG HTML
# ============================================================
def fetch(url: str) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except Exception as e:
        print(f"[NEWS] Lỗi tải {url}: {e}")
        return ""

# ============================================================
# HEURISTIC NHẬN DIỆN BÀI BÁO (NÂNG CẤP)
# ============================================================
def looks_like_article(path: str, full_url: str) -> bool:
    p = path.lower()

    if any(x in full_url.lower() for x in ["search", "tim-kiem", "tag=", "q="]):
        return False

    # 1. Đuôi báo
    if any(p.endswith(ext) for ext in [".html", ".htm", ".chn"]):
        return True

    # 2. Pattern YYYY/MM/DD
    if re.search(r"/20\d{2}/\d{1,2}/\d{1,2}/", p):
        return True

    # 3. Slug có ID
    if re.search(r"-\d{4,10}$", p):
        return True

    # 4. URL dài + nhiều dấu "-"
    if p.count("-") >= 3 and len(p) > 20:
        return True

    return False

# ============================================================
# BFS – THU THẬP ARTICLE URL
# ============================================================
def collect_article_urls() -> List[str]:
    seed_pages = [

        # 3 bài CafeF bạn đưa
        "https://cafef.vn/cach-nhan-biet-trang-web-lua-dao-188230903094844746.chn",
        "https://cafef.vn/danh-sach-50-so-dien-thoai-lua-dao-moi-tuyet-doi-khong-nen-nghe-goi-lai-188241002083851606.chn",
        "https://cafef.vn/danh-sach-cac-tai-khoan-ngan-hang-lua-dao-chuyen-tien-188240926165306991.chn",

        # Cơ quan nhà nước
        "https://ncsc.gov.vn/tin-tuc/canh-bao",
        "https://bocongan.gov.vn/tin-tuc-su-kien.html",
        "https://cand.com.vn/search?q=lừa%20đảo",
        "https://mic.gov.vn/Pages/TinTuc.aspx",
        "https://ais.gov.vn/tin-tuc",

        # Báo lớn
        "https://vnexpress.net/tag/lua-dao-850961",
        "https://vietnamnet.vn/lua-dao-tag-12277269572304495193.html",
        "https://tuoitre.vn/canh-bao-lua-dao.html",
        "https://thanhnien.vn/tim-kiem?q=lừa%20đảo",
        "https://dantri.com.vn/tim-kiem/lừa%20đảo.htm",
        "https://cafef.vn/tim-kiem/từ-khóa/lừa-đảo.htm",
        "https://laodong.vn/tags/lua-dao-81236.ldo",
        "https://plo.vn/search?q=lừa%20đảo",
        "https://congthuong.vn/tim-kiem?q=lừa%20đảo",
        "https://vtc.vn/tim-kiem?q=lừa%20đảo",
    ]

    queue = list(dict.fromkeys(seed_pages))
    visited_pages: Set[str] = set()
    article_urls: Set[str] = set()

    print(f"[NEWS] Seed ban đầu: {len(queue)} trang")

    while queue and len(visited_pages) < MAX_PAGES_VISITED and len(article_urls) < MAX_ARTICLES_COLLECTED:
        current = queue.pop(0)
        if current in visited_pages:
            continue

        visited_pages.add(current)
        print(f"[NEWS] Đang duyệt trang: {current}")

        html = fetch(current)
        if not html:
            continue

        parsed = urlparse(current)
        domain = parsed.netloc
        base = f"{parsed.scheme}://{parsed.netloc}"

        soup = BeautifulSoup(html, "html.parser")

        # Nếu chính URL là bài báo
        if looks_like_article(parsed.path, current):
            article_urls.add(current)

        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = (a.get_text(strip=True) or "").lower()

            # Chuẩn hóa URL
            if href.startswith("//"):
                url_abs = parsed.scheme + ":" + href
            elif href.startswith("/"):
                url_abs = urljoin(base, href)
            elif href.startswith("http"):
                url_abs = href
            else:
                url_abs = urljoin(base + "/", href)

            parsed_href = urlparse(url_abs)

            if parsed_href.netloc != domain:
                continue

            haystack = text + " " + url_abs.lower()

            # QUY TẮC GIỮ LINK
            if domain in TRUSTED_SECTION_DOMAINS:
                keep_link = True
            else:
                if contains_any(haystack, SCAM_KEYWORDS):
                    keep_link = True
                elif looks_like_article(parsed_href.path, url_abs):
                    keep_link = True
                else:
                    keep_link = False

            if not keep_link:
                continue

            # Nếu là bài báo
            if looks_like_article(parsed_href.path, url_abs):
                article_urls.add(url_abs)

            # BFS tiếp
            if url_abs not in visited_pages and url_abs not in queue:
                queue.append(url_abs)

        time.sleep(0.4)

    print(f"[NEWS] Số trang đã duyệt: {len(visited_pages)}")
    print(f"[NEWS] Tổng số bài báo thu được: {len(article_urls)}")
    return sorted(article_urls)

# ============================================================
# PHÂN TÍCH 1 BÀI BÁO
# ============================================================
def parse_article(url: str) -> List[Dict]:
    html = fetch(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    full_text = soup.get_text(separator="\n", strip=True)
    return extract_entities(full_text, url)

# ============================================================
# HÀM CHÍNH
# ============================================================
def crawl_news() -> List[Dict]:
    seen = load_seen()
    new_records: List[Dict] = []

    article_urls = collect_article_urls()

    with OUTPUT_FILE.open("a", encoding="utf-8") as f_out:
        for url in article_urls:
            print(f"[NEWS] Crawling article: {url}")
            entities = parse_article(url)

            for e in entities:
                key = f"{e['type']}:{e['value']}".lower()
                if key in seen:
                    continue

                seen.add(key)
                new_records.append(e)
                f_out.write(json.dumps(e, ensure_ascii=False) + "\n")

            save_seen(seen)
            time.sleep(0.8)

    print(f"[NEWS] Tổng record mới: {len(new_records)}")
    return new_records
# ==========================================================
# RUN FOR CRAWLER_ALL (ENTRY POINT CHUẨN)
# ==========================================================

def run():
    """
    Entry point cho crawler_all.py
    """
    return crawl_news()


if __name__ == "__main__":
    crawl_news()
