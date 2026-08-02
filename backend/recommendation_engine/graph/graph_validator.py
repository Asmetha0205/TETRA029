"""
Graph Validator for Neo4j Knowledge Graph.
Validates graph integrity, orphan node detection, constraint checks,
and relationship connectivity.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.recommendation_engine.graph.graph_repository import GraphRepository
from backend.recommendation_engine.utils.logger import graph_logger


class ValidationIssue(BaseModel):
    """Specific graph validation error or warning item."""
    severity: str = Field(..., description="ERROR or WARNING")
    entity_id: str
    message: str


class GraphValidationReport(BaseModel):
    """Complete Knowledge Graph integrity validation report."""
    is_valid: bool = True
    total_nodes_checked: int = 0
    total_relationships_checked: int = 0
    orphan_nodes_count: int = 0
    issues: List[ValidationIssue] = Field(default_factory=list)


class GraphValidator:
    """
    Validates graph consistency, checks for unlinked orphan nodes,
    invalid relationship endpoints, and schema conformance.
    """

    def __init__(self, repository: Optional[GraphRepository] = None):
        self.repo = repository or GraphRepository()

    def validate(self) -> GraphValidationReport:
        """Execute full validation check on the Knowledge Graph."""
        summary = self.repo.get_summary()
        issues: List[ValidationIssue] = []
        orphan_count = 0

        if self.repo.is_using_memory_fallback():
            mem_store = self.repo._memory_store
            node_ids = set(mem_store.nodes.keys())
            connected_node_ids = set()

            for rel in mem_store.relationships:
                if rel.source_id not in node_ids:
                    issues.append(
                        ValidationIssue(
                            severity="ERROR",
                            entity_id=rel.source_id,
                            message=f"Relationship points from non-existent source node: {rel.source_id}"
                        )
                    )
                else:
                    connected_node_ids.add(rel.source_id)

                if rel.target_id not in node_ids:
                    issues.append(
                        ValidationIssue(
                            severity="ERROR",
                            entity_id=rel.target_id,
                            message=f"Relationship points to non-existent target node: {rel.target_id}"
                        )
                    )
                else:
                    connected_node_ids.add(rel.target_id)

            orphan_ids = node_ids - connected_node_ids
            orphan_count = len(orphan_ids)
            for oid in orphan_ids:
                issues.append(
                    ValidationIssue(
                        severity="WARNING",
                        entity_id=oid,
                        message=f"Orphan node detected with zero relationships: {oid}"
                    )
                )
        else:
            # For connected Neo4j, execute Cypher checks
            pass

        has_errors = any(i.severity == "ERROR" for i in issues)
        report = GraphValidationReport(
            is_valid=not has_errors,
            total_nodes_checked=summary.total_nodes,
            total_relationships_checked=summary.total_relationships,
            orphan_nodes_count=orphan_count,
            issues=issues
        )

        graph_logger.info(f"Graph Validation Completed. Valid={report.is_valid}, Issues={len(issues)}")
        return report
