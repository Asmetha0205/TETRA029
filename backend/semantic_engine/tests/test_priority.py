"""
Unit tests for Priority Engine.
"""

import unittest
from backend.semantic_engine.models.semantic_models import CoverageClassificationEnum, GapPriorityEnum, SkillMatchResult
from backend.semantic_engine.priority import PriorityCalculator, PriorityEngine


class TestPriorityModule(unittest.TestCase):
    """Test suite for PriorityCalculator and PriorityEngine."""

    def test_critical_priority_calculation(self):
        breakdown = PriorityCalculator.calculate_priority(
            industry_score=95.0,
            demand_score=90.0,
            similarity=0.20,
            trend="Rising",
        )
        self.assertEqual(breakdown.priority, GapPriorityEnum.CRITICAL)

    def test_priority_engine_batch_assignment(self):
        engine = PriorityEngine()
        items = [
            SkillMatchResult(
                academic_skill=None,
                industry_skill="LangGraph",
                similarity=0.20,
                classification=CoverageClassificationEnum.GAP,
                industry_score=94.0,
                demand_score=90.0,
            )
        ]
        assigned = engine.assign_priorities(items)
        self.assertEqual(assigned[0].priority, GapPriorityEnum.CRITICAL)


if __name__ == "__main__":
    unittest.main()
