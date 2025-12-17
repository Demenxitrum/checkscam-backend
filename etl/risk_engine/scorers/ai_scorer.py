"""
ai_scorer.py
============

Nhiệm vụ:
- Điều chỉnh risk_score dựa trên đánh giá AI / similarity
- KHÔNG phát hiện entity mới
- KHÔNG override rule-based (pattern_scorer)
- CHỈ tinh chỉnh risk_score + confidence

AI ở đây là:
"TRỢ LÝ ĐÁNH GIÁ" – không phải quyết định cuối cùng
"""

from etl.normalize.schema import NormalizedRecord, RiskLevel


# ==========================================================
# CONFIG
# ==========================================================

# Giới hạn tác động AI
MAX_AI_BONUS = 20       # cộng tối đa +20 điểm
MAX_AI_PENALTY = -15   # giảm tối đa -15 điểm


# ==========================================================
# CORE AI SCORER
# ==========================================================

def score_record(record: NormalizedRecord) -> NormalizedRecord:
    """
    Điều chỉnh risk_score dựa trên:
    - ai_risk_score (0 → 1)
    - ai_label
    - similarity (nếu có)

    AI KHÔNG override rule-based score
    """

    evidence = record.evidence or {}
    record.evidence = evidence  # đảm bảo tồn tại

    current_score = record.risk_score or 0
    delta = 0

    # ======================================================
    # 1️⃣ AI MODEL SCORE (0 → 1)
    # ======================================================
    ai_score = evidence.get("ai_risk_score")

    if isinstance(ai_score, (int, float)):
        if ai_score >= 0.85:
            delta += 15
        elif ai_score >= 0.7:
            delta += 10
        elif ai_score <= 0.3:
            delta -= 10

        # AI score ảnh hưởng confidence
        record.confidence = max(record.confidence or 0, ai_score)

    # ======================================================
    # 2️⃣ AI LABEL (LLM / CLASSIFIER)
    # ======================================================
    ai_label = evidence.get("ai_label")

    if ai_label == "SCAM":
        delta += 10
    elif ai_label == "SAFE":
        delta -= 10

    # ======================================================
    # 3️⃣ SIMILARITY SIGNAL (TỪ similarity_scorer)
    # ======================================================
    similarity = evidence.get("similarity")

    if isinstance(similarity, dict):
        sim_score = similarity.get("score", 0)

        # similarity rất cao → tăng nhẹ
        if sim_score >= 0.9:
            delta += 10
        elif sim_score >= 0.85:
            delta += 5

        record.confidence = max(
            record.confidence or 0,
            min(1.0, 0.6 + sim_score)
        )

    # ======================================================
    # 4️⃣ GIỚI HẠN ẢNH HƯỞNG AI
    # ======================================================
    delta = max(MAX_AI_PENALTY, min(delta, MAX_AI_BONUS))

    final_score = max(0, min(current_score + delta, 100))
    record.risk_score = final_score

    # ======================================================
    # 5️⃣ MAP RISK LEVEL (SAU CÙNG)
    # ======================================================
    if final_score >= 70:
        record.risk_level = RiskLevel.HIGH
    elif final_score >= 40:
        record.risk_level = RiskLevel.MEDIUM
    else:
        record.risk_level = RiskLevel.SAFE

    return record
