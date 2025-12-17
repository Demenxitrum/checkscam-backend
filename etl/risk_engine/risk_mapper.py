"""
risk_mapper.py
==============

Nhiệm vụ:
- Nhận danh sách NormalizedRecord đã chạy qua RiskEngine
- Map sang format phẳng (flat) để:
    - import MySQL
    - ghi JSONL / CSV
- KHÔNG xử lý logic nghiệp vụ
- KHÔNG chấm điểm
- CHỈ chuyển đổi dữ liệu

Đây là tầng:
RISK ENGINE OUTPUT  →  STORAGE / DATABASE FORMAT
"""

from typing import List, Dict, Any
from pathlib import Path
import json
import csv

from etl.normalize.schema import NormalizedRecord


# ==========================================================
# CORE MAPPER
# ==========================================================

def map_record_to_row(record: NormalizedRecord) -> Dict[str, Any]:
    """
    Chuyển 1 NormalizedRecord → dict phẳng (chuẩn DB)

    Output này có thể:
    - insert thẳng vào MySQL
    - ghi CSV / JSONL
    """

    return {
        # ======================
        # ENTITY CORE
        # ======================
        "entity_type": record.entity_type.value,
        "entity_value": record.entity_value,
        "country": record.country,
        "source": record.source,

        # ======================
        # RISK RESULT
        # ======================
        "risk_score": record.risk_score,
        "risk_level": record.risk_level.value if record.risk_level else None,
        "confidence": record.confidence,

        # ======================
        # CONTEXT
        # ======================
        "raw_value": record.raw_value,
        "context": record.context,
        "url": record.url,

        # ======================
        # SYSTEM
        # ======================
        "hash": record.hash,
        "created_at": record.created_at,

        # ======================
        # TRACEABILITY
        # ======================
        "rules_triggered": ",".join(
            getattr(record, "rules_triggered", [])
        ),

        "evidence": json.dumps(
            record.evidence, ensure_ascii=False
        ) if record.evidence else None,
    }


def map_records(records: List[NormalizedRecord]) -> List[Dict[str, Any]]:
    """
    Map hàng loạt record
    """
    return [map_record_to_row(r) for r in records]


# ==========================================================
# EXPORT JSONL
# ==========================================================

def export_jsonl(
    records: List[NormalizedRecord],
    output_path: str | Path,
) -> None:
    """
    Ghi file JSONL (mỗi dòng 1 record)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            row = map_record_to_row(record)
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


# ==========================================================
# EXPORT CSV
# ==========================================================

def export_csv(
    records: List[NormalizedRecord],
    output_path: str | Path,
) -> None:
    """
    Ghi file CSV (phẳng – dễ import MySQL)
    """
    if not records:
        return

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = map_records(records)
    fieldnames = list(rows[0].keys())

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ==========================================================
# QUICK HELPER
# ==========================================================

def export_all(
    records: List[NormalizedRecord],
    *,
    jsonl_path: str | Path | None = None,
    csv_path: str | Path | None = None,
) -> None:
    """
    Export tiện lợi:
    - JSONL
    - CSV
    """

    if jsonl_path:
        export_jsonl(records, jsonl_path)

    if csv_path:
        export_csv(records, csv_path)
