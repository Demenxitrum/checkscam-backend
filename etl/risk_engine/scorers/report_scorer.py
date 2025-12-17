"""
report_scorer.py
================

Nhiệm vụ:
- Điều chỉnh risk_score dựa trên dữ liệu REPORT từ người dùng
- Tận dụng bảng report trong MySQL (nếu có dữ liệu)
- Gắn cực tốt với hệ thống backend hiện tại (ăn điểm đồ án)

Nguyên tắc:
- Nhiều user report → tăng độ nguy hiểm
- Report từ nhiều user khác nhau → tăng mạnh hơn
- KHÔNG phát hiện lừa đảo mới
- CHỈ tinh chỉnh risk_score + risk_level
"""

from etl.normalize.schema import NormalizedRecord, RiskLevel


# ==========================================================
# CONFIG
# ==========================================================

# Mỗi report cộng bao nhiêu điểm
POINT_PER_REPORT = 10

# Giới hạn tối đa điểm cộng từ report
MAX_REPORT_BONUS = 30


# ==========================================================
# CORE SCORER
# ==========================================================

def score_record(record: NormalizedRecord) -> NormalizedRecord:
    """
    Điều chỉnh điểm rủi ro dựa trên số lần user report
    """

    # evidence phải chứa thông tin report
    evidence = record.evidence or {}

    # Giả định backend đã gắn vào evidence
    # Ví dụ:
    # {
    #   "report_count": 5,
    #   "unique_reporters": 3
    # }

    report_count = evidence.get("report_count", 0)
    unique_reporters = evidence.get("unique_reporters", 0)

    # Nếu chưa có report → bỏ qua
    if report_count <= 0:
        return record

    # =========================
    # TÍNH ĐIỂM REPORT
    # =========================

    bonus = report_count * POINT_PER_REPORT

    # Nếu nhiều user khác nhau report → cộng thêm
    if unique_reporters >= 3:
        bonus += 10
    if unique_reporters >= 5:
        bonus += 20

    bonus = min(bonus, MAX_REPORT_BONUS)

    # =========================
    # ÁP DỤNG VÀO RECORD
    # =========================

    current_score = record.risk_score or 0
    final_score = min(current_score + bonus, 100)

    record.risk_score = final_score

    # Cập nhật lại risk_level
    if final_score >= 70:
        record.risk_level = RiskLevel.HIGH
    elif final_score >= 40:
        record.risk_level = RiskLevel.MEDIUM
    else:
        record.risk_level = RiskLevel.SAFE

    return record
