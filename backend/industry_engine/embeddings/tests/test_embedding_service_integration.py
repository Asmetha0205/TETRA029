"""
Integration tests for the Embedding Engine package.

Verifies end-to-end integration:
KnowledgeService -> EmbeddingService -> EmbeddingManager -> EmbeddingGenerator -> EmbeddingCache -> EmbeddingRepository -> Similarity Search.
"""

import tempfile
import unittest
from pathlib import Path

from backend.industry_engine.knowledge.knowledge_service import KnowledgeService
from backend.industry_engine.embeddings.embedding_service import EmbeddingService


class TestEmbeddingServiceIntegration(unittest.TestCase):
    """End-to-end integration test suite for the Embedding Engine."""

    def test_full_embedding_workflow(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            emb_file = str(Path(tmp_dir) / "embeddings.json")

            # 1. Setup Knowledge Service & Embedding Service
            knowledge_service = KnowledgeService()
            embedding_service = EmbeddingService(
                knowledge_service=knowledge_service,
                repository_path=emb_file,
                force_fallback=True,
            )

            # 2. Ingest Technologies into Knowledge Layer
            knowledge_service.create_technology(
                canonical_name="PyTorch",
                category="AI / ML",
                aliases=["torch"],
                description="Deep learning framework.",
            )
            knowledge_service.create_technology(
                canonical_name="React",
                category="Web",
                aliases=["reactjs"],
                description="Frontend UI library.",
            )
            self.assertEqual(knowledge_service.count(), 2)

            # 3. Generate Embeddings from Knowledge Layer
            batch_res = embedding_service.generate_all_from_knowledge()
            self.assertEqual(batch_res.total_processed, 2)
            self.assertEqual(batch_res.generated_count, 2)
            self.assertEqual(len(embedding_service.get_all_embeddings()), 2)

            # 4. Incremental Regeneration (No changes -> Skip/Cache all)
            re_gen_res = embedding_service.regenerate_changed()
            self.assertEqual(re_gen_res.generated_count, 0)
            self.assertEqual(re_gen_res.cached_count + re_gen_res.skipped_count, 2)

            # 5. Modify a Technology in Knowledge Layer & Regenerate
            knowledge_service.update_technology("pytorch", description="Updated deep learning framework with CUDA support.")
            re_gen_res_2 = embedding_service.regenerate_changed()
            self.assertEqual(re_gen_res_2.generated_count, 1)  # Only PyTorch regenerated!
            self.assertEqual(re_gen_res_2.cached_count + re_gen_res_2.skipped_count, 1)  # React bypassed!

            # 6. Similarity Search
            results = embedding_service.search_similar(query="deep learning framework", limit=2)
            self.assertTrue(len(results) > 0)
            top_record, top_score = results[0]
            self.assertEqual(top_record.technology_id, "pytorch")

            # 7. Persistence (Save & Load)
            embedding_service.save()
            self.assertTrue(Path(emb_file).exists())

            fresh_emb_service = EmbeddingService(
                repository_path=emb_file,
                force_fallback=True,
            )
            fresh_emb_service.load()
            self.assertEqual(len(fresh_emb_service.get_all_embeddings()), 2)

            # 8. Validation
            is_valid, errors = fresh_emb_service.validate_engine()
            self.assertTrue(is_valid)
            self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
