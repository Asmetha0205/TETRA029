"""
Unit tests for EmbeddingRepository.
"""

import tempfile
import unittest
from pathlib import Path

from backend.industry_engine.embeddings.exceptions import EmbeddingRepositoryError, EmbeddingValidationError
from backend.industry_engine.embeddings.embedding_models import EmbeddingRecord
from backend.industry_engine.embeddings.embedding_repository import EmbeddingRepository


class TestEmbeddingRepository(unittest.TestCase):
    """Test suite for EmbeddingRepository CRUD and persistence operations."""

    def setUp(self):
        self.repo = EmbeddingRepository()
        self.rec1 = EmbeddingRecord(
            embedding_id="emb-tensorflow",
            technology_id="tensorflow",
            embedding_vector=[0.1] * 384,
            embedding_hash="hash_tf",
        )

    def test_add_and_get(self):
        self.repo.add(self.rec1)
        self.assertTrue(self.repo.exists("tensorflow"))
        fetched = self.repo.get("tensorflow")
        self.assertEqual(fetched.embedding_id, "emb-tensorflow")

    def test_duplicate_add_raises_error(self):
        self.repo.add(self.rec1)
        with self.assertRaises(EmbeddingRepositoryError):
            self.repo.add(self.rec1)

    def test_invalid_vector_raises_validation_error(self):
        invalid_rec = EmbeddingRecord(
            embedding_id="emb-bad",
            technology_id="bad",
            embedding_vector=[float("nan")] * 384,  # NaN vector
            embedding_hash="hash_bad",
        )
        with self.assertRaises(EmbeddingValidationError):
            self.repo.add(invalid_rec)

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = str(Path(tmp_dir) / "repo.json")
            repo = EmbeddingRepository(storage_path=file_path)
            repo.add(self.rec1)
            repo.save()

            fresh_repo = EmbeddingRepository(storage_path=file_path)
            self.assertEqual(fresh_repo.count(), 1)
            self.assertTrue(fresh_repo.exists("tensorflow"))


if __name__ == "__main__":
    unittest.main()
