# Industry REST API

Production-ready FastAPI endpoints for the Industry Intelligence Engine.

## Endpoint Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/industry/technologies` | List all discovered technologies. |
| `GET` | `/industry/technology/{technology_id}` | Retrieve single technology record by ID. |
| `GET` | `/industry/search` | Search technologies by keyword query. |
| `GET` | `/industry/search/similar` | Vector similarity search using natural language or vector query. |
| `GET` | `/industry/trending` | Get top trending technologies. |
| `GET` | `/industry/emerging` | Get top emerging technologies. |
| `GET` | `/industry/core` | Get top core technologies. |
| `GET` | `/industry/statistics` | Get aggregate intelligence statistics. |
| `GET` | `/industry/snapshots` | List knowledge snapshot history. |
| `GET` | `/industry/health` | Check health status across all engine components. |
| `POST` | `/industry/refresh` | Trigger end-to-end industry refresh pipeline run. |
| `POST` | `/industry/rollback` | Rollback knowledge state to a historical snapshot. |

## Quick Example

```python
from fastapi import FastAPI
from backend.industry_engine.api import router

app = FastAPI(title="CurricuAlign AI")
app.include_router(router)
```
