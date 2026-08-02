"""
Unit and Integration Tests for Recommendation Intelligence Layer (Phase 6).
Tests Gemini LLM prompt orchestration, RAG retriever, and learning path generator.
"""

import pytest
from backend.recommendation_engine.service.recommendation_service import RecommendationService
from backend.recommendation_engine.service.service_models import GenerateRecommendationsRequest


def test_recommendation_service():
    service = RecommendationService()
    req = GenerateRecommendationsRequest(
        gap_analysis_data={
            "gap": [
                {
                    "industry_skill": "Docker",
                    "priority": "CRITICAL",
                    "category": "DevOps",
                    "similarity": 12.0,
                }
            ]
        },
        target_gaps=["Docker", "Kubernetes"],
    )

    response = service.generate_recommendations(req)
    assert response is not None
    assert response.success is True
    assert response.recommendations is not None
    assert len(response.recommendations.recommendations) > 0


def test_learning_path_generator():
    service = RecommendationService()
    learning_path = service.get_learning_path(["Docker", "Kubernetes", "Redis"])
    assert learning_path is not None
    assert learning_path.total_steps > 0
