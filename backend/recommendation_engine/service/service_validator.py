"""
Service Validator for Recommendation Service.
Validates input requests, checking for required gap fields and format values.
"""

from typing import List
from pydantic import BaseModel, Field
from backend.recommendation_engine.service.service_models import ExportReportRequest, GenerateRecommendationsRequest
from backend.recommendation_engine.utils.logger import recommendation_logger_tagged


class ServiceValidationResult(BaseModel):
    """Validation report for service request inputs."""
    is_valid: bool = True
    errors: List[str] = Field(default_factory=list)


class ServiceValidator:
    """
    Validates input parameters passed to RecommendationService methods.
    """

    @classmethod
    def validate_generate_request(cls, req: GenerateRecommendationsRequest) -> ServiceValidationResult:
        """Validate recommendation generation request."""
        errors = []
        if not req.gap_analysis_data:
            errors.append("gap_analysis_data is required and cannot be empty.")

        gaps = req.gap_analysis_data.get("gap", [])
        if not gaps and not req.target_gaps:
            errors.append("No gaps found in gap_analysis_data and target_gaps list is empty.")

        is_valid = len(errors) == 0
        if not is_valid:
            recommendation_logger_tagged.warning(f"Generate Request Validation Failed: {errors}")

        return ServiceValidationResult(is_valid=is_valid, errors=errors)

    @classmethod
    def validate_export_request(cls, req: ExportReportRequest) -> ServiceValidationResult:
        """Validate export request parameters."""
        errors = []
        fmt = req.format.lower().strip()
        if fmt not in ["json", "markdown", "pdf", "html"]:
            errors.append(f"Unsupported report export format '{req.format}'. Must be json, markdown, or pdf.")

        is_valid = len(errors) == 0
        return ServiceValidationResult(is_valid=is_valid, errors=errors)
