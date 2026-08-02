"""
Unit tests for Cache Layer.
"""

import unittest
import time
from backend.cache.cache_manager import CacheManager
from backend.cache.cache_service import CacheService


class TestCacheLayer(unittest.TestCase):

    def test_cache_set_get(self):
        cm = CacheManager(default_ttl=60)
        cm.set("key1", {"data": "test"})
        self.assertEqual(cm.get("key1"), {"data": "test"})

    def test_cache_ttl_expiry(self):
        cm = CacheManager(default_ttl=1)
        cm.set("short_key", "value", ttl_seconds=1)
        self.assertEqual(cm.get("short_key"), "value")
        time.sleep(1.1)
        self.assertIsNone(cm.get("short_key"))

    def test_cache_service_domain_methods(self):
        cs = CacheService()
        cs.set_knowledge("python", {"name": "Python"})
        self.assertEqual(cs.get_knowledge("python"), {"name": "Python"})

        stats = cs.get_statistics()
        self.assertGreaterEqual(stats.total_hits, 1)


if __name__ == "__main__":
    unittest.main()
