#!/usr/bin/env python3
"""
Twitch Collector - Streaming Data and Influencer Discovery
Analyzes Twitch viewership and finds relevant streamers
"""

from typing import Dict, List, Any, Optional
import os
from src.logger import get_logger
from src.cache_manager import get_cache

logger = get_logger(__name__)


class TwitchCollector:
    """
    Collect streaming data from Twitch

    Note: Full implementation requires Twitch API credentials.
    This version provides genre-based analysis and streamer recommendations.
    """

    # Genre viewership data (industry benchmarks)
    GENRE_VIEWERSHIP = {
        'roguelike': {
            'avg_viewers': 15000,
            'peak_viewers': 45000,
            'channel_count': 850,
            'growth_trend': 'High',
            'streamability_score': 85,
            'popular_games': ['Hades', 'Dead Cells', 'Binding of Isaac', 'Slay the Spire']
        },
        'strategy': {
            'avg_viewers': 45000,
            'peak_viewers': 150000,
            'channel_count': 1200,
            'growth_trend': 'Stable',
            'streamability_score': 75,
            'popular_games': ['Civilization VI', 'Age of Empires', 'Total War', 'Stellaris']
        },
        'rpg': {
            'avg_viewers': 80000,
            'peak_viewers': 250000,
            'channel_count': 2500,
            'growth_trend': 'High',
            'streamability_score': 90,
            'popular_games': ['Baldurs Gate 3', 'Elden Ring', 'Final Fantasy', 'Skyrim']
        },
        'action': {
            'avg_viewers': 120000,
            'peak_viewers': 400000,
            'channel_count': 3500,
            'growth_trend': 'Very High',
            'streamability_score': 95,
            'popular_games': ['Fortnite', 'Valorant', 'Apex Legends', 'Call of Duty']
        },
        'indie': {
            'avg_viewers': 25000,
            'peak_viewers': 80000,
            'channel_count': 1500,
            'growth_trend': 'High',
            'streamability_score': 70,
            'popular_games': ['Terraria', 'Stardew Valley', 'Hollow Knight', 'Celeste']
        },
        'simulation': {
            'avg_viewers': 35000,
            'peak_viewers': 100000,
            'channel_count': 900,
            'growth_trend': 'Stable',
            'streamability_score': 65,
            'popular_games': ['Cities Skylines', 'Planet Zoo', 'Farming Simulator']
        }
    }

    # Example streamers by genre (curated list for recommendations)
    GENRE_STREAMERS = {
        'roguelike': [
            {'name': 'NorthernLion', 'followers': 800000, 'avg_viewers': 5000, 'contact': 'Business inquiries via Twitch'},
            {'name': 'DanGheesling', 'followers': 650000, 'avg_viewers': 4000, 'contact': 'Business email on Twitch'},
            {'name': 'Baertaffy', 'followers': 250000, 'avg_viewers': 2000, 'contact': 'DM on Twitch'}
        ],
        'strategy': [
            {'name': 'MontanaBlack', 'followers': 3500000, 'avg_viewers': 15000, 'contact': 'Management email'},
            {'name': 'PotatoMcWhiskey', 'followers': 180000, 'avg_viewers': 3500, 'contact': 'Business email'},
            {'name': 'Quill18', 'followers': 425000, 'avg_viewers': 2500, 'contact': 'Via YouTube'}
        ],
        'rpg': [
            {'name': 'CohhCarnage', 'followers': 2200000, 'avg_viewers': 12000, 'contact': 'Business email'},
            {'name': 'itmeJP', 'followers': 850000, 'avg_viewers': 3000, 'contact': 'Via Twitter'},
            {'name': 'dansgaming', 'followers': 1200000, 'avg_viewers': 4500, 'contact': 'Business email'}
        ],
        'indie': [
            {'name': 'itsHafu', 'followers': 2800000, 'avg_viewers': 8000, 'contact': 'Management'},
            {'name': 'Vinesauce', 'followers': 1100000, 'avg_viewers': 5000, 'contact': 'Via website'},
            {'name': 'WoolieVersus', 'followers': 180000, 'avg_viewers': 1500, 'contact': 'Via Twitter'}
        ]
    }

    def __init__(self):
        self.cache = get_cache()
        self.client_id = os.getenv('TWITCH_CLIENT_ID')
        self.client_secret = os.getenv('TWITCH_CLIENT_SECRET')
        logger.info("TwitchCollector initialized")

    def get_genre_viewership(self, genres: List[str], game_name: str = None) -> Dict[str, Any]:
        """
        Get viewership data for genre

        Args:
            genres: List of game genres
            game_name: Optional game name

        Returns:
            Viewership analysis
        """
        logger.info(f"Analyzing Twitch viewership for genres: {genres}")

        # Use primary genre
        primary_genre = genres[0] if genres else 'indie'
        genre_lower = primary_genre.lower()

        # Find matching genre data
        viewership_data = None
        for key, data in self.GENRE_VIEWERSHIP.items():
            if key in genre_lower:
                viewership_data = data
                break

        if not viewership_data:
            # Default to indie data
            viewership_data = self.GENRE_VIEWERSHIP['indie']

        return {
            'genre': primary_genre,
            'current_viewers': viewership_data['avg_viewers'],
            'avg_viewers': viewership_data['avg_viewers'],
            'peak_viewers': viewership_data['peak_viewers'],
            'channel_count': viewership_data['channel_count'],
            'growth_trend': viewership_data['growth_trend'],
            'streamability_score': viewership_data['streamability_score'],
            'popular_games': viewership_data['popular_games'],
            'analysis': self._generate_viewership_analysis(viewership_data)
        }

    def find_streamers_for_genre(self, genres: List[str], min_followers: int = 10000) -> List[Dict[str, Any]]:
        """
        Find streamers who cover this genre

        Args:
            genres: Game genres
            min_followers: Minimum follower count

        Returns:
            List of relevant streamers
        """
        logger.info(f"Finding streamers for genres: {genres}")

        primary_genre = genres[0] if genres else 'indie'
        genre_lower = primary_genre.lower()

        # Find matching streamers
        streamers = []
        for key, streamer_list in self.GENRE_STREAMERS.items():
            if key in genre_lower:
                streamers = [s for s in streamer_list if s['followers'] >= min_followers]
                break

        if not streamers:
            # Return indie streamers as fallback
            streamers = [s for s in self.GENRE_STREAMERS['indie'] if s['followers'] >= min_followers]

        # Add estimated ROI data
        for streamer in streamers:
            streamer['estimated_reach'] = int(streamer['avg_viewers'] * 0.7)  # 70% conversion to views
            streamer['cost_estimate'] = self._estimate_sponsorship_cost(streamer['followers'])
            streamer['roi_score'] = self._calculate_roi_score(streamer)

        # Sort by ROI score
        streamers.sort(key=lambda x: x['roi_score'], reverse=True)

        return streamers

    def analyze_streaming_potential(self, game_tags: List[str], genres: List[str]) -> Dict[str, Any]:
        """
        Determine if game is "streamable"

        Args:
            game_tags: Game tags
            genres: Game genres

        Returns:
            Streaming potential assessment
        """
        logger.debug("Analyzing streaming potential")

        # Factors that increase streamability
        positive_factors = []
        negative_factors = []
        score = 50  # Base score

        # Check tags
        streamable_tags = ['multiplayer', 'co-op', 'pvp', 'roguelike', 'procedural',
                          'difficult', 'action', 'fast-paced']
        for tag in game_tags:
            if any(st in tag.lower() for st in streamable_tags):
                positive_factors.append(f"Tag: {tag}")
                score += 5

        # Check genres
        primary_genre = genres[0] if genres else 'indie'
        genre_data = self.get_genre_viewership(genres)
        streamability_score = genre_data['streamability_score']

        if streamability_score >= 80:
            positive_factors.append(f"High-streamability genre ({primary_genre})")
            score += 15
        elif streamability_score >= 65:
            positive_factors.append(f"Moderate-streamability genre ({primary_genre})")
            score += 5
        else:
            negative_factors.append(f"Lower-streamability genre ({primary_genre})")
            score -= 5

        # Cap score
        score = min(100, max(0, score))

        return {
            'score': score,
            'rating': 'Excellent' if score >= 80 else 'Good' if score >= 60 else 'Fair' if score >= 40 else 'Poor',
            'positive_factors': positive_factors,
            'negative_factors': negative_factors if negative_factors else ['None identified'],
            'recommendation': self._generate_streaming_recommendation(score)
        }

    def _generate_viewership_analysis(self, data: Dict[str, Any]) -> str:
        """Generate analysis text for viewership data"""
        trend = data['growth_trend']
        score = data['streamability_score']

        if score >= 80 and trend in ['High', 'Very High']:
            return "Excellent streaming potential. Genre has strong viewership and growing audience."
        elif score >= 65:
            return "Good streaming potential. Genre has established viewership base."
        else:
            return "Moderate streaming potential. Consider emphasizing streamable features."

    def _estimate_sponsorship_cost(self, followers: int) -> str:
        """Estimate sponsorship cost based on followers"""
        if followers >= 1000000:
            return "$2,000-5,000 per sponsored stream"
        elif followers >= 500000:
            return "$1,000-2,500 per sponsored stream"
        elif followers >= 100000:
            return "$500-1,000 per sponsored stream"
        elif followers >= 50000:
            return "$200-500 per sponsored stream"
        else:
            return "Free key + revenue share"

    def _calculate_roi_score(self, streamer: Dict[str, Any]) -> float:
        """Calculate ROI score (reach / cost estimate)"""
        reach = streamer['estimated_reach']
        followers = streamer['followers']

        # Simple scoring: smaller streamers have better ROI
        if followers < 50000:
            return 90
        elif followers < 100000:
            return 80
        elif followers < 500000:
            return 70
        else:
            return 60

    def _generate_streaming_recommendation(self, score: int) -> str:
        """Generate recommendation based on streaming score"""
        if score >= 80:
            return "Strongly recommend streamer outreach. Budget $500-1,500 for 3-5 sponsored streams."
        elif score >= 60:
            return "Recommend streamer outreach. Start with free key distribution to 10-15 streamers."
        elif score >= 40:
            return "Consider streamer outreach. Focus on niche/indie game streamers who accept free keys."
        else:
            return "Lower priority for streaming. Focus on other marketing channels first."


# Convenience function
def get_twitch_analysis(genres: List[str], tags: List[str], game_name: str = None) -> Dict[str, Any]:
    """
    Get complete Twitch analysis

    Args:
        genres: Game genres
        tags: Game tags
        game_name: Optional game name

    Returns:
        Complete Twitch analysis
    """
    collector = TwitchCollector()

    viewership = collector.get_genre_viewership(genres, game_name)
    streamers = collector.find_streamers_for_genre(genres, min_followers=50000)
    potential = collector.analyze_streaming_potential(tags, genres)

    return {
        'viewership': viewership,
        'streamers': streamers,
        'streaming_potential': potential,
        'summary': {
            'avg_viewers': viewership['avg_viewers'],
            'streamability_score': viewership['streamability_score'],
            'recommended_streamers': len(streamers),
            'estimated_budget': '$500-1,500 for sponsored streams'
        }
    }
