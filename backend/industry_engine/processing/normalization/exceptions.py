"""
Custom Exceptions for CurricuAlign AI Technology Normalization Engine.

All normalization errors derive from a single base class so callers can
either catch granular errors or handle the whole subsystem uniformly.
"""


class NormalizationError(Exception):
    """Base exception for all Technology Normalization Engine errors."""

    pass


class MalformedInputError(NormalizationError):
    """Raised when the input technology profile is malformed or not valid JSON."""

    pass


class EmptyTechnologyNameError(NormalizationError):
    """Raised when a technology name is empty or blank."""

    pass


class InvalidTechnologyNameError(NormalizationError):
    """Raised when a technology name contains invalid characters or is numeric-only."""

    pass


class UnknownCategoryError(NormalizationError):
    """Raised when a technology category cannot be resolved to a canonical category."""

    pass


class InvalidAliasError(NormalizationError):
    """Raised when an alias is empty, malformed, or maps to an unregistered technology."""

    pass


class DuplicateCanonicalIdError(NormalizationError):
    """Raised when two canonical technologies resolve to the same canonical ID."""

    pass


class TechnologyNotRegisteredError(NormalizationError):
    """Raised when an operation requires a registered technology that does not exist."""

    pass
