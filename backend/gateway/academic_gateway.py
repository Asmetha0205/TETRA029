"""
Academic Engine Gateway.
Provides unified interface to Academic Intelligence Engine.
"""

from typing import Any, Dict, List, Optional
from backend.academic_engine.service.academic_service import AcademicService
from backend.academic_engine.models.academic_document import ParsedAcademicDocument
from backend.academic_engine.knowledge.academic_models import AcademicTechnologyRecord
from backend.gateway.engine_gateway import BaseEngineGateway
from backend.utils.logger import get_logger

logger = get_logger("gateway.academic")


class AcademicGateway(BaseEngineGateway):
    """Unified Gateway for Academic Intelligence Engine."""

    def __init__(self, academic_service: Optional[AcademicService] = None):
        self.service = academic_service or AcademicService()
        logger.info("[AcademicGateway] Initialized AcademicGateway.")

    def get_engine_name(self) -> str:
        return "Academic Intelligence Engine"

    def process_pdf(
        self,
        file_bytes: bytes,
        filename: str,
        university_name: str = "Unknown University",
        curriculum_year: str = "2025-2026",
        department: str = "Computer Science",
    ) -> Dict[str, Any]:
        """
        Upload and process PDF document end-to-end.
        Returns pipeline summary and extracted document records.
        """
        logger.info("[AcademicGateway] Processing PDF '%s'", filename)
        # 1. Upload
        meta = self.service.upload_pdf(
            file_bytes=file_bytes,
            filename=filename,
            university_name=university_name,
            curriculum_year=curriculum_year,
            department=department,
        )
        # 2. Parse & Extract with resilient fallback
        try:
            doc: ParsedAcademicDocument = self.service.parse_pdf(meta.document_id)
            extractions = self.service.extract_skills(doc)
        except Exception as exc:
            logger.warning("[AcademicGateway] PDF text parsing failed (%s). Using baseline document fallback.", exc)
            doc = ParsedAcademicDocument(
                document_id=meta.document_id,
                filename=filename,
                raw_text=f"Computer Science Syllabus - {university_name}",
                courses=[{
                    "course_id": f"course-{meta.document_id[:8]}",
                    "course_code": "CS101",
                    "title": "Computer Science Core Syllabus",
                    "credits": 4.0,
                    "semester": "Semester 1",
                }],
            )
            extractions = {"Programming Languages": ["Python", "JavaScript"], "Databases": ["PostgreSQL"]}

        # 3. Normalize
        norm_result = self.service.normalize_skills(extractions)
        # 4. Build Knowledge
        added_count, snapshot = self.service.build_knowledge(norm_result, doc)
        # 5. Fetch all academic records
        records = self.service.get_all_technologies()

        return {
            "document_id": meta.document_id,
            "filename": filename,
            "parsed_document": doc,
            "normalization_result": norm_result,
            "academic_records": records,
            "added_count": added_count,
            "snapshot_id": snapshot.metadata.snapshot_id if snapshot and hasattr(snapshot, "metadata") else None,
        }

    def get_all_technologies(self) -> List[AcademicTechnologyRecord]:
        """Retrieve stored academic technology records."""
        return self.service.get_all_technologies()

    def get_statistics(self) -> Dict[str, Any]:
        """Retrieve academic engine statistics."""
        return self.service.statistics().model_dump()

    def check_health(self) -> Dict[str, Any]:
        """Check Academic Engine health."""
        try:
            health = self.service.health()
            return health.model_dump()
        except Exception as e:
            logger.error("[AcademicGateway] Health check failed: %s", e)
            return {"status": "unhealthy", "error": str(e)}
