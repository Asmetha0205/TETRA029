"""
Structured Logger for Recommendation Intelligence Layer.
Provides consistent logger instances formatted with domain prefixes:
[Graph], [Retriever], [Prompt], [LLM], [Report], [Recommendation].
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "recommendation_engine", level: int = logging.INFO) -> logging.Logger:
    """
    Setup and return a structured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Default logger for the recommendation engine
recommendation_logger = setup_logger("recommendation_engine")


class DomainLogger:
    """Helper logger wrapper that automatically prepends domain tags to log messages."""

    def __init__(self, tag: str, base_logger: Optional[logging.Logger] = None):
        self.tag = tag if tag.startswith("[") and tag.endswith("]") else f"[{tag}]"
        self._logger = base_logger or recommendation_logger

    def info(self, msg: str, *args, **kwargs):
        self._logger.info(f"{self.tag} {msg}", *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self._logger.warning(f"{self.tag} {msg}", *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self._logger.error(f"{self.tag} {msg}", *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs):
        self._logger.debug(f"{self.tag} {msg}", *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
        self._logger.exception(f"{self.tag} {msg}", *args, **kwargs)


graph_logger = DomainLogger("Graph")
retriever_logger = DomainLogger("Retriever")
prompt_logger = DomainLogger("Prompt")
llm_logger = DomainLogger("LLM")
report_logger = DomainLogger("Report")
recommendation_logger_tagged = DomainLogger("Recommendation")
