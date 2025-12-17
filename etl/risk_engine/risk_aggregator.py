# etl/risk_engine/risk_aggregator.py

"""
Risk Aggregation Layer – FINAL
------------------------------
Layer 1: Base risk (nền, không bao giờ = 0)
Layer 2: Frequency-based
Layer 3: Source credibility
Layer 4: Report đã duyệt (human-verified signal)

Sinh ra:
- risk_score (0–100)
- risk_level (SAFE | MEDIUM | HIGH)
- confidence (0.0 – 1.0)

Explainable – đúng chuẩn Anti-Fraud System
"""

from etl.normalize.schema import NormalizedRecord, RiskLevel


# ==========================================================
# CONFIG
# ==========================================================

BASE_RISK = 10

MAX_FREQ_SCORE = 25
MAX_SOURCE_SCORE = 60
MAX_REPORT_SCORE = 40


SOURCE_CREDIBILITY = {
    "facebook": 5,
    "tiktok": 5,
    "news": 15,
    "ncsc": 25,
    "police": 35,
    "phishtank": 40,
    "user_report": 20,
}


def aggregate_risk(record: NormalizedRecord) -> None:
    """
    Tổng hợp rủi ro cho 1 entity đã được aggregate ở main.py
    """

    score = BASE_RISK

    # ======================================================
    # Layer 2 – Frequency
    # ======================================================
    freq = getattr(record, "frequency", 1)
    freq_score = min(MAX_FREQ_SCORE, freq * 2)
    score += freq_score

    # ======================================================
    # Layer 3 – Source Credibility
    # ======================================================
    sources = getattr(record, "sources", {record.source})

    source_score = 0
    for src in sources:
        source_score += SOURCE_CREDIBILITY.get(src, 5)

    source_score = min(MAX_SOURCE_SCORE, source_score)
    score += source_score

    # ======================================================
    # Layer 4 – Report đã duyệt (CORE)
    # ======================================================
    stats = getattr(record, "report_stats", {}) or {}

    approved = stats.get("approved", 0)
    pending = stats.get("pending", 0)

    # Report duyệt là tín hiệu MẠNH
    report_score = min(
        MAX_REPORT_SCORE,
        approved * 15 + pending * 5
    )

    score += report_score

    # ======================================================
    # FINAL SCORE
    # ======================================================
    record.risk_score = min(100, score)

    # ======================================================
    # RISK LEVEL
    # ======================================================
    if record.risk_score >= 70:
        record.risk_level = RiskLevel.HIGH
    elif record.risk_score >= 40:
        record.risk_level = RiskLevel.MEDIUM
    else:
        record.risk_level = RiskLevel.SAFE

    # ======================================================
    # CONFIDENCE (Explainable)
    # ======================================================
    record.confidence = round(
        min(1.0, (freq_score + source_score + report_score) / 100),
        2
    )
