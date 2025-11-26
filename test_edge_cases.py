#!/usr/bin/env python3
"""Edge case testing for bug detection"""
import sys
sys.path.insert(0, '/home/user/Publitz-Automated-Audits')
from src.community_analyzer import analyze_community_reach
from src.report_orchestrator import ReportOrchestrator
from datetime import datetime, timedelta

def test_empty_genres():
    print("\n" + "="*80)
    print("TEST: Empty Genres")
    print("="*80)
    game_data = {'name': 'Game with no genres', 'genres': [], 'tags': []}
    try:
        analysis = analyze_community_reach(game_data)
        print(f"✅ Handled empty genres - Score: {analysis.overall_score}/100")
    except Exception as e:
        print(f"❌ FAILED: {e}")

def test_none_values():
    print("\n" + "="*80)
    print("TEST: None Values")
    print("="*80)
    game_data = {'name': 'Game', 'genres': None, 'tags': None}
    try:
        analysis = analyze_community_reach(game_data)
        print(f"✅ Handled None values - Score: {analysis.overall_score}/100")
    except Exception as e:
        print(f"❌ FAILED: {e}")

def test_empty_curator_list():
    print("\n" + "="*80)
    print("TEST: Empty Curator List")
    print("="*80)
    game_data = {'name': 'Game', 'genres': ['Action']}
    try:
        analysis = analyze_community_reach(game_data, curator_list=[])
        print(f"✅ Handled empty curator list - Score: {analysis.overall_score}/100")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()

def test_free_game():
    print("\n" + "="*80)
    print("TEST: Free Game (price = 0)")
    print("="*80)
    orchestrator = ReportOrchestrator()
    game_data = {
        'app_id': '999999', 'name': 'Free Game', 'price': 0.00,
        'review_score': 80, 'review_count': 500, 'owners': 10000,
        'revenue': 0, 'genres': ['Free to Play'],
        'release_date': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    }
    try:
        report = orchestrator.generate_complete_report(game_data)
        print(f"✅ Handled free game - Score: {report['metadata'].overall_score}/100")
        if report['metadata'].price_analysis:
            print(f"  ⚠️  Price analysis ran on $0 game")
        else:
            print(f"  ✅ Price analysis correctly skipped")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\nEDGE CASE & BUG DETECTION TESTS\n" + "="*80)
    test_empty_genres()
    test_none_values()
    test_empty_curator_list()
    test_free_game()
    print("\n" + "="*80 + "\nEDGE CASE TESTS COMPLETE\n")
