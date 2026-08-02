"""
Comprehensive Unit Tests for CurricuAlign AI LLM Technology Intelligence Engine.
Tests: PromptBuilder, ResponseParser, ExtractionValidator, Cache, TechnologyExtractor.
"""

import json
import os
import sys
import tempfile
import unittest

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from backend.industry_engine.processing.llm.models import (
    TechnologyCategories,
    TechnologyExtraction,
    LLMConfig,
    LLMExecutionStats,
)
from backend.industry_engine.processing.llm.cache import TechnologyExtractionCache
from backend.industry_engine.processing.llm.prompt_builder import PromptBuilder, VALID_CATEGORIES
from backend.industry_engine.processing.llm.response_parser import ResponseParser
from backend.industry_engine.processing.llm.validator import ExtractionValidator
from backend.industry_engine.processing.llm.technology_extractor import TechnologyExtractor


# ============================================================
# Sample Data
# ============================================================

SAMPLE_JOB_DESCRIPTION = (
    "We are looking for a Senior AI Engineer proficient in Python and Java. "
    "Experience with FastAPI, React, and Spring Boot is required. "
    "Must have hands-on experience with PyTorch, TensorFlow, and LangChain. "
    "Familiarity with PostgreSQL, Redis, and MongoDB is a plus. "
    "Cloud experience on AWS and GCP is expected. "
    "Strong skills in Docker, Kubernetes, and Terraform are needed. "
    "Experience with Git, GitHub, and Jenkins is required. "
    "Knowledge of Apache Kafka and RabbitMQ is preferred. "
    "Testing with PyTest and JUnit is expected. "
    "Monitoring experience with Prometheus and Grafana. "
    "Linux administration skills required."
)

SAMPLE_LLM_RESPONSE_CLEAN = json.dumps({
    "languages": ["Python", "Java"],
    "frameworks": ["FastAPI", "React", "Spring Boot"],
    "libraries": [],
    "databases": ["PostgreSQL", "Redis", "MongoDB"],
    "cloud": ["AWS", "GCP"],
    "devops": ["Docker", "Kubernetes", "Jenkins"],
    "ai": ["PyTorch", "TensorFlow", "LangChain"],
    "vector_databases": [],
    "llm_frameworks": [],
    "agent_frameworks": [],
    "operating_systems": ["Linux"],
    "developer_tools": [],
    "version_control": ["Git", "GitHub"],
    "message_brokers": ["Apache Kafka", "RabbitMQ"],
    "container_technologies": [],
    "infrastructure_tools": ["Terraform"],
    "monitoring_tools": ["Prometheus", "Grafana"],
    "testing_frameworks": ["PyTest", "JUnit"],
})

SAMPLE_LLM_RESPONSE_MARKDOWN = (
    "```json\n"
    + SAMPLE_LLM_RESPONSE_CLEAN
    + "\n```"
)

SAMPLE_LLM_RESPONSE_WITH_HALLUCINATIONS = json.dumps({
    "languages": ["Python", "Java", "Rust"],  # "Rust" is hallucinated
    "frameworks": ["FastAPI", "Django"],        # "Django" is hallucinated
    "libraries": [],
    "databases": ["PostgreSQL"],
    "cloud": ["AWS"],
    "devops": ["Docker"],
    "ai": ["PyTorch"],
    "vector_databases": [],
    "llm_frameworks": [],
    "agent_frameworks": [],
    "operating_systems": ["Linux"],
    "developer_tools": [],
    "version_control": ["Git"],
    "message_brokers": [],
    "container_technologies": [],
    "infrastructure_tools": [],
    "monitoring_tools": [],
    "testing_frameworks": [],
})

SAMPLE_LLM_RESPONSE_ALIASED_CATEGORIES = json.dumps({
    "programming_languages": ["Python"],
    "cloud_platforms": ["AWS"],
    "devops_tools": ["Docker"],
    "ai_ml_frameworks": ["PyTorch"],
    "testing": ["PyTest"],
})


# ============================================================
# Test: PromptBuilder
# ============================================================

class TestPromptBuilder(unittest.TestCase):
    """Tests for PromptBuilder."""

    def setUp(self):
        self.builder = PromptBuilder()

    def test_system_prompt_contains_strict_rules(self):
        """System prompt must contain zero-hallucination rules."""
        sp = self.builder.system_prompt
        self.assertIn("Extract ONLY technologies", sp)
        self.assertIn("NEVER infer", sp)
        self.assertIn("guess", sp)
        self.assertIn("NEVER recommend", sp)
        self.assertIn("valid JSON", sp)

    def test_system_prompt_contains_all_categories(self):
        """System prompt must list all 18 valid categories."""
        sp = self.builder.system_prompt
        for cat in VALID_CATEGORIES:
            self.assertIn(f'"{cat}"', sp, f"Category '{cat}' missing from system prompt.")

    def test_user_prompt_contains_job_details(self):
        """User prompt must include job title, company, location, description."""
        up = self.builder.build_user_prompt(
            job_id="test_001",
            title="AI Engineer",
            company="TestCorp",
            location="Remote",
            clean_description="Python and Docker experience needed.",
        )
        self.assertIn("test_001", up)
        self.assertIn("AI Engineer", up)
        self.assertIn("TestCorp", up)
        self.assertIn("Remote", up)
        self.assertIn("Python and Docker experience needed.", up)

    def test_full_prompt_returns_both_prompts(self):
        """build_full_prompt must return dict with system_prompt and user_prompt."""
        result = self.builder.build_full_prompt(
            job_id="test_002",
            title="Backend Dev",
            company="Corp",
            location="NYC",
            clean_description="Java required.",
        )
        self.assertIn("system_prompt", result)
        self.assertIn("user_prompt", result)
        self.assertIsInstance(result["system_prompt"], str)
        self.assertIsInstance(result["user_prompt"], str)

    def test_user_prompt_has_delimiters(self):
        """User prompt should have start/end delimiters for the job description."""
        up = self.builder.build_user_prompt(
            job_id="test_003",
            title="Dev",
            company="X",
            location="Y",
            clean_description="Some description.",
        )
        self.assertIn("JOB DESCRIPTION START", up)
        self.assertIn("JOB DESCRIPTION END", up)


# ============================================================
# Test: ExtractionValidator
# ============================================================

class TestExtractionValidator(unittest.TestCase):
    """Tests for ExtractionValidator."""

    def setUp(self):
        self.validator = ExtractionValidator(strict_presence_check=True)

    def test_validate_structure_valid(self):
        """Valid structure should pass validation."""
        data = {"languages": ["Python"], "frameworks": ["FastAPI"]}
        is_valid, error = self.validator.validate_structure(data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_structure_invalid_type(self):
        """Non-dict input should fail."""
        is_valid, error = self.validator.validate_structure(["Python"])
        self.assertFalse(is_valid)
        self.assertIn("Expected dict", error)

    def test_validate_structure_invalid_category(self):
        """Unknown category should fail."""
        data = {"unknown_tech": ["X"]}
        is_valid, error = self.validator.validate_structure(data)
        self.assertFalse(is_valid)
        self.assertIn("Unexpected category", error)

    def test_validate_structure_non_list_value(self):
        """Category with non-list value should fail."""
        data = {"languages": "Python"}
        is_valid, error = self.validator.validate_structure(data)
        self.assertFalse(is_valid)
        self.assertIn("must be a list", error)

    def test_validate_structure_non_string_item(self):
        """Category with non-string items should fail."""
        data = {"languages": [123]}
        is_valid, error = self.validator.validate_structure(data)
        self.assertFalse(is_valid)
        self.assertIn("non-string", error)

    def test_normalize_categories_aliases(self):
        """Aliased category names should map to canonical keys."""
        data = {
            "programming_languages": ["Python"],
            "cloud_platforms": ["AWS"],
            "devops_tools": ["Docker"],
        }
        normalized = self.validator.normalize_categories(data)
        self.assertIn("Python", normalized["languages"])
        self.assertIn("AWS", normalized["cloud"])
        self.assertIn("Docker", normalized["devops"])

    def test_normalize_categories_unknown_dropped(self):
        """Unrecognized categories should be dropped."""
        data = {"languages": ["Python"], "blockchain": ["Solidity"]}
        # validate_structure would reject this, but normalize_categories just drops unknowns
        normalized = self.validator.normalize_categories(data)
        self.assertIn("Python", normalized["languages"])
        # "blockchain" is not a valid category, so "Solidity" is dropped
        total = sum(len(v) for v in normalized.values())
        self.assertEqual(total, 1)

    def test_deduplicate_case_insensitive(self):
        """Deduplication should be case-insensitive, preserving first occurrence."""
        data = {"languages": ["Python", "python", "PYTHON", "Java"]}
        deduped = self.validator.deduplicate(data)
        self.assertEqual(len(deduped["languages"]), 2)
        self.assertEqual(deduped["languages"][0], "Python")
        self.assertEqual(deduped["languages"][1], "Java")

    def test_deduplicate_strips_whitespace(self):
        """Empty and whitespace-only entries should be removed."""
        data = {"languages": ["Python", "  ", "", "Java"]}
        deduped = self.validator.deduplicate(data)
        self.assertEqual(deduped["languages"], ["Python", "Java"])

    def test_prune_hallucinations_removes_absent(self):
        """Technologies not in source text should be pruned."""
        data = {"languages": ["Python", "Rust"], "frameworks": ["FastAPI", "Django"]}
        source = "We need Python and FastAPI experience."
        pruned, removed = self.validator.prune_hallucinations(data, source)
        self.assertIn("Python", pruned["languages"])
        self.assertNotIn("Rust", pruned["languages"])
        self.assertIn("FastAPI", pruned["frameworks"])
        self.assertNotIn("Django", pruned["frameworks"])
        self.assertIn("Rust", removed)
        self.assertIn("Django", removed)

    def test_prune_hallucinations_case_insensitive(self):
        """Presence check should be case-insensitive."""
        data = {"languages": ["python"]}
        source = "Experience with Python required."
        pruned, removed = self.validator.prune_hallucinations(data, source)
        self.assertIn("python", pruned["languages"])
        self.assertEqual(len(removed), 0)

    def test_prune_hallucinations_short_names(self):
        """Short technology names (<=2 chars) should use word boundary matching."""
        data = {"languages": ["C", "R"]}
        source = "Experience with C programming and R statistics required."
        pruned, removed = self.validator.prune_hallucinations(data, source)
        self.assertIn("C", pruned["languages"])
        self.assertIn("R", pruned["languages"])

    def test_prune_hallucinations_short_name_false_positive(self):
        """Short name should NOT match when embedded in a word."""
        data = {"languages": ["R"]}
        source = "Experience with React and Redis required."
        pruned, removed = self.validator.prune_hallucinations(data, source)
        self.assertNotIn("R", pruned["languages"])
        self.assertIn("R", removed)

    def test_validate_and_clean_full_pipeline(self):
        """Full validation pipeline should work end-to-end."""
        data = json.loads(SAMPLE_LLM_RESPONSE_CLEAN)
        cleaned, removed, warnings = self.validator.validate_and_clean(
            data=data,
            source_text=SAMPLE_JOB_DESCRIPTION,
        )
        self.assertIn("Python", cleaned["languages"])
        self.assertIn("FastAPI", cleaned["frameworks"])
        self.assertEqual(len(removed), 0)

    def test_validate_and_clean_empty_extraction_warning(self):
        """Empty extraction should produce a warning."""
        data = {"languages": [], "frameworks": []}
        cleaned, removed, warnings = self.validator.validate_and_clean(
            data=data,
            source_text="No tech mentioned here.",
        )
        self.assertTrue(any("zero technologies" in w for w in warnings))


# ============================================================
# Test: ResponseParser
# ============================================================

class TestResponseParser(unittest.TestCase):
    """Tests for ResponseParser."""

    def setUp(self):
        self.parser = ResponseParser(strict_presence_check=True)

    def test_strip_markdown_fences_json(self):
        """Should strip ```json ... ``` wrappers."""
        raw = '```json\n{"languages": ["Python"]}\n```'
        result = self.parser.strip_markdown_fences(raw)
        self.assertEqual(result, '{"languages": ["Python"]}')

    def test_strip_markdown_fences_plain(self):
        """Should strip ``` ... ``` wrappers."""
        raw = '```\n{"languages": ["Python"]}\n```'
        result = self.parser.strip_markdown_fences(raw)
        self.assertEqual(result, '{"languages": ["Python"]}')

    def test_strip_markdown_fences_no_fence(self):
        """Should return text as-is if no fences."""
        raw = '{"languages": ["Python"]}'
        result = self.parser.strip_markdown_fences(raw)
        self.assertEqual(result, '{"languages": ["Python"]}')

    def test_extract_json_from_text_with_preamble(self):
        """Should extract JSON even with surrounding text."""
        raw = 'Here is the result:\n{"languages": ["Python"]}\nEnd.'
        result = self.parser.extract_json_from_text(raw)
        parsed = json.loads(result)
        self.assertEqual(parsed["languages"], ["Python"])

    def test_parse_json_valid(self):
        """Valid JSON string should parse to dict."""
        parsed = self.parser.parse_json(SAMPLE_LLM_RESPONSE_CLEAN)
        self.assertIsInstance(parsed, dict)
        self.assertIn("languages", parsed)

    def test_parse_json_invalid(self):
        """Invalid JSON should raise ValueError."""
        with self.assertRaises(ValueError):
            self.parser.parse_json("not valid json {{}}")

    def test_parse_response_clean(self):
        """Clean JSON response should parse into TechnologyExtraction."""
        result = self.parser.parse_response(
            raw_text=SAMPLE_LLM_RESPONSE_CLEAN,
            job_id="test_clean",
            source_text=SAMPLE_JOB_DESCRIPTION,
        )
        self.assertIsInstance(result, TechnologyExtraction)
        self.assertEqual(result.job_id, "test_clean")
        self.assertIn("Python", result.technologies.languages)
        self.assertIn("FastAPI", result.technologies.frameworks)

    def test_parse_response_markdown_wrapped(self):
        """Markdown-wrapped JSON should be handled correctly."""
        result = self.parser.parse_response(
            raw_text=SAMPLE_LLM_RESPONSE_MARKDOWN,
            job_id="test_md",
            source_text=SAMPLE_JOB_DESCRIPTION,
        )
        self.assertIsInstance(result, TechnologyExtraction)
        self.assertIn("Python", result.technologies.languages)

    def test_parse_response_prunes_hallucinations(self):
        """Hallucinated technologies should be pruned from the result."""
        result = self.parser.parse_response(
            raw_text=SAMPLE_LLM_RESPONSE_WITH_HALLUCINATIONS,
            job_id="test_halluc",
            source_text=SAMPLE_JOB_DESCRIPTION,
        )
        self.assertNotIn("Rust", result.technologies.languages)
        self.assertNotIn("Django", result.technologies.frameworks)
        self.assertIn("Python", result.technologies.languages)

    def test_parse_response_handles_nested_technologies_key(self):
        """Response with nested 'technologies' key should be unpacked."""
        nested = json.dumps({"technologies": {"languages": ["Python"], "frameworks": ["FastAPI"]}})
        result = self.parser.parse_response(
            raw_text=nested,
            job_id="test_nested",
            source_text="We use Python and FastAPI.",
        )
        self.assertIn("Python", result.technologies.languages)
        self.assertIn("FastAPI", result.technologies.frameworks)

    def test_parse_response_with_aliased_categories(self):
        """Aliased category names should be normalized."""
        result = self.parser.parse_response(
            raw_text=SAMPLE_LLM_RESPONSE_ALIASED_CATEGORIES,
            job_id="test_alias",
            source_text=SAMPLE_JOB_DESCRIPTION,
        )
        self.assertIn("Python", result.technologies.languages)
        self.assertIn("AWS", result.technologies.cloud)
        self.assertIn("Docker", result.technologies.devops)
        self.assertIn("PyTorch", result.technologies.ai)
        self.assertIn("PyTest", result.technologies.testing_frameworks)


# ============================================================
# Test: TechnologyExtractionCache
# ============================================================

class TestTechnologyExtractionCache(unittest.TestCase):
    """Tests for TechnologyExtractionCache."""

    def setUp(self):
        self.cache = TechnologyExtractionCache()
        self.sample_extraction = TechnologyExtraction(
            job_id="cache_001",
            technologies=TechnologyCategories(
                languages=["Python"],
                frameworks=["FastAPI"],
            ),
        )

    def test_cache_miss(self):
        """Cache should return None on miss."""
        result = self.cache.get("missing_id", "Some description")
        self.assertIsNone(result)

    def test_cache_set_and_hit(self):
        """Cache should return stored extraction on hit."""
        self.cache.set("cache_001", "Python FastAPI job", self.sample_extraction)
        result = self.cache.get("cache_001", "Python FastAPI job")
        self.assertIsNotNone(result)
        self.assertEqual(result.job_id, "cache_001")
        self.assertIn("Python", result.technologies.languages)

    def test_cache_has(self):
        """has() should return correct boolean."""
        self.assertFalse(self.cache.has("x", "y"))
        self.cache.set("x", "y", self.sample_extraction)
        self.assertTrue(self.cache.has("x", "y"))

    def test_cache_different_description_misses(self):
        """Different descriptions for same job_id should miss."""
        self.cache.set("cache_002", "Description A", self.sample_extraction)
        result = self.cache.get("cache_002", "Description B")
        self.assertIsNone(result)

    def test_cache_clear(self):
        """clear() should remove all entries and reset stats."""
        self.cache.set("a", "b", self.sample_extraction)
        self.cache.clear()
        self.assertFalse(self.cache.has("a", "b"))
        stats = self.cache.get_stats()
        self.assertEqual(stats["total_entries"], 0)
        self.assertEqual(stats["hits"], 0)
        self.assertEqual(stats["misses"], 0)

    def test_cache_stats(self):
        """Stats should track hits and misses correctly."""
        self.cache.set("s1", "d1", self.sample_extraction)
        self.cache.get("s1", "d1")  # hit
        self.cache.get("s1", "d1")  # hit
        self.cache.get("s2", "d2")  # miss

        stats = self.cache.get_stats()
        self.assertEqual(stats["hits"], 2)
        self.assertEqual(stats["misses"], 1)
        self.assertAlmostEqual(stats["hit_rate"], 2 / 3, places=3)

    def test_cache_persistence(self):
        """Cache should persist and reload from disk."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            persist_path = f.name

        try:
            # Write cache
            cache1 = TechnologyExtractionCache(persist_path=persist_path)
            cache1.set("p1", "desc1", self.sample_extraction)

            # Load into new cache instance
            cache2 = TechnologyExtractionCache(persist_path=persist_path)
            result = cache2.get("p1", "desc1")
            self.assertIsNotNone(result)
            self.assertEqual(result.job_id, "cache_001")
        finally:
            if os.path.exists(persist_path):
                os.remove(persist_path)


# ============================================================
# Test: TechnologyExtractor (End-to-End with Mock)
# ============================================================

class TestTechnologyExtractor(unittest.TestCase):
    """Tests for TechnologyExtractor with mocked Gemini responses."""

    def _mock_gemini(self, system_prompt: str, user_prompt: str) -> str:
        """Mock Gemini response function."""
        return SAMPLE_LLM_RESPONSE_CLEAN

    def setUp(self):
        self.config = LLMConfig(
            model_name="gemini-2.5-flash",
            temperature=0.0,
            max_tokens=2048,
            retry_count=1,
            timeout=10.0,
            api_key="mock-key",
        )
        self.extractor = TechnologyExtractor(
            config=self.config,
            mock_response_fn=self._mock_gemini,
            strict_presence_check=True,
        )

    def test_extract_returns_technology_extraction(self):
        """Extraction should return TechnologyExtraction with correct data."""
        result = self.extractor.extract(
            job_id="e2e_001",
            title="Senior AI Engineer",
            company="TestCorp",
            location="Remote",
            clean_description=SAMPLE_JOB_DESCRIPTION,
        )
        self.assertIsInstance(result, TechnologyExtraction)
        self.assertEqual(result.job_id, "e2e_001")
        self.assertIn("Python", result.technologies.languages)
        self.assertIn("Java", result.technologies.languages)
        self.assertIn("FastAPI", result.technologies.frameworks)
        self.assertIn("PostgreSQL", result.technologies.databases)
        self.assertIn("AWS", result.technologies.cloud)

    def test_extract_has_stats(self):
        """Extraction result should contain LLM execution stats."""
        result = self.extractor.extract(
            job_id="e2e_stats",
            title="Dev",
            company="Corp",
            location="NYC",
            clean_description=SAMPLE_JOB_DESCRIPTION,
        )
        self.assertIsNotNone(result.stats)
        self.assertFalse(result.stats.cache_hit)
        self.assertGreater(result.stats.prompt_tokens, 0)

    def test_extract_caches_result(self):
        """Second call with same input should be a cache hit."""
        desc = SAMPLE_JOB_DESCRIPTION
        self.extractor.extract(
            job_id="cache_test",
            title="Dev",
            company="Corp",
            location="NYC",
            clean_description=desc,
        )
        result2 = self.extractor.extract(
            job_id="cache_test",
            title="Dev",
            company="Corp",
            location="NYC",
            clean_description=desc,
        )
        self.assertTrue(result2.stats.cache_hit)

    def test_extract_from_clean_job(self):
        """extract_from_clean_job should accept CleanJob and return result."""
        from backend.industry_engine.models.clean_job import CleanJob

        clean_job = CleanJob(
            job_id="cj_001",
            title="ML Engineer",
            company="AIStartup",
            location="San Francisco",
            clean_description=SAMPLE_JOB_DESCRIPTION,
            source="api",
        )
        result = self.extractor.extract_from_clean_job(clean_job)
        self.assertIsInstance(result, TechnologyExtraction)
        self.assertEqual(result.job_id, "cj_001")

    def test_cache_stats_tracking(self):
        """Cache stats should reflect actual usage patterns."""
        desc = SAMPLE_JOB_DESCRIPTION
        self.extractor.extract(
            job_id="stats_test", title="D", company="C", location="L", clean_description=desc,
        )
        self.extractor.extract(
            job_id="stats_test", title="D", company="C", location="L", clean_description=desc,
        )
        stats = self.extractor.get_cache_stats()
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)

    def test_clear_cache(self):
        """Clearing cache should reset all entries."""
        self.extractor.extract(
            job_id="clear_test", title="D", company="C", location="L",
            clean_description=SAMPLE_JOB_DESCRIPTION,
        )
        self.extractor.clear_cache()
        stats = self.extractor.get_cache_stats()
        self.assertEqual(stats["total_entries"], 0)


# ============================================================
# Test: Models
# ============================================================

class TestModels(unittest.TestCase):
    """Tests for data models."""

    def test_technology_categories_defaults(self):
        """TechnologyCategories should default all lists to empty."""
        tc = TechnologyCategories()
        for field_name in TechnologyCategories.model_fields:
            self.assertEqual(getattr(tc, field_name), [])

    def test_technology_extraction_creation(self):
        """TechnologyExtraction should be constructable with required fields."""
        te = TechnologyExtraction(
            job_id="model_test",
            technologies=TechnologyCategories(languages=["Python"]),
        )
        self.assertEqual(te.job_id, "model_test")
        self.assertIn("Python", te.technologies.languages)
        self.assertIsNotNone(te.extraction_timestamp)

    def test_llm_config_defaults(self):
        """LLMConfig should have sensible defaults."""
        config = LLMConfig()
        self.assertEqual(config.temperature, 0.0)
        self.assertEqual(config.max_tokens, 2048)
        self.assertEqual(config.retry_count, 3)
        self.assertEqual(config.timeout, 30.0)

    def test_llm_execution_stats_defaults(self):
        """LLMExecutionStats should default to zeroed values."""
        stats = LLMExecutionStats()
        self.assertEqual(stats.prompt_tokens, 0)
        self.assertEqual(stats.completion_tokens, 0)
        self.assertFalse(stats.cache_hit)

    def test_technology_extraction_serialization(self):
        """TechnologyExtraction should serialize to dict and back."""
        te = TechnologyExtraction(
            job_id="serial_test",
            technologies=TechnologyCategories(
                languages=["Python", "Java"],
                frameworks=["FastAPI"],
            ),
            stats=LLMExecutionStats(prompt_tokens=100, completion_tokens=50),
        )
        data = te.model_dump()
        restored = TechnologyExtraction(**data)
        self.assertEqual(restored.job_id, "serial_test")
        self.assertEqual(restored.technologies.languages, ["Python", "Java"])
        self.assertEqual(restored.stats.prompt_tokens, 100)


if __name__ == "__main__":
    unittest.main(verbosity=2)
