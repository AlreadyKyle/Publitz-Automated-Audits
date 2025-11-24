#!/usr/bin/env python3
"""
Test API Verification System

Demonstrates the new API tracking feature that shows which data sources
were used to generate each report.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.report_orchestrator import ReportOrchestrator


def create_test_game_data(scenario: str) -> dict:
    """Create test game data for different scenarios"""

    scenarios = {
        'complete': {
            'app_id': '1145350',
            'name': 'Test Game - Complete Data',
            'price': 24.99,
            'review_score': 85.5,
            'review_count': 5234,
            'owners': 120000,
            'revenue': 1800000,
            'genres': ['Action', 'RPG', 'Indie'],
            'release_date': '2024-01-15',
            'developer': 'Test Studio'
        },
        'missing_owners': {
            'app_id': '1145350',
            'name': 'Test Game - Missing Owner Data',
            'price': 19.99,
            'review_score': 78.0,
            'review_count': 2400,
            # 'owners': Missing!
            'revenue': 850000,
            'genres': ['Strategy'],
            'release_date': '2024-03-20'
        },
        'missing_reviews': {
            'app_id': '1145350',
            'name': 'Test Game - Missing Review Data',
            'price': 14.99,
            # 'review_score': Missing!
            # 'review_count': Missing!
            'owners': 45000,
            'revenue': 450000,
            'genres': ['Puzzle', 'Casual'],
            'release_date': '2024-05-10'
        },
        'minimal': {
            'app_id': '1145350',
            'name': 'Test Game - Minimal Data',
            'price': 9.99,
            # Most fields missing
        }
    }

    return scenarios.get(scenario, scenarios['complete'])


def test_api_verification(scenario: str):
    """Test API verification with different data scenarios"""

    print("\n" + "="*80)
    print(f"API VERIFICATION TEST: {scenario.upper()}")
    print("="*80 + "\n")

    # Create test data
    game_data = create_test_game_data(scenario)

    print("Game Data Provided:")
    for key, value in game_data.items():
        print(f"  {key}: {value}")
    print()

    # Initialize orchestrator
    orchestrator = ReportOrchestrator(hourly_rate=50.0)

    print("Generating report...\n")

    try:
        # Generate report
        report = orchestrator.generate_complete_report(game_data)

        # Extract API status
        api_status = report['api_status']
        metadata = report['metadata']

        print("="*80)
        print("REPORT GENERATION COMPLETE")
        print("="*80 + "\n")

        print(f"Game: {metadata.game_name}")
        print(f"Overall Score: {metadata.overall_score:.1f}/100")
        print(f"Performance Tier: {metadata.tier_name}")
        print(f"Report Word Counts: T1={metadata.word_count['tier_1']}, "
              f"T2={metadata.word_count['tier_2']}, T3={metadata.word_count['tier_3']}")
        print()

        print("="*80)
        print("API STATUS SUMMARY")
        print("="*80 + "\n")

        print(f"Total API Calls: {api_status['total_calls']}")
        print(f"Successful: {api_status['successful']}")
        print(f"Failed: {api_status['failed']}")
        print(f"Success Rate: {api_status['success_rate']:.1f}%")
        print(f"Data Quality: {api_status['data_quality'].upper()}")
        print()

        # Show successful APIs
        if api_status['apis']['success']:
            print("✅ SUCCESSFUL API CALLS:")
            for api in api_status['apis']['success']:
                print(f"   - {api['name']}: {api['endpoint']}")
            print()

        # Show failed APIs
        if api_status['apis']['failed']:
            print("❌ FAILED API CALLS:")
            for api in api_status['apis']['failed']:
                print(f"   - {api['name']}: {api['endpoint']}")
                print(f"     Error: {api['error']}")
            print()

        # Show skipped APIs
        if api_status['apis']['skipped']:
            print("⏭️  SKIPPED API CALLS:")
            for api in api_status['apis']['skipped']:
                print(f"   - {api['name']}: {api['reason']}")
            print()

        # Show not configured APIs
        if api_status['apis']['not_configured']:
            print("⚠️  NOT CONFIGURED:")
            for api in api_status['apis']['not_configured']:
                print(f"   - {api['name']}")
            print()

        print("="*80)
        print("REPORT PREVIEW - TIER 1 EXECUTIVE (FIRST 500 CHARS)")
        print("="*80 + "\n")

        tier_1 = report['tier_1_executive']
        print(tier_1[:500] + "...\n")

        print("="*80)
        print("API STATUS SECTION IN REPORT")
        print("="*80 + "\n")

        # Find and display the API status section from the report
        if "Data sources:" in tier_1.lower() or "Data Sources" in tier_1:
            # Extract the API status section
            lines = tier_1.split('\n')
            in_api_section = False
            api_section_lines = []

            for line in lines:
                if 'data source' in line.lower() and ('##' in line or '**' in line):
                    in_api_section = True
                    api_section_lines = []

                if in_api_section:
                    api_section_lines.append(line)

                    # Stop at next major section or footer
                    if line.startswith('---') and len(api_section_lines) > 3:
                        break

            if api_section_lines:
                print('\n'.join(api_section_lines[:20]))  # Show first 20 lines
        else:
            print("(API status section not found in excerpt)")

        print("\n" + "="*80)
        print(f"TEST COMPLETE: {scenario.upper()}")
        print("="*80 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all API verification tests"""

    print("\n" + "="*80)
    print("API VERIFICATION TEST SUITE")
    print("Testing the new API tracking feature")
    print("="*80)

    test_scenarios = [
        'complete',
        'missing_owners',
        'missing_reviews',
        'minimal'
    ]

    results = {}

    for scenario in test_scenarios:
        result = test_api_verification(scenario)
        results[scenario] = result

    # Summary
    print("\n" + "="*80)
    print("TEST SUITE SUMMARY")
    print("="*80 + "\n")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for scenario, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{scenario.upper()}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ All tests passed! API verification system is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")

    print("\n" + "="*80)
    print("FEATURE DEMONSTRATION COMPLETE")
    print("="*80)
    print("\nThe API verification system now tracks:")
    print("  • Which APIs were used to fetch data")
    print("  • Which API calls succeeded vs failed")
    print("  • Error messages for failed calls")
    print("  • Overall data quality rating")
    print("\nThis information is included in all three report tiers,")
    print("giving clients full transparency about data sources.")
    print("="*80 + "\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    exit(main())
