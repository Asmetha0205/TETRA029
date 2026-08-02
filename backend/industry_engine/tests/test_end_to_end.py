"""
End-to-End Integration Verification Suite for Industry Intelligence Engine (Phase 3 Finalization).

Verifies that:
Knowledge Layer -> Embedding Engine -> ChromaDB -> Refresh Pipeline -> Industry Service -> REST API -> Health Checks
all work together seamlessly.
"""

import tempfile
import unittest
from pathlib import Path

from backend.industry_engine.service import IndustryService, RefreshRequestOptions
from backend.industry_engine.api import IndustryController, RefreshRequestPayload, RollbackRequestPayload


class TestIndustryEngineEndToEnd(unittest.TestCase):
    """End-to-End verification test suite for the Industry Intelligence Engine."""

    def test_full_engine_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_file = str(Path(tmp_dir) / "knowledge_repo.json")
            snap_file = str(Path(tmp_dir) / "knowledge_snapshots.json")
            emb_file = str(Path(tmp_dir) / "embedding_repo.json")

            # 1. Initialize Principal Service Facade
            service = IndustryService(
                repository_path=repo_file,
                snapshot_path=snap_file,
                embedding_path=emb_file,
                force_fallback_embeddings=True,
            )

            # 2. Health Check (Initial State)
            health = service.health()
            self.assertEqual(health.status, "healthy")
            self.assertIn("knowledge_layer", health.components)
            self.assertIn("embedding_engine", health.components)
            self.assertIn("chromadb", health.components)

            # 3. Refresh Pipeline Run (Fetch -> Clean -> Extract -> Normalize -> Freq -> Demand -> Knowledge -> Embeddings -> ChromaDB -> Snapshot)
            report = service.refresh_industry(
                options=RefreshRequestOptions(source_name="e2e_test", dry_run=False)
            )
            self.assertTrue(report.success)
            self.assertTrue(report.knowledge_created > 0)
            self.assertTrue(report.embeddings_generated > 0)
            self.assertIsNotNone(report.snapshot_id)

            initial_snapshot_id = report.snapshot_id

            # 4. Discovery API via Service Facade
            techs = service.get_all_technologies()
            self.assertEqual(len(techs), report.knowledge_created)

            # 5. Vector Similarity Search
            similar_items = service.search_similar(query="machine learning framework", limit=5)
            self.assertTrue(len(similar_items) > 0)

            # 6. REST API Controller Verification
            controller = IndustryController(service)

            # GET /industry/technologies
            tech_list_res = controller.list_technologies()
            self.assertEqual(tech_list_res.total, len(techs))

            # GET /industry/statistics
            stats_res = controller.get_statistics()
            self.assertEqual(stats_res["total_technologies"], len(techs))

            # GET /industry/health
            health_res = controller.get_health()
            self.assertEqual(health_res["status"], "healthy")

            # 7. Modify State & Rollback Verification
            first_tech_id = techs[0].technology_id
            service.knowledge_service.update_technology(first_tech_id, demand_score=99.9)
            updated_tech = service.get_technology(first_tech_id)
            self.assertEqual(updated_tech.demand_score, 99.9)

            # POST /industry/rollback
            rollback_res = controller.rollback_snapshot(RollbackRequestPayload(snapshot_id=initial_snapshot_id))
            self.assertTrue(rollback_res.success)
            self.assertEqual(rollback_res.snapshot_id, initial_snapshot_id)

            rolled_back_tech = service.get_technology(first_tech_id)
            self.assertNotEqual(rolled_back_tech.demand_score, 99.9)  # Successfully restored!

            # 8. Post-Rollback Vector Similarity Search
            post_rollback_similar = service.search_similar(query="framework", limit=3)
            self.assertTrue(len(post_rollback_similar) > 0)


if __name__ == "__main__":
    unittest.main()
