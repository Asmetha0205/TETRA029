"""
Unit Tests for Grounded Prompt Builder.
"""

import unittest
from backend.recommendation_engine.prompt.prompt_builder import GroundedPromptBuilder
from backend.recommendation_engine.prompt.prompt_validator import PromptValidator


class TestPromptModule(unittest.TestCase):

    def test_grounded_prompt_builder(self):
        builder = GroundedPromptBuilder()
        gap_data = {"gap": ["Redis", "Docker"]}
        evidence_data = [
            {"tech_name": "Redis", "demand_score": 90, "industry_score": 92},
            {"tech_name": "Docker", "demand_score": 88, "industry_score": 90}
        ]

        prompts = builder.build_recommendation_prompt(gap_data, evidence_data)
        self.assertIn("system_prompt", prompts)
        self.assertIn("user_prompt", prompts)
        self.assertIn("Redis", prompts["user_prompt"])
        self.assertIn("Docker", prompts["user_prompt"])

    def test_prompt_validator(self):
        res = PromptValidator.validate_prompt("System prompt test baseline instruction.", "User prompt text with context.")
        self.assertTrue(res.is_valid)

