import re
from typing import List, Dict, Any
from .normalizer import normalize_term, ALIASES_MAP, INDUSTRY_SKILL_BASE

def extract_skills_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extracts and normalizes technical skills from raw text using alias map and skill base patterns.
    """
    text_lower = text.lower()
    found_skills: Dict[str, Dict[str, Any]] = {}
    
    # 1. Scan for canonical skill names and aliases in text
    for skill_item in INDUSTRY_SKILL_BASE:
        name = skill_item["name"]
        aliases = skill_item.get("aliases", [])
        
        all_terms = [name] + aliases
        for term in all_terms:
            # Word boundary regex search to avoid substring mismatches
            pattern = r'\b' + re.escape(term.lower()) + r'\b'
            if re.search(pattern, text_lower):
                skill_id = skill_item["id"]
                if skill_id not in found_skills:
                    found_skills[skill_id] = {
                        "raw_term": term,
                        "canonical_name": skill_item["name"],
                        "skill_id": skill_item["id"],
                        "category": skill_item.get("category", "General"),
                        "demand_score": skill_item.get("demand_score", 0.5),
                        "trend": skill_item.get("trend", "stable"),
                        "sources": skill_item.get("sources", [])
                    }
                break

    # 2. Check alias map entries
    for alias_term, canonical_name in ALIASES_MAP.items():
        pattern = r'\b' + re.escape(alias_term.lower()) + r'\b'
        if re.search(pattern, text_lower):
            normalized = normalize_term(alias_term)
            if normalized:
                skill_id = normalized["skill_id"]
                if skill_id not in found_skills:
                    found_skills[skill_id] = normalized

    return list(found_skills.values())

def extract_skills_by_units(units: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extracts skills unit by unit and returns normalized skills list and unit breakdown.
    """
    all_normalized_map: Dict[str, Dict[str, Any]] = {}
    skills_by_unit: Dict[str, List[str]] = {}
    
    for unit in units:
        unit_id = unit.get("unit_id", "unit_1")
        unit_text = unit.get("text", "") + " " + unit.get("title", "")
        
        unit_skills = extract_skills_from_text(unit_text)
        unit_skill_names = [s["canonical_name"] for s in unit_skills]
        
        unit["extracted_skills"] = unit_skill_names
        skills_by_unit[unit_id] = unit_skill_names
        
        for skill in unit_skills:
            skill_id = skill["skill_id"]
            if skill_id not in all_normalized_map:
                skill["units_covered"] = [unit_id]
                all_normalized_map[skill_id] = skill
            else:
                if unit_id not in all_normalized_map[skill_id]["units_covered"]:
                    all_normalized_map[skill_id]["units_covered"].append(unit_id)
                    
    normalized_list = list(all_normalized_map.values())
    
    return {
        "total_raw_found": len(normalized_list),
        "total_normalized": len(normalized_list),
        "normalized_skills": normalized_list,
        "skills_by_unit": skills_by_unit
    }
