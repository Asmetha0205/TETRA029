"""
Integration tests for the Industry Knowledge Layer.

Programmatically verifies:
Knowledge Builder -> Repository -> Snapshot -> Save -> Load -> Statistics -> Search -> Rollback.
"""

import tempfile
import unittest
from pathlib import Path

from backend.industry_engine.knowledge import (
    KnowledgeBuilder,
    KnowledgeRepository,
    KnowledgeService,
    SnapshotManager,
)


class TestKnowledgeLayerIntegration(unittest.TestCase):
    """Full integration verification suite for the Industry Knowledge Layer."""

    def test_full_knowledge_layer_workflow(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_file = str(Path(tmp_dir) / "knowledge_repo.json")
            snap_file = str(Path(tmp_dir) / "knowledge_snapshots.json")

            # 1. Initialize Service Facade
            service = KnowledgeService(
                repository_path=repo_file,
                snapshot_path=snap_file,
            )
            self.assertEqual(service.count(), 0)

            # 2. Knowledge Builder Ingestion
            norm_input = [
                {"canonical_name": "Python", "category": "Programming Language", "aliases": ["python3"]},
                {"canonical_name": "FastAPI", "category": "Framework", "aliases": ["fastapi"]},
            ]
            freq_input = {
                "technologies": [
                    {"name": "Python", "mentions": 150, "percentage": 75.0, "rank": 1},
                    {"name": "FastAPI", "mentions": 60, "percentage": 30.0, "rank": 5},
                ]
            }
            demand_input = {
                "technologies": [
                    {"name": "Python", "demand_score": 90.0, "industry_score": 88.0, "trend": "Rising", "classification": "Core Technology"},
                    {"name": "FastAPI", "demand_score": 80.0, "industry_score": 82.0, "trend": "Rapidly Rising", "classification": "Emerging Technology"},
                ]
            }

            created, updated, snap1 = service.ingest_pipeline_outputs(
                normalized_techs=norm_input,
                frequency_data=freq_input,
                demand_data=demand_input,
                source="integration_test",
                auto_snapshot=True,
            )
            self.assertEqual(created, 2)
            self.assertEqual(updated, 0)
            self.assertIsNotNone(snap1)
            self.assertEqual(service.count(), 2)

            # 3. Search & Statistics Verification
            results = service.search("fast")
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].canonical_name, "FastAPI")

            stats = service.get_statistics()
            self.assertEqual(stats.total_technologies, 2)
            self.assertEqual(stats.snapshot_count, 1)

            # 4. State Mutation & Snapshot 2
            service.update_technology("python", demand_score=95.0)
            snap2 = service.create_snapshot(description="After Python score bump")

            diff = service.compare_snapshots(snap1.metadata.snapshot_id, snap2.metadata.snapshot_id)
            self.assertEqual(len(diff.changed), 1)
            self.assertEqual(diff.changed[0]["technology_id"], "python")

            # 5. Persistence (Save & Load Verification)
            save_paths = service.save_all()
            self.assertTrue(Path(save_paths["repository"]).exists())
            self.assertTrue(Path(save_paths["snapshots"]).exists())

            # Load into fresh service instance
            fresh_service = KnowledgeService(
                repository_path=repo_file,
                snapshot_path=snap_file,
            )
            fresh_service.load_all()
            self.assertEqual(fresh_service.count(), 2)

            # 6. Rollback Verification
            loaded_count, pre_snap = fresh_service.rollback_snapshot(snap1.metadata.snapshot_id)
            self.assertEqual(loaded_count, 2)
            # Verify python demand_score rolled back to 90.0
            rolled_back_python = fresh_service.get_technology("python")
            self.assertEqual(rolled_back_python.demand_score, 90.0)


if __name__ == "__main__":
    unittest.main()
