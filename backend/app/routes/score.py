from fastapi import APIRouter
from ..models.schemas import AlignmentScoreRequest, AlignmentScoreResponse, RoleScore
from ..services.alignment import calculate_alignment_scores

router = APIRouter(tags=["Stage 4 - Alignment Score Engine"])

@router.post("/alignment-score", response_model=AlignmentScoreResponse)
async def get_alignment_score(payload: AlignmentScoreRequest):
    """
    Stage 4 — Alignment Score: Calculates transparent non-black-box alignment scores
    weighted by NASSCOM FutureSkills demand scores across roles & categories.
    """
    covered_skills = payload.covered_skill_ids or payload.covered_skill_names or []
    
    # If no skills provided, fallback to standard baseline CS syllabus coverage
    if not covered_skills:
        covered_skills = [
            "skill_python", "skill_sql", "skill_ml", "skill_deep_learning",
            "skill_nlp", "skill_git", "skill_html_css", "skill_javascript", "skill_rest_api"
        ]

    scores_result = calculate_alignment_scores(covered_skills)
    
    role_objs = [
        RoleScore(
            role_id=r["role_id"],
            role_name=r["role_name"],
            score=r["score"],
            total_required=r["total_required"],
            total_covered=r["total_covered"],
            missing_skills=r["missing_skills"]
        )
        for r in scores_result["role_scores"]
    ]

    return AlignmentScoreResponse(
        overall_score=scores_result["overall_score"],
        formula_explanation=scores_result["formula_explanation"],
        category_scores=scores_result["category_scores"],
        role_scores=role_objs,
        covered_skills=scores_result["covered_skills"],
        critical_gaps=scores_result["critical_gaps"]
    )
