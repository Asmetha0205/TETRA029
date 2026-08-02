"""
Unit tests for EmbeddingCache.
"""

import unittest
from backend.industry_engine.embeddings.embedding_cache import EmbeddingCache
from backend.industry_engine.embeddings.embedding_models import EmbeddingRecord, EmbeddingStatus


class TestEmbeddingCache(unittest.TestCase):
    """Test suite for EmbeddingCache lookup, eviction, and statistics."""

    def setUp(self):
        self.cache = EmbeddingCache(max_size=2)
        self.rec1 = EmbeddingRecord(
            embedding_id="emb-python",
            technology_id="python",
            embedding_vector=[0.1] * 384,
            embedding_hash="hash_python",
            status=EmbeddingStatus.ACTIVE,
        )
        self.rec2 = EmbeddingRecord(
            embedding_id="emb-java",
            technology_id="java",
            embedding_vector=[0.2] * 384,
            embedding_hash="hash_java",
            status=EmbeddingStatus.ACTIVE,
        )

    def test_put_and_get(self):
        self.cache.put(self.rec1)
        fetched = self.cache.get("python")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.embedding_id, "emb-python")

        by_hash = self.cache.get_by_hash("hash_python")
        self.assertIsNotNone(by_hash)

        stats = self.cache.get_stats()
        self.assertEqual(stats.hits, 2)
        self.assertEqual(stats.misses, 0)
        self.assertEqual(stats.hit_ratio, 1.0)

    def test_lru_eviction(self):
        rec3 = EmbeddingRecord(
            embedding_id="emb-cpp",
            technology_id="cpp",
            embedding_vector=[0.3] * 384,
            embedding_hash="hash_cpp",
        )

        self.cache.put(self.rec1)
        self.cache.put(self.rec2)
        # Cache is full (max_size=2). Inserting rec3 should evict rec1
        self.cache.put(rec3)

        self.assertIsNone(self.cache.get("python"))  # Evicted
        self.assertIsNotNone(self.cache.get("java"))
        self.assertIsNotNone(self.cache.get("cpp"))


if __name__ == "__main__":
    unittest.main()
