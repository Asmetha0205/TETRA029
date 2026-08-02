"""
CurricuAlign AI - Technology Normalization Engine Package.
Phase 3.5: Canonical normalization of LLM-extracted technology intelligence.
"""

from backend.industry_engine.processing.normalization.models import (
    CATEGORY_DISPLAY,
    NormalizationReport,
    NormalizationResult,
    NormalizedTechnology,
    RejectedValue,
    Technology,
    TechnologyProfile,
    TechnologyStatus,
    UnknownTechnology,
    VALID_CATEGORY_KEYS,
)
from backend.industry_engine.processing.normalization.config import (
    NormalizationConfig,
    UnknownPolicy,
    ValidationRules,
)
from backend.industry_engine.processing.normalization.exceptions import (
    NormalizationError,
    MalformedInputError,
    EmptyTechnologyNameError,
    InvalidTechnologyNameError,
    UnknownCategoryError,
    InvalidAliasError,
    DuplicateCanonicalIdError,
    TechnologyNotRegisteredError,
)
from backend.industry_engine.processing.normalization.normalizer import TechnologyNormalizer
from backend.industry_engine.processing.normalization.technology_registry import (
    TechnologyEntry,
    TechnologyRegistry,
)
from backend.industry_engine.processing.normalization.alias_resolver import AliasResolver
from backend.industry_engine.processing.normalization.canonicalizer import Canonicalizer
from backend.industry_engine.processing.normalization.category_mapper import CategoryMapper
from backend.industry_engine.processing.normalization.duplicate_merger import DuplicateMerger
from backend.industry_engine.processing.normalization.unknown_detector import UnknownDetector
from backend.industry_engine.processing.normalization.validator import TechnologyValidator
from backend.industry_engine.processing.normalization.pipeline import NormalizationPipeline

__all__ = [
    "CATEGORY_DISPLAY",
    "NormalizationReport",
    "NormalizationResult",
    "NormalizedTechnology",
    "RejectedValue",
    "Technology",
    "TechnologyProfile",
    "TechnologyStatus",
    "UnknownTechnology",
    "VALID_CATEGORY_KEYS",
    "NormalizationConfig",
    "UnknownPolicy",
    "ValidationRules",
    "NormalizationError",
    "MalformedInputError",
    "EmptyTechnologyNameError",
    "InvalidTechnologyNameError",
    "UnknownCategoryError",
    "InvalidAliasError",
    "DuplicateCanonicalIdError",
    "TechnologyNotRegisteredError",
    "TechnologyNormalizer",
    "TechnologyEntry",
    "TechnologyRegistry",
    "AliasResolver",
    "Canonicalizer",
    "CategoryMapper",
    "DuplicateMerger",
    "UnknownDetector",
    "TechnologyValidator",
    "NormalizationPipeline",
]
