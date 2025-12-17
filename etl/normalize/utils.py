# etl/normalize/utils.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Tuple
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

# =========================
# Regex nền tảng
# =========================

# VN phone: 0xxxxxxxxx (10 số) hoặc 0xxxxxxxxxx (11 số - một số đầu số cũ)
_VN_PHONE_DIGITS_RE = re.compile(r"^(0\d{9,10})$")

# quốc tế dạng +xxxxxxxx (7..15)
_INT_PHONE_RE = re.compile(r"^\+\d{7,15}$")

# Bank account: chỉ digits, VN thường 8..17 (tuỳ ngân hàng)
_BANK_DIGITS_RE = re.compile(r"^\d{8,17}$")

# URL: chấp nhận http/https + domain có dấu chấm
_URL_SCHEME_RE = re.compile(r"^https?://", re.IGNORECASE)
_DOMAIN_HAS_DOT_RE = re.compile(r"\.")  # netloc có dấu chấm là tối thiểu


# =========================
# Helper: clean text
# =========================
def _strip_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def _only_digits(s: str) -> str:
    return re.sub(r"\D+", "", (s or ""))


# =========================
# 1) normalize_phone
# =========================
def normalize_phone(raw: str) -> Optional[str]:
    """
    Chuẩn hoá SĐT về dạng VN chuẩn:
      - Nếu raw là +84xxxxxxxxx -> đổi thành 0xxxxxxxxx
      - Xoá ký tự: space, dot, dash, (, ), ...
      - Kết quả: '0' + 9/10 digits (10 hoặc 11 số), ưu tiên 10 số.
    Trả về:
      - phone chuẩn (string) hoặc None nếu không hợp lệ.
    """
    if not raw:
        return None

    s = _strip_spaces(raw)

    # Giữ dấu '+' nếu có, còn lại bỏ hết ký tự thừa
    # VD: "(+84) 912-345-678" -> "+84912345678"
    s = s.replace("(", "").replace(")", "")
    s = s.replace(".", "").replace("-", "").replace(" ", "")
    s = s.replace("\u200b", "")  # zero-width space nếu có

    # Nếu bắt đầu bằng 84 (không có '+') đôi khi user viết "84912..."
    if s.startswith("84") and len(s) >= 9 and not s.startswith("+"):
        s = "+" + s

    # +84xxxx -> 0xxxx
    if s.startswith("+84"):
        digits = _only_digits(s)  # "84912345678"
        # đổi 84xxxx thành 0xxxx
        s = "0" + digits[2:]

    # Lúc này phải là digits
    digits = _only_digits(s)

    # Bắt buộc bắt đầu bằng 0
    if not digits.startswith("0"):
        return None

    # VN: 10 hoặc 11 số (tuỳ đầu số cũ)
    if _VN_PHONE_DIGITS_RE.match(digits):
        # Nếu 11 số nhưng bắt đầu 01x (đầu số rất cũ) vẫn cho qua
        return digits

    return None


# =========================
# 2) normalize_bank
# =========================
def normalize_bank(raw: str) -> Optional[str]:
    if not raw:
        return None

    digits = _only_digits(raw)

    # ✅ PHƯƠNG ÁN 2: ƯU TIÊN PHONE
    # nếu giống phone VN thì KHÔNG coi là bank
    if _VN_PHONE_DIGITS_RE.match(digits):
        return None

    # chỉ loại nếu quá ngắn hoặc quá dài
    if len(digits) < 8 or len(digits) > 17:
        return None

    return digits

# =========================
# 3) normalize_url
# =========================
_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "igshid", "mc_cid", "mc_eid",
}

def normalize_url(raw: str) -> Optional[str]:
    """
    Chuẩn hoá URL:
      - Thêm scheme nếu thiếu (mặc định https://)
      - lowercase domain
      - bỏ fragment (#...)
      - bỏ tracking query (utm_*, fbclid, gclid...)
      - bỏ trailing slash (trừ root '/')
    Trả về:
      - url chuẩn hoặc None nếu không hợp lệ.
    """
    if not raw:
        return None

    s = _strip_spaces(raw).strip(".,;:)]}\"'")  # bỏ dấu câu dính cuối
    s = s.replace("\u200b", "")

    # Nếu thiếu scheme: example.com/path -> https://example.com/path
    if not _URL_SCHEME_RE.match(s):
        s = "https://" + s

    try:
        p = urlparse(s)
    except Exception:
        return None

    # validate scheme
    if p.scheme.lower() not in ("http", "https"):
        return None

    # validate netloc
    netloc = (p.netloc or "").strip().lower()
    if not netloc or not _DOMAIN_HAS_DOT_RE.search(netloc):
        return None

    # remove default ports
    if netloc.endswith(":80") and p.scheme.lower() == "http":
        netloc = netloc[:-3]
    if netloc.endswith(":443") and p.scheme.lower() == "https":
        netloc = netloc[:-4]

    # clean path
    path = p.path or "/"
    # bỏ double slashes trong path
    path = re.sub(r"/{2,}", "/", path)

    # clean query: remove tracking
    query_pairs = parse_qsl(p.query, keep_blank_values=True)
    query_pairs = [(k, v) for (k, v) in query_pairs if k.lower() not in _TRACKING_PARAMS]
    query = urlencode(query_pairs, doseq=True)

    # remove fragment
    fragment = ""

    # strip trailing slash (trừ root)
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    normalized = urlunparse((p.scheme.lower(), netloc, path, p.params, query, fragment))
    return normalized


# =========================
# 4) detect_country
# =========================
def detect_country(entity_type: str, normalized_value: str) -> str:
    """
    Suy ra country:
      - PHONE: nếu bắt đầu 0 -> VN, nếu + -> INT
      - URL: nếu domain .vn -> VN else INT
      - BANK: mặc định VN (vì bạn đang nhắm hệ VN; sau mở rộng thì đổi)
    """
    t = (entity_type or "").upper().strip()
    v = (normalized_value or "").strip()

    if t == "PHONE":
        if v.startswith("0"):
            return "VN"
        if v.startswith("+"):
            return "INT"
        return "UNKNOWN"

    if t == "URL":
        try:
            netloc = urlparse(v).netloc.lower()
        except Exception:
            return "UNKNOWN"
        return "VN" if netloc.endswith(".vn") else "INT"

    if t == "BANK":
        return "VN"

    return "UNKNOWN"


# =========================
# 5) normalize_entity (wrapper dùng chung)
# =========================
def normalize_entity(entity_type: str, raw_value: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Wrapper chuẩn hoá theo type.
    Trả về (normalized_value, country) hoặc (None, None) nếu fail.
    """
    t = (entity_type or "").upper().strip()

    if t == "PHONE":
        nv = normalize_phone(raw_value)
        return (nv, detect_country("PHONE", nv)) if nv else (None, None)

    if t == "BANK":
        nv = normalize_bank(raw_value)
        return (nv, detect_country("BANK", nv)) if nv else (None, None)

    if t == "URL":
        nv = normalize_url(raw_value)
        return (nv, detect_country("URL", nv)) if nv else (None, None)

    return (None, None)


# =========================
# 6) (Optional) validate quick helpers
# =========================
def is_valid_phone(normalized_phone: str) -> bool:
    return bool(normalized_phone and _VN_PHONE_DIGITS_RE.match(normalized_phone))


def is_valid_bank(normalized_bank: str) -> bool:
    return bool(normalized_bank and _BANK_DIGITS_RE.match(normalized_bank))


def is_valid_url(normalized_url: str) -> bool:
    if not normalized_url:
        return False
    try:
        p = urlparse(normalized_url)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False
