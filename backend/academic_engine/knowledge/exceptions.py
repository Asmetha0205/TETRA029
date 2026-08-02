"""
Custom Exceptions for Academic Knowledge Layer.
"""


class AcademicKnowledgeError(Exception):
    """Base exception for Academic Knowledge Layer errors."""
    pass


class AcademicRecordNotFoundError(AcademicKnowledgeError):
    """Raised when an AcademicTechnologyRecord is not found."""
    pass


class AcademicRepositoryError(AcademicKnowledgeError):
    """Raised when repository operation fails."""
    pass
