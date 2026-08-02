"""
Unit Tests for the Demand & Trend Intelligence Engine.

Tests for:
- Demand Engine
- Trend Engine
- Industry Score
- Technology Ranking
- Growth Detection
"""

import json
import pytest
from typing import Dict, Any

from backend.industry_engine.analysis.demand.config import (
    DemandConfig,
    DemandWeights,
    TrendThresholds,
)
from backend.industry_engine.analysis.demand.demand_calculator import DemandCalculator
from backend.industry_engine.analysis.demand.demand_engine import DemandEngine
from backend.industry_engine.analysis.demand.exceptions import (
    EmptyDatasetError,
    InvalidInputError,
    WeightSumError,
)
from backend.industry_engine.analysis.demand.growth_detector import GrowthDetector
from backend.industry_engine.analysis.demand.industry_score import IndustryScoreCalculator
from backend.industry_engine.analysis.demand.models import (
    DemandScore,
    SnapshotManager,
    TechnologyClassification,
    TechnologyFrequencyInput,
    TechnologySnapshot,
    TrendDirection,
    TrendMetrics,
)
from backend.industry_engine.analysis.demand.report_generator import ReportGenerator
from backend.industry_engine.analysis.demand.technology_ranker import TechnologyRanker
from backend.industry_engine.analysis.demand.trend_calculator import TrendCalculator
from backend.industry_engine.analysis.demand.trend_engine import TrendEngine


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_technologies() -> Dict[str, Dict[str, Any]]:
    """Sample technology frequency data."""
    return {
        "Python": {"mentions": 842, "percentage": 81, "rank": 1},
        "JavaScript": {"mentions": 750, "percentage": 72, "rank": 2},
        "TypeScript": {"mentions": 680, "percentage": 65, "rank": 3},
        "React": {"mentions": 520, "percentage": 50, "rank": 4},
        "Node.js": {"mentions": 480, "percentage": 46, "rank": 5},
        "Docker": {"mentions": 450, "percentage": 43, "rank": 6},
        "AWS": {"mentions": 440, "percentage": 42, "rank": 7},
        "Redis": {"mentions": 420, "percentage": 41, "rank": 8},
        "PostgreSQL": {"mentions": 400, "percentage": 38, "rank": 9},
        "LangGraph": {"mentions": 50, "percentage": 5, "rank": 50},
    }


@pytest.fixture
def sample_config() -> DemandConfig:
    """Sample configuration."""
    return DemandConfig()


@pytest.fixture
def demand_calculator(sample_config) -> DemandCalculator:
    """Create a DemandCalculator instance."""
    return DemandCalculator(config=sample_config)


@pytest.fixture
def trend_calculator(sample_config) -> TrendCalculator:
    """Create a TrendCalculator instance."""
    return TrendCalculator(config=sample_config)


@pytest.fixture
def growth_detector(sample_config) -> GrowthDetector:
    """Create a GrowthDetector instance."""
    return GrowthDetector(config=sample_config)


@pytest.fixture
def industry_score_calculator(sample_config) -> IndustryScoreCalculator:
    """Create an IndustryScoreCalculator instance."""
    return IndustryScoreCalculator(config=sample_config)


@pytest.fixture
def technology_ranker(sample_config) -> TechnologyRanker:
    """Create a TechnologyRanker instance."""
    return TechnologyRanker(config=sample_config)


@pytest.fixture
def demand_engine(sample_config) -> DemandEngine:
    """Create a DemandEngine instance."""
    return DemandEngine(config=sample_config)


# =============================================================================
# Demand Calculator Tests
# =============================================================================

class TestDemandCalculator:
    """Tests for the DemandCalculator class."""

    def test_calculate_scores_basic(self, demand_calculator, sample_technologies):
        """Test basic demand score calculation."""
        freq_inputs = {
            name: TechnologyFrequencyInput(**data)
            for name, data in sample_technologies.items()
        }
        scores = demand_calculator.calculate_scores(
            technologies=freq_inputs,
            total_jobs=1040,
        )
        assert len(scores) == len(sample_technologies)
        assert all(isinstance(s, DemandScore) for s in scores)
        assert all(0 <= s.demand_score <= 100 for s in scores)

    def test_calculate_scores_empty_raises(self, demand_calculator):
        """Test that empty dataset raises EmptyDatasetError."""
        with pytest.raises(EmptyDatasetError):
            demand_calculator.calculate_scores(
                technologies={},
                total_jobs=100,
            )

    def test_calculate_scores_invalid_jobs_raises(self, demand_calculator, sample_technologies):
        """Test that invalid total_jobs raises InvalidInputError."""
        freq_inputs = {
            name: TechnologyFrequencyInput(**data)
            for name, data in sample_technologies.items()
        }
        with pytest.raises(InvalidInputError):
            demand_calculator.calculate_scores(
                technologies=freq_inputs,
                total_jobs=0,
            )

    def test_top_demanded(self, demand_calculator, sample_technologies):
        """Test getting top demanded technologies."""
        freq_inputs = {
            name: TechnologyFrequencyInput(**data)
            for name, data in sample_technologies.items()
        }
        scores = demand_calculator.calculate_scores(
            technologies=freq_inputs,
            total_jobs=1040,
        )
        top_5 = demand_calculator.get_top_demanded(scores, top_n=5)
        assert len(top_5) == 5
        assert top_5[0].demand_score >= top_5[-1].demand_score

    def test_demand_distribution(self, demand_calculator, sample_technologies):
        """Test demand distribution calculation."""
        freq_inputs = {
            name: TechnologyFrequencyInput(**data)
            for name, data in sample_technologies.items()
        }
        scores = demand_calculator.calculate_scores(
            technologies=freq_inputs,
            total_jobs=1040,
        )
        distribution = demand_calculator.get_demand_distribution(scores)
        assert isinstance(distribution, dict)
        assert sum(distribution.values()) == len(sample_technologies)


# =============================================================================
# Trend Calculator Tests
# =============================================================================

class TestTrendCalculator:
    """Tests for the TrendCalculator class."""

    def test_calculate_trends_basic(self, trend_calculator):
        """Test basic trend calculation."""
        current = TechnologySnapshot(
            total_jobs=1000,
            technologies={
                "Python": {"name": "Python", "mentions": 842, "percentage": 81, "rank": 1},
                "Redis": {"name": "Redis", "mentions": 420, "percentage": 41, "rank": 8},
            }
        )
        previous = TechnologySnapshot(
            total_jobs=900,
            technologies={
                "Python": {"name": "Python", "mentions": 800, "percentage": 78, "rank": 1},
                "Redis": {"name": "Redis", "mentions": 350, "percentage": 35, "rank": 10},
            }
        )
        metrics = trend_calculator.calculate_trends(
            current_snapshot=current,
            previous_snapshots=[previous],
        )
        assert len(metrics) == 2
        assert all(isinstance(m, TrendMetrics) for m in metrics)

    def test_calculate_trends_no_history(self, trend_calculator):
        """Test trend calculation without historical data."""
        current = TechnologySnapshot(
            total_jobs=1000,
            technologies={
                "Python": {"name": "Python", "mentions": 842, "percentage": 81, "rank": 1},
            }
        )
        metrics = trend_calculator.calculate_trends(
            current_snapshot=current,
            previous_snapshots=[],
        )
        assert len(metrics) == 1
        assert metrics[0].trend == TrendDirection.STABLE

    def test_growth_rate_calculation(self, trend_calculator):
        """Test growth rate calculation."""
        growth = trend_calculator._calculate_growth_rate([100, 150])
        assert growth == 50.0

        growth = trend_calculator._calculate_growth_rate([100, 50])
        assert growth == -50.0


# =============================================================================
# Growth Detector Tests
# =============================================================================

class TestGrowthDetector:
    """Tests for the GrowthDetector class."""

    def test_detect_patterns_basic(self, growth_detector):
        """Test basic pattern detection."""
        metrics = [
            TrendMetrics(name="Python", growth_rate=5.0, momentum=1.0, volatility=2.0, data_points=3),
            TrendMetrics(name="LangGraph", growth_rate=150.0, momentum=10.0, volatility=5.0, data_points=3),
            TrendMetrics(name="LegacyTech", growth_rate=-40.0, momentum=-5.0, volatility=3.0, data_points=3),
        ]
        patterns = growth_detector.detect_patterns(metrics)
        assert len(patterns) == 3
        assert any(p.pattern_type == "Significant Growth" for p in patterns)
        assert any(p.pattern_type == "Decline" for p in patterns)

    def test_get_emerging_technologies(self, growth_detector):
        """Test getting emerging technologies."""
        from backend.industry_engine.analysis.demand.growth_detector import GrowthPattern
        patterns = [
            GrowthPattern("A", "Explosive Growth", 200.0, 0.9, "desc"),
            GrowthPattern("B", "Stable", 5.0, 0.8, "desc"),
            GrowthPattern("C", "Significant Growth", 60.0, 0.85, "desc"),
        ]
        emerging = growth_detector.get_emerging_technologies(patterns)
        assert len(emerging) == 2


# =============================================================================
# Industry Score Tests
# =============================================================================

class TestIndustryScoreCalculator:
    """Tests for the IndustryScoreCalculator class."""

    def test_calculate_scores_basic(self, industry_score_calculator):
        """Test basic industry score calculation."""
        demand_scores = [
            DemandScore(name="Python", demand_score=95, frequency_score=100, coverage_score=90,
                       category_score=100, role_score=90, rank_score=100),
            DemandScore(name="Redis", demand_score=60, frequency_score=50, coverage_score=60,
                       category_score=85, role_score=70, rank_score=50),
        ]
        trend_metrics = [
            TrendMetrics(name="Python", growth_rate=5.0, momentum=1.0),
            TrendMetrics(name="Redis", growth_rate=15.0, momentum=2.0),
        ]
        scores = industry_score_calculator.calculate_scores(
            demand_scores=demand_scores,
            trend_metrics=trend_metrics,
            total_technologies=2,
        )
        assert len(scores) == 2
        assert all(0 <= s.industry_score <= 100 for s in scores)
        assert all(isinstance(s.classification, TechnologyClassification) for s in scores)

    def test_classify_technology(self, industry_score_calculator):
        """Test technology classification."""
        demand = DemandScore(name="Test", demand_score=85, frequency_score=90, coverage_score=80,
                            category_score=85, role_score=80, rank_score=85)
        trend = TrendMetrics(name="Test", growth_rate=5.0, momentum=1.0)
        
        classification = industry_score_calculator._classify_technology(
            industry_score=85, demand=demand, trend=trend
        )
        assert classification == TechnologyClassification.CORE


# =============================================================================
# Technology Ranker Tests
# =============================================================================

class TestTechnologyRanker:
    """Tests for the TechnologyRanker class."""

    def test_generate_rankings_basic(self, technology_ranker):
        """Test basic ranking generation."""
        from backend.industry_engine.analysis.demand.models import IndustryScore
        technologies = [
            {"name": "Python", "demand_score": 95, "growth": 5.0, "industry_score": 98,
             "classification": TechnologyClassification.CORE, "mentions": 842, "percentage": 81, "rank": 1,
             "trend": TrendDirection.STABLE},
            {"name": "Redis", "demand_score": 60, "growth": 15.0, "industry_score": 70,
             "classification": TechnologyClassification.SUPPORTING, "mentions": 420, "percentage": 41, "rank": 8,
             "trend": TrendDirection.RISING},
        ]
        from backend.industry_engine.analysis.demand.models import TechnologyIntelligence
        tech_intelligences = [TechnologyIntelligence(**t) for t in technologies]
        
        demand_scores = [
            DemandScore(name="Python", demand_score=95, frequency_score=100, coverage_score=90,
                       category_score=100, role_score=90, rank_score=100),
            DemandScore(name="Redis", demand_score=60, frequency_score=50, coverage_score=60,
                       category_score=85, role_score=70, rank_score=50),
        ]
        trend_metrics = [
            TrendMetrics(name="Python", growth_rate=5.0),
            TrendMetrics(name="Redis", growth_rate=15.0),
        ]
        rankings = technology_ranker.generate_rankings(
            technologies=tech_intelligences,
            demand_scores=demand_scores,
            trend_metrics=trend_metrics,
        )
        assert len(rankings) == 2
        assert rankings[0].overall_rank == 1


# =============================================================================
# Demand Engine Integration Tests
# =============================================================================

class TestDemandEngine:
    """Integration tests for the DemandEngine class."""

    def test_process_basic(self, demand_engine, sample_technologies):
        """Test basic demand engine processing."""
        report = demand_engine.process(
            technologies=sample_technologies,
            total_jobs=1040,
        )
        assert report is not None
        assert len(report.technologies) == len(sample_technologies)
        assert report.summary.get("total_technologies") == len(sample_technologies)

    def test_process_empty_raises(self, demand_engine):
        """Test that empty dataset raises EmptyDatasetError."""
        with pytest.raises(EmptyDatasetError):
            demand_engine.process(technologies={}, total_jobs=100)

    def test_get_top_technologies(self, demand_engine, sample_technologies):
        """Test getting top technologies."""
        demand_engine.process(technologies=sample_technologies, total_jobs=1040)
        top_5 = demand_engine.get_top_technologies(top_n=5)
        assert len(top_5) == 5
        assert top_5[0].industry_score >= top_5[-1].industry_score

    def test_get_core_technologies(self, demand_engine, sample_technologies):
        """Test getting core technologies."""
        demand_engine.process(technologies=sample_technologies, total_jobs=1040)
        core = demand_engine.get_core_technologies()
        assert isinstance(core, list)

    def test_get_tech_intelligence(self, demand_engine, sample_technologies):
        """Test getting specific technology intelligence."""
        demand_engine.process( technologies=sample_technologies, total_jobs=1040)
        python_intel = demand_engine.get_tech_intelligence("Python")
        assert python_intel is not None
        assert python_intel.name == "Python"

    def test_export_report(self, demand_engine, sample_technologies, tmp_path):
        """Test report export."""
        demand_engine.process(technologies=sample_technologies, total_jobs=1040)
        output_file = tmp_path / "test_report.json"
        exported_path = demand_engine.export_report(output_file)
        assert exported_path.exists()
        
        with open(exported_path, "r") as f:
            data = json.load(f)
        assert "technologies" in data

    def test_process_json(self, demand_engine, sample_technologies):
        """Test processing from JSON string."""
        json_str = json.dumps(sample_technologies)
        report = demand_engine.process_json(json_str)
        assert report is not None
        assert len(report.technologies) == len(sample_technologies)


# =============================================================================
# Snapshot Manager Tests
# =============================================================================

class TestSnapshotManager:
    """Tests for the SnapshotManager class."""

    def test_create_snapshot(self):
        """Test snapshot creation."""
        manager = SnapshotManager()
        freq_inputs = {
            "Python": TechnologyFrequencyInput(mentions=842, percentage=81, rank=1),
        }
        snapshot = manager.create_snapshot(technologies=freq_inputs, total_jobs=1040)
        assert snapshot is not None
        assert "Python" in snapshot.technologies

    def test_get_latest_snapshot(self):
        """Test getting latest snapshot."""
        manager = SnapshotManager()
        freq_inputs = {
            "Python": TechnologyFrequencyInput(mentions=842, percentage=81, rank=1),
        }
        manager.create_snapshot(technologies=freq_inputs, total_jobs=1040)
        latest = manager.get_latest_snapshot()
        assert latest is not None

    def test_get_previous_snapshot(self):
        """Test getting previous snapshot."""
        manager = SnapshotManager()
        freq1 = {"Python": TechnologyFrequencyInput(mentions=800, percentage=78, rank=1)}
        freq2 = {"Python": TechnologyFrequencyInput(mentions=842, percentage=81, rank=1)}
        manager.create_snapshot(technologies=freq1, total_jobs=1000)
        manager.create_snapshot(technologies=freq2, total_jobs=1040)
        previous = manager.get_previous_snapshot()
        assert previous is not None
        assert previous.total_jobs == 1000


# =============================================================================
# Configuration Tests
# =============================================================================

class TestConfig:
    """Tests for configuration classes."""

    def test_default_config(self):
        """Test default configuration."""
        config = DemandConfig()
        assert config.demand_weights.frequency == 0.35
        assert config.trend_thresholds.emerging_growth == 100.0

    def test_validate_weights_sum(self):
        """Test weight validation."""
        weights = DemandWeights()
        assert weights.validate_weights_sum()

    def test_invalid_weights_sum(self):
        """Test invalid weight sum detection."""
        weights = DemandWeights(frequency=0.5, coverage=0.5, category_importance=0.5,
                               role_importance=0.5, rank_position=0.5)
        assert not weights.validate_weights_sum()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
