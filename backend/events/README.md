# Event System

The Event System provides asynchronous/decoupled pub-sub event notifications and structured logging.

## Core Events
- `PDF_UPLOADED`
- `ACADEMIC_ANALYSIS_STARTED` / `ACADEMIC_ANALYSIS_COMPLETED`
- `SEMANTIC_ANALYSIS_STARTED` / `SEMANTIC_ANALYSIS_COMPLETED`
- `RECOMMENDATION_STARTED` / `RECOMMENDATION_COMPLETED`
- `REPORT_GENERATED`
- `ANALYSIS_COMPLETED`

## Structured Logging Format
Logs tagged events like:
`[Workflow] [Analysis: xxx] ANALYSIS_COMPLETED: Analysis pipeline finished successfully.`
