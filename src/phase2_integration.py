#!/usr/bin/env python3
"""
Phase 2 Integration - Orchestrates collection of community, influencer, and global reach data
Collects data from Reddit, Twitch, YouTube, Steam Curators, and Regional Pricing analyzers
"""

from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.logger import get_logger
from src.reddit_collector import get_reddit_analysis
from src.twitch_collector import get_twitch_analysis
from src.curator_collector import get_curator_analysis
from src.youtube_api import get_youtube_outreach_analysis
from src.regional_pricing import get_regional_pricing_analysis

logger = get_logger(__name__)


class Phase2DataCollector:
    """Collects all Phase 2 enrichment data in parallel"""

    def __init__(self):
        logger.info("Phase2DataCollector initialized")

    def collect_all_data(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect all Phase 2 data in parallel

        Args:
            game_data: Game information from Steam

        Returns:
            Dict containing all Phase 2 data: {
                'reddit': {...},
                'twitch': {...},
                'youtube': {...},
                'curators': {...},
                'regional_pricing': {...},
                'localization': {...}
            }
        """
        logger.info("Collecting Phase 2 enrichment data in parallel")

        # Extract game info
        game_name = game_data.get('name', 'Unknown Game')
        genres = [g.get('description', '') for g in game_data.get('genres', [])]
        tags = game_data.get('tags', [])
        base_price = game_data.get('price_overview', {}).get('final', 1999) / 100  # Convert to dollars
        supported_languages = game_data.get('supported_languages', [])

        # Parse supported languages (simplified - just check if common languages exist)
        current_languages = ['en']  # Always assume English
        if 'chinese' in str(supported_languages).lower():
            current_languages.append('zh-CN')
        if 'japanese' in str(supported_languages).lower():
            current_languages.append('ja')
        if 'korean' in str(supported_languages).lower():
            current_languages.append('ko')
        if 'german' in str(supported_languages).lower():
            current_languages.append('de')
        if 'french' in str(supported_languages).lower():
            current_languages.append('fr')
        if 'spanish' in str(supported_languages).lower():
            current_languages.append('es')

        # Define collection tasks
        tasks = {}

        with ThreadPoolExecutor(max_workers=5) as executor:
            # Reddit analysis
            tasks['reddit'] = executor.submit(
                self._safe_collect,
                'Reddit',
                lambda: get_reddit_analysis(genres, tags)
            )

            # Twitch analysis
            tasks['twitch'] = executor.submit(
                self._safe_collect,
                'Twitch',
                lambda: get_twitch_analysis(genres, tags)
            )

            # YouTube analysis
            tasks['youtube'] = executor.submit(
                self._safe_collect,
                'YouTube',
                lambda: get_youtube_outreach_analysis(game_name, genres)
            )

            # Steam Curators
            tasks['curators'] = executor.submit(
                self._safe_collect,
                'Steam Curators',
                lambda: get_curator_analysis(genres, tags)
            )

            # Regional Pricing & Localization
            tasks['pricing'] = executor.submit(
                self._safe_collect,
                'Regional Pricing',
                lambda: get_regional_pricing_analysis(base_price, current_languages)
            )

            # Collect results
            results = {}
            for name, future in tasks.items():
                try:
                    results[name] = future.result(timeout=30)
                except Exception as e:
                    logger.error(f"Failed to collect {name} data: {e}")
                    results[name] = {}

        # Structure the data
        phase2_data = {
            'reddit': results.get('reddit', {}),
            'twitch': results.get('twitch', {}),
            'youtube': results.get('youtube', {}),
            'curators': results.get('curators', {}),
            'regional_pricing': results.get('pricing', {}).get('pricing', {}),
            'localization': results.get('pricing', {}).get('localization', {})
        }

        logger.info("Phase 2 data collection complete")

        return phase2_data

    def _safe_collect(self, source_name: str, collect_func):
        """Safely execute collection function with error handling"""
        try:
            logger.info(f"Collecting {source_name} data...")
            result = collect_func()
            logger.info(f"✓ {source_name} data collected")
            return result
        except Exception as e:
            logger.error(f"✗ {source_name} data collection failed: {e}")
            return {}


# Convenience function
def collect_phase2_data(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Collect all Phase 2 enrichment data

    Args:
        game_data: Game information from Steam

    Returns:
        Complete Phase 2 data
    """
    collector = Phase2DataCollector()
    return collector.collect_all_data(game_data)
