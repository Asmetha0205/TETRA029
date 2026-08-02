"""
Configuration for CurricuAlign AI Technology Normalization Engine.

Centralizes all tunable knobs: alias file path, category overrides,
validation rules, and the unknown technology policy. Backed by pydantic
so invalid configuration fails fast at construction time.
"""

import os
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field


class UnknownPolicy(str, Enum):
    """
    Policy for handling technologies that are not present in the registry.

    KEEP    - Keep unknowns and surface them in the result.
    FLAG    - Flag unknowns (default) and surface them for future approval.
    DISCARD - Drop unknown technologies entirely.
    """

    KEEP = "keep"
    FLAG = "flag"
    DISCARD = "discard"


class ValidationRules(BaseModel):
    """
    Validation constraints applied to every extracted technology value.
    """

    min_length: int = Field(default=1, ge=1, description="Minimum accepted name length.")
    max_length: int = Field(default=64, ge=1, description="Maximum accepted name length.")
    allow_numeric_only: bool = Field(default=False, description="Whether numeric-only names are accepted.")
    allow_non_string: bool = Field(default=False, description="Whether non-string values are coerced and accepted.")
    invalid_chars_regex: str = Field(
        default=r"[^\w\s.#+/&'-]",
        description="Regex matching characters that are not allowed in a technology name.",
    )


class NormalizationConfig(BaseModel):
    """
    Top-level configuration for the Technology Normalization Engine.
    """

    alias_file: Optional[str] = Field(
        default=None,
        description="Optional JSON file of alias entries loaded into the registry.",
    )
    categories: Dict[str, str] = Field(
        default_factory=dict,
        description="Technology -> category overrides applied on top of the builtin registry.",
    )
    validation: ValidationRules = Field(default_factory=ValidationRules)
    unknown_policy: UnknownPolicy = Field(
        default=UnknownPolicy.FLAG,
        description="Policy for unknown technology handling.",
    )
    case_sensitive: bool = Field(
        default=False,
        description="If True, matching becomes case-sensitive (default False).",
    )

    @classmethod
    def from_env(cls) -> "NormalizationConfig":
        """
        Build a config from environment variables.
        """
        return cls(
            alias_file=os.getenv("CURRICUALIGN_ALIAS_FILE", None),
            unknown_policy=UnknownPolicy(os.getenv("CURRICUALIGN_UNKNOWN_POLICY", UnknownPolicy.FLAG.value)),
        )
