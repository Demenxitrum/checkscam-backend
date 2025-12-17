"""
pattern_rules.py
================

Nhiệm vụ:
- Áp dụng các RULE DÒ TÌM DẤU HIỆU LỪA ĐẢO (rule-based)
- Gán risk_level, risk_score, confidence
- Ghi nhận evidence (rule nào kích hoạt)

⚠️ File này:
- KHÔNG crawl
- KHÔNG normalize
- KHÔNG ghi DB
- KHÔNG quyết định cuối cùng

👉 Chỉ phân tích dựa trên pattern rõ ràng
"""

from typing import List, Dict, Any
from collections import defaultdict

from etl.normalize.schema import (
    NormalizedRecord,
    EntityType,
    RiskLevel,
)

# ==========================================================
# RULE CONFIG
# ==========================================================

# PHONE
SUSPICIOUS_PHONE_PREFIXES = {
    "1900", "1800",   # tổng đài thu phí
    "024", "028",     # đầu số cố định hay giả mạo
}

# URL
SUSPICIOUS_URL_KEYWORDS = {
    "login", "verify", "secure", "account", "bank",
    "update", "confirm", "wallet", "payment"
}

SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl"
}

# BANK
BANK_SCAM_KEYWORDS = {
    "chuyển khoản", "chiếm đoạt", "phong tỏa",
    "hoàn tiền", "lừa đảo", "mạo danh"
}


# ==========================================================
# CORE RULE ENGINE
# ==========================================================

def apply_pattern_rules(
    records: List[NormalizedRecord],
) -> List[NormalizedRecord]:
    """
    Áp dụng rule-based detection cho danh sách record
    """

    # dùng để phát hiện entity xuất hiện nhiều nguồn
    entity_sources: Dict[str, set] = defaultdict(set)

    for r in records:
        entity_sources[r.hash].add(r.source)

    for record in records:
        rules_triggered: List[str] = []
        score = 0

        # ==================================================
        # PHONE RULES
        # ==================================================
        if record.entity_type == EntityType.PHONE:
            value = record.entity_value

            # Rule 1: đầu số đáng ngờ
            if any(value.startswith(p) for p in SUSPICIOUS_PHONE_PREFIXES):
                rules_triggered.append("PHONE_SUSPICIOUS_PREFIX")
                score += 40

            # Rule 2: xuất hiện từ nhiều nguồn
            if len(entity_sources[record.hash]) >= 2:
                rules_triggered.append("PHONE_MULTI_SOURCE")
                score += 30

        # ==================================================
        # BANK RULES
        # ==================================================
        elif record.entity_type == EntityType.BANK:
            context = (record.context or "").lower()

            # Rule 3: từ khóa lừa đảo trong ngữ cảnh
            if any(k in context for k in BANK_SCAM_KEYWORDS):
                rules_triggered.append("BANK_SUSPICIOUS_CONTEXT")
                score += 50

            # Rule 4: xuất hiện nhiều nguồn
            if len(entity_sources[record.hash]) >= 2:
                rules_triggered.append("BANK_MULTI_SOURCE")
                score += 30

        # ==================================================
        # URL RULES
        # ==================================================
        elif record.entity_type == EntityType.URL:
            value = record.entity_value.lower()

            # Rule 5: URL chứa keyword nhạy cảm
            if any(k in value for k in SUSPICIOUS_URL_KEYWORDS):
                rules_triggered.append("URL_SUSPICIOUS_KEYWORD")
                score += 40

            # Rule 6: URL rút gọn
            if any(d in value for d in SHORTENER_DOMAINS):
                rules_triggered.append("URL_SHORTENER")
                score += 30

            # Rule 7: URL xuất hiện nhiều nguồn
            if len(entity_sources[record.hash]) >= 2:
                rules_triggered.append("URL_MULTI_SOURCE")
                score += 30

        # ==================================================
        # GÁN KẾT QUẢ
        # ==================================================
        if score >= 70:
            record.risk_level = RiskLevel.HIGH
        elif score >= 30:
            record.risk_level = RiskLevel.MEDIUM
        else:
            record.risk_level = RiskLevel.SAFE

        record.risk_score = min(score, 100)

        # confidence đơn giản (rule-based)
        record.confidence = min(1.0, 0.4 + 0.1 * len(rules_triggered))

        # ghi evidence
        record.evidence = record.evidence or {}
        record.evidence["rules_triggered"] = rules_triggered

    return records


# ==========================================================
# ENTRY (DÙNG TRONG PIPELINE – KHÔNG CHẠY ĐƠN LẺ)
# ==========================================================

def run(records: List[NormalizedRecord]) -> List[NormalizedRecord]:
    """
    Entry point cho pipeline giai đoạn 2
    """
    return apply_pattern_rules(records)
