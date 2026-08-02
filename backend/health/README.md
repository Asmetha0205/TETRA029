# Health Monitoring

The Health Monitoring subsystem probes and reports operational statuses for all engines and components.

## Probed Components
1. **Academic Engine**: PDF upload, parser, and knowledge store.
2. **Industry Engine**: Knowledge layer, embeddings, and job market records.
3. **Semantic Engine**: Matcher, classifier, priority, and report generation.
4. **Recommendation Engine**: LLM pipeline and learning path builder.
5. **Neo4j DB**: Graph database connectivity.
6. **ChromaDB**: Vector search index persistence.
7. **Gemini API**: LLM service key and connectivity.
8. **Repository Access**: Local filesystem read/write privileges.
9. **Overall Backend Health**: Consolidated state (`healthy`, `degraded`, `unhealthy`).
