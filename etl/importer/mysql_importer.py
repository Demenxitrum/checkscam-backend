"""
mysql_importer.py – OPTIMIZED (BATCH + BULK)

- Commit theo batch
- Bulk UPSERT lookup_cache
- Có progress log
- Có thể tắt report / evidence để chạy nhanh
"""

from typing import List, Dict, Any
from datetime import datetime
import json

import mysql.connector
from mysql.connector import MySQLConnection

from etl.normalize.schema import NormalizedRecord, EntityType, RiskLevel


# ==========================================================
# CONFIG
# ==========================================================

RISK_LEVEL_MAP = {
    RiskLevel.SAFE: 1,
    RiskLevel.MEDIUM: 2,
    RiskLevel.HIGH: 3,
}

ENTITY_TYPE_MAP = {
    EntityType.PHONE: 1,
    EntityType.BANK: 2,
    EntityType.URL: 3,
}

DEFAULT_REPORT_STATUS_ID = 1  # PENDING

# ⚙️ TUNING
BATCH_SIZE = 500

# ⚙️ FLAGS (để chạy nhanh)
ENABLE_REPORT = False
ENABLE_EVIDENCE = False


# ==========================================================
# MYSQL IMPORTER
# ==========================================================

class MySQLImporter:
    def __init__(
        self,
        *,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
    ):
        self.conn: MySQLConnection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            autocommit=False,
        )

    # ======================================================
    # BULK UPSERT LOOKUP CACHE
    # ======================================================
    def bulk_upsert_lookup_cache(self, records: List[NormalizedRecord]):
        cursor = self.conn.cursor()

        sql = """
        INSERT INTO lookup_cache
        (
            value,
            type_id,
            report_count,
            risk_level_id,
            risk_score,
            confidence,
            updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            report_count = report_count + VALUES(report_count),
            risk_level_id = VALUES(risk_level_id),
            risk_score = VALUES(risk_score),
            confidence = VALUES(confidence),
            updated_at = VALUES(updated_at)
        """

        params = []

        now = datetime.utcnow()

        for r in records:
            params.append(
                (
                    r.entity_value,
                    ENTITY_TYPE_MAP.get(r.entity_type),
                    1,
                    RISK_LEVEL_MAP.get(r.risk_level),
                    r.risk_score,
                    r.confidence,
                    now,
                )
            )

        cursor.executemany(sql, params)
        cursor.close()

    # ======================================================
    # INSERT REPORT (OPTIONAL)
    # ======================================================
    def insert_report(self, record: NormalizedRecord) -> int:
        cursor = self.conn.cursor()

        sql = """
        INSERT INTO report
        (
            created_at,
            description,
            info_value,
            user_email,
            user_id,
            risk_level_id,
            status_id,
            type_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            sql,
            (
                record.created_at,
                record.context,
                record.entity_value,
                None,
                None,
                RISK_LEVEL_MAP.get(record.risk_level),
                DEFAULT_REPORT_STATUS_ID,
                ENTITY_TYPE_MAP.get(record.entity_type),
            ),
        )

        report_id = cursor.lastrowid
        cursor.close()
        return report_id

    # ======================================================
    # INSERT EVIDENCE (OPTIONAL)
    # ======================================================
    def insert_evidence(self, report_id: int, evidence: Dict[str, Any]):
        if not evidence:
            return

        cursor = self.conn.cursor()

        sql = """
        INSERT INTO report_evidence (file_path, report_id)
        VALUES (%s, %s)
        """

        cursor.execute(
            sql,
            (
                json.dumps(evidence, ensure_ascii=False),
                report_id,
            ),
        )

        cursor.close()

    # ======================================================
    # IMPORT RECORDS (BATCH)
    # ======================================================
    def import_records(self, records: List[NormalizedRecord]):
        try:
            total = len(records)
            batch: List[NormalizedRecord] = []

            for idx, record in enumerate(records, start=1):
                batch.append(record)

                # =============================
                # BULK COMMIT
                # =============================
                if len(batch) >= BATCH_SIZE:
                    self._commit_batch(batch, idx, total)
                    batch.clear()

            # commit phần còn lại
            if batch:
                self._commit_batch(batch, total, total)

            self.conn.commit()

        except Exception:
            self.conn.rollback()
            raise

    # ======================================================
    # COMMIT 1 BATCH
    # ======================================================
    def _commit_batch(self, batch: List[NormalizedRecord], idx: int, total: int):
        # 1️⃣ lookup_cache (BULK)
        self.bulk_upsert_lookup_cache(batch)

        # 2️⃣ report / evidence (OPTIONAL)
        if ENABLE_REPORT:
            for r in batch:
                report_id = self.insert_report(r)
                if ENABLE_EVIDENCE:
                    self.insert_evidence(report_id, r.evidence)

        self.conn.commit()
        print(f"[IMPORT] committed {idx}/{total}")

    # ======================================================
    # CLOSE
    # ======================================================
    def close(self):
        self.conn.close()


# ==========================================================
# QUICK HELPER
# ==========================================================

def import_to_mysql(
    records: List[NormalizedRecord],
    *,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
):
    importer = MySQLImporter(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )

    try:
        importer.import_records(records)
    finally:
        importer.close()
