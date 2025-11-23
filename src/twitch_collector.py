#!/usr/bin/env python3
"""
Twitch Collector - Real Streaming Data and Influencer Discovery
Analyzes Twitch viewership and finds relevant streamers using Twitch Helix API
"""

from typing import Dict, List, Any, Optional
import os
import requests
import time
from src.logger import get_logger
from src.cache_manager import get_cache

logger = get_logger(__name__)


class TwitchCollector:
    """
    Collect real streaming data from Twitch Helix API
    Requires TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET environment variables
    """

    API_BASE = "https://api.twitch.tv/helix"
    AUTH_URL = "https://id.twitch.tv/oauth2/token"

    def __init__(self):
        self.cache = get_cache()
        self.client_id = os.getenv('TWITCH_CLIENT_ID')
        self.client_secret = os.getenv('TWITCH_CLIENT_SECRET')
        self.access_token = None

        if not self.client_id or not self.client_secret:
            logger.warning("Twitch API credentials not configured. Using fallback data.")
            self.api_available = False
        else:
            self.api_available = True
            logger.info("TwitchCollector initialized with API credentials")

    def _get_access_token(self) -> Optional[str]:
        """Get OAuth access token from Twitch"""
        # Check cache first - FIX: CacheManager requires (namespace, identifier)
        cached_token = self.cache.get('twitch_tokens', 'access_token')
        if cached_token:
            return cached_token

        if not self.api_available:
            return None

        try:
            response = requests.post(
                self.AUTH_URL,
                params={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'client_credentials'
                },
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            token = data.get('access_token')
            expires_in = data.get('expires_in', 3600)

            # Cache token (expires in ~60 days, default cache TTL is 24h which is fine)
            # FIX: CacheManager.set() signature is (namespace, identifier, data)
            self.cache.set('twitch_tokens', 'access_token', token)

            logger.info("Successfully obtained Twitch access token")
            return token

        except Exception as e:
            logger.error(f"Failed to get Twitch access token: {e}")
            return None

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make authenticated request to Twitch API"""
        if not self.api_available:
            return None

        token = self._get_access_token()
        if not token:
            return None

        try:
            headers = {
                'Client-ID': self.client_id,
                'Authorization': f'Bearer {token}'
            }

            response = requests.get(
                f"{self.API_BASE}/{endpoint}",
                headers=headers,
                params=params or {},
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitch API request failed: {e}")
            return None

    def search_game(self, game_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for a game on Twitch

        Args:
            game_name: Name of the game

        Returns:
            Game data including ID and viewer count
        """
        cache_key = f"game_{game_name.lower().replace(' ', '_')}"
        # FIX: CacheManager requires (namespace, identifier)
        cached = self.cache.get('twitch_games', cache_key)
        if cached:
            return cached

        result = self._make_request('games', {'name': game_name})

        if result and result.get('data'):
            game_data = result['data'][0]
            # FIX: CacheManager.set() signature is (namespace, identifier, data)
            self.cache.set('twitch_games', cache_key, game_data)
            return game_data

        return None

    def get_game_streams(self, game_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get current streams for a game

        Args:
            game_id: Twitch game ID
            limit: Maximum number of streams to return

        Returns:
            List of stream data
        """
        result = self._make_request('streams', {
            'game_id': game_id,
            'first': limit
        })

        if result and result.get('data'):
            return result['data']

        return []

    def get_streamer_info(self, user_login: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a streamer

        Args:
            user_login: Twitch username

        Returns:
            Streamer data
        """
        result = self._make_request('users', {'login': user_login})

        if result and result.get('data'):
            user_data = result['data'][0]

            # Get follower count
            user_id = user_data['id']
            followers_result = self._make_request('channels/followers', {'broadcaster_id': user_id})

            if followers_result and 'total' in followers_result:
                user_data['follower_count'] = followers_result['total']
            else:
                user_data['follower_count'] = 0

            return user_data

        return None

    def analyze_game_viewership(self, game_name: str) -> Dict[str, Any]:
        """
        Get real viewership data for a game

        Args:
            game_name: Name of the game

        Returns:
            Viewership analysis with current data
        """
        logger.info(f"Analyzing Twitch viewership for: {game_name}")

        # Try to get real data first
        game_data = self.search_game(game_name)

        if game_data:
            game_id = game_data['id']
            streams = self.get_game_streams(game_id, limit=100)

            # Calculate metrics from real stream data
            total_viewers = sum(s.get('viewer_count', 0) for s in streams)
            channel_count = len(streams)
            avg_viewers_per_channel = total_viewers // channel_count if channel_count > 0 else 0

            # Get top streamers
            top_streamers = sorted(streams, key=lambda x: x.get('viewer_count', 0), reverse=True)[:10]

            return {
                'game_name': game_name,
                'game_id': game_id,
                'current_viewers': total_viewers,
                'channel_count': channel_count,
                'avg_viewers_per_channel': avg_viewers_per_channel,
                'top_streamers': [
                    {
                        'name': s['user_name'],
                        'login': s['user_login'],
                        'current_viewers': s['viewer_count'],
                        'title': s['title']
                    }
                    for s in top_streamers
                ],
                'data_source': 'twitch_api',
                'streamability_score': self._calculate_streamability_score(total_viewers, channel_count)
            }

        # Fallback to estimated data if API unavailable
        return self._get_fallback_analysis(game_name)

    def find_streamers_for_outreach(self, genres: List[str], min_followers: int = 10000, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Find streamers who might be interested in the game

        Args:
            genres: Game genres to match
            min_followers: Minimum follower count
            max_results: Maximum streamers to return

        Returns:
            List of streamers with contact info
        """
        logger.info(f"Finding streamers for genres: {genres}")

        # Map genres to Twitch game categories
        similar_games = self._get_similar_games_by_genre(genres)

        streamers_found = {}

        for game_name in similar_games[:5]:  # Check top 5 similar games
            game_data = self.search_game(game_name)
            if not game_data:
                continue

            streams = self.get_game_streams(game_data['id'], limit=50)

            for stream in streams:
                user_login = stream['user_login']

                # Skip if already found
                if user_login in streamers_found:
                    continue

                # Get detailed user info
                user_info = self.get_streamer_info(user_login)
                if not user_info:
                    continue

                follower_count = user_info.get('follower_count', 0)

                if follower_count >= min_followers:
                    streamers_found[user_login] = {
                        'name': user_info['display_name'],
                        'login': user_login,
                        'followers': follower_count,
                        'description': user_info.get('description', ''),
                        'profile_image': user_info.get('profile_image_url', ''),
                        'twitch_url': f"https://twitch.tv/{user_login}",
                        'current_viewers': stream.get('viewer_count', 0),
                        'plays': game_name,
                        'estimated_cost': self._estimate_sponsorship_cost(follower_count),
                        'roi_score': self._calculate_roi_score(follower_count, stream.get('viewer_count', 0))
                    }

                if len(streamers_found) >= max_results:
                    break

            if len(streamers_found) >= max_results:
                break

        # Sort by ROI score
        streamers_list = list(streamers_found.values())
        streamers_list.sort(key=lambda x: x['roi_score'], reverse=True)

        # If API didn't work or not enough found, add fallback data
        if len(streamers_list) < 3:
            logger.warning("Using fallback streamer data")
            return self._get_fallback_streamers(genres, min_followers)

        return streamers_list[:max_results]

    def _calculate_streamability_score(self, viewers: int, channels: int) -> int:
        """Calculate streamability score based on viewership metrics"""
        if channels == 0:
            return 30

        avg_per_channel = viewers // channels

        # Score based on average viewers per channel
        if avg_per_channel >= 1000:
            return 95
        elif avg_per_channel >= 500:
            return 85
        elif avg_per_channel >= 100:
            return 75
        elif avg_per_channel >= 50:
            return 65
        elif avg_per_channel >= 10:
            return 50
        else:
            return 35

    def _estimate_sponsorship_cost(self, followers: int) -> str:
        """Estimate sponsorship cost based on follower count"""
        if followers >= 1000000:
            return "$2,000-5,000 per sponsored stream"
        elif followers >= 500000:
            return "$1,000-2,500 per sponsored stream"
        elif followers >= 100000:
            return "$500-1,000 per sponsored stream"
        elif followers >= 50000:
            return "$200-500 per sponsored stream"
        elif followers >= 10000:
            return "$50-200 per sponsored stream"
        else:
            return "Free key + revenue share"

    def _calculate_roi_score(self, followers: int, current_viewers: int) -> float:
        """Calculate ROI score for streamer outreach"""
        # Engagement rate
        engagement = (current_viewers / followers * 100) if followers > 0 else 0

        # Sweet spot: 10k-100k followers with good engagement
        if 10000 <= followers <= 100000 and engagement >= 3:
            return 90
        elif 100000 <= followers <= 500000 and engagement >= 2:
            return 80
        elif followers < 10000 and engagement >= 5:
            return 75
        elif followers >= 500000 and engagement >= 1:
            return 70
        else:
            return 50 + (engagement * 5)

    def _get_similar_games_by_genre(self, genres: List[str]) -> List[str]:
        """Get similar games based on genre"""
        genre_games = {
            'roguelike': ['Hades', 'Dead Cells', 'The Binding of Isaac: Rebirth', 'Slay the Spire', 'Risk of Rain 2'],
            'strategy': ['Age of Empires IV', 'Civilization VI', 'Total War', 'Stellaris', 'Europa Universalis IV'],
            'rpg': ["Baldur's Gate 3", 'Elden Ring', 'Cyberpunk 2077', 'The Witcher 3', 'Skyrim'],
            'action': ['Fortnite', 'Valorant', 'Apex Legends', 'Call of Duty', 'Overwatch 2'],
            'indie': ['Terraria', 'Stardew Valley', 'Hollow Knight', 'Celeste', 'Undertale'],
            'simulation': ['Cities: Skylines', 'Planet Zoo', 'Farming Simulator 22', 'The Sims 4'],
            'adventure': ['The Last of Us', 'Uncharted', 'Tomb Raider', 'Horizon Zero Dawn'],
            'survival': ['Rust', 'ARK: Survival Evolved', 'Valheim', 'The Forest', 'Subnautica']
        }

        # Get primary genre
        primary_genre = genres[0].lower() if genres else 'indie'

        # Find matching games
        for genre_key, games in genre_games.items():
            if genre_key in primary_genre:
                return games

        # Default to indie
        return genre_games['indie']

    def _get_fallback_analysis(self, game_name: str) -> Dict[str, Any]:
        """Fallback analysis when API is unavailable"""
        logger.warning("Using fallback Twitch analysis (API unavailable)")

        return {
            'game_name': game_name,
            'current_viewers': 0,
            'channel_count': 0,
            'streamability_score': 50,
            'data_source': 'fallback',
            'note': 'Twitch API credentials not configured. Add TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET to environment.'
        }

    def _get_fallback_streamers(self, genres: List[str], min_followers: int) -> List[Dict[str, Any]]:
        """Fallback streamer recommendations when API unavailable"""
        # Curated list of known indie-friendly streamers
        fallback_streamers = [
            {'name': 'NorthernLion', 'login': 'northernlion', 'followers': 800000, 'genre': 'roguelike'},
            {'name': 'CohhCarnage', 'login': 'cohhcarnage', 'followers': 2200000, 'genre': 'rpg'},
            {'name': 'Vinesauce', 'login': 'vinesauce', 'followers': 1100000, 'genre': 'indie'},
            {'name': 'PotatoMcWhiskey', 'login': 'potatomcwhiskey', 'followers': 180000, 'genre': 'strategy'},
            {'name': 'DanGheesling', 'login': 'dangheesling', 'followers': 650000, 'genre': 'roguelike'},
        ]

        # Filter by genre and followers
        primary_genre = genres[0].lower() if genres else 'indie'

        matches = [
            {
                **s,
                'twitch_url': f"https://twitch.tv/{s['login']}",
                'estimated_cost': self._estimate_sponsorship_cost(s['followers']),
                'roi_score': 75,
                'note': 'Fallback data - configure Twitch API for real-time data'
            }
            for s in fallback_streamers
            if s['followers'] >= min_followers and primary_genre in s['genre'].lower()
        ]

        return matches if matches else fallback_streamers[:3]


# Convenience function
def get_twitch_analysis(genres: List[str], tags: List[str], game_name: str = None) -> Dict[str, Any]:
    """
    Get complete Twitch analysis with real API data

    Args:
        genres: Game genres
        tags: Game tags
        game_name: Game name for direct lookup

    Returns:
        Complete Twitch analysis
    """
    collector = TwitchCollector()

    # Get real viewership data if game name provided
    if game_name:
        viewership = collector.analyze_game_viewership(game_name)
    else:
        viewership = {'streamability_score': 50, 'current_viewers': 0, 'channel_count': 0}

    # Find real streamers for outreach
    streamers = collector.find_streamers_for_outreach(genres, min_followers=10000, max_results=15)

    return {
        'viewership': viewership,
        'streamers': streamers,
        'summary': {
            'current_viewers': viewership.get('current_viewers', 0),
            'streamability_score': viewership.get('streamability_score', 50),
            'recommended_streamers': len(streamers),
            'data_source': viewership.get('data_source', 'unknown')
        }
    }
