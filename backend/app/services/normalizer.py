import json
import os
from typing import Dict, Any, Optional, List, Tuple

# Path resolution: locate project root (where skill_aliases.json and industry_skill_base.json are located)
CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
# Navigate up: services -> app -> backend -> ROOT
BASE_DIR = os.path.abspath(os.path.join(CURRENT_FILE_DIR, "..", "..", ".."))

ALIASES_PATH = os.path.join(BASE_DIR, "skill_aliases.json")
SKILL_BASE_PATH = os.path.join(BASE_DIR, "industry_skill_base.json")
ROLE_MAP_PATH = os.path.join(BASE_DIR, "role_skill_map.json")

def load_data_files() -> Tuple[Dict[str, str], List[Dict[str, Any]], Dict[str, List[str]]]:
    aliases = {}
    if os.path.exists(ALIASES_PATH):
        with open(ALIASES_PATH, "r", encoding="utf-8") as f:
            aliases = json.load(f)

    skill_base = []
    if os.path.exists(SKILL_BASE_PATH):
        with open(SKILL_BASE_PATH, "r", encoding="utf-8") as f:
            skill_base = json.load(f)

    role_map = {}
    if os.path.exists(ROLE_MAP_PATH):
        with open(ROLE_MAP_PATH, "r", encoding="utf-8") as f:
            role_map = json.load(f)

    return aliases, skill_base, role_map

# Load into memory on module import
ALIASES_MAP, INDUSTRY_SKILL_BASE, ROLE_SKILL_MAP = load_data_files()

# Index skill base by canonical name and skill_id for fast lookup
SKILLS_BY_NAME = {item["name"].lower(): item for item in INDUSTRY_SKILL_BASE}
SKILLS_BY_ID = {item["id"]: item for item in INDUSTRY_SKILL_BASE}

def normalize_term(raw_term: str) -> Optional[Dict[str, Any]]:
    """
    Normalizes a raw skill string against skill_aliases.json and industry_skill_base.json.
    Example: 'ML' -> Canonical 'Machine Learning', ID 'skill_ml', Demand 0.88.
    """
    term_clean = raw_term.strip().lower()
    
    # 1. Check exact alias match
    canonical_name = ALIASES_MAP.get(term_clean)
    
    # 2. Check skill base name match if no alias
    if not canonical_name:
        if term_clean in SKILLS_BY_NAME:
            canonical_name = SKILLS_BY_NAME[term_clean]["name"]
            
    # 3. Check alias list inside skill base items
    if not canonical_name:
        for item in INDUSTRY_SKILL_BASE:
            item_aliases = [a.lower() for a in item.get("aliases", [])]
            if term_clean in item_aliases or term_clean == item["name"].lower():
                canonical_name = item["name"]
                break
                
    if not canonical_name:
        return None

    # Retrieve full skill metadata
    skill_item = SKILLS_BY_NAME.get(canonical_name.lower())
    if skill_item:
        return {
            "raw_term": raw_term,
            "canonical_name": skill_item["name"],
            "skill_id": skill_item["id"],
            "category": skill_item.get("category", "General"),
            "demand_score": skill_item.get("demand_score", 0.5),
            "trend": skill_item.get("trend", "stable"),
            "sources": skill_item.get("sources", ["NASSCOM FutureSkills"])
        }
        
    return {
        "raw_term": raw_term,
        "canonical_name": canonical_name,
        "skill_id": f"skill_{canonical_name.lower().replace(' ', '_')}",
        "category": "General",
        "demand_score": 0.5,
        "trend": "stable",
        "sources": ["Syllabus Extracted"]
    }

def get_all_canonical_skills() -> List[Dict[str, Any]]:
    return INDUSTRY_SKILL_BASE

def get_role_map() -> Dict[str, List[str]]:
    return ROLE_SKILL_MAP
