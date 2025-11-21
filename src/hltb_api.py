#!/usr/bin/env python3
"""
HowLongToBeat Integration
Provides game completion time data for engagement analysis
"""

from typing import Dict, Any, Optional


class HLTBApi:
    """Interface to HowLongToBeat via howlongtobeatpy library"""

    def __init__(self):
        self.hltb = None
        self._initialize_hltb()

    def _initialize_hltb(self):
        """Initialize HowLongToBeat library"""
        try:
            from howlongtobeatpy import HowLongToBeat
            self.hltb = HowLongToBeat()
            print("✓ HowLongToBeat initialized")
        except ImportError:
            print("⚠️ howlongtobeatpy not installed. Run: pip install howlongtobeatpy")
            self.hltb = None
        except Exception as e:
            print(f"⚠️ Error initializing HowLongToBeat: {e}")
            self.hltb = None

    def search_game(self, game_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for a game and get completion times

        Args:
            game_name: Name of the game

        Returns:
            Dict with completion time data or None
        """
        if not self.hltb:
            return None

        try:
            print(f"Searching HowLongToBeat for: {game_name}")

            # Search returns a list of results
            results = self.hltb.search(game_name)

            if not results:
                print(f"No results found on HowLongToBeat for: {game_name}")
                return None

            # Get best match (first result)
            best_match = results[0]

            print(f"✓ Found on HLTB: {best_match.game_name}")

            return self._format_hltb_data(best_match)

        except Exception as e:
            print(f"Error searching HowLongToBeat: {e}")
            return None

    def _format_hltb_data(self, hltb_result) -> Dict[str, Any]:
        """Format HLTB data to our standard structure"""

        # Extract completion times (in hours)
        main_story = hltb_result.main_story if hasattr(hltb_result, 'main_story') else 0
        main_extra = hltb_result.main_extra if hasattr(hltb_result, 'main_extra') else 0
        completionist = hltb_result.completionist if hasattr(hltb_result, 'completionist') else 0

        # Get the most relevant time (prefer main story)
        primary_time = main_story if main_story > 0 else main_extra

        # Calculate quality signals
        quality_signals = {
            'very_long_game': primary_time >= 50,  # 50+ hours
            'long_game': primary_time >= 20,  # 20+ hours
            'medium_length': primary_time >= 10,  # 10+ hours
            'high_replayability': completionist > main_story * 1.5 if main_story > 0 else False
        }

        return {
            'source': 'HowLongToBeat',
            'game_name': hltb_result.game_name,
            'main_story_hours': main_story,
            'main_extra_hours': main_extra,
            'completionist_hours': completionist,
            'primary_hours': primary_time,
            'quality_signals': quality_signals
        }

    def get_comprehensive_metrics(self, game_name: str) -> Dict[str, Any]:
        """
        Get comprehensive HLTB metrics for a game

        Returns dict with:
        - Completion times (main, extra, completionist)
        - Engagement signals
        - Quality indicators
        """
        hltb_data = self.search_game(game_name)

        if not hltb_data:
            return {}

        return hltb_data


def test_hltb():
    """Test HowLongToBeat integration"""
    hltb = HLTBApi()

    if not hltb.hltb:
        print("Cannot test: howlongtobeatpy not available")
        print("Install with: pip install howlongtobeatpy")
        return

    # Test games
    test_games = ['Hades II', 'Hollow Knight', 'Elden Ring']

    for game_name in test_games:
        print(f"\n{'='*60}")
        print(f"Testing: {game_name}")
        print('='*60)

        result = hltb.get_comprehensive_metrics(game_name)

        if result:
            print(f"\n✓ HLTB Data:")
            print(f"  Game: {result['game_name']}")
            print(f"  Main Story: {result['main_story_hours']} hours")
            print(f"  Main + Extra: {result['main_extra_hours']} hours")
            print(f"  Completionist: {result['completionist_hours']} hours")
            print(f"  Quality Signals: {result['quality_signals']}")
        else:
            print(f"✗ No HLTB data")


if __name__ == '__main__':
    test_hltb()
