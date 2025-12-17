"""
ai_risk.py
==========

Nhiệm vụ:
- Nhận NormalizedRecord đã qua:
    normalize
    validate
    pattern_rules
    pattern_scorer
    trust_score
- Phân tích NGỮ CẢNH (context / evidence) ở mức AI / heuristic
- Điều chỉnh:
    - risk_score
    - confidence
    - (optional) risk_level

LƯU Ý:
- File này KHÔNG thay thế rule-based
- CHỈ tinh chỉnh kết quả cuối
- Có thể bật / tắt trong RiskEngine
"""

from typing import Optional

from etl.normalize.schema import NormalizedRecord, RiskLevel


# ==========================================================
# CONFIG
# ==========================================================

# Ngưỡng AI tác động
AI_SCORE_BOOST_HIGH = 20
AI_SCORE_BOOST_MEDIUM = 10
AI_SCORE_PENALTY_LOW = -10

# Confidence mặc định khi AI can thiệp
AI_CONFIDENCE_HIGH = 0.9
AI_CONFIDENCE_MEDIUM = 0.7


# ==========================================================
# SIMPLE AI HEURISTIC (SAFE FOR DATN)
# ==========================================================

def analyze_context_with_ai(record: NormalizedRecord) -> Optional[str]:
    """
    Phân tích ngữ cảnh bằng heuristic / AI giả lập

    Trả về:
    - "HIGH"
    - "MEDIUM"
    - "LOW"
    - None nếu không đủ dữ liệu
    """

    text = (record.context or "").lower()

    if not text:
        return None

    # RẤT NGUY HIỂM
    high_signals = [
        "lừa đảo",
        "chiếm đoạt",
        "mạo danh công an",
        "mạo danh ngân hàng",
        "chuyển tiền gấp",
        "khóa tài khoản",
        "đe dọa",
        "khẩn cấp",
    ]

    # ĐÁNG NGỜ
    medium_signals = [
        "liên hệ",
        "xác minh",
        "hỗ trợ",
        "trúng thưởng",
        "đầu tư",
        "cam kết lợi nhuận",
    ]

    if any(k in text for k in high_signals):
        return "HIGH"

    if any(k in text for k in medium_signals):
        return "MEDIUM"

    return "LOW"


# ==========================================================
# CORE AI SCORER
# ==========================================================

def score_record(record: NormalizedRecord) -> NormalizedRecord:
    """
    AI-based scoring (tinh chỉnh cuối)

    Input:
    - NormalizedRecord đã có:
        risk_score
        risk_level
        confidence (có thể có hoặc chưa)

    Output:
    - NormalizedRecord được điều chỉnh
    """

    # Nếu chưa có risk_score → bỏ qua
    if record.risk_score is None:
        return record

    ai_result = analyze_context_with_ai(record)

    if not ai_result:
        return record

    # ======================
    # HIGH RISK – AI xác nhận
    # ======================
    if ai_result == "HIGH":
        record.risk_score = min(
            (record.risk_score or 0) + AI_SCORE_BOOST_HIGH,
            100
        )
        record.confidence = max(
            record.confidence or 0,
            AI_CONFIDENCE_HIGH
        )
        record.risk_level = RiskLevel.HIGH
        return record

    # ======================
    # MEDIUM RISK – AI hỗ trợ
    # ======================
    if ai_result == "MEDIUM":
        record.risk_score = min(
            (record.risk_score or 0) + AI_SCORE_BOOST_MEDIUM,
            100
        )
        record.confidence = max(
            record.confidence or 0,
            AI_CONFIDENCE_MEDIUM
        )

        # chỉ nâng level nếu chưa HIGH
        if record.risk_level != RiskLevel.HIGH:
            record.risk_level = RiskLevel.MEDIUM

        return record

    # ======================
    # LOW SIGNAL – AI giảm nhẹ
    # ======================
    if ai_result == "LOW":
        record.risk_score = max(
            (record.risk_score or 0) + AI_SCORE_PENALTY_LOW,
            0
        )

        # không ép hạ level nếu đã HIGH
        if record.risk_level == RiskLevel.UNKNOWN:
            record.risk_level = RiskLevel.SAFE

        return record

    return record
