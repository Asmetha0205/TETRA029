"""
Unified Logger for CurricuAlign AI Phase 7 Integration.
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Get or configure a structured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


system_logger = get_logger("curricualign.system")
