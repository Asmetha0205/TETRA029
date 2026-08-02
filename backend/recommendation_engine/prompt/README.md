# Prompt Builder Module

Constructs evidence-bound prompts for Gemini LLM.

## Features
- Strict zero-hallucination rules: forbids LLM from inventing technologies or stats.
- Accepts `GapAnalysisResult` + Neo4j Evidence + Industry & Academic Knowledge Context.
- Returns JSON-only output instructions.
- Prompt Validator checks for missing variables and structural integrity.
