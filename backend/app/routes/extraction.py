from fastapi import APIRouter, HTTPException
from ..models.schemas import SkillExtractRequest, SkillExtractResponse, NormalizedSkill
from ..services.skill_extractor import extract_skills_from_text, extract_skills_by_units
from ..services.normalizer import get_all_canonical_skills

router = APIRouter(tags=["Stage 2 - Skill Extraction & Normalization"])

@router.post("/extract-skills", response_model=SkillExtractResponse)
async def extract_and_normalize_skills(payload: SkillExtractRequest):
    """
    Stage 2 — Skill Extraction & Normalization: Extracts technical terms from
    syllabus text or units, and normalizes them using Malav's skill_aliases.json map.
    """
    if payload.units and len(payload.units) > 0:
        units_dict = [u.model_dump() for u in payload.units]
        extracted = extract_skills_by_units(units_dict)
        
        normalized_objs = [
            NormalizedSkill(
                raw_term=s["raw_term"],
                canonical_name=s["canonical_name"],
                skill_id=s["skill_id"],
                category=s.get("category"),
                demand_score=s.get("demand_score", 0.5),
                units_covered=s.get("units_covered", [])
            )
            for s in extracted["normalized_skills"]
        ]
        
        return SkillExtractResponse(
            total_raw_found=extracted["total_raw_found"],
            total_normalized=extracted["total_normalized"],
            normalized_skills=normalized_objs,
            skills_by_unit=extracted["skills_by_unit"]
        )
    
    elif payload.syllabus_text:
        skills = extract_skills_from_text(payload.syllabus_text)
        normalized_objs = [
            NormalizedSkill(
                raw_term=s["raw_term"],
                canonical_name=s["canonical_name"],
                skill_id=s["skill_id"],
                category=s.get("category"),
                demand_score=s.get("demand_score", 0.5),
                units_covered=["all"]
            )
            for s in skills
        ]
        
        return SkillExtractResponse(
            total_raw_found=len(skills),
            total_normalized=len(skills),
            normalized_skills=normalized_objs,
            skills_by_unit={"all": [s["canonical_name"] for s in skills]}
        )
    
    else:
        raise HTTPException(status_code=400, detail="Provide either syllabus_text or units list.")

@router.get("/skill-base")
async def get_industry_skill_base():
    """
    Returns the complete NASSCOM FutureSkills industry skill base.
    """
    return get_all_canonical_skills()
