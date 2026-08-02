"""
API Dependency Injection Providers.
"""

from typing import Generator
from backend.orchestrator.analysis_orchestrator import AnalysisOrchestrator
from backend.health.health_service import HealthService
from backend.cache.cache_service import CacheService
from backend.events.event_bus import event_bus, EventBus
from backend.monitoring.performance_monitor import PerformanceMonitor

# Singleton instances
_orchestrator_instance = AnalysisOrchestrator()
_health_service_instance = HealthService()
_cache_service_instance = CacheService()


def get_orchestrator() -> AnalysisOrchestrator:
    """Dependency provider for AnalysisOrchestrator."""
    return _orchestrator_instance


def get_health_service() -> HealthService:
    """Dependency provider for HealthService."""
    return _health_service_instance


def get_cache_service() -> CacheService:
    """Dependency provider for CacheService."""
    return _cache_service_instance


def get_event_bus() -> EventBus:
    """Dependency provider for EventBus."""
    return event_bus


def get_performance_monitor() -> PerformanceMonitor:
    """Dependency provider for PerformanceMonitor."""
    return PerformanceMonitor()
