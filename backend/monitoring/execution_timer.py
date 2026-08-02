"""
Execution Timer Context Manager and Decorator.
Measures wall-clock time for blocks and functions.
"""

import time
from typing import Any, Callable, Dict, Optional


class ExecutionTimer:
    """Context manager for timing code block execution."""

    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.elapsed_seconds: float = 0.0

    def __enter__(self) -> "ExecutionTimer":
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.end_time = time.time()
        self.elapsed_seconds = round(self.end_time - self.start_time, 4)

    @classmethod
    def time_function(cls, func: Callable) -> Callable:
        """Decorator to measure function execution time."""
        def wrapper(*args, **kwargs):
            t0 = time.time()
            res = func(*args, **kwargs)
            dt = round(time.time() - t0, 4)
            return res, dt
        return wrapper
