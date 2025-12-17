"""
risk_engine.py
==============

Vai trò:
- Điều phối các scorer
- KHÔNG chứa công thức risk
- Giao việc kết luận cho risk_aggregator
"""

from typing import List

from etl.normalize.schema import NormalizedRecord

from etl.risk_engine.scorers.pattern_scorer import score_record as pattern_score_record

try:
    from etl.risk_engine.scorers.source_scorer import score_record as source_score_record
except ImportError:
    source_score_record = None

try:
    from etl.risk_engine.scorers.report_scorer import score_record as report_score_record
except ImportError:
    report_score_record = None

try:
    from etl.risk_engine.scorers.ai_scorer import score_record as ai_score_record
except ImportError:
    ai_score_record = None

# ✅ IMPORT AGGREGATION LAYER
from etl.risk_engine.risk_aggregator import aggregate_risk


# ==========================================================
# CORE ENGINE
# ==========================================================

class RiskEngine:
    """
    Orchestrator:
    NHIỀU SCORER → 1 KẾT LUẬN RỦI RO
    """

    def __init__(
        self,
        enable_pattern: bool = True,
        enable_source: bool = False,
        enable_report: bool = False,
        enable_ai: bool = False,
    ):
        self.enable_pattern = enable_pattern
        self.enable_source = enable_source
        self.enable_report = enable_report
        self.enable_ai = enable_ai

    # ======================================================
    # SCORE 1 RECORD
    # ======================================================
    def score(self, record: NormalizedRecord) -> NormalizedRecord:

        # 1️⃣ Pattern-based scoring (BẮT BUỘC)
        if self.enable_pattern:
            record = pattern_score_record(record)

        # 2️⃣ Source-based scoring
        if self.enable_source and source_score_record:
            record = source_score_record(record)

        # 3️⃣ Report-based scoring
        if self.enable_report and report_score_record:
            record = report_score_record(record)

        # 4️⃣ AI-based scoring
        if self.enable_ai and ai_score_record:
            record = ai_score_record(record)

        # 5️⃣ ✅ AGGREGATION (BẮT BUỘC)
        aggregate_risk(record)

        return record

    # ======================================================
    # SCORE BATCH
    # ======================================================
    def score_batch(self, records: List[NormalizedRecord]) -> List[NormalizedRecord]:
        return [self.score(r) for r in records]


# ==========================================================
# HELPER
# ==========================================================

def run_risk_engine(
    records: List[NormalizedRecord],
    *,
    enable_pattern: bool = True,
    enable_source: bool = False,
    enable_report: bool = False,
    enable_ai: bool = False,
) -> List[NormalizedRecord]:

    engine = RiskEngine(
        enable_pattern=enable_pattern,
        enable_source=enable_source,
        enable_report=enable_report,
        enable_ai=enable_ai,
    )

    return engine.score_batch(records)
