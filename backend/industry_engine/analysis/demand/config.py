"""
Configuration for the Demand & Trend Intelligence Engine.

Supports configurable weights, thresholds, and classification parameters.
"""

from pydantic import BaseModel, Field


class DemandWeights(BaseModel):
    """Weights for demand score calculation components."""
    frequency: float = Field(default=0.35, ge=0, le=1, description="Weight for job frequency.")
    coverage: float = Field(default=0.25, ge=0, le=1, description="Weight for unique job coverage.")
    category_importance: float = Field(default=0.15, ge=0, le=1, description="Weight for category importance.")
    role_importance: float = Field(default=0.15, ge=0, le=1, description="Weight for role importance.")
    rank_position: float = Field(default=0.10, ge=0, le=1, description="Weight for technology rank.")

    def validate_weights_sum(self) -> bool:
        """Check that weights sum to approximately 1.0."""
        total = self.frequency + self.coverage + self.category_importance + self.role_importance + self.rank_position
        return abs(total - 1.0) < 0.001


class TrendThresholds(BaseModel):
    """Thresholds for trend direction classification."""
    emerging_growth: float = Field(default=100.0, description="Min growth % for Emerging.")
    rapidly_rising_growth: float = Field(default=50.0, description="Min growth % for Rapidly Rising.")
    rising_growth: float = Field(default=10.0, description="Min growth % for Rising.")
    declining_threshold: float = Field(default=-10.0, description="Max growth % for Declining.")
    legacy_threshold: float = Field(default=-30.0, description="Max growth % for Legacy.")
    deprecated_threshold: float = Field(default=-60.0, description="Max growth % for Deprecated.")
    min_data_points: int = Field(default=2, ge=1, description="Minimum data points for trend analysis.")
    moving_average_window: int = Field(default=3, ge=2, description="Window size for moving average.")


class GrowthThresholds(BaseModel):
    """Thresholds for growth detection and classification."""
    significant_growth: float = Field(default=25.0, description="Min growth % for significant growth.")
    explosive_growth: float = Field(default=100.0, description="Min growth % for explosive growth.")
    decline_threshold: float = Field(default=-10.0, description="Max growth % for decline.")
    steep_decline: float = Field(default=-50.0, description="Max growth % for steep decline.")
    min_mentions: int = Field(default=5, ge=0, description="Minimum mentions to consider growth.")


class ClassificationThresholds(BaseModel):
    """Thresholds for technology classification."""
    core_min_score: float = Field(default=80.0, ge=0, le=100, description="Min score for Core Technology.")
    supporting_min_score: float = Field(default=50.0, ge=0, le=100, description="Min score for Supporting Technology.")
    emerging_min_score: float = Field(default=30.0, ge=0, le=100, description="Min score for Emerging Technology.")
    experimental_min_score: float = Field(default=10.0, ge=0, le=100, description="Min score for Experimental.")
    legacy_max_score: float = Field(default=30.0, ge=0, le=100, description="Max score for Legacy classification.")
    core_min_mentions: int = Field(default=100, ge=0, description="Min mentions for Core Technology.")
    emerging_max_mentions: int = Field(default=50, ge=0, description="Max mentions for Emerging Technology.")


class SnapshotConfig(BaseModel):
    """Configuration for historical snapshot management."""
    max_snapshots: int = Field(default=52, ge=1, description="Maximum number of snapshots to retain.")
    auto_prune: bool = Field(default=True, description="Automatically prune old snapshots.")
    snapshot_interval_hours: int = Field(default=24, ge=1, description="Minimum hours between snapshots.")


class IndustryScoreWeights(BaseModel):
    """Weights for industry intelligence score calculation."""
    demand: float = Field(default=0.30, ge=0, le=1, description="Weight for demand component.")
    growth: float = Field(default=0.25, ge=0, le=1, description="Weight for growth component.")
    role_importance: float = Field(default=0.20, ge=0, le=1, description="Weight for role importance.")
    category_importance: float = Field(default=0.15, ge=0, le=1, description="Weight for category importance.")
    popularity: float = Field(default=0.10, ge=0, le=1, description="Weight for technology popularity.")


class CategoryImportance(BaseModel):
    """Importance scores for technology categories."""
    scores: dict = Field(
        default_factory=lambda: {
            "Programming Language": 1.0,
            "Framework": 0.9,
            "Library": 0.8,
            "Database": 0.85,
            "Cloud": 0.9,
            "DevOps": 0.8,
            "AI / ML": 0.95,
            "Vector Database": 0.7,
            "LLM Framework": 0.85,
            "Agent Framework": 0.75,
            "Operating System": 0.6,
            "Developer Tool": 0.7,
            "Version Control": 0.8,
            "Message Broker": 0.65,
            "Container Technology": 0.8,
            "Infrastructure Tool": 0.7,
            "Monitoring Tool": 0.6,
            "Testing Framework": 0.75,
            "Unknown": 0.3,
        }
    )

    def get_score(self, category: str) -> float:
        """Get importance score for a category."""
        return self.scores.get(category, 0.5)


class RoleImportance(BaseModel):
    """Importance scores for job roles."""
    scores: dict = Field(
        default_factory=lambda: {
            "Software Engineer": 0.9,
            "Data Scientist": 0.85,
            "Machine Learning Engineer": 0.95,
            "DevOps Engineer": 0.8,
            "Cloud Architect": 0.85,
            "Backend Developer": 0.9,
            "Frontend Developer": 0.85,
            "Full Stack Developer": 0.9,
            "Data Engineer": 0.85,
            "AI Engineer": 0.95,
            "Platform Engineer": 0.8,
            "Site Reliability Engineer": 0.75,
            "Security Engineer": 0.7,
            "Mobile Developer": 0.8,
            "QA Engineer": 0.65,
            "Technical Lead": 0.9,
            "Engineering Manager": 0.85,
        }
    )

    def get_score(self, role: str) -> float:
        """Get importance score for a role."""
        return self.scores.get(role, 0.5)


class DemandConfig(BaseModel):
    """Central configuration for the Demand & Trend Intelligence Engine."""
    demand_weights: DemandWeights = Field(default_factory=DemandWeights)
    trend_thresholds: TrendThresholds = Field(default_factory=TrendThresholds)
    growth_thresholds: GrowthThresholds = Field(default_factory=GrowthThresholds)
    classification_thresholds: ClassificationThresholds = Field(default_factory=ClassificationThresholds)
    snapshot_config: SnapshotConfig = Field(default_factory=SnapshotConfig)
    industry_score_weights: IndustryScoreWeights = Field(default_factory=IndustryScoreWeights)
    category_importance: CategoryImportance = Field(default_factory=CategoryImportance)
    role_importance: RoleImportance = Field(default_factory=RoleImportance)

    def validate_all_weights(self) -> bool:
        """Validate that all weight configurations sum to approximately 1.0."""
        return (
            self.demand_weights.validate_weights_sum() and
            abs(self.industry_score_weights.demand + self.industry_score_weights.growth +
                self.industry_score_weights.role_importance + self.industry_score_weights.category_importance +
                self.industry_score_weights.popularity - 1.0) < 0.001
        )
