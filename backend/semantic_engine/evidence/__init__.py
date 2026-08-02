"""
Evidence Package for CurricuAlign AI Semantic Engine.
"""

from backend.semantic_engine.evidence.evidence_builder import EvidenceBuilder
from backend.semantic_engine.evidence.evidence_models import DetailedEvidence
from backend.semantic_engine.evidence.exceptions import EvidenceError, ExplanationGenerationError
from backend.semantic_engine.evidence.explanation_generator import ExplanationGenerator

__all__ = [
    "EvidenceBuilder",
    "ExplanationGenerator",
    "DetailedEvidence",
    "EvidenceError",
    "ExplanationGenerationError",
]
