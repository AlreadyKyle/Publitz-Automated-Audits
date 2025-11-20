#!/usr/bin/env python3
"""
Test Components - Verify each part works independently
Run this BEFORE deploying to find issues early
"""

import sys
from src.game_search import GameSearch
from src.steamdb_scraper import SteamDBScraper

def test_url_parsing():
    """Test 1: URL Parsing"""
    print("\n" + "="*60)
    print("TEST 1: Steam URL Parsing")
    print("="*60)

    game_search = GameSearch()
    test_urls = [
        "https://store.steampowered.com/app/3183790/Defense_Of_Fort_Burton/",
        "https://store.steampowered.com/app/292030/The_Witcher_3_Wild_Hunt/",
        "https://store.steampowered.com/app/730/Counter_Strike_2/",
    ]

    for url in test_urls:
        app_id = game_search.parse_steam_url(url)
        status = "✅ PASS" if app_id else "❌ FAIL"
        print(f"{status} | URL: {url}")
        print(f"      | App ID: {app_id}")

    return True

def test_game_fetching():
    """Test 2: Game Data Fetching"""
    print("\n" + "="*60)
    print("TEST 2: Game Data Fetching")
    print("="*60)

    game_search = GameSearch()
    test_url = "https://store.steampowered.com/app/3183790/Defense_Of_Fort_Burton/"

    try:
        game_data = game_search.get_game_from_url(test_url)
        if game_data:
            print(f"✅ PASS | Found game: {game_data.get('name')}")
            print(f"      | Developer: {game_data.get('developer')}")
            print(f"      | Release: {game_data.get('release_date')}")
            print(f"      | Price: {game_data.get('price')}")
            print(f"      | Genres: {game_data.get('genres')}")
            return game_data
        else:
            print("❌ FAIL | No game data returned")
            return None
    except Exception as e:
        print(f"❌ FAIL | Error: {e}")
        return None

def test_launch_detection(game_data):
    """Test 3: Launch Status Detection"""
    print("\n" + "="*60)
    print("TEST 3: Launch Status Detection")
    print("="*60)

    if not game_data:
        print("⚠️  SKIP | No game data from previous test")
        return

    game_search = GameSearch()
    try:
        status = game_search.detect_launch_status(game_data)
        print(f"✅ PASS | Detected: {status}")
        print(f"      | Release Date: {game_data.get('release_date')}")
        return status
    except Exception as e:
        print(f"❌ FAIL | Error: {e}")
        return None

def test_competitor_finding(game_data):
    """Test 4: Competitor Finding"""
    print("\n" + "="*60)
    print("TEST 4: Competitor Finding")
    print("="*60)

    if not game_data:
        print("⚠️  SKIP | No game data from previous test")
        return []

    game_search = GameSearch()
    try:
        competitors = game_search.find_competitors(game_data, min_competitors=3, max_competitors=5)
        num_comps = len(competitors)

        if num_comps >= 3:
            print(f"✅ PASS | Found {num_comps} competitors")
        elif num_comps > 0:
            print(f"⚠️  WARN | Found only {num_comps} competitors (minimum is 3)")
        else:
            print(f"❌ FAIL | Found ZERO competitors (should never happen)")

        for i, comp in enumerate(competitors[:3], 1):
            print(f"      | {i}. {comp.get('name')} ({comp.get('price')})")

        return competitors
    except Exception as e:
        print(f"❌ FAIL | Error: {e}")
        return []

def test_sales_data(game_data):
    """Test 5: Sales Data Fetching"""
    print("\n" + "="*60)
    print("TEST 5: Sales Data Fetching")
    print("="*60)

    if not game_data:
        print("⚠️  SKIP | No game data from previous test")
        return None

    scraper = SteamDBScraper()
    try:
        sales_data = scraper.get_sales_data(game_data['app_id'])
        if sales_data:
            print(f"✅ PASS | Retrieved sales data")
            print(f"      | Owners: {sales_data.get('owners_display', 'N/A')}")
            print(f"      | Revenue Est: {sales_data.get('estimated_revenue', 'N/A')}")
            print(f"      | Reviews: {sales_data.get('reviews_total', 'N/A')}")
            print(f"      | Score: {sales_data.get('review_score', 'N/A')}")
            return sales_data
        else:
            print("❌ FAIL | No sales data returned")
            return None
    except Exception as e:
        print(f"❌ FAIL | Error: {e}")
        return None

def test_anthropic_version():
    """Test 6: Anthropic Library Version"""
    print("\n" + "="*60)
    print("TEST 6: Anthropic Library Version")
    print("="*60)

    try:
        import anthropic
        version = anthropic.__version__

        # Check if version is >= 0.40.0
        major, minor = map(int, version.split('.')[:2])
        if major == 0 and minor >= 40:
            print(f"✅ PASS | anthropic version: {version}")
        elif major > 0:
            print(f"✅ PASS | anthropic version: {version}")
        else:
            print(f"❌ FAIL | anthropic version: {version} (needs >= 0.40.0)")
            print(f"      | Run: pip install --upgrade anthropic")
    except Exception as e:
        print(f"❌ FAIL | Error checking version: {e}")

def main():
    """Run all tests"""
    print("\n🧪 PUBLITZ AUTOMATED AUDITS - COMPONENT TESTS")
    print("="*60)
    print("Testing each component independently...")
    print("This helps identify issues before deployment")
    print("="*60)

    # Test 6: Check library versions first
    test_anthropic_version()

    # Test 1: URL Parsing
    test_url_parsing()

    # Test 2: Game Data Fetching
    game_data = test_game_fetching()

    # Test 3: Launch Detection
    test_launch_detection(game_data)

    # Test 4: Competitor Finding
    competitors = test_competitor_finding(game_data)

    # Test 5: Sales Data
    test_sales_data(game_data)

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("If all tests above show ✅ PASS, the Steam integration works!")
    print("If any show ❌ FAIL, fix those issues before testing Claude API")
    print("")
    print("Next Step: Test with Streamlit app")
    print("  streamlit run app.py")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
