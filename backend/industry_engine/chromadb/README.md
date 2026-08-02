# ChromaDB Synchronization Layer (Phase 3.8.3)

The ChromaDB Synchronization Layer manages vector indexing, metadata payload validation, and similarity search queries for the `industry_technologies` collection in ChromaDB.

## Architecture

```text
Embedding Engine & Knowledge Layer
              |
              v
     +-----------------+
     |ChromaSyncService|  ← Batch & Incremental Vector Upsert
     +--------+--------+
              |
     +--------v-----------+
     | CollectionManager  |  ← Manages 'industry_technologies' Collection
     +--------+-----------+
              |
     +--------v-----------+
     |ChromaClientWrapper |  ← Native ChromaDB Client or In-Memory Fallback
     +--------+-----------+
              |
     +--------v-----------+
     | ChromaQueryService |  ← Similarity Search & Metadata Filtering
     +--------------------+
```

## Collection Specifications

- **Collection Name**: `industry_technologies`
- **Distance Metric**: Cosine distance (`hnsw:space = cosine`)
- **Document ID Format**: `vec-{technology_id}`
- **Metadata Fields**:
  - `technology_id` (str)
  - `canonical_name` (str)
  - `category` (str)
  - `demand_score` (float)
  - `industry_score` (float)
  - `frequency` (int)
  - `trend` (str)
  - `growth` (float)
  - `classification` (str)
  - `version` (str)
  - `embedding_version` (str)
  - `embedding_hash` (str)

## Usage Example

```python
from backend.industry_engine.chromadb import (
    ChromaClientWrapper,
    CollectionManager,
    ChromaSyncService,
    ChromaQueryService,
)

# 1. Initialize Wrapper & Services
client_wrapper = ChromaClientWrapper(persist_directory="data/chroma_db")
col_manager = CollectionManager(client_wrapper)
sync_service = ChromaSyncService(col_manager)
query_service = ChromaQueryService(col_manager)

# 2. Sync (Technology, Embedding) pair batch
sync_result = sync_service.sync_batch(pairs, incremental=True)
print(f"Upserted: {sync_result.inserted_count}, Skipped: {sync_result.skipped_count}")

# 3. Vector Similarity Search
results = query_service.search_by_vector(query_vector=[0.1] * 384, limit=5)
for res in results:
    print(f"Match: {res['canonical_name']} (Similarity: {res['similarity_score']})")
```
