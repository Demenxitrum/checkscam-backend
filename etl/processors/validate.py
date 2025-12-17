"""
validate.py
===========

GIAI ĐOẠN 2 – KIỂM SOÁT & LỌC DỮ LIỆU

Nhiệm vụ:
- Loại bỏ record không hợp lệ về mặt kỹ thuật
- KHÔNG chấm điểm
- KHÔNG gán risk
- KHÔNG phụ thuộc source

Input  : List[NormalizedRecord]
Output : List[NormalizedRecord] (đã lọc)
"""

from typing import List

from etl.normalize.schema import NormalizedRecord, EntityType
from etl.normalize.utils import (
    is_valid_phone,
    is_valid_bank,
    is_valid_url,
)


# ==========================================================
# CORE VALIDATION
# ==========================================================

def is_record_valid(record: NormalizedRecord) -> bool:
    """
    Validate 1 record ở mức kỹ thuật (schema + format)
    """

    # ---------- schema-level ----------
    if not record:
        return False

    if not record.entity_type:
        return False

    if not record.entity_value:
        return False

    if not record.source:
        return False

    if record.country not in {"VN", "INT"}:
        return False

    # ---------- type-specific ----------
    et = record.entity_type

    if et == EntityType.PHONE:
        return is_valid_phone(record.entity_value)

    if et == EntityType.BANK:
        return is_valid_bank(record.entity_value)

    if et == EntityType.URL:
        return is_valid_url(record.entity_value)

    # ---------- unknown type ----------
    return False


# ==========================================================
# PIPELINE FUNCTION
# ==========================================================

def validate_records(
    records: List[NormalizedRecord],
) -> List[NormalizedRecord]:
    """
    Lọc danh sách record, giữ lại record hợp lệ
    """

    if not records:
        return []

    valid_records: List[NormalizedRecord] = []

    for record in records:
        try:
            if is_record_valid(record):
                valid_records.append(record)
        except Exception:
            # defensive: nếu record lỗi bất ngờ thì bỏ
            continue

    return valid_records
