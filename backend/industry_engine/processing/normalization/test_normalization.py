"""
Comprehensive Unit Tests for CurricuAlign AI Technology Normalization Engine.
Tests: Normalizer, Registry, AliasResolver, Canonicalizer, CategoryMapper,
DuplicateMerger, UnknownDetector, Validator, and the full Pipeline.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from backend.industry_engine.processing.normalization.config import NormalizationConfig, UnknownPolicy
from backend.industry_engine.processing.normalization.exceptions import (
    DuplicateCanonicalIdError,
    EmptyTechnologyNameError,
    InvalidAliasError,
    InvalidTechnologyNameError,
    MalformedInputError,
    TechnologyNotRegisteredError,
)
from backend.industry_engine.processing.normalization.models import (
    TechnologyProfile,
    TechnologyStatus,
    UnknownTechnology,
)
from backend.industry_engine.processing.normalization.normalizer import TechnologyNormalizer
from backend.industry_engine.processing.normalization.technology_registry import TechnologyRegistry
from backend.industry_engine.processing.normalization.alias_resolver import AliasResolver
from backend.industry_engine.processing.normalization.canonicalizer import Canonicalizer
from backend.industry_engine.processing.normalization.category_mapper import CategoryMapper
from backend.industry_engine.processing.normalization.duplicate_merger import DuplicateMerger
from backend.industry_engine.processing.normalization.unknown_detector import UnknownDetector
from backend.industry_engine.processing.normalization.validator import TechnologyValidator
from backend.industry_engine.processing.normalization.pipeline import NormalizationPipeline


# ============================================================
# Sample Data
# ============================================================

SAMPLE_RAW_PROFILE = {
    "languages": ["Python", "py", "JS", "TS"],
    "frameworks": ["FastAPI", "fast api", "React"],
    "databases": ["Redis", "redis", "Redis Cache", "Postgres", "MongoDB"],
    "ai": ["LLMs", "Gen AI", "AI/ML", "LangChain", "MCP"],
    "devops": ["Docker", "K8s", "Kubernetes"],
}


class TestTechnologyNormalizer(unittest.TestCase):

    def setUp(self):
        self.normalizer = TechnologyNormalizer()

    def test_normalize_collapses_whitespace(self):
        self.assertEqual(self.normalizer.normalize("  Fast   API  "), "Fast API")

    def test_normalize_strips(self):
        self.assertEqual(self.normalizer.normalize("   Redis   "), "Redis")

    def test_normalize_rejects_non_string(self):
        with self.assertRaises(InvalidTechnologyNameError):
            self.normalizer.normalize(123)

    def test_soft_key_lowercases(self):
        self.assertEqual(self.normalizer.normalize_key_soft("Fast API"), "fast api")
        self.assertEqual(self.normalizer.normalize_key_soft("C++"), "c++")
        self.assertEqual(self.normalizer.normalize_key_soft("C#"), "c#")

    def test_aggressive_key_removes_punctuation(self):
        self.assertEqual(self.normalizer.normalize_key_aggressive("Fast API"), "fastapi")
        self.assertEqual(self.normalizer.normalize_key_aggressive("M/L"), "ml")
        self.assertEqual(self.normalizer.normalize_key_aggressive("machine-learning"), "machinelearning")
        self.assertEqual(self.normalizer.normalize_key_aggressive("C++"), "c++")
        self.assertEqual(self.normalizer.normalize_key_aggressive("C#"), "c#")

    def test_slugify(self):
        self.assertEqual(self.normalizer.slugify("Machine Learning"), "machine-learning")
        self.assertEqual(self.normalizer.slugify("FastAPI"), "fastapi")
        self.assertEqual(self.normalizer.slugify("C++"), "c++")


class TestTechnologyRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = TechnologyRegistry()

    def test_builtin_loaded(self):
        self.assertGreater(len(self.registry), 100)

    def test_register_and_resolve(self):
        self.registry.register("FakeTech", "Framework", ["fake alias"])
        self.assertTrue(self.registry.is_known("fake alias"))
        self.assertEqual(self.registry.resolve("FakeTech"), "FakeTech")
        self.assertEqual(self.registry.resolve("fake alias"), "FakeTech")
        self.assertEqual(self.registry.get_category("FakeTech"), "Framework")

    def test_duplicate_canonical_id_raises(self):
        with self.assertRaises(DuplicateCanonicalIdError):
            self.registry.register("PYTHON", "AI / ML", [])

    def test_empty_canonical_name_raises(self):
        with self.assertRaises(EmptyTechnologyNameError):
            self.registry.register("   ", "AI / ML", [])

    def test_register_alias_unknown_raises(self):
        with self.assertRaises(TechnologyNotRegisteredError):
            self.registry.register_alias("DoesNotExist", "foo")

    def test_register_blank_alias_raises(self):
        with self.assertRaises(InvalidAliasError):
            self.registry.register("SomeNewTech", "Framework", ["   "])

    def test_resolve_unknown_returns_none(self):
        self.assertIsNone(self.registry.resolve("MCP"))
        self.assertIsNone(self.registry.resolve("Completely Random Tech 2026"))

    def test_get_entry_by_id(self):
        entry = self.registry.get_entry_by_id("python")
        self.assertIsNotNone(entry)
        self.assertEqual(entry.canonical_name, "Python")

    def test_load_external_alias_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(
                [
                    {"canonical_name": "RocketMQ", "category": "Message Broker", "aliases": ["apache rocketmq"]},
                    {"canonical_name": "WebAssembly", "category": "Programming Language", "aliases": ["wasm"]},
                ],
                f,
            )
            path = f.name
        try:
            config = NormalizationConfig(alias_file=path)
            reg = TechnologyRegistry(config=config)
            self.assertTrue(reg.is_known("wasm"))
            self.assertEqual(reg.resolve("apache rocketmq"), "RocketMQ")
            self.assertEqual(reg.get_category("WebAssembly"), "Programming Language")
        finally:
            os.unlink(path)


class TestAliasResolver(unittest.TestCase):

    def setUp(self):
        self.resolver = AliasResolver(TechnologyRegistry())

    def test_alias_normalization_examples(self):
        cases = {
            "ML": "Machine Learning",
            "machine-learning": "Machine Learning",
            "M/L": "Machine Learning",
            "AI/ML": "Artificial Intelligence & Machine Learning",
            "GenAI": "Generative AI",
            "Gen AI": "Generative AI",
            "LLMs": "Large Language Models",
            "K8s": "Kubernetes",
            "JS": "JavaScript",
            "TS": "TypeScript",
            "Postgres": "PostgreSQL",
            "Redis Cache": "Redis",
            "Fast API": "FastAPI",
            "fast-api": "FastAPI",
        }
        for raw, canonical in cases.items():
            self.assertEqual(
                self.resolver.resolve(raw), canonical, f"Expected '{raw}' -> '{canonical}'"
            )

    def test_direct_vs_alias_kind(self):
        canonical, kind = self.resolver.resolve_with_kind("Redis")
        self.assertEqual(canonical, "Redis")
        self.assertEqual(kind, "direct")

        canonical, kind = self.resolver.resolve_with_kind("redis cache")
        self.assertEqual(canonical, "Redis")
        self.assertEqual(kind, "alias")

    def test_resolve_unknown(self):
        self.assertIsNone(self.resolver.resolve("MCP"))


class TestCanonicalizer(unittest.TestCase):

    def setUp(self):
        self.registry = TechnologyRegistry()
        self.canonicalizer = Canonicalizer(self.registry)

    def test_canonicalize_known(self):
        tech, unknown = self.canonicalizer.canonicalize("Redis Cache", source_category="databases")
        self.assertIsNone(unknown)
        self.assertIsNotNone(tech)
        self.assertEqual(tech.canonical_name, "Redis")
        self.assertEqual(tech.id, "redis")
        self.assertEqual(tech.category, "Database")
        self.assertEqual(tech.status, TechnologyStatus.KNOWN)
        self.assertIn("redis cache", tech.aliases)
        self.assertEqual(tech.source_category, "databases")

    def test_canonicalize_unknown(self):
        tech, unknown = self.canonicalizer.canonicalize("MCP", source_category="ai")
        self.assertIsNone(tech)
        self.assertIsNotNone(unknown)
        self.assertEqual(unknown.technology, "MCP")
        self.assertEqual(unknown.category, "Unknown")


class TestCategoryMapper(unittest.TestCase):

    def setUp(self):
        self.mapper = CategoryMapper()

    def test_to_display(self):
        self.assertEqual(self.mapper.to_display("languages"), "Programming Language")
        self.assertEqual(self.mapper.to_display("databases"), "Database")
        self.assertEqual(self.mapper.to_display("devops"), "DevOps")
        self.assertEqual(self.mapper.to_display("cloud"), "Cloud")
        self.assertEqual(self.mapper.to_display("llm_frameworks"), "LLM Framework")
        self.assertEqual(self.mapper.to_display("agent_frameworks"), "Agent Framework")

    def test_unknown_category_falls_back_verbatim(self):
        self.assertEqual(self.mapper.to_display("bogus_category"), "bogus_category")

    def test_assign_prefers_registry_category(self):
        category = self.mapper.assign("LangChain", "LLM Framework", "ai")
        self.assertEqual(category, "LLM Framework")

    def test_assign_falls_back_to_source_category(self):
        category = self.mapper.assign("SomeTech", None, "databases")
        self.assertEqual(category, "Database")


class TestDuplicateMerger(unittest.TestCase):

    def setUp(self):
        self.canonicalizer = Canonicalizer(TechnologyRegistry())
        self.merger = DuplicateMerger()

    def test_merge_duplicates(self):
        techs = [
            self.canonicalizer.canonicalize("Redis", source_category="databases")[0],
            self.canonicalizer.canonicalize("redis", source_category="databases")[0],
            self.canonicalizer.canonicalize("Redis Cache", source_category="databases")[0],
            self.canonicalizer.canonicalize("Python", source_category="languages")[0],
        ]
        merged, count = self.merger.merge(techs)
        self.assertEqual(count, 2)
        self.assertEqual(len(merged), 2)
        redis = next(t for t in merged if t.canonical_name == "Redis")
        self.assertEqual(len(redis.matched_variants), 3)

    def test_no_duplicates(self):
        techs = [
            self.canonicalizer.canonicalize("Python", source_category="languages")[0],
            self.canonicalizer.canonicalize("Docker", source_category="devops")[0],
        ]
        merged, count = self.merger.merge(techs)
        self.assertEqual(count, 0)
        self.assertEqual(len(merged), 2)


class TestUnknownDetector(unittest.TestCase):

    def setUp(self):
        self.registry = TechnologyRegistry()

    def test_detect_unknown(self):
        detector = UnknownDetector(self.registry)
        record = detector.detect("MCP", source_category="ai")
        self.assertIsNotNone(record)
        self.assertEqual(record.category, "Unknown")
        self.assertIsNone(detector.detect("Python"))

    def test_flag_policy_keeps_unknowns(self):
        detector = UnknownDetector(self.registry, policy=UnknownPolicy.FLAG)
        surfaced, dropped = detector.apply_policy(
            [UnknownTechnology(technology="MCP", category="Unknown")]
        )
        self.assertEqual(len(surfaced), 1)
        self.assertEqual(dropped, 0)

    def test_discard_policy_drops_unknowns(self):
        detector = UnknownDetector(self.registry, policy=UnknownPolicy.DISCARD)
        surfaced, dropped = detector.apply_policy(
            [UnknownTechnology(technology="MCP", category="Unknown")]
        )
        self.assertEqual(len(surfaced), 0)
        self.assertEqual(dropped, 1)


class TestTechnologyValidator(unittest.TestCase):

    def setUp(self):
        self.validator = TechnologyValidator()

    def test_valid_values(self):
        for value in ["Python", "C++", "C#", "Fast API", "R&D", "LangChain"]:
            is_valid, _ = self.validator.validate_value(value)
            self.assertTrue(is_valid, f"Expected '{value}' to be valid")

    def test_empty_name_rejected(self):
        is_valid, reason = self.validator.validate_value("   ")
        self.assertFalse(is_valid)
        self.assertIn("Empty", reason)

    def test_numeric_only_rejected(self):
        is_valid, reason = self.validator.validate_value("12345")
        self.assertFalse(is_valid)
        self.assertIn("Numeric-only", reason)

    def test_invalid_characters_rejected(self):
        is_valid, _ = self.validator.validate_value("Python!!")
        self.assertFalse(is_valid)

    def test_non_string_rejected(self):
        is_valid, _ = self.validator.validate_value(123)
        self.assertFalse(is_valid)

    def test_overlong_rejected(self):
        is_valid, _ = self.validator.validate_value("X" * 100)
        self.assertFalse(is_valid)

    def test_validate_profile_collects_rejections(self):
        profile = TechnologyProfile.from_raw({"languages": ["Python", "", "12345", "ok!!"]})
        valid, rejected = self.validator.validate_profile(profile)
        self.assertEqual(len(valid), 1)
        self.assertEqual(len(rejected), 3)


class TestPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = NormalizationPipeline()

    def test_pipeline_example_output_format(self):
        result = self.pipeline.normalize_raw(SAMPLE_RAW_PROFILE)
        output = result.to_dict()

        self.assertIn("normalized", output)
        self.assertIn("unknown", output)

        # Python merged with py
        python = next(t for t in output["normalized"] if t["canonical_name"] == "Python")
        self.assertEqual(python["category"], "Programming Language")
        self.assertIn("py", python["aliases"])

        # FastAPI merged from "FastAPI" + "fast api"
        fastapi = next(t for t in output["normalized"] if t["canonical_name"] == "FastAPI")
        self.assertEqual(fastapi["category"], "Framework")

        # Redis merged from Redis / redis / Redis Cache
        redis = next(t for t in output["normalized"] if t["canonical_name"] == "Redis")
        self.assertEqual(redis["category"], "Database")

        # MCP flagged as unknown
        self.assertTrue(any(u["technology"] == "MCP" for u in output["unknown"]))
        mcp = next(u for u in output["unknown"] if u["technology"] == "MCP")
        self.assertEqual(mcp["category"], "Unknown")

    def test_pipeline_report_counts(self):
        result = self.pipeline.normalize_raw(SAMPLE_RAW_PROFILE)
        report = result.report

        self.assertEqual(report.total_technologies, 20)
        self.assertEqual(report.known, 14)
        self.assertEqual(report.unknown, 1)
        self.assertEqual(report.duplicates_merged, 5)
        self.assertEqual(report.rejected_values, 0)
        self.assertGreaterEqual(report.aliases_resolved, 9)

    def test_pipeline_rejects_invalid_values(self):
        raw = {
            "languages": ["Python", "", "2024", "JS!!", 123],
            "databases": ["Redis"],
        }
        result = self.pipeline.normalize_raw(raw)
        self.assertEqual(result.report.rejected_values, 4)
        self.assertEqual(result.report.known, 2)
        self.assertEqual(len(result.rejected), 4)

    def test_pipeline_malformed_json(self):
        with self.assertRaises(MalformedInputError):
            self.pipeline.normalize_raw("{ this is not valid json")

    def test_pipeline_accepts_json_string(self):
        raw_json = json.dumps({"languages": ["Python", "py"], "ai": ["MCP"]})
        result = self.pipeline.normalize_raw(raw_json)
        self.assertEqual(result.report.known, 1)
        self.assertEqual(result.report.unknown, 1)

    def test_pipeline_technology_profile_object(self):
        profile = TechnologyProfile.from_raw({"languages": ["python", "py"]})
        result = self.pipeline.normalize(profile)
        self.assertEqual(len(result.normalized), 1)
        self.assertEqual(result.normalized[0].canonical_name, "Python")

    def test_pipeline_registry_category_overrides_llm_category(self):
        raw = {"ai": ["LangChain", "CrewAI"]}
        result = self.pipeline.normalize_raw(raw)
        names = {t["canonical_name"]: t["category"] for t in result.to_dict()["normalized"]}
        self.assertEqual(names["LangChain"], "LLM Framework")
        self.assertEqual(names["CrewAI"], "Agent Framework")

    def test_pipeline_discard_unknown_policy(self):
        pipeline = NormalizationPipeline(config=NormalizationConfig(unknown_policy=UnknownPolicy.DISCARD))
        result = pipeline.normalize_raw({"ai": ["MCP", "LLMs"]})
        self.assertEqual(result.report.unknown, 0)
        self.assertEqual(len(result.unknown), 0)
        self.assertEqual(result.report.known, 1)

    def test_pipeline_custom_registry_category_override(self):
        config = NormalizationConfig(categories={"Redis": "Custom Store"})
        pipeline = NormalizationPipeline(config=config)
        result = pipeline.normalize_raw({"databases": ["Redis"]})
        self.assertEqual(result.normalized[0].category, "Custom Store")


if __name__ == "__main__":
    unittest.main()
