"""
Configuration Settings for Recommendation Intelligence Layer.
Reads environment variables with sensible defaults for Neo4j, Gemini, and engine pipelines.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class Neo4jConfig(BaseModel):
    """Neo4j Database Connection Settings."""
    uri: str = Field(default_factory=lambda: os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    user: str = Field(default_factory=lambda: os.getenv("NEO4J_USER", "neo4j"))
    password: str = Field(default_factory=lambda: os.getenv("NEO4J_PASSWORD", "password"))
    database: str = Field(default_factory=lambda: os.getenv("NEO4J_DATABASE", "neo4j"))
    max_connection_lifetime: int = 3600
    max_connection_pool_size: int = 50
    enabled: bool = Field(default_factory=lambda: os.getenv("NEO4J_ENABLED", "true").lower() == "true")


class LLMRecommendationConfig(BaseModel):
    """Google Gemini LLM Configuration Settings."""
    api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    model_name: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
    temperature: float = 0.2
    max_tokens: int = 4096
    timeout: float = 30.0
    retry_count: int = 3


class RecommendationEngineConfig(BaseModel):
    """Overall Recommendation Engine Settings."""
    neo4j: Neo4jConfig = Field(default_factory=Neo4jConfig)
    llm: LLMRecommendationConfig = Field(default_factory=LLMRecommendationConfig)
    cache_ttl_seconds: int = 3600
    enable_memory_fallback: bool = True
    default_confidence_threshold: float = 0.5


# Default singleton settings instance
config = RecommendationEngineConfig()
