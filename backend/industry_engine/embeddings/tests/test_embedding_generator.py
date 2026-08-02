"""
Unit tests for EmbeddingGenerator in the Embedding Engine.
"""

import unittest
from backend.industry_engine.knowledge.knowledge_models import TechnologyKnowledgeRecord
from backend.industry_engine.embeddings.embedding_generator import EmbeddingGenerator


class TestEmbeddingGenerator(unittest.TestCase):
    """Test suite for EmbeddingGenerator vector creation and text prompt formatting."""

    def setUp(self):
        self.generator = EmbeddingGenerator(dimension=384, force_fallback=True)

    def test_text_prompt_formatting(self):
        record = TechnologyKnowledgeRecord(
            technology_id="pytorch",
            canonical_name="PyTorch",
            category="AI / ML",
            aliases=["torch", "pytorch-framework"],
            description="Deep learning framework.",
            related_technologies=["python", "tensorflow"],
            demand_score=95.0,  # Should be excluded from text prompt!
        )

        prompt, content_hash = self.generator.format_text_prompt(record)

        self.assertIn("Technology: PyTorch", prompt)
        self.assertIn("Category: AI / ML", prompt)
        self.assertIn("Aliases: pytorch-framework, torch", prompt)
        self.assertNotIn("95.0", prompt)  # Demand score excluded!
        self.assertTrue(len(content_hash) == 64)  # Valid SHA-256 hex string

    def test_generate_single_embedding(self):
        record = TechnologyKnowledgeRecord(
            technology_id="redis",
            canonical_name="Redis",
            category="Database",
            aliases=["redis-db"],
        )

        emb_rec = self.generator.generate(record)

        self.assertEqual(emb_rec.technology_id, "redis")
        self.assertEqual(emb_rec.embedding_id, "emb-redis")
        self.assertEqual(len(emb_rec.embedding_vector), 384)
        self.assertEqual(emb_rec.embedding_dimension, 384)
        self.assertIn("redis", emb_rec.text_content.lower())

    def test_determinism(self):
        record = TechnologyKnowledgeRecord(
            technology_id="docker",
            canonical_name="Docker",
            category="DevOps",
        )

        rec1 = self.generator.generate(record)
        rec2 = self.generator.generate(record)

        self.assertEqual(rec1.embedding_hash, rec2.embedding_hash)
        self.assertEqual(rec1.embedding_vector, rec2.embedding_vector)


if __name__ == "__main__":
    unittest.main()
