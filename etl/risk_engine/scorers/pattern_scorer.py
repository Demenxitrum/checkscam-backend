"""
pattern_scorer.py
=================

Nhiệm vụ:
- Nhận NormalizedRecord đã qua:
    validate.py
    pattern_rules.py
- Dựa trên:
    - rules_triggered
    - confidence (rule-based)
- Gán:
    - risk_score (0 → 100)
    - risk_level (SAFE / MEDIUM / HIGH)

Đây là tầng:
RULE-BASED INTELLIGENCE → ĐIỂM RỦI RO ĐỊNH LƯỢNG
"""

from typing import List

from etl.normalize.schema import NormalizedRecord, RiskLevel


# ==========================================================
# CONFIG – WEIGHT THEO RULE
# ==========================================================

# Mỗi rule đóng góp bao nhiêu điểm
RULE_WEIGHTS = {
    # PHONE
    "PHONE_1900": 30,
    "PHONE_SHORTCODE": 25,

    # BANK
    "BANK_REPEATED": 35,
    "BANK_SUSPICIOUS_PATTERN": 30,

    # URL
    "URL_DANGEROUS_DOMAIN": 40,
    "URL_SHORTENER": 20,
    "URL_SUSPICIOUS_TLD": 15,

    # TEXT / CONTEXT
    "SCAM_KEYWORD": 15,
}


# ==========================================================
# SCORE HELPERS
# ==========================================================

def calculate_base_score(rules_triggered: List[str]) -> int:
    """
    Tính điểm nền dựa trên rule bị kích hoạt
    """
    score = 0
    for rule in rules_triggered:
        score += RULE_WEIGHTS.get(rule, 10)  # default nhẹ nếu rule lạ
    return score


def apply_confidence(score: int, confidence: float | None) -> int:
    """
    Điều chỉnh score theo confidence (0 → 1)
    """
    if confidence is None:
        return score

    adjusted = int(score * confidence)
    return min(adjusted, 100)


def map_score_to_level(score: int) -> RiskLevel:
    """
    Map score → RiskLevel
    """
    if score >= 70:
        return RiskLevel.HIGH
    if score >= 40:
        return RiskLevel.MEDIUM
    if score > 0:
        return RiskLevel.SAFE
    return RiskLevel.UNKNOWN


# ==========================================================
# CORE SCORER
# ==========================================================

def score_record(record: NormalizedRecord) -> NormalizedRecord:
    """
    Chấm điểm 1 NormalizedRecord dựa trên pattern rules
    """

    # Nếu chưa có rule → không chấm
    rules = getattr(record, "rules_triggered", None)
    if not rules:
        record.risk_score = 0
        record.risk_level = RiskLevel.UNKNOWN
        return record

    # 1️⃣ base score từ rule
    base_score = calculate_base_score(rules)

    # 2️⃣ áp confidence
    final_score = apply_confidence(base_score, record.confidence)

    # 3️⃣ map level
    level = map_score_to_level(final_score)

    # 4️⃣ gán vào record
    record.risk_score = final_score
    record.risk_level = level

    return record


# ==========================================================
# BATCH SCORER
# ==========================================================

def score_records(records: List[NormalizedRecord]) -> List[NormalizedRecord]:
    """
    Chấm điểm hàng loạt record
    """
    return [score_record(r) for r in records]
