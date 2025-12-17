"""
TikTok OCR Video V6 – Selenium (Production)
- Fetch video thật bằng Selenium
- OCR thumbnail
- Phân biệt PHONE / BANK / URL
- Dedup chuẩn production
"""

import json
import os
import re
import time
import hashlib
import tempfile
import random
from datetime import datetime
from pathlib import Path

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# ==========================================================
# OCR (EN + VI)
# ==========================================================
try:
    import easyocr
    ocr = easyocr.Reader(["en", "vi"], gpu=False)
    OCR_ENABLED = True
except:
    OCR_ENABLED = False


def ocr_image_from_url(url: str) -> str:
    if not OCR_ENABLED or not url:
        return ""
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(r.content)
            path = f.name
        text = ocr.readtext(path, detail=0)
        os.remove(path)
        return " ".join(text)
    except:
        return ""


# ==========================================================
# CONFIG
# ==========================================================
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "storage" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = RAW_DIR / "tiktok_raw.json"

CHROME_BINARY = r"D:\Chrome123\chrome-win64\chrome.exe"
CHROMEDRIVER_PATH = r"D:\Chrome123\chromedriver-win64\chromedriver.exe"
PROFILE_DIR = r"D:\Chrome123Profile"

SCROLL_DEPTH = 25
SCROLL_PAUSE = 1.8

KEYWORDS = [
    "lừa đảo",
    "scam",
    "fraud",
    "số điện thoại lừa đảo",
    "stk lừa đảo",
    "chuyển khoản lừa đảo",
    "1900 lừa đảo",
    "024 lừa đảo",
    "028 lừa đảo",
    "mạo danh công an",
    "mạo danh ngân hàng",
]

# ==========================================================
# REGEX (GIỐNG FACEBOOK – CHUẨN)
# ==========================================================
PHONE_RE = re.compile(r"(?:\+?84|0)(?:3|5|7|8|9)[0-9\.\-\s]{7,12}")
BANK_RE = re.compile(r"\b[1-9][0-9]{11,17}\b")
URL_RE = re.compile(r"https?://[^\s\"'>]+")


def normalize_phone(p: str):
    p = p.replace(".", "").replace(" ", "").replace("-", "")
    if p.startswith("+84"):
        p = "0" + p[3:]
    return p


def extract_entities(text: str):
    if not text:
        return [], [], []

    text = text.replace("\n", " ")

    phones = {
        normalize_phone(p)
        for p in PHONE_RE.findall(text)
        if len(normalize_phone(p)) == 10
    }

    banks = {
        b for b in BANK_RE.findall(text)
        if not b.startswith("0") and b not in phones
    }

    urls = set(URL_RE.findall(text))
    return sorted(phones), sorted(banks), sorted(urls)


# ==========================================================
# DEDUP HASH
# ==========================================================
def sha(s: str):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def content_hash(item):
    key = "|".join([
        item["video_url"],
        ",".join(item["phones"]),
        ",".join(item["banks"]),
        ",".join(item["urls"]),
    ])
    return sha(key)


# ==========================================================
# DRIVER
# ==========================================================
def init_driver():
    opts = Options()
    opts.binary_location = CHROME_BINARY
    opts.add_argument(f"--user-data-dir={PROFILE_DIR}")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--start-maximized")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(CHROMEDRIVER_PATH),
        options=opts
    )

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"},
    )
    return driver


# ==========================================================
# FETCH VIDEOS BY KEYWORD (SELENIUM)
# ==========================================================
def fetch_videos_by_keyword(driver, keyword):
    print(f"[INFO] TikTok keyword: {keyword}")

    url = f"https://www.tiktok.com/search?q={keyword.replace(' ', '%20')}"
    driver.get(url)
    time.sleep(5)

    videos = {}
    last_height = 0

    for _ in range(SCROLL_DEPTH):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE + random.uniform(0.5, 1.2))

        height = driver.execute_script("return document.body.scrollHeight")
        if height == last_height:
            break
        last_height = height

        cards = driver.find_elements(By.XPATH, "//a[contains(@href,'/video/')]")
        for c in cards:
            try:
                href = c.get_attribute("href")
                if not href or "/video/" not in href:
                    continue
                videos[href] = True
            except:
                continue

    print(f"[DEBUG] Found {len(videos)} video URLs")
    return list(videos.keys())


# ==========================================================
# CRAWL VIDEO DETAIL
# ==========================================================
def crawl_video(driver, video_url):
    try:
        driver.get(video_url)
        time.sleep(4)

        text = ""
        try:
            text = driver.find_element(By.XPATH, "//div[contains(@data-e2e,'browse-video-desc')]").text
        except:
            pass

        img_url = ""
        try:
            img_url = driver.find_element(By.XPATH, "//img").get_attribute("src")
        except:
            pass

        phones, banks, urls = extract_entities(text)

        ocr_text = ""
        if not (phones or banks or urls) and img_url:
            ocr_text = ocr_image_from_url(img_url)
            phones, banks, urls = extract_entities(text + " " + ocr_text)

        if not (phones or banks or urls):
            return None

        return {
            "source": "tiktok",
            "video_url": video_url,
            "caption": text,
            "ocr_text": ocr_text,
            "thumbnail": img_url,
            "phones": phones,
            "banks": banks,
            "urls": urls,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
    except:
        return None


# ==========================================================
# SAVE JSON (CHỈ GHI MỚI)
# ==========================================================
def save_json(path, data):
    old = json.load(open(path, "r", encoding="utf-8")) if path.exists() else []
    seen = {content_hash(x) for x in old}

    new_items = []
    for item in data:
        h = content_hash(item)
        if h not in seen:
            item["content_hash"] = h
            new_items.append(item)
            seen.add(h)

    merged = old + new_items
    json.dump(merged, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[INFO] Added {len(new_items)} records (total: {len(merged)})")


def main():
    driver = init_driver()
    collected = []

    try:
        for kw in KEYWORDS:
            video_urls = fetch_videos_by_keyword(driver, kw)
            for v in video_urls:
                item = crawl_video(driver, v)
                if item:
                    collected.append(item)
    finally:
        driver.quit()

    save_json(OUTPUT_FILE, collected)
    return collected

def run():
    """
    Entry point cho crawler_all.py
    """
    return main()

if __name__ == "__main__":
    main()
