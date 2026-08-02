"""
FastAPI Routes for the Academic REST API.

Provides production-ready REST endpoints under the '/academic' prefix.
"""

import logging
from typing import Any, Dict, List, Optional

from backend.academic_engine.api.controllers import AcademicController
from backend.academic_engine.api.dependencies import get_academic_service
from backend.academic_engine.api.schemas import (
    AcademicTechnologyListResponse,
    AcademicTechnologyResponse,
    CourseListResponse,
    CourseResponse,
    DocumentListResponse,
    UploadMetadataResponse,
)
from backend.academic_engine.service.academic_service import AcademicService

logger = logging.getLogger("academic_engine.api.routes")

_FASTAPI_AVAILABLE = False
try:
    from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
    _FASTAPI_AVAILABLE = True
except ImportError:
    _FASTAPI_AVAILABLE = False


if _FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/academic", tags=["Academic Intelligence Engine"])

    @router.post("/upload", response_model=UploadMetadataResponse, summary="Upload curriculum PDF")
    async def upload_pdf(
        file: UploadFile = File(...),
        university_name: str = Form(default="Unknown University"),
        curriculum_year: str = Form(default="2025-2026"),
        department: str = Form(default="Computer Science"),
        service: AcademicService = Depends(get_academic_service),
    ):
        controller = AcademicController(service)
        try:
            content = await file.read()
            return controller.upload_pdf(
                file_bytes=content,
                filename=file.filename or "curriculum.pdf",
                university_name=university_name,
                curriculum_year=curriculum_year,
                department=department,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.get("/documents", response_model=DocumentListResponse, summary="List uploaded documents")
    def list_documents(service: AcademicService = Depends(get_academic_service)):
        controller = AcademicController(service)
        return controller.list_documents()

    @router.get("/document/{document_id}", response_model=UploadMetadataResponse, summary="Get document by ID")
    def get_document(document_id: str, service: AcademicService = Depends(get_academic_service)):
        controller = AcademicController(service)
        try:
            return controller.get_document(document_id)
        except Exception as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/courses", response_model=CourseListResponse, summary="List detected courses")
    def list_courses(service: AcademicService = Depends(get_academic_service)):
        controller = AcademicController(service)
        return controller.list_courses()

    @router.get("/course/{course_id}", response_model=CourseResponse, summary="Get course by ID")
    def get_course(course_id: str, service: AcademicService = Depends(get_academic_service)):
        controller = AcademicController(service)
        try:
            return controller.get_course(course_id)
        except Exception as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/technologies", response_model=AcademicTechnologyListResponse, summary="Get all academic technologies")
    def list_technologies(service: AcademicService = Depends(get_academic_service)):
        controller = AcademicController(service)
        return controller.list_technologies()

    @router.get("/search", response_model=AcademicTechnologyListResponse, summary="Search academic technologies")
    def search_technologies(
        q: str = Query(..., min_length=1, description="Search query string"),
        service: AcademicService = Depends(get_academic_service),
    ):
        controller = AcademicController(service)
        return controller.search_technologies(q)

    @router.get("/statistics", summary="Get academic intelligence statistics")
    def get_statistics(service: AcademicService = Depends(get_academic_service)):
        controller = AcademicController(service)
        return controller.get_statistics()

    @router.get("/health", summary="Get academic engine health")
    def get_health(service: AcademicService = Depends(get_academic_service)):
        controller = AcademicController(service)
        return controller.get_health()

else:
    class MockRoute:
        def __init__(self, path: str, method: str, endpoint: Any) -> None:
            self.path = path
            self.method = method
            self.endpoint = endpoint

    class MockRouter:
        def __init__(self, prefix: str = "/academic") -> None:
            self.prefix = prefix
            self.routes: List[MockRoute] = []

        def get(self, path: str, **kwargs: Any):
            def decorator(fn):
                self.routes.append(MockRoute(self.prefix + path, "GET", fn))
                return fn
            return decorator

        def post(self, path: str, **kwargs: Any):
            def decorator(fn):
                self.routes.append(MockRoute(self.prefix + path, "POST", fn))
                return fn
            return decorator

    router = MockRouter(prefix="/academic")

    @router.post("/upload")
    def upload_pdf(file_bytes: bytes, filename: str, service: Optional[AcademicService] = None):
        c = AcademicController(service or get_academic_service())
        return c.upload_pdf(file_bytes=file_bytes, filename=filename)

    @router.get("/documents")
    def list_documents(service: Optional[AcademicService] = None):
        c = AcademicController(service or get_academic_service())
        return c.list_documents()

    @router.get("/document/{document_id}")
    def get_document(document_id: str, service: Optional[AcademicService] = None):
        c = AcademicController(service or get_academic_service())
        return c.get_document(document_id)

    @router.get("/courses")
    def list_courses(service: Optional[AcademicService] = None):
        c = AcademicController(service or get_academic_service())
        return c.list_courses()

    @router.get("/course/{course_id}")
    def get_course(course_id: str, service: Optional[AcademicService] = None):
        c = AcademicController(service or get_academic_service())
        return c.get_course(course_id)

    @router.get("/technologies")
    def list_technologies(service: Optional[AcademicService] = None):
        c = AcademicController(service or get_academic_service())
        return c.list_technologies()

    @router.get("/search")
    def search_technologies(q: str, service: Optional[AcademicService] = None):
        c = AcademicController(service or get_academic_service())
        return c.search_technologies(q)

    @router.get("/statistics")
    def get_statistics(service: Optional[AcademicService] = None):
        c = AcademicController(service or get_academic_service())
        return c.get_statistics()

    @router.get("/health")
    def get_health(service: Optional[AcademicService] = None):
        c = AcademicController(service or get_academic_service())
        return c.get_health()
