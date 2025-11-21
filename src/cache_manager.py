#!/usr/bin/env python3
"""
Disk-based cache manager for API responses
Speeds up data collection without affecting report quality
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from src.logger import get_logger

logger = get_logger(__name__)


class CacheManager:
    """
    Disk-based cache with TTL (time-to-live) for API responses

    Features:
    - Automatic cache expiration (configurable TTL)
    - Hash-based keys for any data type
    - JSON serialization
    - Cache statistics tracking
    - Automatic cleanup of expired entries
    """

    def __init__(self, cache_dir: str = ".cache", default_ttl_hours: int = 24):
        """
        Initialize cache manager

        Args:
            cache_dir: Directory for cache files
            default_ttl_hours: Default time-to-live in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = default_ttl_hours * 3600  # Convert to seconds

        # Statistics
        self.hits = 0
        self.misses = 0

        logger.info(f"Cache initialized at {self.cache_dir} with {default_ttl_hours}h TTL")

    def _generate_key(self, namespace: str, identifier: Any) -> str:
        """
        Generate cache key from namespace and identifier

        Args:
            namespace: Category (e.g., 'steam_game', 'competitors')
            identifier: Unique identifier (app_id, game_name, etc.)

        Returns:
            Hash-based cache key
        """
        # Create consistent string representation
        key_string = f"{namespace}:{str(identifier)}"

        # Generate SHA256 hash for filesystem safety
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()

        return f"{namespace}_{key_hash[:16]}.json"

    def get(self, namespace: str, identifier: Any, ttl_hours: Optional[int] = None) -> Optional[Any]:
        """
        Get cached data if available and not expired

        Args:
            namespace: Category of cached data
            identifier: Unique identifier
            ttl_hours: Custom TTL (overrides default)

        Returns:
            Cached data or None if not found/expired
        """
        cache_key = self._generate_key(namespace, identifier)
        cache_file = self.cache_dir / cache_key

        if not cache_file.exists():
            self.misses += 1
            logger.debug(f"Cache MISS: {namespace}:{identifier}")
            return None

        try:
            # Read cache file
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)

            # Check expiration
            ttl = (ttl_hours * 3600) if ttl_hours else self.default_ttl
            age = time.time() - cache_data['timestamp']

            if age > ttl:
                logger.debug(f"Cache EXPIRED: {namespace}:{identifier} (age: {age/3600:.1f}h)")
                cache_file.unlink()  # Delete expired cache
                self.misses += 1
                return None

            # Cache hit!
            self.hits += 1
            logger.debug(f"Cache HIT: {namespace}:{identifier} (age: {age/60:.1f}min)")
            return cache_data['data']

        except (json.JSONDecodeError, KeyError, OSError) as e:
            logger.warning(f"Cache read error for {namespace}:{identifier}: {e}")
            # Delete corrupted cache file
            if cache_file.exists():
                cache_file.unlink()
            self.misses += 1
            return None

    def set(self, namespace: str, identifier: Any, data: Any) -> bool:
        """
        Store data in cache

        Args:
            namespace: Category of data
            identifier: Unique identifier
            data: Data to cache (must be JSON-serializable)

        Returns:
            True if successful, False otherwise
        """
        cache_key = self._generate_key(namespace, identifier)
        cache_file = self.cache_dir / cache_key

        try:
            cache_data = {
                'timestamp': time.time(),
                'namespace': namespace,
                'identifier': str(identifier),
                'data': data
            }

            # Write to cache
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

            logger.debug(f"Cache SET: {namespace}:{identifier}")
            return True

        except (TypeError, OSError) as e:
            logger.error(f"Cache write error for {namespace}:{identifier}: {e}")
            return False

    def cached(self, namespace: str, ttl_hours: Optional[int] = None):
        """
        Decorator to automatically cache function results

        Usage:
            @cache.cached('steam_game', ttl_hours=24)
            def get_game_details(app_id):
                return fetch_from_api(app_id)

        Args:
            namespace: Category for cached data
            ttl_hours: Custom TTL

        Returns:
            Decorated function
        """
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                # Generate cache key from function arguments
                # Use first positional arg as identifier (usually app_id, game_name, etc.)
                identifier = args[0] if args else str(kwargs)

                # Try to get from cache
                cached_result = self.get(namespace, identifier, ttl_hours)
                if cached_result is not None:
                    return cached_result

                # Cache miss - call function
                logger.debug(f"Executing {func.__name__}({identifier})")
                result = func(*args, **kwargs)

                # Store in cache (only if result is not None/empty)
                if result:
                    self.set(namespace, identifier, result)

                return result

            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            return wrapper

        return decorator

    def invalidate(self, namespace: str, identifier: Optional[Any] = None):
        """
        Invalidate cache entries

        Args:
            namespace: Category to invalidate
            identifier: Specific identifier (if None, invalidates entire namespace)
        """
        if identifier is not None:
            # Invalidate specific entry
            cache_key = self._generate_key(namespace, identifier)
            cache_file = self.cache_dir / cache_key
            if cache_file.exists():
                cache_file.unlink()
                logger.info(f"Invalidated cache: {namespace}:{identifier}")
        else:
            # Invalidate entire namespace
            pattern = f"{namespace}_*.json"
            deleted = 0
            for cache_file in self.cache_dir.glob(pattern):
                cache_file.unlink()
                deleted += 1
            logger.info(f"Invalidated {deleted} cache entries in namespace: {namespace}")

    def clear_all(self):
        """Clear all cache files"""
        deleted = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            deleted += 1
        logger.info(f"Cleared all cache: {deleted} entries deleted")
        self.hits = 0
        self.misses = 0

    def cleanup_expired(self, ttl_hours: Optional[int] = None):
        """
        Remove expired cache entries

        Args:
            ttl_hours: Custom TTL for cleanup (uses default if None)
        """
        ttl = (ttl_hours * 3600) if ttl_hours else self.default_ttl
        deleted = 0
        current_time = time.time()

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)

                age = current_time - cache_data['timestamp']
                if age > ttl:
                    cache_file.unlink()
                    deleted += 1
            except (json.JSONDecodeError, KeyError, OSError):
                # Delete corrupted files
                cache_file.unlink()
                deleted += 1

        if deleted > 0:
            logger.info(f"Cleaned up {deleted} expired cache entries")

    def get_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        # Get cache size
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            'hits': self.hits,
            'misses': self.misses,
            'total_requests': total_requests,
            'hit_rate': f"{hit_rate:.1f}%",
            'cached_entries': len(cache_files),
            'total_size_kb': total_size / 1024,
            'cache_dir': str(self.cache_dir)
        }

    def print_stats(self):
        """Print cache statistics to console"""
        stats = self.get_stats()
        logger.info("=== Cache Statistics ===")
        logger.info(f"Hit Rate: {stats['hit_rate']} ({stats['hits']} hits, {stats['misses']} misses)")
        logger.info(f"Cached Entries: {stats['cached_entries']}")
        logger.info(f"Cache Size: {stats['total_size_kb']:.1f} KB")
        logger.info(f"Cache Directory: {stats['cache_dir']}")


# Global cache instance
_global_cache = None


def get_cache() -> CacheManager:
    """
    Get global cache instance (singleton pattern)

    Returns:
        Global CacheManager instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache
