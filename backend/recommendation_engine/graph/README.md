# Knowledge Graph Module (Neo4j)

Provides Neo4j graph storage and retrieval for CurricuAlign AI.

## Architecture
- Nodes: University, Department, Course, Semester, Module, Learning Outcome, Academic Skill, Industry Skill, Technology, Category, Industry Role, Technology Trend, Recommendation.
- Relationships: `COURSE_TEACHES`, `MODULE_CONTAINS`, `SKILL_RELATED_TO`, `ROLE_REQUIRES`, `TECHNOLOGY_BELONGS_TO`, `TECHNOLOGY_PRECEDES`, `TECHNOLOGY_DEPENDS_ON`, `RECOMMENDS`.

## Files
- `graph_models.py`: Pydantic definitions for Graph Nodes and Relationships.
- `graph_queries.py`: Optimized Cypher query registry.
- `graph_repository.py`: Neo4j driver connection pooling & in-memory fallback.
- `graph_builder.py`: Ingestion pipeline for Academic & Industry entities.
- `graph_validator.py`: Graph integrity validator and orphan node detector.
- `graph_service.py`: High-level entry point service.
