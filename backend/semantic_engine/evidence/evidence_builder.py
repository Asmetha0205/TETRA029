"""
Evidence Builder for CurricuAlign AI Semantic Intelligence Engine.

Builds structured EvidenceItem objects attached to SkillMatchResult items.
"""

import logging
from typing import Optional

from backend.semantic_engine.evidence.explanation_generator import ExplanationGenerator
from backend.semantic_engine.models.semantic_models import CoverageClassificationEnum, EvidenceItem

logger = logging.getLogger("semantic_engine.evidence.evidence_builder")


class EvidenceBuilder:
    """Builds EvidenceItem models."""

    @classmethod
    def build_evidence(
        cls,
        academic_skill: Optional[str],
        industry_skill: str,
        similarity: float,
        classification: CoverageClassificationEnum,
        demand_percentage: float = 0.0,
    ) -> EvidenceItem:
        """
        Build an EvidenceItem.
        """
        explanation = ExplanationGenerator.generate_explanation(
            academic_skill=academic_skill,
            industry_skill=industry_skill,
            similarity=similarity,
            classification=classification,
            demand_percentage=demand_percentage,
        )

        status_str = f"Covered by {academic_skill}" if academic_skill else "Missing in Curriculum"

        return EvidenceItem(
            summary=explanation,
            job_mention_percentage=round(demand_percentage, 1),
            curriculum_status=status_str,
            rationale=f"Classification '{classification.value}' derived from vector similarity {similarity:.2f}.",
        )
