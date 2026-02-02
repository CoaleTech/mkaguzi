"""API Rate Limiting Utility for Mkaguzi

This module provides rate limiting functionality for API endpoints to prevent
abuse and ensure fair resource allocation.
"""

import frappe
import time
from functools import wraps
from typing import Callable, Optional


class RateLimiter:
    """Simple rate limiter using Frappe cache"""

    CACHE_PREFIX = "mkaguzi:rate_limit:"
    DEFAULT_LIMIT = 100  # requests per window
    DEFAULT_WINDOW = 3600  # 1 hour in seconds

    @classmethod
    def check_rate_limit(cls, user: str, endpoint: str,
                        limit: int = DEFAULT_LIMIT,
                        window: int = DEFAULT_WINDOW) -> bool:
        """Check if user has exceeded rate limit

        Args:
            user: The user identifier
            endpoint: The endpoint identifier
            limit: Maximum requests allowed in time window
            window: Time window in seconds

        Returns:
            True if under rate limit, False if exceeded
        """
        cache = frappe.cache()
        key = f"{cls.CACHE_PREFIX}{user}:{endpoint}"
        current = cache.get(key) or 0

        if current >= limit:
            return False

        # Increment counter
        cache.set(key, current + 1, expiry=window)
        return True

    @classmethod
    def get_remaining_requests(cls, user: str, endpoint: str,
                               limit: int = DEFAULT_LIMIT) -> int:
        """Get remaining requests for user

        Args:
            user: The user identifier
            endpoint: The endpoint identifier
            limit: Maximum requests allowed

        Returns:
            Number of remaining requests
        """
        cache = frappe.cache()
        key = f"{cls.CACHE_PREFIX}{user}:{endpoint}"
        current = cache.get(key) or 0
        return max(0, limit - current)

    @classmethod
    def reset_rate_limit(cls, user: str, endpoint: str) -> None:
        """Reset rate limit counter for user

        Args:
            user: The user identifier
            endpoint: The endpoint identifier
        """
        cache = frappe.cache()
        key = f"{cls.CACHE_PREFIX}{user}:{endpoint}"
        cache.delete(key)

    @classmethod
    def get_usage_stats(cls, user: str, endpoint: str) -> dict:
        """Get usage statistics for user

        Args:
            user: The user identifier
            endpoint: The endpoint identifier

        Returns:
            Dictionary with usage statistics
        """
        cache = frappe.cache()
        key = f"{cls.CACHE_PREFIX}{user}:{endpoint}"
        current = cache.get(key) or 0

        return {
            'user': user,
            'endpoint': endpoint,
            'requests_used': current,
            'limit': RateLimiter.DEFAULT_LIMIT,
            'remaining': max(0, RateLimiter.DEFAULT_LIMIT - current)
        }


def rate_limit(limit: int = DEFAULT_LIMIT, window: int = DEFAULT_WINDOW,
               bypass_roles: Optional[list] = None):
    """Decorator for rate limiting API endpoints

    Args:
        limit: Maximum requests per time window
        window: Time window in seconds
        bypass_roles: List of roles that bypass rate limiting

    Returns:
        Decorator function
    """
    if bypass_roles is None:
        bypass_roles = ['System Manager']

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = frappe.session.user

            # Check if user has bypass role
            user_roles = frappe.get_roles(user)
            if any(role in user_roles for role in bypass_roles):
                return func(*args, **kwargs)

            # Generate endpoint identifier
            endpoint = func.__name__

            # Check rate limit
            if not RateLimiter.check_rate_limit(user, endpoint, limit, window):
                remaining = RateLimiter.get_remaining_requests(user, endpoint, limit)

                frappe.throw(
                    _("Rate limit exceeded. Please try again later. "
                      "Remaining requests: {0}").format(remaining),
                    title=_('Rate Limit Exceeded'),
                    exc=frappe.TooManyRequestsError
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator


class SlidingWindowRateLimiter:
    """Sliding window rate limiter for more accurate rate limiting"""

    CACHE_PREFIX = "mkaguzi:sliding_rate_limit:"
    DEFAULT_LIMIT = 100
    DEFAULT_WINDOW = 3600

    @classmethod
    def check_rate_limit(cls, user: str, endpoint: str,
                        limit: int = DEFAULT_LIMIT,
                        window: int = DEFAULT_WINDOW) -> bool:
        """Check if user has exceeded rate limit using sliding window

        Args:
            user: The user identifier
            endpoint: The endpoint identifier
            limit: Maximum requests allowed in time window
            window: Time window in seconds

        Returns:
            True if under rate limit, False if exceeded
        """
        cache = frappe.cache()
        current_time = int(time.time())
        key = f"{cls.CACHE_PREFIX}{user}:{endpoint}"

        # Get existing request timestamps
        request_times = cache.get(key)
        if not request_times:
            request_times = []

        # Filter out timestamps outside the window
        request_times = [t for t in request_times if current_time - t < window]

        # Check if limit exceeded
        if len(request_times) >= limit:
            return False

        # Add current request timestamp
        request_times.append(current_time)

        # Store updated list with expiry
        cache.set(key, request_times, expiry=window)

        return True


class TokenBucketRateLimiter:
    """Token bucket rate limiter for burst traffic handling"""

    CACHE_PREFIX = "mkaguzi:token_bucket:"
    DEFAULT_CAPACITY = 100  # Maximum tokens
    DEFAULT_REFILL_RATE = 10  # Tokens per second

    @classmethod
    def check_rate_limit(cls, user: str, endpoint: str,
                        capacity: int = DEFAULT_CAPACITY,
                        refill_rate: int = DEFAULT_REFILL_RATE) -> bool:
        """Check if user has tokens available using token bucket algorithm

        Args:
            user: The user identifier
            endpoint: The endpoint identifier
            capacity: Maximum token capacity
            refill_rate: Tokens refilled per second

        Returns:
            True if tokens available, False if bucket empty
        """
        cache = frappe.cache()
        key = f"{cls.CACHE_PREFIX}{user}:{endpoint}"
        current_time = time.time()

        # Get current token state
        state = cache.get(key)
        if not state:
            state = {
                'tokens': capacity,
                'last_refill': current_time
            }

        # Calculate tokens to add
        time_passed = current_time - state['last_refill']
        tokens_to_add = time_passed * refill_rate

        # Update tokens
        state['tokens'] = min(capacity, state['tokens'] + tokens_to_add)
        state['last_refill'] = current_time

        # Check if token available
        if state['tokens'] < 1:
            cache.set(key, state, expiry=3600)
            return False

        # Consume token
        state['tokens'] -= 1
        cache.set(key, state, expiry=3600)

        return True


def rate_limit_by_ip(limit: int = 100, window: int = 3600):
    """Rate limit by IP address instead of user

    Useful for public/unauthenticated endpoints

    Args:
        limit: Maximum requests per time window
        window: Time window in seconds

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get IP address from request
            from frappe.local import request
            ip = frappe.local.request_ip

            if not ip:
                return func(*args, **kwargs)

            endpoint = func.__name__

            if not RateLimiter.check_rate_limit(f"ip:{ip}", endpoint, limit, window):
                frappe.throw(
                    _("Rate limit exceeded from this IP address"),
                    title=_('Rate Limit Exceeded'),
                    exc=frappe.TooManyRequestsError
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator


class RateLimitExceeded(frappe.TooManyRequestsError):
    """Custom exception for rate limit exceeded"""
    pass


def get_rate_limit_headers(user: str, endpoint: str,
                           limit: int = RateLimiter.DEFAULT_LIMIT,
                           window: int = RateLimiter.DEFAULT_WINDOW) -> dict:
    """Get rate limit headers for API responses

    Args:
        user: The user identifier
        endpoint: The endpoint identifier
        limit: Maximum requests allowed
        window: Time window in seconds

    Returns:
        Dictionary with rate limit headers
    """
    remaining = RateLimiter.get_remaining_requests(user, endpoint, limit)

    return {
        'X-RateLimit-Limit': str(limit),
        'X-RateLimit-Remaining': str(remaining),
        'X-RateLimit-Reset': str(int(time.time()) + window)
    }
