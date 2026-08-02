# Recommendation Builder Module

Formats, enriches, and validates final curriculum recommendations.

## Features
- Complete output model matching Phase 6 specification.
- Includes `technology`, `priority`, `industry_score`, `trend`, `reason`, `recommended_course`, `recommended_module`, `learning_outcomes`, `lab`, `mini_project`, `learning_path`, `references`, `confidence`.
- Dynamic confidence scoring combining industry score and evidence counts.
- Strict Pydantic schema validation.
