"""
Course Data Model for Academic Engine.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AcademicCourse(BaseModel):
    """
    Representation of an academic course detected in a curriculum PDF.
    """
    course_id: str = Field(..., description="Unique course identifier (e.g. 'cs101').")
    course_code: str = Field(..., description="Official course code (e.g. 'CS-101', 'CSE302').")
    title: str = Field(..., description="Course title.")
    credits: float = Field(default=3.0, ge=0.0)
    semester: str = Field(default="Semester 1")
    department: str = Field(default="Computer Science")
    prerequisites: List[str] = Field(default_factory=list)
    modules: List[Dict[str, Any]] = Field(default_factory=list)
    learning_outcomes: List[str] = Field(default_factory=list)
    description: str = Field(default="")
    metadata: Dict[str, Any] = Field(default_factory=dict)
