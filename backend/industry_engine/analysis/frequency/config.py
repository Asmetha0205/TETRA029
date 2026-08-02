"""
Configuration for the Technology Frequency Analysis Engine.

Supports batched processing thresholds, minimum-mention floor for noise
reduction, and role-analysis switches.
"""

from pydantic import BaseModel, Field


class FrequencyConfig(BaseModel):
    """
    Central configuration for the frequency analysis engine.
    """

    batch_size: int = Field(
        default=512,
        ge=1,
        description="Number of job records processed in a single batch for streaming workflows.",
    )
    min_mentions_threshold: int = Field(
        default=0,
        ge=0,
        description="Minimum number of mentions before a technology is included in top-N reports.",
    )
    top_n_limit: int = Field(
        default=10,
        ge=1,
        description="Default number of technologies returned by top-N queries.",
    )
    top_n_per_category: int = Field(
        default=5,
        ge=1,
        description="Default number of technologies returned per category in top-N queries.",
    )
    include_unknown_technologies: bool = Field(
        default=False,
        description="When True, technologies marked as unknown by normalization are included in counts.",
    )
    compute_role_statistics: bool = Field(
        default=True,
        description="When True, per-role technology frequency is calculated.",
    )
    compute_category_statistics: bool = Field(
        default=True,
        description="When True, per-category frequency aggregation is calculated.",
    )
    compute_combination_statistics: bool = Field(
        default=False,
        description="When True, most-common technology combinations are computed (can be expensive for large datasets).",
    )
    combination_max_technologies: int = Field(
        default=10,
        ge=1,
        description="Maximum technologies per job to consider when computing frequent combinations.",
    )
    combination_max_jobs: int = Field(
        default=5000,
        ge=1,
        description="Maximum jobs to scan when computing frequent technology combinations.",
    )
    role_field: str = Field(
        default="title",
        description="Field name used for role-based aggregation.",
    )