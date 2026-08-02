# Recommendation Intelligence Layer (Phase 6)

The Recommendation Intelligence Layer transforms `GapAnalysisResult` from the Semantic Engine into explainable, evidence-backed curriculum recommendations.

## Submodules
- `graph/`: Neo4j Knowledge Graph builder, Cypher query registry, and graph repository.
- `retrieval/`: targeted Evidence Retrieval Engine.
- `prompt/`: Grounded, zero-hallucination Prompt Builder.
- `llm/`: Google Gemini LLM API client, response parser, and grounding validator.
- `recommendation/`: Recommendation object builder and models.
- `learning_path/`: Dependency resolver and topological sort path generator.
- `report/`: Executive report builder and JSON/Markdown/PDF exporters.
- `service/`: Master orchestration service.
- `api/`: FastAPI REST endpoints and controllers.
- `config/`: System configuration.
- `utils/`: Structured logging and shared helper functions.
