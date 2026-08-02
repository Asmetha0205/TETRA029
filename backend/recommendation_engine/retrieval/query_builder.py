"""
Retrieval Query Builder for Evidence Engine.
Builds strict target Cypher queries to extract evidence ONLY for specified gap technologies.
"""

from typing import Any, Dict, List, Optional
from backend.recommendation_engine.graph.graph_queries import CypherQueries


class EvidenceQueryBuilder:
    """
    Constructs graph queries to retrieve targeted evidence for curriculum gaps.
    Guarantees no unrelated nodes are returned.
    """

    @staticmethod
    def build_evidence_query(tech_name: str, tech_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Build parameter payload for evidence query for a single gap technology.
        """
        return {
            "query": CypherQueries.GET_GAP_EVIDENCE,
            "params": {
                "tech_name": tech_name,
                "tech_id": tech_id or f"tech_{tech_name.lower().replace(' ', '_')}"
            }
        }

    @staticmethod
    def build_dependency_query(tech_name: str, tech_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Build parameter payload for dependency tree query.
        """
        return {
            "query": CypherQueries.GET_DEPENDENCY_CHAIN,
            "params": {
                "tech_name": tech_name,
                "tech_id": tech_id or f"tech_{tech_name.lower().replace(' ', '_')}"
            }
        }
