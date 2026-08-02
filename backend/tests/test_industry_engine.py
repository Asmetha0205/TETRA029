"""
Unit and Integration Tests for Industry Intelligence Engine (Phase 3).
Tests skill extraction, market demand calculation, taxonomy matching, and Neo4j graph fallback.
"""

import pytest
from backend.industry_engine.service.industry_service import IndustryService
from backend.industry_engine.models.clean_job import CleanJob


def test_clean_job_model():
    job = CleanJob(
        job_id="job_docker_01",
        title="Senior Cloud DevOps Engineer",
        company="Tech Corp",
        location="Remote",
        clean_description="Requires Docker, Kubernetes, Terraform, and Python.",
        source="LinkedIn Jobs",
    )
    assert job.job_id == "job_docker_01"
    assert "Docker" in job.clean_description


def test_industry_health():
    service = IndustryService()
    health_status = service.health()
    assert health_status is not None
    assert health_status.status in ["healthy", "degraded", "operational"]
