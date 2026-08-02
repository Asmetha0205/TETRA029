# Analysis Orchestrator

The Analysis Orchestrator coordinates end-to-end curriculum analysis execution across all four underlying engines:

`Academic Engine -> Industry Engine -> Semantic Engine -> Recommendation Engine`

## Architecture Principles
1. **Single Entry Point**: Accepts PDF document bytes and runs full orchestration.
2. **Decoupled Gateways**: Interacts strictly through Gateway wrappers.
3. **Resilient Error Recovery**: Partial result fallbacks prevent system crashes when individual subsystems fail.
4. **Structured Tagged Logging**: Emits `[Workflow]`, `[Academic]`, `[Semantic]`, `[Recommendation]`, `[Report]` logs.
5. **Unified Analysis Result**: Produces a standardized `AnalysisResult` schema.
