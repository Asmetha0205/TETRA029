# Recommendation Service Module

Primary service orchestrator layer for Phase 6.

## Methods
- `generate_recommendations(request)`: End-to-end pipeline execution from `GapAnalysisResult` to full recommendations.
- `get_recommendation(id_or_tech)`: Fetch single recommendation item.
- `get_learning_path(target_technologies)`: Graph-resolved dependency path.
- `get_evidence(gap_technologies)`: Evidence metrics for specified gaps.
- `export_report(request)`: Multi-format report exporter (JSON, Markdown, PDF/HTML).
