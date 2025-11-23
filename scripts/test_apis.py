#!/usr/bin/env python3
"""
API Testing Script
Tests all external APIs to verify they're configured correctly
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_anthropic():
    """Test Anthropic Claude API"""
    print("\n🧠 Testing Anthropic Claude API...")
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print("   ❌ ANTHROPIC_API_KEY not set")
        return False

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=50,
            messages=[{"role": "user", "content": "Say 'API test successful'"}]
        )

        print(f"   ✅ Claude API working: {response.content[0].text}")
        return True
    except Exception as e:
        print(f"   ❌ Claude API failed: {e}")
        return False


def test_twitch():
    """Test Twitch API"""
    print("\n🎮 Testing Twitch API...")
    client_id = os.getenv('TWITCH_CLIENT_ID')
    client_secret = os.getenv('TWITCH_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("   ⚠️  Twitch credentials not set (will use fallback data)")
        return None

    try:
        from src.twitch_collector import TwitchCollector
        twitch = TwitchCollector()

        data = twitch.analyze_game_viewership("Hades")

        if data.get('data_source') == 'twitch_api':
            print(f"   ✅ Twitch API working")
            print(f"      Current viewers: {data.get('current_viewers', 0):,}")
            print(f"      Channels: {data.get('channel_count', 0)}")
            return True
        else:
            print(f"   ⚠️  Using fallback data (API credentials invalid)")
            return False
    except Exception as e:
        print(f"   ❌ Twitch API failed: {e}")
        return False


def test_youtube():
    """Test YouTube API"""
    print("\n📺 Testing YouTube API...")
    api_key = os.getenv('YOUTUBE_API_KEY')

    if not api_key:
        print("   ⚠️  YOUTUBE_API_KEY not set (will use fallback data)")
        return None

    try:
        from src.youtube_api import YouTubeAPI
        yt = YouTubeAPI(api_key)

        result = yt.search_videos("Hades game", max_results=1)

        if result and 'videos' in result:
            print(f"   ✅ YouTube API working")
            print(f"      Videos found: {len(result['videos'])}")
            print(f"      Total views: {result.get('total_views', 0):,}")
            return True
        else:
            print(f"   ⚠️  No results from YouTube API")
            return False
    except Exception as e:
        print(f"   ❌ YouTube API failed: {e}")
        return False


def test_rawg():
    """Test RAWG API"""
    print("\n🎯 Testing RAWG API...")
    api_key = os.getenv('RAWG_API_KEY')

    if not api_key:
        print("   ℹ️  RAWG_API_KEY not set (optional)")
        return None

    try:
        from src.rawg_api import RAWGApi
        rawg = RAWGApi()

        data = rawg.search_game("Hades")

        if data:
            print(f"   ✅ RAWG API working")
            print(f"      Game: {data.get('name')}")
            print(f"      Rating: {data.get('rating', 0)}/5")
            print(f"      Ratings: {data.get('ratings_count', 0):,}")
            if data.get('metacritic'):
                print(f"      Metacritic: {data['metacritic']}/100")
            return True
        else:
            print(f"   ⚠️  No results from RAWG API")
            return False
    except Exception as e:
        print(f"   ❌ RAWG API failed: {e}")
        return False


def test_igdb():
    """Test IGDB API"""
    print("\n🎮 Testing IGDB API...")
    client_id = os.getenv('IGDB_CLIENT_ID')
    client_secret = os.getenv('IGDB_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("   ℹ️  IGDB credentials not set (optional)")
        return None

    try:
        from src.igdb_api import IGDBApi
        igdb = IGDBApi()

        data = igdb.search_game("Hades")

        if data:
            print(f"   ✅ IGDB API working")
            print(f"      Game: {data.get('name')}")
            print(f"      User Rating: {data.get('rating', 0):.1f}/5")
            print(f"      Critic Score: {data.get('aggregated_rating', 0):.0f}/100")
            print(f"      Followers: {data.get('follows', 0):,}")
            return True
        else:
            print(f"   ⚠️  No results from IGDB API")
            return False
    except Exception as e:
        print(f"   ❌ IGDB API failed: {e}")
        return False


def main():
    """Run all API tests"""
    print("=" * 60)
    print("🧪 Publitz API Test Suite")
    print("=" * 60)

    results = {
        'Anthropic (REQUIRED)': test_anthropic(),
        'Twitch': test_twitch(),
        'YouTube': test_youtube(),
        'RAWG': test_rawg(),
        'IGDB': test_igdb()
    }

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    for api, result in results.items():
        if result is True:
            status = "✅ WORKING"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⚠️  NOT CONFIGURED"

        print(f"{api:30} {status}")

    # Check if minimum requirements met
    print("\n" + "=" * 60)
    if not results['Anthropic (REQUIRED)']:
        print("❌ CRITICAL: Anthropic API is required for the app to work")
        print("   Get your API key: https://console.anthropic.com/")
        sys.exit(1)

    working_count = sum(1 for r in results.values() if r is True)
    total_count = len(results)

    print(f"✅ {working_count}/{total_count} APIs configured and working")

    if working_count >= 4:
        print("🎉 Excellent! You have most APIs configured for professional audits")
    elif working_count >= 3:
        print("👍 Good! Consider adding more APIs for comprehensive reports")
    else:
        print("⚠️  Limited functionality - configure more APIs for best results")

    print("\n💡 See API_SETUP_GUIDE.md for setup instructions")
    print("=" * 60)


if __name__ == "__main__":
    main()
