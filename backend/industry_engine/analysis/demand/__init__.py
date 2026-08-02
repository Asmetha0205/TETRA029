"""
Demand & Trend Intelligence Engine for CurricuAlign AI.

Converts raw frequency statistics into meaningful Industry Intelligence.
"""

from backend.industry_engine.analysis.demand.demand_engine import DemandEngine
from backend.industry_engine.analysis.demand.trend_engine import TrendEngine

__all__ = ["DemandEngine", "TrendEngine"]
