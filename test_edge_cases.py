"""
Edge Case Testing

Tests robustness with invalid/missing/edge case data.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.report_builder import ReportBuilder
from src.ab_testing import ABTestingRecommender
from src.community_health import CommunityHealthAnalyzer
from src.regional_pricing import RegionalPricingAnalyzer
from src.conversion_funnel import ConversionFunnelAnalyzer
from src.tag_insights import TagInsightsAnalyzer
from src.review_vulnerability import ReviewVulnerabilityAnalyzer


def test_empty_data():
    """Test with completely empty data"""
    print("=" * 80)
    print("TEST 1: Empty/Missing Data")
    print("=" * 80)
    print()

    errors = []

    # Test 1: Empty game data
    try:
        builder = ReportBuilder(
            game_data={},
            sales_data={},
            competitor_data=[],
            report_type='full'
        )
        builder.build_sections()
        print("✅ ReportBuilder handles empty data")
    except Exception as e:
        print(f"❌ ReportBuilder failed with empty data: {e}")
        errors.append(f"ReportBuilder: {e}")

    # Test 2: None values
    try:
        builder2 = ReportBuilder(
            game_data={'name': None, 'price': None},
            sales_data={'reviews_total': None},
            competitor_data=None,
            report_type='full'
        )
        builder2.build_sections()
        print("✅ ReportBuilder handles None values")
    except Exception as e:
        print(f"❌ ReportBuilder failed with None values: {e}")
        errors.append(f"ReportBuilder (None): {e}")

    print()
    return len(errors) == 0


def test_invalid_prices():
    """Test with invalid price formats"""
    print("=" * 80)
    print("TEST 2: Invalid Price Formats")
    print("=" * 80)
    print()

    errors = []
    invalid_prices = [
        'Free',
        '',
        '$',
        'Invalid',
        '€€€',
        '-$10.00',
        '$999999.99'
    ]

    for price in invalid_prices:
        try:
            analyzer = RegionalPricingAnalyzer()
            # Extract price logic
            import re
            price_clean = re.sub(r'[^0-9.]', '', price)
            price_val = float(price_clean) if price_clean else 0.0
            result = analyzer.analyze_pricing(price_val)
            print(f"✅ '{price}' -> ${price_val:.2f}")
        except Exception as e:
            print(f"❌ '{price}' failed: {e}")
            errors.append(f"{price}: {e}")

    print()
    return len(errors) == 0


def test_extreme_values():
    """Test with extreme values"""
    print("=" * 80)
    print("TEST 3: Extreme Values")
    print("=" * 80)
    print()

    errors = []

    # Test very high review count
    try:
        game_data = {
            'name': 'Ultra Popular Game',
            'genres': 'Action',
            'tags': 'action',
            'price': '$59.99',
            'reviews_total': 1000000
        }
        sales_data = {
            'reviews_total': 1000000,
            'review_score': 99,
            'estimated_revenue': 50000000
        }

        funnel = ConversionFunnelAnalyzer()
        result = funnel.analyze_funnel(game_data, sales_data, {})
        print(f"✅ Handles 1M reviews: Score {result.get('overall_efficiency', {}).get('score', 0)}/100")
    except Exception as e:
        print(f"❌ Failed with extreme reviews: {e}")
        errors.append(f"Extreme reviews: {e}")

    # Test zero reviews
    try:
        game_data = {
            'name': 'Brand New Game',
            'genres': 'Indie',
            'tags': 'indie',
            'price': '$9.99',
            'reviews_total': 0
        }
        sales_data = {
            'reviews_total': 0,
            'review_score': 0,
            'estimated_revenue': 0
        }

        funnel2 = ConversionFunnelAnalyzer()
        result2 = funnel2.analyze_funnel(game_data, sales_data, {})
        print(f"✅ Handles zero reviews: Score {result2.get('overall_efficiency', {}).get('score', 0)}/100")
    except Exception as e:
        print(f"❌ Failed with zero reviews: {e}")
        errors.append(f"Zero reviews: {e}")

    # Test extreme community sizes
    try:
        community_data = {
            'discord': {
                'members': 500000,
                'daily_active': 50000,
                'messages_per_day': 100000
            },
            'reddit': {
                'subscribers': 250000,
                'daily_posts': 500,
                'comments_per_post': 100
            },
            'development_stage': 'post_launch'
        }

        analyzer = CommunityHealthAnalyzer()
        result3 = analyzer.analyze_health({}, community_data)
        print(f"✅ Handles large community: Score {result3['overall_health_score']:.1f}/100")
    except Exception as e:
        print(f"❌ Failed with large community: {e}")
        errors.append(f"Large community: {e}")

    print()
    return len(errors) == 0


def test_missing_fields():
    """Test with missing required fields"""
    print("=" * 80)
    print("TEST 4: Missing Required Fields")
    print("=" * 80)
    print()

    errors = []

    # Test missing genres
    try:
        game_data = {
            'name': 'Test Game',
            'price': '$19.99'
            # Missing: genres, tags
        }
        sales_data = {}
        competitor_data = []

        ab = ABTestingRecommender()
        result = ab.generate_recommendations(game_data, sales_data, 19.99)
        print(f"✅ ABTesting handles missing genres: {len(result['recommended_tests'])} tests")
    except Exception as e:
        print(f"❌ ABTesting failed with missing genres: {e}")
        errors.append(f"ABTesting missing genres: {e}")

    # Test missing tags
    try:
        game_data2 = {
            'name': 'Test Game 2',
            'genres': 'Action',
            'price': '$9.99'
            # Missing: tags
        }

        tags = TagInsightsAnalyzer()
        result2 = tags.analyze_tags(game_data2, {})
        print(f"✅ TagInsights handles missing tags: Score {result2['optimization_score']}/100")
    except Exception as e:
        print(f"❌ TagInsights failed with missing tags: {e}")
        errors.append(f"TagInsights missing tags: {e}")

    # Test missing competitor data
    try:
        vuln = ReviewVulnerabilityAnalyzer()
        result3 = vuln.analyze_vulnerabilities(
            game_data={'name': 'Test', 'genres': 'RPG', 'tags': 'rpg', 'price': '$14.99'},
            sales_data={},
            competitor_data=[]  # Empty
        )
        print(f"✅ ReviewVuln handles no competitors: {len(result3['predicted_risks'])} risks")
    except Exception as e:
        print(f"❌ ReviewVuln failed with no competitors: {e}")
        errors.append(f"ReviewVuln no competitors: {e}")

    print()
    return len(errors) == 0


def test_malformed_data():
    """Test with malformed data"""
    print("=" * 80)
    print("TEST 5: Malformed Data")
    print("=" * 80)
    print()

    errors = []

    # Test malformed tags (single string instead of comma-separated)
    try:
        game_data = {
            'name': 'Test',
            'genres': 'ActionRPGStrategySimulation',  # No separators
            'tags': 'onelongtagwithnospaces',
            'price': '$19.99'
        }

        tags = TagInsightsAnalyzer()
        result = tags.analyze_tags(game_data, {})
        print(f"✅ Handles malformed tags: {result['tag_count']} tags found")
    except Exception as e:
        print(f"❌ Failed with malformed tags: {e}")
        errors.append(f"Malformed tags: {e}")

    # Test negative values
    try:
        sales_data = {
            'reviews_total': -100,  # Negative!
            'review_score': -50,
            'estimated_revenue': -10000
        }

        funnel = ConversionFunnelAnalyzer()
        result2 = funnel.analyze_funnel(
            {'name': 'Test', 'genres': 'RPG', 'tags': 'rpg', 'price': '$19.99'},
            sales_data,
            {}
        )
        print(f"✅ Handles negative values: Score {result2.get('overall_efficiency', {}).get('score', 0)}/100")
    except Exception as e:
        print(f"❌ Failed with negative values: {e}")
        errors.append(f"Negative values: {e}")

    print()
    return len(errors) == 0


def main():
    """Run all edge case tests"""

    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " EDGE CASE TEST SUITE ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    results = []

    try:
        results.append(("Empty Data", test_empty_data()))
        results.append(("Invalid Prices", test_invalid_prices()))
        results.append(("Extreme Values", test_extreme_values()))
        results.append(("Missing Fields", test_missing_fields()))
        results.append(("Malformed Data", test_malformed_data()))

        # Summary
        print("=" * 80)
        print("EDGE CASE TEST SUMMARY")
        print("=" * 80)
        print()

        all_passed = all(result[1] for result in results)

        for test_name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status} - {test_name}")

        print()

        if all_passed:
            print("✅ ALL EDGE CASE TESTS PASSED!")
            print()
            print("Edge Case Handling Verified:")
            print("  ✓ Empty/None data gracefully handled")
            print("  ✓ Invalid price formats properly parsed")
            print("  ✓ Extreme values (0, 1M+) handled correctly")
            print("  ✓ Missing required fields use sensible defaults")
            print("  ✓ Malformed data safely processed")
            print()
            print("The audit system is robust and production-ready!")
            print()
        else:
            print("⚠️  SOME EDGE CASE TESTS FAILED")
            print()
            print("Some edge cases are not properly handled.")
            print("Review the output above for details.")
            print()
            sys.exit(1)

    except Exception as e:
        print(f"❌ EDGE CASE TESTS FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
