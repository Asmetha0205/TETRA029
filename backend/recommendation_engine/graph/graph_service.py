"""
Graph Service for Recommendation Intelligence Layer.
High-level service interface for Knowledge Graph operations, querying,
node retrieval, search, and statistics.
"""

from typing import Any, Dict, List, Optional
from backend.recommendation_engine.graph.graph_builder import GraphBuilder
from backend.recommendation_engine.graph.graph_models import GraphNode, KnowledgeGraphSummary
from backend.recommendation_engine.graph.graph_repository import GraphRepository
from backend.recommendation_engine.graph.graph_validator import GraphValidationReport, GraphValidator
from backend.recommendation_engine.utils.logger import graph_logger


class GraphService:
    """
    High-level Graph Service orchestrating graph building, queries,
    node lookup, searching, and schema validation.
    """

    def __init__(self, repository: Optional[GraphRepository] = None):
        self.repo = repository or GraphRepository()
        self.builder = GraphBuilder(self.repo)
        self.validator = GraphValidator(self.repo)
        # Ensure seed graph data is populated
        self.initialize_seed_data()

    def initialize_seed_data(self):
        """Populate initial graph data if graph is currently empty."""
        summary = self.repo.get_summary()
        if summary.total_nodes == 0:
            graph_logger.info("Empty graph detected. Populating seed dataset...")
            self.builder.build_seed_graph()

    def get_statistics(self) -> KnowledgeGraphSummary:
        """Get graph statistics and metrics summary."""
        stats = self.repo.get_summary()
        graph_logger.info(f"Retrieved Graph Statistics: {stats.total_nodes} nodes, {stats.total_relationships} relationships")
        return stats

    def get_node_by_id(self, node_id: str) -> Optional[GraphNode]:
        """Fetch a specific node by ID."""
        node = self.repo.find_node_by_id(node_id)
        if node:
            graph_logger.info(f"Node Found id={node_id} label={node.label}")
        else:
            graph_logger.warning(f"Node Not Found id={node_id}")
        return node

    def search_nodes(self, query: str, limit: int = 20) -> List[GraphNode]:
        """Search nodes matching keyword."""
        results = self.repo.search_nodes(query, limit=limit)
        graph_logger.info(f"Node Search query='{query}' returned {len(results)} matches")
        return results

    def validate_graph(self) -> GraphValidationReport:
        """Run validation audit on graph."""
        return self.validator.validate()
