"""
Academic Knowledge Layer Package for CurricuAlign AI Academic Engine.
"""

from backend.academic_engine.knowledge.academic_builder import AcademicKnowledgeBuilder
from backend.academic_engine.knowledge.academic_models import (
    AcademicKnowledgeStats,
    AcademicSnapshot,
    AcademicSnapshotMetadata,
    AcademicTechnologyRecord,
    AcademicTechnologyStatus,
)
from backend.academic_engine.knowledge.academic_repository import AcademicKnowledgeRepository
from backend.academic_engine.knowledge.academic_service import AcademicKnowledgeService
from backend.academic_engine.knowledge.exceptions import AcademicKnowledgeError, AcademicRecordNotFoundError, AcademicRepositoryError

__all__ = [
    "AcademicTechnologyRecord",
    "AcademicTechnologyStatus",
    "AcademicSnapshot",
    "AcademicSnapshotMetadata",
    "AcademicKnowledgeStats",
    "AcademicKnowledgeBuilder",
    "AcademicKnowledgeRepository",
    "AcademicKnowledgeService",
    "AcademicKnowledgeError",
    "AcademicRecordNotFoundError",
    "AcademicRepositoryError",
]
