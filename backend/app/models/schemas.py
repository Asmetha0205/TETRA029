from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SyllabusUnit(BaseModel):
    unit_id: str
    title: str
    text: str
    extracted_skills: List[str] = []

class UploadResponse(BaseModel):
    status: str
    filename: str
    character_count: int
    unit_count: int
    units: List[SyllabusUnit]
    raw_text_preview: str

class SkillExtractRequest(BaseModel):
    syllabus_text: Optional[str] = None
    units: Optional[List[SyllabusUnit]] = None

class NormalizedSkill(BaseModel):
    raw_term: str
    canonical_name: str
    skill_id: Optional[str] = None
    category: Optional[str] = None
    demand_score: float = 0.0
    units_covered: List[str] = []

class SkillExtractResponse(BaseModel):
    total_raw_found: int
    total_normalized: int
    normalized_skills: List[NormalizedSkill]
    skills_by_unit: Dict[str, List[str]]

class AlignmentScoreRequest(BaseModel):
    covered_skill_ids: Optional[List[str]] = None
    covered_skill_names: Optional[List[str]] = None
    target_role: Optional[str] = "all"

class RoleScore(BaseModel):
    role_id: str
    role_name: str
    score: float
    total_required: int
    total_covered: int
    missing_skills: List[str]

class CategoryScore(BaseModel):
    category: str
    score: float
    covered_count: int
    total_count: int

class AlignmentScoreResponse(BaseModel):
    overall_score: float
    formula_explanation: str
    category_scores: Dict[str, float]
    role_scores: List[RoleScore]
    covered_skills: List[str]
    critical_gaps: List[Dict[str, Any]]
