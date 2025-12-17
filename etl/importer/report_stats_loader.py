# etl/importer/report_stats_loader.py

"""
Report Stats Loader
-------------------
Nhiệm vụ:
- Đọc report từ DB
- Gom thống kê theo (entity_value + type_id)
- Chỉ trả về số lượng report đã được DUYỆT / PENDING / REJECTED

File này:
- KHÔNG chấm điểm
- KHÔNG phụ thuộc Risk Engine
- Dùng cho Layer 4
"""

from collections import defaultdict
from typing import Dict, Tuple

import mysql.connector


# status_id trong DB (theo thiết kế backend)
STATUS_PENDING = 1
STATUS_APPROVED = 2
STATUS_REJECTED = 3


def load_report_stats(mysql_config) -> Dict[Tuple[str, int], dict]:
    """
    Return:
        {
          (value, type_id): {
              approved: int,
              pending: int,
              rejected: int
          }
        }
    """

    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()

    sql = """
    SELECT info_value, type_id, status_id, COUNT(*) AS cnt
    FROM report
    GROUP BY info_value, type_id, status_id
    """

    cursor.execute(sql)

    stats = defaultdict(lambda: {
        "approved": 0,
        "pending": 0,
        "rejected": 0,
    })

    for value, type_id, status_id, cnt in cursor.fetchall():
        key = (value, type_id)

        if status_id == STATUS_APPROVED:
            stats[key]["approved"] += cnt
        elif status_id == STATUS_PENDING:
            stats[key]["pending"] += cnt
        elif status_id == STATUS_REJECTED:
            stats[key]["rejected"] += cnt

    cursor.close()
    conn.close()

    return stats
