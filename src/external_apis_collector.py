#!/usr/bin/env python3
"""
External APIs Collector - Integrates RAWG and IGDB data
Provides comprehensive game metadata from multiple gaming databases
"""

from typing import Dict, List, Any, Optional
from src.logger import get_logger
from src.rawg_api import RAWGApi
from src.igdb_api import IGDBApi
from src.cache_manager import get_cache

logger = get_logger(__name__)


def collect_external_game_data(game_name: str) -> Dict[str, Any]:
    """
    Collect game metadata from RAWG and IGDB APIs

    Args:
        game_name: Name of the game

    Returns:
        Combined metadata from both sources
    """
    logger.info(f"Collecting external API data for: {game_name}")

    cache = get_cache()
    cache_key = f"external_apis_{game_name.lower().replace(' ', '_')}"

    # Check cache first
    cached = cache.get(cache_key)
    if cached:
        logger.info("Using cached external API data")
        return cached

    result = {
        'rawg': None,
        'igdb': None,
        'combined_metrics': {}
    }

    # RAWG data collection
    try:
        rawg = RAWGApi()
        rawg_data = rawg.search_game(game_name)
        if rawg_data:
            result['rawg'] = rawg_data
            logger.info(f"✓ RAWG data collected: {rawg_data.get('ratings_count', 0)} ratings")
    except Exception as e:
        logger.error(f"Failed to collect RAWG data: {e}")

    # IGDB data collection
    try:
        igdb = IGDBApi()
        igdb_data = igdb.search_game(game_name)
        if igdb_data:
            result['igdb'] = igdb_data
            logger.info(f"✓ IGDB data collected: {igdb_data.get('rating_count', 0)} ratings")
    except Exception as e:
        logger.error(f"Failed to collect IGDB data: {e}")

    # Create combined metrics from both sources
    result['combined_metrics'] = _create_combined_metrics(result['rawg'], result['igdb'])

    # Cache for 24 hours
    cache.set(cache_key, result, ttl=86400)

    return result


def _create_combined_metrics(rawg_data: Optional[Dict], igdb_data: Optional[Dict]) -> Dict[str, Any]:
    """
    Combine metrics from RAWG and IGDB into unified scores

    Args:
        rawg_data: Data from RAWG API
        igdb_data: Data from IGDB API

    Returns:
        Combined metrics dictionary
    """
    metrics = {
        'community_score': None,
        'critic_score': None,
        'engagement_score': None,
        'total_ratings': 0,
        'metacritic_score': None,
        'quality_indicators': [],
        'data_sources_available': []
    }

    if rawg_data:
        metrics['data_sources_available'].append('RAWG')

        # RAWG provides community ratings (0-5 scale)
        rawg_rating = rawg_data.get('rating', 0)
        if rawg_rating > 0:
            metrics['community_score'] = rawg_rating * 20  # Convert to 0-100

        metrics['total_ratings'] += rawg_data.get('ratings_count', 0)

        # Metacritic from RAWG
        if rawg_data.get('metacritic'):
            metrics['metacritic_score'] = rawg_data['metacritic']
            metrics['critic_score'] = rawg_data['metacritic']

        # Engagement metrics
        added_count = rawg_data.get('added', 0)
        if added_count > 10000:
            metrics['quality_indicators'].append(f"{added_count:,} players have added this game")

        # Quality signals from RAWG
        signals = rawg_data.get('quality_signals', {})
        if signals.get('high_metacritic'):
            metrics['quality_indicators'].append("High Metacritic score (80+)")
        if signals.get('high_rating'):
            metrics['quality_indicators'].append("Highly rated by community (4.0+/5)")
        if signals.get('high_engagement'):
            metrics['quality_indicators'].append("Strong community engagement (1000+ ratings)")

    if igdb_data:
        metrics['data_sources_available'].append('IGDB')

        # IGDB provides both user and critic ratings
        igdb_user_rating = igdb_data.get('rating', 0)  # Already 0-5, convert to 0-100
        igdb_critic_rating = igdb_data.get('aggregated_rating', 0)  # Already 0-100

        # Average IGDB user rating with RAWG if both available
        if igdb_user_rating > 0:
            if metrics['community_score']:
                metrics['community_score'] = (metrics['community_score'] + (igdb_user_rating * 20)) / 2
            else:
                metrics['community_score'] = igdb_user_rating * 20

        # Use IGDB critic rating if RAWG metacritic not available
        if igdb_critic_rating > 0 and not metrics['critic_score']:
            metrics['critic_score'] = igdb_critic_rating

        metrics['total_ratings'] += igdb_data.get('rating_count', 0)

        # Community signals
        follows = igdb_data.get('follows', 0)
        hypes = igdb_data.get('hypes', 0)

        if follows > 1000:
            metrics['quality_indicators'].append(f"{follows:,} followers on IGDB")
        if hypes > 100:
            metrics['quality_indicators'].append(f"{hypes} hype ratings")

        # Quality signals from IGDB
        signals = igdb_data.get('quality_signals', {})
        if signals.get('high_user_rating'):
            if "Highly rated by community" not in ' '.join(metrics['quality_indicators']):
                metrics['quality_indicators'].append("Highly rated by IGDB community")
        if signals.get('high_critic_rating'):
            metrics['quality_indicators'].append("High critic score (80+)")
        if signals.get('strong_community'):
            metrics['quality_indicators'].append("Strong community following")

    # Calculate overall engagement score (0-100)
    engagement_factors = []

    if metrics['total_ratings'] > 0:
        # Logarithmic scale for ratings count
        import math
        rating_score = min(100, (math.log10(metrics['total_ratings']) / math.log10(100000)) * 100)
        engagement_factors.append(rating_score)

    if metrics['community_score']:
        engagement_factors.append(metrics['community_score'])

    if engagement_factors:
        metrics['engagement_score'] = sum(engagement_factors) / len(engagement_factors)

    return metrics


def format_external_data_for_report(external_data: Dict[str, Any]) -> str:
    """
    Format external API data for inclusion in markdown report

    Args:
        external_data: Data from collect_external_game_data()

    Returns:
        Formatted markdown text
    """
    if not external_data or not external_data.get('combined_metrics'):
        return ""

    metrics = external_data['combined_metrics']

    if not metrics.get('data_sources_available'):
        return ""

    lines = ["\n## 🎮 Community & Critic Reception\n"]

    sources = ", ".join(metrics['data_sources_available'])
    lines.append(f"**Data Sources**: {sources}\n")

    # Scores
    if metrics.get('community_score'):
        score = metrics['community_score']
        rating = "⭐⭐⭐⭐⭐" if score >= 90 else "⭐⭐⭐⭐" if score >= 75 else "⭐⭐⭐" if score >= 60 else "⭐⭐"
        lines.append(f"- **Community Score**: {score:.0f}/100 {rating}")

    if metrics.get('critic_score'):
        lines.append(f"- **Critic Score**: {metrics['critic_score']:.0f}/100")

    if metrics.get('metacritic_score'):
        lines.append(f"- **Metacritic**: {metrics['metacritic_score']}/100")

    if metrics.get('total_ratings'):
        lines.append(f"- **Total Ratings**: {metrics['total_ratings']:,}")

    if metrics.get('engagement_score'):
        lines.append(f"- **Engagement Score**: {metrics['engagement_score']:.0f}/100")

    # Quality indicators
    if metrics.get('quality_indicators'):
        lines.append("\n**Quality Indicators:**")
        for indicator in metrics['quality_indicators']:
            lines.append(f"- {indicator}")

    return "\n".join(lines)
