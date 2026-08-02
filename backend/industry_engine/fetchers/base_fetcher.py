"""
Abstract Base Fetcher for CurricuAlign AI Job Source Plugins.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
from backend.industry_engine.models.job import Job

logger = logging.getLogger("industry_engine.fetchers.base_fetcher")


class AbstractJobFetcher(ABC):
    """
    Abstract Base Class for all job fetcher plugins.
    Enforces a standard plugin contract across API fetchers, scrapers, dataset loaders, etc.
    """

    def __init__(self, source_name: str, config: Dict[str, Any]):
        """
        Initialize base properties for the job fetcher plugin.
        """
        self.source_name = source_name
        self.config = config
        self.is_initialized = False

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize resources, authenticate, prepare connections, or load configuration.
        Must set self.is_initialized = True upon clean setup.
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the job source endpoint/resource is available and operational.
        Returns True if healthy, False otherwise.
        """
        pass

    @abstractmethod
    def fetch_jobs(self, limit: int = 100) -> List[Job]:
        """
        Fetch job listings from the source up to the specified limit.
        Must handle source-specific parsing and return a list of standardized Job instances.
        """
        pass

    def validate(self, raw_job_dict: Dict[str, Any]) -> bool:
        """
        Validates raw job record dictionary before creating a Job model instance.
        Rejects records missing critical required fields: title, description, job_id.
        """
        if not isinstance(raw_job_dict, dict):
            logger.warning(f"[{self.source_name}] Validation failed: Record is not a dictionary.")
            return False

        job_id = raw_job_dict.get("job_id") or raw_job_dict.get("id")
        title = raw_job_dict.get("title")
        description = raw_job_dict.get("description") or raw_job_dict.get("details")

        if not job_id or not str(job_id).strip():
            logger.warning(f"[{self.source_name}] Validation rejected: Missing or empty 'job_id'. Record: {raw_job_dict}")
            return False

        if not title or not str(title).strip():
            logger.warning(f"[{self.source_name}] Validation rejected: Missing or empty 'title' for job_id '{job_id}'.")
            return False

        if not description or not str(description).strip():
            logger.warning(f"[{self.source_name}] Validation rejected: Missing or empty 'description' for job_id '{job_id}'.")
            return False

        return True

    @abstractmethod
    def close(self) -> None:
        """
        Safely release network connections, HTTP client sessions, or file handlers.
        """
        pass

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
