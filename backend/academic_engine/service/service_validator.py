"""
Service Validator for Academic Service Layer.
"""


class AcademicServiceValidator:
    """Validates parameters passed to Academic Service Layer facade."""

    @staticmethod
    def validate_document_id(document_id: str) -> str:
        if not document_id or not document_id.strip():
            raise ValueError("document_id must be a non-empty string.")
        return document_id.strip()

    @staticmethod
    def validate_query(query: str) -> str:
        if not query or not query.strip():
            raise ValueError("query string must be non-empty.")
        return query.strip()
