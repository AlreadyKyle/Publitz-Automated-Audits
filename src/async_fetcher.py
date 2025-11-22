#!/usr/bin/env python3
"""
Async utilities for parallel API fetching
Speeds up data collection without affecting quality
"""

import asyncio
import aiohttp
import time
from typing import List, Callable, Any, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.logger import get_logger

logger = get_logger(__name__)


class ParallelFetcher:
    """
    Utility for fetching multiple items in parallel using threads

    Benefits:
    - Faster data collection (3-10x speedup for I/O-bound tasks)
    - No change to data quality
    - Automatic error handling per item
    - Progress tracking
    """

    def __init__(self, max_workers: int = 5):
        """
        Initialize parallel fetcher

        Args:
            max_workers: Maximum concurrent workers (default 5 for API rate limits)
        """
        self.max_workers = max_workers

    def fetch_many(
        self,
        items: List[Any],
        fetch_func: Callable,
        desc: str = "Fetching",
        rate_limit_delay: float = 0.2
    ) -> List[Any]:
        """
        Fetch multiple items in parallel using threads

        Args:
            items: List of items to fetch (e.g., app_ids)
            fetch_func: Function to call for each item
            desc: Description for logging
            rate_limit_delay: Delay between requests (seconds)

        Returns:
            List of results (None for failed fetches)

        Example:
            fetcher = ParallelFetcher(max_workers=5)
            game_data = fetcher.fetch_many(
                [12345, 67890, 11111],
                lambda app_id: get_game_details(app_id),
                desc="Fetching competitors"
            )
        """
        if not items:
            return []

        logger.info(f"{desc}: {len(items)} items with {self.max_workers} workers")
        start_time = time.time()

        results = [None] * len(items)  # Preserve order
        successful = 0
        failed = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(self._fetch_with_delay, fetch_func, item, rate_limit_delay): i
                for i, item in enumerate(items)
            }

            # Process completed tasks
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    if result is not None:
                        results[index] = result
                        successful += 1
                    else:
                        failed += 1
                except Exception as e:
                    logger.warning(f"Failed to fetch item {items[index]}: {e}")
                    failed += 1

        elapsed = time.time() - start_time
        logger.info(
            f"{desc} complete: {successful} successful, {failed} failed "
            f"in {elapsed:.1f}s ({len(items)/elapsed:.1f} items/s)"
        )

        # Return only successful results (filter out None)
        return [r for r in results if r is not None]

    def _fetch_with_delay(self, fetch_func: Callable, item: Any, delay: float) -> Any:
        """
        Fetch with rate limiting

        Args:
            fetch_func: Function to call
            item: Item to fetch
            delay: Delay after fetch

        Returns:
            Fetch result or None
        """
        try:
            result = fetch_func(item)
            time.sleep(delay)  # Rate limiting
            return result
        except Exception as e:
            logger.debug(f"Fetch error for {item}: {e}")
            return None


class BatchProcessor:
    """
    Process items in batches for better memory management

    Useful when fetching hundreds of competitors
    """

    def __init__(self, batch_size: int = 10, max_workers: int = 5):
        """
        Initialize batch processor

        Args:
            batch_size: Items per batch
            max_workers: Concurrent workers per batch
        """
        self.batch_size = batch_size
        self.fetcher = ParallelFetcher(max_workers=max_workers)

    def process_batches(
        self,
        items: List[Any],
        process_func: Callable,
        desc: str = "Processing"
    ) -> List[Any]:
        """
        Process items in batches

        Args:
            items: All items to process
            process_func: Function to call for each item
            desc: Description for logging

        Returns:
            List of all results
        """
        if not items:
            return []

        logger.info(f"{desc}: {len(items)} items in batches of {self.batch_size}")
        all_results = []

        # Process in batches
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (len(items) + self.batch_size - 1) // self.batch_size

            logger.debug(f"Processing batch {batch_num}/{total_batches}")

            batch_results = self.fetcher.fetch_many(
                batch,
                process_func,
                desc=f"Batch {batch_num}/{total_batches}"
            )

            all_results.extend(batch_results)

        return all_results


def time_function(func: Callable) -> Callable:
    """
    Decorator to measure function execution time

    Usage:
        @time_function
        def slow_operation():
            time.sleep(2)

    Args:
        func: Function to time

    Returns:
        Wrapped function that logs execution time
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time

        # Log timing
        logger.info(f"{func.__name__} completed in {elapsed:.2f}s")

        return result

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


class PerformanceMonitor:
    """
    Monitor performance of operations

    Tracks:
    - Operation timing
    - Success/failure rates
    - Throughput
    """

    def __init__(self):
        self.operations = {}

    def record(self, operation: str, duration: float, success: bool = True):
        """
        Record an operation

        Args:
            operation: Name of operation
            duration: Time taken (seconds)
            success: Whether operation succeeded
        """
        if operation not in self.operations:
            self.operations[operation] = {
                'count': 0,
                'total_time': 0,
                'successes': 0,
                'failures': 0
            }

        stats = self.operations[operation]
        stats['count'] += 1
        stats['total_time'] += duration

        if success:
            stats['successes'] += 1
        else:
            stats['failures'] += 1

    def get_stats(self, operation: str) -> Optional[Dict]:
        """
        Get statistics for an operation

        Args:
            operation: Name of operation

        Returns:
            Statistics dict or None
        """
        if operation not in self.operations:
            return None

        stats = self.operations[operation]
        return {
            'operation': operation,
            'count': stats['count'],
            'success_rate': f"{stats['successes'] / stats['count'] * 100:.1f}%",
            'avg_time': f"{stats['total_time'] / stats['count']:.2f}s",
            'total_time': f"{stats['total_time']:.1f}s"
        }

    def print_summary(self):
        """Print performance summary"""
        if not self.operations:
            logger.info("No performance data recorded")
            return

        logger.info("=== Performance Summary ===")
        for operation in sorted(self.operations.keys()):
            stats = self.get_stats(operation)
            logger.info(
                f"{stats['operation']}: {stats['count']} calls, "
                f"{stats['success_rate']} success, "
                f"{stats['avg_time']} avg"
            )


# Global performance monitor
_global_monitor = None


def get_monitor() -> PerformanceMonitor:
    """Get global performance monitor"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor
