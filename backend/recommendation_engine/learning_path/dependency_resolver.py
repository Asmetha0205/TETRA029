"""
Dependency Resolver for Learning Path Generator.
Performs Directed Acyclic Graph (DAG) topological sorting and graph dependency resolution
using graph relationships (TECHNOLOGY_PRECEDES / TECHNOLOGY_DEPENDS_ON).
"""

from collections import defaultdict, deque
from typing import Dict, List, Optional, Set
from backend.recommendation_engine.graph.graph_repository import GraphRepository
from backend.recommendation_engine.utils.logger import recommendation_logger_tagged


class DependencyResolver:
    """
    Graph-based dependency resolver for technology prerequisites.
    Uses topological sort (Kahn's algorithm) to guarantee valid learning progressions.
    """

    # Static default fallback prerequisite map if graph has missing explicit links
    DEFAULT_PREREQUISITES = {
        "sql": ["python"],
        "docker": ["sql"],
        "redis": ["docker"],
        "fastapi": ["python", "redis"],
        "kubernetes": ["docker", "fastapi"],
        "microservices": ["kubernetes"],
        "kafka": ["docker"],
        "graphql": ["fastapi"],
    }

    def __init__(self, repository: Optional[GraphRepository] = None):
        self.repo = repository or GraphRepository()

    def resolve_dependencies(self, technologies: List[str]) -> List[str]:
        """
        Perform topological sort on list of requested target technologies.
        """
        tech_set = {t.strip() for t in technologies if t.strip()}
        if not tech_set:
            return []

        tech_map = {t.lower(): t for t in tech_set}

        # Build adjacency graph & in-degree counters
        in_degree: Dict[str, int] = defaultdict(int)
        adj_list: Dict[str, List[str]] = defaultdict(list)

        for t_lower in tech_map:
            in_degree[t_lower] = 0

        # Extract dependencies from graph or static fallback map
        for t_lower, orig_name in tech_map.items():
            prereqs = self._get_prerequisites_for_tech(orig_name)
            for p in prereqs:
                p_lower = p.lower()
                if p_lower in tech_map:
                    # p_lower PRECEDES t_lower
                    adj_list[p_lower].append(t_lower)
                    in_degree[t_lower] += 1

        # Topological Sort (Kahn's Algorithm)
        queue = deque([node for node in tech_map if in_degree[node] == 0])
        sorted_order: List[str] = []

        while queue:
            curr = queue.popleft()
            sorted_order.append(tech_map[curr])

            for neighbor in adj_list[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Append any remaining nodes if cycles existed
        if len(sorted_order) < len(tech_map):
            for t_lower, orig_name in tech_map.items():
                if orig_name not in sorted_order:
                    sorted_order.append(orig_name)

        recommendation_logger_tagged.info(f"Resolved Learning Path Dependency Sequence: {' -> '.join(sorted_order)}")
        return sorted_order

    def _get_prerequisites_for_tech(self, tech_name: str) -> List[str]:
        """Fetch prerequisites for technology."""
        if not self.repo.is_using_memory_fallback():
            try:
                query = """
                MATCH (t:Technology)-[:TECHNOLOGY_DEPENDS_ON]->(p:Technology)
                WHERE toLower(t.name) = toLower($tech_name)
                RETURN p.name AS prereq
                """
                with self.repo._driver.session(database=self.repo._cfg.database) as session:
                    records = session.run(query, {"tech_name": tech_name})
                    prereqs = [rec["prereq"] for rec in records if rec["prereq"]]
                    if prereqs:
                        return prereqs
            except Exception:
                pass

        # Fallback memory store lookup
        mem_store = self.repo._memory_store
        t_node = None
        for n in mem_store.nodes.values():
            if n.name.lower() == tech_name.lower():
                t_node = n
                break

        if t_node:
            prereqs = []
            for r in mem_store.relationships:
                if r.source_id == t_node.id and r.type.value in ["TECHNOLOGY_DEPENDS_ON"]:
                    target = mem_store.nodes.get(r.target_id)
                    if target:
                        prereqs.append(target.name)
                elif r.target_id == t_node.id and r.type.value in ["TECHNOLOGY_PRECEDES"]:
                    source = mem_store.nodes.get(r.source_id)
                    if source:
                        prereqs.append(source.name)
            if prereqs:
                return prereqs

        # Fallback default map
        return self.DEFAULT_PREREQUISITES.get(tech_name.lower(), [])
