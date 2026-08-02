"""
Candidate Selector for Semantic Matching Engine.

Queries ChromaDB vector database (or Industry Engine facade) to retrieve Top-K candidate matches.
"""

import logging
from typing import List, Optional

from backend.industry_engine.service.industry_service import IndustryService
from backend.semantic_engine.models.semantic_models import CandidateMatch

logger = logging.getLogger("semantic_engine.matching.candidate_selector")


class CandidateSelector:
    """Retrieves Top-K industry candidate technologies for an academic skill."""

    def __init__(self, industry_service: IndustryService, top_k: int = 10) -> None:
        self.industry_service = industry_service
        self.top_k = top_k

    def select_candidates(self, academic_skill: str) -> List[CandidateMatch]:
        """
        Query ChromaDB / Industry Engine to retrieve top candidate matches for academic_skill.

        Returns:
            List of CandidateMatch objects sorted by similarity score descending.
        """
        candidates: List[CandidateMatch] = []
        try:
            results = self.industry_service.search_similar(query=academic_skill, limit=self.top_k)
            for res in results:
                candidates.append(
                    CandidateMatch(
                        academic_skill=academic_skill,
                        industry_skill=res.canonical_name,
                        industry_technology_id=res.technology_id,
                        similarity_score=res.similarity_score,
                        category=res.category,
                        metadata=res.metadata,
                    )
                )
        except Exception as exc:
            logger.warning("[Semantic] Candidate selection error for '%s': %s", academic_skill, exc)

        logger.info("[Semantic] Retrieved %d candidates for '%s'.", len(candidates), academic_skill)
        return candidates
