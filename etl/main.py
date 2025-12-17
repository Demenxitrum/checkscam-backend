# etl/main.py

"""
PRODUCTION DATA PIPELINE – FINAL VERSION (Layer 1 → 4)

Luồng:
- Load RAW
- Normalize
- Validate
- Risk Engine
- Aggregate (value + type + frequency + sources)
- Load report stats (Layer 4)
- Import MySQL

Ghi DB:
- lookup_cache
- report
- report_evidence
"""

from pathlib import Path
import json
import csv
from typing import List, Dict, Any

# =========================================================
# ETL CORE
# =========================================================

from etl.normalize.normalize import (
    normalize_from_social_raw,
    normalize_from_entity_records,
)
from etl.normalize.schema import NormalizedRecord, EntityType
from etl.processors.validate import is_record_valid
from etl.risk_engine.risk_engine import run_risk_engine

# =========================================================
# LAYER 4 – REPORT STATS
# =========================================================

from etl.importer.report_stats_loader import load_report_stats

# =========================================================
# MYSQL IMPORTER
# =========================================================

from etl.importer.mysql_importer import import_to_mysql


# =========================================================
# CONFIG
# =========================================================

RAW_DIR = Path("storage/raw")

MYSQL_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "123456",   # 🔴 đổi cho đúng máy bạn
    "database": "checkscam",
}

ENTITY_TYPE_ID_MAP = {
    EntityType.PHONE: 1,
    EntityType.BANK: 2,
    EntityType.URL: 3,
}


# =========================================================
# LOAD RAW DATA
# =========================================================

def load_raw_records() -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []

    if not RAW_DIR.exists():
        print(f"[WARN] RAW_DIR not found: {RAW_DIR}")
        return records

    for file in RAW_DIR.iterdir():
        if file.name == "global_seen.json":
            continue

        try:
            if file.suffix == ".jsonl":
                with file.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        obj = json.loads(line)
                        if isinstance(obj, dict):
                            records.append(obj)

            elif file.suffix == ".json":
                with file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        records.extend([x for x in data if isinstance(x, dict)])
                    elif isinstance(data, dict):
                        records.append(data)

            elif file.suffix == ".csv":
                with file.open("r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        url = row.get("url") or row.get("URL")
                        if url:
                            records.append({
                                "source": "phishtank",
                                "type": "URL",
                                "value": url,
                            })

        except Exception as e:
            print(f"[WARN] Skip {file.name}: {e}")

    return records


# =========================================================
# MAIN PIPELINE
# =========================================================

def main():
    # =============================
    # LOAD
    # =============================
    raw_records = load_raw_records()
    print(f"[LOAD] RAW records: {len(raw_records)}")

    if not raw_records:
        print("[STOP] No raw data")
        return

    # =============================
    # NORMALIZE
    # =============================
    normalized: List[NormalizedRecord] = []

    for raw in raw_records:
        if not isinstance(raw, dict):
            continue

        src = raw.get("source")
        if not src:
            continue

        if src in ("facebook", "tiktok"):
            normalized.extend(
                normalize_from_social_raw([raw], source=src)
            )
        else:
            normalized.extend(
                normalize_from_entity_records([raw], source=src)
            )

    print(f"[NORMALIZE] entities: {len(normalized)}")

    # =============================
    # VALIDATE
    # =============================
    valid_records = [r for r in normalized if is_record_valid(r)]
    print(f"[VALIDATE] valid entities: {len(valid_records)}")

    if not valid_records:
        print("[STOP] No valid entities")
        return

    # =============================
    # RISK ENGINE (Layer 1–3)
    # =============================
    scored_records = run_risk_engine(valid_records)
    print("[RISK ENGINE] scoring done")

    # =============================
    # AGGREGATE (VALUE + TYPE)
    # =============================
    aggregated: Dict[tuple, Dict[str, Any]] = {}

    for r in scored_records:
        key = (r.entity_value, r.entity_type)

        if key not in aggregated:
            aggregated[key] = {
                "record": r,
                "count": 1,
                "sources": {r.source},
            }
        else:
            aggregated[key]["count"] += 1
            aggregated[key]["sources"].add(r.source)

    final_records: List[NormalizedRecord] = []

    for item in aggregated.values():
        rec = item["record"]

        # Layer 2 – Frequency
        setattr(rec, "frequency", item["count"])

        # Layer 3 – Source credibility
        setattr(rec, "sources", item["sources"])

        final_records.append(rec)

    print(f"[AGGREGATE] final entities: {len(final_records)}")

    # =============================
    # LAYER 4 – LOAD REPORT STATS
    # =============================
    report_stats_map = load_report_stats(MYSQL_CONFIG)

    for rec in final_records:
        type_id = ENTITY_TYPE_ID_MAP.get(rec.entity_type)
        key = (rec.entity_value, type_id)

        setattr(
            rec,
            "report_stats",
            report_stats_map.get(
                key,
                {"approved": 0, "pending": 0, "rejected": 0}
            )
        )

    print("[LAYER 4] report stats attached")
    # =============================
    # RE-RUN RISK ENGINE (Layer 4)
    # =============================
    final_records = run_risk_engine(final_records)
    print("[RISK ENGINE] re-scored with report stats")

    # =============================
    # MYSQL IMPORT
    # =============================
    import_to_mysql(
        final_records,
        **MYSQL_CONFIG
    )

    print(f"[DONE] Imported / updated {len(final_records)} records into lookup_cache")


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()
