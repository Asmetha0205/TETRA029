"""
Example usage for CurricuAlign AI Technology Normalization Engine (Phase 3.5).

Demonstrates the full normalization flow with the canonical example from the
phase specification and prints the resulting output format + report.
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from backend.industry_engine.processing.normalization.pipeline import NormalizationPipeline


def main() -> None:
    # Raw LLM-extracted technology profile (Phase 3.4 output)
    example_input = {
        "languages": ["Python", "py"],
        "frameworks": ["FastAPI", "fast api"],
        "databases": ["Redis", "redis cache"],
        "ai": ["LLMs", "Gen AI", "LangChain"],
    }

    pipeline = NormalizationPipeline()

    result = pipeline.normalize_raw(example_input, job_id="job_example_001")

    print("=" * 60)
    print("INPUT PROFILE")
    print("=" * 60)
    print(json.dumps(example_input, indent=2))

    print("\n" + "=" * 60)
    print("NORMALIZED OUTPUT")
    print("=" * 60)
    print(json.dumps(result.to_dict(), indent=2))

    print("\n" + "=" * 60)
    print("NORMALIZATION REPORT")
    print("=" * 60)
    print(json.dumps(result.report.to_dict(), indent=2))


if __name__ == "__main__":
    main()
