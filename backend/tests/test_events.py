"""
Unit tests for Event System.
"""

import unittest
from backend.events.event_bus import EventBus
from backend.events.event_models import EventType


class TestEventSystem(unittest.TestCase):

    def test_publish_and_subscribe(self):
        bus = EventBus()
        received = []

        def sub(evt):
            received.append(evt)

        bus.subscribe(EventType.PDF_UPLOADED, sub)
        bus.publish(EventType.PDF_UPLOADED, {"file": "syllabus.pdf"})

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].payload["file"], "syllabus.pdf")

    def test_event_history_filtering(self):
        bus = EventBus()
        bus.publish(EventType.ACADEMIC_ANALYSIS_STARTED, analysis_id="an-1")
        bus.publish(EventType.ACADEMIC_ANALYSIS_COMPLETED, analysis_id="an-1")
        bus.publish(EventType.RECOMMENDATION_STARTED, analysis_id="an-2")

        history = bus.get_history(analysis_id="an-1")
        self.assertEqual(len(history), 2)


if __name__ == "__main__":
    unittest.main()
