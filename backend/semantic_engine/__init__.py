"""
Semantic Intelligence Engine Package for CurricuAlign AI.

Compares Academic Knowledge Layer against Industry Knowledge Layer to identify Covered, Partial, and Gap skills.
"""

from backend.semantic_engine.service.semantic_service import SemanticService
from backend.semantic_engine.config.config import SemanticEngineConfig

__all__ = ["SemanticService", "SemanticEngineConfig"]
