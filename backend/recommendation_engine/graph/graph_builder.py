"""
Graph Builder for Recommendation Intelligence Layer.
Ingests Academic Intelligence, Industry Intelligence, and Gap Analysis results
to construct the Neo4j Knowledge Graph.
"""

from typing import Any, Dict, List, Optional
from backend.recommendation_engine.graph.graph_models import (
    GraphNode,
    GraphRelationship,
    NodeLabel,
    RelationshipType,
)
from backend.recommendation_engine.graph.graph_repository import GraphRepository
from backend.recommendation_engine.utils.helpers import generate_id
from backend.recommendation_engine.utils.logger import graph_logger


class GraphBuilder:
    """
    Populates and builds the Neo4j Knowledge Graph with Nodes and Relationships:
    - University, Department, Course, Semester, Module, LearningOutcome, AcademicSkill
    - IndustryRole, IndustrySkill, Technology, Category, TechnologyTrend, Recommendation
    - Relationships: COURSE_TEACHES, MODULE_CONTAINS, SKILL_RELATED_TO, ROLE_REQUIRES,
      TECHNOLOGY_BELONGS_TO, TECHNOLOGY_PRECEDES, TECHNOLOGY_DEPENDS_ON, RECOMMENDS
    """

    def __init__(self, repository: Optional[GraphRepository] = None):
        self.repo = repository or GraphRepository()

    def build_academic_nodes(self, academic_data: List[Dict[str, Any]]) -> int:
        """
        Build academic nodes (University, Course, Module, AcademicSkill) and links.
        """
        count = 0
        for item in academic_data:
            univ_id = generate_id("univ", item.get("university", "Default University"))
            course_id = generate_id("course", item.get("course_code", item.get("course_name", "CS101")))

            # University Node
            self.repo.create_node(
                GraphNode(
                    id=univ_id,
                    label=NodeLabel.UNIVERSITY,
                    name=item.get("university", "Default University"),
                    properties={"country": item.get("country", "Global")}
                )
            )

            # Course Node
            self.repo.create_node(
                GraphNode(
                    id=course_id,
                    label=NodeLabel.COURSE,
                    name=item.get("course_name", "Computer Science Course"),
                    properties={
                        "code": item.get("course_code", "CS101"),
                        "credits": item.get("credits", 4),
                        "level": item.get("level", "Undergraduate")
                    }
                )
            )
            count += 2

            # Modules & Skills
            for mod_idx, mod_name in enumerate(item.get("modules", [])):
                mod_id = generate_id("mod", f"{course_id}_{mod_name}_{mod_idx}")
                self.repo.create_node(
                    GraphNode(
                        id=mod_id,
                        label=NodeLabel.MODULE,
                        name=mod_name,
                        properties={"sequence": mod_idx + 1}
                    )
                )
                self.repo.create_relationship(
                    GraphRelationship(
                        source_id=course_id,
                        target_id=mod_id,
                        type=RelationshipType.MODULE_CONTAINS
                    )
                )
                count += 1

            for skill_name in item.get("skills", []):
                skill_id = generate_id("askill", skill_name)
                self.repo.create_node(
                    GraphNode(
                        id=skill_id,
                        label=NodeLabel.ACADEMIC_SKILL,
                        name=skill_name
                    )
                )
                self.repo.create_relationship(
                    GraphRelationship(
                        source_id=course_id,
                        target_id=skill_id,
                        type=RelationshipType.COURSE_TEACHES
                    )
                )
                count += 1

        graph_logger.info(f"Built {count} Academic nodes and relationships")
        return count

    def build_industry_nodes(self, industry_techs: List[Dict[str, Any]], industry_roles: Optional[List[Dict[str, Any]]] = None) -> int:
        """
        Build industry nodes (Technology, Category, IndustryRole, TechnologyTrend) and relationships.
        """
        count = 0
        tech_nodes_map: Dict[str, str] = {}

        for tech in industry_techs:
            tech_name = tech.get("name", tech.get("technology", "Unknown"))
            tech_id = generate_id("tech", tech_name)
            tech_nodes_map[tech_name.lower()] = tech_id

            cat_name = tech.get("category", "General")
            cat_id = generate_id("cat", cat_name)

            # Category Node
            self.repo.create_node(
                GraphNode(
                    id=cat_id,
                    label=NodeLabel.CATEGORY,
                    name=cat_name
                )
            )

            # Technology Node
            self.repo.create_node(
                GraphNode(
                    id=tech_id,
                    label=NodeLabel.TECHNOLOGY,
                    name=tech_name,
                    properties={
                        "demand_score": tech.get("demand_score", 80.0),
                        "industry_score": tech.get("industry_score", 85.0),
                        "trend": tech.get("trend", "Rising"),
                        "frequency": tech.get("frequency", 50)
                    }
                )
            )

            # Rel: BELONGS_TO
            self.repo.create_relationship(
                GraphRelationship(
                    source_id=tech_id,
                    target_id=cat_id,
                    type=RelationshipType.TECHNOLOGY_BELONGS_TO
                )
            )
            count += 2

        # Wire prerequisites & dependencies if present in data
        for tech in industry_techs:
            tech_name = tech.get("name", tech.get("technology", ""))
            tech_id = tech_nodes_map.get(tech_name.lower())
            if not tech_id:
                continue

            for prereq in tech.get("prerequisites", []):
                prereq_id = tech_nodes_map.get(prereq.lower())
                if prereq_id and prereq_id != tech_id:
                    # prereq PRECEDES tech_id
                    self.repo.create_relationship(
                        GraphRelationship(
                            source_id=prereq_id,
                            target_id=tech_id,
                            type=RelationshipType.TECHNOLOGY_PRECEDES
                        )
                    )
                    # tech_id DEPENDS_ON prereq
                    self.repo.create_relationship(
                        GraphRelationship(
                            source_id=tech_id,
                            target_id=prereq_id,
                            type=RelationshipType.TECHNOLOGY_DEPENDS_ON
                        )
                    )
                    count += 2

        # Process Roles if provided
        if industry_roles:
            for role in industry_roles:
                role_name = role.get("role_name", role.get("title", "Software Engineer"))
                role_id = generate_id("role", role_name)

                self.repo.create_node(
                    GraphNode(
                        id=role_id,
                        label=NodeLabel.INDUSTRY_ROLE,
                        name=role_name,
                        properties={"seniority": role.get("seniority", "Mid")}
                    )
                )

                for req_tech in role.get("required_technologies", []):
                    tech_id = tech_nodes_map.get(req_tech.lower())
                    if tech_id:
                        self.repo.create_relationship(
                            GraphRelationship(
                                source_id=role_id,
                                target_id=tech_id,
                                type=RelationshipType.ROLE_REQUIRES
                            )
                        )
                count += 1

        graph_logger.info(f"Built {count} Industry nodes and relationships")
        return count

    def build_seed_graph(self):
        """Build initial rich default dataset into graph for offline/demo operation."""
        sample_academic = [
            {
                "university": "MIT",
                "course_name": "Distributed Systems & Cloud Computing",
                "course_code": "CS-6033",
                "credits": 4,
                "modules": ["Concurrency Basics", "Network Protocols", "Microservices Concepts"],
                "skills": ["Java", "Multithreading", "REST APIs", "SQL"]
            },
            {
                "university": "Stanford",
                "course_name": "Full Stack Web Development",
                "course_code": "CS-142",
                "credits": 3,
                "modules": ["HTML/CSS Foundations", "JavaScript Core", "Database Design"],
                "skills": ["JavaScript", "HTML", "CSS", "SQL", "Git"]
            }
        ]

        sample_industry_techs = [
            {"name": "Python", "category": "Programming Languages", "demand_score": 95, "industry_score": 98, "trend": "Rising", "frequency": 120, "prerequisites": []},
            {"name": "SQL", "category": "Databases", "demand_score": 90, "industry_score": 92, "trend": "Stable", "frequency": 110, "prerequisites": ["Python"]},
            {"name": "Docker", "category": "DevOps & Cloud", "demand_score": 88, "industry_score": 90, "trend": "Rising", "frequency": 95, "prerequisites": ["SQL"]},
            {"name": "Redis", "category": "Databases & Caching", "demand_score": 85, "industry_score": 91, "trend": "Rising", "frequency": 80, "prerequisites": ["Docker"]},
            {"name": "FastAPI", "category": "Web Frameworks", "demand_score": 82, "industry_score": 89, "trend": "Rapidly Growing", "frequency": 75, "prerequisites": ["Python", "Redis"]},
            {"name": "Kubernetes", "category": "DevOps & Cloud", "demand_score": 89, "industry_score": 93, "trend": "Rising", "frequency": 90, "prerequisites": ["Docker", "FastAPI"]},
            {"name": "Microservices", "category": "Architecture", "demand_score": 86, "industry_score": 88, "trend": "Stable", "frequency": 85, "prerequisites": ["Kubernetes"]},
            {"name": "Kafka", "category": "Message Queue", "demand_score": 84, "industry_score": 87, "trend": "Rising", "frequency": 70, "prerequisites": ["Docker"]},
            {"name": "GraphQL", "category": "APIs", "demand_score": 78, "industry_score": 80, "trend": "Stable", "frequency": 55, "prerequisites": ["FastAPI"]},
        ]

        sample_roles = [
            {"role_name": "Senior Backend Engineer", "required_technologies": ["Python", "SQL", "Docker", "Redis", "FastAPI", "Kubernetes", "Microservices"]},
            {"role_name": "DevOps & Cloud Specialist", "required_technologies": ["Docker", "Kubernetes", "Python", "Kafka"]},
        ]

        self.build_academic_nodes(sample_academic)
        self.build_industry_nodes(sample_industry_techs, sample_roles)
        graph_logger.info("Seed Graph population completed successfully.")
