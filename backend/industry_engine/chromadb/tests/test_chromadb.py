"""
Unit tests for ChromaDB Synchronization Layer.
"""

import unittest
from backend.industry_engine.chromadb import (
    ChromaClientWrapper,
    CollectionManager,
    ChromaMetadataManager,
    ChromaSyncService,
    ChromaQueryService,
)
from backend.industry_engine.knowledge.knowledge_models import TechnologyKnowledgeRecord
from backend.industry_engine.embeddings.embedding_models import EmbeddingRecord


class TestChromaDBLayer(unittest.TestCase):
    """Test suite for ChromaDB Client, CollectionManager, Sync, and Query Services."""

    def setUp(self):
        self.client_wrapper = ChromaClientWrapper(force_in_memory=True)
        self.collection_manager = CollectionManager(self.client_wrapper)
        self.sync_service = ChromaSyncService(self.collection_manager)
        self.query_service = ChromaQueryService(self.collection_manager)

        self.tech_rec = TechnologyKnowledgeRecord(
            technology_id="pytorch",
            canonical_name="PyTorch",
            category="AI / ML",
            aliases=["torch"],
            demand_score=95.0,
            industry_score=92.0,
        )
        self.emb_rec = EmbeddingRecord(
            embedding_id="emb-pytorch",
            technology_id="pytorch",
            embedding_vector=[0.1] * 384,
            embedding_hash="hash_pytorch",
        )

    def test_sync_single_and_query(self):
        self.sync_service.sync_single(self.tech_rec, self.emb_rec)
        self.assertEqual(self.collection_manager.count(), 1)

        result = self.query_service.get_by_technology_id("pytorch")
        self.assertIsNotNone(result)
        self.assertEqual(result["metadata"]["canonical_name"], "PyTorch")

    def test_vector_search(self):
        self.sync_service.sync_single(self.tech_rec, self.emb_rec)
        query_vec = [0.1] * 384
        results = self.query_service.search_by_vector(query_vec, limit=5)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["technology_id"], "pytorch")
        self.assertTrue(results[0]["similarity_score"] > 0.9)


if __name__ == "__main__":
    unittest.main()
