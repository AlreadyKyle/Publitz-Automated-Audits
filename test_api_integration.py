#!/usr/bin/env python3
"""
API Integration Test Suite

Tests all external API integrations to verify they're working correctly.
"""

import sys
sys.path.insert(0, '/home/user/Publitz-Automated-Audits')

import os
import time


def test_steam_api():
    """Test Steam API integration"""
    print("\n" + "="*80)
    print("TEST 1: STEAM API INTEGRATION")
    print("="*80 + "\n")

    try:
        from src.game_search import GameSearch

        search = GameSearch()

        # Test with Hades II (well-known game)
        app_id = 1145350
        print(f"Testing with Hades II (App ID: {app_id})...")

        game_details = search.get_game_details(app_id)

        if game_details:
            print(f"✅ Steam API working!")
            print(f"   Game Name: {game_details.get('name', 'Unknown')}")
            print(f"   Price: {game_details.get('price', 'Unknown')}")
            print(f"   Genres: {game_details.get('genres', [])}")
            print(f"   Release Date: {game_details.get('release_date', 'Unknown')}")
            print(f"   Review Score: {game_details.get('review_score_raw', 0)}%")
            print(f"   Review Count: {game_details.get('review_count', 0):,}")
            return True
        else:
            print("❌ Steam API failed - no data returned")
            return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Missing dependency: bs4 (BeautifulSoup)")
        print("   Install with: pip install beautifulsoup4 lxml")
        return False
    except Exception as e:
        print(f"❌ Steam API error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_steamspy_api():
    """Test SteamSpy API integration"""
    print("\n" + "="*80)
    print("TEST 2: STEAMSPY API INTEGRATION")
    print("="*80 + "\n")

    try:
        from src.game_search import GameSearch

        search = GameSearch()

        # Test with Hades II
        app_id = 1145350
        print(f"Testing with Hades II (App ID: {app_id})...")

        spy_data = search.get_steamspy_data(app_id)

        if spy_data:
            print(f"✅ SteamSpy API working!")
            print(f"   Owners: {spy_data.get('owners', 'Unknown')}")
            print(f"   Average Owners: {spy_data.get('owners_avg', 0):,}")
            print(f"   Positive Reviews: {spy_data.get('positive', 0):,}")
            print(f"   Negative Reviews: {spy_data.get('negative', 0):,}")
            print(f"   Average Playtime: {spy_data.get('average_forever', 0)} minutes")
            return True
        else:
            print("❌ SteamSpy API failed - no data returned")
            return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ SteamSpy API error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_claude_api():
    """Test Claude API configuration"""
    print("\n" + "="*80)
    print("TEST 3: CLAUDE API CONFIGURATION")
    print("="*80 + "\n")

    api_key = os.environ.get('ANTHROPIC_API_KEY')

    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        print("   Claude API is required for negative review analysis")
        print("   Set with: export ANTHROPIC_API_KEY='your-key-here'")
        return False

    print(f"✅ ANTHROPIC_API_KEY is set")
    print(f"   Key length: {len(api_key)} characters")
    print(f"   Key prefix: {api_key[:10]}...")

    # Try to import the analyzer
    try:
        from src.negative_review_analyzer import NegativeReviewAnalyzer
        analyzer = NegativeReviewAnalyzer()
        print("✅ NegativeReviewAnalyzer imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Missing dependency: anthropic")
        print("   Install with: pip install anthropic")
        return False
    except Exception as e:
        print(f"❌ Claude API configuration error: {e}")
        return False


def test_data_parsing():
    """Test data parsing and formatting"""
    print("\n" + "="*80)
    print("TEST 4: DATA PARSING AND FORMATTING")
    print("="*80 + "\n")

    try:
        from src.comparable_games_analyzer import ComparableGamesAnalyzer

        analyzer = ComparableGamesAnalyzer()

        # Test owner range parsing
        test_cases = [
            ("10000 .. 20000", 15000),
            ("50000 .. 100000", 75000),
            ("1000000 .. 2000000", 1500000),
            ("0 .. 20000", 10000)
        ]

        print("Testing owner range parsing:")
        all_pass = True
        for owners_str, expected in test_cases:
            result = analyzer._parse_owners_range(owners_str)
            status = "✅" if result == expected else "❌"
            print(f"  {status} '{owners_str}' → {result:,} (expected: {expected:,})")
            if result != expected:
                all_pass = False

        # Test owner tier classification
        print("\nTesting owner tier classification:")
        tier_cases = [
            (500, "<1K"),
            (3000, "1K-5K"),
            (7000, "5K-10K"),
            (25000, "10K-50K"),
            (75000, "50K-100K"),
            (250000, "100K-500K"),
            (750000, "500K-1M"),
            (2000000, "1M+")
        ]

        for owners, expected_tier in tier_cases:
            result = analyzer._get_owner_tier(owners)
            status = "✅" if result == expected_tier else "❌"
            print(f"  {status} {owners:,} owners → {result} (expected: {expected_tier})")
            if result != expected_tier:
                all_pass = False

        if all_pass:
            print("\n✅ All data parsing tests passed!")
            return True
        else:
            print("\n❌ Some data parsing tests failed")
            return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Data parsing error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_roi_calculations():
    """Test ROI calculator data correctness"""
    print("\n" + "="*80)
    print("TEST 5: ROI CALCULATION ACCURACY")
    print("="*80 + "\n")

    try:
        from src.roi_calculator import ROICalculator

        # Test with known values
        calculator = ROICalculator(hourly_rate=50)

        # Test 1: Regional pricing
        print("Test 1: Regional Pricing ROI")
        result = calculator.calculate_regional_pricing_roi(
            current_revenue=5000,
            current_regions=1
        )

        expected_time_cost = 12 * 50  # 12 hours * $50/hr = $600
        expected_total = 600  # No financial costs

        print(f"  Time investment: {result.time_investment.total_hours} hours")
        print(f"  Time cost: ${result.time_investment.total_hours * result.hourly_rate:.0f}")
        print(f"  Total investment: ${result.total_investment:.0f}")

        if abs(result.total_investment - expected_total) < 0.01:
            print(f"  ✅ Calculation correct (expected ${expected_total})")
        else:
            print(f"  ❌ Calculation wrong (expected ${expected_total}, got ${result.total_investment:.0f})")
            return False

        # Test 2: Custom hourly rate
        print("\nTest 2: Custom Hourly Rate")
        calculator_custom = ROICalculator(hourly_rate=100)
        result_custom = calculator_custom.calculate_regional_pricing_roi(
            current_revenue=5000,
            current_regions=1
        )

        expected_custom = 12 * 100  # 12 hours * $100/hr = $1200

        print(f"  Hourly rate: ${calculator_custom.hourly_rate:.0f}/hr")
        print(f"  Total investment: ${result_custom.total_investment:.0f}")

        if abs(result_custom.total_investment - expected_custom) < 0.01:
            print(f"  ✅ Custom rate working (expected ${expected_custom})")
        else:
            print(f"  ❌ Custom rate broken (expected ${expected_custom}, got ${result_custom.total_investment:.0f})")
            return False

        # Test 3: ROI ratio calculation
        print("\nTest 3: ROI Ratio Calculation")
        # If revenue impact is $1200 and investment is $600, ROI should be 2.0x
        if result.revenue_impact.likely > 0:
            expected_roi = result.revenue_impact.likely / result.total_investment
            actual_roi = result.roi_likely

            print(f"  Revenue (likely): ${result.revenue_impact.likely:.0f}")
            print(f"  Investment: ${result.total_investment:.0f}")
            print(f"  ROI: {actual_roi:.2f}x")

            if abs(actual_roi - expected_roi) < 0.01:
                print(f"  ✅ ROI calculation correct")
            else:
                print(f"  ❌ ROI calculation wrong (expected {expected_roi:.2f}x, got {actual_roi:.2f}x)")
                return False

        print("\n✅ All ROI calculation tests passed!")
        return True

    except Exception as e:
        print(f"❌ ROI calculation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_end_to_end():
    """Test end-to-end data flow"""
    print("\n" + "="*80)
    print("TEST 6: END-TO-END DATA FLOW")
    print("="*80 + "\n")

    try:
        from src.game_search import GameSearch

        search = GameSearch()
        app_id = 1145350  # Hades II

        print(f"Fetching complete game data for app {app_id}...")

        # Get Steam data
        game_details = search.get_game_details(app_id)
        if not game_details:
            print("❌ Failed to get Steam data")
            return False

        # Get SteamSpy data
        spy_data = search.get_steamspy_data(app_id)
        if not spy_data:
            print("❌ Failed to get SteamSpy data")
            return False

        # Build game_data dict (as report orchestrator would)
        game_data = {
            'app_id': str(app_id),
            'name': game_details.get('name'),
            'price': game_details.get('price_raw', 0),
            'review_score': game_details.get('review_score_raw', 0),
            'review_count': game_details.get('review_count', 0),
            'owners': spy_data.get('owners_avg', 0),
            'revenue': spy_data.get('revenue_estimate', 0),
            'genres': game_details.get('genres', []),
            'release_date': game_details.get('release_date', '')
        }

        print(f"\n✅ Successfully built game_data:")
        print(f"   Name: {game_data['name']}")
        print(f"   Price: ${game_data['price']:.2f}")
        print(f"   Reviews: {game_data['review_count']:,} ({game_data['review_score']:.0f}% positive)")
        print(f"   Owners: {game_data['owners']:,}")
        print(f"   Revenue: ${game_data['revenue']:,}")
        print(f"   Genres: {', '.join(game_data['genres'][:3])}")

        # Verify data makes sense
        issues = []

        if game_data['price'] < 0:
            issues.append("Price is negative")
        if game_data['review_score'] < 0 or game_data['review_score'] > 100:
            issues.append(f"Review score out of range: {game_data['review_score']}")
        if game_data['review_count'] < 0:
            issues.append("Review count is negative")
        if game_data['owners'] < 0:
            issues.append("Owner count is negative")
        if not game_data['genres']:
            issues.append("No genres found")

        if issues:
            print(f"\n❌ Data validation issues:")
            for issue in issues:
                print(f"   - {issue}")
            return False

        print(f"\n✅ All data validation passed!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ End-to-end test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all API tests"""
    print("\n" + "="*80)
    print("PUBLITZ API INTEGRATION TEST SUITE")
    print("="*80)

    results = {
        'Steam API': test_steam_api(),
        'SteamSpy API': test_steamspy_api(),
        'Claude API Config': test_claude_api(),
        'Data Parsing': test_data_parsing(),
        'ROI Calculations': test_roi_calculations(),
        'End-to-End Flow': test_end_to_end()
    }

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80 + "\n")

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    total = len(results)
    passed = sum(results.values())
    failed = total - passed

    print(f"\nResults: {passed}/{total} tests passed")

    if failed > 0:
        print(f"\n⚠️  {failed} test(s) failed - see details above")

        # Provide recommendations
        print("\n" + "="*80)
        print("RECOMMENDATIONS")
        print("="*80 + "\n")

        if not results['Steam API'] or not results['SteamSpy API']:
            print("📋 Install missing dependencies:")
            print("   pip install beautifulsoup4 lxml requests")

        if not results['Claude API Config']:
            print("\n📋 Set up Claude API:")
            print("   export ANTHROPIC_API_KEY='your-api-key-here'")
            print("   pip install anthropic")

        print("\n📋 Some tests require internet connectivity and working APIs")

    else:
        print("\n🎉 All tests passed! System is ready for use.")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
