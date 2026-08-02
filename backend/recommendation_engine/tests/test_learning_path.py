"""
Unit Tests for Learning Path Generator Module.
"""

import unittest
from backend.recommendation_engine.learning_path.dependency_resolver import DependencyResolver
from backend.recommendation_engine.learning_path.learning_path_builder import LearningPathBuilder


class TestLearningPathModule(unittest.TestCase):

    def test_dependency_resolver_topological_sort(self):
        resolver = DependencyResolver()
        techs = ["Kubernetes", "Redis", "Docker", "Python", "FastAPI", "SQL", "Microservices"]
        resolved = resolver.resolve_dependencies(techs)

        # Verify prerequisite ordering constraints
        self.assertLess(resolved.index("Python"), resolved.index("SQL"))
        self.assertLess(resolved.index("SQL"), resolved.index("Docker"))
        self.assertLess(resolved.index("Docker"), resolved.index("Redis"))
        self.assertLess(resolved.index("Redis"), resolved.index("FastAPI"))
        self.assertLess(resolved.index("FastAPI"), resolved.index("Kubernetes"))
        self.assertLess(resolved.index("Kubernetes"), resolved.index("Microservices"))

    def test_learning_path_builder(self):
        builder = LearningPathBuilder()
        plan = builder.build_learning_path(["Docker", "Redis", "FastAPI", "Kubernetes"])
        self.assertEqual(plan.total_steps, 4)
        self.assertGreater(plan.total_estimated_hours, 0)
        self.assertEqual(plan.sequence[0], "Docker")

