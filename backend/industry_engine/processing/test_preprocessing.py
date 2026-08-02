"""
Unit Test Suite for Job Cleaning & Preprocessing Subsystem.
Tests Cleaner, Normalizer, Duplicate Detector, Language Detector, Validator, and Pipeline.
"""

import unittest
from backend.industry_engine.models.job import Job
from backend.industry_engine.processing.job_cleaner import JobCleaner
from backend.industry_engine.processing.text_normalizer import TextNormalizer
from backend.industry_engine.processing.duplicate_detector import DuplicateDetector
from backend.industry_engine.processing.language_detector import LanguageDetector
from backend.industry_engine.processing.validators import PreprocessingValidator
from backend.industry_engine.processing.pipeline import JobPreprocessingPipeline


class TestPreprocessingSubsystem(unittest.TestCase):

    def setUp(self):
        self.cleaner = JobCleaner()
        self.normalizer = TextNormalizer()
        self.duplicate_detector = DuplicateDetector()
        self.language_detector = LanguageDetector()
        self.validator = PreprocessingValidator(min_description_length=50)
        self.pipeline = JobPreprocessingPipeline(min_description_length=50)

    def test_job_cleaner_html_and_boilerplate_stripping(self):
        raw_html = """
        <html>
            <body>
                <h2>Senior Backend Engineer</h2>
                <p>We are hiring a Python &amp; FastAPI engineer 😀!</p>
                <p>Requirements include Docker, Kubernetes, and C++.</p>
                <p>We are an Equal Opportunity Employer M/F/D/V. Apply Now!</p>
            </body>
        </html>
        """
        cleaned = self.cleaner.clean_text(raw_html)
        self.assertNotIn("<html>", cleaned)
        self.assertNotIn("&amp;", cleaned)
        self.assertIn("Python & FastAPI", cleaned)
        self.assertIn("Docker, Kubernetes, and C++", cleaned)
        self.assertNotIn("Equal Opportunity Employer", cleaned)
        self.assertNotIn("Apply Now", cleaned)

    def test_text_normalizer_quotes_and_bullets(self):
        raw_text = "• Required: “Python”, ‘FastAPI’, and “vLLM”.\r\n➢ Preferred: C# and .NET."
        normalized = self.normalizer.normalize(raw_text)
        self.assertIn('- Required: "Python", \'FastAPI\', and "vLLM".', normalized)
        self.assertIn('- Preferred: C# and .NET.', normalized)
        self.assertNotIn("\r\n", normalized)

    def test_language_detector(self):
        english_text = "We are seeking a Software Engineer proficient in Python, SQL, and Docker to join our engineering team."
        german_text = "Wir suchen einen erfahrenen Software-Entwickler mit Kenntnissen in Python und SQL für unser Team in Berlin."

        is_en_1, lang_1, _ = self.language_detector.is_english(english_text)
        is_en_2, lang_2, _ = self.language_detector.is_english(german_text)

        self.assertTrue(is_en_1)
        self.assertEqual(lang_1, "en")
        self.assertFalse(is_en_2)

    def test_duplicate_detector(self):
        job1 = Job(job_id="job_001", title="AI Engineer", company="TechCorp", description="Python and PyTorch developer for LLM pipelines.", source="test")
        job2 = Job(job_id="job_001", title="AI Engineer", company="TechCorp", description="Different text but duplicate ID.", source="test")
        job3 = Job(job_id="job_002", title="AI Engineer", company="TechCorp", description="Python and PyTorch developer for LLM pipelines.", source="test")

        is_dup1, _ = self.duplicate_detector.is_duplicate(job1, job1.description)
        is_dup2, reason2 = self.duplicate_detector.is_duplicate(job2, job2.description)
        is_dup3, reason3 = self.duplicate_detector.is_duplicate(job3, job3.description)

        self.assertFalse(is_dup1)
        self.assertTrue(is_dup2)
        self.assertTrue(is_dup3)

    def test_pipeline_execution(self):
        raw_jobs = [
            Job(
                job_id="p_001",
                title="Cloud Infrastructure Architect",
                company="AWS Systems",
                description="<p>Looking for a Senior Cloud Architect with expertise in AWS, Terraform, Docker, and Kubernetes.</p><p>EOE Employer.</p>",
                source="api"
            ),
            Job(
                job_id="p_002",
                title="Short Job",
                company="Unknown",
                description="Too short description.",  # Rejected due to length < 50
                source="api"
            ),
            Job(
                job_id="p_001",
                title="Cloud Infrastructure Architect",
                company="AWS Systems",
                description="<p>Looking for a Senior Cloud Architect with expertise in AWS, Terraform, Docker, and Kubernetes.</p><p>Duplicate job ID posting.</p>",
                source="api"
            )
        ]

        clean_jobs, stats = self.pipeline.process_jobs(raw_jobs)

        self.assertEqual(len(clean_jobs), 1)
        self.assertEqual(clean_jobs[0].job_id, "p_001")
        self.assertIn("Terraform, Docker, and Kubernetes", clean_jobs[0].clean_description)
        self.assertEqual(stats["total_raw_jobs_processed"], 3)
        self.assertEqual(stats["valid_clean_jobs_produced"], 1)
        self.assertEqual(stats["duplicates_removed"], 1)
        self.assertEqual(stats["jobs_rejected"], 1)


if __name__ == "__main__":
    unittest.main()
