#!/usr/bin/env python3
"""
Google Trends Integration
Provides search interest trends and popularity metrics for games
"""

from typing import Dict, Any, Optional, List
import time


class TrendsApi:
    """Interface to Google Trends via pytrends library"""

    def __init__(self):
        self.pytrends = None
        self._initialize_pytrends()

    def _initialize_pytrends(self):
        """Initialize pytrends library"""
        try:
            from pytrends.request import TrendReq
            # Initialize with retries and timeout
            self.pytrends = TrendReq(
                hl='en-US',
                tz=360,
                timeout=(3, 5),  # Connect timeout, read timeout
                retries=2,
                backoff_factor=0.1
            )
            print("✓ Google Trends initialized")
        except ImportError:
            print("Warning: pytrends not installed. Run: pip install pytrends")
            self.pytrends = None
        except Exception as e:
            print(f"Error initializing Google Trends: {e}")
            self.pytrends = None

    def get_interest_over_time(self, game_name: str, timeframe: str = 'today 12-m') -> Optional[Dict[str, Any]]:
        """
        Get search interest over time for a game

        Args:
            game_name: Name of the game
            timeframe: Time period (default: last 12 months)
                      Options: 'today 1-m', 'today 3-m', 'today 12-m', 'today 5-y', 'all'

        Returns:
            Dict with interest data or None
        """
        if not self.pytrends:
            return None

        try:
            print(f"Getting Google Trends for: {game_name} ({timeframe})")

            # Build payload
            self.pytrends.build_payload(
                kw_list=[game_name],
                timeframe=timeframe,
                geo='',  # Worldwide
                gprop=''  # Web search
            )

            # Get interest over time
            interest_df = self.pytrends.interest_over_time()

            if interest_df.empty:
                print(f"No trends data found for: {game_name}")
                return None

            # Calculate metrics
            values = interest_df[game_name].values
            current_interest = int(values[-1]) if len(values) > 0 else 0
            avg_interest = int(values.mean()) if len(values) > 0 else 0
            peak_interest = int(values.max()) if len(values) > 0 else 0

            # Determine trend direction (last 30 days vs previous 30 days)
            if len(values) >= 8:  # Need at least 8 weeks
                recent_avg = values[-4:].mean()  # Last 4 weeks
                previous_avg = values[-8:-4].mean()  # Previous 4 weeks
                trend_direction = 'rising' if recent_avg > previous_avg * 1.1 else \
                                'falling' if recent_avg < previous_avg * 0.9 else 'stable'
            else:
                trend_direction = 'unknown'

            print(f"✓ Trends: Current={current_interest}, Peak={peak_interest}, Trend={trend_direction}")

            return {
                'current_interest': current_interest,  # 0-100 scale
                'average_interest': avg_interest,
                'peak_interest': peak_interest,
                'trend_direction': trend_direction,  # 'rising', 'falling', 'stable'
                'data_points': len(values),
                'timeframe': timeframe
            }

        except Exception as e:
            print(f"Error getting trends data: {e}")
            return None

    def get_related_queries(self, game_name: str) -> Optional[Dict[str, Any]]:
        """Get related search queries for a game"""
        if not self.pytrends:
            return None

        try:
            print(f"Getting related queries for: {game_name}")

            # Build payload
            self.pytrends.build_payload(
                kw_list=[game_name],
                timeframe='today 12-m',
                geo='',
                gprop=''
            )

            # Get related queries
            related = self.pytrends.related_queries()

            if not related or game_name not in related:
                return None

            game_related = related[game_name]

            top_queries = []
            if game_related['top'] is not None and not game_related['top'].empty:
                top_queries = game_related['top']['query'].head(5).tolist()

            rising_queries = []
            if game_related['rising'] is not None and not game_related['rising'].empty:
                rising_queries = game_related['rising']['query'].head(5).tolist()

            return {
                'top_queries': top_queries,
                'rising_queries': rising_queries
            }

        except Exception as e:
            print(f"Error getting related queries: {e}")
            return None

    def compare_games(self, game_names: List[str], timeframe: str = 'today 12-m') -> Optional[Dict[str, Any]]:
        """
        Compare search interest for multiple games

        Args:
            game_names: List of game names to compare (max 5)
            timeframe: Time period

        Returns:
            Dict with comparison data
        """
        if not self.pytrends or not game_names:
            return None

        # Limit to 5 games (Google Trends API limit)
        game_names = game_names[:5]

        try:
            print(f"Comparing trends for: {', '.join(game_names)}")

            # Build payload
            self.pytrends.build_payload(
                kw_list=game_names,
                timeframe=timeframe,
                geo='',
                gprop=''
            )

            # Get interest over time
            interest_df = self.pytrends.interest_over_time()

            if interest_df.empty:
                return None

            # Calculate rankings
            rankings = {}
            for game in game_names:
                if game in interest_df.columns:
                    values = interest_df[game].values
                    rankings[game] = {
                        'avg_interest': int(values.mean()),
                        'current_interest': int(values[-1]) if len(values) > 0 else 0,
                        'peak_interest': int(values.max())
                    }

            # Sort by average interest
            sorted_games = sorted(rankings.items(), key=lambda x: x[1]['avg_interest'], reverse=True)

            return {
                'rankings': dict(sorted_games),
                'leader': sorted_games[0][0] if sorted_games else None,
                'timeframe': timeframe
            }

        except Exception as e:
            print(f"Error comparing games: {e}")
            return None

    def get_comprehensive_metrics(self, game_name: str) -> Dict[str, Any]:
        """
        Get comprehensive trends metrics for a game

        Returns dict with:
        - Interest over time
        - Trend direction
        - Related queries
        - Quality signals for estimation
        """
        # Get interest over time
        interest_data = self.get_interest_over_time(game_name)

        # Small delay to avoid rate limiting
        time.sleep(0.5)

        # Get related queries
        related_data = self.get_related_queries(game_name)

        if not interest_data:
            return {}

        # Calculate quality signals
        current = interest_data.get('current_interest', 0)
        peak = interest_data.get('peak_interest', 0)
        trend = interest_data.get('trend_direction', 'unknown')

        return {
            'source': 'Google Trends',
            'current_interest': current,
            'peak_interest': peak,
            'average_interest': interest_data.get('average_interest', 0),
            'trend_direction': trend,
            'top_queries': related_data.get('top_queries', []) if related_data else [],
            'rising_queries': related_data.get('rising_queries', []) if related_data else [],
            'quality_signals': {
                'high_current_interest': current >= 50,  # High search volume
                'viral_peak': peak >= 80,  # Had viral moment
                'rising_trend': trend == 'rising',  # Growing interest
                'stable_interest': current >= 25,  # Sustained interest
            }
        }


def test_trends():
    """Test Google Trends integration"""
    trends = TrendsApi()

    if not trends.pytrends:
        print("Cannot test: pytrends not available")
        return

    # Test games
    test_games = ['Hades II', 'Elden Ring', 'Hollow Knight']

    for game_name in test_games:
        print(f"\n{'='*60}")
        print(f"Testing: {game_name}")
        print('='*60)

        result = trends.get_comprehensive_metrics(game_name)

        if result:
            print(f"\n✓ Trends Data:")
            print(f"  Current Interest: {result['current_interest']}/100")
            print(f"  Peak Interest: {result['peak_interest']}/100")
            print(f"  Trend: {result['trend_direction']}")
            print(f"  Top Queries: {', '.join(result['top_queries'][:3])}")
        else:
            print(f"✗ No trends data")

        # Delay between requests
        time.sleep(2)


if __name__ == '__main__':
    test_trends()
