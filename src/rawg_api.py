#!/usr/bin/env python3
"""
RAWG API Integration
Provides game metadata from RAWG.io database
"""

import requests
import os
from typing import Dict, Any, Optional


class RAWGApi:
    """Interface to RAWG Video Games Database API"""

    def __init__(self):
        self.api_key = os.getenv('RAWG_API_KEY')
        self.base_url = "https://api.rawg.io/api"
        self.session = requests.Session()

    def search_game(self, game_name: str, exact_match: bool = False) -> Optional[Dict[str, Any]]:
        """
        Search for a game by name

        Args:
            game_name: Name of the game to search for
            exact_match: If True, only return exact matches

        Returns:
            Game data dict or None if not found
        """
        if not self.api_key:
            print("Warning: RAWG_API_KEY not set. Skipping RAWG API.")
            return None

        try:
            print(f"Searching RAWG for: {game_name}")

            params = {
                'key': self.api_key,
                'search': game_name,
                'page_size': 5,  # Get top 5 results
                'ordering': '-rating'  # Sort by rating
            }

            response = self.session.get(
                f"{self.base_url}/games",
                params=params,
                timeout=3
            )
            response.raise_for_status()

            data = response.json()
            results = data.get('results', [])

            if not results:
                print(f"No results found on RAWG for: {game_name}")
                return None

            # If exact_match, look for exact name match
            if exact_match:
                for game in results:
                    if game.get('name', '').lower() == game_name.lower():
                        print(f"✓ Found exact match on RAWG: {game['name']}")
                        return self._format_game_data(game)

            # Otherwise return best match (first result)
            best_match = results[0]
            print(f"✓ Found on RAWG: {best_match['name']} (confidence: {self._calculate_match_confidence(game_name, best_match['name'])}%)")
            return self._format_game_data(best_match)

        except requests.Timeout:
            print("Timeout accessing RAWG API")
            return None
        except Exception as e:
            print(f"Error accessing RAWG API: {e}")
            return None

    def get_game_by_id(self, rawg_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed game information by RAWG ID"""
        if not self.api_key:
            return None

        try:
            response = self.session.get(
                f"{self.base_url}/games/{rawg_id}",
                params={'key': self.api_key},
                timeout=3
            )
            response.raise_for_status()
            return self._format_game_data(response.json())
        except Exception as e:
            print(f"Error getting RAWG game details: {e}")
            return None

    def _format_game_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format RAWG data to our standard structure"""

        # Extract relevant fields
        genres = [g['name'] for g in raw_data.get('genres', [])]
        tags = [t['name'] for t in raw_data.get('tags', [])[:15]]
        platforms = [p['platform']['name'] for p in raw_data.get('platforms', [])]

        # Get ratings breakdown
        ratings = raw_data.get('ratings', [])
        total_ratings = sum(r.get('count', 0) for r in ratings)

        # Calculate positive percentage (exceptional + recommended)
        positive_count = sum(
            r.get('count', 0) for r in ratings
            if r.get('title', '').lower() in ['exceptional', 'recommended']
        )

        rating_percent = (positive_count / total_ratings * 100) if total_ratings > 0 else 0

        return {
            'rawg_id': raw_data.get('id'),
            'name': raw_data.get('name'),
            'released': raw_data.get('released'),  # Release date (YYYY-MM-DD)
            'rating': raw_data.get('rating', 0),  # Average rating (0-5)
            'rating_top': raw_data.get('rating_top', 5),
            'ratings_count': raw_data.get('ratings_count', 0),  # Total ratings
            'reviews_count': raw_data.get('reviews_text_count', 0),
            'added': raw_data.get('added', 0),  # Times added to libraries
            'metacritic': raw_data.get('metacritic'),
            'playtime': raw_data.get('playtime', 0),  # Average playtime hours
            'genres': genres,
            'tags': tags,
            'platforms': platforms,
            'esrb_rating': raw_data.get('esrb_rating', {}).get('name') if raw_data.get('esrb_rating') else None,
            'description': raw_data.get('description_raw', ''),
            'website': raw_data.get('website'),
            'background_image': raw_data.get('background_image'),

            # Derived fields for our use
            'positive_rating_percent': rating_percent,
            'total_ratings': total_ratings,
            'has_steam': any('PC' in p for p in platforms),

            # Quality signals
            'quality_signals': {
                'high_metacritic': raw_data.get('metacritic', 0) >= 80 if raw_data.get('metacritic') else False,
                'high_rating': raw_data.get('rating', 0) >= 4.0,
                'high_engagement': raw_data.get('ratings_count', 0) > 1000,
                'recent_release': self._is_recent_release(raw_data.get('released')),
            }
        }

    def _calculate_match_confidence(self, query: str, result: str) -> int:
        """Calculate how confident we are this is the right game"""
        query_lower = query.lower().strip()
        result_lower = result.lower().strip()

        # Exact match
        if query_lower == result_lower:
            return 100

        # Contains query
        if query_lower in result_lower or result_lower in query_lower:
            return 85

        # Word overlap
        query_words = set(query_lower.split())
        result_words = set(result_lower.split())
        overlap = len(query_words & result_words) / max(len(query_words), len(result_words))

        return int(overlap * 70)

    def _is_recent_release(self, release_date: Optional[str]) -> bool:
        """Check if game was released in last 2 years"""
        if not release_date:
            return False

        try:
            from datetime import datetime
            release = datetime.strptime(release_date, '%Y-%m-%d')
            years_old = (datetime.now() - release).days / 365.25
            return years_old <= 2
        except:
            return False


def test_rawg_api():
    """Test RAWG API integration"""
    api = RAWGApi()

    # Test search
    game = api.search_game("Hades II")
    if game:
        print("\n=== RAWG Data ===")
        print(f"Name: {game['name']}")
        print(f"Released: {game['released']}")
        print(f"Rating: {game['rating']}/5 ({game['ratings_count']:,} ratings)")
        print(f"Metacritic: {game['metacritic']}")
        print(f"Playtime: {game['playtime']} hours average")
        print(f"Genres: {', '.join(game['genres'])}")
        print(f"Platforms: {', '.join(game['platforms'][:5])}")
        print(f"Positive %: {game['positive_rating_percent']:.1f}%")
        print(f"Quality Signals: {game['quality_signals']}")

    return game


if __name__ == "__main__":
    test_rawg_api()
