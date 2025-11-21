#!/usr/bin/env python3
"""
Steam Web API Integration
Provides official Steam data: player counts, achievements, stats
"""

import requests
from typing import Dict, Any, Optional


class SteamWebApi:
    """Interface to official Steam Web API"""

    def __init__(self):
        self.base_url = "https://api.steampowered.com"
        self.session = requests.Session()

    def get_current_players(self, app_id: int) -> Optional[int]:
        """
        Get current concurrent player count for a game

        Args:
            app_id: Steam app ID

        Returns:
            Number of current players or None
        """
        try:
            print(f"Fetching Steam player count for app {app_id}...")

            url = f"{self.base_url}/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
            params = {'appid': app_id}

            response = self.session.get(url, params=params, timeout=3)
            response.raise_for_status()

            data = response.json()

            if data.get('response', {}).get('result') == 1:
                player_count = data['response'].get('player_count', 0)
                print(f"✓ Steam API: {player_count:,} current players")
                return player_count
            else:
                print(f"⚠️ Steam API returned no player data for app {app_id}")
                return None

        except requests.Timeout:
            print("Timeout accessing Steam Web API")
            return None
        except Exception as e:
            print(f"Error accessing Steam Web API: {e}")
            return None

    def get_player_stats_schema(self, app_id: int) -> Optional[Dict[str, Any]]:
        """
        Get achievement schema for a game

        Args:
            app_id: Steam app ID

        Returns:
            Achievement data or None
        """
        try:
            url = f"{self.base_url}/ISteamUserStats/GetSchemaForGame/v2/"
            params = {'appid': app_id}

            response = self.session.get(url, params=params, timeout=3)
            response.raise_for_status()

            data = response.json()

            if 'game' in data:
                achievements = data['game'].get('availableGameStats', {}).get('achievements', [])
                return {
                    'total_achievements': len(achievements),
                    'achievements': achievements
                }

            return None

        except Exception as e:
            print(f"Error getting achievement schema: {e}")
            return None

    def get_comprehensive_metrics(self, app_id: int) -> Dict[str, Any]:
        """
        Get comprehensive Steam metrics for a game

        Returns dict with:
        - Current player count
        - Achievement data
        - Quality signals for estimation
        """
        # Get current players
        player_count = self.get_current_players(app_id)

        if not player_count:
            return {}

        # Calculate quality signals based on player count
        quality_signals = {
            'very_high_players': player_count >= 50000,  # 50K+ concurrent
            'high_players': player_count >= 10000,  # 10K+ concurrent
            'moderate_players': player_count >= 1000,  # 1K+ concurrent
            'active_playerbase': player_count >= 100,  # 100+ concurrent
        }

        return {
            'source': 'Steam Web API',
            'current_players': player_count,
            'quality_signals': quality_signals
        }


def test_steam_api():
    """Test Steam Web API integration"""
    steam = SteamWebApi()

    # Test games with known player counts
    test_games = [
        (730, 'Counter-Strike 2'),  # Always has high players
        (1145350, 'Hades II'),
        (413150, 'Stardew Valley')
    ]

    for app_id, name in test_games:
        print(f"\n{'='*60}")
        print(f"Testing: {name} (App ID: {app_id})")
        print('='*60)

        result = steam.get_comprehensive_metrics(app_id)

        if result:
            print(f"\n✓ Steam Web API Data:")
            print(f"  Current Players: {result['current_players']:,}")
            print(f"  Quality Signals: {result['quality_signals']}")
        else:
            print(f"✗ No Steam data available")


if __name__ == '__main__':
    test_steam_api()
