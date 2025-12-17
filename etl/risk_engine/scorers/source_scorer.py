"""
source_scorer.py
================

Nhiệm vụ:
- Điều chỉnh rủi ro dựa trên ĐỘ TIN CẬY NGUỒN (source)
- KHÔNG phát hiện pattern mới
- KHÔNG validate dữ liệu
- CHỈ dùng trust_score đã được tính trước

Tầng:
NGUỒN DỮ LIỆU → ĐIỀU CHỈNH ĐIỂM RỦI RO
"""

from etl.normalize.schema import NormalizedRecord, RiskLevel


# ==========================================================
# CONFIG – NGƯỠNG ĐIỀU CHỈNH
# ==========================================================

# Nếu nguồn rất uy tín → tăng độ tin cậy kết luận
HIGH_TRUST_THRESHOLD = 0.85

# Nếu nguồn kém uy tín → giảm độ tin cậy
LOW_TRUST_THRESHOLD = 0.4

# Hệ số điều chỉnh score
HIGH_TRUST_BONUS = 10      # + điểm nếu nguồn rất uy tín
LOW_TRUST_PENALTY = -10    # - điểm nếu nguồn kém


# ==========================================================
# CORE SCORER
# ==========================================================

def score_record(record: NormalizedRecord) -> NormalizedRecord:
    """
    Điều chỉnh risk_score & risk_level dựa trên trust_score (source-based)

    Điều kiện:
    - record đã được chấm điểm trước đó (pattern_scorer)
    - record có trust_score (gán từ trust_score.py)
    """

    trust = getattr(record, "trust_score", None)

    # Nếu chưa có trust_score → bỏ qua
    if trust is None:
        return record

    # Nếu chưa có risk_score → không điều chỉnh
    if record.risk_score is None:
        return record

    score = record.risk_score

    # ==========================
    # NGUỒN RẤT UY TÍN
    # ==========================
    if trust >= HIGH_TRUST_THRESHOLD:
        score += HIGH_TRUST_BONUS

    # ==========================
    # NGUỒN KÉM UY TÍN
    # ==========================
    elif trust <= LOW_TRUST_THRESHOLD:
        score += LOW_TRUST_PENALTY

    # ==========================
    # GÁN LẠI GIÁ TRỊ
    # ==========================
    score = max(0, min(score, 100))
    record.risk_score = score

    # Cập nhật lại risk_level theo score mới
    if score >= 70:
        record.risk_level = RiskLevel.HIGH
    elif score >= 40:
        record.risk_level = RiskLevel.MEDIUM
    elif score > 0:
        record.risk_level = RiskLevel.SAFE
    else:
        record.risk_level = RiskLevel.UNKNOWN

    return record
