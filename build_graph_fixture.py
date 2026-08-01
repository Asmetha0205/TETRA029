"""
Offline generator for the /graph JSON shape, built straight from the three JSON
files (no database needed). Produces the SAME { nodes, edges } shape that
graph_db.fetch_graph() returns from AuraDB, so Member 1 (/graph endpoint) and
Member 5 (React Flow) can build against a real fixture before Neo4j is live.

    python build_graph_fixture.py   ->  writes graph_sample.json
"""
import json
from pathlib import Path

from graph_db import EMERGING_IDS

HERE = Path(__file__).parent


def build():
    skills = json.loads((HERE / "industry_skill_base.json").read_text("utf-8"))
    roles = json.loads((HERE / "role_skill_map.json").read_text("utf-8"))
    skill_ids = {s["id"] for s in skills}

    nodes, edges = [], []

    for s in skills:
        node_type = "EmergingTech" if s["id"] in EMERGING_IDS else "Skill"
        nodes.append({"id": s["id"], "label": s["name"], "type": node_type})
    for rid in roles:
        nodes.append({"id": rid, "label": rid, "type": "Role"})

    for s in skills:
        for r in s.get("related_skills", []):
            if r in skill_ids:
                edges.append({"source": s["id"], "target": r, "relation": "RELATED_TO"})
    for rid, sids in roles.items():
        for sid in sids:
            if sid in skill_ids:
                edges.append({"source": sid, "target": rid, "relation": "REQUIRED_BY"})
            if sid in EMERGING_IDS:
                edges.append({"source": rid, "target": sid, "relation": "DEMANDS"})

    return {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    graph = build()
    out = HERE / "graph_sample.json"
    out.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    print(f"wrote {out.name}: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
