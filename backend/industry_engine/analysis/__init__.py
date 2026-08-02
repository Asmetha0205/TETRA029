"""
Analysis modules for CurricuAlign AI Industry Engine.

Provides:
- Technology Frequency Analysis (Phase 3.6)
- Demand & Trend Intelligence Engine (Phase 3.7)
"""

from backend.industry_engine.analysis.frequency import FrequencyEngine
from backend.industry_engine.analysis.demand import DemandEngine, TrendEngine

__all__ = ["FrequencyEngine", "DemandEngine", "TrendEngine"]
