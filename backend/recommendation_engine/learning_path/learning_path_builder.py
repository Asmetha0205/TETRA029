"""
Learning Path Builder for Recommendation Intelligence Layer.
High-level service interface to construct dependency-aware learning paths.
"""

from typing import List, Optional
from backend.recommendation_engine.graph.graph_repository import GraphRepository
from backend.recommendation_engine.learning_path.dependency_resolver import DependencyResolver
from backend.recommendation_engine.learning_path.path_generator import LearningPathPlan, PathGenerator


class LearningPathBuilder:
    """
    Entry point to build dependency-aware learning paths for curriculum recommendations.
    """

    def __init__(self, repository: Optional[GraphRepository] = None):
        self.resolver = DependencyResolver(repository)

    def build_learning_path(self, target_technologies: List[str]) -> LearningPathPlan:
        """
        Build dependency-aware learning path for target technologies.
        Example: ["Redis", "Docker", "Python", "Kubernetes", "FastAPI", "Microservices", "SQL"]
        Output sequence: Python -> SQL -> Docker -> Redis -> FastAPI -> Kubernetes -> Microservices
        """
        resolved_seq = self.resolver.resolve_dependencies(target_technologies)
        return PathGenerator.generate_path_plan(resolved_seq)
