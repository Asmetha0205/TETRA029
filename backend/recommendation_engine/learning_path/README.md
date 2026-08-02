# Learning Path Generator

Generates dependency-aware technology learning paths for curriculum recommendations.

## Features
- Graph-based topological sort using `TECHNOLOGY_PRECEDES` and `TECHNOLOGY_DEPENDS_ON` relationships.
- Guarantees valid learning progressions (e.g., Python -> SQL -> Docker -> Redis -> FastAPI -> Kubernetes -> Microservices).
- Provides estimated learning hours and prerequisite tracking per step.
