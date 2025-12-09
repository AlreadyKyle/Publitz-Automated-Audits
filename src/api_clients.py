"""
API Clients for External Data Sources

Integrates multiple free APIs to enhance audit report quality:
- SteamSpy: Owner estimates and player data
- RAWG: Metacritic scores and ratings
- YouTube: Video counts and buzz metrics
- Enhanced Steam Web API: Richer game data
"""

import requests
import time
from typing import Dict, List, Any, Optional


class SteamSpyClient:
    """
    Fetch owner estimates and player data from SteamSpy.

    API: https://steamspy.com/api.php
    No API key required (free public API)
    """

    BASE_URL = "https://steamspy.com/api.php"

    def __init__(self):
        """Initialize SteamSpy client."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Publitz Audit System 1.0'
        })

    def get_game_data(self, app_id: str) -> Dict[str, Any]:
        """
        Get comprehensive game data from SteamSpy.

        Returns:
            - owners: Owner estimate range (e.g., "100,000 .. 200,000")
            - players_forever: Total players who own the game
            - average_forever: Average playtime (minutes)
            - median_forever: Median playtime (minutes)
            - ccu: Current concurrent users
        """
        try:
            params = {
                'request': 'appdetails',
                'appid': app_id
            }

            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                # Check if we got valid data
                if data and 'name' in data:
                    return {
                        'found': True,
                        'name': data.get('name', ''),
                        'owners': data.get('owners', '0 .. 0'),
                        'owners_variance': data.get('owners_variance', 0),
                        'players_forever': data.get('players_forever', 0),
                        'average_playtime': data.get('average_forever', 0),  # minutes
                        'median_playtime': data.get('median_forever', 0),  # minutes
                        'ccu': data.get('ccu', 0),
                        'price': data.get('price', 0) / 100 if data.get('price') else 0,  # Convert cents to dollars
                        'positive': data.get('positive', 0),
                        'negative': data.get('negative', 0),
                        'score_rank': data.get('score_rank', ''),
                        'userscore': data.get('userscore', 0)
                    }

        except Exception as e:
            print(f"⚠️  SteamSpy error for app {app_id}: {e}")

        return {'found': False}

    def parse_owner_range(self, owners_string: str) -> tuple:
        """
        Parse owner range string like "100,000 .. 200,000" to (min, max).

        Returns:
            (min_owners, max_owners) as integers
        """
        try:
            parts = owners_string.replace(',', '').split('..')
            min_owners = int(parts[0].strip())
            max_owners = int(parts[1].strip()) if len(parts) > 1 else min_owners
            return (min_owners, max_owners)
        except:
            return (0, 0)

    def get_owner_estimate_midpoint(self, owners_string: str) -> int:
        """Get midpoint of owner range for comparison purposes."""
        min_owners, max_owners = self.parse_owner_range(owners_string)
        return (min_owners + max_owners) // 2


class RAWGClient:
    """
    Fetch game ratings and Metacritic scores from RAWG.

    API: https://api.rawg.io/api/
    API Key required (free tier available)
    """

    BASE_URL = "https://api.rawg.io/api"

    def __init__(self, api_key: str):
        """Initialize RAWG client with API key."""
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Publitz Audit System 1.0'
        })

    def search_game(self, game_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for game by name and return best match.

        Returns game data including Metacritic score, ratings, etc.
        """
        try:
            params = {
                'key': self.api_key,
                'search': game_name,
                'page_size': 5
            }

            response = self.session.get(
                f"{self.BASE_URL}/games",
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])

                if results:
                    # Return first result (best match)
                    game = results[0]
                    return self._parse_game_data(game)

        except Exception as e:
            print(f"⚠️  RAWG search error for '{game_name}': {e}")

        return None

    def get_game_details(self, game_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed game information by RAWG game ID."""
        try:
            params = {'key': self.api_key}

            response = self.session.get(
                f"{self.BASE_URL}/games/{game_id}",
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                game = response.json()
                return self._parse_game_data(game)

        except Exception as e:
            print(f"⚠️  RAWG details error for game {game_id}: {e}")

        return None

    def _parse_game_data(self, game: Dict[str, Any]) -> Dict[str, Any]:
        """Parse RAWG game data into consistent format."""
        return {
            'found': True,
            'rawg_id': game.get('id'),
            'name': game.get('name', ''),
            'metacritic': game.get('metacritic'),  # Metacritic score (0-100)
            'rating': game.get('rating', 0),  # RAWG rating (0-5)
            'rating_top': game.get('rating_top', 5),
            'ratings_count': game.get('ratings_count', 0),
            'reviews_count': game.get('reviews_text_count', 0),
            'added': game.get('added', 0),  # Users who added to library
            'playtime': game.get('playtime', 0),  # Average playtime (hours)
            'esrb_rating': game.get('esrb_rating', {}).get('name', 'Not Rated'),
            'released': game.get('released', ''),
            'platforms': [p.get('platform', {}).get('name', '') for p in game.get('platforms', [])],
            'genres': [g.get('name', '') for g in game.get('genres', [])],
            'tags': [t.get('name', '') for t in game.get('tags', [])][:10],  # Top 10 tags
            'website': game.get('website', ''),
            'reddit_url': game.get('reddit_url', ''),
            'metacritic_url': game.get('metacritic_url', '')
        }


class YouTubeClient:
    """
    Fetch video counts and view data from YouTube Data API.

    API: https://www.googleapis.com/youtube/v3/
    API Key required (free tier: 10,000 units/day)
    """

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str):
        """Initialize YouTube client with API key."""
        self.api_key = api_key
        self.session = requests.Session()

    def search_game_videos(self, game_name: str, max_results: int = 50) -> Dict[str, Any]:
        """
        Search for videos about the game and return aggregated statistics.

        Returns:
            - video_count: Number of videos found
            - total_views: Estimated total views across videos
            - recent_videos: Count of videos in last 30 days
            - top_channels: Most active channels covering the game
        """
        try:
            # Search for videos
            search_params = {
                'key': self.api_key,
                'q': game_name,
                'part': 'id,snippet',
                'type': 'video',
                'maxResults': max_results,
                'order': 'relevance'
            }

            response = self.session.get(
                f"{self.BASE_URL}/search",
                params=search_params,
                timeout=10
            )

            if response.status_code != 200:
                return {'found': False, 'error': f"API error: {response.status_code}"}

            data = response.json()
            items = data.get('items', [])

            if not items:
                return {
                    'found': True,
                    'video_count': 0,
                    'total_views': 0,
                    'message': 'No videos found'
                }

            # Get video IDs
            video_ids = [item['id']['videoId'] for item in items if 'videoId' in item['id']]

            # Get video statistics
            stats = self._get_video_statistics(video_ids)

            return {
                'found': True,
                'video_count': len(video_ids),
                'total_views': stats['total_views'],
                'total_likes': stats['total_likes'],
                'total_comments': stats['total_comments'],
                'average_views': stats['average_views'],
                'top_video_views': stats['top_video_views'],
                'top_video_title': stats['top_video_title']
            }

        except Exception as e:
            print(f"⚠️  YouTube search error for '{game_name}': {e}")
            return {'found': False, 'error': str(e)}

    def _get_video_statistics(self, video_ids: List[str]) -> Dict[str, Any]:
        """Get detailed statistics for a list of video IDs."""
        try:
            # YouTube API allows up to 50 IDs per request
            video_ids_str = ','.join(video_ids[:50])

            params = {
                'key': self.api_key,
                'id': video_ids_str,
                'part': 'statistics,snippet'
            }

            response = self.session.get(
                f"{self.BASE_URL}/videos",
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])

                total_views = 0
                total_likes = 0
                total_comments = 0
                top_views = 0
                top_title = ''

                for item in items:
                    stats = item.get('statistics', {})
                    views = int(stats.get('viewCount', 0))
                    likes = int(stats.get('likeCount', 0))
                    comments = int(stats.get('commentCount', 0))

                    total_views += views
                    total_likes += likes
                    total_comments += comments

                    if views > top_views:
                        top_views = views
                        top_title = item.get('snippet', {}).get('title', '')

                return {
                    'total_views': total_views,
                    'total_likes': total_likes,
                    'total_comments': total_comments,
                    'average_views': total_views // len(items) if items else 0,
                    'top_video_views': top_views,
                    'top_video_title': top_title
                }

        except Exception as e:
            print(f"⚠️  YouTube stats error: {e}")

        return {
            'total_views': 0,
            'total_likes': 0,
            'total_comments': 0,
            'average_views': 0,
            'top_video_views': 0,
            'top_video_title': ''
        }


class EnhancedSteamClient:
    """
    Enhanced Steam Web API client for richer game data.

    Uses Steam Web API instead of basic Store API for:
    - Real-time player counts
    - Review sentiment analysis
    - News and announcements
    - More detailed stats
    """

    BASE_URL = "https://api.steampowered.com"
    STORE_API = "https://store.steampowered.com/api"

    def __init__(self, api_key: str):
        """Initialize Steam Web API client."""
        self.api_key = api_key
        self.session = requests.Session()

    def get_player_count(self, app_id: str) -> int:
        """Get current concurrent player count."""
        try:
            params = {
                'key': self.api_key,
                'appid': app_id
            }

            response = self.session.get(
                f"{self.BASE_URL}/ISteamUserStats/GetNumberOfCurrentPlayers/v1/",
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('response', {}).get('player_count', 0)

        except Exception as e:
            print(f"⚠️  Steam player count error: {e}")

        return 0

    def get_review_details(self, app_id: str) -> Dict[str, Any]:
        """
        Get detailed review statistics and sentiment.

        Returns positive/negative counts and percentages.
        """
        try:
            params = {
                'json': 1,
                'filter': 'all',
                'language': 'english',
                'purchase_type': 'all'
            }

            response = self.session.get(
                f"{self.STORE_API}/appreviews/{app_id}",
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                query_summary = data.get('query_summary', {})

                total = query_summary.get('total_reviews', 0)
                positive = query_summary.get('total_positive', 0)
                negative = query_summary.get('total_negative', 0)

                return {
                    'found': True,
                    'total_reviews': total,
                    'positive_reviews': positive,
                    'negative_reviews': negative,
                    'positive_percentage': (positive / total * 100) if total > 0 else 0,
                    'review_score': query_summary.get('review_score', 0),
                    'review_score_desc': query_summary.get('review_score_desc', 'No reviews')
                }

        except Exception as e:
            print(f"⚠️  Steam review details error: {e}")

        return {'found': False}

    def get_news(self, app_id: str, count: int = 5) -> List[Dict[str, Any]]:
        """Get recent news/announcements for the game."""
        try:
            params = {
                'appid': app_id,
                'count': count,
                'maxlength': 300
            }

            response = self.session.get(
                f"{self.BASE_URL}/ISteamNews/GetNewsForApp/v2/",
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                newsitems = data.get('appnews', {}).get('newsitems', [])

                return [
                    {
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'date': item.get('date', 0),
                        'feedlabel': item.get('feedlabel', ''),
                        'contents': item.get('contents', '')[:200]
                    }
                    for item in newsitems
                ]

        except Exception as e:
            print(f"⚠️  Steam news error: {e}")

        return []


# Convenience function for creating clients with credentials
def create_api_clients(
    rawg_key: Optional[str] = None,
    youtube_key: Optional[str] = None,
    steam_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create all API clients with provided credentials.

    Returns dict with initialized clients.
    """
    clients = {
        'steamspy': SteamSpyClient()  # No key needed
    }

    if rawg_key:
        clients['rawg'] = RAWGClient(rawg_key)

    if youtube_key:
        clients['youtube'] = YouTubeClient(youtube_key)

    if steam_key:
        clients['steam_enhanced'] = EnhancedSteamClient(steam_key)

    return clients


if __name__ == "__main__":
    """Test API clients"""
    print("API Clients Module")
    print("=" * 80)
    print("\nAvailable clients:")
    print("  - SteamSpyClient: Owner estimates (no key required)")
    print("  - RAWGClient: Metacritic scores (key required)")
    print("  - YouTubeClient: Video/buzz metrics (key required)")
    print("  - EnhancedSteamClient: Enhanced Steam data (key required)")
    print("\nUsage:")
    print("  from src.api_clients import create_api_clients")
    print("  clients = create_api_clients(rawg_key='...', youtube_key='...')")
