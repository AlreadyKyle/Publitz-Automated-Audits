#!/usr/bin/env python3
"""
Full integration test for Publitz Automated Audits
Tests all new systems: price analysis, generic detection, community reach
"""

import sys
sys.path.insert(0, '/home/user/Publitz-Automated-Audits')

from src.report_orchestrator import ReportOrchestrator
from datetime import datetime, timedelta


def test_full_integration():
    """Test full report generation with all new features"""
    print("\n" + "="*80)
    print("FULL INTEGRATION TEST")
    print("Testing: Price Analysis + Generic Detection + Community Reach")
    print("="*80 + "\n")

    orchestrator = ReportOrchestrator()

    # Create a roguelike game (should get specific community recommendations)
    game_data = {
        'app_id': '999999',
        'name': 'Roguelike Dungeon Crawler',
        'price': 14.99,
        'review_score': 85,
        'review_count': 2500,
        'owners': 50000,
        'revenue': 600000,
        'genres': ['Roguelike', 'Action', 'Indie'],
        'tags': ['Pixel Graphics', 'Roguelike', 'Dungeon Crawler', 'Permadeath'],
        'release_date': (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d'),
        'is_early_access': False
    }

    print(f"Game: {game_data['name']}")
    print(f"Price: ${game_data['price']:.2f}")
    print(f"Genres: {', '.join(game_data['genres'])}")
    print(f"Reviews: {game_data['review_count']} ({game_data['review_score']}%)")
    print(f"Revenue: ${game_data['revenue']:,}\n")

    try:
        report = orchestrator.generate_complete_report(game_data)

        print("✅ Report generated successfully\n")

        # Check basic metadata
        print(f"Overall Score: {report['metadata'].overall_score:.1f}/100")
        print(f"Performance Tier: {report['metadata'].performance_tier} ({report['metadata'].tier_name})")
        print(f"\nWord Counts:")
        print(f"  - Tier 1: {report['metadata'].word_count['tier_1']:,} words")
        print(f"  - Tier 2: {report['metadata'].word_count['tier_2']:,} words")
        print(f"  - Tier 3: {report['metadata'].word_count['tier_3']:,} words")

        # Check price analysis
        print(f"\n{'='*80}")
        print("PRICE ANALYSIS RESULTS")
        print(f"{'='*80}")

        if report['metadata'].price_analysis:
            pa = report['metadata'].price_analysis
            print(f"✅ Price Analysis Completed")
            print(f"  - Price Tier: {pa['price_tier'].tier}")
            print(f"  - Severity: {pa['price_tier'].severity if pa['price_tier'].severity else 'None'}")

            if report['metadata'].price_warnings:
                print(f"\n⚠️  Price warnings generated:")
                print(report['metadata'].price_warnings[:200] + "...")
            else:
                print(f"\n✅ No price warnings (price is acceptable)")
        else:
            print("❌ Price analysis not run")

        # Check community reach integration
        print(f"\n{'='*80}")
        print("COMMUNITY REACH INTEGRATION")
        print(f"{'='*80}")

        tier_2 = report['tier_2_strategic']

        if 'Community Reach Analysis' in tier_2:
            print("✅ Community Reach section found in Tier 2 report")

            # Check for specific vs generic recommendations
            if 'roguelike' in tier_2.lower():
                print("✅ Genre-specific recommendations detected (roguelike)")
            else:
                print("⚠️  No genre-specific keywords found")

            # Check for value labels
            if '✅ Personalized' in tier_2:
                print("✅ Personalized recommendations detected")
            elif '⚠️  Generic' in tier_2:
                print("⚠️  Generic recommendations detected (unexpected for roguelike game)")
            else:
                print("❌ No value labels found")

            # Check for generic detection warnings
            if 'SCORE ADJUSTED FOR GENERIC DATA' in tier_2:
                print("⚠️  Generic data warnings present (checking if appropriate...)")
            else:
                print("✅ No generic data warnings (good for specific game)")

        else:
            print("❌ Community Reach section NOT found in Tier 2 report")

        # Check data consistency
        print(f"\n{'='*80}")
        print("DATA VALIDATION")
        print(f"{'='*80}")

        api_status = report['api_status']
        print(f"API Calls: {api_status['successful']}/{api_status['total_calls']} successful")

        if report['metadata'].was_capped:
            print(f"✅ Score was capped: {report['metadata'].original_score:.1f} → {report['metadata'].overall_score:.1f}")
            print(f"  Limiting factor: {report['metadata'].score_caps.limiting_factor}")
        else:
            print(f"✅ Score within limits: {report['metadata'].overall_score:.1f}/100")

        # Extract community recommendations from report
        print(f"\n{'='*80}")
        print("COMMUNITY RECOMMENDATIONS PREVIEW")
        print(f"{'='*80}")

        # Find community section in report
        if 'Community Reach Analysis' in tier_2:
            start = tier_2.find('Community Reach Analysis')
            end = tier_2.find('##', start + 100)  # Find next section
            community_section = tier_2[start:end] if end > start else tier_2[start:start+800]

            print(community_section[:600] + "..." if len(community_section) > 600 else community_section)
        else:
            print("Community section not found in report")

        print(f"\n{'='*80}")
        print("TEST COMPLETE ✅")
        print(f"{'='*80}")

        return report

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("\n" + "="*80)
    print("PUBLITZ AUTOMATED AUDITS - FULL SYSTEM TEST")
    print("="*80)

    # Run test
    test_full_integration()

    print("\n" + "="*80)
    print("ALL TESTS COMPLETE")
    print("="*80 + "\n")
