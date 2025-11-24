#!/usr/bin/env python3
"""
Direct Steam and SteamSpy API Test
Tests the actual API endpoints to see if they work
"""

import requests
import time
import json

def test_steam_api_direct():
    """Test Steam API directly without any wrappers"""
    print("\n" + "="*80)
    print("STEAM STORE API - DIRECT TEST")
    print("="*80 + "\n")

    # Test with Hades II (well-known game)
    app_id = 1145350

    # Method 1: Steam Store API (appdetails)
    print(f"Testing App ID: {app_id} (Hades II)")
    print("\n1. Steam Store API (appdetails endpoint):")
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if str(app_id) in data and data[str(app_id)]['success']:
                game_data = data[str(app_id)]['data']
                print(f"   ✅ SUCCESS! Got game data")
                print(f"   Game Name: {game_data.get('name', 'N/A')}")
                print(f"   Type: {game_data.get('type', 'N/A')}")
                print(f"   Is Free: {game_data.get('is_free', 'N/A')}")

                # Price info
                price_overview = game_data.get('price_overview', {})
                if price_overview:
                    print(f"   Price: ${price_overview.get('final', 0) / 100:.2f}")
                    print(f"   Currency: {price_overview.get('currency', 'N/A')}")
                else:
                    print(f"   Price: Free or N/A")

                # Release date
                release_date = game_data.get('release_date', {})
                print(f"   Release Date: {release_date.get('date', 'N/A')}")

                # Genres
                genres = game_data.get('genres', [])
                if genres:
                    genre_names = [g['description'] for g in genres]
                    print(f"   Genres: {', '.join(genre_names)}")

                # Developers
                developers = game_data.get('developers', [])
                print(f"   Developers: {', '.join(developers) if developers else 'N/A'}")

                # Reviews (aggregate)
                recommendations = game_data.get('recommendations', {})
                if recommendations:
                    print(f"   Total Reviews: {recommendations.get('total', 'N/A'):,}")

                return True
            else:
                print(f"   ❌ API returned success=false")
                print(f"   Response: {json.dumps(data, indent=2)[:500]}")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False

    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False


def test_steamspy_api_direct():
    """Test SteamSpy API directly"""
    print("\n" + "="*80)
    print("STEAMSPY API - DIRECT TEST")
    print("="*80 + "\n")

    app_id = 1145350

    print(f"Testing App ID: {app_id} (Hades II)")
    url = f"https://steamspy.com/api.php?request=appdetails&appid={app_id}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Check if we got valid data
            if data.get('name'):
                print(f"✅ SUCCESS! Got SteamSpy data")
                print(f"   Game Name: {data.get('name', 'N/A')}")
                print(f"   Owners: {data.get('owners', 'N/A')}")
                print(f"   Average Forever: {data.get('average_forever', 'N/A')} minutes")
                print(f"   Average 2 Weeks: {data.get('average_2weeks', 'N/A')} minutes")
                print(f"   Positive Reviews: {data.get('positive', 'N/A'):,}")
                print(f"   Negative Reviews: {data.get('negative', 'N/A'):,}")

                # Calculate review percentage
                positive = data.get('positive', 0)
                negative = data.get('negative', 0)
                total = positive + negative
                if total > 0:
                    percentage = (positive / total) * 100
                    print(f"   Review Score: {percentage:.1f}% positive ({total:,} total)")

                # Owner range parsing
                owners_str = data.get('owners', '0 .. 0')
                if '..' in owners_str:
                    parts = owners_str.split('..')
                    low = int(parts[0].strip().replace(',', ''))
                    high = int(parts[1].strip().replace(',', ''))
                    avg = (low + high) // 2
                    print(f"   Owner Range: {low:,} - {high:,} (avg: {avg:,})")

                return True
            else:
                print(f"❌ No valid data returned")
                print(f"Response: {json.dumps(data, indent=2)[:500]}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_games():
    """Test with multiple games to see consistency"""
    print("\n" + "="*80)
    print("TESTING MULTIPLE GAMES")
    print("="*80 + "\n")

    test_games = [
        (1145350, "Hades II"),
        (1091500, "Cyberpunk 2077"),
        (1174180, "Red Dead Redemption 2"),
        (570, "Dota 2"),
        (730, "Counter-Strike 2")
    ]

    results = []

    for app_id, name in test_games:
        print(f"\nTesting {name} ({app_id})...")

        # Quick Steam API test
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
        headers = {'User-Agent': 'Mozilla/5.0'}

        try:
            response = requests.get(url, headers=headers, timeout=5)
            steam_works = response.status_code == 200
            print(f"  Steam API: {'✅' if steam_works else '❌'} ({response.status_code})")
        except Exception as e:
            steam_works = False
            print(f"  Steam API: ❌ ({str(e)[:50]})")

        # Quick SteamSpy test
        url = f"https://steamspy.com/api.php?request=appdetails&appid={app_id}"

        try:
            response = requests.get(url, headers=headers, timeout=5)
            spy_works = response.status_code == 200
            print(f"  SteamSpy API: {'✅' if spy_works else '❌'} ({response.status_code})")
        except Exception as e:
            spy_works = False
            print(f"  SteamSpy API: ❌ ({str(e)[:50]})")

        results.append({
            'name': name,
            'app_id': app_id,
            'steam_works': steam_works,
            'spy_works': spy_works
        })

        time.sleep(1)  # Rate limiting

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    steam_success = sum(1 for r in results if r['steam_works'])
    spy_success = sum(1 for r in results if r['spy_works'])

    print(f"\nSteam API: {steam_success}/{len(results)} successful")
    print(f"SteamSpy API: {spy_success}/{len(results)} successful")

    if steam_success == 0:
        print("\n❌ BLOCKER: Steam API is not accessible")
    elif steam_success < len(results):
        print("\n⚠️  WARNING: Steam API has intermittent failures")
    else:
        print("\n✅ Steam API working consistently")

    if spy_success == 0:
        print("❌ BLOCKER: SteamSpy API is not accessible")
    elif spy_success < len(results):
        print("⚠️  WARNING: SteamSpy API has intermittent failures")
    else:
        print("✅ SteamSpy API working consistently")

    return results


def main():
    print("\n" + "="*80)
    print("STEAM & STEAMSPY API DIRECT TEST SUITE")
    print("="*80)

    # Test 1: Steam API with detailed output
    steam_result = test_steam_api_direct()
    time.sleep(2)

    # Test 2: SteamSpy API with detailed output
    spy_result = test_steamspy_api_direct()
    time.sleep(2)

    # Test 3: Multiple games
    multi_results = test_multiple_games()

    print("\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80 + "\n")

    if steam_result and spy_result:
        print("✅ BOTH APIs ARE WORKING!")
        print("\n📊 Data We Can Get:")
        print("   From Steam API:")
        print("   - Game name, type, price")
        print("   - Release date")
        print("   - Genres, developers, publishers")
        print("   - Total review count (aggregate)")
        print("   - Description, screenshots, videos")
        print("\n   From SteamSpy API:")
        print("   - Owner counts (ranges)")
        print("   - Positive/negative review counts")
        print("   - Average playtime")
        print("   - Player count estimates")
        print("\n✅ NO BLOCKERS - System can proceed")
    elif steam_result or spy_result:
        print("⚠️  PARTIAL SUCCESS")
        print(f"   Steam API: {'✅ Working' if steam_result else '❌ Not working'}")
        print(f"   SteamSpy API: {'✅ Working' if spy_result else '❌ Not working'}")
        print("\n🔧 RECOMMENDATION: Implement fallbacks and caching")
    else:
        print("❌ BOTH APIs BLOCKED")
        print("\n🚨 BLOCKERS IDENTIFIED:")
        print("   - Steam API: Not accessible")
        print("   - SteamSpy API: Not accessible")
        print("\n💡 POSSIBLE SOLUTIONS:")
        print("   1. Use alternative data sources (RAWG, IGDB)")
        print("   2. Implement proxy rotation")
        print("   3. Use cached/manual data entry")
        print("   4. Try different endpoints or methods")


if __name__ == "__main__":
    main()
