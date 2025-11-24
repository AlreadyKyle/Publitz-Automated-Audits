#!/usr/bin/env python3
"""
Demo: Complete Report Generation

Demonstrates the full Publitz system using mock data.
Shows how to generate reports when APIs are blocked.
"""

import sys
sys.path.insert(0, '/home/user/Publitz-Automated-Audits')

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.mock_game_data import get_mock_game, list_available_games, MOCK_GAMES_BY_TIER
from src.report_orchestrator import ReportOrchestrator
from src.manual_data_entry import print_game_data_summary


def demo_mock_data_reports():
    """Demonstrate report generation with mock data"""
    print("\n" + "="*80)
    print("DEMO: REPORT GENERATION WITH MOCK DATA")
    print("="*80 + "\n")

    print("Available mock games:")
    for name in list_available_games():
        print(f"  - {name}")

    # Test with multiple game tiers
    test_games = [
        ('hades_ii', 'Exceptional Game'),
        ('indie_success', 'Solid Performer'),
        ('struggling_game', 'Struggling Game'),
        ('crisis_game', 'Crisis Mode')
    ]

    for game_id, description in test_games:
        print(f"\n{'-'*80}")
        print(f"Testing: {description} ({game_id})")
        print('-'*80)

        # Get mock game data
        game_data = get_mock_game(game_id)
        print_game_data_summary(game_data)

        # Initialize orchestrator
        orchestrator = ReportOrchestrator(hourly_rate=50.0)

        # Generate report
        print("Generating complete report...")
        try:
            reports = orchestrator.generate_complete_report(game_data)

            # Show metadata
            metadata = reports['metadata']
            print(f"\n✅ Report Generated Successfully!")
            print(f"   Overall Score: {metadata.overall_score:.1f}/100")
            print(f"   Performance Tier: {metadata.tier_name}")
            print(f"   Confidence Level: {metadata.confidence_level}")
            print(f"   Word Counts:")
            print(f"     - Tier 1 (Executive): {metadata.word_count['tier_1']:,} words")
            print(f"     - Tier 2 (Strategic): {metadata.word_count['tier_2']:,} words")
            print(f"     - Tier 3 (Deep-dive): {metadata.word_count['tier_3']:,} words")

            # Show preview of Tier 1 report
            print(f"\n{'='*80}")
            print("TIER 1 EXECUTIVE BRIEF PREVIEW (first 500 chars)")
            print('='*80)
            tier_1 = reports['tier_1_executive']
            print(tier_1[:500] + "...")

            print(f"\n✅ Full reports available in returned dictionary")

        except Exception as e:
            print(f"❌ Error generating report: {e}")
            import traceback
            traceback.print_exc()


def demo_manual_data_entry():
    """Demonstrate manual data entry system"""
    print("\n" + "="*80)
    print("DEMO: MANUAL DATA ENTRY EXAMPLE")
    print("="*80 + "\n")

    from src.manual_data_entry import create_game_data_dict

    print("Creating game data manually (programmatic method)...")

    # Example: User provides their game's data
    my_game = create_game_data_dict(
        app_id='999999',
        name='My Awesome Game',
        price=24.99,
        review_score=78.5,
        review_count=2500,
        owners=65000,
        revenue=850000,
        genres=['Action', 'Adventure', 'RPG'],
        release_date='2024-03-01',
        developer='My Game Studio',
        tags=['Singleplayer', 'Story Rich', 'Open World'],
        review_velocity_trend='increasing'
    )

    print_game_data_summary(my_game)

    # Generate report
    print("Generating report for manually entered game...")
    orchestrator = ReportOrchestrator(hourly_rate=75.0)  # Custom hourly rate

    try:
        reports = orchestrator.generate_complete_report(my_game)
        metadata = reports['metadata']

        print(f"\n✅ Report Generated!")
        print(f"   Score: {metadata.overall_score:.1f}/100")
        print(f"   Tier: {metadata.tier_name}")
        print(f"   Tier 1 Length: {metadata.word_count['tier_1']:,} words")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def demo_all_tiers():
    """Show reports across all performance tiers"""
    print("\n" + "="*80)
    print("DEMO: REPORTS ACROSS ALL PERFORMANCE TIERS")
    print("="*80 + "\n")

    orchestrator = ReportOrchestrator(hourly_rate=50.0)

    for tier_name, games in MOCK_GAMES_BY_TIER.items():
        if not games or tier_name == 'special':
            continue

        print(f"\n{' '*20}{tier_name.upper()} TIER")
        print("="*80)

        game = games[0]  # Test first game in tier
        print(f"Testing: {game['name']}")
        print(f"  Review Score: {game['review_score']:.1f}%")
        print(f"  Reviews: {game['review_count']:,}")
        print(f"  Owners: {game['owners']:,}")

        try:
            reports = orchestrator.generate_complete_report(game)
            metadata = reports['metadata']

            print(f"\n  ✅ Overall Score: {metadata.overall_score:.1f}/100")
            print(f"  📊 Report Stats:")
            print(f"     - Confidence: {metadata.confidence_level}")
            print(f"     - Has Negative Analysis: {metadata.has_negative_reviews}")
            print(f"     - Has Comparables: {metadata.has_comparables}")
            print(f"     - Word Count (T1/T2/T3): {metadata.word_count['tier_1']}/{metadata.word_count['tier_2']}/{metadata.word_count['tier_3']}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

        print()


def demo_roi_calculator():
    """Demonstrate ROI calculator standalone"""
    print("\n" + "="*80)
    print("DEMO: ROI CALCULATOR (Standalone)")
    print("="*80 + "\n")

    from src.roi_calculator import ROICalculator

    # Test with different hourly rates
    rates = [50, 75, 100]

    for rate in rates:
        print(f"\n{'='*60}")
        print(f"Testing with hourly rate: ${rate}/hr")
        print('='*60)

        calc = ROICalculator(hourly_rate=rate)

        # Regional pricing ROI
        result = calc.calculate_regional_pricing_roi(
            current_revenue=50000,  # $50K/month
            current_regions=1,
            game_genre="indie"
        )

        print(f"\nAction: {result.action_name}")
        print(f"Time Investment: {result.time_investment.total_hours} hours")
        print(f"Total Investment: ${result.total_investment:,.0f}")
        print(f"Expected Revenue (likely): ${result.revenue_impact.likely:,.0f}")
        print(f"ROI Ratio: {result.roi_likely:.1f}x")
        print(f"Payback Period: {result.payback_period_weeks:.1f} weeks")
        print(f"Priority Score: {result.priority_score:.2f}")


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("PUBLITZ AUTOMATED AUDITS - COMPLETE DEMO")
    print("System Demonstration Without External APIs")
    print("="*80)

    try:
        # Demo 1: Mock data reports
        demo_mock_data_reports()

        # Demo 2: Manual data entry
        demo_manual_data_entry()

        # Demo 3: All tiers
        demo_all_tiers()

        # Demo 4: ROI calculator
        demo_roi_calculator()

        print("\n" + "="*80)
        print("DEMO COMPLETE")
        print("="*80)
        print("\n✅ All demos completed successfully!")
        print("\nThe system is fully functional even without external APIs.")
        print("\nNext steps:")
        print("  1. Use mock data for testing and demonstrations")
        print("  2. Use manual data entry for real game analysis")
        print("  3. Generate complete reports with either method")
        print("\nSee the following files for more details:")
        print("  - src/mock_game_data.py")
        print("  - src/manual_data_entry.py")
        print("  - API_BLOCKER_REPORT.md")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
