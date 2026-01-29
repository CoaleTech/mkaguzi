"""
Cache management for frequently accessed data
"""
import frappe
from functools import wraps
from typing import Any, Callable, Optional
import hashlib
import json

class CacheManager:
    """Manages caching for audit system data"""

    CACHE_PREFIX = "mkaguzi:"
    DEFAULT_TTL = 300  # 5 minutes

    @staticmethod
    def get_cache_key(prefix: str, *args, **kwargs) -> str:
        """
        Generate a cache key from function arguments

        Args:
            prefix: Cache key prefix
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Generated cache key
        """
        key_parts = [prefix]

        # Add args to key
        if args:
            key_parts.extend(str(arg) for arg in args)

        # Add sorted kwargs to key
        if kwargs:
            sorted_kwargs = json.dumps(sorted(kwargs.items()), sort_keys=True)
            key_parts.append(sorted_kwargs)

        key_string = ":".join(key_parts)
        hashed = hashlib.md5(key_string.encode()).hexdigest()

        return f"{CacheManager.CACHE_PREFIX}{prefix}:{hashed}"

    @staticmethod
    def get(cache_key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            return frappe.cache().get(cache_key)
        except Exception:
            return None

    @staticmethod
    def set(cache_key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            frappe.cache().set(cache_key, value, ttl or CacheManager.DEFAULT_TTL)
            return True
        except Exception:
            return False

    @staticmethod
    def delete(cache_key: str) -> bool:
        """Delete value from cache"""
        try:
            frappe.cache().delete(cache_key)
            return True
        except Exception:
            return False

    @staticmethod
    def clear_pattern(pattern: str) -> bool:
        """Clear all cache keys matching pattern"""
        try:
            frappe.cache().delete_keys(pattern)
            return True
        except Exception:
            return False


def cached(ttl: int = 300, key_prefix: Optional[str] = None):
    """
    Decorator for caching function results

    Args:
        ttl: Time to live in seconds
        key_prefix: Optional custom key prefix
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            prefix = key_prefix or func.__name__
            cache_key = CacheManager.get_cache_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = CacheManager.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            CacheManager.set(cache_key, result, ttl)

            return result

        # Add cache invalidation method
        wrapper.invalidate = lambda *args, **kwargs: CacheManager.delete(
            CacheManager.get_cache_key(prefix or func.__name__, *args, **kwargs)
        )

        return wrapper

    return decorator