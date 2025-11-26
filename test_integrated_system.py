#!/usr/bin/env python3
"""
Test integrated report orchestrator with price analysis and validation systems
"""

import sys
sys.path.insert(0, '/home/user/Publitz-Automated-Audits')

from src.report_orchestrator import ReportOrchestrator
from datetime import datetime, timedelta


def test_catastrophic_pricing():
    """Test report generation with catastrophic pricing ($0.99)"""
    print("\n" + "="*80)
    print("TEST: Catastrophic Pricing Detection")
    print("="*80 + "\n")

    orchestrator = ReportOrchestrator()

    # Game with $0.99 price (catastrophic)
    game_data = {
        'app_id': '999991',
        'name': 'Test Game - Catastrophic Pricing',
        'price': 0.99,
        'review_score': 80,
        'review_count': 380,
        'owners': 380,
        'revenue': 375,  # 380 units * $0.99
        'genres': ['Indie', 'Action'],
        'release_date': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
        'is_early_access': False
    }

    print(f"Game: {game_data['name']}")
    print(f"Price: ${game_data['price']:.2f}")
    print(f"Reviews: {game_data['review_count']} ({game_data['review_score']}%)")
    print(f"Revenue: ${game_data['revenue']:,}")
    print()

    try:
        report = orchestrator.generate_complete_report(game_data)

        print("✅ Report generated successfully")
        print(f"Overall Score: {report['metadata'].overall_score:.1f}/100")
        print(f"Performance Tier: {report['metadata'].performance_tier} ({report['metadata'].tier_name})")

        # Check if price warnings were generated
        if report['metadata'].price_warnings:
            print("\n🚨 PRICE WARNINGS DETECTED:")
            print("-" * 80)
            print(report['metadata'].price_warnings[:500] + "...")
        else:
            print("\n❌ NO PRICE WARNINGS - This is a BUG!")

        # Check if price analysis was run
        if report['metadata'].price_analysis:
            print("\n✅ Price Analysis Completed:")
            pa = report['metadata'].price_analysis
            print(f"  - Price Tier: {pa['price_tier'].tier}")
            print(f"  - Severity: {pa['price_tier'].severity}")
            print(f"  - Lost Revenue: ${pa.get('lost_revenue', 0):,.0f}")
            print(f"  - Recommended Price: ${pa.get('potential_price', 0):.2f}")
        else:
            print("\n❌ NO PRICE ANALYSIS - This is a BUG!")

        # Check Tier 1 report contains price warning
        if '🚨 PRICING ALERT' in report['tier_1_executive']:
            print("\n✅ Tier 1 report contains price warning")
        else:
            print("\n❌ Tier 1 report missing price warning - This is a BUG!")

        print("\n" + "="*80)
        print("TEST PASSED" if report['metadata'].price_warnings else "TEST FAILED")
        print("="*80 + "\n")

        return report

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_normal_pricing():
    """Test report generation with normal pricing"""
    print("\n" + "="*80)
    print("TEST: Normal Pricing (No Warnings)")
    print("="*80 + "\n")

    orchestrator = ReportOrchestrator()

    # Game with normal price
    game_data = {
        'app_id': '999992',
        'name': 'Test Game - Normal Pricing',
        'price': 19.99,
        'review_score': 85,
        'review_count': 2500,
        'owners': 50000,
        'revenue': 750000,
        'genres': ['Indie', 'RPG'],
        'release_date': (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d'),
        'is_early_access': False
    }

    print(f"Game: {game_data['name']}")
    print(f"Price: ${game_data['price']:.2f}")
    print(f"Reviews: {game_data['review_count']} ({game_data['review_score']}%)")
    print(f"Revenue: ${game_data['revenue']:,}")
    print()

    try:
        report = orchestrator.generate_complete_report(game_data)

        print("✅ Report generated successfully")
        print(f"Overall Score: {report['metadata'].overall_score:.1f}/100")
        print(f"Performance Tier: {report['metadata'].performance_tier} ({report['metadata'].tier_name})")

        # Check that NO price warnings were generated for normal pricing
        if report['metadata'].price_warnings:
            print(f"\n⚠️  Price warnings generated (unexpected):")
            print(report['metadata'].price_warnings[:200] + "...")
        else:
            print("\n✅ No price warnings (as expected for normal pricing)")

        # Check price analysis was still run
        if report['metadata'].price_analysis:
            print("\n✅ Price Analysis Completed:")
            pa = report['metadata'].price_analysis
            print(f"  - Price Tier: {pa['price_tier'].tier}")
            print(f"  - Severity: {pa['price_tier'].severity}")
        else:
            print("\n✅ No price analysis (price is 0 or unavailable)")

        print("\n" + "="*80)
        print("TEST PASSED")
        print("="*80 + "\n")

        return report

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_data_consistency_validation():
    """Test that data consistency validation still works"""
    print("\n" + "="*80)
    print("TEST: Data Consistency Validation")
    print("="*80 + "\n")

    orchestrator = ReportOrchestrator()

    # Game with inconsistent data (more reviews than owners - impossible)
    game_data = {
        'app_id': '999993',
        'name': 'Test Game - Bad Data',
        'price': 14.99,
        'review_score': 75,
        'review_count': 10000,  # More reviews than owners!
        'owners': 100,
        'revenue': 1500,
        'genres': ['Indie', 'Strategy'],
        'release_date': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),
        'is_early_access': False
    }

    print(f"Game: {game_data['name']}")
    print(f"Reviews: {game_data['review_count']} (MORE THAN OWNERS)")
    print(f"Owners: {game_data['owners']} (IMPOSSIBLE)")
    print()

    try:
        report = orchestrator.generate_complete_report(game_data)

        # Should return error report
        if 'DATA CONSISTENCY ERRORS' in report['tier_1_executive']:
            print("✅ Data consistency validation caught the error")
            print("✅ Error report generated")
            print(f"Report Type: {report['metadata'].tier_name}")
        else:
            print("❌ Data consistency validation failed to catch error")

        print("\n" + "="*80)
        print("TEST PASSED" if 'DATA CONSISTENCY ERRORS' in report['tier_1_executive'] else "TEST FAILED")
        print("="*80 + "\n")

        return report

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("\n" + "="*80)
    print("INTEGRATED SYSTEM TEST SUITE")
    print("Testing: Price Analysis + Data Consistency + Score Validation")
    print("="*80)

    # Run all tests
    test_catastrophic_pricing()
    test_normal_pricing()
    test_data_consistency_validation()

    print("\n" + "="*80)
    print("ALL TESTS COMPLETE")
    print("="*80 + "\n")
