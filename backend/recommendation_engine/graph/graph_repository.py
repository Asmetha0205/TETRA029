"""
Neo4j Graph Repository for Recommendation Intelligence Layer.
Provides database execution layer for Cypher queries with graceful
in-memory graph fallback when Neo4j is offline or disabled.
"""

from typing import Any, Dict, List, Optional
from backend.recommendation_engine.config.config import Neo4jConfig, config as default_config
from backend.recommendation_engine.graph.graph_models import GraphNode, GraphRelationship, KnowledgeGraphSummary, NodeLabel, RelationshipType
from backend.recommendation_engine.graph.graph_queries import CypherQueries
from backend.recommendation_engine.utils.logger import graph_logger

try:
    from neo4j import GraphDatabase, Driver
    HAS_NEO4J_DRIVER = True
except ImportError:
    HAS_NEO4J_DRIVER = False


class InMemoryGraphStore:
    """In-memory fallback graph store used when Neo4j database is unreachable."""

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.relationships: List[GraphRelationship] = []

    def clear(self):
        self.nodes.clear()
        self.relationships.clear()

    def add_node(self, node: GraphNode):
        self.nodes[node.id] = node

    def add_relationship(self, rel: GraphRelationship):
        self.relationships.append(rel)

    def get_summary(self) -> KnowledgeGraphSummary:
        label_counts: Dict[str, int] = {}
        for node in self.nodes.values():
            lbl = node.label.value if hasattr(node.label, "value") else str(node.label)
            label_counts[lbl] = label_counts.get(lbl, 0) + 1

        rel_counts: Dict[str, int] = {}
        for rel in self.relationships:
            rtype = rel.type.value if hasattr(rel.type, "value") else str(rel.type)
            rel_counts[rtype] = rel_counts.get(rtype, 0) + 1

        return KnowledgeGraphSummary(
            total_nodes=len(self.nodes),
            total_relationships=len(self.relationships),
            node_counts_by_label=label_counts,
            relationship_counts_by_type=rel_counts,
            status="Connected (InMemory Fallback)"
        )


class GraphRepository:
    """
    Neo4j Graph Repository handling connection pooling, Cypher queries,
    and fallback store when Neo4j DB is disabled or unreachable.
    """

    def __init__(self, cfg: Optional[Neo4jConfig] = None):
        self._cfg = cfg or default_config.neo4j
        self._driver: Optional[Any] = None
        self._memory_store = InMemoryGraphStore()
        self._using_memory_fallback = False
        self._initialize_driver()

    def _initialize_driver(self):
        if not self._cfg.enabled:
            graph_logger.info("Neo4j explicitly disabled in configuration. Using In-Memory Graph Store.")
            self._using_memory_fallback = True
            return

        if not HAS_NEO4J_DRIVER:
            graph_logger.warning("neo4j Python package not installed. Using In-Memory Graph Store.")
            self._using_memory_fallback = True
            return

        try:
            self._driver = GraphDatabase.driver(
                self._cfg.uri,
                auth=(self._cfg.user, self._cfg.password),
                max_connection_lifetime=self._cfg.max_connection_lifetime,
                max_connection_pool_size=self._cfg.max_connection_pool_size,
            )
            # Verify connectivity
            self._driver.verify_connectivity()
            graph_logger.info(f"Neo4j Connected successfully to {self._cfg.uri}")
        except Exception as e:
            graph_logger.warning(f"Neo4j Connection Failed ({e}). Falling back to In-Memory Graph Store.")
            self._using_memory_fallback = True
            self._driver = None

    def close(self):
        if self._driver:
            self._driver.close()
            graph_logger.info("Neo4j driver closed.")

    def is_using_memory_fallback(self) -> bool:
        return self._using_memory_fallback

    def create_node(self, node: GraphNode) -> GraphNode:
        """Upsert a node in graph."""
        if self._using_memory_fallback:
            self._memory_store.add_node(node)
            graph_logger.info(f"Node Created [InMemory] label={node.label} id={node.id}")
            return node

        query = CypherQueries.MERGE_NODE.format(label=node.label.value)
        params = {
            "id": node.id,
            "name": node.name,
            "properties": node.properties,
        }

        with self._driver.session(database=self._cfg.database) as session:
            session.run(query, params)
            graph_logger.info(f"Node Created label={node.label} id={node.id}")
        return node

    def create_relationship(self, rel: GraphRelationship) -> GraphRelationship:
        """Upsert a relationship in graph."""
        if self._using_memory_fallback:
            self._memory_store.add_relationship(rel)
            graph_logger.info(f"Relationship Created [InMemory] type={rel.type} {rel.source_id}->{rel.target_id}")
            return rel

        query = CypherQueries.MERGE_RELATIONSHIP.format(rel_type=rel.type.value)
        params = {
            "source_id": rel.source_id,
            "target_id": rel.target_id,
            "properties": rel.properties,
        }

        with self._driver.session(database=self._cfg.database) as session:
            session.run(query, params)
            graph_logger.info(f"Relationship Created type={rel.type} {rel.source_id}->{rel.target_id}")
        return rel

    def get_summary(self) -> KnowledgeGraphSummary:
        """Fetch node & relationship statistics."""
        if self._using_memory_fallback:
            return self._memory_store.get_summary()

        try:
            with self._driver.session(database=self._cfg.database) as session:
                res_totals = session.run(CypherQueries.GET_GRAPH_STATS).single()
                total_nodes = res_totals["total_nodes"] if res_totals else 0
                total_rels = res_totals["total_relationships"] if res_totals else 0

                res_labels = session.run(CypherQueries.GET_NODE_COUNTS_BY_LABEL)
                node_counts = {rec["label"]: rec["count"] for rec in res_labels if rec["label"]}

                res_rels = session.run(CypherQueries.GET_RELATIONSHIP_COUNTS_BY_TYPE)
                rel_counts = {rec["rel_type"]: rec["count"] for rec in res_rels if rec["rel_type"]}

            return KnowledgeGraphSummary(
                total_nodes=total_nodes,
                total_relationships=total_rels,
                node_counts_by_label=node_counts,
                relationship_counts_by_type=rel_counts,
                status="Connected (Neo4j)",
            )
        except Exception as e:
            graph_logger.error(f"Error fetching summary from Neo4j: {e}")
            return self._memory_store.get_summary()

    def find_node_by_id(self, node_id: str) -> Optional[GraphNode]:
        """Find node by ID."""
        if self._using_memory_fallback:
            return self._memory_store.nodes.get(node_id)

        query = "MATCH (n {id: $id}) RETURN n.id AS id, labels(n)[0] AS label, n.name AS name, properties(n) AS props"
        with self._driver.session(database=self._cfg.database) as session:
            result = session.run(query, {"id": node_id}).single()
            if not result:
                return None
            return GraphNode(
                id=result["id"],
                label=NodeLabel(result["label"]),
                name=result["name"] or result["id"],
                properties=result["props"] or {}
            )

    def search_nodes(self, query_str: str, limit: int = 20) -> List[GraphNode]:
        """Search nodes by keyword matching."""
        if self._using_memory_fallback:
            matches = []
            q = query_str.lower()
            for n in self._memory_store.nodes.values():
                if q in n.name.lower() or q in n.id.lower():
                    matches.append(n)
                if len(matches) >= limit:
                    break
            return matches

        with self._driver.session(database=self._cfg.database) as session:
            records = session.run(CypherQueries.SEARCH_NODES, {"query": query_str, "limit": limit})
            nodes = []
            for rec in records:
                nodes.append(
                    GraphNode(
                        id=rec["id"],
                        label=NodeLabel(rec["label"]),
                        name=rec["name"] or rec["id"],
                        properties=rec["properties"] or {}
                    )
                )
            return nodes
