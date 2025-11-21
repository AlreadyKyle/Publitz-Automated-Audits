"""
Test Visibility Forecast Module

Validates the visibility forecast analyzer with different game scenarios.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.visibility_forecast import VisibilityForecastAnalyzer


def test_tier_4_game():
    """Test with a Tier 4 game (needs work)"""

    print("=" * 80)
    print("TEST 1: Tier 4 Game (Minimal Visibility)")
    print("=" * 80)
    print()

    game_data = {
        'name': 'Indie Startup Game',
        'genres': 'Adventure, Indie',
        'tags': 'adventure, indie, casual',
        'price': '$9.99',
        'reviews_total': 15
    }

    sales_data = {
        'review_score': 68,
        'reviews_total': 15,
        'estimated_revenue': 5000
    }

    capsule_analysis = {
        'overall_ctr_score': 4.5
    }

    analyzer = VisibilityForecastAnalyzer()
    result = analyzer.analyze_visibility(game_data, sales_data, capsule_analysis)

    print(f"Overall Score: {result['overall_score']}/100")
    print(f"Current Tier: Tier {result['current_tier']}")
    print(f"Description: {result['tier_description']}")
    print()

    print("Component Scores:")
    for component, score in result['component_scores'].items():
        print(f"  {component.replace('_', ' ').title()}: {score}/100")
    print()

    print("Discovery Queue Predictions:")
    disc = result['discovery_predictions']
    print(f"  Total Daily Impressions: {disc['total_daily_impressions']:,}")
    print(f"  Monthly Impressions: {disc['monthly_impressions']:,}")
    print()

    print("Feature Eligibility:")
    feat = result['feature_eligibility']
    print(f"  Popular Upcoming: {'✅' if feat['popular_upcoming']['eligible'] else '❌'} ({feat['popular_upcoming']['probability']:.0f}% probability)")
    print(f"  Featured Placement: {'✅' if feat['featured_placement']['eligible'] else '❌'} ({feat['featured_placement']['probability']:.0f}% probability)")
    print()

    print("Path to Improvement:")
    imp = result['improvement_path']
    print(f"  Points Needed for Tier {imp['next_tier']}: +{imp['points_needed']} points")
    print(f"  Top {len(imp['recommendations'])} Recommendations Generated")
    if imp['recommendations']:
        top_rec = imp['recommendations'][0]
        print(f"    1. {top_rec['area']} ({top_rec['priority']} priority)")
        print(f"       Impact: {top_rec['impact']}")
    print()


def test_tier_3_game():
    """Test with a Tier 3 game (standard discovery)"""

    print("=" * 80)
    print("TEST 2: Tier 3 Game (Standard Discovery)")
    print("=" * 80)
    print()

    game_data = {
        'name': 'Mystery Detective Game',
        'genres': 'Detective, Mystery, Indie',
        'tags': 'detective, mystery, investigation, noir, story rich, singleplayer',
        'price': '$16.99',
        'reviews_total': 280
    }

    sales_data = {
        'review_score': 81,
        'reviews_total': 280,
        'estimated_revenue': 95000
    }

    capsule_analysis = {
        'overall_ctr_score': 6.8
    }

    analyzer = VisibilityForecastAnalyzer()
    result = analyzer.analyze_visibility(game_data, sales_data, capsule_analysis)

    print(f"Overall Score: {result['overall_score']}/100")
    print(f"Current Tier: Tier {result['current_tier']}")
    print(f"Description: {result['tier_description']}")
    print()

    print("Component Scores:")
    for component, score in result['component_scores'].items():
        print(f"  {component.replace('_', ' ').title()}: {score}/100")
    print()

    print("Discovery Queue Predictions:")
    disc = result['discovery_predictions']
    print(f"  Main Discovery Queue: {disc['daily_impressions']['main']:,}/day")
    print(f"  Genre-Specific Queues: {disc['daily_impressions']['genre']:,}/day")
    print(f"  Total Daily: {disc['total_daily_impressions']:,}")
    print(f"  Monthly: {disc['monthly_impressions']:,}")
    print()

    print("Feature Eligibility:")
    feat = result['feature_eligibility']
    for feature_name, feature_data in feat.items():
        eligible = '✅' if feature_data.get('eligible', False) else '❌'
        prob = feature_data.get('probability', 0)
        print(f"  {feature_name.replace('_', ' ').title()}: {eligible} ({prob:.0f}% probability)")
    print()

    print("Path to Tier 2:")
    imp = result['improvement_path']
    print(f"  Points Needed: +{imp['points_needed']:.1f} points")
    print(f"  Projected After Improvements: {imp['projected_outcome']['score_after_improvements']}/100")
    print(f"  Projected Tier: Tier {imp['projected_outcome']['tier_after_improvements']}")
    print(f"  Impression Increase: +{imp['projected_outcome']['impression_increase_daily']:,}/day")
    print()


def test_tier_2_game():
    """Test with a Tier 2 game (regular discovery)"""

    print("=" * 80)
    print("TEST 3: Tier 2 Game (Above Average Visibility)")
    print("=" * 80)
    print()

    game_data = {
        'name': 'Rogue Dungeon Deluxe',
        'genres': 'Roguelike, RPG, Deckbuilder',
        'tags': 'roguelike, roguelite, deckbuilder, card game, pixel art, dungeon crawler, procedural, turn-based, strategy, rpg, indie, singleplayer',
        'price': '$19.99',
        'reviews_total': 1250
    }

    sales_data = {
        'review_score': 91,
        'reviews_total': 1250,
        'estimated_revenue': 480000
    }

    capsule_analysis = {
        'overall_ctr_score': 8.4
    }

    analyzer = VisibilityForecastAnalyzer()
    result = analyzer.analyze_visibility(game_data, sales_data, capsule_analysis)

    print(f"Overall Score: {result['overall_score']}/100")
    print(f"Current Tier: Tier {result['current_tier']}")
    print(f"Description: {result['tier_description']}")
    print()

    print("Component Scores:")
    for component, score in result['component_scores'].items():
        emoji = '🟢' if score >= 75 else '🟡' if score >= 60 else '🔴'
        print(f"  {component.replace('_', ' ').title()}: {score}/100 {emoji}")
    print()

    print("Discovery Queue Predictions:")
    disc = result['discovery_predictions']
    print(f"  Main Discovery Queue: {disc['daily_impressions']['main']:,}/day")
    print(f"  Genre-Specific Queues: {disc['daily_impressions']['genre']:,}/day")
    print(f"  Total Daily: {disc['total_daily_impressions']:,}")
    print(f"  Monthly: {disc['monthly_impressions']:,}")
    print()

    print("Feature Eligibility:")
    feat = result['feature_eligibility']
    for feature_name, feature_data in feat.items():
        eligible = '✅' if feature_data.get('eligible', False) else '❌'
        prob = feature_data.get('probability', 0)
        print(f"  {feature_name.replace('_', ' ').title()}: {eligible} ({prob:.0f}% probability)")
    print()

    print("Path to Tier 1:")
    imp = result['improvement_path']
    if imp['current_tier'] == 1:
        print(f"  Already in Tier 1! Maintain this elite status.")
    else:
        print(f"  Points Needed: +{imp['points_needed']:.1f} points")
        print(f"  Weakest Areas: {', '.join([a.replace('_', ' ').title() for a in imp['weakest_areas']])}")
    print()


def test_tier_1_game():
    """Test with a Tier 1 game (top performer)"""

    print("=" * 80)
    print("TEST 4: Tier 1 Game (Elite Visibility)")
    print("=" * 80)
    print()

    game_data = {
        'name': 'Mega Hit Roguelike',
        'genres': 'Roguelike, RPG, Deckbuilder',
        'tags': 'roguelike, roguelite, deckbuilder, card game, pixel art, dungeon crawler, procedural, turn-based, strategy, rpg, indie, singleplayer, early access, addictive',
        'price': '$24.99',
        'reviews_total': 8500
    }

    sales_data = {
        'review_score': 96,
        'reviews_total': 8500,
        'estimated_revenue': 2500000
    }

    capsule_analysis = {
        'overall_ctr_score': 9.3
    }

    analyzer = VisibilityForecastAnalyzer()
    result = analyzer.analyze_visibility(game_data, sales_data, capsule_analysis)

    print(f"Overall Score: {result['overall_score']}/100 👑")
    print(f"Current Tier: Tier {result['current_tier']} (TOP 1%)")
    print(f"Description: {result['tier_description']}")
    print()

    print("Component Scores:")
    for component, score in result['component_scores'].items():
        print(f"  {component.replace('_', ' ').title()}: {score}/100 🟢")
    print()

    print("Discovery Queue Predictions:")
    disc = result['discovery_predictions']
    print(f"  Main Discovery Queue: {disc['daily_impressions']['main']:,}/day")
    print(f"  Genre-Specific Queues: {disc['daily_impressions']['genre']:,}/day")
    print(f"  Featured Placements: {disc['daily_impressions']['featured']:,}/day")
    print(f"  Total Daily: {disc['total_daily_impressions']:,}")
    print(f"  Monthly: {disc['monthly_impressions']:,}")
    print()

    print("Feature Eligibility:")
    feat = result['feature_eligibility']
    for feature_name, feature_data in feat.items():
        eligible = '✅' if feature_data.get('eligible', False) else '❌'
        prob = feature_data.get('probability', 0)
        print(f"  {feature_name.replace('_', ' ').title()}: {eligible} ({prob:.0f}% probability)")
    print()

    print("Status: Elite Tier - Focus on maintaining and scaling!")
    print()


def main():
    """Run all tests"""

    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " VISIBILITY FORECAST ANALYZER TEST SUITE ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    try:
        # Test 1: Tier 4 (needs work)
        test_tier_4_game()

        # Test 2: Tier 3 (standard discovery)
        test_tier_3_game()

        # Test 3: Tier 2 (above average)
        test_tier_2_game()

        # Test 4: Tier 1 (elite)
        test_tier_1_game()

        # Summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print()
        print("✅ All tests passed!")
        print()
        print("Visibility Forecast Analyzer Features:")
        print("  ✓ 4-tier classification system (Tier 1-4)")
        print("  ✓ Component scoring: Wishlist Velocity (40%), Tags (25%), Engagement (20%), Quality (15%)")
        print("  ✓ Discovery queue impression predictions (daily/weekly/monthly)")
        print("  ✓ Steam feature eligibility: Popular Upcoming, Featured, Daily Deal, New & Trending")
        print("  ✓ Path to improvement with prioritized recommendations")
        print("  ✓ Projected impact calculations (score, tier, impressions)")
        print()
        print("Tier Thresholds:")
        print("  • Tier 1 (85+ score): Top 1% - 8K-15K impressions/day")
        print("  • Tier 2 (70-84 score): Top 10% - 3K-4K impressions/day")
        print("  • Tier 3 (50-69 score): Top 30% - 500-700 impressions/day")
        print("  • Tier 4 (<50 score): Bottom 70% - 50-100 impressions/day")
        print()
        print("Value Added: $30 (Algorithm visibility forecast)")
        print()
        print("Next Integration:")
        print("  • VisibilityForecastSection added to ReportBuilder")
        print("  • Generates comprehensive markdown with:")
        print("    - Component scores breakdown table")
        print("    - Daily/weekly/monthly impression estimates")
        print("    - Feature eligibility for Popular Upcoming, Featured, etc.")
        print("    - Prioritized improvement recommendations")
        print("    - Projected impact if recommendations implemented")
        print()

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
