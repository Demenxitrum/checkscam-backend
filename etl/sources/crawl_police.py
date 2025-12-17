# ============================================================
# CRAWLER CÔNG AN – POLICE V2 (TỐI ƯU LẤY NHIỀU DỮ LIỆU NHẤT)
# ============================================================

import json
import re
import time
from pathlib import Path
from typing import List, Dict, Set
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup


# ================== CẤU HÌNH CHUNG ==========================

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)

GLOBAL_SEEN_FILE = DATA_DIR / "global_seen.json"
OUTPUT_FILE = DATA_DIR / "police_records.jsonl"

SOURCE_NAME = "police_vn"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "CheckScamCrawler/1.0 (+https://example.com)"
}

# Đào sâu hơn một chút nhưng vẫn an toàn
MAX_PAGES_VISITED = 700
MAX_ARTICLES_COLLECTED = 2500


# ================== TỪ KHÓA & REGEX =========================

SCAM_KEYWORDS = [
    "lừa đảo", "chiếm đoạt", "tội phạm", "cảnh báo",
    "điều tra", "khởi tố", "bắt giữ", "bắt tạm giam",
    "tạm giữ", "đường dây", "lừa qua mạng", "mạng xã hội",
    "mạo danh", "giả mạo", "tín dụng đen", "đa cấp",
    "công an cảnh báo", "cảnh sát", "phòng chống tội phạm",
    "rửa tiền", "giao dịch", "chuyển khoản", "tài khoản"
]

BANK_KEYWORDS = [
    "tài khoản", "số tài khoản", "stk", "ngân hàng",
    "chủ tài khoản", "tk ngân hàng"
]

BANK_REGEX = re.compile(r"\b\d{9,16}\b")
PHONE_VN_REGEX = re.compile(r"\b0[2-9]\d{7,9}\b")
PHONE_INT_REGEX = re.compile(r"\+\d{7,15}")
URL_REGEX = re.compile(r"https?://\S+", re.IGNORECASE)

# Hạn chế crawler chỉ ở đúng các chuyên mục pháp luật / tội phạm
DOMAIN_VALID_PATH_KEYWORDS = {
    "cand.com.vn": [
        "phap-luat", "thong-tin-phap-luat", "an-ninh-mang", "toi-pham"
    ],
    "bocongan.gov.vn": [
        "tin-tuc", "tin-tuc-su-kien", "tin-an-ninh-trat-tu", "canh-bao"
    ],
    "anninhthudo.vn": [
        "vu-an", "phap-luat", "dieu-tra", "luat-su-tu-van"
    ],
    "baovephapluat.vn": [
        "phap-luat", "bao-ve-phap-luat", "phong-chong-toi-pham"
    ],
    "phapluat.suckhoedoisong.vn": [
        "phong-chong-toi-pham", "phong-chong"
    ],
}


# ================== TIỆN ÍCH ================================

def now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def load_seen() -> Set[str]:
    if GLOBAL_SEEN_FILE.exists():
        try:
            return set(json.loads(GLOBAL_SEEN_FILE.read_text(encoding="utf-8")))
        except Exception:
            return set()
    return set()


def save_seen(seen: Set[str]):
    GLOBAL_SEEN_FILE.write_text(
        json.dumps(sorted(list(seen)), ensure_ascii=False),
        encoding="utf-8"
    )


def fetch(url: str) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except Exception as e:
        print(f"[POLICE] Lỗi tải {url}: {e}")
        return ""


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def contains_any(text: str, keywords: List[str]) -> bool:
    lower = text.lower()
    return any(k in lower for k in keywords)


# ================== NHẬN DIỆN BÀI BÁO =======================

def looks_like_article(path: str, full_url: str) -> bool:
    p = path.lower()

    # bỏ trang search / filter
    if any(x in full_url.lower() for x in ["search", "tim-kiem", "?q=", "tag="]):
        return False

    # 1. Đuôi chuẩn bài báo
    if any(p.endswith(ext) for ext in [".html", ".htm"]):
        return True

    # 2. Có pattern ngày tháng
    if re.search(r"/20\d{2}/\d{1,2}/\d{1,2}/", p):
        return True

    # 3. Có ID ở cuối
    if re.search(r"-\d{4,10}$", p):
        return True

    # 4. Slug dài, nhiều dấu gạch
    if p.count("-") >= 2 and len(p) > 20:
        return True

    return False


def path_allowed_for_domain(domain: str, path: str) -> bool:
    path = path.lower()
    if domain not in DOMAIN_VALID_PATH_KEYWORDS:
        # nếu chưa cấu hình thì cho phép
        return True
    allowed_keywords = DOMAIN_VALID_PATH_KEYWORDS[domain]
    return any(k in path for k in allowed_keywords)


# ================== EXTRACT ENTITY ==========================

def extract_entities(text: str, url: str) -> List[Dict]:
    records: List[Dict] = []

    # URL
    for m in URL_REGEX.findall(text):
        val = m.strip().rstrip(").,;")
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

    # PHONE quốc tế
    for m in PHONE_INT_REGEX.findall(text):
        if len(m) >= 4:
            records.append({
                "source": SOURCE_NAME,
                "url": url,
                "type": "PHONE",
                "value": m,
                "context": m,
                "country": "INT",
                "risk_level": "HIGH",
                "created_at": now_iso(),
            })

    # PHONE/BANK theo từng đoạn
    paragraphs = re.split(r"\n+", text)
    for para in paragraphs:
        para_norm = normalize(para)
        if not para_norm:
            continue

        # chỉ xét đoạn có từ khóa liên quan tội phạm / lừa đảo
        if not contains_any(para_norm, SCAM_KEYWORDS):
            continue

        # BANK
        for b in BANK_REGEX.findall(para_norm):
            if contains_any(para_norm, BANK_KEYWORDS):
                records.append({
                    "source": SOURCE_NAME,
                    "url": url,
                    "type": "BANK",
                    "value": b,
                    "context": para_norm[:500],
                    "country": "VN",
                    "risk_level": "HIGH",
                    "created_at": now_iso(),
                })

        # PHONE Việt Nam
        for ph in PHONE_VN_REGEX.findall(para_norm):
            records.append({
                "source": SOURCE_NAME,
                "url": url,
                "type": "PHONE",
                "value": ph,
                "context": para_norm[:500],
                "country": "VN",
                "risk_level": "HIGH",
                "created_at": now_iso(),
            })

    return records


# ================== THU THẬP LINK (BFS) =====================

def collect_article_urls() -> List[str]:
    """
    BFS từ các chuyên mục pháp luật / tội phạm của:
      - Bộ Công an
      - Báo Công an Nhân dân
      - An ninh Thủ đô
      - Báo Bảo vệ Pháp luật
      - Chuyên mục phòng chống tội phạm
    Ưu tiên giữ link có từ khóa scam hoặc thuộc path pháp luật.
    """

    SEED_PAGES = [
        # Bộ Công an
        "https://bocongan.gov.vn/tin-tuc-su-kien.html",
        "https://bocongan.gov.vn/tin-tuc-su-kien.html?Tag=l%E1%BB%ABa%20%C4%91%E1%BA%A3o",

        # Báo Công an Nhân dân
        "https://cand.com.vn/Phap-luat/",
        "https://cand.com.vn/Thong-tin-phap-luat/",
        "https://cand.com.vn/An-ninh-mang/",

        # An ninh Thủ đô
        "https://anninhthudo.vn/vu-an.html",
        "https://anninhthudo.vn/phap-luat.html",

        # Báo bảo vệ pháp luật
        "https://baovephapluat.vn/phap-luat/bao-ve-phap-luat/",
        "https://baovephapluat.vn/phap-luat/phong-chong-toi-pham/",

        # Chuyên mục phòng chống tội phạm
        "https://phapluat.suckhoedoisong.vn/phong-chong-toi-pham.htm",
    ]

    visited: Set[str] = set()
    queue: List[str] = list(dict.fromkeys(SEED_PAGES))
    article_urls: Set[str] = set()

    print(f"[POLICE] Seed ban đầu: {len(queue)} trang")

    while queue and len(visited) < MAX_PAGES_VISITED and len(article_urls) < MAX_ARTICLES_COLLECTED:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)

        print(f"[POLICE] Đang duyệt: {current}")
        html = fetch(current)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")
        parsed = urlparse(current)
        base = f"{parsed.scheme}://{parsed.netloc}"

        # Nếu bản thân URL hiện tại là bài báo
        if looks_like_article(parsed.path, current) and path_allowed_for_domain(parsed.netloc, parsed.path):
            article_urls.add(current)

        for a in soup.find_all("a", href=True):
            href = a["href"]

            if href.startswith("//"):
                url_abs = parsed.scheme + ":" + href
            elif href.startswith("/"):
                url_abs = urljoin(base, href)
            elif href.startswith("http"):
                url_abs = href
            else:
                url_abs = urljoin(base + "/", href)

            parsed_href = urlparse(url_abs)

            if parsed_href.netloc != parsed.netloc:
                continue

            # chỉ giữ link thuộc đúng chuyên mục pháp luật / tội phạm
            if not path_allowed_for_domain(parsed_href.netloc, parsed_href.path):
                continue

            link_text = (a.get_text(strip=True) or "").lower()
            haystack = link_text + " " + url_abs.lower()

            keep_link = False
            if contains_any(haystack, SCAM_KEYWORDS):
                keep_link = True
            elif looks_like_article(parsed_href.path, url_abs):
                keep_link = True

            if not keep_link:
                continue

            if looks_like_article(parsed_href.path, url_abs):
                article_urls.add(url_abs)

            if url_abs not in visited and url_abs not in queue:
                queue.append(url_abs)

        time.sleep(0.3)

    print(f"[POLICE] Số trang đã duyệt: {len(visited)}")
    print(f"[POLICE] Tổng bài báo thu được: {len(article_urls)}")
    return sorted(article_urls)


# ================== PARSE 1 BÀI =============================

def parse_article(url: str) -> List[Dict]:
    html = fetch(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    full_text = soup.get_text(separator="\n", strip=True)
    return extract_entities(full_text, url)


# ================== HÀM CHÍNH ===============================

def crawl_police() -> List[Dict]:
    seen = load_seen()
    new_records: List[Dict] = []

    urls = collect_article_urls()

    with OUTPUT_FILE.open("a", encoding="utf-8") as f_out:
        for url in urls:
            print(f"[POLICE] Crawling: {url}")
            entities = parse_article(url)

            for e in entities:
                key = f"{e['type']}:{e['value']}".lower()
                if key in seen:
                    continue

           

                seen.add(key)
                new_records.append(e)
                f_out.write(json.dumps(e, ensure_ascii=False) + "\n")

            save_seen(seen)
            time.sleep(0.5)

    print(f"[POLICE] Tổng record mới: {len(new_records)}")
    return new_records
# ==========================================================
# RUN FOR CRAWLER_ALL (ENTRY POINT CHUẨN)
# ==========================================================

def run():
    """
    Entry point cho crawler_all.py
    """
    return crawl_police()


if __name__ == "__main__":
    crawl_police()
