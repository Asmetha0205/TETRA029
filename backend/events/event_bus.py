"""
Event Bus Singleton and Broadcaster.
Supports pub/sub subscriptions, filtering, and event history recording.
"""

import threading
from typing import Any, Callable, Dict, List, Optional
from backend.events.event_models import Event, EventType
from backend.events.event_logger import EventLogger
from backend.utils.logger import get_logger

logger = get_logger("events.bus")


class EventBus:
    """Thread-safe event bus for publishing and subscribing to system events."""

    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._global_subscribers: List[Callable[[Event], None]] = []
        self._history: List[Event] = []
        self._lock = threading.RLock()

        # Register default event logger
        self.subscribe_global(EventLogger.log_event)

    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """Subscribe callback to specific event type."""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)

    def subscribe_global(self, callback: Callable[[Event], None]) -> None:
        """Subscribe callback to all events."""
        with self._lock:
            self._global_subscribers.append(callback)

    def publish(
        self,
        event_type: EventType,
        payload: Optional[Dict[str, Any]] = None,
        analysis_id: Optional[str] = None,
        source: str = "system",
    ) -> Event:
        """Publish an event to all interested subscribers."""
        event = Event(
            event_type=event_type,
            payload=payload or {},
            analysis_id=analysis_id,
            source=source,
        )

        with self._lock:
            self._history.append(event)

            # Invoke specific subscribers
            for cb in self._subscribers.get(event_type, []):
                try:
                    cb(event)
                except Exception as exc:
                    logger.error("[EventBus] Subscriber exception for %s: %s", event_type, exc)

            # Invoke global subscribers
            for cb in self._global_subscribers:
                try:
                    cb(event)
                except Exception as exc:
                    logger.error("[EventBus] Global subscriber exception for %s: %s", event_type, exc)

        return event

    def get_history(
        self,
        analysis_id: Optional[str] = None,
        event_type: Optional[EventType] = None,
        limit: int = 100,
    ) -> List[Event]:
        """Retrieve historical published events with optional filtering."""
        with self._lock:
            filtered = self._history
            if analysis_id:
                filtered = [e for e in filtered if e.analysis_id == analysis_id]
            if event_type:
                filtered = [e for e in filtered if e.event_type == event_type]
            return filtered[-limit:]


# Global singleton instance
event_bus = EventBus()
