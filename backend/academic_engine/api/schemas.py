"""
API Schemas for Academic REST API.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class UploadMetadataResponse(BaseModel):
    """Response model for uploaded document metadata."""
    document_id: str
    filename: str
    file_size_bytes: int
    checksum: str
    university_name: str
    curriculum_year: str
    department: str
    upload_timestamp: str
    status: str


class DocumentListResponse(BaseModel):
    """List of uploaded documents."""
    total: int
    documents: List[UploadMetadataResponse]


class AcademicTechnologyResponse(BaseModel):
    """Response model for single academic technology record."""
    technology_id: str
    canonical_name: str
    category: str
    aliases: List[str] = Field(default_factory=list)
    university: str
    department: str
    degree_program: str
    course_code: str
    course_name: str
    semester: str
    credits: float
    frequency: int
    status: str
    version: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AcademicTechnologyListResponse(BaseModel):
    """List of academic technologies."""
    total: int
    technologies: List[AcademicTechnologyResponse]


class CourseResponse(BaseModel):
    """Response model for single academic course."""
    course_id: str
    course_code: str
    title: str
    credits: float
    semester: str


class CourseListResponse(BaseModel):
    """List of academic courses."""
    total: int
    courses: List[CourseResponse]


class PipelineSummaryResponse(BaseModel):
    """Response model for complete pipeline summary."""
    documents_processed: int
    courses_detected: int
    technologies_extracted: int
    new_technologies: int
    normalized: int
    unknown: int
    snapshot_created: bool
    execution_time: str
