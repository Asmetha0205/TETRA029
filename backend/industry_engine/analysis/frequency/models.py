"""
Data Models for the CurricuAlign AI Technology Frequency Analysis Engine.

Defines the canonical per-technology frequency, per-category aggregation,
per-role distribution, computed statistics, and the envelope report model.
"""

import datetime
from collections import Counter
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class JobTechnologyRecord(BaseModel):
    """
    A single job with its normalized technologies used as input to the engine.
    """

    job_id: str = Field(..., description="Unique job identifier.")
    technologies: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Category key to list of canonical technology names.",
    )
    role: Optional[str] = Field(
        default=None,
        description="Job title used for per-role aggregation.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata such as source, location, or company.",
    )


class TechnologyFrequency(BaseModel):
    """
    Aggregated frequency metrics for a single technology.
    """

    name: str = Field(..., description="Canonical technology name.")
    category: str = Field(..., description="Canonical category label.")
    mentions: int = Field(..., description="Total number of times the technology appeared across all categories.")
    unique_jobs: int = Field(..., description="Number of distinct jobs that mention this technology.")
    percentage: float = Field(..., description="Percentage of total jobs that mention this technology.")
    rank: int = Field(..., description="Occurrence rank relative to other technologies (1 = most frequent).")


class CategoryFrequency(BaseModel):
    """
    Aggregated frequency metrics for a technology category.
    """

    category: str = Field(..., description="Canonical category label.")
    mentions: int = Field(..., description="Total mentions of all technologies within this category.")
    unique_technologies: int = Field(..., description="Number of distinct technologies found in this category.")
    unique_jobs: int = Field(..., description="Number of distinct jobs that mention at least one tech in this category.")


class RoleTechnology(BaseModel):
    """
    A technology and its percentage within a single role.
    """

    technology: str = Field(..., description="Technology name.")
    percentage: float = Field(..., description="Percentage of jobs within this role that mention the technology.")


class RoleFrequency(BaseModel):
    """
    Per-role technology frequency distribution.
    """

    role: str = Field(..., description="Job role title.")
    job_count: int = Field(..., description="Number of jobs with this role.")
    top_technologies: List[RoleTechnology] = Field(
        default_factory=list,
        description="Top technologies by percentage within the role.",
    )


class FrequencyStatistics(BaseModel):
    """
    Computed statistical metrics over the full frequency dataset.
    """

    top_technologies: List[TechnologyFrequency] = Field(
        default_factory=list,
        description="Top N technologies across all categories.",
    )
    top_per_category: Dict[str, List[TechnologyFrequency]] = Field(
        default_factory=dict,
        description="Top N technologies per canonical category.",
    )
    total_unique_technologies: int = Field(default=0)
    average_technologies_per_job: float = Field(default=0.0)
    technology_diversity_score: float = Field(
        default=0.0,
        description="Ratio of unique techs mentioned to total mentions as a proxy for diversity.",
    )
    most_common_combinations: List[List[str]] = Field(
        default_factory=list,
        description="Most frequent ordered pairs of co-occurring technologies.",
    )


class FrequencyReport(BaseModel):
    """
    Envelope returned by the frequency analysis engine.
    """

    summary: Dict[str, Any] = Field(default_factory=dict)
    technologies: List[TechnologyFrequency] = Field(default_factory=list)
    categories: List[CategoryFrequency] = Field(default_factory=list)
    roles: List[RoleFrequency] = Field(default_factory=list)
    statistics: FrequencyStatistics = Field(default_factory=FrequencyStatistics)
    generation_timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
    )