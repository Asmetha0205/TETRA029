"""
Coverage Classification Package for CurricuAlign AI Semantic Engine.
"""

from backend.semantic_engine.classification.coverage_classifier import CoverageClassifier
from backend.semantic_engine.classification.coverage_models import CoverageClassificationSummary
from backend.semantic_engine.classification.coverage_rules import CoverageRulesEvaluator
from backend.semantic_engine.classification.exceptions import ClassificationError, RuleEvaluationError

__all__ = [
    "CoverageClassifier",
    "CoverageClassificationSummary",
    "CoverageRulesEvaluator",
    "ClassificationError",
    "RuleEvaluationError",
]
