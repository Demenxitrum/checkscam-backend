"""
normalize.py
============

Nhiệm vụ:
- Nhận dữ liệu RAW từ các crawler (facebook / tiktok / news / ncsc / police / phishtank)
- Chuẩn hoá entity (PHONE / BANK / URL)
- Convert sang NormalizedRecord (schema chuẩn toàn hệ thống)
- Deduplicate ở mức ENTITY (không phụ thuộc source)

File này là CẦU NỐI:
RAW DATA  --->  NORMALIZED SCHEMA  --->  RISK ENGINE / DB
"""

from typing import List, Dict, Any, Iterable
from datetime import datetime, timezone

from etl.normalize.schema import (
    NormalizedRecord,
    EntityType,
    RiskLevel,
)
from etl.normalize.utils import (
    normalize_entity,
    detect_country,
)


# ==========================================================
# HELPER
# ==========================================================

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ==========================================================
# CORE NORMALIZE FUNCTION
# ==========================================================

def normalize_raw_item(
    *,
    entity_type: str,
    raw_value: str,
    source: str,
    context: str | None = None,
    url: str | None = None,
    evidence: Dict[str, Any] | None = None,
) -> NormalizedRecord | None:
    """
    Normalize 1 entity RAW → NormalizedRecord

    Trả về:
    - NormalizedRecord nếu hợp lệ
    - None nếu normalize thất bại
    """

    normalized_value, country = normalize_entity(entity_type, raw_value)

    if not normalized_value or not country:
        return None

    record = NormalizedRecord(
        entity_type=EntityType(entity_type),
        entity_value=normalized_value,
        raw_value=raw_value,
        source=source,
        country=country,
        context=context,
        url=url,
        evidence=evidence,
        created_at=now_iso(),
        risk_level=RiskLevel.UNKNOWN,
    )

    if not record.is_valid():
        return None

    return record


# ==========================================================
# NORMALIZE FROM COMMON RAW STRUCTURES
# ==========================================================

def normalize_from_social_raw(
    raw_items: Iterable[Dict[str, Any]],
    *,
    source: str,
) -> List[NormalizedRecord]:
    """
    Normalize dữ liệu từ:
    - Facebook
    - TikTok

    Format RAW mong đợi:
    {
        "phones": [...],
        "banks": [...],
        "urls": [...],
        "text" / "caption": "...",
        "video_url" / "group": "...",
        ...
    }
    """

    records: Dict[str, NormalizedRecord] = {}

    for item in raw_items:
        context = item.get("text") or item.get("caption")
        url = item.get("video_url") or item.get("group")

        # PHONE
        for raw_phone in item.get("phones", []):
            rec = normalize_raw_item(
                entity_type="PHONE",
                raw_value=raw_phone,
                source=source,
                context=context,
                url=url,
                evidence=item,
            )
            if rec:
                records[rec.hash] = rec

        # BANK
        for raw_bank in item.get("banks", []):
            rec = normalize_raw_item(
                entity_type="BANK",
                raw_value=raw_bank,
                source=source,
                context=context,
                url=url,
                evidence=item,
            )
            if rec:
                records[rec.hash] = rec

        # URL
        for raw_url in item.get("urls", []):
            rec = normalize_raw_item(
                entity_type="URL",
                raw_value=raw_url,
                source=source,
                context=context,
                url=url,
                evidence=item,
            )
            if rec:
                records[rec.hash] = rec

    return list(records.values())


# ==========================================================
# NORMALIZE FROM JSONL RECORDS (NEWS / NCSC / POLICE / PHISHTANK)
# ==========================================================

def normalize_from_entity_records(
    raw_items: Iterable[Dict[str, Any]],
    *,
    source: str,
) -> List[NormalizedRecord]:
    """
    Normalize dữ liệu từ các crawler dạng entity-level:
    - news
    - ncsc
    - police
    - phishtank

    RAW format mong đợi:
    {
        "type": "PHONE" | "BANK" | "URL",
        "value": "...",
        "context": "...",
        "url": "...",
        ...
    }
    """

    records: Dict[str, NormalizedRecord] = {}

    for item in raw_items:
        entity_type = item.get("type")
        raw_value = item.get("value")

        if not entity_type or not raw_value:
            continue

        rec = normalize_raw_item(
            entity_type=entity_type,
            raw_value=raw_value,
            source=source,
            context=item.get("context"),
            url=item.get("url"),
            evidence=item,
        )

        if rec:
            records[rec.hash] = rec

    return list(records.values())


# ==========================================================
# PIPELINE ENTRY (OPTIONAL)
# ==========================================================

def normalize_all(
    *,
    facebook_raw: Iterable[Dict[str, Any]] | None = None,
    tiktok_raw: Iterable[Dict[str, Any]] | None = None,
    news_raw: Iterable[Dict[str, Any]] | None = None,
    ncsc_raw: Iterable[Dict[str, Any]] | None = None,
    police_raw: Iterable[Dict[str, Any]] | None = None,
    phishtank_raw: Iterable[Dict[str, Any]] | None = None,
) -> List[NormalizedRecord]:
    """
    Normalize toàn bộ dữ liệu RAW từ nhiều nguồn → 1 list chuẩn duy nhất
    """

    result: Dict[str, NormalizedRecord] = {}

    if facebook_raw:
        for r in normalize_from_social_raw(facebook_raw, source="facebook"):
            result[r.hash] = r

    if tiktok_raw:
        for r in normalize_from_social_raw(tiktok_raw, source="tiktok"):
            result[r.hash] = r

    if news_raw:
        for r in normalize_from_entity_records(news_raw, source="news"):
            result[r.hash] = r

    if ncsc_raw:
        for r in normalize_from_entity_records(ncsc_raw, source="ncsc"):
            result[r.hash] = r

    if police_raw:
        for r in normalize_from_entity_records(police_raw, source="police"):
            result[r.hash] = r

    if phishtank_raw:
        for r in normalize_from_entity_records(phishtank_raw, source="phishtank"):
            result[r.hash] = r

    return list(result.values())
