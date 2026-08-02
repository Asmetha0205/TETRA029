"""
Recommendation Validator for Recommendation Builder.
Validates finalized RecommendationItem instances before exposure or report export.
"""

from typing import List
from pydantic import BaseModel, Field
from backend.recommendation_engine.recommendation.recommendation_models import RecommendationItem, RecommendationResultSet
from backend.recommendation_engine.utils.logger import recommendation_logger_tagged


class RecommendationValidationReport(BaseModel):
    """Validation report for recommendation objects."""
    is_valid: bool = True
    total_validated: int = 0
    errors: List[str] = Field(default_factory=list)


class RecommendationValidator:
    """
    Validates finalized recommendation collections for field completeness and score integrity.
    """

    @classmethod
    def validate_item(cls, item: RecommendationItem) -> List[str]:
        """Validate a single RecommendationItem."""
        errs = []
        if not item.technology or not item.technology.strip():
            errs.append("Technology name is blank.")
        if item.industry_score < 0 or item.industry_score > 100:
            errs.append(f"Invalid industry_score {item.industry_score}")
        if item.confidence < 0.0 or item.confidence > 1.0:
            errs.append(f"Invalid confidence score {item.confidence}")
        if not item.learning_outcomes:
            errs.append("Learning outcomes list is empty.")
        if not item.lab or not item.lab.strip():
            errs.append("Lab exercise description is blank.")
        return errs

    @classmethod
    def validate_result_set(cls, result_set: RecommendationResultSet) -> RecommendationValidationReport:
        """Validate full recommendation result set."""
        all_errors = []
        for idx, rec in enumerate(result_set.recommendations):
            item_errs = cls.validate_item(rec)
            for e in item_errs:
                all_errors.append(f"Item {idx} ({rec.technology}): {e}")

        is_valid = len(all_errors) == 0
        if is_valid:
            recommendation_logger_tagged.info(f"Validated {len(result_set.recommendations)} recommendation items cleanly.")
        else:
            recommendation_logger_tagged.warning(f"Recommendation validation issues: {all_errors}")

        return RecommendationValidationReport(
            is_valid=is_valid,
            total_validated=len(result_set.recommendations),
            errors=all_errors
        )
