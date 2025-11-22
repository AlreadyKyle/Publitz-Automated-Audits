#!/usr/bin/env python3
"""
Retry utilities for API calls with exponential backoff
"""

import time
import functools
from typing import Callable, Type, Tuple, Optional
from src.logger import get_logger
from src.exceptions import RateLimitError, TimeoutError as PublitzTimeoutError

logger = get_logger(__name__)


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 30.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator for retrying functions with exponential backoff

    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each attempt
        max_delay: Maximum delay between retries
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Optional callback function(attempt, exception, delay)

    Example:
        @retry_with_backoff(max_attempts=3, initial_delay=1.0)
        def fetch_data():
            return requests.get(url)
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    # Don't retry on last attempt
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts",
                            exc_info=True
                        )
                        break

                    # Calculate next delay
                    current_delay = min(delay, max_delay)

                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}). "
                        f"Retrying in {current_delay:.1f}s... Error: {str(e)}"
                    )

                    # Call retry callback if provided
                    if on_retry:
                        on_retry(attempt, e, current_delay)

                    # Sleep before retry
                    time.sleep(current_delay)

                    # Exponential backoff
                    delay *= backoff_factor

            # All retries exhausted
            raise last_exception

        return wrapper

    return decorator


def timeout_handler(timeout_seconds: int):
    """
    Decorator to add timeout to function calls

    Note: This uses a simple approach. For production, consider using
    signal-based timeouts (Unix) or threading-based approaches.

    Args:
        timeout_seconds: Maximum execution time in seconds

    Example:
        @timeout_handler(10)
        def slow_operation():
            # This will raise TimeoutError if it takes > 10s
            time.sleep(15)
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal

            def timeout_signal_handler(signum, frame):
                raise PublitzTimeoutError(func.__name__, timeout_seconds)

            # Set up signal handler (Unix only)
            try:
                signal.signal(signal.SIGALRM, timeout_signal_handler)
                signal.alarm(timeout_seconds)

                try:
                    result = func(*args, **kwargs)
                finally:
                    signal.alarm(0)  # Disable alarm

                return result

            except AttributeError:
                # Windows doesn't support SIGALRM, fallback to simple execution
                logger.warning(f"Timeout handler not supported on this platform")
                return func(*args, **kwargs)

        return wrapper

    return decorator


class RateLimiter:
    """
    Simple rate limiter using token bucket algorithm

    Usage:
        limiter = RateLimiter(calls_per_minute=60)

        @limiter.limit
        def api_call():
            return requests.get(url)
    """

    def __init__(self, calls_per_minute: int):
        """
        Initialize rate limiter

        Args:
            calls_per_minute: Maximum number of calls per minute
        """
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_call = 0

    def limit(self, func):
        """
        Decorator to rate limit function calls

        Args:
            func: Function to rate limit

        Returns:
            Wrapped function
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            elapsed = now - self.last_call

            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)

            self.last_call = time.time()
            return func(*args, **kwargs)

        return wrapper


# Pre-configured rate limiters for common APIs
steam_api_limiter = RateLimiter(calls_per_minute=100)  # Conservative limit
claude_api_limiter = RateLimiter(calls_per_minute=45)  # 50 req/min with safety margin
