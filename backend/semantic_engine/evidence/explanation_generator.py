"""
Explanation Generator for Evidence Engine.

Generates human-readable narrative explanations detailing why a technology is Covered, Partial, or a Gap.
"""

import logging
from typing import Optional

from backend.semantic_engine.models.semantic_models import CoverageClassificationEnum

logger = logging.getLogger("semantic_engine.evidence.explanation_generator")


class ExplanationGenerator:
    """Generates natural language evidence explanations."""

    @classmethod
    def generate_explanation(
        cls,
        academic_skill: Optional[str],
        industry_skill: str,
        similarity: float,
        classification: CoverageClassificationEnum,
        demand_percentage: float = 0.0,
    ) -> str:
        """
        Generate explanation sentence.

        Returns:
            Human readable evidence sentence.
        """
        pct_str = f"{demand_percentage:.1f}%" if demand_percentage > 0 else "high demand"

        if classification == CoverageClassificationEnum.COVERED:
            if academic_skill and academic_skill.lower() == industry_skill.lower():
                return f"{industry_skill} appears in {pct_str} of industry jobs and is fully taught in the curriculum."
            return f"Curriculum skill '{academic_skill}' directly matches industry technology '{industry_skill}' (similarity {similarity:.2f})."

        elif classification == CoverageClassificationEnum.PARTIAL:
            return f"{industry_skill} appears in {pct_str} of industry jobs. Curriculum covers {academic_skill} conceptually but not {industry_skill} explicitly (similarity {similarity:.2f})."

        else: # GAP
            return f"{industry_skill} appears in {pct_str} of industry jobs but is missing from the academic curriculum."
