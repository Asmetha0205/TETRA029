import json
import os
from fastapi import APIRouter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GRAPH_FIXTURE_PATH = os.path.join(BASE_DIR, "graph_sample.json")

router = APIRouter(tags=["Knowledge Graph Layer"])

@router.get("/graph")
async def get_knowledge_graph():
    """
    Returns the Knowledge Graph { nodes, edges } dataset for Member 5 React Flow visualization.
    Checks live Neo4j database first, or falls back to graph_sample.json fixture.
    """
    # 1. Attempt Live Neo4j query if NEO4J_URI environment variable is provided
    if os.getenv("NEO4J_URI"):
        try:
            import graph_db
            return graph_db.fetch_graph()
        except Exception:
            pass

    # 2. Fallback to graph_sample.json fixture pushed by Member 3 (Malav)
    if os.path.exists(GRAPH_FIXTURE_PATH):
        with open(GRAPH_FIXTURE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    return {"nodes": [], "edges": []}
