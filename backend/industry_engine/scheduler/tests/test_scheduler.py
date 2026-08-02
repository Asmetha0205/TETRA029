"""
Unit tests for Refresh Pipeline and Scheduler.
"""

import unittest
from backend.industry_engine.knowledge import KnowledgeService
from backend.industry_engine.embeddings import EmbeddingService
from backend.industry_engine.chromadb import ChromaClientWrapper, CollectionManager, ChromaSyncService
from backend.industry_engine.scheduler import RefreshPipeline, RefreshManager, RefreshJobConfig


class TestRefreshScheduler(unittest.TestCase):
    """Test suite for Refresh Pipeline execution and Refresh Manager."""

    def setUp(self):
        self.ks = KnowledgeService()
        self.es = EmbeddingService(knowledge_service=self.ks, force_fallback=True)
        self.client_wrapper = ChromaClientWrapper(force_in_memory=True)
        self.col_manager = CollectionManager(self.client_wrapper)
        self.chroma_sync = ChromaSyncService(self.col_manager)

        self.pipeline = RefreshPipeline(
            knowledge_service=self.ks,
            embedding_service=self.es,
            chroma_sync_service=self.chroma_sync,
        )
        self.manager = RefreshManager(pipeline=self.pipeline)

    def test_pipeline_refresh_run(self):
        report = self.pipeline.run_refresh(source_name="test_run")

        self.assertTrue(report.success)
        self.assertTrue(report.raw_jobs_count > 0)
        self.assertTrue(report.clean_jobs_count > 0)
        self.assertTrue(report.knowledge_created > 0)
        self.assertEqual(self.ks.count(), report.knowledge_created)

    def test_manager_manual_trigger(self):
        report = self.manager.trigger_refresh(config=RefreshJobConfig(source_name="manual_test"))

        self.assertTrue(report.success)
        state = self.manager.get_state()
        self.assertEqual(state.total_runs, 1)
        self.assertEqual(state.failed_runs, 0)


if __name__ == "__main__":
    unittest.main()
