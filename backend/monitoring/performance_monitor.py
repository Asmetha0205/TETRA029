"""
Performance Monitor.
Monitors system resources (RAM, CPU, execution times) using psutil/os.
"""

import os
from typing import Any, Dict
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from backend.monitoring.metrics import metrics_collector, PerformanceMetrics
from backend.utils.logger import get_logger

logger = get_logger("monitoring.performance")


class PerformanceMonitor:
    """System resource and benchmark performance monitor."""

    @staticmethod
    def get_memory_usage_mb() -> float:
        """Get RSS memory usage of current Python process in MB."""
        if not HAS_PSUTIL:
            return 0.0
        try:
            process = psutil.Process(os.getpid())
            mem = process.memory_info().rss / (1024 * 1024)
            return round(mem, 2)
        except Exception:
            return 0.0

    @staticmethod
    def get_cpu_percent() -> float:
        """Get CPU usage percent of current Python process."""
        if not HAS_PSUTIL:
            return 0.0
        try:
            process = psutil.Process(os.getpid())
            return round(process.cpu_percent(interval=0.1), 1)
        except Exception:
            return 0.0

    @classmethod
    def get_system_telemetry(cls) -> Dict[str, Any]:
        """Collect current system telemetry."""
        mem_mb = cls.get_memory_usage_mb()
        cpu_pct = cls.get_cpu_percent()

        metrics_collector.update_memory_usage(mem_mb)
        snapshot: PerformanceMetrics = metrics_collector.get_snapshot()

        return {
            "process": {
                "pid": os.getpid(),
                "memory_usage_mb": mem_mb,
                "cpu_percent": cpu_pct,
            },
            "performance_metrics": snapshot.model_dump(),
        }
