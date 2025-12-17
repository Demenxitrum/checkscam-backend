"""
pipeline_debug.py
=================

Debug pipeline:
RAW → normalize → validate → risk_engine → trust_score

❌ Không ghi DB
❌ Không production
✅ Chỉ để debug & demo logic
"""

from pathlib import Path
import json
from typing import List, Dict, Any

# =========================
# IMPORT ĐÚNG – KHÔNG ẢNH HƯỞNG FILE KHÁC
# =========================

# Normalize
from etl.normalize.normalize import (
    normalize_from_social_raw,
    normalize_from_entity_records,
)
from etl.normalize.schema import NormalizedRecord

# Validate
from etl.processors.validate import is_record_valid

# Trust score (BATCH)
from etl.processors.trust_score import (
    apply_trust_score,
    build_entity_source_count,
)

# Risk Engine
from etl.risk_engine.risk_engine import run_risk_engine


# =========================
# CONFIG
# =========================
RAW_DIR = Path("storage/raw")
DEBUG_LIMIT = 20


# =========================
# LOAD RAW RECORDS
# =========================
def load_raw_records(limit: int) -> List[Dict[str, Any]]:
    """
    Load RAW records từ storage/raw
    Hỗ trợ:
    - .json   (list hoặc object)
    - .jsonl  (mỗi dòng 1 JSON)
    - .csv    (PhishTank online valid)
    """

    records: List[Dict[str, Any]] = []

    if not RAW_DIR.exists():
        print(f"[WARN] RAW_DIR not found: {RAW_DIR}")
        return []

    for file in RAW_DIR.iterdir():
        if len(records) >= limit:
            break

        try:
            # =========================
            # JSONL
            # =========================
            if file.suffix == ".jsonl":
                with file.open("r", encoding="utf-8") as f:
                    for line in f:
                        if len(records) >= limit:
                            break
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            records.append(json.loads(line))
                        except Exception:
                            continue

            # =========================
            # JSON
            # =========================
            elif file.suffix == ".json":
                with file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        records.extend(data)
                    elif isinstance(data, dict):
                        records.append(data)

            # =========================
            # CSV (PhishTank online)
            # =========================
            elif file.suffix == ".csv":
                import csv
                with file.open("r", encoding="utf-8", newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if len(records) >= limit:
                            break

                        # Chuẩn hóa row CSV về format entity-level
                        # PhishTank thường là URL
                        value = row.get("url") or row.get("URL")
                        if not value:
                            continue

                        records.append({
                            "source": "phishtank",
                            "type": "URL",
                            "value": value,
                            "context": None,
                            "url": value,
                        })

        except Exception as e:
            print(f"[ERROR] Cannot read {file.name}: {e}")

    return records[:limit]

# =========================
# DEBUG PIPELINE
# =========================
def debug_pipeline():
    raw_records = load_raw_records(DEBUG_LIMIT)

    print("=" * 90)
    print(f"DEBUG PIPELINE — RAW RECORDS: {len(raw_records)}")
    print("=" * 90)

    all_valid_records: List[NormalizedRecord] = []

    # =========================
    # 1) NORMALIZE + VALIDATE + RISK
    # =========================
    for idx, raw in enumerate(raw_records, start=1):
        print("\n" + "-" * 90)
        source = raw.get("source")
        print(f"[{idx}] SOURCE = {source}")
        print("-" * 90)

        if not source:
            print("⚠️  Missing source → SKIP")
            continue

        # ---------- NORMALIZE ----------
        if source in ("facebook", "tiktok"):
            normalized_records = normalize_from_social_raw(
                [raw], source=source
            )

        elif source in ("news", "ncsc", "police", "phishtank"):
            normalized_records = normalize_from_entity_records(
                [raw], source=source
            )

        else:
            print(f"⚠️  Unknown source '{source}' → SKIP")
            continue

        if not normalized_records:
            print("❌ No entity detected after normalize")
            continue

        # ---------- VALIDATE + RISK ----------
        for record in normalized_records:
            if not is_record_valid(record):
                print(
                    f"   ❌ INVALID → {record.entity_type} {record.entity_value}"
                )
                continue

            # Risk engine (rule-based)
            run_risk_engine([record])
            all_valid_records.append(record)

    if not all_valid_records:
        print("\n❌ No valid records to process trust score")
        return

    # =========================
    # 2) TRUST SCORE (BATCH)
    # =========================
    source_count = build_entity_source_count(all_valid_records)
    apply_trust_score(
        all_valid_records,
        entity_source_count=source_count,
    )

    # =========================
    # 3) FINAL OUTPUT
    # =========================
    print("\n" + "=" * 90)
    print("FINAL RESULTS")
    print("=" * 90)

    for r in all_valid_records:
        print("\n🔹 ENTITY")
        print(f"   Type        : {r.entity_type}")
        print(f"   Value       : {r.entity_value}")
        print(f"   Source      : {r.source}")
        print(f"   Risk Score  : {r.risk_score}")
        print(
            f"   Risk Level  : "
            f"{r.risk_level.name if r.risk_level else None}"
        )
        print(f"   Trust Score : {getattr(r, 'trust_score', None)}")
        print(f"   Confidence  : {r.confidence}")

    print("\n" + "=" * 90)
    print("PIPELINE DEBUG FINISHED")
    print("=" * 90)


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    debug_pipeline()
