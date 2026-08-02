"""
System Metrics Collector.
Collects timings, counters, gauges, and historical metrics.
"""

import threading
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PerformanceMetrics(BaseModel):
    """Aggregate system performance snapshot."""
    upload_time: float = 0.0
    parsing_time: float = 0.0
    semantic_matching_time: float = 0.0
    recommendation_time: float = 0.0
    total_analysis_time: float = 0.0
    memory_usage_mb: float = 0.0
    total_analyses_run: int = 0
    successful_analyses: int = 0
    failed_analyses: int = 0


class MetricsCollector:
    """Thread-safe metrics registry."""

    def __init__(self):
        self._lock = threading.RLock()
        self._timings: Dict[str, List[float]] = {
            "upload_time": [],
            "parsing_time": [],
            "semantic_matching_time": [],
            "recommendation_time": [],
            "total_analysis_time": [],
        }
        self._total_analyses = 0
        self._successful_analyses = 0
        self._failed_analyses = 0
        self._current_memory_mb = 0.0

    def record_timing(self, metric_name: str, value_seconds: float) -> None:
        """Record execution duration for a metric."""
        with self._lock:
            if metric_name not in self._timings:
                self._timings[metric_name] = []
            self._timings[metric_name].append(value_seconds)

    def record_analysis_complete(self, success: bool = True) -> None:
        """Record analysis run outcome."""
        with self._lock:
            self._total_analyses += 1
            if success:
                self._successful_analyses += 1
            else:
                self._failed_analyses += 1

    def update_memory_usage(self, memory_mb: float) -> None:
        """Update current process memory usage gauge."""
        with self._lock:
            self._current_memory_mb = round(memory_mb, 2)

    def get_summary(self) -> PerformanceMetrics:
        """Calculate average metrics and aggregate status."""
        return self.get_snapshot()

    def get_snapshot(self) -> PerformanceMetrics:
        """Return aggregate summary metrics."""
        with self._lock:
            def avg(lst: List[float]) -> float:
                return round(sum(lst) / len(lst), 4) if lst else 0.0

            return PerformanceMetrics(
                upload_time=avg(self._timings.get("upload_time", [])),
                parsing_time=avg(self._timings.get("parsing_time", [])),
                semantic_matching_time=avg(self._timings.get("semantic_matching_time", [])),
                recommendation_time=avg(self._timings.get("recommendation_time", [])),
                total_analysis_time=avg(self._timings.get("total_analysis_time", [])),
                memory_usage_mb=self._current_memory_mb,
                total_analyses_run=self._total_analyses,
                successful_analyses=self._successful_analyses,
                failed_analyses=self._failed_analyses,
            )


# Global metrics collector instance
metrics_collector = MetricsCollector()
