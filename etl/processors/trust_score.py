"""
trust_score.py
==============

Nhiệm vụ:
- Nhận NormalizedRecord (đã qua validate + pattern_rules)
- Tính TRUST SCORE (0 → 1):
    - dựa trên độ uy tín nguồn (source)
    - mức đầy đủ bằng chứng (url/context/evidence)
    - số nguồn cùng xác nhận (nếu có aggregation map)
- Gắn vào record:
    - record.trust_score (float 0..1)
    - record.trust_factors (dict để trace)
- Tinh chỉnh record.confidence theo trust_score
  (KHÔNG chấm risk_score, KHÔNG set risk_level)

Đầu vào:
- List[NormalizedRecord]
- (optional) entity_source_count: dict {record.hash: int} hoặc {hash: count}
  => cho biết thực thể này xuất hiện ở bao nhiêu nguồn

Đầu ra:
- List[NormalizedRecord] (đã được enrich trust_score)
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

from etl.normalize.schema import NormalizedRecord


# ==========================================================
# 1) CONFIG – ĐỘ UY TÍN THEO NGUỒN
# ==========================================================
# Bạn có thể tinh chỉnh theo tiêu chí hội đồng:
# - NCSC / Police: nguồn nhà nước → rất cao
# - News (báo lớn): cao
# - PhishTank: cao (quốc tế) nhưng thường chỉ URL
# - Facebook/TikTok: crowdsourced → thấp hơn (dễ nhiễu)
SOURCE_TRUST: Dict[str, float] = {
    "ncsc": 0.95,
    "police": 0.92,
    "news": 0.85,
    "phishtank": 0.88,
    "facebook": 0.55,
    "tiktok": 0.50,
}


# ==========================================================
# 2) CONFIG – TRỌNG SỐ FACTOR
# ==========================================================
W_SOURCE = 0.50     # nguồn chiếm 50%
W_EVIDENCE = 0.25   # bằng chứng chiếm 25%
W_CROSS = 0.25      # đa nguồn chiếm 25%


# ==========================================================
# 3) HELPER – safe clamp
# ==========================================================
def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _has_meaningful_text(s: Optional[str], min_len: int = 20) -> bool:
    if not s:
        return False
    return len(s.strip()) >= min_len


def _is_valid_http_url(u: Optional[str]) -> bool:
    if not u:
        return False
    try:
        p = urlparse(u)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


# ==========================================================
# 4) FACTOR 1 – SOURCE TRUST
# ==========================================================
def source_trust(record: NormalizedRecord) -> float:
    src = (record.source or "").strip().lower()
    return SOURCE_TRUST.get(src, 0.60)  # default trung bình


# ==========================================================
# 5) FACTOR 2 – EVIDENCE COMPLETENESS
# ==========================================================
def evidence_score(record: NormalizedRecord) -> float:
    """
    Chấm mức "đủ bằng chứng" (0..1):
    - có url bài viết/video: +0.45
    - có context đủ dài: +0.35
    - có evidence metadata: +0.20
    """
    score = 0.0

    if _is_valid_http_url(record.url):
        score += 0.45

    if _has_meaningful_text(record.context, min_len=20):
        score += 0.35

    if record.evidence:
        score += 0.20

    return _clamp(score)


# ==========================================================
# 6) FACTOR 3 – CROSS-SOURCE CONFIRMATION
# ==========================================================
def cross_source_score(source_count: int) -> float:
    """
    Quy đổi số nguồn cùng xác nhận -> 0..1
    1 nguồn: 0.25
    2 nguồn: 0.55
    3 nguồn: 0.75
    >=4 nguồn: 0.90
    """
    if source_count <= 1:
        return 0.25
    if source_count == 2:
        return 0.55
    if source_count == 3:
        return 0.75
    return 0.90


# ==========================================================
# 7) TÍNH TRUST SCORE CHO 1 RECORD
# ==========================================================
def compute_trust_score(
    record: NormalizedRecord,
    *,
    source_count: int = 1,
) -> float:
    s_trust = source_trust(record)
    e_score = evidence_score(record)
    c_score = cross_source_score(source_count)

    trust = (
        W_SOURCE * s_trust +
        W_EVIDENCE * e_score +
        W_CROSS * c_score
    )

    return _clamp(trust)


# ==========================================================
# 8) CẬP NHẬT CONFIDENCE THEO TRUST
# ==========================================================
def combine_confidence(
    base_confidence: Optional[float],
    trust_score: float
) -> float:
    """
    Ý tưởng:
    - pattern_rules tạo base_confidence (rule-based)
    - trust_score là mức "tin tưởng nguồn + bằng chứng + đa nguồn"
    Kết hợp:
    - nếu base_confidence chưa có: lấy trust làm nền
    - nếu có: lấy trung bình có trọng số (ưu tiên rule-based)
    """
    t = _clamp(trust_score)

    if base_confidence is None:
        return t

    b = _clamp(float(base_confidence))
    # 65% rule-based + 35% trust-based
    return _clamp(0.65 * b + 0.35 * t)


# ==========================================================
# 9) APPLY BATCH
# ==========================================================
def apply_trust_score(
    records: List[NormalizedRecord],
    *,
    entity_source_count: Optional[Dict[str, int]] = None,
) -> List[NormalizedRecord]:
    """
    Gắn trust_score vào từng record.
    entity_source_count: dict {record.hash: count}
    """
    entity_source_count = entity_source_count or {}

    for r in records:
        count = int(entity_source_count.get(r.hash, 1))
        trust = compute_trust_score(r, source_count=count)

        # Gắn thêm field động (không cần sửa schema.py)
        setattr(r, "trust_score", trust)

        factors: Dict[str, Any] = {
            "source": (r.source or "").lower(),
            "source_trust": source_trust(r),
            "evidence_score": evidence_score(r),
            "source_count": count,
            "cross_source_score": cross_source_score(count),
            "weights": {"source": W_SOURCE, "evidence": W_EVIDENCE, "cross": W_CROSS},
        }
        setattr(r, "trust_factors", factors)

        # Tinh chỉnh confidence (nếu pattern_rules đã set confidence)
        r.confidence = combine_confidence(r.confidence, trust)

    return records


# ==========================================================
# 10) QUICK HELPER – build source_count nếu bạn muốn
# ==========================================================
def build_entity_source_count(records: List[NormalizedRecord]) -> Dict[str, int]:
    """
    Nếu bạn đang merge nhiều nguồn trước đó, hàm này giúp đếm
    thực thể (hash) xuất hiện bao nhiêu lần (bao nhiêu record).
    """
    m: Dict[str, int] = {}
    for r in records:
        m[r.hash] = m.get(r.hash, 0) + 1
    return m
