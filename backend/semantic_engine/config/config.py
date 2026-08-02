"""
Configuration Settings for the CurricuAlign AI Semantic Intelligence Engine.
"""

from typing import Dict
from pydantic import BaseModel, Field


class SemanticThresholdConfig(BaseModel):
    """Configurable similarity thresholds for coverage classification."""
    covered_threshold: float = Field(default=0.85, ge=0.0, le=1.0, description="Covered if similarity >= threshold")
    partial_threshold: float = Field(default=0.60, ge=0.0, le=1.0, description="Partial if threshold <= similarity < covered")
    gap_threshold: float = Field(default=0.60, ge=0.0, le=1.0, description="Gap if similarity < threshold")


class SemanticEngineConfig(BaseModel):
    """Main configuration for Semantic Intelligence Engine."""
    top_k_candidates: int = Field(default=10, ge=1, le=100, description="Top-K vector search candidates")
    thresholds: SemanticThresholdConfig = Field(default_factory=SemanticThresholdConfig)

    # Category weightings for overall alignment score calculation
    category_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "AI / ML": 1.2,
            "Programming Languages": 1.1,
            "Cloud & DevOps": 1.1,
            "Databases": 1.0,
            "Frameworks & Libraries": 1.0,
            "Core CS & Mathematics": 0.9,
            "Developer Tools": 0.8,
        }
    )
