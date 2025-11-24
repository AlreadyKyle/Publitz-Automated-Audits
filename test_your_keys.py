#!/usr/bin/env python3
"""
Direct test of YOUR specific API keys
No bullshit, just testing if these keys work
"""

import requests
import json

def test_anthropic_key():
    """Test your Anthropic API key"""
    print("\n" + "="*80)
    print("TESTING ANTHROPIC API KEY")
    print("="*80)

    import os
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set in environment")
        return False

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        # Simple test
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=20,
            messages=[{"role": "user", "content": "Say 'working'"}]
        )

        response = message.content[0].text
        print(f"✅ ANTHROPIC KEY WORKS")
        print(f"   Response: {response}")
        return True

    except Exception as e:
        print(f"❌ ANTHROPIC KEY FAILED: {e}")
        return False


def test_rawg_key():
    """Test your RAWG API key"""
    print("\n" + "="*80)
    print("TESTING RAWG API KEY")
    print("="*80)

    import os
    api_key = os.getenv('RAWG_API_KEY')
    if not api_key:
        print("❌ RAWG_API_KEY not set in environment")
        return False

    try:
        # Test with a simple game search
        url = f"https://api.rawg.io/api/games?key={api_key}&search=hades&page_size=1"

        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                game = data['results'][0]
                print(f"✅ RAWG KEY WORKS")
                print(f"   Found: {game['name']}")
                return True
            else:
                print(f"❌ RAWG KEY: No results")
                return False
        else:
            print(f"❌ RAWG KEY FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ RAWG KEY FAILED: {e}")
        return False


def test_youtube_key():
    """Test your YouTube API key"""
    print("\n" + "="*80)
    print("TESTING YOUTUBE API KEY")
    print("="*80)

    import os
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ YOUTUBE_API_KEY not set in environment")
        return False

    try:
        # Search for gaming videos
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q=hades+game&type=video&key={api_key}&maxResults=1"

        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                video = data['items'][0]
                print(f"✅ YOUTUBE KEY WORKS")
                print(f"   Found: {video['snippet']['title'][:50]}")
                return True
            else:
                print(f"❌ YOUTUBE KEY: No results")
                return False
        else:
            print(f"❌ YOUTUBE KEY FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ YOUTUBE KEY FAILED: {e}")
        return False


def test_twitch_keys():
    """Test your Twitch API credentials"""
    print("\n" + "="*80)
    print("TESTING TWITCH API CREDENTIALS")
    print("="*80)

    import os
    client_id = os.getenv('TWITCH_CLIENT_ID')
    client_secret = os.getenv('TWITCH_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("❌ TWITCH credentials not set in environment")
        return False

    try:
        # Get OAuth token first
        auth_url = "https://id.twitch.tv/oauth2/token"
        auth_params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
        }

        auth_response = requests.post(auth_url, params=auth_params, timeout=10)
        print(f"   Auth Status: {auth_response.status_code}")

        if auth_response.status_code == 200:
            token_data = auth_response.json()
            access_token = token_data['access_token']

            # Test with games endpoint
            headers = {
                'Client-ID': client_id,
                'Authorization': f'Bearer {access_token}'
            }

            games_url = "https://api.twitch.tv/helix/games/top?first=1"
            games_response = requests.get(games_url, headers=headers, timeout=10)

            if games_response.status_code == 200:
                data = games_response.json()
                if data.get('data'):
                    game = data['data'][0]
                    print(f"✅ TWITCH KEYS WORK")
                    print(f"   Top Game: {game['name']}")
                    return True
            else:
                print(f"❌ TWITCH API CALL FAILED: HTTP {games_response.status_code}")
                return False
        else:
            print(f"❌ TWITCH AUTH FAILED: HTTP {auth_response.status_code}")
            print(f"   Response: {auth_response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ TWITCH KEYS FAILED: {e}")
        return False


def test_steam_direct():
    """Test Steam API (no key needed, but checking if accessible)"""
    print("\n" + "="*80)
    print("TESTING STEAM API ACCESS")
    print("="*80)

    try:
        url = "https://store.steampowered.com/api/appdetails?appids=1145350"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if '1145350' in data and data['1145350']['success']:
                game_data = data['1145350']['data']
                print(f"✅ STEAM API ACCESSIBLE")
                print(f"   Found: {game_data['name']}")
                return True
        else:
            print(f"❌ STEAM API BLOCKED: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ STEAM API ERROR: {e}")
        return False


def test_steamspy_direct():
    """Test SteamSpy API (no key needed, but checking if accessible)"""
    print("\n" + "="*80)
    print("TESTING STEAMSPY API ACCESS")
    print("="*80)

    try:
        url = "https://steamspy.com/api.php?request=appdetails&appid=1145350"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('name'):
                print(f"✅ STEAMSPY API ACCESSIBLE")
                print(f"   Found: {data['name']}")
                print(f"   Owners: {data.get('owners', 'N/A')}")
                return True
        else:
            print(f"❌ STEAMSPY API BLOCKED: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ STEAMSPY API ERROR: {e}")
        return False


def main():
    print("\n" + "="*80)
    print("TESTING YOUR ACTUAL API KEYS")
    print("Direct test - no bullshit")
    print("="*80)

    results = {}

    # Test each API
    results['anthropic'] = test_anthropic_key()
    results['rawg'] = test_rawg_key()
    results['youtube'] = test_youtube_key()
    results['twitch'] = test_twitch_keys()
    results['steam'] = test_steam_direct()
    results['steamspy'] = test_steamspy_direct()

    # Summary
    print("\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80 + "\n")

    working = [k for k, v in results.items() if v]
    broken = [k for k, v in results.items() if not v]

    print(f"✅ WORKING ({len(working)}/6):")
    for api in working:
        print(f"   - {api.upper()}")

    print(f"\n❌ NOT WORKING ({len(broken)}/6):")
    for api in broken:
        print(f"   - {api.upper()}")

    print("\n" + "="*80)
    print("WHAT THIS MEANS")
    print("="*80 + "\n")

    if results['steam'] and results['steamspy']:
        print("✅ You CAN use Steam and SteamSpy APIs")
        print("   → System can fetch game data automatically")
        print("   → Full automation possible")
    else:
        print("❌ Steam/SteamSpy APIs are BLOCKED in this environment")
        print("   → Cannot fetch game data automatically")
        print("   → This is a network/firewall issue, NOT a key issue")
        print("   → Solution: Run from different environment OR use manual entry")

    if results['anthropic']:
        print("\n✅ Claude API works")
        print("   → AI-powered review analysis available")
    else:
        print("\n❌ Claude API doesn't work")
        print("   → Check key or network access")

    if results['rawg'] or results['youtube'] or results['twitch']:
        print("\n✅ Some alternative APIs work")
        print("   → Can use for supplementary data")
    else:
        print("\n❌ All alternative APIs blocked")
        print("   → Likely environment-wide HTTP restrictions")

    print("\n" + "="*80)
    print("BOTTOM LINE")
    print("="*80 + "\n")

    if not results['steam'] and not results['steamspy']:
        print("🚨 CRITICAL: Steam/SteamSpy APIs are blocked")
        print("\nThis is NOT a key problem - it's environment blocking.")
        print("\nYour options:")
        print("1. Run this tool from a different network/machine")
        print("2. Use a VPN/proxy")
        print("3. Contact your IT about outbound HTTP restrictions")
        print("\nThe keys you provided might be fine - we just can't test them from here.")
    else:
        print("✅ GOOD NEWS: Core APIs are accessible")
        print("\nYou can proceed with automated data fetching.")

    return 0 if (results['steam'] and results['steamspy']) else 1


if __name__ == "__main__":
    exit(main())
