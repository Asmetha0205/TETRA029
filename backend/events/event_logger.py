"""
Event Logger for Structured Tagged Logging.
Logs system events with tagged prefixes like [Workflow], [Academic], [Semantic], [Recommendation], [Report].
"""

import logging
from backend.events.event_models import Event, EventType
from backend.utils.logger import get_logger

logger = get_logger("events.logger")


class EventLogger:
    """Subscriber component that formats and logs system events."""

    TAG_MAPPING = {
        EventType.PDF_UPLOADED: "[Workflow]",
        EventType.ACADEMIC_ANALYSIS_STARTED: "[Academic]",
        EventType.ACADEMIC_ANALYSIS_COMPLETED: "[Academic]",
        EventType.SEMANTIC_ANALYSIS_STARTED: "[Semantic]",
        EventType.SEMANTIC_ANALYSIS_COMPLETED: "[Semantic]",
        EventType.RECOMMENDATION_STARTED: "[Recommendation]",
        EventType.RECOMMENDATION_COMPLETED: "[Recommendation]",
        EventType.REPORT_GENERATED: "[Report]",
        EventType.ANALYSIS_COMPLETED: "[Workflow]",
        EventType.WORKFLOW_FAILED: "[Workflow]",
        EventType.STEP_FAILED: "[Workflow]",
    }

    @classmethod
    def log_event(cls, event: Event) -> None:
        """Format and write structured log message."""
        tag = cls.TAG_MAPPING.get(event.event_type, "[System]")
        analysis_str = f" [Analysis: {event.analysis_id}]" if event.analysis_id else ""
        msg = f"{tag}{analysis_str} {event.event_type.value}: {event.payload.get('message', event.payload)}"

        if "FAILED" in event.event_type.value:
            logger.error(msg)
        else:
            logger.info(msg)
