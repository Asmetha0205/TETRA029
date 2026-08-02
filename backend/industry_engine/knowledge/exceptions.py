"""
Custom Exceptions for the CurricuAlign AI Industry Knowledge Layer.

Provides a structured exception hierarchy for error handling across
knowledge management, snapshots, versions, and validation operations.
"""


class KnowledgeError(Exception):
    """Base exception for all Knowledge Layer errors."""
    pass


class TechnologyNotFound(KnowledgeError):
    """Raised when a technology record is not found in the repository."""
    pass


class DuplicateTechnology(KnowledgeError):
    """Raised when attempting to create a technology that already exists."""
    pass


class SnapshotError(KnowledgeError):
    """Raised when a snapshot operation fails (create, load, compare, rollback)."""
    pass


class VersionError(KnowledgeError):
    """Raised when a versioning operation fails or encounters an invalid state."""
    pass


class ValidationError(KnowledgeError):
    """Raised when data validation fails during creation or update."""
    pass


class RepositoryError(KnowledgeError):
    """Raised when a persistence operation (load, save, delete) fails."""
    pass


class SnapshotNotFoundError(SnapshotError):
    """Raised when a specific snapshot ID is not found."""
    pass


class SnapshotComparisonError(SnapshotError):
    """Raised when snapshot comparison fails due to incompatible snapshots."""
    pass


class InvalidVersionFormat(VersionError):
    """Raised when a version string does not follow semantic versioning."""
    pass


class TechnologyIdConflict(KnowledgeError):
    """Raised when a generated technology ID conflicts with an existing record."""
    pass
