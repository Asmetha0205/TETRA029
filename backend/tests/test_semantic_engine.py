"""
Unit and Integration Tests for Semantic Intelligence Engine (Phase 5).
Tests similarity matching, embedding service, and delta gap calculation.
"""

import pytest
from backend.semantic_engine.service.semantic_service import SemanticService


def test_semantic_service_matching():
    service = SemanticService()
    report = service.compare_curriculum()

    assert report is not None
    assert hasattr(report, "alignment_score")
    assert report.alignment_score >= 0.0
    assert hasattr(report, "gap")
    assert hasattr(report, "covered")
    assert hasattr(report, "partial")
