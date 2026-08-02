"""
Prompt Builder for Academic Technology Extraction.

Constructs strict JSON extraction prompts for Gemini API.
Instructs the model to extract ONLY explicitly mentioned technologies in university text.
"""

import logging

logger = logging.getLogger("academic_engine.extraction.prompt_builder")


class ExtractionPromptBuilder:
    """Builds prompt templates for LLM academic technology extraction."""

    SYSTEM_INSTRUCTION = (
        "You are an expert Academic Curriculum Technology Extractor. "
        "Your sole task is to analyze university course syllabus text and extract ONLY explicitly "
        "mentioned technologies, programming languages, frameworks, libraries, databases, cloud, "
        "devops, AI tools, mathematics, core CS subjects, and developer tools. "
        "STRICT RULES:\n"
        "1. Extract ONLY technologies explicitly present in the text.\n"
        "2. Do NOT invent, assume, infer, or hallucinate technologies.\n"
        "3. Do NOT make recommendations.\n"
        "4. Return STRICT JSON containing category keys."
    )

    @classmethod
    def build_prompt(cls, text: str) -> str:
        """
        Build extraction prompt for input text snippet.
        """
        return f"""Analyze the following university curriculum syllabus text:

--- CURRICULUM TEXT BEGIN ---
{text[:4000]}
--- CURRICULUM TEXT END ---

Extract all explicitly mentioned technology entities into the following exact JSON format:

```json
{{
  "programming_languages": ["Python", "C++"],
  "frameworks": ["Django", "FastAPI"],
  "libraries": ["PyTorch", "NumPy"],
  "databases": ["PostgreSQL", "Redis"],
  "cloud": ["AWS"],
  "devops": ["Docker", "Kubernetes"],
  "ai_technologies": ["Machine Learning", "Deep Learning"],
  "mathematics": ["Linear Algebra", "Calculus"],
  "core_computer_science": ["Data Structures", "Algorithms", "Operating Systems"],
  "developer_tools": ["Git", "VS Code"]
}}
```

Return ONLY the raw JSON object. Do not include markdown code block backticks if possible.
"""
