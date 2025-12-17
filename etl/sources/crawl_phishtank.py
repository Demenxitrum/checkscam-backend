# ============================
# PHISHTANK CRAWLER - FULL POWER VERSION
# ============================

import csv
import json
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Set, Optional

import requests

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)

GLOBAL_SEEN_FILE = DATA_DIR / "global_seen.json"
OUTPUT_FILE = DATA_DIR / "phishtank_records.jsonl"

PHISHTANK_CSV_URL = "https://data.phishtank.com/data/online-valid.csv"
PHISHTANK_DETAIL_URL = "https://phishtank.org/phish_detail.php?phish_id={id}"

SOURCE_NAME = "phishtank"

PHONE_REGEX = re.compile(r"(\+?\d{7,15})")
BANK_REGEX = re.compile(r"\b\d{9,14}\b")   # STK VN
BIN_REGEX = re.compile(r"\b\d{6}\b")      # BIN bank


# ----------------------------------------------
# LOAD / SAVE SEEN FINGERPRINTS
# ----------------------------------------------
def load_seen() -> Set[str]:
    if GLOBAL_SEEN_FILE.exists():
        try:
            return set(json.loads(GLOBAL_SEEN_FILE.read_text(encoding="utf-8")))
        except:
            return set()
    return set()


def save_seen(seen: Set[str]) -> None:
    GLOBAL_SEEN_FILE.write_text(
        json.dumps(sorted(list(seen)), ensure_ascii=False),
        encoding="utf-8"
    )


# ----------------------------------------------
# HASH FINGERPRINT
# ----------------------------------------------
def fingerprint(record: Dict) -> str:
    raw = f"{record['type']}|{record['value']}|{record.get('country','INT')}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ----------------------------------------------
# URL NORMALIZATION
# ----------------------------------------------
def normalize_url(url: str) -> str:
    url = url.strip()

    # lowercase domain
    parts = url.split("://", 1)
    if len(parts) == 2:
        scheme, rest = parts
        rest = rest.lower()
        url = f"{scheme}://{rest}"

    # remove trailing slash
    if url.endswith("/"):
        url = url[:-1]

    return url


# ----------------------------------------------
# COUNTRY DETECTION
# ----------------------------------------------
def detect_country(url: str) -> str:
    url = url.lower()
    if ".vn" in url:
        return "VN"
    return "INT"


# ----------------------------------------------
# DOWNLOAD CSV
# ----------------------------------------------
def download_csv() -> Optional[Path]:
    dest = DATA_DIR / "phishtank_online_valid.csv"
    try:
        print("[PHISHTANK] Đang tải CSV...")
        resp = requests.get(PHISHTANK_CSV_URL, timeout=30)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
        print(f"[PHISHTANK] Đã lưu CSV tại {dest}")
        return dest
    except Exception as e:
        print(f"[PHISHTANK] Lỗi tải CSV: {e}")
        return dest if dest.exists() else None


# ----------------------------------------------
# PARSE CSV
# ----------------------------------------------
def parse_csv(path: Path) -> List[Dict]:
    records = []
    if not path.exists():
        print("[PHISHTANK] CSV không tồn tại.")
        return records

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            url = normalize_url(row.get("url") or "")

            if not url:
                continue

            country = detect_country(url)

            rec = {
                "source": SOURCE_NAME,
                "type": "URL",
                "value": url,
                "url": url,
                "risk_level": "HIGH",
                "country": country,
                "meta": {
                    "phish_id": row.get("phish_id"),
                    "detail": row.get("phish_detail_url")
                }
            }
            records.append(rec)

    print(f"[PHISHTANK] Đã parse {len(records)} URL.")
    return records


# ----------------------------------------------
# MAIN CRAWLER
# ----------------------------------------------
def crawl_phishtank() -> List[Dict]:
    seen = load_seen()
    csv_path = download_csv()
    if not csv_path:
        return []

    parsed = parse_csv(csv_path)
    new_records = []

    with OUTPUT_FILE.open("a", encoding="utf-8") as out:
        for rec in parsed:
            fp = fingerprint(rec)

            if fp in seen:
                continue

            seen.add(fp)
            new_records.append(rec)
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")

    save_seen(seen)
    print(f"[PHISHTANK] Tổng record mới: {len(new_records)}")
    return new_records
# ==========================================================
# RUN FOR CRAWLER_ALL (ENTRY POINT CHUẨN)
# ==========================================================

def run():
    """
    Entry point cho crawler_all.py
    """
    return crawl_phishtank()


if __name__ == "__main__":
    crawl_phishtank()

