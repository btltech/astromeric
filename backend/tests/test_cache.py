"""
test_cache.py
-------------
Comprehensive tests for the caching system.
"""

import pytest
import time
from unittest.mock import patch

from app.cache import (
    ChartCache,
    CacheEntry,
    get_chart_cache,
    cached_build_chart,
)


class TestChartCache:
    """Tests for ChartCache class."""

    def test_basic_set_and_get(self):
        cache = ChartCache(max_size=10, ttl_seconds=3600)
        profile = {
            "date_of_birth": "1990-01-01",
            "time_of_birth": "12:00",
            "latitude": 40.0,
            "longitude": -74.0,
            "house_system": "Placidus",
        }
        chart_data = {"planets": [], "houses": []}
        
        cache.set(profile, "natal", chart_data)
        result = cache.get(profile, "natal")
        
        assert result == chart_data

    def test_cache_miss_returns_none(self):
        cache = ChartCache()
        profile = {"date_of_birth": "1990-01-01"}
        
        result = cache.get(profile, "natal")
        assert result is None

    def test_different_profiles_different_keys(self):
        cache = ChartCache()
        profile_a = {"date_of_birth": "1990-01-01", "latitude": 40.0, "longitude": -74.0}
        profile_b = {"date_of_birth": "1990-01-02", "latitude": 40.0, "longitude": -74.0}
        
        cache.set(profile_a, "natal", {"person": "A"})
        cache.set(profile_b, "natal", {"person": "B"})
        
        assert cache.get(profile_a, "natal")["person"] == "A"
        assert cache.get(profile_b, "natal")["person"] == "B"

    def test_different_chart_types(self):
        cache = ChartCache()
        profile = {"date_of_birth": "1990-01-01", "latitude": 40.0, "longitude": -74.0}
        
        cache.set(profile, "natal", {"type": "natal"})
        cache.set(profile, "transit", {"type": "transit"})
        
        assert cache.get(profile, "natal")["type"] == "natal"
        assert cache.get(profile, "transit")["type"] == "transit"

    def test_ttl_expiration(self):
        cache = ChartCache(ttl_seconds=1)  # 1 second TTL
        profile = {"date_of_birth": "1990-01-01"}
        
        cache.set(profile, "natal", {"data": "test"})
        assert cache.get(profile, "natal") is not None
        
        time.sleep(1.1)  # Wait for expiration
        assert cache.get(profile, "natal") is None

    def test_max_size_eviction(self):
        cache = ChartCache(max_size=2, ttl_seconds=3600)
        
        profile_a = {"date_of_birth": "1990-01-01"}
        profile_b = {"date_of_birth": "1990-01-02"}
        profile_c = {"date_of_birth": "1990-01-03"}
        
        cache.set(profile_a, "natal", {"id": "A"})
        cache.set(profile_b, "natal", {"id": "B"})
        cache.set(profile_c, "natal", {"id": "C"})  # Should evict A
        
        assert cache.get(profile_a, "natal") is None  # Evicted
        assert cache.get(profile_b, "natal") is not None
        assert cache.get(profile_c, "natal") is not None

    def test_access_updates_lru_order(self):
        cache = ChartCache(max_size=2, ttl_seconds=3600)
        
        profile_a = {"date_of_birth": "1990-01-01"}
        profile_b = {"date_of_birth": "1990-01-02"}
        profile_c = {"date_of_birth": "1990-01-03"}
        
        cache.set(profile_a, "natal", {"id": "A"})
        cache.set(profile_b, "natal", {"id": "B"})
        
        # Access A to make it recently used
        cache.get(profile_a, "natal")
        
        # Add C - should evict B (least recently used)
        cache.set(profile_c, "natal", {"id": "C"})
        
        assert cache.get(profile_a, "natal") is not None  # Still there
        assert cache.get(profile_b, "natal") is None  # Evicted
        assert cache.get(profile_c, "natal") is not None

    def test_invalidate_removes_entry(self):
        cache = ChartCache()
        profile = {"date_of_birth": "1990-01-01"}
        
        cache.set(profile, "natal", {"data": "test"})
        assert cache.get(profile, "natal") is not None
        
        result = cache.invalidate(profile, "natal")
        assert result is True
        assert cache.get(profile, "natal") is None

    def test_invalidate_nonexistent_returns_false(self):
        cache = ChartCache()
        profile = {"date_of_birth": "1990-01-01"}
        
        result = cache.invalidate(profile, "natal")
        assert result is False

    def test_clear_removes_all(self):
        cache = ChartCache()
        
        for i in range(5):
            cache.set({"date_of_birth": f"1990-01-0{i}"}, "natal", {"i": i})
        
        assert len(cache) == 5
        count = cache.clear()
        assert count == 5
        assert len(cache) == 0

    def test_cleanup_expired(self):
        cache = ChartCache(ttl_seconds=1)
        
        cache.set({"date_of_birth": "1990-01-01"}, "natal", {"data": 1})
        cache.set({"date_of_birth": "1990-01-02"}, "natal", {"data": 2})
        
        time.sleep(1.1)
        
        # Add a fresh entry
        cache.set({"date_of_birth": "1990-01-03"}, "natal", {"data": 3})
        
        removed = cache.cleanup_expired()
        assert removed == 2  # Two expired entries removed
        assert len(cache) == 1  # Only fresh entry remains

    def test_get_stats(self):
        cache = ChartCache(max_size=10, ttl_seconds=3600)
        profile = {"date_of_birth": "1990-01-01"}
        
        # Generate some activity
        cache.get(profile, "natal")  # Miss
        cache.set(profile, "natal", {"data": "test"})
        cache.get(profile, "natal")  # Hit
        cache.get(profile, "natal")  # Hit
        
        stats = cache.get_stats()
        
        assert stats["size"] == 1
        assert stats["max_size"] == 10
        assert stats["ttl_seconds"] == 3600
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == pytest.approx(66.67, rel=0.1)

    def test_len(self):
        cache = ChartCache()
        assert len(cache) == 0
        
        cache.set({"date_of_birth": "1990-01-01"}, "natal", {})
        assert len(cache) == 1
        
        cache.set({"date_of_birth": "1990-01-02"}, "natal", {})
        assert len(cache) == 2

    def test_contains(self):
        cache = ChartCache()
        profile = {"date_of_birth": "1990-01-01"}
        
        assert profile not in cache
        
        cache.set(profile, "natal", {})
        assert profile in cache

    def test_update_existing_entry(self):
        cache = ChartCache()
        profile = {"date_of_birth": "1990-01-01"}
        
        cache.set(profile, "natal", {"version": 1})
        cache.set(profile, "natal", {"version": 2})
        
        result = cache.get(profile, "natal")
        assert result["version"] == 2
        assert len(cache) == 1  # Still just one entry


class TestCacheEntry:
    """Tests for CacheEntry dataclass."""

    def test_creation(self):
        entry = CacheEntry(
            value={"data": "test"},
            created_at=1000.0,
            access_count=5,
            last_accessed=1500.0
        )
        
        assert entry.value == {"data": "test"}
        assert entry.created_at == 1000.0
        assert entry.access_count == 5
        assert entry.last_accessed == 1500.0

    def test_defaults(self):
        entry = CacheEntry(value={}, created_at=0.0)
        
        assert entry.access_count == 0
        assert entry.last_accessed == 0


class TestGetChartCache:
    """Tests for global cache singleton."""

    def test_returns_same_instance(self):
        cache1 = get_chart_cache()
        cache2 = get_chart_cache()
        
        assert cache1 is cache2


class TestCachedBuildChart:
    """Tests for cached_build_chart helper function."""

    def test_calls_builder_on_miss(self):
        # Use a fresh cache to avoid interference
        with patch('app.cache._chart_cache', ChartCache()):
            profile = {"date_of_birth": "1990-01-01", "latitude": 0, "longitude": 0}
            
            def mock_builder(p):
                return {"metadata": {}, "built": True}
            
            result = cached_build_chart(profile, "natal", mock_builder)
            
            assert result["built"] is True
            assert result["metadata"]["cached"] is False

    def test_returns_cached_on_hit(self):
        with patch('app.cache._chart_cache', ChartCache()):
            profile = {"date_of_birth": "1990-01-01", "latitude": 0, "longitude": 0}
            call_count = 0
            
            def mock_builder(p):
                nonlocal call_count
                call_count += 1
                return {"metadata": {}, "built": True}
            
            # First call - builds
            cached_build_chart(profile, "natal", mock_builder)
            assert call_count == 1
            
            # Second call - from cache
            result = cached_build_chart(profile, "natal", mock_builder)
            assert call_count == 1  # Builder not called again
            assert result["metadata"]["cached"] is True


class TestCacheKeyGeneration:
    """Tests for cache key generation consistency."""

    def test_same_profile_same_key(self):
        cache = ChartCache()
        profile = {"date_of_birth": "1990-01-01", "latitude": 40.0, "longitude": -74.0}
        
        key1 = cache._generate_key(profile, "natal")
        key2 = cache._generate_key(profile, "natal")
        
        assert key1 == key2

    def test_different_date_different_key(self):
        cache = ChartCache()
        profile_a = {"date_of_birth": "1990-01-01", "latitude": 40.0, "longitude": -74.0}
        profile_b = {"date_of_birth": "1990-01-02", "latitude": 40.0, "longitude": -74.0}
        
        key_a = cache._generate_key(profile_a, "natal")
        key_b = cache._generate_key(profile_b, "natal")
        
        assert key_a != key_b

    def test_different_time_different_key(self):
        cache = ChartCache()
        profile_a = {"date_of_birth": "1990-01-01", "time_of_birth": "12:00"}
        profile_b = {"date_of_birth": "1990-01-01", "time_of_birth": "14:00"}
        
        key_a = cache._generate_key(profile_a, "natal")
        key_b = cache._generate_key(profile_b, "natal")
        
        assert key_a != key_b

    def test_coordinate_precision(self):
        cache = ChartCache()
        # Coordinates rounded to 4 decimal places should be same key
        # The 5th decimal place should be ignored (diff of 0.00001)
        profile_a = {"date_of_birth": "1990-01-01", "latitude": 40.71280, "longitude": -74.00600}
        profile_b = {"date_of_birth": "1990-01-01", "latitude": 40.71280, "longitude": -74.00600}
        
        key_a = cache._generate_key(profile_a, "natal")
        key_b = cache._generate_key(profile_b, "natal")
        
        # Same coordinates should produce same key
        assert key_a == key_b
        
        # Significantly different coordinates should produce different keys
        profile_c = {"date_of_birth": "1990-01-01", "latitude": 40.72, "longitude": -74.01}
        key_c = cache._generate_key(profile_c, "natal")
        assert key_a != key_c

    def test_house_system_affects_key(self):
        cache = ChartCache()
        profile_a = {"date_of_birth": "1990-01-01", "house_system": "Placidus"}
        profile_b = {"date_of_birth": "1990-01-01", "house_system": "Whole"}
        
        key_a = cache._generate_key(profile_a, "natal")
        key_b = cache._generate_key(profile_b, "natal")
        
        assert key_a != key_b
