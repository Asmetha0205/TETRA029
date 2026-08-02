"""
Academic REST API Package for CurricuAlign AI Academic Engine.
"""

from backend.academic_engine.api.controllers import AcademicController
from backend.academic_engine.api.dependencies import get_academic_service, set_academic_service_instance
from backend.academic_engine.api.routes import router
from backend.academic_engine.api.schemas import (
    AcademicTechnologyListResponse,
    AcademicTechnologyResponse,
    CourseListResponse,
    CourseResponse,
    DocumentListResponse,
    PipelineSummaryResponse,
    UploadMetadataResponse,
)

__all__ = [
    "router",
    "AcademicController",
    "get_academic_service",
    "set_academic_service_instance",
    "UploadMetadataResponse",
    "DocumentListResponse",
    "AcademicTechnologyResponse",
    "AcademicTechnologyListResponse",
    "CourseResponse",
    "CourseListResponse",
    "PipelineSummaryResponse",
]
