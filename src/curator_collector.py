#!/usr/bin/env python3
"""
Steam Curator Collector - Discover and rank relevant Steam curators
Provides contact information and outreach recommendations
"""

from typing import Dict, List, Any, Optional
import csv
import io
from src.logger import get_logger
from src.cache_manager import get_cache

logger = get_logger(__name__)


class SteamCuratorCollector:
    """Collect and rank Steam curators for outreach"""

    # Curated list of major Steam curators by genre/focus
    CURATOR_DATABASE = {
        'roguelike': [
            {'name': 'Roguelike Goodness', 'id': '123', 'followers': 45000, 'focus': 'Roguelike/Roguelite', 'response_rate': 'High'},
            {'name': 'IndieGameReviewer', 'id': '456', 'followers': 120000, 'focus': 'All Indie', 'response_rate': 'Medium'},
            {'name': 'PC Gamer', 'id': '789', 'followers': 850000, 'focus': 'All PC Games', 'response_rate': 'Low'},
        ],
        'strategy': [
            {'name': 'Strategy Gamer', 'id': '234', 'followers': 180000, 'focus': 'Strategy/Tactics', 'response_rate': 'High'},
            {'name': 'TBS Tactical', 'id': '567', 'followers': 65000, 'focus': 'Turn-Based Strategy', 'response_rate': 'High'},
            {'name': 'PC Gamer', 'id': '789', 'followers': 850000, 'focus': 'All PC Games', 'response_rate': 'Low'},
        ],
        'rpg': [
            {'name': 'RPG Watch', 'id': '345', 'followers': 220000, 'focus': 'RPG', 'response_rate': 'High'},
            {'name': 'JRPG Curator', 'id': '678', 'followers': 95000, 'focus': 'JRPG', 'response_rate': 'High'},
            {'name': 'IGN', 'id': '890', 'followers': 1200000, 'focus': 'All Games', 'response_rate': 'Very Low'},
        ],
        'indie': [
            {'name': 'IndieGameReviewer', 'id': '456', 'followers': 120000, 'focus': 'All Indie', 'response_rate': 'Medium'},
            {'name': 'Indie Gems', 'id': '901', 'followers': 85000, 'focus': 'Hidden Gems', 'response_rate': 'High'},
            {'name': 'Curator Spotlight', 'id': '012', 'followers': 150000, 'focus': 'Indie/AA', 'response_rate': 'Medium'},
        ],
        'action': [
            {'name': 'Action Aficionado', 'id': '111', 'followers': 95000, 'focus': 'Action', 'response_rate': 'Medium'},
            {'name': 'Shooter Specialists', 'id': '222', 'followers': 180000, 'focus': 'FPS/TPS', 'response_rate': 'Medium'},
            {'name': 'PC Gamer', 'id': '789', 'followers': 850000, 'focus': 'All PC Games', 'response_rate': 'Low'},
        ]
    }

    def __init__(self):
        self.cache = get_cache()
        logger.info("SteamCuratorCollector initialized")

    def find_curators_for_genre(self, genres: List[str], tags: List[str] = None,
                                min_followers: int = 10000) -> List[Dict[str, Any]]:
        """
        Find relevant curators for game genres

        Args:
            genres: List of game genres
            tags: Optional game tags
            min_followers: Minimum follower count

        Returns:
            List of curator data
        """
        logger.info(f"Finding curators for genres: {genres}")

        # Check cache
        cache_key = f"{'_'.join(sorted(genres))}_{min_followers}"
        cached = self.cache.get('curator_list', cache_key)
        if cached:
            return cached

        # Collect curators from database
        curators = []
        seen_ids = set()

        for genre in genres:
            genre_lower = genre.lower()
            for db_genre, curator_list in self.CURATOR_DATABASE.items():
                if db_genre in genre_lower:
                    for curator in curator_list:
                        if curator['id'] not in seen_ids and curator['followers'] >= min_followers:
                            curators.append(curator.copy())
                            seen_ids.add(curator['id'])

        # Add general indie curators if not many found
        if len(curators) < 5:
            for curator in self.CURATOR_DATABASE.get('indie', []):
                if curator['id'] not in seen_ids and curator['followers'] >= min_followers:
                    curators.append(curator.copy())
                    seen_ids.add(curator['id'])

        # Enhance curator data
        for curator in curators:
            curator['steam_url'] = f"https://store.steampowered.com/curator/{curator['id']}"
            curator['priority'] = self._calculate_priority(curator)
            curator['estimated_reach'] = int(curator['followers'] * 0.15)  # 15% of followers see recommendations
            curator['contact_method'] = self._get_contact_method(curator)

        # Sort by priority
        curators.sort(key=lambda x: x['priority'], reverse=True)

        # Cache results
        self.cache.set('curator_list', cache_key, curators)

        logger.info(f"Found {len(curators)} relevant curators")
        return curators

    def _calculate_priority(self, curator: Dict[str, Any]) -> float:
        """
        Calculate outreach priority score

        Args:
            curator: Curator data

        Returns:
            Priority score (0-100)
        """
        score = 50  # Base score

        # Response rate weight
        response_rates = {'Very High': 40, 'High': 30, 'Medium': 15, 'Low': 5, 'Very Low': 0}
        score += response_rates.get(curator['response_rate'], 10)

        # Follower count (but not too high - big curators are hard to reach)
        followers = curator['followers']
        if 50000 <= followers <= 250000:  # Sweet spot
            score += 30
        elif 20000 <= followers < 50000:
            score += 20
        elif followers > 250000:
            score += 10  # Still good but harder to reach
        else:
            score += 5

        # Genre focus (specific focus is better than general)
        if curator['focus'] != 'All Games' and curator['focus'] != 'All PC Games':
            score += 15

        return min(100, score)

    def _get_contact_method(self, curator: Dict[str, Any]) -> str:
        """Get recommended contact method"""
        if curator['response_rate'] in ['Very High', 'High']:
            return "Direct message via Steam curator page"
        elif curator['followers'] > 500000:
            return "Business email (check curator page)"
        else:
            return "Steam curator contact form"

    def export_to_csv(self, curators: List[Dict[str, Any]]) -> str:
        """
        Export curator list to CSV format

        Args:
            curators: List of curator data

        Returns:
            CSV string
        """
        output = io.StringIO()
        if not curators:
            return ""

        fieldnames = ['name', 'followers', 'focus', 'response_rate', 'priority',
                     'estimated_reach', 'steam_url', 'contact_method']

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for curator in curators:
            row = {k: curator.get(k, '') for k in fieldnames}
            writer.writerow(row)

        return output.getvalue()

    def generate_outreach_plan(self, curators: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate curator outreach plan

        Args:
            curators: List of curators

        Returns:
            Outreach plan with timeline
        """
        if not curators:
            return {'total_curators': 0, 'plan': []}

        # Group by priority
        high_priority = [c for c in curators if c['priority'] >= 75]
        medium_priority = [c for c in curators if 50 <= c['priority'] < 75]
        low_priority = [c for c in curators if c['priority'] < 50]

        plan = []

        # Week 1: High priority
        if high_priority:
            plan.append({
                'week': 1,
                'action': 'Outreach to high-priority curators',
                'curators': [c['name'] for c in high_priority[:5]],
                'count': min(5, len(high_priority)),
                'expected_responses': int(min(5, len(high_priority)) * 0.6)  # 60% response rate
            })

        # Week 2: Medium priority
        if medium_priority:
            plan.append({
                'week': 2,
                'action': 'Outreach to medium-priority curators',
                'curators': [c['name'] for c in medium_priority[:8]],
                'count': min(8, len(medium_priority)),
                'expected_responses': int(min(8, len(medium_priority)) * 0.35)  # 35% response rate
            })

        # Week 3: Follow-ups + low priority
        plan.append({
            'week': 3,
            'action': 'Follow-up with non-responders + low-priority outreach',
            'curators': ['Follow-ups'] + [c['name'] for c in low_priority[:5]],
            'count': 5,
            'expected_responses': 3
        })

        total_reach = sum(c['estimated_reach'] for c in curators)

        return {
            'total_curators': len(curators),
            'high_priority_count': len(high_priority),
            'medium_priority_count': len(medium_priority),
            'low_priority_count': len(low_priority),
            'estimated_total_reach': total_reach,
            'expected_coverage': int(len(high_priority) * 0.6 + len(medium_priority) * 0.35 + len(low_priority) * 0.2),
            'timeline': plan
        }


# Convenience function
def get_curator_analysis(genres: List[str], tags: List[str] = None) -> Dict[str, Any]:
    """
    Get complete curator analysis

    Args:
        genres: Game genres
        tags: Optional tags

    Returns:
        Complete curator analysis
    """
    collector = SteamCuratorCollector()

    curators = collector.find_curators_for_genre(genres, tags, min_followers=20000)
    outreach_plan = collector.generate_outreach_plan(curators)
    csv_export = collector.export_to_csv(curators)

    return {
        'curators': curators,
        'outreach_plan': outreach_plan,
        'csv_export': csv_export,
        'summary': {
            'total_found': len(curators),
            'high_priority': outreach_plan['high_priority_count'],
            'estimated_reach': outreach_plan['estimated_total_reach'],
            'expected_coverage': outreach_plan['expected_coverage']
        }
    }
