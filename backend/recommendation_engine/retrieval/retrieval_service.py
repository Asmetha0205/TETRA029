"""
Retrieval Service for Recommendation Intelligence Layer.
Orchestrates batch evidence retrieval, caching, and parallel execution.
"""

from typing import Any, Dict, List, Optional
from backend.recommendation_engine.graph.graph_repository import GraphRepository
from backend.recommendation_engine.retrieval.evidence_retriever import EvidenceRetriever
from backend.recommendation_engine.retrieval.ranking import RankedEvidence
from backend.recommendation_engine.utils.logger import retriever_logger


class RetrievalService:
    """
    Service wrapper around Evidence Retriever providing caching and execution.
    """

    def __init__(self, repository: Optional[GraphRepository] = None):
        self.retriever = EvidenceRetriever(repository)
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get_evidence_for_gaps(self, gap_technologies: List[str]) -> List[RankedEvidence]:
        """
        Retrieve evidence for gap technologies with caching.
        """
        retriever_logger.info(f"Retrieving evidence for gap technologies: {gap_technologies}")
        return self.retriever.retrieve_batch_evidence(gap_technologies)

    def get_single_evidence(self, tech_name: str) -> Dict[str, Any]:
        """
        Retrieve evidence for a single gap technology with cache lookup.
        """
        cache_key = tech_name.lower().strip()
        if cache_key in self._cache:
            retriever_logger.info(f"Retrieved evidence for '{tech_name}' from cache")
            return self._cache[cache_key]

        evidence = self.retriever.retrieve_evidence_for_gap(tech_name)
        self._cache[cache_key] = evidence
        return evidence
