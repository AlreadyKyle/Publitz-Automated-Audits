#!/usr/bin/env python3
"""
Data Collection Pipeline - Orchestrates Parallel Data Fetching
Manages collection from multiple sources with error handling
"""

from typing import Dict, List, Any, Optional
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.logger import get_logger
from src.cache_manager import get_cache

logger = get_logger(__name__)


class DataCollector:
    """Orchestrate parallel data collection from multiple sources"""

    def __init__(self, max_workers: int = 5):
        """
        Initialize data collector

        Args:
            max_workers: Maximum parallel collection tasks
        """
        self.max_workers = max_workers
        self.cache = get_cache()
        logger.info(f"DataCollector initialized with {max_workers} workers")

    def collect_all(self, app_id: int, game_name: str, game_data: Dict[str, Any],
                   competitor_ids: List[int] = None) -> Dict[str, Any]:
        """
        Collect all data in parallel

        Args:
            app_id: Steam app ID
            game_name: Game name
            game_data: Initial game data from Steam
            competitor_ids: List of competitor app IDs

        Returns:
            Dict with all collected data
        """
        logger.info(f"Starting parallel data collection for {game_name} ({app_id})")
        start_time = time.time()

        results = {
            'steam_data': game_data,
            'sales_data': None,
            'competitor_data': [],
            'social_data': {},
            'influencer_data': {},
            'errors': []
        }

        # Define collection tasks
        tasks = []

        # Task 1: Sales/market data (SteamDB, SteamSpy)
        tasks.append(('sales', app_id, game_name))

        # Task 2: Competitor data (if provided)
        if competitor_ids:
            for comp_id in competitor_ids[:10]:  # Limit to 10 competitors
                tasks.append(('competitor', comp_id, None))

        # Task 3: Social data (future: Reddit, Twitter)
        # tasks.append(('social', app_id, game_name))

        # Task 4: Influencer data (future: YouTube, Twitch, Curators)
        # tasks.append(('influencer', app_id, game_name))

        # Execute tasks in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {
                executor.submit(self._collect_task, task_type, identifier, name): (task_type, identifier)
                for task_type, identifier, name in tasks
            }

            for future in as_completed(future_to_task):
                task_type, identifier = future_to_task[future]
                try:
                    result = future.result()
                    if result:
                        if task_type == 'sales':
                            results['sales_data'] = result
                        elif task_type == 'competitor':
                            results['competitor_data'].append(result)
                        elif task_type == 'social':
                            results['social_data'].update(result)
                        elif task_type == 'influencer':
                            results['influencer_data'].update(result)

                    logger.debug(f"Task {task_type} for {identifier} completed")

                except Exception as e:
                    error_msg = f"{task_type} collection failed for {identifier}: {str(e)}"
                    logger.warning(error_msg)
                    results['errors'].append(error_msg)

        elapsed = time.time() - start_time
        logger.info(f"Data collection completed in {elapsed:.2f}s. Errors: {len(results['errors'])}")

        return results

    def _collect_task(self, task_type: str, identifier: Any, name: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Execute a single collection task

        Args:
            task_type: Type of data to collect
            identifier: ID or identifier for the resource
            name: Optional name for logging

        Returns:
            Collected data or None if failed
        """
        # Check cache first
        cache_key = f"{task_type}_{identifier}"
        cached = self.cache.get(f"pipeline_{task_type}", identifier)
        if cached:
            logger.debug(f"Cache hit for {cache_key}")
            return cached

        # Collect data based on task type
        try:
            if task_type == 'sales':
                result = self._collect_sales_data(identifier, name)
            elif task_type == 'competitor':
                result = self._collect_competitor_data(identifier)
            elif task_type == 'social':
                result = self._collect_social_data(identifier, name)
            elif task_type == 'influencer':
                result = self._collect_influencer_data(identifier, name)
            else:
                logger.warning(f"Unknown task type: {task_type}")
                return None

            # Cache successful result
            if result:
                self.cache.set(f"pipeline_{task_type}", identifier, result)

            return result

        except Exception as e:
            logger.error(f"Task {task_type} failed for {identifier}: {e}")
            return None

    def _collect_sales_data(self, app_id: int, game_name: Optional[str]) -> Optional[Dict[str, Any]]:
        """Collect sales/market data"""
        logger.debug(f"Collecting sales data for app {app_id}")

        try:
            from src.steamdb_scraper import SteamDBScraper
            scraper = SteamDBScraper()
            return scraper.get_sales_data(app_id, game_name)
        except Exception as e:
            logger.error(f"Sales data collection failed: {e}")
            return None

    def _collect_competitor_data(self, app_id: int) -> Optional[Dict[str, Any]]:
        """Collect competitor game data"""
        logger.debug(f"Collecting competitor data for app {app_id}")

        try:
            from src.game_search import GameSearch
            game_search = GameSearch()
            return game_search.get_game_details(app_id)
        except Exception as e:
            logger.error(f"Competitor data collection failed for {app_id}: {e}")
            return None

    def _collect_social_data(self, app_id: int, game_name: str) -> Dict[str, Any]:
        """
        Collect social media data

        Future implementation:
        - Reddit: Find relevant subreddits, sentiment
        - Twitter: Trend data, mentions
        """
        logger.debug(f"Collecting social data for {game_name}")

        # Placeholder for future implementation
        return {
            'reddit': {},
            'twitter': {}
        }

    def _collect_influencer_data(self, app_id: int, game_name: str) -> Dict[str, Any]:
        """
        Collect influencer/creator data

        Future implementation:
        - YouTube: Relevant channels, view counts
        - Twitch: Streamers, viewership
        - Steam Curators: Relevant curators
        """
        logger.debug(f"Collecting influencer data for {game_name}")

        # Placeholder for future implementation
        return {
            'youtube': {},
            'twitch': {},
            'curators': []
        }


class EnhancedDataCollector(DataCollector):
    """
    Extended data collector with additional sources

    This will be implemented in Phase 2 with:
    - Reddit API integration
    - Twitch API integration
    - YouTube enhanced analysis
    - Steam curator discovery
    """

    def __init__(self, max_workers: int = 5):
        super().__init__(max_workers)
        logger.info("EnhancedDataCollector initialized (Phase 2 features)")

    def collect_all_enhanced(self, app_id: int, game_name: str, game_data: Dict[str, Any],
                           competitor_ids: List[int] = None) -> Dict[str, Any]:
        """
        Collect all data including Phase 2 enhancements

        Phase 2 will add:
        - Reddit community analysis
        - Twitch viewership data
        - YouTube channel recommendations
        - Steam curator contacts
        - Regional pricing analysis
        """
        # Start with base collection
        results = self.collect_all(app_id, game_name, game_data, competitor_ids)

        # Phase 2: Add enhanced collections here
        logger.info("Enhanced data collection will be implemented in Phase 2")

        return results


# Convenience function
def collect_game_data(app_id: int, game_name: str, game_data: Dict[str, Any],
                     competitor_ids: List[int] = None) -> Dict[str, Any]:
    """
    Convenience function for data collection

    Args:
        app_id: Steam app ID
        game_name: Game name
        game_data: Initial game data
        competitor_ids: Optional list of competitor IDs

    Returns:
        Dict with all collected data
    """
    collector = DataCollector()
    return collector.collect_all(app_id, game_name, game_data, competitor_ids)
