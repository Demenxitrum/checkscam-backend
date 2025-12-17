import re

# =========================================================
# REGEX CHUẨN VIỆT NAM
# =========================================================

# PHONE: 0xxx / +84xxx, cho phép dấu cách, dấu chấm
PHONE_RE = re.compile(
    r"(?:\+?84|0)(?:3|5|7|8|9)[0-9\.\-\s]{7,12}"
)

# BANK: 12–18 số LIÊN TỤC, KHÔNG bắt đầu bằng 0
BANK_RE = re.compile(
    r"\b[1-9][0-9]{11,17}\b"
)

# URL
URL_RE = re.compile(
    r"https?://[^\s\"'>]+"
)


# =========================================================
# NORMALIZE
# =========================================================
def normalize_phone(phone: str) -> str:
    phone = phone.replace(".", "").replace(" ", "").replace("-", "")
    if phone.startswith("+84"):
        phone = "0" + phone[3:]
    return phone


# =========================================================
# MAIN EXTRACT
# =========================================================
def extract_entities(text: str):
    """
    Trả về:
    - phones: list[str]
    - banks: list[str]
    - urls: list[str]

    Đảm bảo:
    - PHONE ≠ BANK
    - BANK không bị nhận nhầm số điện thoại
    """

    if not text:
        return [], [], []

    text = text.replace("\n", " ")

    # -------- PHONE --------
    phones = set()
    for p in PHONE_RE.findall(text):
        p = normalize_phone(p)
        if len(p) == 10 and p.startswith("0"):
            phones.add(p)

    # -------- BANK --------
    banks = set()
    for b in BANK_RE.findall(text):
        if not b.startswith("0") and b not in phones:
            banks.add(b)

    # -------- URL --------
    urls = set(URL_RE.findall(text))

    return sorted(phones), sorted(banks), sorted(urls)
