# CurricuAlign AI — Data & Knowledge Graph Layer (Member 3)

Everything Member 1 (alignment score) and Member 2 (semantic gap engine) need to
start is in this folder. **You are unblocked — build against these now.**

## Files you consume

| File | Owner reads | What it is |
|------|-------------|------------|
| `industry_skill_base.json` | M1 + M2 | 46 skills, all 6 NASSCOM FutureSkills domains. One array of records. |
| `skill_aliases.json` | **M1** | 164-entry normalization map `alias -> canonical skill name`. |
| `role_skill_map.json` | **M1** | 5 roles → skill IDs they demand. Weights come from `demand_score`. |
| `graph_sample.json` | M1 + M5 | Offline fixture of the exact `/graph` `{nodes, edges}` shape. |

### ⚠️ Naming note for Member 1
The alias file is **`skill_aliases.json`**, NOT `alias_map.json` (an earlier brief).
Point your loader at `skill_aliases.json`.

### Record shape (`industry_skill_base.json`)
```json
{
  "id": "skill_rag",
  "name": "Retrieval-Augmented Generation",
  "aliases": ["RAG", "retrieval augmented generation"],
  "category": "AI/ML",
  "demand_score": 0.90,
  "trend": "rising",
  "related_skills": ["skill_vectordb", "skill_llm", "skill_prompt_eng"],
  "sources": ["NASSCOM FutureSkills", "Naukri snapshot 2026"]
}
```
- **No `embedding` field** — Member 2 computes embeddings from `name`.
- Skill IDs are the single source of truth. The identical strings appear in
  `industry_skill_base.json`, `role_skill_map.json`, and the graph. Don't invent IDs.

### The demo gap (why the GenAI cluster is high + rising)
6 skills carry demand ≥ 0.85 and `trend: "rising"` and are also graph-labelled
`EmergingTech`: Generative AI, LLMs, RAG, Vector Databases, Prompt Engineering,
AI Agents. A normal CS syllabus won't cover these → this is the visible skill gap.

## Neo4j knowledge graph (Member 5 viz / `/graph` endpoint)

Node labels: `Course, Unit, Skill, Role, EmergingTech`
(Course/Unit are created by the syllabus-ingestion side; Skill/Role/EmergingTech
come from my JSON.)

Relationships:
- `(Unit)-[:COVERS]->(Skill)`   (populated by ingestion)
- `(Skill)-[:REQUIRED_BY]->(Role)`
- `(Skill)-[:RELATED_TO]->(Skill)`
- `(Role)-[:DEMANDS]->(EmergingTech)`

### Setup
```bash
pip install -r requirements.txt
cp .env.example .env      # then fill in AuraDB creds
python graph_db.py test   # HOUR ZERO: verify connectivity + one query
python graph_db.py load    # wipe + load skills/roles/edges
python graph_db.py graph   # print the /graph {nodes, edges} JSON
```

### `/graph` output shape (for M1's endpoint → M5's React Flow)
```json
{
  "nodes": [ { "id": "skill_rag", "label": "Retrieval-Augmented Generation", "type": "EmergingTech" } ],
  "edges": [ { "source": "data_scientist", "target": "skill_rag", "relation": "DEMANDS" } ]
}
```
`type` uses the most specific label (EmergingTech wins over Skill) so the viz can
highlight gap-driving nodes.

**Don't wait for AuraDB:** `graph_sample.json` already contains this exact shape
(51 nodes, 201 edges) built offline from the JSON via `build_graph_fixture.py`.
M1 can serve it as a stub and M5 can render it today. Swap to `graph_db.fetch_graph()`
once Neo4j is loaded.

Credentials load from env vars only (`NEO4J_URI/USER/PASSWORD`); nothing hardcoded.
