# Refresh Pipeline & Background Scheduler

Orchestrates the 9-stage end-to-end data pipeline across all components of the Industry Intelligence Engine.

## Refresh Execution Flow

```text
1. Fetch Jobs (APIFetcher / DatasetFetcher)
      │
      ▼
2. Clean Jobs (JobPreprocessingPipeline)
      │
      ▼
3. Technology Extraction (TechnologyProfile)
      │
      ▼
4. Normalization (NormalizationPipeline)
      │
      ▼
5. Frequency Analysis (FrequencyEngine)
      │
      ▼
6. Demand Analysis (DemandEngine)
      │
      ▼
7. Knowledge Layer Update (KnowledgeService)
      │
      ▼
8. Embedding Generation (EmbeddingService)
      │
      ▼
9. ChromaDB Sync (ChromaSyncService) & Snapshot
```

## Features

- **Manual Refresh**: Explicit trigger via `refresh_manager.trigger_refresh()`.
- **Scheduled Refresh**: Background thread loop managed via `refresh_manager.start_scheduler()`.
- **Dry-Run Mode**: Test pipeline execution without persisting to Knowledge Layer / Embeddings.
- **Incremental Sync**: Skips unchanged records to minimize processing time.
