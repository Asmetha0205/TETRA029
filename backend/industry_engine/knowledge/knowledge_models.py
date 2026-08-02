"""
Data Models for the CurricuAlign AI Industry Knowledge Layer.

Defines the canonical technology knowledge record, snapshot models,
version tracking, comparison results, and statistics models.
All models use Pydantic v2 for validation and serialization.
"""

import datetime
import re
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Enums
# =============================================================================

class TechnologyStatus(str, Enum):
    """Lifecycle status of a technology in the knowledge layer."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class TechnologyTrend(str, Enum):
    """Trend direction for technology adoption."""
    EMERGING = "Emerging"
    RAPIDLY_RISING = "Rapidly Rising"
    RISING = "Rising"
    STABLE = "Stable"
    DECLINING = "Declining"
    LEGACY = "Legacy"
    DEPRECATED = "Deprecated"


class TechnologyClassification(str, Enum):
    """Technology lifecycle classification."""
    CORE = "Core Technology"
    SUPPORTING = "Supporting Technology"
    EMERGING = "Emerging Technology"
    EXPERIMENTAL = "Experimental"
    LEGACY = "Legacy"


class SnapshotStatus(str, Enum):
    """Status of a snapshot."""
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ROLLED_BACK = "rolled_back"


# =============================================================================
# Version Model
# =============================================================================

class VersionInfo(BaseModel):
    """Semantic versioning information for a technology record."""
    major: int = Field(default=1, ge=0, description="Major version number.")
    minor: int = Field(default=0, ge=0, description="Minor version number.")
    patch: int = Field(default=0, ge=0, description="Patch version number.")
    created_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="ISO timestamp when this version was created.",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="ISO timestamp when this version was last updated.",
    )
    snapshot_version: Optional[int] = Field(
        default=None,
        description="Snapshot number this version was part of, if any.",
    )

    def to_string(self) -> str:
        """Return version as semver string (e.g. '1.0.0')."""
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def from_string(cls, version_str: str) -> "VersionInfo":
        """Parse a semver string into VersionInfo."""
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version_str.strip())
        if not match:
            raise ValueError(f"Invalid semantic version format: '{version_str}'. Expected 'X.Y.Z'.")
        return cls(major=int(match.group(1)), minor=int(match.group(2)), patch=int(match.group(3)))

    def increment_major(self) -> "VersionInfo":
        """Return a new VersionInfo with major version bumped."""
        return VersionInfo(major=self.major + 1, minor=0, patch=0)

    def increment_minor(self) -> "VersionInfo":
        """Return a new VersionInfo with minor version bumped."""
        return VersionInfo(major=self.major, minor=self.minor + 1, patch=0)

    def increment_patch(self) -> "VersionInfo":
        """Return a new VersionInfo with patch version bumped."""
        return VersionInfo(major=self.major, minor=self.minor, patch=self.patch + 1)


# =============================================================================
# Core Technology Knowledge Record
# =============================================================================

class TechnologyKnowledgeRecord(BaseModel):
    """
    The single authoritative record for a technology in the Industry Knowledge Layer.

    Every technology discovered through the pipeline is stored as one of these records
    with all associated intelligence data.
    """
    technology_id: str = Field(
        ...,
        description="Unique slugified identifier (e.g. 'pytorch', 'redis').",
        min_length=1,
    )
    canonical_name: str = Field(
        ...,
        description="Single canonical display name (e.g. 'PyTorch', 'Redis').",
        min_length=1,
    )
    category: str = Field(
        ...,
        description="Canonical category label (e.g. 'AI / ML', 'Database').",
        min_length=1,
    )
    aliases: List[str] = Field(
        default_factory=list,
        description="Known aliases for this technology.",
    )
    description: str = Field(
        default="",
        description="Brief description of the technology and its role.",
    )
    frequency: int = Field(
        default=0,
        ge=0,
        description="Total number of job mentions across the dataset.",
    )
    demand_score: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Computed demand score (0-100).",
    )
    industry_score: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Combined industry intelligence score (0-100).",
    )
    trend: TechnologyTrend = Field(
        default=TechnologyTrend.STABLE,
        description="Current trend direction.",
    )
    growth: float = Field(
        default=0.0,
        description="Growth percentage (positive = growing, negative = declining).",
    )
    classification: TechnologyClassification = Field(
        default=TechnologyClassification.SUPPORTING,
        description="Lifecycle classification.",
    )
    related_technologies: List[str] = Field(
        default_factory=list,
        description="List of related technology IDs.",
    )
    role_coverage: Dict[str, float] = Field(
        default_factory=dict,
        description="Mapping of job role to percentage coverage.",
    )
    sources: List[str] = Field(
        default_factory=list,
        description="Data source identifiers that contributed to this record.",
    )
    status: TechnologyStatus = Field(
        default=TechnologyStatus.ACTIVE,
        description="Lifecycle status.",
    )
    first_seen: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="ISO timestamp when this technology was first discovered.",
    )
    last_updated: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="ISO timestamp when this record was last updated.",
    )
    version: VersionInfo = Field(
        default_factory=VersionInfo,
        description="Current semantic version of this record.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata (rank, percentage, score breakdowns, etc.).",
    )

    @field_validator("technology_id")
    @classmethod
    def validate_technology_id(cls, value: str) -> str:
        """Ensure technology_id is a clean slug."""
        value = value.strip().lower()
        if not value:
            raise ValueError("technology_id must be a non-empty string.")
        if not re.match(r"^[a-z0-9][a-z0-9_\-]*$", value):
            raise ValueError(
                f"technology_id '{value}' contains invalid characters. "
                "Use only lowercase alphanumeric, hyphens, and underscores."
            )
        return value

    @field_validator("canonical_name")
    @classmethod
    def validate_canonical_name(cls, value: str) -> str:
        """Ensure canonical_name is non-empty after stripping."""
        value = value.strip()
        if not value:
            raise ValueError("canonical_name must be a non-empty string.")
        return value

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        """Ensure category is non-empty after stripping."""
        value = value.strip()
        if not value:
            raise ValueError("category must be a non-empty string.")
        return value

    def touch(self) -> None:
        """Update the last_updated timestamp to now."""
        self.last_updated = datetime.datetime.now(datetime.timezone.utc).isoformat()


# =============================================================================
# Snapshot Models
# =============================================================================

class SnapshotMetadata(BaseModel):
    """Metadata for a knowledge snapshot."""
    snapshot_id: str = Field(..., description="Unique snapshot identifier.")
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="ISO timestamp when the snapshot was created.",
    )
    version: int = Field(default=1, ge=1, description="Monotonically increasing snapshot number.")
    technology_count: int = Field(default=0, ge=0, description="Number of technologies in the snapshot.")
    status: SnapshotStatus = Field(default=SnapshotStatus.ACTIVE, description="Snapshot status.")
    execution_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of the pipeline execution that produced this snapshot.",
    )
    description: str = Field(default="", description="Optional human-readable description.")


class KnowledgeSnapshot(BaseModel):
    """
    An immutable snapshot of the entire knowledge layer at a point in time.

    Snapshots are never modified after creation. Rollback creates a new
    active state from a snapshot's data, preserving history.
    """
    metadata: SnapshotMetadata
    records: List[TechnologyKnowledgeRecord] = Field(
        default_factory=list,
        description="Complete set of technology records at snapshot time.",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize snapshot to a dictionary."""
        return {
            "metadata": self.metadata.model_dump(),
            "records": [r.model_dump() for r in self.records],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeSnapshot":
        """Deserialize snapshot from a dictionary."""
        metadata = SnapshotMetadata(**data.get("metadata", {}))
        records = [TechnologyKnowledgeRecord(**r) for r in data.get("records", [])]
        return cls(metadata=metadata, records=records)


class SnapshotComparison(BaseModel):
    """Result of comparing two snapshots."""
    snapshot_a_id: str = Field(..., description="ID of the first snapshot.")
    snapshot_b_id: str = Field(..., description="ID of the second snapshot.")
    added: List[str] = Field(default_factory=list, description="Technology IDs present in B but not A.")
    removed: List[str] = Field(default_factory=list, description="Technology IDs present in A but not B.")
    changed: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Technology IDs that exist in both but have differences.",
    )
    unchanged: int = Field(default=0, description="Number of technologies unchanged between snapshots.")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Comparison summary statistics.")


# =============================================================================
# Statistics Model
# =============================================================================

class KnowledgeStats(BaseModel):
    """Aggregate statistics for the knowledge layer."""
    total_technologies: int = Field(default=0, ge=0)
    active_count: int = Field(default=0, ge=0)
    deprecated_count: int = Field(default=0, ge=0)
    archived_count: int = Field(default=0, ge=0)
    categories: Dict[str, int] = Field(default_factory=dict, description="Category to count mapping.")
    avg_demand_score: float = Field(default=0.0, ge=0, le=100)
    avg_industry_score: float = Field(default=0.0, ge=0, le=100)
    avg_frequency: float = Field(default=0.0, ge=0)
    snapshot_count: int = Field(default=0, ge=0)
    latest_snapshot_id: Optional[str] = Field(default=None)
    trend_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Trend label to count mapping.",
    )
    classification_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Classification label to count mapping.",
    )
