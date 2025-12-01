"""
cache.py
--------
In-memory caching for chart calculations with TTL support.

Features:
- LRU cache with configurable size
- TTL-based expiration
- Thread-safe operations
- Cache statistics for monitoring
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Dict, Optional

# Configuration via environment
CACHE_MAX_SIZE = int(os.getenv("CHART_CACHE_MAX_SIZE", "1000"))
CACHE_TTL_SECONDS = int(os.getenv("CHART_CACHE_TTL", "3600"))  # 1 hour default


@dataclass
class CacheEntry:
    """Single cache entry with value and metadata."""
    value: Any
    created_at: float
    access_count: int = 0
    last_accessed: float = 0


class ChartCache:
    """
    Thread-safe LRU cache with TTL for chart calculations.
    
    Features:
    - O(1) get/set operations
    - Automatic eviction of oldest entries when max size reached
    - TTL-based expiration
    - Statistics tracking
    """
    
    def __init__(
        self, 
        max_size: int = CACHE_MAX_SIZE, 
        ttl_seconds: int = CACHE_TTL_SECONDS
    ):
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._lock = threading.RLock()
        
        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._expirations = 0
    
    def _generate_key(self, profile: Dict, chart_type: str = "natal") -> str:
        """Generate a unique cache key from profile data."""
        # Include all factors that affect chart calculation
        key_data = {
            "date": profile.get("date_of_birth"),
            "time": profile.get("time_of_birth"),
            "lat": round(profile.get("latitude", 0.0), 4),  # 4 decimal places ≈ 11m precision
            "lon": round(profile.get("longitude", 0.0), 4),
            "house": profile.get("house_system", "Placidus"),
            "type": chart_type,
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]
    
    def get(self, profile: Dict, chart_type: str = "natal") -> Optional[Dict]:
        """
        Get a cached chart result.
        
        Args:
            profile: Profile dictionary
            chart_type: Type of chart (natal, transit)
        
        Returns:
            Cached chart data or None if not found/expired
        """
        key = self._generate_key(profile, chart_type)
        
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._misses += 1
                return None
            
            # Check TTL
            now = time.time()
            if now - entry.created_at > self._ttl_seconds:
                # Expired - remove and return None
                del self._cache[key]
                self._expirations += 1
                self._misses += 1
                return None
            
            # Update access stats and move to end (most recently used)
            entry.access_count += 1
            entry.last_accessed = now
            self._cache.move_to_end(key)
            self._hits += 1
            
            return entry.value
    
    def set(self, profile: Dict, chart_type: str, value: Dict) -> None:
        """
        Cache a chart result.
        
        Args:
            profile: Profile dictionary
            chart_type: Type of chart (natal, transit)
            value: Chart data to cache
        """
        key = self._generate_key(profile, chart_type)
        now = time.time()
        
        with self._lock:
            # If key exists, update it
            if key in self._cache:
                self._cache[key].value = value
                self._cache[key].created_at = now
                self._cache.move_to_end(key)
                return
            
            # Evict oldest if at capacity
            while len(self._cache) >= self._max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._evictions += 1
            
            # Add new entry
            self._cache[key] = CacheEntry(
                value=value,
                created_at=now,
                access_count=0,
                last_accessed=now
            )
    
    def invalidate(self, profile: Dict, chart_type: str = "natal") -> bool:
        """
        Remove a specific entry from cache.
        
        Args:
            profile: Profile dictionary
            chart_type: Type of chart
        
        Returns:
            True if entry was found and removed
        """
        key = self._generate_key(profile, chart_type)
        
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> int:
        """
        Clear all cached entries.
        
        Returns:
            Number of entries cleared
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        now = time.time()
        expired_keys = []
        
        with self._lock:
            for key, entry in self._cache.items():
                if now - entry.created_at > self._ttl_seconds:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                self._expirations += 1
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0.0
            
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "ttl_seconds": self._ttl_seconds,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 2),
                "evictions": self._evictions,
                "expirations": self._expirations,
            }
    
    def __len__(self) -> int:
        return len(self._cache)
    
    def __contains__(self, profile: Dict) -> bool:
        return self.get(profile) is not None


# Global cache instance
_chart_cache: Optional[ChartCache] = None


def get_chart_cache() -> ChartCache:
    """Get the global chart cache instance."""
    global _chart_cache
    if _chart_cache is None:
        _chart_cache = ChartCache()
    return _chart_cache


def cached_build_chart(profile: Dict, chart_type: str, builder_func) -> Dict:
    """
    Build a chart with caching.
    
    Args:
        profile: Profile dictionary
        chart_type: Type of chart
        builder_func: Function to call if cache miss
    
    Returns:
        Chart data (from cache or freshly built)
    """
    cache = get_chart_cache()
    
    # Try cache first
    cached = cache.get(profile, chart_type)
    if cached is not None:
        # Add cache indicator to metadata
        cached_copy = dict(cached)
        if "metadata" in cached_copy:
            cached_copy["metadata"]["cached"] = True
        return cached_copy
    
    # Cache miss - build and cache
    result = builder_func(profile)
    cache.set(profile, chart_type, result)
    
    # Mark as fresh
    if "metadata" in result:
        result["metadata"]["cached"] = False
    
    return result
