"""
Unit Tests for Neo4j Knowledge Graph Module.
"""

import unittest
from backend.recommendation_engine.graph.graph_builder import GraphBuilder
from backend.recommendation_engine.graph.graph_models import GraphNode, GraphRelationship, NodeLabel, RelationshipType
from backend.recommendation_engine.graph.graph_repository import GraphRepository
from backend.recommendation_engine.graph.graph_service import GraphService


class TestGraphModule(unittest.TestCase):

    def test_graph_node_and_relationship_creation(self):
        repo = GraphRepository()
        node1 = GraphNode(id="tech_redis", label=NodeLabel.TECHNOLOGY, name="Redis", properties={"demand_score": 90})
        node2 = GraphNode(id="cat_dbs", label=NodeLabel.CATEGORY, name="Databases & Caching")

        repo.create_node(node1)
        repo.create_node(node2)

        rel = GraphRelationship(source_id="tech_redis", target_id="cat_dbs", type=RelationshipType.TECHNOLOGY_BELONGS_TO)
        repo.create_relationship(rel)

        found = repo.find_node_by_id("tech_redis")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Redis")

    def test_graph_service_seed_and_summary(self):
        svc = GraphService()
        summary = svc.get_statistics()
        self.assertGreater(summary.total_nodes, 0)
        self.assertGreater(summary.total_relationships, 0)

    def test_graph_validator(self):
        svc = GraphService()
        validation = svc.validate_graph()
        self.assertTrue(validation.is_valid)
        self.assertGreater(validation.total_nodes_checked, 0)

