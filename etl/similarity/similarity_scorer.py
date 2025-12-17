"""
similarity_scorer.py
====================

Nhiệm vụ:
- So sánh NormalizedRecord với các vector đã lưu
- Phát hiện entity tương tự (phone / bank / url)
- Trả về kết quả similarity cho AI scorer

KHÔNG:
- gán risk_level cuối
- ghi DB
"""

from dataclasses import dataclass
from typing import List, Optional

from etl.normalize.schema import NormalizedRecord
from etl.similarity.vector_client import VectorClient


# ==========================================================
# RESULT SCHEMA
# ==========================================================

@dataclass
class SimilarityResult:
    is_similar: bool
    similarity_score: float        # 0.0 → 1.0
    matched_hashes: List[str]      # các record giống
    confidence: float              # độ tin cậy AI
    risk_score: int                # điểm gợi ý cho AI


# ==========================================================
# CONFIG
# ==========================================================

SIMILARITY_THRESHOLD = 0.85   # >= coi là trùng nguy hiểm
MAX_RISK_SCORE = 80           # AI không override 100%
BASE_CONFIDENCE = 0.6


# ==========================================================
# CORE FUNCTION
# ==========================================================

def score_similarity(
    record: NormalizedRecord,
    *,
    top_k: int = 5,
) -> SimilarityResult:
    """
    So sánh record với vector store
    """

    client = VectorClient()

    # Nếu chưa có embedding → bỏ qua
    vector = client.embed_text(record.entity_value)
    if not vector:
        return SimilarityResult(
            is_similar=False,
            similarity_score=0.0,
            matched_hashes=[],
            confidence=0.0,
            risk_score=0,
        )

    # Query vector store
    matches = client.query(
        vector=vector,
        top_k=top_k,
    )

    if not matches:
        return SimilarityResult(
            is_similar=False,
            similarity_score=0.0,
            matched_hashes=[],
            confidence=0.0,
            risk_score=0,
        )

    # Lấy match tốt nhất
    best = matches[0]
    best_score = best["score"]

    if best_score < SIMILARITY_THRESHOLD:
        return SimilarityResult(
            is_similar=False,
            similarity_score=best_score,
            matched_hashes=[],
            confidence=0.0,
            risk_score=0,
        )

    # Có similarity nguy hiểm
    matched_hashes = [m["id"] for m in matches if m["score"] >= SIMILARITY_THRESHOLD]

    # Risk score tăng theo độ giống
    risk_score = int(MAX_RISK_SCORE * best_score)

    # Confidence tăng nếu nhiều match
    confidence = min(
        1.0,
        BASE_CONFIDENCE + 0.1 * len(matched_hashes)
    )

    return SimilarityResult(
        is_similar=True,
        similarity_score=best_score,
        matched_hashes=matched_hashes,
        confidence=confidence,
        risk_score=risk_score,
    )
