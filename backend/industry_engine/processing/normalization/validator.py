"""
Technology Validator for CurricuAlign AI Technology Normalization Engine.

Validates raw extracted technology values before normalization. Rejects empty
names, invalid characters, numeric-only values, overlong names, and malformed
(non-string) entries.
"""

import logging
import re
from typing import Any, List, Optional, Tuple

from backend.industry_engine.processing.normalization.config import NormalizationConfig, ValidationRules
from backend.industry_engine.processing.normalization.models import RejectedValue, TechnologyProfile

logger = logging.getLogger("industry_engine.processing.normalization.validator")


class TechnologyValidator:
    """
    Validates technology names against configurable validation rules.
    """

    def __init__(self, config: Optional[NormalizationConfig] = None, rules: Optional[ValidationRules] = None):
        self._config = config or NormalizationConfig()
        self._rules = rules or self._config.validation
        self._invalid_chars_re = re.compile(self._rules.invalid_chars_regex) if self._rules.invalid_chars_regex else None

    def validate_value(self, value: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate a single technology value.

        Returns:
            (is_valid, rejection_reason)
        """
        if not isinstance(value, str):
            if self._rules.allow_non_string:
                value = str(value)
            else:
                return False, f"Non-string technology value: {value!r}"

        stripped = value.strip()
        if not stripped:
            return False, "Empty technology name"

        if len(stripped) < self._rules.min_length:
            return False, f"Name shorter than minimum length {self._rules.min_length}"

        if len(stripped) > self._rules.max_length:
            return False, f"Name exceeds maximum length {self._rules.max_length}"

        if stripped.isdigit() and not self._rules.allow_numeric_only:
            return False, f"Numeric-only technology name: '{stripped}'"

        if self._invalid_chars_re and self._invalid_chars_re.search(stripped):
            return False, f"Invalid characters in technology name: '{stripped}'"

        return True, None

    def validate_profile(
        self,
        profile: TechnologyProfile,
    ) -> Tuple[List[Tuple[str, str]], List[RejectedValue]]:
        """
        Validate every value in a TechnologyProfile.

        Returns:
            (valid_items, rejected_values)
            valid_items is a list of (category_key, value) tuples.
        """
        valid_items: List[Tuple[str, str]] = []
        rejected: List[RejectedValue] = []

        for category_key, values in profile.categories.items():
            if not isinstance(values, list):
                rejected.append(RejectedValue(value=values, category=str(category_key), reason="Category value is not a list"))
                continue
            for value in values:
                is_valid, reason = self.validate_value(value)
                if is_valid:
                    valid_items.append((str(category_key), str(value).strip()))
                else:
                    rejected.append(
                        RejectedValue(
                            value=value,
                            category=str(category_key),
                            reason=reason or "Validation failed",
                        )
                    )
                    logger.debug(
                        f"[Validator] Rejected value {value!r} in category '{category_key}': {reason}"
                    )

        if rejected:
            logger.info(f"[Validator] Rejected {len(rejected)} invalid technology value(s).")

        return valid_items, rejected
