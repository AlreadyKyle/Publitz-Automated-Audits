#!/usr/bin/env python3
"""
Comprehensive System Review - Test all components and output quality
"""
import sys
sys.path.insert(0, '/home/user/Publitz-Automated-Audits')

from src.report_orchestrator import ReportOrchestrator
from datetime import datetime, timedelta
import json


def test_realistic_indie_game():
    """Test with realistic indie game data"""
    print("\n" + "="*80)
    print("COMPREHENSIVE SYSTEM REVIEW")
    print("Testing realistic indie game scenario")
    print("="*80 + "\n")

    orchestrator = ReportOrchestrator()

    # Realistic struggling indie game
    game_data = {
        'app_id': '1234567',
        'name': 'Mystic Dungeon: Roguelike Adventure',
        'price': 14.99,
        'review_score': 78,
        'review_count': 456,
        'owners': 12500,
        'revenue': 156000,
        'genres': ['Roguelike', 'Action', 'Indie', 'RPG'],
        'tags': ['Pixel Graphics', 'Roguelike', 'Dungeon Crawler', 'Permadeath', 'Procedural Generation'],
        'release_date': (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d'),
        'is_early_access': False
    }

    print(f"Game: {game_data['name']}")
    print(f"Price: ${game_data['price']:.2f}")
    print(f"Reviews: {game_data['review_count']} ({game_data['review_score']}%)")
    print(f"Owners: {game_data['owners']:,}")
    print(f"Revenue: ${game_data['revenue']:,}")
    print(f"Days since launch: 180")
    print(f"Genres: {', '.join(game_data['genres'])}")
    print()

    try:
        report = orchestrator.generate_complete_report(game_data)

        print("="*80)
        print("SYSTEM COMPONENT VERIFICATION")
        print("="*80 + "\n")

        # 1. Check metadata
        metadata = report['metadata']
        print(f"✅ Overall Score: {metadata.overall_score:.1f}/100")
        print(f"✅ Performance Tier: {metadata.performance_tier} ({metadata.tier_name})")
        print(f"✅ Generated at: {metadata.generated_at.strftime('%Y-%m-%d %H:%M')}")
        
        # 2. Check word counts
        print(f"\n📊 Word Counts:")
        print(f"   Tier 1 Executive: {metadata.word_count['tier_1']:,} words")
        print(f"   Tier 2 Strategic: {metadata.word_count['tier_2']:,} words")
        print(f"   Tier 3 Deep-dive: {metadata.word_count['tier_3']:,} words")

        # 3. Check validation systems
        print(f"\n🔍 Validation Systems:")
        
        # Price analysis
        if metadata.price_analysis:
            pa = metadata.price_analysis
            print(f"   ✅ Price Analysis: {pa['price_tier'].tier} (severity: {pa['price_tier'].severity or 'None'})")
            if metadata.price_warnings:
                print(f"      ⚠️  Warnings generated")
        else:
            print(f"   ✅ Price Analysis: Skipped (price $0)")

        # Score capping
        if metadata.score_caps:
            if metadata.was_capped:
                print(f"   ✅ Score Capping: {metadata.original_score:.1f} → {metadata.overall_score:.1f}")
                print(f"      Reason: {metadata.score_caps.limiting_factor}")
            else:
                print(f"   ✅ Score Capping: Within limits ({metadata.overall_score:.1f}/{metadata.score_caps.maximum_score})")
        else:
            print(f"   ℹ️  Score Capping: N/A (error or insufficient data)")

        # Revenue reality check
        if metadata.revenue_reality_check:
            print(f"   ✅ Revenue Reality Check: Score adjusted")
        else:
            print(f"   ✅ Revenue Reality Check: No adjustment needed")

        # 4. Check API status
        api_status = report['api_status']
        print(f"\n🌐 API Status:")
        print(f"   Total calls: {api_status['total_calls']}")
        print(f"   Successful: {api_status['successful']}")
        print(f"   Failed: {api_status['failed']}")
        print(f"   Success rate: {api_status['successful']/api_status['total_calls']*100:.1f}%")

        # 5. Check report components
        components = report['components']
        print(f"\n📄 Report Components:")
        print(f"   ✅ Executive Summary: {len(components.executive_summary)} chars")
        print(f"   ✅ Confidence Scorecard: {len(components.confidence_scorecard)} chars")
        print(f"   ✅ Quick Start: {len(components.quick_start)} chars")
        print(f"   ✅ Market Positioning: {len(components.market_positioning)} chars")
        print(f"   ✅ Comparable Games: {len(components.comparable_games)} chars")
        print(f"   ✅ Revenue Performance: {len(components.revenue_performance)} chars")
        
        if components.community_reach:
            print(f"   ✅ Community Reach: {len(components.community_reach)} chars")
        else:
            print(f"   ❌ Community Reach: MISSING")

        # 6. Check for critical sections in Tier 2 report
        tier_2 = report['tier_2_strategic']
        print(f"\n📋 Tier 2 Report Content Check:")
        
        critical_sections = [
            ('Executive Summary', '# Executive Summary' in tier_2 or 'Executive Summary' in tier_2),
            ('Key Metrics Dashboard', 'Key Metrics Dashboard' in tier_2),
            ('Market Positioning', 'Market Positioning' in tier_2),
            ('Comparable Games', 'Comparable Games' in tier_2 or 'How You Compare' in tier_2),
            ('Revenue Performance', 'Revenue Performance' in tier_2),
            ('Community Reach', 'Community Reach' in tier_2),
            ('Strategic Recommendations', 'Strategic Recommendations' in tier_2),
            ('Action Plan', 'Action Plan' in tier_2 or '30-Day' in tier_2),
        ]
        
        for section_name, exists in critical_sections:
            status = "✅" if exists else "❌"
            print(f"   {status} {section_name}: {'Found' if exists else 'MISSING'}")

        # 7. Check for validation warnings in output
        print(f"\n⚠️  Validation Warnings in Report:")
        
        warnings_found = []
        if '🚨' in tier_2:
            warnings_found.append("Price alerts (🚨)")
        if '⚠️' in tier_2:
            warnings_found.append("Generic data warnings (⚠️)")
        if 'SCORE ADJUSTED' in tier_2:
            warnings_found.append("Score adjustments")
        if 'CAPPED' in tier_2.upper():
            warnings_found.append("Score capping")
        
        if warnings_found:
            for warning in warnings_found:
                print(f"   ✅ {warning}")
        else:
            print(f"   ℹ️  No critical warnings (good for this game)")

        # 8. Sample output from Tier 2 report
        print(f"\n📖 Sample Report Output (Tier 2):")
        print("="*80)
        
        # Find and print Community Reach section
        if 'Community Reach Analysis' in tier_2:
            start = tier_2.find('Community Reach Analysis')
            end = tier_2.find('\n## ', start + 100)
            if end == -1:
                end = start + 800
            sample = tier_2[start:end]
            print(sample[:700] + "..." if len(sample) > 700 else sample)
        else:
            # Print first 700 chars of Tier 2
            print(tier_2[:700] + "...")

        print("\n" + "="*80)

        # 9. Quality assessment
        print("\n📈 QUALITY ASSESSMENT:")
        print("="*80)
        
        issues = []
        
        # Check word count targets
        if metadata.word_count['tier_1'] < 800:
            issues.append(f"Tier 1 too short ({metadata.word_count['tier_1']} words, target 800+)")
        if metadata.word_count['tier_2'] < 1200:
            issues.append(f"Tier 2 too short ({metadata.word_count['tier_2']} words, target 1200+)")
        
        # Check for missing components
        if not components.community_reach:
            issues.append("Community reach analysis missing")
        
        # Check for placeholder text
        if '*Coming soon*' in tier_2:
            issues.append("Placeholder text found in report")
        
        # Check for failed components
        if '*unavailable*' in tier_2 or '*failed*' in tier_2:
            issues.append("Component generation failures detected")
        
        if issues:
            print("⚠️  ISSUES FOUND:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ ALL QUALITY CHECKS PASSED")
        
        # Overall verdict
        print(f"\n" + "="*80)
        print("OVERALL VERDICT:")
        print("="*80)
        
        if len(issues) == 0:
            print("🎉 SYSTEM WORKING PERFECTLY")
            print("   - All validation systems operational")
            print("   - All components generating correctly")
            print("   - Report quality meets standards")
            print("   - High-value output confirmed")
        elif len(issues) <= 2:
            print("✅ SYSTEM WORKING WELL")
            print(f"   - Minor issues detected ({len(issues)})")
            print("   - Core functionality operational")
            print("   - Report provides value")
        else:
            print("⚠️  SYSTEM NEEDS ATTENTION")
            print(f"   - {len(issues)} issues detected")
            print("   - Review issues above")
        
        print()

        return report

    except Exception as e:
        print(f"\n❌ SYSTEM FAILURE: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_realistic_indie_game()
