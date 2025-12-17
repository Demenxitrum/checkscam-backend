# ============================================================
#   CRAWL NCSC (tinnhiemmang.vn) – FULL POWER VERSION
#   - BFS sâu trong toàn bộ site tinnhiemmang.vn
#   - Thu tối đa URL / PHONE / BANK (không bỏ sót)
#   - Chỉ lưu bản ghi mới nhờ global_seen.json
# ============================================================

import json
import re
import time
import random
from pathlib import Path
from typing import List, Dict, Set
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

# ================== CẤU HÌNH ===============================

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)
GLOBAL_SEEN_FILE = DATA_DIR / "global_seen.json"
OUTPUT_FILE = DATA_DIR / "ncsc_records.jsonl"

SOURCE_NAME = "ncsc_vn"

USER_AGENTS = [
    # Bạn có thể thêm UA khác nếu muốn
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]

ALLOWED_DOMAINS = {"tinnhiemmang.vn", "www.tinnhiemmang.vn"}

MAX_PAGES_VISITED = 600   # số trang HTML tối đa duyệt (BFS)
MAX_ARTICLES = 3000       # số bài tối đa parse chi tiết

REQUEST_TIMEOUT = 10
CRAWL_DELAY = 0.2         # delay nhẹ để tránh bị chặn

# ================== KEYWORDS & REGEX =======================

SCAM_KEYWORDS = [
    "lừa đảo", "cảnh báo", "phishing", "giả mạo", "mạo danh",
    "chiếm đoạt", "tấn công", "hack", "fraud", "scam"
]

BANK_KEYWORDS = [
    "tài khoản", "stk", "ngân hàng",
    "số tài khoản", "chủ tài khoản", "tk ngân hàng"
]

BANK_REGEX = re.compile(r"\b\d{9,17}\b")
PHONE_VN_REGEX = re.compile(r"\b0[1-9]\d{8,9}\b")
PHONE_INT_REGEX = re.compile(r"\+\d{7,15}")
URL_REGEX = re.compile(
    r"https?://[a-zA-Z0-9\-\._~:/\?#\[\]@!\$&'\(\)\*\+,;=%]+",
    re.IGNORECASE,
)

INVALID_URL_PATTERNS = [
    "github[", "youtube[", "custom-report-example",
    "sharp\\icons", "deployment\\"
]

# ================== TIỆN ÍCH ===============================

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


def get_headers() -> Dict[str, str]:
    ua = random.choice(USER_AGENTS)
    return {"User-Agent": ua}


def fetch(url: str) -> str:
    try:
        resp = requests.get(url, headers=get_headers(), timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return resp.text
    except Exception as e:
        print(f"[NCSC] Lỗi tải {url}: {e}")
        return ""


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def contains_any(text: str, keywords: List[str]) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in keywords)


def clean_url(url: str) -> str:
    # loại bỏ ký tự thừa ở cuối
    url = url.strip()
    url = url.rstrip(".,;:\"'[]() ")
    return url


def is_valid_url(url: str) -> bool:
    if not url.startswith("http"):
        return False
    if any(bad in url for bad in INVALID_URL_PATTERNS):
        return False
    # domain phải có ít nhất 1 dấu chấm
    try:
        parsed = urlparse(url)
        if "." not in parsed.netloc:
            return False
    except Exception:
        return False
    return True


# ================== NHẬN DIỆN BÀI / CATEGORY ===============

def looks_like_article(path: str) -> bool:
    """
    Heuristic nhận diện 1 URL là bài chi tiết/case lừa đảo
    hoặc profile tổ chức trong 'danh-ba-tin-nhiem'.
    """
    p = path.lower()

    # loại file tài liệu
    if p.endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx")):
        return False

    # các path chắc chắn là bài hoặc profile
    if any(seg in p for seg in [
        "/canh-bao-lua-dao",
        "/website-lua-dao",
        "/danh-ba-tin-nhiem/",
        "/dau-tu-vao-du-an-gia-mao",
        "/tin-tuc/",
        "/su-kien/",
    ]):
        return True

    # slug dài, nhiều dấu gạch
    slug = p.rstrip("/").split("/")[-1]
    if slug.count("-") >= 3 and len(slug) > 25:
        return True

    return False


def looks_like_category(path: str) -> bool:
    """
    Heuristic nhận diện trang danh mục để BFS sâu.
    """
    p = path.lower()

    if any(seg in p for seg in [
        "/canh-bao",
        "/canh-bao-lua-dao",
        "/danh-ba-tin-nhiem",
        "/danh-cho-to-chuc",
        "/danh-cho-nguoi-dung",
        "/tin-tuc",
        "/su-kien",
        "/page/",
        "/tag/",
        "/chuyen-muc",
    ]):
        return True

    # path ngắn, không phải file, dùng làm danh mục
    slug = p.rstrip("/")
    if slug and not slug.endswith((".html", ".htm")) and slug.count("/") <= 3:
        return True

    return False


# ================== EXTRACT ENTITIES =======================

def extract_entities_from_sentence(sentence: str) -> List[Dict]:
    s = normalize_text(sentence)
    if not s:
        return []

    entities: List[Dict] = []

    # BANK (nếu câu có từ khoá ngân hàng)
    if contains_any(s, BANK_KEYWORDS):
        for value in BANK_REGEX.findall(s):
            entities.append({
                "type": "BANK",
                "value": value,
                "context": s,
                "country": "VN",
                "risk_level": "HIGH",
            })

    # PHONE VN
    for value in PHONE_VN_REGEX.findall(s):
        entities.append({
            "type": "PHONE",
            "value": value,
            "context": s,
            "country": "VN",
            "risk_level": "HIGH" if "lừa đảo" in s.lower() else "MEDIUM",
        })

    # PHONE INT
    for value in PHONE_INT_REGEX.findall(s):
        if len(value) > 4:
            entities.append({
                "type": "PHONE",
                "value": value,
                "context": s,
                "country": "INT",
                "risk_level": "HIGH",
            })

    # URL
    for raw in URL_REGEX.findall(s):
        url_clean = clean_url(raw)
        if is_valid_url(url_clean):
            entities.append({
                "type": "URL",
                "value": url_clean,
                "context": s,
                "country": "VN",
                "risk_level": "HIGH",
            })

    return entities


def extract_entities_from_text(full_text: str) -> List[Dict]:
    """
    FULL POWER: phân tích *toàn bộ* văn bản, không chỉ câu có từ 'lừa đảo'.
    Vì tinnhiemmang.vn còn có 'danh-ba-tin-nhiem' chứa nhiều PHONE/URL hữu ích.
    """
    records: List[Dict] = []
    # Tách câu đơn giản: xuống dòng + dấu câu lớn
    parts = re.split(r"[\.!\?\n]+", full_text)
    for sent in parts:
        sent = sent.strip()
        if not sent:
            continue
        entities = extract_entities_from_sentence(sent)
        records.extend(entities)
    return records


# ================== BFS COLLECT URL ========================

SEED_PAGES = [
    "https://tinnhiemmang.vn/",
    "https://tinnhiemmang.vn/canh-bao-lua-dao",
    "https://tinnhiemmang.vn/canh-bao",
    "https://tinnhiemmang.vn/danh-ba-tin-nhiem",
    "https://tinnhiemmang.vn/danh-cho-to-chuc",
    "https://tinnhiemmang.vn/danh-cho-nguoi-dung",
    "https://tinnhiemmang.vn/tin-tuc",
]


def collect_article_urls() -> List[str]:
    visited: Set[str] = set()
    queue: List[str] = list(dict.fromkeys(SEED_PAGES))  # giữ thứ tự, bỏ trùng
    article_urls: Set[str] = set()

    while queue and len(visited) < MAX_PAGES_VISITED and len(article_urls) < MAX_ARTICLES:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)

        print(f"[NCSC] Đang duyệt: {current}")
        html = fetch(current)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")
        parsed = urlparse(current)
        base = f"{parsed.scheme}://{parsed.netloc}"

        # Nếu trang hiện tại đã giống bài chi tiết
        if parsed.netloc.lower() in ALLOWED_DOMAINS and looks_like_article(parsed.path):
            article_urls.add(current)

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()

            # chuẩn hoá absolute URL
            if href.startswith("//"):
                abs_url = parsed.scheme + ":" + href
            elif href.startswith("/"):
                abs_url = urljoin(base, href)
            elif href.startswith("http"):
                abs_url = href
            else:
                abs_url = urljoin(base + "/", href)

            parsed_abs = urlparse(abs_url)
            domain = parsed_abs.netloc.lower()
            path = parsed_abs.path or "/"

            if domain not in ALLOWED_DOMAINS:
                continue

            # bỏ file tài liệu
            if path.lower().endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx")):
                continue

            # URL có dấu hiệu scam trong chính URL
            if any(kw in abs_url.lower() for kw in [
                "lua-dao", "gia-mao", "phishing", "canh-bao", "website-lua-dao"
            ]):
                article_urls.add(abs_url)

            # anchor text có từ khoá scam
            text = a.get_text(strip=True)
            if contains_any(text, SCAM_KEYWORDS):
                article_urls.add(abs_url)

            # path giống bài chi tiết
            if looks_like_article(path):
                article_urls.add(abs_url)

            # path giống danh mục → cho vào queue để BFS sâu
            if looks_like_category(path):
                if abs_url not in visited and abs_url not in queue:
                    queue.append(abs_url)

        time.sleep(CRAWL_DELAY)

    print(f"[NCSC] Số trang đã duyệt: {len(visited)}")
    print(f"[NCSC] Tổng bài thu được: {len(article_urls)}")
    return sorted(article_urls)


# ================== PARSE 1 BÀI ============================

def parse_article(url: str) -> List[Dict]:
    html = fetch(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    full_text = soup.get_text(separator="\n", strip=True)
    entities = extract_entities_from_text(full_text)
    for e in entities:
        e["source"] = SOURCE_NAME
        e["url"] = url
        e["created_at"] = now_iso()
    return entities


# ================== HÀM CHÍNH ==============================

def crawl_ncsc() -> List[Dict]:
    seen = load_seen()
    new_records: List[Dict] = []

    urls = collect_article_urls()

    with OUTPUT_FILE.open("a", encoding="utf-8") as f_out:
        for url in urls:
            print(f"[NCSC] Crawling: {url}")
            entities = parse_article(url)

            for e in entities:
                key = f"{e['type']}:{e['value']}".lower()
                if key in seen:
                    continue  # ĐÃ CÓ → BỎ
                seen.add(key)
                new_records.append(e)
                f_out.write(json.dumps(e, ensure_ascii=False) + "\n")

            save_seen(seen)
            time.sleep(CRAWL_DELAY)

    print(f"[NCSC] Tổng record mới: {len(new_records)}")
    return new_records
# ==========================================================
# RUN FOR CRAWLER_ALL (ENTRY POINT CHUẨN)
# ==========================================================

def run():
    """
    Entry point cho crawler_all.py
    """
    return crawl_ncsc()


if __name__ == "__main__":
    crawl_ncsc()
