#!/usr/bin/env python3
"""
Test Steam Web API with your key
This is different from Steam Store API - requires authentication
"""

import requests
import json

STEAM_WEB_API_KEY = "7CD62F6A17C80F8E8889CE738578C014"

def test_steam_web_api_appdetails():
    """Test Steam Web API - GetAppDetails"""
    print("\n" + "="*80)
    print("STEAM WEB API - GetAppDetails")
    print("="*80)

    app_id = 1145350  # Hades II

    # This endpoint doesn't use the API key but let's try the web API format
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&key={STEAM_WEB_API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if str(app_id) in data and data[str(app_id)]['success']:
                game = data[str(app_id)]['data']
                print(f"✅ SUCCESS")
                print(f"   Game: {game['name']}")
                print(f"   Type: {game['type']}")
                return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_steam_web_api_player_summaries():
    """Test Steam Web API - GetPlayerSummaries"""
    print("\n" + "="*80)
    print("STEAM WEB API - GetPlayerSummaries")
    print("="*80)

    # Test with Gabe Newell's Steam ID
    steam_id = "76561197960287930"

    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_WEB_API_KEY}&steamids={steam_id}"

    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if 'response' in data and 'players' in data['response']:
                players = data['response']['players']
                if players:
                    print(f"✅ SUCCESS")
                    print(f"   Player: {players[0].get('personaname', 'Unknown')}")
                    return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_steam_web_api_app_list():
    """Test Steam Web API - GetAppList"""
    print("\n" + "="*80)
    print("STEAM WEB API - GetAppList")
    print("="*80)

    url = f"https://api.steampowered.com/ISteamApps/GetAppList/v2/?key={STEAM_WEB_API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if 'applist' in data and 'apps' in data['applist']:
                apps = data['applist']['apps']
                print(f"✅ SUCCESS")
                print(f"   Total apps: {len(apps):,}")
                print(f"   Sample: {apps[0]['name']}")
                return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_steam_web_api_news():
    """Test Steam Web API - GetNewsForApp"""
    print("\n" + "="*80)
    print("STEAM WEB API - GetNewsForApp")
    print("="*80)

    app_id = 1145350

    url = f"https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid={app_id}&key={STEAM_WEB_API_KEY}&count=1"

    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if 'appnews' in data and 'newsitems' in data['appnews']:
                items = data['appnews']['newsitems']
                if items:
                    print(f"✅ SUCCESS")
                    print(f"   Latest news: {items[0]['title'][:50]}...")
                    return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_steam_web_api_reviews():
    """Test Steam Web API - GetReviews (Store API, not Web API)"""
    print("\n" + "="*80)
    print("STEAM STORE API - GetReviews")
    print("="*80)

    app_id = 1145350

    # Reviews endpoint doesn't use Web API key
    url = f"https://store.steampowered.com/appreviews/{app_id}?json=1&filter=recent&num_per_page=10"

    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if 'success' in data and data['success'] == 1:
                reviews = data.get('reviews', [])
                print(f"✅ SUCCESS")
                print(f"   Reviews fetched: {len(reviews)}")
                if reviews:
                    print(f"   Sample: {reviews[0]['review'][:50]}...")
                return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    print("\n" + "="*80)
    print("STEAM WEB API KEY TEST")
    print(f"Key: {STEAM_WEB_API_KEY[:20]}...")
    print("="*80)

    results = {
        'appdetails': test_steam_web_api_appdetails(),
        'player_summaries': test_steam_web_api_player_summaries(),
        'app_list': test_steam_web_api_app_list(),
        'news': test_steam_web_api_news(),
        'reviews': test_steam_web_api_reviews()
    }

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80 + "\n")

    working = [k for k, v in results.items() if v]
    broken = [k for k, v in results.items() if not v]

    print(f"✅ Working: {len(working)}/5")
    for endpoint in working:
        print(f"   - {endpoint}")

    print(f"\n❌ Not Working: {len(broken)}/5")
    for endpoint in broken:
        print(f"   - {endpoint}")

    print("\n" + "="*80)
    print("WHAT THIS MEANS")
    print("="*80 + "\n")

    if len(working) >= 3:
        print("✅ Steam Web API is accessible!")
        print("\nYou can use:")
        if results['appdetails']:
            print("  - Game details (name, price, genres, etc.)")
        if results['player_summaries']:
            print("  - Player data")
        if results['app_list']:
            print("  - Full Steam game catalog")
        if results['news']:
            print("  - Game news and updates")
        if results['reviews']:
            print("  - User reviews")

        print("\n⚠️  Still need SteamSpy for:")
        print("  - Owner counts")
        print("  - Revenue estimates")
        print("  - Positive/Negative review split")

    else:
        print("❌ Steam Web API is also blocked")
        print("\nSame network restrictions apply.")
        print("The API key is valid but environment blocks access.")

    return 0 if len(working) >= 3 else 1


if __name__ == "__main__":
    exit(main())
