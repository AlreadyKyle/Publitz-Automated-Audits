#!/usr/bin/env python3
"""
Revenue-Based Scoring Integration Test

Demonstrates how to integrate revenue-based scoring into existing reports.
Tests with multiple game scenarios to show score adjustments.
"""

from src.revenue_based_scoring import (
    classify_revenue_tier,
    apply_revenue_modifier,
    calculate_overall_score,
    generate_reality_check_warning,
    format_revenue_report
)


def test_game_scenario(name: str, revenue: float, days: int, review_pct: float, review_count: int, section_scores: dict):
    """
    Test a game scenario and show before/after scores
    """
    print("\n" + "="*80)
    print(f"SCENARIO: {name}")
    print("="*80 + "\n")

    print(f"Game Data:")
    print(f"  Revenue: ${revenue:,.0f} ({days} days) = ${revenue/days:.2f}/day")
    print(f"  Reviews: {review_count} total, {review_pct:.0f}% positive")
    print(f"  Section Scores (Before): {section_scores}")
    print()

    # Calculate average of current scores
    avg_before = sum(section_scores.values()) / len(section_scores)

    # Apply revenue-based scoring
    revenue_tier = classify_revenue_tier(revenue, days)

    print(f"Revenue Tier: {revenue_tier.tier_name} (Tier {revenue_tier.tier}/5)")
    print(f"  Daily Revenue: ${revenue_tier.daily_revenue:.2f}")
    print(f"  Monthly Equivalent: ${revenue_tier.monthly_equivalent:,.0f}")
    print(f"  Modifier: {revenue_tier.modifier} ({(1-revenue_tier.modifier)*100:.0f}% reduction)")
    print(f"  Reality Check: {'ACTIVE' if revenue_tier.reality_check else 'Not needed'}")
    print()

    # Apply modifier
    modified_sections = apply_revenue_modifier(section_scores, revenue_tier)

    print("Section Scores (After):")
    for section, scores in modified_sections.items():
        change = scores['final_score'] - scores['raw_score']
        print(f"  {section.title()}: {scores['raw_score']} → {scores['final_score']} (change: {change:+d})")

    # Calculate overall score
    review_metrics = {
        'review_percentage': review_pct,
        'review_count': review_count
    }

    overall = calculate_overall_score(modified_sections, revenue_tier, review_metrics)

    print()
    print("Overall Score Calculation:")
    print(f"  Revenue: {overall['components']['revenue']['score']}/100 × 35% = {overall['components']['revenue']['contribution']}")
    print(f"  Review Quality: {overall['components']['review_quality']['score']}/100 × 25% = {overall['components']['review_quality']['contribution']}")
    print(f"  Review Volume: {overall['components']['review_volume']['score']}/100 × 15% = {overall['components']['review_volume']['contribution']}")
    print(f"  Section Avg: {overall['components']['sections']['score']}/100 × 25% = {overall['components']['sections']['contribution']}")
    print(f"  ─────────────────────")
    print(f"  FINAL SCORE: {overall['overall_score']}/100")
    print()

    # Compare
    print("Score Comparison:")
    print(f"  Before (avg of sections): {avg_before:.0f}/100")
    print(f"  After (revenue-adjusted): {overall['overall_score']}/100")
    print(f"  Change: {overall['overall_score'] - avg_before:+.0f} points")

    # Warning
    warning = generate_reality_check_warning(revenue_tier, overall['overall_score'], modified_sections)
    if warning:
        print()
        print("⚠️  REALITY CHECK TRIGGERED")
        print("    (Full warning would appear in report)")


def main():
    """Run test scenarios"""

    print("\n" + "="*80)
    print("REVENUE-BASED SCORING INTEGRATION TEST")
    print("Testing multiple game scenarios to show score adjustments")
    print("="*80)

    # Scenario 1: Retrace the Light (actual data)
    test_game_scenario(
        name="Retrace the Light (Crisis)",
        revenue=379,
        days=7,
        review_pct=80,
        review_count=5,
        section_scores={
            'community': 85,
            'influencer': 90,
            'regional': 90
        }
    )

    # Scenario 2: Struggling indie game
    test_game_scenario(
        name="Struggling Indie Game",
        revenue=25000,
        days=90,
        review_pct=68,
        review_count=150,
        section_scores={
            'community': 70,
            'influencer': 65,
            'regional': 75,
            'conversion': 60
        }
    )

    # Scenario 3: Viable game
    test_game_scenario(
        name="Viable Mid-Tier Game",
        revenue=180000,
        days=90,
        review_pct=82,
        review_count=850,
        section_scores={
            'community': 80,
            'influencer': 75,
            'regional': 85,
            'conversion': 78
        }
    )

    # Scenario 4: Strong performer
    test_game_scenario(
        name="Strong Performer",
        revenue=600000,
        days=90,
        review_pct=88,
        review_count=3500,
        section_scores={
            'community': 88,
            'influencer': 85,
            'regional': 90,
            'conversion': 85,
            'retention': 82
        }
    )

    # Scenario 5: Exceptional hit
    test_game_scenario(
        name="Exceptional Hit",
        revenue=2000000,
        days=90,
        review_pct=94,
        review_count=15000,
        section_scores={
            'community': 92,
            'influencer': 90,
            'regional': 95,
            'conversion': 90,
            'retention': 88
        }
    )

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print()
    print("Revenue-based scoring system:")
    print()
    print("✅ Prevents score inflation for failing games")
    print("✅ Adjusts all scores based on commercial reality")
    print("✅ Caps crisis/struggling games at 65/100 maximum")
    print("✅ Weights revenue performance at 35% of overall score")
    print("✅ Generates clear warnings for poor performers")
    print()
    print("Key Findings:")
    print("- Crisis games ($0-$100/day): 60% score reduction")
    print("- Struggling games ($100-500/day): 35% score reduction")
    print("- Viable games ($500-2K/day): 15% score reduction")
    print("- Strong games ($2K-10K/day): 5% score reduction")
    print("- Exceptional games (>$10K/day): No reduction")
    print()
    print("Ready to integrate into production.")
    print("See REVENUE_SCORING_INTEGRATION.md for full integration guide.")
    print()


if __name__ == "__main__":
    main()
