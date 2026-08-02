"""
Industry Engine Fetchers Package.
Exposes Job Fetcher interfaces, implementations, factories, and managers.
"""

from backend.industry_engine.models.job import Job
from backend.industry_engine.fetchers.base_fetcher import AbstractJobFetcher
from backend.industry_engine.fetchers.api_fetcher import APIJobFetcher
from backend.industry_engine.fetchers.dataset_fetcher import DatasetJobFetcher
from backend.industry_engine.fetchers.factory import FetcherFactory
from backend.industry_engine.fetchers.manager import FetcherManager

__all__ = [
    "Job",
    "AbstractJobFetcher",
    "APIJobFetcher",
    "DatasetJobFetcher",
    "FetcherFactory",
    "FetcherManager"
]
