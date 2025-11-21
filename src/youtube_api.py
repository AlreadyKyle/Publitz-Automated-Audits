#!/usr/bin/env python3
"""
YouTube Data API Integration
Provides video count, view metrics, and engagement data for games
"""

import requests
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class YouTubeApi:
    """Interface to YouTube Data API v3"""

    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def search_videos(self, game_name: str, max_results: int = 10) -> Optional[Dict[str, Any]]:
        """
        Search for videos related to a game

        Args:
            game_name: Name of the game
            max_results: Number of results to return (max 50)

        Returns:
            Dict with video data or None
        """
        if not self.api_key:
            print("Warning: YOUTUBE_API_KEY not set")
            return None

        try:
            print(f"Searching YouTube for: {game_name}")

            # Search for videos (costs 100 quota units)
            params = {
                'key': self.api_key,
                'part': 'snippet',
                'q': f'{game_name} gameplay',
                'type': 'video',
                'maxResults': max_results,
                'order': 'viewCount',  # Most popular first
                'relevanceLanguage': 'en'
            }

            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                timeout=3
            )
            response.raise_for_status()

            data = response.json()
            items = data.get('items', [])

            if not items:
                print(f"No YouTube videos found for: {game_name}")
                return None

            # Get video IDs
            video_ids = [item['id']['videoId'] for item in items]

            # Get detailed video statistics (costs 1 unit per video)
            stats = self._get_video_statistics(video_ids)

            print(f"✓ Found {len(items)} YouTube videos for {game_name}")

            return {
                'video_count': len(items),
                'video_ids': video_ids,
                'statistics': stats,
                'items': items
            }

        except requests.Timeout:
            print("Timeout accessing YouTube API")
            return None
        except Exception as e:
            print(f"Error accessing YouTube API: {e}")
            return None

    def _get_video_statistics(self, video_ids: list) -> Dict[str, Any]:
        """Get detailed statistics for videos"""
        if not self.api_key or not video_ids:
            return {}

        try:
            # Get stats for up to 50 videos at once
            video_ids_str = ','.join(video_ids[:50])

            params = {
                'key': self.api_key,
                'part': 'statistics',
                'id': video_ids_str
            }

            response = requests.get(
                f"{self.base_url}/videos",
                params=params,
                timeout=3
            )
            response.raise_for_status()

            data = response.json()
            items = data.get('items', [])

            # Aggregate statistics
            total_views = 0
            total_likes = 0
            total_comments = 0

            for item in items:
                stats = item.get('statistics', {})
                total_views += int(stats.get('viewCount', 0))
                total_likes += int(stats.get('likeCount', 0))
                total_comments += int(stats.get('commentCount', 0))

            avg_views = total_views // len(items) if items else 0
            avg_likes = total_likes // len(items) if items else 0
            avg_comments = total_comments // len(items) if items else 0

            return {
                'total_views': total_views,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'avg_views': avg_views,
                'avg_likes': avg_likes,
                'avg_comments': avg_comments,
                'video_count': len(items)
            }

        except Exception as e:
            print(f"Error getting video statistics: {e}")
            return {}

    def get_channel_count(self, game_name: str) -> Optional[int]:
        """
        Estimate number of channels creating content for a game

        Args:
            game_name: Name of the game

        Returns:
            Approximate number of channels
        """
        if not self.api_key:
            return None

        try:
            # Search for channels (costs 100 units)
            params = {
                'key': self.api_key,
                'part': 'snippet',
                'q': game_name,
                'type': 'channel',
                'maxResults': 50
            }

            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                timeout=3
            )
            response.raise_for_status()

            data = response.json()
            total_results = data.get('pageInfo', {}).get('totalResults', 0)

            return total_results

        except Exception as e:
            print(f"Error getting channel count: {e}")
            return None

    def get_recent_activity(self, game_name: str, days: int = 30) -> Optional[Dict[str, Any]]:
        """
        Get recent upload activity for a game

        Args:
            game_name: Name of the game
            days: Number of days to look back

        Returns:
            Dict with recent activity metrics
        """
        if not self.api_key:
            return None

        try:
            # Calculate date range
            published_after = (datetime.now() - timedelta(days=days)).isoformat() + 'Z'

            params = {
                'key': self.api_key,
                'part': 'snippet',
                'q': f'{game_name} gameplay',
                'type': 'video',
                'maxResults': 50,
                'publishedAfter': published_after,
                'order': 'date'
            }

            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                timeout=3
            )
            response.raise_for_status()

            data = response.json()
            items = data.get('items', [])
            total_results = data.get('pageInfo', {}).get('totalResults', 0)

            return {
                'recent_videos': len(items),
                'estimated_total': total_results,
                'uploads_per_day': total_results / days if days > 0 else 0,
                'days_analyzed': days
            }

        except Exception as e:
            print(f"Error getting recent activity: {e}")
            return None

    def get_comprehensive_metrics(self, game_name: str) -> Dict[str, Any]:
        """
        Get comprehensive YouTube metrics for a game

        Returns dict with:
        - Video statistics (views, likes, comments)
        - Content creator engagement
        - Recent activity trends
        - Quality signals for estimation
        """
        # Search for top videos
        video_data = self.search_videos(game_name, max_results=10)

        if not video_data:
            return {}

        stats = video_data.get('statistics', {})
        total_views = stats.get('total_views', 0)
        avg_views = stats.get('avg_views', 0)
        video_count = stats.get('video_count', 0)

        # Calculate quality signals
        quality_signals = {
            'high_video_count': video_count >= 5,
            'high_engagement': total_views >= 1_000_000,
            'very_high_engagement': total_views >= 10_000_000,
            'strong_avg_views': avg_views >= 100_000,
        }

        return {
            'source': 'YouTube',
            'total_views': total_views,
            'avg_views': avg_views,
            'total_likes': stats.get('total_likes', 0),
            'total_comments': stats.get('total_comments', 0),
            'video_count': video_count,
            'engagement_rate': (stats.get('total_likes', 0) / total_views * 100) if total_views > 0 else 0,
            'quality_signals': quality_signals
        }


def test_youtube():
    """Test YouTube API integration"""
    youtube = YouTubeApi()

    if not youtube.api_key:
        print("Cannot test: YOUTUBE_API_KEY not set")
        print("Get a free API key at: https://console.cloud.google.com/apis/credentials")
        return

    # Test games
    test_games = ['Hades II', 'Hollow Knight']

    for game_name in test_games:
        print(f"\n{'='*60}")
        print(f"Testing: {game_name}")
        print('='*60)

        result = youtube.get_comprehensive_metrics(game_name)

        if result:
            print(f"\n✓ YouTube Data:")
            print(f"  Videos Found: {result['video_count']}")
            print(f"  Total Views: {result['total_views']:,}")
            print(f"  Avg Views: {result['avg_views']:,}")
            print(f"  Engagement Rate: {result['engagement_rate']:.2f}%")
            print(f"  Quality Signals: {result['quality_signals']}")
        else:
            print(f"✗ No YouTube data")


if __name__ == '__main__':
    test_youtube()
