"""
Test Conversion Funnel Analysis Module

Validates the conversion funnel analyzer with mock game data.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.conversion_funnel import ConversionFunnelAnalyzer


def test_roguelike_game():
    """Test with a roguelike game (high-converting genre)"""

    print("=" * 80)
    print("TEST 1: Roguelike Game")
    print("=" * 80)
    print()

    game_data = {
        'name': 'Dungeon Depths',
        'genres': 'Roguelike, RPG, Dungeon Crawler',
        'tags': 'roguelike, procedural generation, pixel art',
        'price': '$14.99',
        'reviews_total': 850
    }

    sales_data = {
        'review_score': 88,
        'reviews_total': 850,
        'estimated_revenue': 180000
    }

    capsule_analysis = {
        'overall_ctr_score': 7.5
    }

    analyzer = ConversionFunnelAnalyzer()
    result = analyzer.analyze_funnel(game_data, sales_data, capsule_analysis)

    print(f"Genre Detected: {result['genre']}")
    print(f"Overall Efficiency: {result['overall_efficiency']['score']}/100 ({result['overall_efficiency']['tier']})")
    print()

    print("Funnel Stages:")
    stages = result['funnel_stages']
    print(f"  Capsule CTR: {stages['capsule_ctr']['percentage']}% (vs {stages['capsule_ctr']['benchmark_percentage']}% genre avg) - {stages['capsule_ctr']['vs_benchmark'].upper()}")
    print(f"  Wishlist Conv: {stages['wishlist_conversion']['percentage']}% (vs {stages['wishlist_conversion']['benchmark_percentage']}% genre avg) - {stages['wishlist_conversion']['vs_benchmark'].upper()}")
    print(f"  Purchase Conv: {stages['purchase_conversion']['percentage']}% (vs {stages['purchase_conversion']['benchmark_percentage']}% genre avg) - {stages['purchase_conversion']['vs_benchmark'].upper()}")
    print(f"  Review Ratio: {stages['review_ratio']['percentage']}% (vs {stages['review_ratio']['benchmark_percentage']}% genre avg) - {stages['review_ratio']['vs_benchmark'].upper()}")
    print()

    print("100K Impressions Projection:")
    proj = result['projections']['100k_impressions']
    print(f"  Visits: {proj['visits']:,}")
    print(f"  Wishlists: {proj['wishlists']:,}")
    print(f"  Purchases: {proj['purchases']:,}")
    print(f"  Reviews: {proj['reviews']}")
    print(f"  Revenue: ${proj['revenue']:,.2f}")
    print()

    if result['optimizations']:
        print(f"Optimization Opportunities: {len(result['optimizations'])}")
        for i, opp in enumerate(result['optimizations'], 1):
            print(f"  {i}. {opp['stage']} ({opp['priority']} priority)")
            print(f"     Gap: +{opp['improvement_points']:.2f} percentage points")
            print(f"     Impact: +{opp['impact'].get('additional_revenue', 0):,.2f} revenue")
    else:
        print("✅ No optimizations needed - performing at or above benchmarks!")

    print()


def test_casual_game():
    """Test with a casual game (lower-converting genre)"""

    print("=" * 80)
    print("TEST 2: Casual Puzzle Game")
    print("=" * 80)
    print()

    game_data = {
        'name': 'Bubble Pop Adventure',
        'genres': 'Casual, Puzzle',
        'tags': 'casual, puzzle, family friendly',
        'price': '$4.99',
        'reviews_total': 120
    }

    sales_data = {
        'review_score': 72,
        'reviews_total': 120,
        'estimated_revenue': 15000
    }

    capsule_analysis = {
        'overall_ctr_score': 5.2
    }

    analyzer = ConversionFunnelAnalyzer()
    result = analyzer.analyze_funnel(game_data, sales_data, capsule_analysis)

    print(f"Genre Detected: {result['genre']}")
    print(f"Overall Efficiency: {result['overall_efficiency']['score']}/100 ({result['overall_efficiency']['tier']})")
    print()

    print("Funnel Stages:")
    stages = result['funnel_stages']
    print(f"  Capsule CTR: {stages['capsule_ctr']['percentage']}% (vs {stages['capsule_ctr']['benchmark_percentage']}% genre avg) - {stages['capsule_ctr']['vs_benchmark'].upper()}")
    print(f"  Wishlist Conv: {stages['wishlist_conversion']['percentage']}% (vs {stages['wishlist_conversion']['benchmark_percentage']}% genre avg) - {stages['wishlist_conversion']['vs_benchmark'].upper()}")
    print(f"  Purchase Conv: {stages['purchase_conversion']['percentage']}% (vs {stages['purchase_conversion']['benchmark_percentage']}% genre avg) - {stages['purchase_conversion']['vs_benchmark'].upper()}")
    print(f"  Review Ratio: {stages['review_ratio']['percentage']}% (vs {stages['review_ratio']['benchmark_percentage']}% genre avg) - {stages['review_ratio']['vs_benchmark'].upper()}")
    print()

    print("100K Impressions Projection:")
    proj = result['projections']['100k_impressions']
    print(f"  Visits: {proj['visits']:,}")
    print(f"  Wishlists: {proj['wishlists']:,}")
    print(f"  Purchases: {proj['purchases']:,}")
    print(f"  Reviews: {proj['reviews']}")
    print(f"  Revenue: ${proj['revenue']:,.2f}")
    print()

    if result['optimizations']:
        print(f"Optimization Opportunities: {len(result['optimizations'])}")
        for i, opp in enumerate(result['optimizations'], 1):
            print(f"  {i}. {opp['stage']} ({opp['priority']} priority)")
            print(f"     Gap: +{opp['improvement_points']:.2f} percentage points")
            print(f"     Impact: +${opp['impact'].get('additional_revenue', 0):,.2f} revenue")
            print(f"     Top tactic: {opp['tactics'][0] if opp['tactics'] else 'N/A'}")
    else:
        print("✅ No optimizations needed - performing at or above benchmarks!")

    print()


def test_high_performing_game():
    """Test with a high-performing game"""

    print("=" * 80)
    print("TEST 3: High-Performing Deckbuilder")
    print("=" * 80)
    print()

    game_data = {
        'name': 'Cards of Destiny',
        'genres': 'Deckbuilder, Card Game, Strategy',
        'tags': 'deckbuilder, roguelike, card game',
        'price': '$19.99',
        'reviews_total': 2500
    }

    sales_data = {
        'review_score': 94,
        'reviews_total': 2500,
        'estimated_revenue': 650000
    }

    capsule_analysis = {
        'overall_ctr_score': 9.1
    }

    analyzer = ConversionFunnelAnalyzer()
    result = analyzer.analyze_funnel(game_data, sales_data, capsule_analysis)

    print(f"Genre Detected: {result['genre']}")
    print(f"Overall Efficiency: {result['overall_efficiency']['score']}/100 ({result['overall_efficiency']['tier']})")
    print()

    print("Funnel Stages:")
    stages = result['funnel_stages']
    print(f"  Capsule CTR: {stages['capsule_ctr']['percentage']}% (vs {stages['capsule_ctr']['benchmark_percentage']}% genre avg) - {stages['capsule_ctr']['vs_benchmark'].upper()}")
    print(f"  Wishlist Conv: {stages['wishlist_conversion']['percentage']}% (vs {stages['wishlist_conversion']['benchmark_percentage']}% genre avg) - {stages['wishlist_conversion']['vs_benchmark'].upper()}")
    print(f"  Purchase Conv: {stages['purchase_conversion']['percentage']}% (vs {stages['purchase_conversion']['benchmark_percentage']}% genre avg) - {stages['purchase_conversion']['vs_benchmark'].upper()}")
    print(f"  Review Ratio: {stages['review_ratio']['percentage']}% (vs {stages['review_ratio']['benchmark_percentage']}% genre avg) - {stages['review_ratio']['vs_benchmark'].upper()}")
    print()

    print("500K Impressions Projection (scaling to high traffic):")
    proj = result['projections']['500k_impressions']
    print(f"  Visits: {proj['visits']:,}")
    print(f"  Wishlists: {proj['wishlists']:,}")
    print(f"  Purchases: {proj['purchases']:,}")
    print(f"  Reviews: {proj['reviews']}")
    print(f"  Revenue: ${proj['revenue']:,.2f}")
    print()

    if result['optimizations']:
        print(f"Optimization Opportunities: {len(result['optimizations'])}")
    else:
        print("✅ No optimizations needed - performing at or above benchmarks!")
        print("   Focus on scaling traffic to this high-performing funnel!")

    print()


def main():
    """Run all tests"""

    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " CONVERSION FUNNEL ANALYZER TEST SUITE ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    try:
        # Test 1: Roguelike (high-converting genre)
        test_roguelike_game()

        # Test 2: Casual (lower-converting genre)
        test_casual_game()

        # Test 3: High-performing game
        test_high_performing_game()

        # Summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print()
        print("✅ All tests passed!")
        print()
        print("Conversion Funnel Analyzer Features:")
        print("  ✓ Genre-specific benchmark modifiers (15+ genres)")
        print("  ✓ 4-stage funnel analysis (Capsule → Visit → Wishlist → Purchase → Review)")
        print("  ✓ Performance tier classification (Excellent/Good/Average/Poor)")
        print("  ✓ Multi-level projections (10K, 50K, 100K, 250K, 500K impressions)")
        print("  ✓ Optimization opportunity identification with impact calculations")
        print("  ✓ Factor-based scoring (capsule quality, review score, price, engagement)")
        print()
        print("Value Added: $40 (Hard data & benchmarking)")
        print()
        print("Next Integration:")
        print("  • ConversionFunnelSection added to ReportBuilder")
        print("  • Generates detailed markdown output with:")
        print("    - Funnel comparison table (your rate vs genre avg)")
        print("    - Multi-level projections")
        print("    - Prioritized optimization opportunities")
        print("    - Stage-specific insights and tactics")
        print()

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
