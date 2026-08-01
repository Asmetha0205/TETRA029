from typing import List, Dict, Any
from .normalizer import INDUSTRY_SKILL_BASE, ROLE_SKILL_MAP, SKILLS_BY_ID, SKILLS_BY_NAME

ROLE_NAMES = {
    "data_scientist": "Data Scientist",
    "ml_engineer": "AI / ML Engineer",
    "full_stack": "Full Stack Developer",
    "cloud_engineer": "Cloud / DevOps Engineer",
    "cyber_analyst": "Cybersecurity Analyst"
}

def calculate_alignment_scores(covered_skills_input: List[str]) -> Dict[str, Any]:
    """
    Computes transparent alignment scores using formula:
    alignment(role) = Σ (coverage_i × demand_weight_i) / Σ demand_weight_i * 100
    where coverage_i ∈ {0, 0.5, 1.0}
    """
    # 1. Normalize covered skill input to skill IDs
    covered_ids = set()
    for item in covered_skills_input:
        item_lower = item.strip().lower()
        if item_lower in SKILLS_BY_ID:
            covered_ids.add(item_lower)
        elif item_lower in SKILLS_BY_NAME:
            covered_ids.add(SKILLS_BY_NAME[item_lower]["id"])
        else:
            # Match by name or canonical name
            for s in INDUSTRY_SKILL_BASE:
                if item_lower == s["name"].lower() or item_lower in [a.lower() for a in s.get("aliases", [])]:
                    covered_ids.add(s["id"])
                    break

    # 2. Compute Role-Wise Alignment Scores
    role_scores = []
    total_role_weights = 0.0
    weighted_role_score_sum = 0.0

    for role_id, required_skill_ids in ROLE_SKILL_MAP.items():
        role_name = ROLE_NAMES.get(role_id, role_id.replace("_", " ").title())
        
        numerator = 0.0
        denominator = 0.0
        covered_count = 0
        missing_skills = []

        for skill_id in required_skill_ids:
            skill_info = SKILLS_BY_ID.get(skill_id, {})
            demand_weight = skill_info.get("demand_score", 0.5)
            skill_name = skill_info.get("name", skill_id)

            denominator += demand_weight

            if skill_id in covered_ids:
                coverage = 1.0
                covered_count += 1
                numerator += (coverage * demand_weight)
            else:
                # Check for partial coverage (same category match)
                skill_cat = skill_info.get("category", "")
                has_category_coverage = any(
                    SKILLS_BY_ID.get(cid, {}).get("category") == skill_cat 
                    for cid in covered_ids
                )
                if has_category_coverage:
                    coverage = 0.5
                    numerator += (coverage * demand_weight)
                else:
                    coverage = 0.0
                missing_skills.append(skill_name)

        role_score = round((numerator / denominator * 100), 1) if denominator > 0 else 0.0
        
        role_scores.append({
            "role_id": role_id,
            "role_name": role_name,
            "score": role_score,
            "total_required": len(required_skill_ids),
            "total_covered": covered_count,
            "missing_skills": missing_skills
        })

        weighted_role_score_sum += role_score
        total_role_weights += 1.0

    # Overall Score is average across key roles
    overall_score = round(weighted_role_score_sum / max(1, len(role_scores)), 1)

    # 3. Compute Category-Wise Scores
    categories: Dict[str, Dict[str, Any]] = {}
    for skill in INDUSTRY_SKILL_BASE:
        cat = skill.get("category", "General")
        if cat not in categories:
            categories[cat] = {"num": 0.0, "den": 0.0, "covered": 0, "total": 0}
        
        weight = skill.get("demand_score", 0.5)
        categories[cat]["den"] += weight
        categories[cat]["total"] += 1
        
        if skill["id"] in covered_ids:
            categories[cat]["num"] += (1.0 * weight)
            categories[cat]["covered"] += 1

    category_scores = {}
    for cat, data in categories.items():
        cat_score = round((data["num"] / data["den"] * 100), 1) if data["den"] > 0 else 0.0
        category_scores[cat] = cat_score

    # 4. Identify Critical Gaps (demand_score >= 0.85 and missing)
    critical_gaps = []
    for skill in INDUSTRY_SKILL_BASE:
        if skill["id"] not in covered_ids and skill.get("demand_score", 0.0) >= 0.85:
            critical_gaps.append({
                "skill_id": skill["id"],
                "name": skill["name"],
                "category": skill["category"],
                "demand_score": skill["demand_score"],
                "trend": skill["trend"],
                "sources": skill.get("sources", [])
            })
            
    critical_gaps.sort(key=lambda x: x["demand_score"], reverse=True)

    formula_explanation = (
        "alignment(role) = Σ (coverage_i × demand_weight_i) / Σ demand_weight_i * 100. "
        "Coverage is 1.0 for direct syllabus coverage, 0.5 for partial category coverage, and 0.0 for missing skills. "
        "Weights are grounded on NASSCOM FutureSkills demand scores."
    )

    return {
        "overall_score": overall_score,
        "formula_explanation": formula_explanation,
        "category_scores": category_scores,
        "role_scores": role_scores,
        "covered_skills": [SKILLS_BY_ID[cid]["name"] for cid in covered_ids if cid in SKILLS_BY_ID],
        "critical_gaps": critical_gaps
    }
