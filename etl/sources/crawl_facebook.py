

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
OCR_MODEL_DIR = r"D:\easyocr_models"
os.makedirs(OCR_MODEL_DIR, exist_ok=True)

try:
    import easyocr
    ocr = easyocr.Reader(["en", "vi"], gpu=False, model_storage_directory=OCR_MODEL_DIR)
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
OUTPUT_FILE = RAW_DIR / "facebook_raw.json"

CHROME_BINARY = r"D:\Chrome123\chrome-win64\chrome.exe"
CHROMEDRIVER_PATH = r"D:\Chrome123\chromedriver-win64\chromedriver.exe"
PROFILE_DIR = r"D:\Chrome123Profile"

SCROLL_DEPTH = 40
SCROLL_PAUSE = 2.0

FACEBOOK_GROUP_URLS = [
    "https://www.facebook.com/groups/326079906387736",
    "https://www.facebook.com/groups/268254096019827",
    "https://www.facebook.com/groups/168125343870460",
    "https://www.facebook.com/groups/1050470770063711",
    "https://www.facebook.com/groups/1526866181116301",
    "https://www.facebook.com/groups/1463249574120047",
    "https://www.facebook.com/groups/471329939373051",
    "https://www.facebook.com/groups/321901092553912",
    "https://www.facebook.com/groups/267969922194281",
    "https://www.facebook.com/groups/1984857118400127",
    "https://www.facebook.com/groups/1577974349381545",
    "https://www.facebook.com/groups/1298729557388152",
    "https://www.facebook.com/groups/796104498168541",
    "https://www.facebook.com/groups/Online10s",
    "https://www.facebook.com/groups/1677487326216814",
    "https://www.facebook.com/groups/1229692298297542",
    "https://www.facebook.com/groups/dautukiemtienantoan",
    "https://www.facebook.com/groups/1047886833563117",
    "https://www.facebook.com/groups/1159502885472456",
]


# ==========================================================
# REGEX + LOGIC CHUẨN
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

    phones = set()
    for p in PHONE_RE.findall(text):
        p = normalize_phone(p)
        if len(p) == 10 and p.startswith("0"):
            phones.add(p)

    banks = {
        b for b in BANK_RE.findall(text)
        if not b.startswith("0") and b not in phones
    }

    urls = set(URL_RE.findall(text))

    return sorted(phones), sorted(banks), sorted(urls)


# ==========================================================
# HASH (DEDUP CHUẨN)
# ==========================================================
def sha(s: str):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def content_hash(item):
    key = "|".join([
        item["source"],
        item["group"],
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
# CRAWL GROUP
# ==========================================================
def crawl_group(driver, url):
    driver.get(url + "?sorting_setting=CHRONOLOGICAL")
    time.sleep(6)

    results = []
    seen = set()

    last_height = 0
    for step in range(SCROLL_DEPTH):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE + random.uniform(0.5, 1.5))

        height = driver.execute_script("return document.body.scrollHeight")
        if height == last_height:
            break
        last_height = height

        posts = driver.find_elements(By.XPATH, "//div[@role='article']")

        for p in posts:
            try:
                text = p.text.strip()
                if not text:
                    continue

                phones, banks, urls = extract_entities(text)

                imgs = []
                ocr_texts = []

                # OCR CHỈ KHI TEXT KHÔNG CÓ ENTITY
                if not (phones or banks or urls):
                    imgs = [
                        i.get_attribute("src")
                        for i in p.find_elements(By.TAG_NAME, "img")
                        if i.get_attribute("src") and "emoji" not in i.get_attribute("src")
                    ][:3]
                    ocr_texts = [ocr_image_from_url(x) for x in imgs]
                    phones, banks, urls = extract_entities(
                        text + " " + " ".join(ocr_texts)
                    )

                if not (phones or banks or urls):
                    continue

                h = sha(text)
                if h in seen:
                    continue
                seen.add(h)

                results.append({
                    "source": "facebook",
                    "group": url,
                    "text": text,
                    "ocr_text": ocr_texts,
                    "images": imgs,
                    "phones": phones,
                    "banks": banks,
                    "urls": urls,
                    "created_at": datetime.utcnow().isoformat() + "Z",
                })

            except:
                continue

    return results


# ==========================================================
# SAVE JSON – CHỈ GHI DỮ LIỆU MỚI
# ==========================================================
def save_json(path, data):
    old = json.load(path.open("r", encoding="utf-8")) if path.exists() else []
    seen = {content_hash(item) for item in old}

    new_items = []
    for item in data:
        h = content_hash(item)
        if h not in seen:
            item["content_hash"] = h
            new_items.append(item)
            seen.add(h)

    merged = old + new_items

    with path.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Added {len(new_items)} new records (total: {len(merged)})")


# ==========================================================
# MAIN LOGIC
# ==========================================================

def crawl_facebook():
    driver = init_driver()
    all_data = []
    try:
        for url in FACEBOOK_GROUP_URLS:
            all_data.extend(crawl_group(driver, url))
    finally:
        driver.quit()

    save_json(OUTPUT_FILE, all_data)
    return all_data


# ==========================================================
# RUN FOR CRAWLER_ALL (ENTRY POINT CHUẨN)
# ==========================================================

def run():
    """
    Entry point cho crawler_all.py
    """
    return crawl_facebook()


if __name__ == "__main__":
    crawl_facebook()
