"""
Industry Service Layer Package for CurricuAlign AI Industry Intelligence Engine.

The single public facade for the Industry Engine.
"""

from backend.industry_engine.service.exceptions import HealthCheckError, IndustryServiceError, RefreshError, RollbackError
from backend.industry_engine.service.industry_service import IndustryService
from backend.industry_engine.service.service_models import ComponentHealth, IndustryHealthStatus, RefreshRequestOptions, SimilarSearchResultItem
from backend.industry_engine.service.service_validator import ServiceValidator

__all__ = [
    # Exceptions
    "IndustryServiceError",
    "RefreshError",
    "HealthCheckError",
    "RollbackError",
    # Models
    "ComponentHealth",
    "IndustryHealthStatus",
    "SimilarSearchResultItem",
    "RefreshRequestOptions",
    # Validator
    "ServiceValidator",
    # Facade Service
    "IndustryService",
]
