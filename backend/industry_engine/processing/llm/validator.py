"""
Extraction Validator for CurricuAlign AI LLM Technology Intelligence Engine.
Strict validation, category normalization, deduplication, and hallucination pruning.
"""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional

from backend.industry_engine.processing.llm.prompt_builder import VALID_CATEGORIES

logger = logging.getLogger("industry_engine.processing.llm.validator")

# Map common alternate category names returned by LLMs to canonical category keys
CATEGORY_ALIASES: Dict[str, str] = {
    "programming_languages": "languages",
    "programming languages": "languages",
    "language": "languages",
    "framework": "frameworks",
    "library": "libraries",
    "database": "databases",
    "cloud_platforms": "cloud",
    "cloud platforms": "cloud",
    "cloud_services": "cloud",
    "devops_tools": "devops",
    "devops tools": "devops",
    "ai_ml": "ai",
    "ai_ml_frameworks": "ai",
    "ai/ml": "ai",
    "ai / ml frameworks": "ai",
    "ml": "ai",
    "machine_learning": "ai",
    "vector_database": "vector_databases",
    "vector databases": "vector_databases",
    "llm_framework": "llm_frameworks",
    "llm frameworks": "llm_frameworks",
    "agent_framework": "agent_frameworks",
    "agent frameworks": "agent_frameworks",
    "operating_system": "operating_systems",
    "operating systems": "operating_systems",
    "os": "operating_systems",
    "developer_tool": "developer_tools",
    "developer tools": "developer_tools",
    "dev_tools": "developer_tools",
    "version_control_systems": "version_control",
    "version control": "version_control",
    "vcs": "version_control",
    "message_broker": "message_brokers",
    "message brokers": "message_brokers",
    "messaging": "message_brokers",
    "container_technology": "container_technologies",
    "container technologies": "container_technologies",
    "containers": "container_technologies",
    "infrastructure_tool": "infrastructure_tools",
    "infrastructure tools": "infrastructure_tools",
    "infrastructure": "infrastructure_tools",
    "iac": "infrastructure_tools",
    "monitoring_tool": "monitoring_tools",
    "monitoring tools": "monitoring_tools",
    "monitoring": "monitoring_tools",
    "observability": "monitoring_tools",
    "testing_framework": "testing_frameworks",
    "testing frameworks": "testing_frameworks",
    "testing": "testing_frameworks",
    "test_frameworks": "testing_frameworks",
}


class ExtractionValidator:
    """
    Validates, normalizes, deduplicates, and prunes LLM extraction results.
    Ensures zero hallucinations by verifying technology presence in source text.
    """

    def __init__(self, strict_presence_check: bool = True):
        """
        Args:
            strict_presence_check: If True, every extracted technology name is checked
                                   against the original job description text. Technologies
                                   not found in the source are removed.
        """
        self._strict_presence_check = strict_presence_check

    def validate_structure(self, data: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate that the parsed data is a dictionary with valid category keys.

        Returns:
            Tuple of (is_valid, error_message).
        """
        if not isinstance(data, dict):
            return False, f"Expected dict, got {type(data).__name__}"

        for key, value in data.items():
            normalized_key = self._normalize_category(key)
            if normalized_key is None:
                return False, f"Unexpected category: '{key}'"
            if not isinstance(value, list):
                return False, f"Category '{key}' must be a list, got {type(value).__name__}"
            for item in value:
                if not isinstance(item, str):
                    return False, f"Category '{key}' contains non-string value: {item!r}"

        return True, None

    def normalize_categories(self, data: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Map any aliased category names to canonical VALID_CATEGORIES keys.
        Unrecognized categories are dropped with a warning.
        """
        normalized: Dict[str, List[str]] = {cat: [] for cat in VALID_CATEGORIES}

        for key, values in data.items():
            canonical = self._normalize_category(key)
            if canonical is None:
                logger.warning(f"[Validator] Dropping unrecognized category: '{key}'")
                continue
            normalized[canonical].extend(values)

        return normalized

    def deduplicate(self, data: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Remove duplicate technology entries within each category (case-insensitive).
        Preserves the first occurrence's casing.
        """
        deduped: Dict[str, List[str]] = {}
        for category, techs in data.items():
            seen_lower: Dict[str, str] = {}
            unique: List[str] = []
            for tech in techs:
                tech_stripped = tech.strip()
                if not tech_stripped:
                    continue
                lower = tech_stripped.lower()
                if lower not in seen_lower:
                    seen_lower[lower] = tech_stripped
                    unique.append(tech_stripped)
            deduped[category] = unique
        return deduped

    def prune_hallucinations(
        self,
        data: Dict[str, List[str]],
        source_text: str,
    ) -> Tuple[Dict[str, List[str]], List[str]]:
        """
        Remove technologies not explicitly found in the source job description text.

        Args:
            data: Normalized, deduplicated extraction dictionary.
            source_text: Original cleaned job description text to verify against.

        Returns:
            Tuple of (pruned_data, list_of_removed_technologies).
        """
        if not self._strict_presence_check:
            return data, []

        source_lower = source_text.lower()
        pruned: Dict[str, List[str]] = {}
        removed: List[str] = []

        for category, techs in data.items():
            valid_techs: List[str] = []
            for tech in techs:
                # Check if the technology name appears in the source text (case-insensitive)
                # Use word-boundary-aware matching for short names to avoid false positives
                tech_lower = tech.lower()
                if len(tech_lower) <= 2:
                    # Very short names (e.g. "C", "R") require word boundary matching
                    pattern = r'(?<![a-zA-Z])' + re.escape(tech_lower) + r'(?![a-zA-Z])'
                    if re.search(pattern, source_lower):
                        valid_techs.append(tech)
                    else:
                        removed.append(tech)
                        logger.debug(
                            f"[Validator] Pruned hallucinated technology '{tech}' "
                            f"from category '{category}' — not found in source text."
                        )
                else:
                    if tech_lower in source_lower:
                        valid_techs.append(tech)
                    else:
                        removed.append(tech)
                        logger.debug(
                            f"[Validator] Pruned hallucinated technology '{tech}' "
                            f"from category '{category}' — not found in source text."
                        )
            pruned[category] = valid_techs

        if removed:
            logger.info(
                f"[Validator] Pruned {len(removed)} hallucinated technologies: {removed}"
            )

        return pruned, removed

    def validate_and_clean(
        self,
        data: Any,
        source_text: str,
    ) -> Tuple[Dict[str, List[str]], List[str], List[str]]:
        """
        Full validation pipeline: structure check → normalize → deduplicate → prune.

        Args:
            data: Raw parsed JSON from LLM response.
            source_text: Original cleaned job description text.

        Returns:
            Tuple of (cleaned_data, removed_hallucinations, validation_warnings).
        """
        warnings: List[str] = []

        # Step 1: Structure validation
        is_valid, error_msg = self.validate_structure(data)
        if not is_valid:
            logger.error(f"[Validator] Structure validation failed: {error_msg}")
            raise ValueError(f"Invalid extraction structure: {error_msg}")

        # Step 2: Normalize categories
        normalized = self.normalize_categories(data)

        # Step 3: Deduplicate
        deduped = self.deduplicate(normalized)

        # Step 4: Prune hallucinations
        pruned, removed = self.prune_hallucinations(deduped, source_text)

        # Step 5: Check for entirely empty extraction
        total_techs = sum(len(v) for v in pruned.values())
        if total_techs == 0:
            warnings.append("Extraction produced zero technologies across all categories.")
            logger.warning("[Validator] Extraction result is entirely empty.")

        return pruned, removed, warnings

    def _normalize_category(self, key: str) -> Optional[str]:
        """
        Normalize a category key to its canonical form.
        Returns None if the key is unrecognized.
        """
        key_clean = key.strip().lower()
        if key_clean in VALID_CATEGORIES:
            return key_clean
        return CATEGORY_ALIASES.get(key_clean)
