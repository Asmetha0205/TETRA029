# Unified API Layer

The Unified API Layer exposes RESTful HTTP endpoints for frontend integration and administrative monitoring.

## Endpoints
1. `POST /analyze-curriculum`: Single-call PDF upload and full multi-engine pipeline execution.
2. `GET /analysis/{analysis_id}`: Retrieve completed analysis result by ID.
3. `GET /report/{analysis_id}`: Retrieve executive summary report by ID.
4. `GET /dashboard`: Aggregate system dashboard analytics.
5. `GET /status`: System operational status and active workflow list.
6. `GET /health`: Comprehensive multi-subsystem health probes.
7. `GET /system/statistics`: Resource telemetry and cache statistics.

## Security Features
- Upload file validation (PDF extension, maximum size limit).
- Path traversal prevention via filename sanitization.
- Input string trimming and length limiting.
- Graceful exception handling returning structured `ApiResponse` envelope.
