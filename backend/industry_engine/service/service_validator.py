"""
Service Validator for the Industry Service Layer.
"""

from backend.industry_engine.knowledge.exceptions import ValidationError


class ServiceValidator:
    """Validator for business service layer arguments."""

    @staticmethod
    def validate_technology_id(technology_id: str) -> str:
        if not technology_id or not technology_id.strip():
            raise ValidationError("technology_id must be a non-empty string.")
        return technology_id.strip().lower()

    @staticmethod
    def validate_limit(limit: int, min_val: int = 1, max_val: int = 500) -> int:
        if not (min_val <= limit <= max_val):
            raise ValidationError(f"limit must be between {min_val} and {max_val}, got {limit}.")
        return limit

    @staticmethod
    def validate_query(query: str) -> str:
        if not query or not query.strip():
            raise ValidationError("query string must be non-empty.")
        return query.strip()
