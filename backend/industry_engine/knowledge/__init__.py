"""
Industry Knowledge Layer for CurricuAlign AI.

The single source of truth for every discovered industry technology.
Provides versioned knowledge records, immutable snapshots, diff-based
comparisons, and safe rollback capabilities.
"""

from backend.industry_engine.knowledge.exceptions import (
    DuplicateTechnology,
    InvalidVersionFormat,
    KnowledgeError,
    KnowledgeError as KnowledgeBaseError,
    RepositoryError,
    SnapshotComparisonError,
    SnapshotError,
    SnapshotNotFoundError,
    TechnologyIdConflict,
    TechnologyNotFound,
    ValidationError,
    VersionError,
)
from backend.industry_engine.knowledge.knowledge_builder import KnowledgeBuilder
from backend.industry_engine.knowledge.knowledge_models import (
    KnowledgeSnapshot,
    KnowledgeStats,
    SnapshotComparison,
    SnapshotMetadata,
    SnapshotStatus,
    TechnologyClassification,
    TechnologyKnowledgeRecord,
    TechnologyStatus,
    TechnologyTrend,
    VersionInfo,
)
from backend.industry_engine.knowledge.knowledge_repository import KnowledgeRepository
from backend.industry_engine.knowledge.knowledge_service import KnowledgeService
from backend.industry_engine.knowledge.snapshot_manager import SnapshotManager
from backend.industry_engine.knowledge.version_manager import VersionManager

__all__ = [
    # Exceptions
    "KnowledgeError",
    "KnowledgeBaseError",
    "TechnologyNotFound",
    "DuplicateTechnology",
    "TechnologyIdConflict",
    "SnapshotError",
    "SnapshotNotFoundError",
    "SnapshotComparisonError",
    "VersionError",
    "InvalidVersionFormat",
    "ValidationError",
    "RepositoryError",
    # Enums
    "TechnologyStatus",
    "TechnologyTrend",
    "TechnologyClassification",
    "SnapshotStatus",
    # Models
    "VersionInfo",
    "TechnologyKnowledgeRecord",
    "SnapshotMetadata",
    "KnowledgeSnapshot",
    "SnapshotComparison",
    "KnowledgeStats",
    # Components
    "VersionManager",
    "KnowledgeRepository",
    "SnapshotManager",
    "KnowledgeBuilder",
    # Service
    "KnowledgeService",
]
