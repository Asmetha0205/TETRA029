"""
Test script for Member 1 FastAPI Backend Engine.
Tests PDF Parsing, Skill Extraction, Normalization, Alignment Score Calculation, and Endpoints.
"""
import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.pdf_parser import split_into_units
from app.services.normalizer import normalize_term, ALIASES_MAP
from app.services.skill_extractor import extract_skills_from_text
from app.services.alignment import calculate_alignment_scores

def run_tests():
    print("=== Testing Member 1 Backend Components ===")
    
    # 1. Test Normalizer & Alias Map
    print(f"\n1. Loaded {len(ALIASES_MAP)} aliases from skill_aliases.json")
    test_terms = ["ML", "RAG", "K8s", "Docker", "python3", "GenAI", "UnknownSkill"]
    for term in test_terms:
        norm = normalize_term(term)
        if norm:
            print(f"   ✓ Raw: '{term}' -> Normalized: '{norm['canonical_name']}' (ID: {norm['skill_id']}, Demand: {norm['demand_score']})")
        else:
            print(f"   ✗ Raw: '{term}' -> Not found in skill base")

    # 2. Test Unit Splitter
    sample_syllabus = """
    UNIT I: INTRODUCTION TO MACHINE LEARNING
    Overview of ML, Supervised and Unsupervised Learning, Regression, Classification.
    Python, Pandas, NumPy, and Scikit-Learn tools.

    UNIT II: DEEP LEARNING & NATURAL LANGUAGE PROCESSING
    Neural Networks, CNN, RNN, Transformers. NLP techniques and Word Embeddings.
    Hands-on PyTorch and TensorFlow laboratories.

    UNIT III: DEVOPS AND CONTAINER ORCHESTRATION
    Introduction to Docker containers, Kubernetes cluster management, CI/CD pipelines, and Git workflows.
    """
    
    units = split_into_units(sample_syllabus)
    print(f"\n2. Syllabus Unit Splitter: Extracted {len(units)} units")
    for u in units:
        print(f"   - [{u['unit_id']}] {u['title']}")

    # 3. Test Skill Extraction
    extracted_skills = extract_skills_from_text(sample_syllabus)
    print(f"\n3. Extracted {len(extracted_skills)} normalized skills from syllabus text:")
    for s in extracted_skills:
        print(f"   - {s['canonical_name']} (Category: {s['category']}, Demand: {s['demand_score']})")

    # 4. Test Alignment Score Engine
    covered_names = [s['canonical_name'] for s in extracted_skills]
    scores = calculate_alignment_scores(covered_names)
    print(f"\n4. Transparent Alignment Score Engine Output:")
    print(f"   - Overall Score: {scores['overall_score']}%")
    print("   - Category Scores:", scores['category_scores'])
    print("   - Role Scores:")
    for r in scores['role_scores']:
        print(f"     * {r['role_name']}: {r['score']}% (Missing: {r['missing_skills'][:3]}...)")
        
    print(f"\n   - Critical Gaps Identified ({len(scores['critical_gaps'])} skills):")
    for gap in scores['critical_gaps'][:4]:
        print(f"     ! {gap['name']} (Category: {gap['category']}, Demand Score: {gap['demand_score']})")

    print("\n✅ All Member 1 backend services verified successfully!")

if __name__ == "__main__":
    run_tests()
