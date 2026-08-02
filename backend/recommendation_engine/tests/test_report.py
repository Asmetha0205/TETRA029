"""
Unit Tests for Recommendation Report Module.
"""

import unittest
from backend.recommendation_engine.learning_path.learning_path_builder import LearningPathBuilder
from backend.recommendation_engine.recommendation.recommendation_builder import RecommendationBuilder
from backend.recommendation_engine.report.json_export import JSONReportExporter
from backend.recommendation_engine.report.markdown_export import MarkdownReportExporter
from backend.recommendation_engine.report.pdf_export import PDFReportExporter
from backend.recommendation_engine.report.report_builder import ReportBuilder


class TestReportModule(unittest.TestCase):

    def test_report_builder_and_exporters(self):
        rec_builder = RecommendationBuilder()
        path_builder = LearningPathBuilder()
        report_builder = ReportBuilder()

        llm_payload = {
            "recommendations": [
                {
                    "technology": "Redis",
                    "priority": "High",
                    "industry_score": 91,
                    "trend": "Rising",
                    "reason": "Redis is used for caching.",
                    "recommended_course": "Advanced Backend Systems",
                    "recommended_module": "Caching & Distributed Systems",
                    "learning_outcomes": ["Implement Redis cache"],
                    "lab": "Implement Redis cache in FastAPI.",
                    "mini_project": "Distributed API Cache",
                    "learning_path": ["Docker", "Redis", "FastAPI"],
                    "references": ["Graph Evidence"],
                    "confidence": 0.94
                }
            ]
        }
        recs = rec_builder.build_recommendations(llm_payload, [{"tech_name": "Redis"}])
        path_plan = path_builder.build_learning_path(["Docker", "Redis", "FastAPI"])

        exec_report = report_builder.build_report(recs, path_plan, [])

        # Test Exporters
        report_dict = exec_report.model_dump()
        json_out = JSONReportExporter.export(report_dict)
        self.assertIn('"alignment_score"', json_out)

        md_out = MarkdownReportExporter.export(report_dict)
        self.assertIn("# CurricuAlign AI", md_out)
        self.assertIn("Redis", md_out)

        pdf_out = PDFReportExporter.export(report_dict)
        self.assertIn("<html>", pdf_out)

