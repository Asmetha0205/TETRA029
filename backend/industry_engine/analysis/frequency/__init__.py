"""
CurricuAlign AI - Technology Frequency Analysis Engine Package.
Phase 3.6: Computes technology frequency statistics across industry job datasets.
"""

from backend.industry_engine.analysis.frequency.config import FrequencyConfig
from backend.industry_engine.analysis.frequency.models import (
    CategoryFrequency,
    FrequencyReport,
    FrequencyStatistics,
    JobTechnologyRecord,
    RoleFrequency,
    RoleTechnology,
    TechnologyFrequency,
)
from backend.industry_engine.analysis.frequency.exceptions import (
    DuplicateJobError,
    EmptyDatasetError,
    FrequencyAnalysisError,
    InvalidInputError,
    InvalidPercentageError,
    InvalidTechnologyError,
    MalformedRecordError,
    MissingCategoryError,
    NegativeCountError,
)
from backend.industry_engine.analysis.frequency.frequency_counter import FrequencyCounter
from backend.industry_engine.analysis.frequency.category_counter import CategoryCounter
from backend.industry_engine.analysis.frequency.role_counter import RoleCounter
from backend.industry_engine.analysis.frequency.statistics import StatisticsGenerator
from backend.industry_engine.analysis.frequency.aggregator import Aggregator
from backend.industry_engine.analysis.frequency.report_generator import ReportGenerator
from backend.industry_engine.analysis.frequency.frequency_engine import FrequencyEngine

__all__ = [
    "FrequencyConfig",
    "JobTechnologyRecord",
    "TechnologyFrequency",
    "CategoryFrequency",
    "RoleTechnology",
    "RoleFrequency",
    "FrequencyStatistics",
    "FrequencyReport",
    "FrequencyAnalysisError",
    "EmptyDatasetError",
    "DuplicateJobError",
    "InvalidTechnologyError",
    "MissingCategoryError",
    "MalformedRecordError",
    "NegativeCountError",
    "InvalidPercentageError",
    "InvalidInputError",
    "FrequencyCounter",
    "CategoryCounter",
    "RoleCounter",
    "StatisticsGenerator",
    "Aggregator",
    "ReportGenerator",
    "FrequencyEngine",
]