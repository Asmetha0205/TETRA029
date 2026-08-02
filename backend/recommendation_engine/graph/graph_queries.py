"""
Cypher Queries Registry for Neo4j Knowledge Graph.
Contains optimized Cypher queries for node creation, relationship linking,
evidence retrieval, dependency traversal, and statistics.
"""

from typing import Dict, Any


class CypherQueries:
    """Cypher query templates for Neo4j graph operations."""

    # Schema Constraints
    CREATE_CONSTRAINTS = [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:University) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Course) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Module) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Technology) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Category) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:IndustryRole) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Recommendation) REQUIRE n.id IS UNIQUE;",
    ]

    # Node Ingestion
    MERGE_NODE = """
    MERGE (n:{label} {{id: $id}})
    SET n += $properties, n.name = $name
    RETURN n
    """

    # Relationship Linking
    MERGE_RELATIONSHIP = """
    MATCH (source {{id: $source_id}})
    MATCH (target {{id: $target_id}})
    MERGE (source)-[r:{rel_type}]->(target)
    SET r += $properties
    RETURN r
    """

    # Evidence Retrieval for Gap Technology
    GET_GAP_EVIDENCE = """
    MATCH (t:Technology)
    WHERE toLower(t.name) = toLower($tech_name) OR t.id = $tech_id
    OPTIONAL MATCH (t)-[:TECHNOLOGY_BELONGS_TO]->(c:Category)
    OPTIONAL MATCH (t)<-[:TECHNOLOGY_DEPENDS_ON|TECHNOLOGY_PRECEDES]-(dep:Technology)
    OPTIONAL MATCH (r:IndustryRole)-[:ROLE_REQUIRES]->(s:IndustrySkill)-[:SKILL_RELATED_TO]->(t)
    OPTIONAL MATCH (t)-[:HAS_TREND]->(tr:TechnologyTrend)
    RETURN t.id AS tech_id,
           t.name AS tech_name,
           coalesce(t.demand_score, 80.0) AS demand_score,
           coalesce(t.industry_score, 85.0) AS industry_score,
           coalesce(t.trend, 'Rising') AS trend,
           coalesce(t.frequency, 45) AS frequency,
           c.name AS category,
           collect(DISTINCT dep.name) AS related_technologies,
           collect(DISTINCT r.name) AS related_roles,
           collect(DISTINCT s.name) AS related_skills
    """

    # Dependency Traversal
    GET_DEPENDENCY_CHAIN = """
    MATCH p=(start:Technology)-[:TECHNOLOGY_PRECEDES*0..5]->(end:Technology)
    WHERE toLower(start.name) = toLower($tech_name) OR start.id = $tech_id
    RETURN [node IN nodes(p) | node.name] AS path
    LIMIT 10
    """

    # Academic Alignment Lookup
    GET_ACADEMIC_COURSE_MODULES = """
    MATCH (c:Course)-[:MODULE_CONTAINS]->(m:Module)
    OPTIONAL MATCH (c)-[:COURSE_TEACHES]->(s:AcademicSkill)
    RETURN c.id AS course_id,
           c.name AS course_name,
           m.id AS module_id,
           m.name AS module_name,
           collect(DISTINCT s.name) AS academic_skills
    """

    # Graph Statistics
    GET_GRAPH_STATS = """
    CALL {
        MATCH (n) RETURN count(n) AS total_nodes
    }
    CALL {
        MATCH ()-[r]->() RETURN count(r) AS total_relationships
    }
    RETURN total_nodes, total_relationships
    """

    GET_NODE_COUNTS_BY_LABEL = """
    MATCH (n)
    RETURN labels(n)[0] AS label, count(n) AS count
    """

    GET_RELATIONSHIP_COUNTS_BY_TYPE = """
    MATCH ()-[r]->()
    RETURN type(r) AS rel_type, count(r) AS count
    """

    # Node Search
    SEARCH_NODES = """
    MATCH (n)
    WHERE toLower(n.name) CONTAINS toLower($query)
    RETURN n.id AS id, labels(n)[0] AS label, n.name AS name, properties(n) AS properties
    LIMIT $limit
    """
