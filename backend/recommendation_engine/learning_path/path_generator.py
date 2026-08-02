"""
Path Generator for Learning Path Module.
Formats topologically sorted technology lists into detailed progression steps.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class LearningPathStep(BaseModel):
    """Step node in a learning path progression."""
    step_number: int
    technology: str
    stage: str = Field(default="Foundational", description="Foundational, Intermediate, Advanced")
    estimated_hours: int = 20
    description: str = ""
    prerequisites: List[str] = Field(default_factory=list)


class LearningPathPlan(BaseModel):
    """Complete Learning Path plan container."""
    title: str = "Curriculum Gap Learning Path"
    total_steps: int = 0
    total_estimated_hours: int = 0
    sequence: List[str] = Field(default_factory=list)
    steps: List[LearningPathStep] = Field(default_factory=list)


class PathGenerator:
    """
    Generates detailed learning path plans from resolved dependency sequences.
    """

    STAGE_HOURS = {
        1: (15, "Foundational"),
        2: (20, "Intermediate"),
        3: (25, "Intermediate"),
        4: (30, "Advanced"),
        5: (35, "Advanced System Design"),
    }

    @classmethod
    def generate_path_plan(cls, resolved_sequence: List[str]) -> LearningPathPlan:
        """
        Build LearningPathPlan object.
        """
        steps: List[LearningPathStep] = []
        total_hours = 0

        for idx, tech in enumerate(resolved_sequence, start=1):
            hours, stage = cls.STAGE_HOURS.get(idx, (30, "Advanced Mastery"))
            total_hours += hours

            prereqs = resolved_sequence[:idx-1]

            steps.append(
                LearningPathStep(
                    step_number=idx,
                    technology=tech,
                    stage=stage,
                    estimated_hours=hours,
                    description=f"Master {tech} concepts, practical labs, and integration patterns.",
                    prerequisites=prereqs
                )
            )

        return LearningPathPlan(
            title=f"Curriculum Gap Learning Progression ({len(resolved_sequence)} Technologies)",
            total_steps=len(steps),
            total_estimated_hours=total_hours,
            sequence=resolved_sequence,
            steps=steps
        )
