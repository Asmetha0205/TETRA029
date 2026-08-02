"""
API Controllers for Academic REST API.

Maps HTTP API requests to AcademicService methods.
"""

import logging
from typing import Any, Dict, List, Optional

from backend.academic_engine.api.schemas import (
    AcademicTechnologyListResponse,
    AcademicTechnologyResponse,
    CourseListResponse,
    CourseResponse,
    DocumentListResponse,
    PipelineSummaryResponse,
    UploadMetadataResponse,
)
from backend.academic_engine.service.academic_service import AcademicService

logger = logging.getLogger("academic_engine.api.controllers")


class AcademicController:
    """Controller mapping API routes to AcademicService."""

    def __init__(self, service: AcademicService) -> None:
        self.service = service

    def upload_pdf(
        self,
        file_bytes: bytes,
        filename: str,
        university_name: str = "Unknown University",
        curriculum_year: str = "2025-2026",
        department: str = "Computer Science",
    ) -> UploadMetadataResponse:
        logger.info("[API] POST /academic/upload (%s)", filename)
        meta = self.service.upload_pdf(
            file_bytes=file_bytes,
            filename=filename,
            university_name=university_name,
            curriculum_year=curriculum_year,
            department=department,
        )
        return UploadMetadataResponse.model_validate(meta.model_dump())

    def process_pipeline(
        self,
        file_bytes: bytes,
        filename: str,
        university_name: str = "Unknown University",
        curriculum_year: str = "2025-2026",
        department: str = "Computer Science",
    ) -> PipelineSummaryResponse:
        logger.info("[API] Pipeline Process (%s)", filename)
        summary = self.service.process_pipeline(
            file_bytes=file_bytes,
            filename=filename,
            university_name=university_name,
            curriculum_year=curriculum_year,
            department=department,
        )
        return PipelineSummaryResponse.model_validate(summary)

    def list_documents(self) -> DocumentListResponse:
        logger.info("[API] GET /academic/documents")
        docs = self.service.upload_service.list_documents()
        items = [UploadMetadataResponse.model_validate(d.model_dump()) for d in docs]
        return DocumentListResponse(total=len(items), documents=items)

    def get_document(self, document_id: str) -> UploadMetadataResponse:
        logger.info("[API] GET /academic/document/%s", document_id)
        doc = self.service.upload_service.get_document(document_id)
        if not doc:
            raise ValueError(f"Document '{document_id}' not found.")
        return UploadMetadataResponse.model_validate(doc.model_dump())

    def list_courses(self) -> CourseListResponse:
        logger.info("[API] GET /academic/courses")
        courses = self.service.get_courses()
        items = [
            CourseResponse(
                course_id=c.get("course_id", ""),
                course_code=c.get("course_code", ""),
                title=c.get("title", ""),
                credits=float(c.get("credits", 3.0)),
                semester=c.get("semester", "Semester 1"),
            )
            for c in courses
        ]
        return CourseListResponse(total=len(items), courses=items)

    def get_course(self, course_id: str) -> CourseResponse:
        logger.info("[API] GET /academic/course/%s", course_id)
        c = self.service.get_course(course_id)
        return CourseResponse(
            course_id=c.get("course_id", ""),
            course_code=c.get("course_code", ""),
            title=c.get("title", ""),
            credits=float(c.get("credits", 3.0)),
            semester=c.get("semester", "Semester 1"),
        )

    def list_technologies(self) -> AcademicTechnologyListResponse:
        logger.info("[API] GET /academic/technologies")
        records = self.service.get_all_technologies()
        items = [self._record_to_schema(r) for r in records]
        return AcademicTechnologyListResponse(total=len(items), technologies=items)

    def search_technologies(self, query: str) -> AcademicTechnologyListResponse:
        logger.info("[API] GET /academic/search?q=%s", query)
        records = self.service.search(query)
        items = [self._record_to_schema(r) for r in records]
        return AcademicTechnologyListResponse(total=len(items), technologies=items)

    def get_statistics(self) -> Dict[str, Any]:
        logger.info("[API] GET /academic/statistics")
        stats = self.service.statistics()
        return stats.model_dump()

    def get_health(self) -> Dict[str, Any]:
        logger.info("[API] GET /academic/health")
        health = self.service.health()
        return health.model_dump()

    @staticmethod
    def _record_to_schema(r: Any) -> AcademicTechnologyResponse:
        return AcademicTechnologyResponse(
            technology_id=r.technology_id,
            canonical_name=r.canonical_name,
            category=r.category,
            aliases=r.aliases,
            university=r.university,
            department=r.department,
            degree_program=r.degree_program,
            course_code=r.course_code,
            course_name=r.course_name,
            semester=r.semester,
            credits=r.credits,
            frequency=r.frequency,
            status=r.status.value if hasattr(r.status, "value") else str(r.status),
            version=r.version.to_string() if hasattr(r.version, "to_string") else str(r.version),
            metadata=r.metadata,
        )
