# Industry Knowledge Layer

The Industry Knowledge Layer serves as the **single source of truth** for every discovered technology within the CurricuAlign AI system.

## 1. Purpose

The Knowledge Layer consolidates, normalizes, versions, and persists industry technology data produced by preceding pipeline stages (Normalization, Frequency Analysis, and Demand & Trend Intelligence). It guarantees deterministic record construction, semantic versioning, point-in-time snapshotting, and non-destructive rollback capabilities for curriculum alignment downstream.

---

## 2. Architecture

```text
                               +-----------------------------+
                               |     KnowledgeService        |  ← Business Facade (APIs / Controllers)
                               +--------------+--------------+
                                              |
        +-------------------------+-----------+-----------+-------------------------+
        |                         |                       |                         |
+-------v----------+   +----------v---------+   +---------v--------+   +------------v------------+
| KnowledgeBuilder |   | KnowledgeRepo      |   | SnapshotManager  |   |     VersionManager      |
| (Fuses Pipeline) |   | (Storage / Search) |   | (Snapshots/Diff) |   | (SemVer/Content Hashes) |
+------------------+   +--------------------+   +------------------+   +-------------------------+
```

---

## 3. Folder Structure

```text
backend/industry_engine/knowledge/
├── __init__.py               # Exports public domain objects with explicit __all__
├── exceptions.py             # Domain exception hierarchy (KnowledgeError base)
├── knowledge_builder.py      # Deterministic transformation of pipeline outputs
├── knowledge_models.py       # Pydantic v2 data models, enums, & VersionInfo
├── knowledge_repository.py   # Thread-safe in-memory storage + JSON persistence
├── knowledge_service.py      # Business facade for controllers & API endpoints
├── snapshot_manager.py       # Immutable point-in-time state capture & diffs
├── version_manager.py        # Semantic versioning (major.minor.patch) & content hashing
└── README.md                 # Package documentation
```

---

## 4. Data Flow

1. **Pipeline Outputs**: Raw extractions are normalized by `NormalizationEngine`, counted by `FrequencyEngine`, and scored by `DemandEngine`.
2. **Deterministic Record Building**: `KnowledgeBuilder` receives `NormalizationResult`, `FrequencyReport`, and `IndustryReport`, merging them into canonical `TechnologyKnowledgeRecord` objects.
3. **Repository Persistence**: `KnowledgeRepository` stores records, updating content hashes and incrementing semantic versions via `VersionManager`.
4. **Snapshot Capture**: `SnapshotManager` captures immutable snapshots of repository state with audit metadata.
5. **Downstream Integration**: The Embedding Engine and Vector Store (ChromaDB) query `KnowledgeService` for clean, versioned technology records.

---

## 5. Class Responsibilities

| Class | Responsibility |
|---|---|
| `KnowledgeService` | Primary business layer interface for creating, updating, searching, snapshotting, and rolling back technology records. |
| `KnowledgeBuilder` | Deterministic fusion engine converting pipeline stage outputs (`NormalizationResult`, `FrequencyReport`, `IndustryReport`) into canonical `TechnologyKnowledgeRecord` objects. |
| `KnowledgeRepository` | Thread-safe, in-memory repository implementing the Repository pattern with JSON persistence. |
| `SnapshotManager` | Manages immutable point-in-time snapshots, diff-based comparisons (`compare_snapshots`), and state restoration. |
| `VersionManager` | Tracks semantic versions (Major.Minor.Patch) and SHA-256 content hashes per technology record. |
| `TechnologyKnowledgeRecord` | Canonical Pydantic v2 model representing technology intelligence (scores, trends, roles, version, status). |

---

## 6. Example Usage

```python
from backend.industry_engine.knowledge import KnowledgeService

# Initialize service
service = KnowledgeService(
    repository_path="data/knowledge_repo.json",
    snapshot_path="data/knowledge_snapshots.json",
)

# 1. Ingest pipeline outputs
created, updated, snapshot = service.ingest_pipeline_outputs(
    normalized_techs=normalization_result,
    frequency_data=frequency_report,
    demand_data=industry_report,
    source="pipeline_run_001",
)

# 2. Search & Filter
python_record = service.get_technology("python")
ai_techs = service.filter_by_category("AI / ML")
trending_techs = service.get_trending(limit=10)

# 3. Create Snapshot
snap_1 = service.create_snapshot(description="Initial baseline snapshot")

# 4. Compare Snapshots
diff = service.compare_snapshots(snap_1.metadata.snapshot_id, "snapshot-000002")
print(f"Added: {diff.added}, Changed: {len(diff.changed)}")

# 5. Rollback State (Preserves history)
loaded_count, pre_snap = service.rollback_snapshot(snap_1.metadata.snapshot_id)

# 6. Statistics
stats = service.get_statistics()
print(f"Total: {stats.total_technologies}, Avg Industry Score: {stats.avg_industry_score}")
```

---

## 7. Lifecycle Specifications

### Snapshot Lifecycle
1. **Creation**: `create_snapshot()` captures a deep copy of active repository records with incremental versioning (`snapshot-000001`, `snapshot-000002`).
2. **Superseding**: Marking new snapshots sets previous active snapshots to `superseded`.
3. **Comparison**: `compare_snapshots(id_a, id_b)` calculates set differences (added, removed, changed fields).
4. **Rollback**: `rollback_snapshot(snapshot_id)` replaces current repository records with snapshot data while taking a pre-rollback snapshot, ensuring full audit trail preservation.

### Version Lifecycle
1. **Initial Record**: Created with semantic version `1.0.0`.
2. **Updates**: Increments patch version (`1.0.1`, `1.0.2`).
3. **Major/Minor Bumps**: Triggered on major schema or model revisions.
4. **Content Hashing**: SHA-256 hash checks ensure version increments occur only on actual data mutations.

### Repository Pattern
The `KnowledgeRepository` decouples business logic from storage mechanisms. It provides an in-memory thread-safe (`threading.RLock`) store with JSON serialization, making it straightforward to swap in PostgreSQL/SQLAlchemy without altering `KnowledgeService`.

---

## 8. Integration Architecture

```text
+-----------------------+     +--------------------------+     +-------------------------+
| Industry Engine       |     | Industry Knowledge Layer |     | Embedding Engine        |
| (Pipeline 3.1 - 3.7)  | --> | (Phase 3.8 Facade)       | --> | (Phase 3.8.2 Vectorizer)|
+-----------------------+     +------------+-------------+     +------------+------------+
                                           |                                |
                                           v                                v
                              +--------------------------+     +-------------------------+
                              | Knowledge Persistence    |     | ChromaDB Vector Store   |
                              | (JSON / DB Repository)   |     | (Semantic Search Index) |
                              +--------------------------+     +-------------------------+
```

- **Industry Engine**: Feeds normalized extractions, frequencies, and demand scores into `KnowledgeService.ingest_pipeline_outputs()`.
- **Embedding Engine**: Fetches canonical `TechnologyKnowledgeRecord` objects from `KnowledgeService.get_all()` to generate text embeddings.
- **ChromaDB**: Stores vector embeddings paired with `technology_id` metadata for fast similarity search.
- **Semantic Engine**: Queries `KnowledgeService` alongside ChromaDB vector search to compare academic curriculum topics against validated industry demand scores.
