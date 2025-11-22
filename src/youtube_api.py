#!/usr/bin/env python3
"""
YouTube Data API Integration
Provides video count, view metrics, engagement data, and influencer discovery for games
"""

import requests
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from src.logger import get_logger
from src.cache_manager import get_cache

logger = get_logger(__name__)


class YouTubeApi:
    """Interface to YouTube Data API v3"""

    # Genre-specific channel categories
    GENRE_CHANNEL_TYPES = {
        'roguelike': ['gameplay', 'review', 'lets_play', 'challenge_runs'],
        'strategy': ['gameplay', 'tutorial', 'competitive'],
        'rpg': ['lets_play', 'story_playthrough', 'review'],
        'action': ['montage', 'gameplay', 'speedrun'],
        'indie': ['review', 'first_impressions', 'indie_showcase'],
        'simulation': ['gameplay', 'tutorial', 'time_lapse'],
    }

    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.cache = get_cache()
        logger.info("YouTubeApi initialized")

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

    def find_channels_for_outreach(self, game_name: str, genres: List[str],
                                   min_subscribers: int = 10000,
                                   max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Find YouTube channels for game marketing outreach

        Args:
            game_name: Name of the game
            genres: List of game genres
            min_subscribers: Minimum subscriber count
            max_results: Maximum channels to return

        Returns:
            List of channel data with contact info and ROI estimates
        """
        logger.info(f"Finding YouTube channels for {game_name}")

        # Check cache
        cache_key = f"{game_name}_{min_subscribers}"
        cached = self.cache.get('youtube_channels', cache_key)
        if cached:
            logger.debug("Using cached channel data")
            return cached

        if not self.api_key:
            logger.warning("YOUTUBE_API_KEY not set, using fallback data")
            return self._get_fallback_channels(genres)

        try:
            # Search for channels covering similar games
            search_terms = [
                f"{game_name} review",
                f"indie game review",
                f"{genres[0] if genres else 'indie'} games"
            ]

            all_channels = []
            seen_channel_ids = set()

            for search_term in search_terms:
                params = {
                    'key': self.api_key,
                    'part': 'snippet',
                    'q': search_term,
                    'type': 'channel',
                    'maxResults': 10,
                    'order': 'relevance'
                }

                response = requests.get(
                    f"{self.base_url}/search",
                    params=params,
                    timeout=5
                )
                response.raise_for_status()

                data = response.json()
                items = data.get('items', [])

                for item in items:
                    channel_id = item['id']['channelId']
                    if channel_id not in seen_channel_ids:
                        seen_channel_ids.add(channel_id)

                        # Get channel details
                        channel_info = self._get_channel_details(channel_id)
                        if channel_info and channel_info.get('subscribers', 0) >= min_subscribers:
                            all_channels.append(channel_info)

            # Enhance with ROI estimates
            for channel in all_channels:
                channel['roi_score'] = self._calculate_channel_roi(channel)
                channel['outreach_priority'] = self._get_outreach_priority(channel)
                channel['contact_method'] = self._extract_contact_info(channel)
                channel['recommended_video_types'] = self._get_video_type_recommendations(genres)

            # Sort by ROI score
            all_channels.sort(key=lambda x: x['roi_score'], reverse=True)

            # Limit results
            result = all_channels[:max_results]

            # Cache results
            self.cache.set('youtube_channels', cache_key, result)

            logger.info(f"Found {len(result)} relevant YouTube channels")
            return result

        except Exception as e:
            logger.error(f"Error finding YouTube channels: {e}")
            return self._get_fallback_channels(genres)

    def _get_channel_details(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about a specific channel"""
        try:
            params = {
                'key': self.api_key,
                'part': 'snippet,statistics,contentDetails',
                'id': channel_id
            }

            response = requests.get(
                f"{self.base_url}/channels",
                params=params,
                timeout=5
            )
            response.raise_for_status()

            data = response.json()
            items = data.get('items', [])

            if not items:
                return None

            item = items[0]
            snippet = item.get('snippet', {})
            stats = item.get('statistics', {})

            # Parse subscriber count
            subscriber_count = int(stats.get('subscriberCount', 0))
            view_count = int(stats.get('viewCount', 0))
            video_count = int(stats.get('videoCount', 1))

            # Calculate average views per video
            avg_views = view_count // video_count if video_count > 0 else 0

            return {
                'channel_id': channel_id,
                'name': snippet.get('title', 'Unknown'),
                'description': snippet.get('description', '')[:200],
                'subscribers': subscriber_count,
                'total_views': view_count,
                'video_count': video_count,
                'avg_views_per_video': avg_views,
                'url': f"https://www.youtube.com/channel/{channel_id}",
                'custom_url': snippet.get('customUrl', ''),
                'country': snippet.get('country', 'Unknown'),
                'thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url', '')
            }

        except Exception as e:
            logger.debug(f"Error getting channel details for {channel_id}: {e}")
            return None

    def _calculate_channel_roi(self, channel: Dict[str, Any]) -> float:
        """
        Calculate ROI score for outreach (0-100)

        Factors:
        - Subscriber count (engagement potential)
        - Avg views per video (actual reach)
        - Video count (content creation frequency)
        - Subscriber-to-view ratio (engagement quality)
        """
        score = 50  # Base score

        subscribers = channel.get('subscribers', 0)
        avg_views = channel.get('avg_views_per_video', 0)
        video_count = channel.get('video_count', 0)

        # Subscriber score (sweet spot: 10K-100K)
        if 10000 <= subscribers <= 100000:
            score += 25  # Best ROI range
        elif 5000 <= subscribers < 10000:
            score += 15
        elif subscribers > 100000:
            score += 10  # Still good but harder to reach

        # Engagement quality (views/subscriber ratio)
        if subscribers > 0:
            engagement_ratio = avg_views / subscribers
            if engagement_ratio > 0.5:  # >50% view rate
                score += 20
            elif engagement_ratio > 0.2:  # >20% view rate
                score += 10

        # Content frequency
        if video_count > 100:
            score += 5  # Active creator

        return min(100, score)

    def _get_outreach_priority(self, channel: Dict[str, Any]) -> str:
        """Determine outreach priority level"""
        roi_score = channel.get('roi_score', 0)

        if roi_score >= 75:
            return "high"
        elif roi_score >= 50:
            return "medium"
        else:
            return "low"

    def _extract_contact_info(self, channel: Dict[str, Any]) -> Dict[str, Any]:
        """Extract or recommend contact methods"""

        description = channel.get('description', '').lower()

        # Look for email in description
        has_email = 'email' in description or '@' in description
        has_business_inquiry = 'business' in description or 'partnership' in description

        contact_method = "YouTube 'About' page"
        if has_email:
            contact_method = "Email (check 'About' page)"
        elif has_business_inquiry:
            contact_method = "Business inquiry form"

        return {
            'primary_method': contact_method,
            'url': f"{channel.get('url', '')}/about",
            'tips': [
                'Check channel "About" page for business email',
                'Send personalized message mentioning their content',
                'Offer key copy or early access',
                'Be specific about why your game fits their audience'
            ]
        }

    def _get_video_type_recommendations(self, genres: List[str]) -> List[str]:
        """Get recommended video types based on genres"""

        video_types = set()

        for genre in genres:
            genre_lower = genre.lower()
            for key, types in self.GENRE_CHANNEL_TYPES.items():
                if key in genre_lower:
                    video_types.update(types)

        if not video_types:
            video_types = ['review', 'gameplay', 'first_impressions']

        return list(video_types)

    def _get_fallback_channels(self, genres: List[str]) -> List[Dict[str, Any]]:
        """Provide fallback channel recommendations when API unavailable"""

        # Curated list of indie game YouTubers by genre
        fallback_channels = {
            'indie': [
                {'name': 'Splattercat', 'subscribers': 250000, 'focus': 'Indie game coverage',
                 'url': 'https://youtube.com/@splattercatgaming', 'roi_score': 85},
                {'name': 'Wanderbots', 'subscribers': 180000, 'focus': 'Indie & roguelike games',
                 'url': 'https://youtube.com/@wanderbots', 'roi_score': 80},
                {'name': 'Retromation', 'subscribers': 160000, 'focus': 'Roguelike/roguelite',
                 'url': 'https://youtube.com/@retromation', 'roi_score': 82},
            ],
            'roguelike': [
                {'name': 'Retromation', 'subscribers': 160000, 'focus': 'Roguelike specialist',
                 'url': 'https://youtube.com/@retromation', 'roi_score': 90},
                {'name': 'Wanderbots', 'subscribers': 180000, 'focus': 'Roguelike coverage',
                 'url': 'https://youtube.com/@wanderbots', 'roi_score': 85},
            ],
            'strategy': [
                {'name': 'Pravus Gaming', 'subscribers': 220000, 'focus': 'Strategy games',
                 'url': 'https://youtube.com/@pravusgaming', 'roi_score': 83},
            ]
        }

        # Find matching channels
        result_channels = []
        seen = set()

        for genre in genres:
            genre_lower = genre.lower()
            for key, channels in fallback_channels.items():
                if key in genre_lower:
                    for channel in channels:
                        if channel['name'] not in seen:
                            seen.add(channel['name'])
                            # Enhance with standard fields
                            channel['outreach_priority'] = 'high' if channel['roi_score'] >= 80 else 'medium'
                            channel['contact_method'] = {'primary_method': "Check channel 'About' page",
                                                        'url': f"{channel['url']}/about"}
                            channel['recommended_video_types'] = self._get_video_type_recommendations(genres)
                            result_channels.append(channel)

        # Add general indie channels if not many found
        if len(result_channels) < 3:
            for channel in fallback_channels.get('indie', []):
                if channel['name'] not in seen:
                    seen.add(channel['name'])
                    channel['outreach_priority'] = 'medium'
                    channel['contact_method'] = {'primary_method': "Check channel 'About' page"}
                    channel['recommended_video_types'] = self._get_video_type_recommendations(genres)
                    result_channels.append(channel)

        return result_channels

    def generate_outreach_report(self, channels: List[Dict[str, Any]],
                                 game_name: str) -> Dict[str, Any]:
        """
        Generate YouTube outreach report

        Args:
            channels: List of channel data
            game_name: Name of the game

        Returns:
            Outreach report with recommendations
        """
        if not channels:
            return {
                'total_channels': 0,
                'recommendations': ['No YouTube channels identified. Consider using fallback list.']
            }

        # Group by priority
        high_priority = [c for c in channels if c.get('outreach_priority') == 'high']
        medium_priority = [c for c in channels if c.get('outreach_priority') == 'medium']
        low_priority = [c for c in channels if c.get('outreach_priority') == 'low']

        # Calculate total reach
        total_reach = sum(c.get('subscribers', 0) for c in channels)
        avg_views = sum(c.get('avg_views_per_video', 0) for c in channels) // len(channels) if channels else 0

        recommendations = []

        # Top priority channels
        if high_priority:
            top_channel = high_priority[0]
            recommendations.append(
                f"🎯 **Top Priority**: Reach out to {top_channel['name']} "
                f"({top_channel.get('subscribers', 0):,} subscribers, ROI score: {top_channel.get('roi_score', 0):.0f})"
            )

        # Overall strategy
        recommendations.append(
            f"📊 **Total Reach**: {len(channels)} channels with {total_reach:,} combined subscribers"
        )

        recommendations.append(
            f"💡 **Strategy**: Focus on {len(high_priority)} high-priority channels first"
        )

        # Video type recommendations
        if channels:
            video_types = channels[0].get('recommended_video_types', [])
            recommendations.append(
                f"🎥 **Suggested Content**: {', '.join(video_types[:3])}"
            )

        # Budget estimate
        estimated_cost_per_video = 500  # Average sponsored video cost for indie games
        total_budget = len(high_priority) * estimated_cost_per_video
        recommendations.append(
            f"💰 **Estimated Budget**: ${total_budget:,} for {len(high_priority)} sponsored videos"
        )

        return {
            'total_channels': len(channels),
            'high_priority': len(high_priority),
            'medium_priority': len(medium_priority),
            'low_priority': len(low_priority),
            'total_reach': total_reach,
            'avg_views_per_video': avg_views,
            'recommendations': recommendations,
            'channels': channels
        }


# Convenience function
def get_youtube_outreach_analysis(game_name: str, genres: List[str]) -> Dict[str, Any]:
    """
    Get complete YouTube outreach analysis

    Args:
        game_name: Name of the game
        genres: List of game genres

    Returns:
        Complete YouTube channel and outreach analysis
    """
    youtube = YouTubeApi()

    # Find channels
    channels = youtube.find_channels_for_outreach(game_name, genres, min_subscribers=10000)

    # Generate outreach report
    outreach_report = youtube.generate_outreach_report(channels, game_name)

    return {
        'channels': channels,
        'outreach_report': outreach_report,
        'summary': {
            'total_channels': len(channels),
            'high_priority_count': outreach_report['high_priority'],
            'total_reach': outreach_report['total_reach'],
            'recommendations': outreach_report['recommendations']
        }
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
