"""
Academic Service Layer Package for CurricuAlign AI Academic Engine.
"""

from backend.academic_engine.service.academic_service import AcademicService
from backend.academic_engine.service.exceptions import AcademicServiceError, CourseNotFoundError, DocumentNotFoundError, PipelineExecutionError
from backend.academic_engine.service.service_models import AcademicHealthStatus, AcademicPipelineSummary, ComponentHealth
from backend.academic_engine.service.service_validator import AcademicServiceValidator

__all__ = [
    "AcademicService",
    "AcademicServiceValidator",
    "AcademicPipelineSummary",
    "AcademicHealthStatus",
    "ComponentHealth",
    "AcademicServiceError",
    "DocumentNotFoundError",
    "CourseNotFoundError",
    "PipelineExecutionError",
]
