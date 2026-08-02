"""
Job Fetcher Factory for CurricuAlign AI.
Implements dynamic plugin creation for job fetcher implementations.
"""

import logging
from typing import Dict, Type, Any, Optional, List
from backend.industry_engine.fetchers.base_fetcher import AbstractJobFetcher
from backend.industry_engine.fetchers.api_fetcher import APIJobFetcher
from backend.industry_engine.fetchers.dataset_fetcher import DatasetJobFetcher

logger = logging.getLogger("industry_engine.fetchers.factory")


class FetcherFactory:
    """
    Factory responsible for instantiating Job Fetcher plugins dynamically.
    Supports zero-code-change plugin registration for new job data sources.
    """

    _registry: Dict[str, Type[AbstractJobFetcher]] = {
        "api": APIJobFetcher,
        "dataset": DatasetJobFetcher
    }

    @classmethod
    def register_fetcher(cls, source_type: str, fetcher_class: Type[AbstractJobFetcher]) -> None:
        """
        Dynamically registers a new job fetcher plugin class.
        """
        if not issubclass(fetcher_class, AbstractJobFetcher):
            raise TypeError(f"Fetcher class '{fetcher_class.__name__}' must inherit from AbstractJobFetcher.")
        
        cls._registry[source_type.lower()] = fetcher_class
        logger.info(f"[FetcherFactory] Registered new job fetcher plugin: '{source_type.lower()}' -> {fetcher_class.__name__}")

    @classmethod
    def create_fetcher(cls, source_type: str, config: Optional[Dict[str, Any]] = None) -> AbstractJobFetcher:
        """
        Instantiates a registered fetcher plugin by source_type string.
        """
        source_key = source_type.lower()
        if source_key not in cls._registry:
            raise KeyError(f"[FetcherFactory] Unknown fetcher plugin source_type '{source_type}'. Registered plugins: {list(cls._registry.keys())}")

        fetcher_cls = cls._registry[source_key]
        config = config or {}
        fetcher_instance = fetcher_cls(source_name=source_key, config=config)
        logger.info(f"[FetcherFactory] Created fetcher instance for source '{source_key}'.")
        return fetcher_instance

    @classmethod
    def get_registered_sources(cls) -> List[str]:
        """
        Returns list of all currently registered source identifiers.
        """
        return list(cls._registry.keys())
