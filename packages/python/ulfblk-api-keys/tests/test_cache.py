"""Tests for InMemoryCache with TTL."""

from __future__ import annotations

import time
from unittest.mock import patch

from ulfblk_api_keys import InMemoryCache


class TestInMemoryCache:

    def test_set_and_get(self):
        cache = InMemoryCache(default_ttl=60)
        cache.set("k1", {"data": "value"})
        assert cache.get("k1") == {"data": "value"}

    def test_get_nonexistent_returns_none(self):
        cache = InMemoryCache(default_ttl=60)
        assert cache.get("missing") is None

    def test_ttl_expiration(self):
        cache = InMemoryCache(default_ttl=1)
        cache.set("k1", "value", ttl=0)  # expires immediately
        # Simulate time passing
        with patch("ulfblk_api_keys.cache.time.monotonic", return_value=time.monotonic() + 2):
            assert cache.get("k1") is None

    def test_invalidate(self):
        cache = InMemoryCache(default_ttl=60)
        cache.set("k1", "value")
        assert cache.invalidate("k1") is True
        assert cache.get("k1") is None
        assert cache.invalidate("k1") is False

    def test_clear(self):
        cache = InMemoryCache(default_ttl=60)
        cache.set("k1", "a")
        cache.set("k2", "b")
        assert cache.size == 2
        cache.clear()
        assert cache.size == 0

    def test_custom_ttl_per_entry(self):
        cache = InMemoryCache(default_ttl=60)
        cache.set("short", "val", ttl=0)
        cache.set("long", "val", ttl=9999)
        with patch("ulfblk_api_keys.cache.time.monotonic", return_value=time.monotonic() + 2):
            assert cache.get("short") is None
            assert cache.get("long") == "val"
