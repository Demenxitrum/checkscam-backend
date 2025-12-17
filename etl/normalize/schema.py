"""
schema.py
=========
Định nghĩa SCHEMA CHUẨN cho toàn bộ hệ thống CheckScam ETL + Risk Engine.

Mọi dữ liệu sau khi normalize PHẢI tuân theo NormalizedRecord.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime, timezone
import hashlib
import json


# ==========================================================
# ENUM – LOẠI THỰC THỂ
# ==========================================================

class EntityType(str, Enum):
    PHONE = "PHONE"
    BANK = "BANK"
    URL = "URL"


class RiskLevel(str, Enum):
    SAFE = "SAFE"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


# ==========================================================
# SCHEMA CHUẨN – NORMALIZED RECORD
# ==========================================================

# ==========================================================
# SCHEMA CHUẨN – NORMALIZED RECORD (FINAL)
# ==========================================================

@dataclass
class NormalizedRecord:
    """
    Một record lừa đảo chuẩn sau khi normalize
    """

    # =====================
    # BẮT BUỘC (CORE)
    # =====================
    entity_type: EntityType          # PHONE / BANK / URL
    entity_value: str                # giá trị đã normalize
    source: str                      # facebook / tiktok / ncsc / police / phishtank / news
    country: str                     # VN / INT
    created_at: Optional[str] = None # ISO-8601 UTC

    # =====================
    # TÙY CHỌN (CONTEXT)
    # =====================
    raw_value: Optional[str] = None
    context: Optional[str] = None
    url: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None

    # =====================
    # RISK ENGINE – OUTPUT
    # =====================
    risk_level: RiskLevel = RiskLevel.UNKNOWN
    risk_score: Optional[int] = None          # 0 → 100
    confidence: Optional[float] = None        # 0 → 1

    # =====================
    # RISK ENGINE – INPUT SIGNALS
    # =====================
    report_stats: Dict[str, int] = field(
        default_factory=lambda: {
            "approved": 0,
            "pending": 0,
            "rejected": 0,
        }
    )

    risk_signals: list[str] = field(default_factory=list)

    # =====================
    # SYSTEM
    # =====================
    hash: str = field(init=False)

    # ======================================================
    # INIT
    # ======================================================
    def __post_init__(self):
        # chuẩn hóa entity_value
        self.entity_value = self.entity_value.strip()

        # auto created_at nếu chưa có
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

        # sinh hash chống trùng
        self.hash = self.generate_hash()

    # ======================================================
    # HASH FINGERPRINT
    # ======================================================
    def generate_hash(self) -> str:
        raw = f"{self.entity_type.value}|{self.entity_value}|{self.country}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # ======================================================
    # SERIALIZE
    # ======================================================
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["entity_type"] = self.entity_type.value
        data["risk_level"] = self.risk_level.value
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    # ======================================================
    # BASIC VALIDATION
    # ======================================================
    def is_valid(self) -> bool:
        if not self.entity_value:
            return False
        if not self.source:
            return False
        if self.country not in {"VN", "INT"}:
            return False
        return True
