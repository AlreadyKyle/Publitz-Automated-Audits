#!/usr/bin/env python3
"""
Test Alternative APIs since Steam/SteamSpy are blocked
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_rawg_api():
    """Test RAWG API as Steam alternative"""
    print("\n" + "="*80)
    print("RAWG API TEST")
    print("="*80 + "\n")

    api_key = os.getenv('RAWG_API_KEY')

    if not api_key:
        print("❌ RAWG_API_KEY not set")
        return False

    print(f"API Key: {api_key[:20]}...")

    # Search for Hades II
    print("\n1. Searching for 'Hades II'...")
    url = f"https://api.rawg.io/api/games?key={api_key}&search=Hades+II&page_size=5"

    try:
        response = requests.get(url, timeout=10)
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])

            if results:
                print(f"   ✅ Found {len(results)} games")

                for i, game in enumerate(results[:3], 1):
                    print(f"\n   Game {i}:")
                    print(f"   - ID: {game.get('id')}")
                    print(f"   - Name: {game.get('name')}")
                    print(f"   - Released: {game.get('released')}")
                    print(f"   - Rating: {game.get('rating')}/5 ({game.get('ratings_count')} ratings)")
                    print(f"   - Metacritic: {game.get('metacritic')}")

                    # Platforms
                    platforms = game.get('platforms', [])
                    if platforms:
                        platform_names = [p['platform']['name'] for p in platforms]
                        print(f"   - Platforms: {', '.join(platform_names[:3])}")

                    # Genres
                    genres = game.get('genres', [])
                    if genres:
                        genre_names = [g['name'] for g in genres]
                        print(f"   - Genres: {', '.join(genre_names)}")

                # Get detailed info for first result
                if results:
                    game_id = results[0]['id']
                    print(f"\n2. Getting detailed info for game ID {game_id}...")

                    detail_url = f"https://api.rawg.io/api/games/{game_id}?key={api_key}"
                    detail_response = requests.get(detail_url, timeout=10)

                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        print(f"   ✅ Got detailed data")
                        print(f"   - Description: {detail_data.get('description_raw', 'N/A')[:200]}...")
                        print(f"   - Website: {detail_data.get('website')}")
                        print(f"   - Developers: {[d['name'] for d in detail_data.get('developers', [])]}")
                        print(f"   - Publishers: {[p['name'] for p in detail_data.get('publishers', [])]}")
                        print(f"   - Tags: {[t['name'] for t in detail_data.get('tags', [])[:5]]}")
                    else:
                        print(f"   ❌ Detail request failed: {detail_response.status_code}")

                return True
            else:
                print(f"   ❌ No results found")
                return False
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False

    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_steam_web_scraping():
    """Test if we can scrape Steam store pages"""
    print("\n" + "="*80)
    print("STEAM WEB SCRAPING TEST")
    print("="*80 + "\n")

    app_id = 1145350
    url = f"https://store.steampowered.com/app/{app_id}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    try:
        print(f"Attempting to access: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print(f"✅ Successfully accessed Steam store page")
            print(f"   Page size: {len(response.text)} bytes")

            # Check for key content
            content = response.text
            if "Hades" in content or "hades" in content:
                print(f"   ✅ Found game content")
            if "price" in content.lower():
                print(f"   ✅ Found price information")
            if "review" in content.lower():
                print(f"   ✅ Found review information")

            return True
        else:
            print(f"❌ Cannot access Steam store page: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def compare_data_sources():
    """Compare what data we can get from different sources"""
    print("\n" + "="*80)
    print("DATA SOURCE COMPARISON")
    print("="*80 + "\n")

    data_needs = {
        "Game Name": {"steam": "✓", "steamspy": "✓", "rawg": "?", "scraping": "?"},
        "Price": {"steam": "✓", "steamspy": "✗", "rawg": "✗", "scraping": "?"},
        "Owner Count": {"steam": "✗", "steamspy": "✓", "rawg": "✗", "scraping": "✗"},
        "Review Score %": {"steam": "✗", "steamspy": "✓", "rawg": "✗", "scraping": "?"},
        "Review Count": {"steam": "✓", "steamspy": "✓", "rawg": "✓", "scraping": "?"},
        "Genres": {"steam": "✓", "steamspy": "✗", "rawg": "✓", "scraping": "?"},
        "Release Date": {"steam": "✓", "steamspy": "✗", "rawg": "✓", "scraping": "?"},
        "Developer": {"steam": "✓", "steamspy": "✗", "rawg": "✓", "scraping": "?"},
        "Description": {"steam": "✓", "steamspy": "✗", "rawg": "✓", "scraping": "?"},
        "Playtime": {"steam": "✗", "steamspy": "✓", "rawg": "✗", "scraping": "✗"},
    }

    print("Data Availability Matrix:")
    print("\n{:<20} {:<10} {:<10} {:<10} {:<10}".format(
        "Data Point", "Steam API", "SteamSpy", "RAWG", "Scraping"
    ))
    print("-" * 60)

    for data_point, sources in data_needs.items():
        print("{:<20} {:<10} {:<10} {:<10} {:<10}".format(
            data_point,
            sources["steam"],
            sources["steamspy"],
            sources["rawg"],
            sources["scraping"]
        ))

    print("\n" + "="*80)
    print("CRITICAL MISSING DATA")
    print("="*80)
    print("\nIf Steam & SteamSpy are blocked:")
    print("  ❌ Owner Count - CRITICAL (needed for revenue estimates)")
    print("  ❌ Review Score % - CRITICAL (needed for performance score)")
    print("  ❌ Price - HIGH (needed for ROI calculations)")
    print("  ⚠️  Playtime - MEDIUM (nice to have)")


def main():
    print("\n" + "="*80)
    print("ALTERNATIVE API TESTING")
    print("Since Steam & SteamSpy are blocked (403 errors)")
    print("="*80)

    # Test RAWG
    rawg_works = test_rawg_api()

    # Test Steam web scraping
    scraping_works = test_steam_web_scraping()

    # Show comparison
    compare_data_sources()

    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80 + "\n")

    if rawg_works:
        print("✅ RAWG API is working")
        print("   Can provide: Name, genres, release date, developer, ratings")
        print("   CANNOT provide: Owner counts, review %, price")
    else:
        print("❌ RAWG API not working")

    if scraping_works:
        print("\n✅ Steam web scraping might work")
        print("   Can potentially extract: Price, reviews, some metadata")
        print("   ⚠️  Fragile - breaks if Steam changes page structure")
    else:
        print("\n❌ Steam web scraping blocked")

    print("\n" + "="*80)
    print("FINAL ASSESSMENT")
    print("="*80 + "\n")

    print("🚨 CRITICAL BLOCKERS:")
    print("   1. No owner count data → Cannot estimate revenue")
    print("   2. No review score % → Cannot calculate performance score")
    print("   3. No price data → Cannot calculate ROI accurately")
    print("\n💡 POSSIBLE SOLUTIONS:")
    print("   1. Manual Data Entry - User provides Steam data")
    print("   2. Use Cached Data - If we have previous data")
    print("   3. Alternative Data Sources - IGDB, other game databases")
    print("   4. Proxy Services - Pay for Steam API access via proxy")
    print("   5. Estimated/Mock Data - For demonstration purposes")


if __name__ == "__main__":
    main()
