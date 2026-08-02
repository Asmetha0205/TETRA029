# Embedding Engine (Phase 3.8.2)

The Embedding Engine generates, manages, caches, versions, and validates dense numerical vector representations for technology records stored in the CurricuAlign AI **Industry Knowledge Layer**.

---

## 1. Overview & Independence

The Embedding Engine operates as a self-contained, independent package. It relies **only** on the Industry Knowledge Layer for data input and has **no external dependencies** on ChromaDB, FastAPI, Neo4j, or external network databases. ChromaDB vector store synchronization will be added in Phase 3.8.3.

---

## 2. Architecture

```text
                               +-----------------------------+
                               |      EmbeddingService       |  ← Primary Business Facade
                               +--------------+--------------+
                                              |
                               +--------------v--------------+
                               |      EmbeddingManager       |  ← High-Level Orchestrator
                               +--------------+--------------+
                                              |
        +-------------------------+-----------+-----------+-------------------------+
        |                         |                       |                         |
+-------v----------+   +----------v---------+   +---------v--------+   +------------v------------+
|EmbeddingGenerator|   | EmbeddingRepository|   |  EmbeddingCache  |   | EmbeddingValidator      |
| (SentenceTrans.) |   | (JSON Persistence) |   | (LRU Cache)      |   | (Vector Sanity/Norm)    |
+------------------+   +--------------------+   +------------------+   +-------------------------+
```

---

## 3. Folder Structure

```text
backend/industry_engine/embeddings/
├── __init__.py               # Exports public domain objects with explicit __all__
├── embedding_cache.py        # Thread-safe LRU cache with hit/miss statistics
├── embedding_generator.py    # SentenceTransformers vector encoder (all-MiniLM-L6-v2)
├── embedding_manager.py      # Orchestrator for generation, caching, and updates
├── embedding_models.py       # Pydantic v2 EmbeddingRecord, EmbeddingStatus, Stats
├── embedding_repository.py   # Thread-safe storage with JSON persistence
├── embedding_service.py      # Business facade connecting Knowledge Layer & embeddings
├── embedding_validator.py    # Vector dimension, NaN/Inf, and non-zero L2 norm validation
├── exceptions.py             # Custom EmbeddingError exception hierarchy
└── README.md                 # Package documentation
```

---

## 4. Text Prompt & Embedding Strategy

### Text Prompt Construction
To generate clean semantic embeddings, the generator formats each `TechnologyKnowledgeRecord` into a standardized text prompt:

```text
Technology: PyTorch
Category: AI / ML
Aliases: pytorch, torch
Description: PyTorch is an open source machine learning framework.
Related Technologies: python, tensorflow
```

### Exclusions
The following dynamic metrics are **explicitly excluded** from the text prompt to prevent vector drift when scores update:
- Demand Score
- Trend Direction
- Growth Percentage
- Version / Timestamps / Metadata

### SHA-256 Content Hashing
Every generated embedding record stores the SHA-256 hash of its input text prompt:
$$\text{content\_hash} = \text{SHA-256}(\text{text\_content})$$
If a technology's text prompt has not changed, vector generation is **skipped** (cache hit / repository skip), achieving maximum performance.

---

## 5. Class Responsibilities

| Class | Responsibility |
|---|---|
| `EmbeddingService` | Business facade connecting `KnowledgeService` with embedding management; provides similarity search. |
| `EmbeddingManager` | High-level orchestrator for batch generation, incremental updates, and validation. |
| `EmbeddingGenerator` | Encodes text prompts into unit-normalized 384-dimensional float vectors using SentenceTransformers. |
| `EmbeddingRepository` | Thread-safe, in-memory repository implementing the Repository pattern with JSON persistence. |
| `EmbeddingCache` | Thread-safe LRU cache storing vectors by technology ID and content hash. |
| `EmbeddingValidator` | Ensures zero-NaN/Inf vectors, correct dimensions, non-zero L2 norm, and ID uniqueness. |
| `EmbeddingRecord` | Authoritative Pydantic v2 data model storing the vector, model metadata, and status. |

---

## 6. Code Example

```python
from backend.industry_engine.knowledge import KnowledgeService
from backend.industry_engine.embeddings import EmbeddingService

# 1. Initialize Knowledge & Embedding Services
knowledge_service = KnowledgeService()
embedding_service = EmbeddingService(knowledge_service=knowledge_service)

# 2. Ingest pipeline data into Knowledge Layer
knowledge_service.create_technology(
    canonical_name="PyTorch",
    category="AI / ML",
    aliases=["torch"],
    description="Open-source machine learning framework.",
)

# 3. Generate embeddings from Knowledge Layer
result = embedding_service.generate_all_from_knowledge()
print(f"Generated: {result.generated_count}, Skipped: {result.skipped_count}")

# 4. Perform Vector Cosine Similarity Search
similar = embedding_service.search_similar(query="machine learning framework", limit=5)
for record, score in similar:
    print(f"Match: {record.technology_id} (Score: {score})")

# 5. Save Embedding Repository
embedding_service.save("data/embeddings.json")
```

---

## 7. Preparation for Phase 3.8.3 (ChromaDB Sync)

The `EmbeddingService` exposes `get_all_embeddings()` and `search_similar()`. In Phase 3.8.3:
1. `ChromaSyncManager` will read `EmbeddingRecord` objects from `EmbeddingService`.
2. Vector arrays and `metadata` will be pushed directly into ChromaDB collections.
3. Content hashes will ensure ChromaDB stays synchronized incrementally with zero redundant vector re-computations.
