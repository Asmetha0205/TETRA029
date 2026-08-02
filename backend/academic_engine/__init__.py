"""
Academic Intelligence Engine Package for CurricuAlign AI.

Converts university curriculum PDFs into a structured, normalized Academic Knowledge Layer.
"""

from backend.academic_engine.service.academic_service import AcademicService
from backend.academic_engine.config.config import AcademicEngineConfig

__all__ = ["AcademicService", "AcademicEngineConfig"]
