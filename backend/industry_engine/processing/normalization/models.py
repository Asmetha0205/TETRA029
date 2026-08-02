"""
Data Models for CurricuAlign AI Technology Normalization Engine.

Defines the canonical Technology representation, the input TechnologyProfile,
unknown/rejected records, and the normalization report + result envelope.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TechnologyStatus(str, Enum):
    """
    Lifecycle status of a technology after normalization.
    """

    KNOWN = "known"
    UNKNOWN = "unknown"
    REJECTED = "rejected"


# Maps the 18 LLM extraction category keys to human-readable display categories.
CATEGORY_DISPLAY: Dict[str, str] = {
    "languages": "Programming Language",
    "frameworks": "Framework",
    "libraries": "Library",
    "databases": "Database",
    "cloud": "Cloud",
    "devops": "DevOps",
    "ai": "AI / ML",
    "vector_databases": "Vector Database",
    "llm_frameworks": "LLM Framework",
    "agent_frameworks": "Agent Framework",
    "operating_systems": "Operating System",
    "developer_tools": "Developer Tool",
    "version_control": "Version Control",
    "message_brokers": "Message Broker",
    "container_technologies": "Container Technology",
    "infrastructure_tools": "Infrastructure Tool",
    "monitoring_tools": "Monitoring Tool",
    "testing_frameworks": "Testing Framework",
}

VALID_CATEGORY_KEYS: List[str] = list(CATEGORY_DISPLAY.keys())

UNKNOWN_CATEGORY: str = "Unknown"


class TechnologyProfile(BaseModel):
    """
    Input profile containing raw, categorized technology values extracted
    by the LLM Technology Intelligence Engine.
    """

    job_id: Optional[str] = Field(default=None, description="Optional job identifier associated with the extraction.")
    categories: Dict[str, List[Any]] = Field(
        default_factory=dict,
        description="Category key -> list of raw extracted technology values.",
    )
    extraction_timestamp: Optional[str] = Field(default=None, description="ISO timestamp of the extraction.")

    @classmethod
    def from_raw(cls, raw: Dict[str, Any], job_id: Optional[str] = None) -> "TechnologyProfile":
        """
        Build a TechnologyProfile from a parsed dictionary.

        Only list-valued keys are treated as categories; all other keys are
        ignored so extra metadata in the payload never crashes normalization.
        """
        if not isinstance(raw, dict):
            raise TypeError(f"Expected a dict input, got {type(raw).__name__}")

        categories: Dict[str, List[Any]] = {}
        for key, value in raw.items():
            if isinstance(value, list):
                categories[str(key)] = value

        return cls(job_id=job_id, categories=categories)


class Technology(BaseModel):
    """
    Canonical Technology representation produced by the normalization engine.
    """

    id: str = Field(..., description="Unique canonical identifier (slugified).")
    canonical_name: str = Field(..., description="Single canonical display name.")
    category: str = Field(..., description="Canonical category label.")
    aliases: List[str] = Field(default_factory=list, description="Known aliases for this technology.")
    normalized_name: str = Field(..., description="Normalized form of the input value that produced this record.")
    status: TechnologyStatus = Field(default=TechnologyStatus.KNOWN)


class NormalizedTechnology(Technology):
    """
    A resolved technology plus audit trail of the raw variants that merged into it.
    """

    matched_variants: List[str] = Field(default_factory=list, description="All normalized input variants merged into this record.")
    source_category: Optional[str] = Field(default=None, description="Original LLM category key the value arrived under.")


class UnknownTechnology(BaseModel):
    """
    A technology flagged as unknown because it is not present in the registry.
    Never discarded silently; always surfaced for future approval.
    """

    technology: str = Field(..., description="Raw (normalized) technology value.")
    category: str = Field(default=UNKNOWN_CATEGORY, description="Category label (Unknown for unregistered technologies).")
    source_category: Optional[str] = Field(default=None, description="Original LLM category key the value arrived under.")


class RejectedValue(BaseModel):
    """
    A technology value rejected during validation with the reason it failed.
    """

    value: Any = Field(..., description="Original raw value.")
    category: str = Field(default="", description="Category key the value arrived under.")
    reason: str = Field(..., description="Human-readable rejection reason.")


class NormalizationReport(BaseModel):
    """
    Aggregate statistics for a single normalization run.
    """

    total_technologies: int = Field(default=0)
    known: int = Field(default=0)
    unknown: int = Field(default=0)
    duplicates_merged: int = Field(default=0)
    aliases_resolved: int = Field(default=0)
    rejected_values: int = Field(default=0)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class NormalizationResult(BaseModel):
    """
    Envelope returned by the normalization pipeline.
    """

    normalized: List[NormalizedTechnology] = Field(default_factory=list)
    unknown: List[UnknownTechnology] = Field(default_factory=list)
    rejected: List[RejectedValue] = Field(default_factory=list)
    report: NormalizationReport = Field(default_factory=NormalizationReport)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to the canonical output format:
        { "normalized": [...], "unknown": [...] }
        """
        return {
            "normalized": [
                {
                    "canonical_name": t.canonical_name,
                    "category": t.category,
                    "aliases": list(t.aliases),
                }
                for t in self.normalized
            ],
            "unknown": [
                {"technology": u.technology, "category": u.category}
                for u in self.unknown
            ],
        }
