"""
Semantic Matcher for CurricuAlign AI Semantic Intelligence Engine.

Main orchestrator reading Academic Knowledge Layer & Industry Knowledge Layer,
querying ChromaDB, and retrieving top candidates.
"""

import logging
from typing import Dict, List, Optional, Tuple

from backend.industry_engine.service.industry_service import IndustryService
from backend.academic_engine.knowledge.academic_models import AcademicTechnologyRecord
from backend.semantic_engine.config.config import SemanticEngineConfig
from backend.semantic_engine.matching.candidate_selector import CandidateSelector
from backend.semantic_engine.models.semantic_models import CandidateMatch

logger = logging.getLogger("semantic_engine.matching.semantic_matcher")


class SemanticMatcher:
    """
    Main Matcher facade retrieving top candidate technology matches across Knowledge Layers.
    """

    def __init__(
        self,
        industry_service: IndustryService,
        config: Optional[SemanticEngineConfig] = None,
    ) -> None:
        self.industry_service = industry_service
        self.config = config or SemanticEngineConfig()
        self.candidate_selector = CandidateSelector(
            industry_service=self.industry_service,
            top_k=self.config.top_k_candidates,
        )

    def find_best_candidate(self, academic_skill: str) -> Optional[CandidateMatch]:
        """
        Find top matching industry technology candidate for a given academic skill.

        Returns:
            Best CandidateMatch or None if no candidate matches.
        """
        candidates = self.candidate_selector.select_candidates(academic_skill)
        if not candidates:
            return None
        return candidates[0]

    def match_all_academic_skills(
        self, academic_records: List[AcademicTechnologyRecord]
    ) -> Dict[str, Optional[CandidateMatch]]:
        """
        Batch match all academic skills against Industry Knowledge.

        Returns:
            Dict mapping academic technology_id to best CandidateMatch.
        """
        results: Dict[str, Optional[CandidateMatch]] = {}
        for rec in academic_records:
            match = self.find_best_candidate(rec.canonical_name)
            results[rec.technology_id] = match
        logger.info("[Semantic] Matched %d academic skills against Industry Knowledge.", len(results))
        return results
