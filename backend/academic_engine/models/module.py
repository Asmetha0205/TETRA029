"""
Course Module Data Model for Academic Engine.
"""

from typing import List
from pydantic import BaseModel, Field


class AcademicModule(BaseModel):
    """
    Representation of a specific module/unit within a course.
    """
    module_number: int = Field(default=1, ge=1)
    title: str = Field(..., description="Module heading title.")
    topics: List[str] = Field(default_factory=list, description="Topics taught within this module.")
    hours: float = Field(default=0.0, ge=0.0)
