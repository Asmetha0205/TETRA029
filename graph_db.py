"""
CurricuAlign AI — Member 3 (Indian Data & Knowledge Graph Lead)
Neo4j / AuraDB layer: connection, loader, and the /graph query.

Usage:
    python graph_db.py test     # HOUR-ZERO: verify AuraDB connects (run this FIRST)
    python graph_db.py load     # wipe + load skills/roles/relationships from JSON
    python graph_db.py graph    # print the node/edge JSON Member 1's /graph endpoint returns

Credentials come from environment variables (NEO4J_URI / NEO4J_USER /
NEO4J_PASSWORD), loaded from a local .env if python-dotenv is installed.
Never hardcode credentials.
"""
import json
import os
import sys
from pathlib import Path

from neo4j import GraphDatabase

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional; env vars may be set another way

HERE = Path(__file__).parent
SKILL_BASE = HERE / "industry_skill_base.json"
ROLE_MAP = HERE / "role_skill_map.json"

# The rising GenAI cluster is dual-labelled :Skill:EmergingTech so the graph can
# highlight the gap-driving nodes. These IDs MUST exist in industry_skill_base.json.
EMERGING_IDS = {
    "skill_generative_ai",
    "skill_llm",
    "skill_rag",
    "skill_vectordb",
    "skill_prompt_eng",
    "skill_ai_agents",
}


def get_driver():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USER")
    password = os.environ.get("NEO4J_PASSWORD")
    if not all([uri, user, password]):
        raise ValueError("Missing environment variables: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD")
    return GraphDatabase.driver(uri, auth=(user, password))


# --------------------------------------------------------------------------- #
# HOUR-ZERO connectivity check & offline fallback
# --------------------------------------------------------------------------- #
def fetch_offline_graph():
    """Fallback generator when AuraDB is offline/not configured yet."""
    from build_graph_fixture import build
    return build()

def cmd_test():
    try:
        driver = get_driver()
        driver.verify_connectivity()
        with driver.session() as s:
            val = s.run("RETURN 1 AS ok").single()["ok"]
        print(f"OK: connected to AuraDB, test query returned {val}")
        driver.close()
    except Exception as e:
        print(f"AuraDB Connectivity Check: NOT CONNECTED ({e})")
        print("Note: Set real NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD in .env to connect to live Neo4j AuraDB.")
        print("Offline fixture (graph_sample.json) is available for Member 1 & Member 5.")


# --------------------------------------------------------------------------- #
# Loader
# --------------------------------------------------------------------------- #
def _load_json():
    skills = json.loads(SKILL_BASE.read_text(encoding="utf-8"))
    roles = json.loads(ROLE_MAP.read_text(encoding="utf-8"))
    return skills, roles

def _create_constraints(tx):
    for label in ("Skill", "Role", "Course", "Unit", "EmergingTech"):
        tx.run(
            f"CREATE CONSTRAINT {label.lower()}_id IF NOT EXISTS "
            f"FOR (n:{label}) REQUIRE n.id IS UNIQUE"
        )

def _load_skills(tx, skills):
    tx.run(
        """
        UNWIND $skills AS s
        MERGE (n:Skill {id: s.id})
        SET n.name = s.name,
            n.category = s.category,
            n.demand_score = s.demand_score,
            n.trend = s.trend,
            n.aliases = s.aliases
        WITH n, s
        WHERE s.id IN $emerging
        SET n:EmergingTech
        """,
        skills=skills, emerging=list(EMERGING_IDS),
    )

def _load_related(tx, skills):
    pairs = [{"src": s["id"], "dst": r}
             for s in skills for r in s.get("related_skills", [])]
    tx.run(
        """
        UNWIND $pairs AS p
        MATCH (a:Skill {id: p.src})
        MATCH (b:Skill {id: p.dst})
        MERGE (a)-[:RELATED_TO]->(b)
        """,
        pairs=pairs,
    )

def _load_roles(tx, roles, skills):
    skill_ids = {s["id"] for s in skills}
    tx.run("UNWIND $roles AS r MERGE (:Role {id: r.id})",
           roles=[{"id": rid} for rid in roles])
    req = [{"skill": sid, "role": rid}
           for rid, sids in roles.items() for sid in sids if sid in skill_ids]
    tx.run(
        """
        UNWIND $req AS p
        MATCH (sk:Skill {id: p.skill})
        MATCH (ro:Role {id: p.role})
        MERGE (sk)-[:REQUIRED_BY]->(ro)
        """,
        req=req,
    )
    # (Role)-[:DEMANDS]->(EmergingTech): role demands an emerging skill it requires.
    demands = [{"role": rid, "tech": sid}
               for rid, sids in roles.items()
               for sid in sids if sid in EMERGING_IDS]
    tx.run(
        """
        UNWIND $demands AS p
        MATCH (ro:Role {id: p.role})
        MATCH (et:EmergingTech {id: p.tech})
        MERGE (ro)-[:DEMANDS]->(et)
        """,
        demands=demands,
    )

def cmd_load():
    skills, roles = _load_json()
    try:
        driver = get_driver()
        with driver.session() as s:
            s.run("MATCH (n) DETACH DELETE n")  # clean slate for the demo
            s.execute_write(_create_constraints)
            s.execute_write(_load_skills, skills)
            s.execute_write(_load_related, skills)
            s.execute_write(_load_roles, roles, skills)
            counts = s.run(
                "MATCH (n) RETURN labels(n)[0] AS l, count(*) AS c ORDER BY l"
            ).data()
        print("Loaded successfully into Neo4j:", {c["l"]: c["c"] for c in counts})
        driver.close()
    except Exception as e:
        print(f"Error loading into Neo4j: {e}")
        print("Ensure valid credentials in .env and network connectivity.")


# --------------------------------------------------------------------------- #
# /graph query  ->  { "nodes": [...], "edges": [...] }
# --------------------------------------------------------------------------- #
GRAPH_QUERY = """
MATCH (n)
WHERE n:Skill OR n:Role OR n:Course OR n:Unit OR n:EmergingTech
WITH collect(DISTINCT {
    id: n.id,
    label: coalesce(n.name, n.id),
    // most specific label wins so the viz can highlight EmergingTech
    type: CASE
        WHEN n:EmergingTech THEN 'EmergingTech'
        WHEN n:Skill THEN 'Skill'
        WHEN n:Role  THEN 'Role'
        WHEN n:Unit  THEN 'Unit'
        WHEN n:Course THEN 'Course'
        ELSE head(labels(n)) END
}) AS nodes
MATCH (a)-[r]->(b)
WITH nodes, collect(DISTINCT {
    source: a.id, target: b.id, relation: type(r)
}) AS edges
RETURN nodes, edges
"""

def fetch_graph(driver):
    """Return {'nodes': [...], 'edges': [...]} for Member 1's /graph endpoint."""
    with driver.session() as s:
        rec = s.run(GRAPH_QUERY).single()
        if rec is None:
            return {"nodes": [], "edges": []}
        return {"nodes": rec["nodes"], "edges": rec["edges"]}

def cmd_graph():
    if "--offline" in sys.argv:
        print(json.dumps(fetch_offline_graph(), indent=2))
        return
    try:
        driver = get_driver()
        print(json.dumps(fetch_graph(driver), indent=2))
        driver.close()
    except Exception as e:
        sys.stderr.write(f"[WARN] Live Neo4j failed ({e}), serving offline graph fixture...\n")
        print(json.dumps(fetch_offline_graph(), indent=2))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "test"
    {"test": cmd_test, "load": cmd_load, "graph": cmd_graph}.get(
        cmd, lambda: sys.exit(f"unknown command: {cmd} (use test|load|graph)")
    )()
