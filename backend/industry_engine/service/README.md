# Industry Service Layer

The **single public facade** for the CurricuAlign AI Industry Intelligence Engine.

## Purpose

The Industry Service Layer consolidates all underlying modules (Knowledge Layer, Embedding Engine, ChromaDB Vector Store, Refresh Pipeline, Scheduler) behind a unified, production-grade business API.

## Public Interface

External engines (Academic Engine, Semantic Engine, Recommendation Engine) and API controllers interact with the Industry Engine strictly through `IndustryService`:

```python
from backend.industry_engine.service import IndustryService

service = IndustryService()

# 1. Discovery API
techs = service.get_all_technologies()
python_tech = service.get_technology("python")

# 2. Search & Similarity
text_matches = service.search("deep learning")
similar_vecs = service.search_similar("computer vision framework", limit=5)

# 3. Trending & Core
trending = service.get_trending(limit=10)
core_techs = service.get_core(limit=10)

# 4. Refresh Pipeline
report = service.refresh_industry()

# 5. Snapshots & Rollback
loaded_count, pre_snap = service.rollback_snapshot("snapshot-000001")

# 6. Engine Health
health_status = service.health()
print(health_status.status)
```
