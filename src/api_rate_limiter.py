#!/usr/bin/env python3
"""
API Rate Limiter - Prevents hitting API rate limits with smart backoff

This module provides decorators and utilities for rate limiting API calls
with exponential backoff and retry logic.
"""

import time
import logging
from functools import wraps
from typing import Callable, List, Optional
from collections import deque

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter with sliding window algorithm.
    
    Tracks API call timestamps and enforces rate limits with automatic delays.
    """
    
    def __init__(self, calls_per_minute: int = 30, max_retries: int = 4):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_minute: Maximum API calls allowed per minute
            max_retries: Maximum number of retries for failed requests
        """
        self.calls_per_minute = calls_per_minute
        self.max_retries = max_retries
        self.call_times: deque = deque()  # Timestamps of recent calls
        self.window_size = 60  # 60 seconds
    
    def _clean_old_calls(self):
        """Remove call timestamps older than window_size"""
        now = time.time()
        while self.call_times and (now - self.call_times[0]) > self.window_size:
            self.call_times.popleft()
    
    def _wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        self._clean_old_calls()
        
        if len(self.call_times) >= self.calls_per_minute:
            # Calculate how long to wait
            oldest_call = self.call_times[0]
            wait_time = self.window_size - (time.time() - oldest_call)
            
            if wait_time > 0:
                logger.warning(
                    f"Rate limit reached ({self.calls_per_minute} calls/min). "
                    f"Waiting {wait_time:.1f}s..."
                )
                time.sleep(wait_time + 0.1)  # Small buffer
                self._clean_old_calls()
    
    def __call__(self, func: Callable) -> Callable:
        """
        Decorator to rate limit a function.
        
        Usage:
            @RateLimiter(calls_per_minute=30)
            def fetch_data(url):
                return requests.get(url)
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            self._wait_if_needed()
            self.call_times.append(time.time())
            return func(*args, **kwargs)
        
        return wrapper


class RetryWithBackoff:
    """
    Retry decorator with exponential backoff.
    
    Automatically retries failed requests with increasing delays.
    """
    
    def __init__(
        self,
        max_retries: int = 4,
        initial_delay: float = 2.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,)
    ):
        """
        Initialize retry decorator.
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds (2s)
            backoff_factor: Multiply delay by this after each retry (2.0)
            exceptions: Tuple of exceptions to catch and retry
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.exceptions = exceptions
    
    def __call__(self, func: Callable) -> Callable:
        """
        Decorator to add retry logic with exponential backoff.
        
        Usage:
            @RetryWithBackoff(max_retries=4, initial_delay=2.0)
            def fetch_data(url):
                return requests.get(url)
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = self.initial_delay
            
            for attempt in range(self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                
                except self.exceptions as e:
                    if attempt == self.max_retries:
                        logger.error(
                            f"{func.__name__} failed after {self.max_retries} retries: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{self.max_retries}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                    delay *= self.backoff_factor
            
            return None
        
        return wrapper


def rate_limited_api_call(
    calls_per_minute: int = 30,
    max_retries: int = 4,
    retry_exceptions: tuple = (Exception,)
) -> Callable:
    """
    Combined decorator for rate limiting + retry with backoff.
    
    This is a convenience function that combines both RateLimiter and
    RetryWithBackoff for easy application to API functions.
    
    Args:
        calls_per_minute: Maximum API calls per minute
        max_retries: Maximum retry attempts
        retry_exceptions: Exceptions to catch and retry
    
    Usage:
        @rate_limited_api_call(calls_per_minute=30, max_retries=4)
        def fetch_steamspy_data(app_id):
            return requests.get(f"https://steamspy.com/api.php?appid={app_id}")
    
    Example:
        @rate_limited_api_call(
            calls_per_minute=60,
            max_retries=3,
            retry_exceptions=(requests.exceptions.HTTPError,)
        )
        def get_game_data(game_id):
            response = requests.get(f"https://api.example.com/games/{game_id}")
            response.raise_for_status()
            return response.json()
    """
    def decorator(func: Callable) -> Callable:
        # Apply rate limiter first, then retry logic
        rate_limiter = RateLimiter(calls_per_minute=calls_per_minute)
        retry_decorator = RetryWithBackoff(
            max_retries=max_retries,
            exceptions=retry_exceptions
        )
        
        return rate_limiter(retry_decorator(func))
    
    return decorator


# Pre-configured rate limiters for common APIs
steamspy_rate_limiter = RateLimiter(calls_per_minute=30)
steam_api_rate_limiter = RateLimiter(calls_per_minute=100)
general_api_rate_limiter = RateLimiter(calls_per_minute=60)


# Test the rate limiter
if __name__ == "__main__":
    import requests
    
    print("="*80)
    print("API RATE LIMITER TEST")
    print("="*80 + "\n")
    
    # Test 1: Rate limiting
    print("TEST 1: Rate Limiting (5 calls in quick succession)")
    print("-"*80)
    
    @RateLimiter(calls_per_minute=3)  # Only 3 calls per minute
    def test_call(call_num):
        print(f"  Call {call_num} executed at {time.time():.2f}")
        return f"Result {call_num}"
    
    start = time.time()
    for i in range(5):
        test_call(i + 1)
    elapsed = time.time() - start
    
    print(f"\nTotal time: {elapsed:.2f}s")
    if elapsed > 60:
        print("✅ Rate limiting working (took >60s for 5 calls with 3/min limit)")
    else:
        print("⚠️  Rate limiting may not be working correctly")
    
    # Test 2: Retry with backoff
    print("\n" + "="*80)
    print("TEST 2: Retry with Exponential Backoff")
    print("-"*80)
    
    attempt_count = [0]
    
    @RetryWithBackoff(max_retries=3, initial_delay=1.0, exceptions=(ValueError,))
    def flaky_function():
        attempt_count[0] += 1
        print(f"  Attempt {attempt_count[0]}")
        if attempt_count[0] < 3:
            raise ValueError("Simulated failure")
        return "Success!"
    
    try:
        result = flaky_function()
        print(f"\n✅ Function succeeded after {attempt_count[0]} attempts: {result}")
    except ValueError as e:
        print(f"\n❌ Function failed after max retries: {e}")
    
    # Test 3: Combined decorator
    print("\n" + "="*80)
    print("TEST 3: Combined Rate Limiting + Retry")
    print("-"*80)
    
    @rate_limited_api_call(calls_per_minute=60, max_retries=2)
    def mock_api_call(item_id):
        print(f"  Fetching item {item_id}")
        return {"id": item_id, "data": "example"}
    
    for i in range(3):
        result = mock_api_call(i + 1)
        print(f"  ✅ Got result: {result}")
    
    print("\n" + "="*80)
    print("RATE LIMITER TESTS COMPLETE")
    print("="*80)
