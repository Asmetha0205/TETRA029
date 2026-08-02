"""
Academic Document Data Models for CurricuAlign AI Academic Engine.
"""

import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ParsedSection(BaseModel):
    """A section detected within an academic document."""
    title: str = Field(..., description="Section heading title.")
    content: str = Field(..., description="Text content of the section.")
    section_type: str = Field(default="general", description="Category of section (syllabus, outcomes, etc.).")


class ParsedAcademicDocument(BaseModel):
    """
    Structured representation of a parsed university curriculum PDF document.
    """
    document_id: str = Field(..., description="Unique document identifier.")
    university_name: str = Field(default="Unknown University")
    department: str = Field(default="Computer Science")
    degree_program: str = Field(default="B.Tech Computer Science")
    academic_year: str = Field(default="2025-2026")
    total_pages: int = Field(default=1)
    clean_text: str = Field(..., description="Full cleaned text of the document.")
    sections: List[ParsedSection] = Field(default_factory=list)
    courses: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    parse_timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
