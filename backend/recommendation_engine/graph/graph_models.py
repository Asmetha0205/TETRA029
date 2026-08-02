"""
Knowledge Graph Domain Models for Neo4j Graph.
Defines Node types, Relationship types, and property schemas.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NodeLabel(str, Enum):
    """Neo4j Node Labels for CurricuAlign AI Knowledge Graph."""
    UNIVERSITY = "University"
    DEPARTMENT = "Department"
    COURSE = "Course"
    SEMESTER = "Semester"
    MODULE = "Module"
    LEARNING_OUTCOME = "LearningOutcome"
    ACADEMIC_SKILL = "AcademicSkill"
    INDUSTRY_SKILL = "IndustrySkill"
    TECHNOLOGY = "Technology"
    CATEGORY = "Category"
    INDUSTRY_ROLE = "IndustryRole"
    TECHNOLOGY_TREND = "TechnologyTrend"
    RECOMMENDATION = "Recommendation"


class RelationshipType(str, Enum):
    """Neo4j Relationship Types for CurricuAlign AI Knowledge Graph."""
    COURSE_TEACHES = "COURSE_TEACHES"
    MODULE_CONTAINS = "MODULE_CONTAINS"
    SKILL_RELATED_TO = "SKILL_RELATED_TO"
    ROLE_REQUIRES = "ROLE_REQUIRES"
    TECHNOLOGY_BELONGS_TO = "TECHNOLOGY_BELONGS_TO"
    TECHNOLOGY_PRECEDES = "TECHNOLOGY_PRECEDES"
    TECHNOLOGY_DEPENDS_ON = "TECHNOLOGY_DEPENDS_ON"
    RECOMMENDS = "RECOMMENDS"
    HAS_DEPARTMENT = "HAS_DEPARTMENT"
    OFFERS_COURSE = "OFFERS_COURSE"
    HAS_SEMESTER = "HAS_SEMESTER"


class GraphNode(BaseModel):
    """Generic Neo4j Node Representation."""
    id: str = Field(..., description="Unique node identifier")
    label: NodeLabel = Field(..., description="Primary node label")
    name: str = Field(..., description="Display name of the node")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node key-value attributes")


class GraphRelationship(BaseModel):
    """Generic Neo4j Relationship Representation."""
    id: Optional[str] = Field(default=None, description="Optional relationship ID")
    source_id: str = Field(..., description="Source node ID")
    target_id: str = Field(..., description="Target node ID")
    type: RelationshipType = Field(..., description="Relationship type")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Edge key-value attributes")


class KnowledgeGraphSummary(BaseModel):
    """Summary metrics of the Neo4j Knowledge Graph."""
    total_nodes: int = 0
    total_relationships: int = 0
    node_counts_by_label: Dict[str, int] = Field(default_factory=dict)
    relationship_counts_by_type: Dict[str, int] = Field(default_factory=dict)
    status: str = "Connected"
