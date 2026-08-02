"""
Data Models for the Academic Knowledge Layer.

Defines AcademicTechnologyRecord, AcademicSnapshot, and AcademicKnowledgeStats.
"""

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.industry_engine.knowledge.knowledge_models import VersionInfo


class AcademicTechnologyStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class AcademicTechnologyRecord(BaseModel):
    """
    Authoritative record representing a technology taught within an academic curriculum.
    Compatible with Industry Knowledge Layer records.
    """
    technology_id: str = Field(..., description="Unique technology ID slug (e.g. 'python').")
    canonical_name: str = Field(..., description="Canonical display name (e.g. 'Python').")
    category: str = Field(..., description="Category (e.g. 'Programming Languages').")
    aliases: List[str] = Field(default_factory=list)

    # Academic Provenance & Alignment Fields
    university: str = Field(default="Unknown University")
    department: str = Field(default="Computer Science")
    degree_program: str = Field(default="B.Tech Computer Science")
    course_code: str = Field(default="CS101")
    course_name: str = Field(default="Core Syllabus")
    semester: str = Field(default="Semester 1")
    credits: float = Field(default=3.0)
    module_name: str = Field(default="Core Technology Unit")
    learning_outcomes: List[str] = Field(default_factory=list)

    frequency: int = Field(default=1, ge=0, description="Mention count across curriculum courses.")
    status: AcademicTechnologyStatus = Field(default=AcademicTechnologyStatus.ACTIVE)
    first_seen: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    last_updated: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    version: VersionInfo = Field(default_factory=VersionInfo)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def touch(self) -> None:
        """Bump timestamp and patch version."""
        now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.last_updated = now_ts
        self.version = self.version.increment_patch()


class AcademicSnapshotMetadata(BaseModel):
    """Metadata for an Academic Knowledge Repository snapshot."""
    snapshot_id: str
    record_count: int
    created_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    description: str = Field(default="Academic Knowledge Snapshot")


class AcademicSnapshot(BaseModel):
    """Snapshot containing complete dump of Academic Technology Records."""
    metadata: AcademicSnapshotMetadata
    records: List[AcademicTechnologyRecord]


class AcademicKnowledgeStats(BaseModel):
    """Aggregate statistics for Academic Knowledge Layer."""
    total_technologies: int = 0
    total_courses: int = 0
    total_universities: int = 0
    categories: Dict[str, int] = Field(default_factory=dict)
    top_technologies: List[Dict[str, Any]] = Field(default_factory=list)
