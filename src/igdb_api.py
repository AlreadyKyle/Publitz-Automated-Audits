#!/usr/bin/env python3
"""
IGDB API Integration (Twitch/Amazon owned)
Provides comprehensive game database with ratings, platforms, release dates
"""

import requests
import os
import time
from typing import Dict, Any, Optional


class IGDBApi:
    """Interface to IGDB (Internet Game Database) API"""

    def __init__(self):
        self.client_id = os.getenv('IGDB_CLIENT_ID')
        self.client_secret = os.getenv('IGDB_CLIENT_SECRET')
        self.base_url = "https://api.igdb.com/v4"
        self.access_token = None
        self.token_expires_at = 0

    def _get_access_token(self) -> Optional[str]:
        """Get OAuth access token from Twitch"""
        if not self.client_id or not self.client_secret:
            print("Warning: IGDB_CLIENT_ID or IGDB_CLIENT_SECRET not set")
            return None

        # Check if we have a valid token
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        try:
            print("Getting IGDB access token from Twitch...")
            response = requests.post(
                'https://id.twitch.tv/oauth2/token',
                params={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'client_credentials'
                },
                timeout=5
            )
            response.raise_for_status()

            data = response.json()
            self.access_token = data['access_token']
            # Token typically expires in 60 days, but we'll refresh after 50 days
            self.token_expires_at = time.time() + (50 * 24 * 60 * 60)

            print("✓ Got IGDB access token")
            return self.access_token

        except Exception as e:
            print(f"Error getting IGDB access token: {e}")
            return None

    def search_game(self, game_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for a game by name

        Args:
            game_name: Name of the game to search for

        Returns:
            Game data dict or None if not found
        """
        token = self._get_access_token()
        if not token:
            return None

        try:
            print(f"Searching IGDB for: {game_name}")

            # IGDB uses POST requests with a query body
            headers = {
                'Client-ID': self.client_id,
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }

            # Query for games with ratings, genres, platforms, etc.
            query = f'''
                search "{game_name}";
                fields name, rating, rating_count, aggregated_rating, aggregated_rating_count,
                       total_rating, total_rating_count, first_release_date,
                       genres.name, platforms.name, follows, hypes,
                       summary, storyline, url;
                limit 5;
            '''

            response = requests.post(
                f"{self.base_url}/games",
                headers=headers,
                data=query,
                timeout=3
            )
            response.raise_for_status()

            results = response.json()

            if not results:
                print(f"No results found on IGDB for: {game_name}")
                return None

            # Return best match (first result)
            best_match = results[0]
            print(f"✓ Found on IGDB: {best_match.get('name', 'Unknown')}")
            return self._format_game_data(best_match)

        except requests.Timeout:
            print("Timeout accessing IGDB API")
            return None
        except Exception as e:
            print(f"Error accessing IGDB API: {e}")
            return None

    def _format_game_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format IGDB data to our standard structure"""

        # Extract genres
        genres = []
        if 'genres' in raw_data:
            genres = [g.get('name', '') for g in raw_data['genres']]

        # Extract platforms
        platforms = []
        if 'platforms' in raw_data:
            platforms = [p.get('name', '') for p in raw_data['platforms']]

        # Convert Unix timestamp to readable date
        release_date = None
        if 'first_release_date' in raw_data:
            from datetime import datetime
            timestamp = raw_data['first_release_date']
            release_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

        # IGDB uses 0-100 rating scale
        rating = raw_data.get('rating', 0)  # User rating
        aggregated_rating = raw_data.get('aggregated_rating', 0)  # Critic rating (like Metacritic)
        total_rating = raw_data.get('total_rating', 0)  # Combined rating

        return {
            'igdb_id': raw_data.get('id'),
            'name': raw_data.get('name'),
            'released': release_date,
            'rating': rating / 20 if rating else 0,  # Convert 0-100 to 0-5 scale
            'rating_count': raw_data.get('rating_count', 0),
            'aggregated_rating': aggregated_rating,  # Keep 0-100 for Metacritic-like score
            'total_rating': total_rating / 20 if total_rating else 0,  # Convert to 0-5
            'total_rating_count': raw_data.get('total_rating_count', 0),
            'follows': raw_data.get('follows', 0),  # Community interest
            'hypes': raw_data.get('hypes', 0),  # Pre-release interest
            'genres': genres,
            'platforms': platforms,
            'summary': raw_data.get('summary', ''),
            'url': raw_data.get('url', ''),
            'quality_signals': {
                'high_rating': rating >= 80,  # 80+ on 0-100 scale
                'high_critic_score': aggregated_rating >= 80,
                'high_engagement': raw_data.get('rating_count', 0) > 100,
                'strong_community': raw_data.get('follows', 0) > 1000,
            }
        }

    def get_multiple_signals(self, game_name: str) -> Dict[str, Any]:
        """
        Get comprehensive game data from IGDB

        Returns dict with:
        - Basic info (name, release date)
        - Ratings (user, critic, combined)
        - Community signals (follows, hypes, rating_count)
        - Quality signals for estimation
        """
        game_data = self.search_game(game_name)
        if not game_data:
            return {}

        return {
            'source': 'IGDB',
            'name': game_data['name'],
            'release_date': game_data['released'],
            'user_rating': game_data['rating'],  # 0-5 scale
            'critic_rating': game_data['aggregated_rating'],  # 0-100 scale (Metacritic-like)
            'combined_rating': game_data['total_rating'],  # 0-5 scale
            'rating_count': game_data['rating_count'],
            'follows': game_data['follows'],
            'hypes': game_data['hypes'],
            'genres': game_data['genres'],
            'quality_signals': game_data['quality_signals']
        }


def test_igdb():
    """Test IGDB API integration"""
    igdb = IGDBApi()

    # Test search
    test_games = ['Hades II', 'Hollow Knight', 'Elden Ring']

    for game_name in test_games:
        print(f"\n{'='*60}")
        print(f"Testing: {game_name}")
        print('='*60)

        result = igdb.get_multiple_signals(game_name)

        if result:
            print(f"\n✓ Found: {result['name']}")
            print(f"  Release: {result['release_date']}")
            print(f"  User Rating: {result['user_rating']:.1f}/5")
            print(f"  Critic Score: {result['critic_rating']:.0f}/100")
            print(f"  Follows: {result['follows']:,}")
            print(f"  Genres: {', '.join(result['genres'][:3])}")
        else:
            print(f"✗ Not found on IGDB")


if __name__ == '__main__':
    test_igdb()
