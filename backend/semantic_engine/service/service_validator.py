"""
Service Validator for Semantic Service Layer.
"""

from typing import List
from backend.academic_engine.knowledge.academic_models import AcademicTechnologyRecord
from backend.semantic_engine.service.exceptions import EmptyCurriculumError


class SemanticServiceValidator:
    """Validates incoming comparison requests."""

    @staticmethod
    def validate_academic_records(academic_records: List[AcademicTechnologyRecord]) -> None:
        """Ensure academic_records list is non-empty."""
        if not academic_records:
            raise EmptyCurriculumError("Curriculum comparison requires at least one academic technology record.")
