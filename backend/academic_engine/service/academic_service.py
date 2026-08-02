"""
Academic Service for CurricuAlign AI Academic Intelligence Engine.

The single authoritative public interface for the entire Academic Engine.
Orchestrates Upload -> Parsing -> Extraction -> Normalization -> Knowledge Layer.
"""

import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.academic_engine.config.config import AcademicEngineConfig
from backend.academic_engine.upload.upload_service import UploadService
from backend.academic_engine.upload.metadata import DocumentUploadMetadata
from backend.academic_engine.parser.pdf_parser import PDFParser
from backend.academic_engine.models.academic_document import ParsedAcademicDocument
from backend.academic_engine.extraction.academic_extractor import AcademicExtractor
from backend.academic_engine.normalization.academic_normalizer import AcademicTechnologyNormalizer
from backend.academic_engine.knowledge.academic_service import AcademicKnowledgeService
from backend.academic_engine.knowledge.academic_models import (
    AcademicKnowledgeStats,
    AcademicSnapshot,
    AcademicTechnologyRecord,
)
from backend.academic_engine.service.exceptions import DocumentNotFoundError, CourseNotFoundError
from backend.academic_engine.service.service_models import AcademicHealthStatus, AcademicPipelineSummary, ComponentHealth
from backend.academic_engine.service.service_validator import AcademicServiceValidator

logger = logging.getLogger("academic_engine.service.academic_service")


class AcademicService:
    """
    Principal Business Facade for the Academic Intelligence Engine.
    """

    def __init__(
        self,
        config: Optional[AcademicEngineConfig] = None,
        repository_path: Optional[str] = None,
        snapshot_path: Optional[str] = None,
    ) -> None:
        self.config = config or AcademicEngineConfig()

        self.upload_service = UploadService(config=self.config)
        self.parser = PDFParser()
        self.extractor = AcademicExtractor(config=self.config)
        self.normalizer = AcademicTechnologyNormalizer()
        self.knowledge_service = AcademicKnowledgeService(
            repository_path=repository_path or self.config.repository_path,
            snapshot_path=snapshot_path or self.config.snapshot_path,
        )

        self._documents_cache: Dict[str, ParsedAcademicDocument] = {}

        logger.info("[Academic] AcademicService facade initialized successfully.")

    # ------------------------------------------------------------------
    # Step-by-Step Pipeline Steps
    # ------------------------------------------------------------------

    def upload_pdf(
        self,
        file_bytes: bytes,
        filename: str,
        university_name: str = "Unknown University",
        curriculum_year: str = "2025-2026",
        department: str = "Computer Science",
    ) -> DocumentUploadMetadata:
        """Upload and validate a curriculum PDF."""
        return self.upload_service.upload_pdf(
            file_bytes=file_bytes,
            filename=filename,
            university_name=university_name,
            curriculum_year=curriculum_year,
            department=department,
        )

    def parse_pdf(self, document_id: str) -> ParsedAcademicDocument:
        """Parse stored document into structured ParsedAcademicDocument."""
        clean_id = AcademicServiceValidator.validate_document_id(document_id)
        meta = self.upload_service.get_document(clean_id)
        if not meta:
            raise DocumentNotFoundError(f"Document '{clean_id}' not found in upload catalog.")

        doc = self.parser.parse_pdf(file_source=meta.storage_path, document_id=clean_id)
        self._documents_cache[clean_id] = doc
        return doc

    def extract_skills(self, document: ParsedAcademicDocument) -> Dict[str, List[str]]:
        """Extract technology categories from parsed document."""
        return self.extractor.extract_technologies_from_document(document)

    def normalize_skills(self, extracted_categories: Dict[str, List[str]]) -> Any:
        """Normalize extracted skills using Industry Engine registry."""
        return self.normalizer.normalize_academic_extractions(extracted_categories)

    def build_knowledge(self, normalization_result: Any, document: ParsedAcademicDocument) -> Tuple[int, Optional[AcademicSnapshot]]:
        """Build and ingest academic records into Knowledge Layer."""
        return self.knowledge_service.ingest_document_extractions(
            normalization_result=normalization_result,
            document=document,
            auto_snapshot=True,
        )

    # ------------------------------------------------------------------
    # Complete End-to-End Processing Pipeline
    # ------------------------------------------------------------------

    def process_pipeline(
        self,
        file_bytes: bytes,
        filename: str,
        university_name: str = "Unknown University",
        curriculum_year: str = "2025-2026",
        department: str = "Computer Science",
    ) -> Dict[str, Any]:
        """
        Execute full end-to-end processing pipeline:
        Upload -> Validate -> Store -> Parse -> Clean -> Extract -> Normalize -> Knowledge Builder -> Snapshot.

        Returns:
            Dict matching strict spec output requirements.
        """
        start_time = time.time()
        logger.info("[Academic] Starting End-to-End Academic Pipeline for '%s'.", filename)

        # 1. Upload
        meta = self.upload_pdf(
            file_bytes=file_bytes,
            filename=filename,
            university_name=university_name,
            curriculum_year=curriculum_year,
            department=department,
        )

        # 2. Parse
        doc = self.parse_pdf(meta.document_id)

        # 3. Extract
        extractions = self.extract_skills(doc)
        total_extracted = sum(len(v) for v in extractions.values())

        # 4. Normalize
        norm_result = self.normalize_skills(extractions)

        # 5. Knowledge Builder & Snapshot
        added_count, snapshot = self.build_knowledge(norm_result, doc)

        elapsed = round(time.time() - start_time, 1)

        summary = {
            "documents_processed": 1,
            "courses_detected": len(doc.courses),
            "technologies_extracted": total_extracted,
            "new_technologies": len(norm_result.unknown),
            "normalized": len(norm_result.normalized),
            "unknown": len(norm_result.unknown),
            "snapshot_created": snapshot is not None,
            "execution_time": f"{elapsed}s",
        }

        logger.info("[Academic] End-to-End Academic Pipeline Complete in %ss.", elapsed)
        return summary

    # ------------------------------------------------------------------
    # Course & Knowledge Queries
    # ------------------------------------------------------------------

    def get_courses(self) -> List[Dict[str, Any]]:
        """List all detected courses across parsed documents."""
        courses = []
        for doc in self._documents_cache.values():
            courses.extend(doc.courses)
        if not courses:
            # Baseline course fallback if cache is empty
            courses.append({
                "course_id": "course-cs101",
                "course_code": "CS101",
                "title": "Computer Science Core Syllabus",
                "credits": 4.0,
                "semester": "Semester 1",
            })
        return courses

    def get_course(self, course_id: str) -> Dict[str, Any]:
        """Retrieve course details by course_id."""
        clean_cid = course_id.lower().strip()
        for course in self.get_courses():
            if course.get("course_id", "").lower() == clean_cid or course.get("course_code", "").lower() == clean_cid:
                return course
        raise CourseNotFoundError(f"Course '{course_id}' not found.")

    def get_all_technologies(self) -> List[AcademicTechnologyRecord]:
        """Return all academic technology records."""
        return self.knowledge_service.get_all()

    def search(self, query: str) -> List[AcademicTechnologyRecord]:
        """Search academic technologies by keyword."""
        clean_q = AcademicServiceValidator.validate_query(query)
        return self.knowledge_service.search(clean_q)

    def statistics(self) -> AcademicKnowledgeStats:
        """Get aggregate statistics for Academic Knowledge Layer."""
        return self.knowledge_service.get_statistics()

    def create_snapshot(self, description: str = "Manual Academic Snapshot") -> AcademicSnapshot:
        """Create a manual knowledge snapshot."""
        return self.knowledge_service.create_snapshot(description=description)

    # ------------------------------------------------------------------
    # Engine Health Monitoring
    # ------------------------------------------------------------------

    def health(self) -> AcademicHealthStatus:
        """
        Evaluate overall health of the Academic Intelligence Engine.
        """
        components: Dict[str, ComponentHealth] = {}
        is_healthy = True

        # 1. Upload Service Check
        try:
            docs = self.upload_service.list_documents()
            components["upload_service"] = ComponentHealth(
                status="healthy",
                message=f"Operating normally ({len(docs)} documents cataloged).",
                details={"document_count": len(docs)},
            )
        except Exception as exc:
            is_healthy = False
            components["upload_service"] = ComponentHealth(status="unhealthy", message=str(exc))

        # 2. Knowledge Layer Check
        try:
            stats = self.knowledge_service.get_statistics()
            components["knowledge_layer"] = ComponentHealth(
                status="healthy",
                message=f"Operating normally ({stats.total_technologies} technologies stored).",
                details=stats.model_dump(),
            )
        except Exception as exc:
            is_healthy = False
            components["knowledge_layer"] = ComponentHealth(status="unhealthy", message=str(exc))

        overall = "healthy" if is_healthy else "unhealthy"
        return AcademicHealthStatus(status=overall, components=components)
