nnh# Phase 3.8 — Industry Intelligence Engine Completion
## Implementation Plan

---

## 1. CURRENT STATE ASSESSMENT

### Completed Phases (DO NOT MODIFY)
| Phase | Module | Entry Point |
|-------|--------|-------------|
| 3.2 | Job Fetching | `fetchers/manager.py` → `FetcherManager` |
| 3.3 | Job Cleaning | `processing/pipeline.py` → `JobPreprocessingPipeline` |
| 3.4 | LLM Extraction | `processing/llm/technology_extractor.py` → `TechnologyExtractor` |
| 3.5 | Normalization | `processing/normalization/pipeline.py` → `NormalizationPipeline` |
| 3.6 | Frequency Analysis | `analysis/frequency/frequency_engine.py` → `FrequencyEngine` |
| 3.7 | Demand & Trend | `analysis/demand/demand_engine.py` → `DemandEngine` |

### Key Codebase Patterns (MUST FOLLOW)
- **Imports**: Absolute only — `from backend.industry_engine.X import Y`
- **Models**: Pydantic v2 `BaseModel` with `Field(...)`, `model_dump()`, `model_copy(deep=True)`
- **Engine pattern**: `__init__(config)`, `self._config`, `self.last_report`, verb-first methods
- **Logging**: Module-level `logger = logging.getLogger("industry_engine.X.Y")`, bracket-tag `[ClassName]` prefix
- **Config**: Nested Pydantic `BaseModel` configs per subsystem
- **Exceptions**: Custom hierarchy inheriting from `BaseEngineError`
- **Init files**: Explicit re-exports with `__all__` lists

### Dependencies to Install
```
sentence-transformers
chromadb
pyyaml
httpx
```
(torch is pulled in by sentence-transformers)

---

## 2. FILES TO CREATE (35 files)

### knowledge/ (8 files)
```
backend/industry_engine/knowledge/
├── __init__.py
├── knowledge_models.py      — TechnologyKnowledgeRecord, KnowledgeSnapshot, KnowledgeStats
├── knowledge_repository.py  — In-memory + JSON file persistence
├── knowledge_service.py     — Business logic facade (get, search, trending, etc.)
├── knowledge_builder.py     — Builds KnowledgeRecords from pipeline outputs
├── snapshot_manager.py      — Snapshot CRUD, comparison, rollback, growth calc
├── version_manager.py       — Version tracking per technology
└── exceptions.py            — KnowledgeError hierarchy
```

### embeddings/ (5 files)
```
backend/industry_engine/embeddings/
├── __init__.py
├── embedding_service.py     — Facade: generate, search, batch operations
├── embedding_generator.py   — SentenceTransformer model loading + encode
├── embedding_repository.py  — In-memory vector store + JSON persistence
├── embedding_manager.py     — Orchestrates generator + repository
└── embedding_cache.py       — LRU cache for repeated embeddings
```

### chromadb/ (5 files)
```
backend/industry_engine/chromadb/
├── __init__.py
├── chroma_client.py         — ChromaDB Client wrapper with lazy init
├── collection_manager.py    — Create/get/delete collections
├── index_manager.py         — Upsert/remove/query technology vectors
├── sync_service.py          — Diff-based sync: new/update/remove
└── query_service.py         — Semantic search + metadata filtering
```

### api/ (4 files)
```
backend/industry_engine/api/
├── __init__.py
├── routes.py                — FastAPI router with all endpoints
├── schemas.py               — Pydantic request/response models
├── controllers.py           — Thin logic layer between routes and services
└── services.py              — Injects IndustryService + orchestrates responses
```

### scheduler/ (3 files)
```
backend/industry_engine/scheduler/
├── __init__.py
├── refresh_pipeline.py      — Full orchestration: Fetch → Clean → Extract → Normalize → Analyze → Knowledge → Embed → ChromaDB → Snapshot
├── refresh_manager.py       — Manages refresh state, scheduling, locking
└── jobs.py                  — Job dataclass for scheduled refresh tasks
```

### Root-level
```
backend/industry_engine/requirements.txt   — Dependencies
```

### Missing __init__.py files to create
```
backend/__init__.py
backend/industry_engine/__init__.py
backend/industry_engine/models/__init__.py
```

---

## 3. DETAILED FILE RESPONSIBILITIES

### 3.1 knowledge/knowledge_models.py

```python
class TechnologyKnowledgeRecord(BaseModel):
    technology_id: str          # slugified canonical name
    canonical_name: str
    category: str
    aliases: List[str]
    demand_score: float         # 0-100
    industry_score: float       # 0-100
    trend: TrendDirection       # reuses enum from demand models
    growth: float               # percentage
    classification: TechnologyClassification  # reuses enum
    related_technologies: List[str]
    frequency: int              # total mentions
    role_coverage: Dict[str, float]  # role -> percentage
    source_list: List[str]      # data source identifiers
    first_seen: str             # ISO timestamp
    last_updated: str           # ISO timestamp
    version: int                # monotonically increasing
    embedding_id: Optional[str]
    status: str                 # "active", "deprecated", "archived"

class KnowledgeSnapshot(BaseModel):
    snapshot_id: str
    timestamp: str
    technology_count: int
    records: List[TechnologyKnowledgeRecord]
    metadata: Dict[str, Any]

class KnowledgeStats(BaseModel):
    total_technologies: int
    active_count: int
    deprecated_count: int
    categories: Dict[str, int]
    avg_demand_score: float
    avg_industry_score: float
    snapshot_count: int
```

### 3.2 knowledge/knowledge_repository.py

- `add_record(record)` / `upsert_record(record)` — Insert or update
- `get_record(technology_id)` → Optional
- `get_all_records()` → List
- `search_by_name(query)` → List  (case-insensitive substring)
- `search_by_category(category)` → List
- `get_by_classification(classification)` → List
- `get_trending(threshold)` → List  (trend == EMERGING or RAPIDLY_RISING)
- `get_emerging()` → List  (classification == EMERGING)
- `get_core()` → List  (classification == CORE)
- `remove_record(technology_id)` → bool
- `count()` → int
- `get_stats()` → KnowledgeStats
- `to_dict()` / `from_dict()` — JSON serialization
- `save(path)` / `load(path)` — File persistence
- Uses `threading.Lock` for thread safety

### 3.3 knowledge/knowledge_service.py

Business logic facade consumed by API + Refresh Pipeline:
- `get_all_technologies(category, classification, sort_by, limit, offset)` → paginated list
- `get_technology(technology_id)` → single record
- `search_technologies(query, category, limit)` → search results
- `get_trending(limit)` → trending technologies
- `get_emerging(limit)` → emerging technologies
- `get_core_technologies(limit)` → core technologies
- `get_statistics()` → KnowledgeStats
- `get_snapshots()` → list of snapshots
- `get_snapshot(snapshot_id)` → single snapshot
- `compare_snapshots(id1, id2)` → comparison diff
- `rollback_to_snapshot(snapshot_id)` → restore state
- `refresh_industry()` → triggers full pipeline (delegates to RefreshPipeline)
- `update_technology(technology_id, updates)` → partial update
- `deprecate_technology(technology_id)` → set status=deprecated

### 3.4 knowledge/knowledge_builder.py

Converts pipeline outputs into KnowledgeRecords:
- `build_from_demand_report(report: IndustryReport, freq_report: FrequencyReport)` → List[TechnologyKnowledgeRecord]
- `build_single(tech_name, demand_score, trend, frequency, ...)` → TechnologyKnowledgeRecord
- `_generate_tech_id(canonical_name)` → slugified ID
- `_compute_related(tech_name, all_techs)` → List[str]  (same-category co-occurrence)
- `_merge_role_coverage(freq_roles, demand_roles)` → Dict[str, float]

### 3.5 knowledge/snapshot_manager.py

- `create_snapshot(records)` → KnowledgeSnapshot  (generates unique snapshot_id)
- `get_snapshot(snapshot_id)` → Optional
- `list_snapshots()` → List
- `compare_snapshots(id1, id2)` → SnapshotComparison (added, removed, changed)
- `calculate_growth(current, previous)` → Dict[str, float]
- `rollback_to(snapshot_id)` → List[TechnologyKnowledgeRecord]
- `prune(max_keep)` — removes oldest beyond limit
- `save(path)` / `load(path)` — JSON persistence
- Stores `List[KnowledgeSnapshot]` internally

### 3.6 knowledge/version_manager.py

- `get_version(technology_id)` → int
- `increment(technology_id)` → int  (returns new version)
- `set_version(technology_id, version)` → None
- `get_all_versions()` → Dict[str, int]
- `has_changed(technology_id, new_data)` → bool  (compares with stored hash)

### 3.7 embeddings/embedding_generator.py

- `__init__(model_name="all-MiniLM-L6-v2")` — lazy loads model
- `_load_model()` — SentenceTransformer(model_name)
- `generate(text: str)` → List[float]
- `generate_batch(texts: List[str])` → List[List[float]]
- `get_model_info()` → Dict  (name, dimension, device)

### 3.8 embeddings/embedding_repository.py

- `store(embedding_id, vector, metadata)` → None
- `get(embedding_id)` → Optional
- `get_batch(ids)` → List
- `remove(embedding_id)` → bool
- `count()` → int
- `to_dict()` / `from_dict()` — serialization
- `save(path)` / `load(path)` — file persistence

### 3.9 embeddings/embedding_cache.py

- LRU cache with configurable max_size (default 1000)
- `get(text)` → Optional[List[float]]
- `put(text, vector)` → None
- `has(text)` → bool
- `clear()` → None
- `size()` → int
- Uses `functools.lru_cache` internally or custom OrderedDict

### 3.10 embeddings/embedding_manager.py

- `__init__(generator, repository, cache)` — dependency injection
- `embed_technology(tech_record: TechnologyKnowledgeRecord)` → str  (embedding_id)
- `embed_batch(tech_records)` → Dict[str, str]  (tech_id → embedding_id)
- `get_embedding(embedding_id)` → Optional
- `remove_embedding(embedding_id)` → bool

### 3.11 embeddings/embedding_service.py

- `__init__(generator, manager, cache)`
- `generate_embedding(text)` → List[float]
- `embed_technology(tech)` → str
- `embed_batch(techs)` → Dict
- `search_similar(text, top_k)` → List  (semantic search)
- `get_embedding(embedding_id)` → Optional

### 3.12 chromadb/chroma_client.py

- `__init__(persist_directory, collection_name)`
- `_get_or_create_client()` — `chromadb.Client(Settings(...))`
- `get_client()` → Client
- `is_available()` → bool  (try/except import)
- `reset()` → None

### 3.13 chromadb/collection_manager.py

- `create_collection(name, metadata)` → Collection
- `get_collection(name)` → Optional
- `delete_collection(name)` → bool
- `list_collections()` → List[str]
- `get_or_create(name)` → Collection

### 3.14 chromadb/index_manager.py

- `upsert(collection_name, doc_id, embedding, metadata, document)` → None
- `upsert_batch(collection_name, ids, embeddings, metadatas, documents)` → None
- `remove(collection_name, doc_id)` → bool
- `get(collection_name, doc_id)` → Optional
- `get_many(collection_name, ids)` → List
- `count(collection_name)` → int

### 3.15 chromadb/sync_service.py

- `__init__(index_manager, collection_manager)`
- `sync_technologies(records, collection_name)` → SyncResult
  - Diff current vs new (by technology_id)
  - Upsert new/changed
  - Mark removed as deprecated (or soft delete)
- `SyncResult` model: inserted, updated, removed, unchanged counts

### 3.16 chromadb/query_service.py

- `__init__(collection_manager, embedding_generator)`
- `semantic_search(query_text, collection_name, top_k, filters)` → List
- `search_by_metadata(collection_name, filters, where)` → List
- `get_similar_technologies(tech_id, collection_name, top_k)` → List

### 3.17 api/schemas.py

```python
class TechnologyResponse(BaseModel): ...
class TechnologyListResponse(BaseModel): ...
class TrendingResponse(BaseModel): ...
class EmergingResponse(BaseModel): ...
class StatisticsResponse(BaseModel): ...
class RefreshRequest(BaseModel): ...
class RefreshResponse(BaseModel): ...
class SnapshotResponse(BaseModel): ...
class SnapshotListResponse(BaseModel): ...
class SearchRequest(BaseModel): ...
class SearchResponse(BaseModel): ...
class HealthResponse(BaseModel): ...
```

### 3.18 api/routes.py

```python
router = APIRouter(prefix="/industry", tags=["Industry Intelligence"])

GET  /technologies          — list all (pagination, filters)
GET  /technology/{id}       — single technology
GET  /trending              — trending technologies
GET  /emerging              — emerging technologies
GET  /statistics            — knowledge stats
POST /refresh               — trigger refresh pipeline
GET  /snapshots             — list snapshots
GET  /snapshots/{id}        — single snapshot
POST /snapshots/{id}/rollback — rollback to snapshot
GET  /search                — semantic search
GET  /health                — health check
```

### 3.19 api/controllers.py

Thin layer between routes and services:
- `list_technologies(params)` → TechnologyListResponse
- `get_technology(tech_id)` → TechnologyResponse
- `get_trending(limit)` → TrendingResponse
- `get_emerging(limit)` → EmergingResponse
- `get_statistics()` → StatisticsResponse
- `trigger_refresh(request)` → RefreshResponse
- `list_snapshots()` → SnapshotListResponse
- `get_snapshot(snapshot_id)` → SnapshotResponse
- `rollback_snapshot(snapshot_id)` → SnapshotResponse
- `search_technologies(query, filters)` → SearchResponse

### 3.20 api/services.py

```python
class IndustryAPIService:
    def __init__(self, industry_service: IndustryKnowledgeService): ...
    # Delegates to IndustryKnowledgeService + wraps results in API schemas
```

### 3.21 scheduler/refresh_pipeline.py

```python
class RefreshPipeline:
    def execute(self) -> RefreshSummary:
        # 1. FetcherManager.fetch_all_jobs()
        # 2. JobPreprocessingPipeline.process_jobs()
        # 3. TechnologyExtractor.extract_from_clean_job() (per job)
        # 4. NormalizationPipeline.normalize()
        # 5. FrequencyEngine.process()
        # 6. DemandEngine.process()
        # 7. KnowledgeBuilder.build_from_demand_report()
        # 8. KnowledgeRepository.upsert_records()
        # 9. EmbeddingManager.embed_batch()
        # 10. ChromaDBSyncService.sync_technologies()
        # 11. SnapshotManager.create_snapshot()
        # Return RefreshSummary
```

### 3.22 scheduler/refresh_manager.py

```python
class RefreshManager:
    def __init__(pipeline, interval_seconds): ...
    def start(self) → None  # background thread
    def stop(self) → None
    def refresh_now() → RefreshSummary  # manual trigger
    def get_status() → RefreshStatus  # last refresh, next refresh, running?
```

### 3.23 scheduler/jobs.py

```python
class RefreshJob(BaseModel):
    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    started_at: Optional[str]
    completed_at: Optional[str]
    summary: Optional[RefreshSummary]
    error: Optional[str]
```

---

## 4. REFRESH PIPELINE FLOW

```
refresh_industry()
│
├─ 1. Fetch Jobs
│  └─ FetcherManager.fetch_all_jobs() → List[Job]
│
├─ 2. Clean Jobs
│  └─ JobPreprocessingPipeline.process_jobs() → List[CleanJob]
│
├─ 3. Extract Technologies (per job)
│  └─ TechnologyExtractor.extract_from_clean_job() → List[TechnologyExtraction]
│     (Gemini API call — may fail; skip failed jobs gracefully)
│
├─ 4. Normalize
│  └─ NormalizationPipeline.normalize_raw() → NormalizationResult
│     (per extraction, then merge)
│
├─ 5. Frequency Analysis
│  └─ FrequencyEngine.process() → FrequencyReport
│
├─ 6. Demand & Trend Analysis
│  └─ DemandEngine.process() → IndustryReport
│
├─ 7. Build Knowledge Records
│  └─ KnowledgeBuilder.build_from_demand_report() → List[TechnologyKnowledgeRecord]
│
├─ 8. Update Knowledge Repository
│  └─ KnowledgeRepository.upsert_records()
│
├─ 9. Generate Embeddings
│  └─ EmbeddingManager.embed_batch()
│
├─ 10. Sync ChromaDB
│  └─ ChromaDBSyncService.sync_technologies()
│
├─ 11. Create Snapshot
│  └─ SnapshotManager.create_snapshot()
│
└─ Return RefreshSummary
```

---

## 5. KNOWLEDGE LAYER LIFECYCLE

```
                    ┌──────────────┐
                    │  Refresh     │
                    │  Pipeline    │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Knowledge   │
                    │  Builder     │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐     ┌──────────────┐
                    │  Knowledge   │────►│  Version     │
                    │  Repository  │     │  Manager     │
                    └──────┬───────┘     └──────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──────┐ ┌──▼───┐ ┌─────▼──────┐
       │  Embedding  │ │ Snap │ │  ChromaDB  │
       │  Manager    │ │ Mgr  │ │  Sync      │
       └─────────────┘ └──────┘ └────────────┘
```

---

## 6. EMBEDDING LIFECYCLE

```
Text Input
    │
    ▼
┌─────────────┐    hit    ┌───────────┐
│  Embedding  │──────────►│  Return   │
│  Cache      │           │  Cached   │
└──────┬──────┘           └───────────┘
       │ miss
       ▼
┌─────────────┐
│  Sentence   │
│  Transformer│
│  (MiniLM)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Embedding  │
│  Repository │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  ChromaDB   │
│  Index      │
└─────────────┘
```

---

## 7. CHROMADB SYNCHRONIZATION FLOW

```
New Technology Records
        │
        ▼
┌───────────────┐
│  Diff Engine  │ (compare by technology_id)
└───────┬───────┘
        │
   ┌────┼────┐
   │    │    │
   ▼    ▼    ▼
 NEW  UPD  DEL
   │    │    │
   ▼    ▼    ▼
┌────────────────┐
│  Upsert Batch  │ (new + updated)
└────────────────┘
        │
        ▼
┌────────────────┐
│  Soft Delete   │ (removed → status=deprecated)
└────────────────┘
        │
        ▼
┌────────────────┐
│  Sync Result   │
│  {inserted,    │
│   updated,     │
│   removed}     │
└────────────────┘
```

---

## 8. SNAPSHOT LIFECYCLE

```
Refresh Complete
       │
       ▼
┌──────────────┐
│  Capture     │ ← all current records + metadata
│  Snapshot    │
└──────┬───────┘
       │
       ▼
┌──────────────┐    ┌──────────────┐
│  Store in    │    │  Prune old   │
│  History     │    │  (if > max)  │
└──────┬───────┘    └──────────────┘
       │
       ▼
┌──────────────┐
│  Available   │
│  for:        │
│  - Compare   │
│  - Rollback  │
│  - Growth    │
│    Calc      │
└──────────────┘
```

---

## 9. API DOCUMENTATION

### GET /industry/technologies
Query params: `category`, `classification`, `sort_by`, `limit` (default 50), `offset` (default 0)

### GET /industry/technology/{technology_id}
Path param: `technology_id` (slugified name)

### GET /industry/trending
Query params: `limit` (default 10)

### GET /industry/emerging
Query params: `limit` (default 10)

### GET /industry/statistics
No params. Returns KnowledgeStats.

### POST /industry/refresh
Body: `{ "force": false, "skip_llm": false }`
Returns RefreshSummary with execution details.

### GET /industry/snapshots
No params. Returns list of snapshots.

### GET /industry/snapshots/{snapshot_id}
Path param: `snapshot_id`

### POST /industry/snapshots/{snapshot_id}/rollback
Path param: `snapshot_id`. Restores knowledge state.

### GET /industry/search
Query params: `q` (search query), `category`, `limit` (default 10)

### GET /industry/health
No params. Returns `{ status: "healthy", version: "...", timestamp: "..." }`

---

## 10. EXAMPLE API REQUESTS & RESPONSES

### GET /industry/technologies?category=AI / ML&limit=5
```json
{
  "technologies": [
    {
      "technology_id": "pytorch",
      "canonical_name": "PyTorch",
      "category": "AI / ML",
      "demand_score": 92.5,
      "industry_score": 88.3,
      "trend": "Rising",
      "growth": 15.2,
      "classification": "Core Technology",
      "frequency": 234,
      "status": "active"
    }
  ],
  "total": 42,
  "limit": 5,
  "offset": 0
}
```

### GET /industry/trending?limit=3
```json
{
  "trending": [
    { "technology_id": "langchain", "trend": "Rapidly Rising", "growth": 67.5 },
    { "technology_id": "vllm", "trend": "Emerging", "growth": 120.0 },
    { "technology_id": "crewai", "trend": "Emerging", "growth": 95.0 }
  ]
}
```

### POST /industry/refresh
```json
// Request
{ "force": false }

// Response
{
  "status": "completed",
  "jobs_processed": 150,
  "technologies_discovered": 87,
  "new_technologies": 12,
  "updated_technologies": 75,
  "embeddings_generated": 87,
  "chromadb_updated": 87,
  "snapshot_created": true,
  "execution_time_seconds": 45.2
}
```

---

## 11. DEPLOYMENT & INDEPENDENT RUNNING

### Install Dependencies
```bash
cd "D:\CurriculAlign AI"
.venv\Scripts\pip install sentence-transformers chromadb pyyaml httpx
```

### Run as API Server
```bash
.venv\Scripts\python -m uvicorn backend.industry_engine.api.routes:app --host 0.0.0.0 --port 8000
```

### Run Refresh Pipeline Standalone
```python
from backend.industry_engine.scheduler.refresh_pipeline import RefreshPipeline
pipeline = RefreshPipeline()
summary = pipeline.execute()
print(summary)
```

### Run Knowledge Service Standalone
```python
from backend.industry_engine.knowledge.knowledge_service import IndustryKnowledgeService
service = IndustryKnowledgeService()
# service.load_from_disk()
techs = service.get_all_technologies()
stats = service.get_statistics()
```

---

## 12. IMPLEMENTATION ORDER

### Step 1: Infrastructure (no external deps)
1. `knowledge/exceptions.py`
2. `knowledge/knowledge_models.py`
3. `knowledge/version_manager.py`
4. `knowledge/knowledge_repository.py`
5. `knowledge/snapshot_manager.py`
6. `knowledge/knowledge_builder.py`
7. `knowledge/knowledge_service.py`
8. `knowledge/__init__.py`

### Step 2: Embeddings (sentence-transformers)
9. `embeddings/embedding_cache.py`
10. `embeddings/embedding_generator.py`
11. `embeddings/embedding_repository.py`
12. `embeddings/embedding_manager.py`
13. `embeddings/embedding_service.py`
14. `embeddings/__init__.py`

### Step 3: ChromaDB
15. `chromadb/chroma_client.py`
16. `chromadb/collection_manager.py`
17. `chromadb/index_manager.py`
18. `chromadb/sync_service.py`
19. `chromadb/query_service.py`
20. `chromadb/__init__.py`

### Step 4: API
21. `api/schemas.py`
22. `api/services.py`
23. `api/controllers.py`
24. `api/routes.py`
25. `api/__init__.py`

### Step 5: Scheduler
26. `scheduler/jobs.py`
27. `scheduler/refresh_pipeline.py`
28. `scheduler/refresh_manager.py`
29. `scheduler/__init__.py`

### Step 6: Wiring
30. Missing `__init__.py` files
31. `requirements.txt`
32. `backend/industry_engine/__init__.py`

### Step 7: Tests
33. `knowledge/test_knowledge_repository.py`
34. `embeddings/test_embedding_engine.py`
35. `chromadb/test_chromadb_sync.py`
36. `scheduler/test_refresh_pipeline.py`
37. `knowledge/test_knowledge_service.py`
38. `api/test_industry_api.py`

---

## 13. KEY DESIGN DECISIONS

1. **No Neo4j**: ChromaDB only for vector storage. No graph database.
2. **No Academic Engine / Semantic Engine / Recommendation Engine**: Only Industry Intelligence.
3. **Existing modules untouched**: All 6 prior phases remain as-is.
4. **Gemini LLM optional**: RefreshPipeline skips LLM extraction if API key missing or `skip_llm=True`.
5. **In-memory first, file persistence second**: All repositories support JSON file save/load but work in-memory by default.
6. **ChromaDB optional**: If chromadb not installed, sync_service degrades gracefully (logs warning, skips).
7. **Embeddings optional**: If sentence-transformers not installed, embedding_generator degrades gracefully.
8. **Thread safety**: Repositories use `threading.Lock` for concurrent access.
9. **Snapshots are immutable**: Once created, never modified. Rollback creates new state from snapshot.
