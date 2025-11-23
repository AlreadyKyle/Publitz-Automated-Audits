#!/usr/bin/env python3
"""
Test script for comparable games analyzer

Tests with:
1. Hades II (1145350) - high-performing game
2. A lower-performing indie game for contrast
"""

import sys
sys.path.insert(0, '/home/user/Publitz-Automated-Audits')

from src.comparable_games_analyzer import test_analyzer, ComparableGamesAnalyzer


def main():
    print("\n" + "="*80)
    print("COMPARABLE GAMES ANALYZER TEST")
    print("="*80)

    # Test 1: Hades II (high-performing game)
    print("\n\n### TEST 1: Hades II (1145350) - High-Performing Game ###\n")
    hades_analyzer, hades_comparables = test_analyzer("1145350")

    if hades_comparables:
        print("\n--- Generating Comparison Report ---")
        # Get full game data for report generation
        game_data = hades_analyzer.game_search.get_game_details(1145350)
        spy_data = hades_analyzer.game_search.get_steamspy_data(1145350)

        # Build target game object
        target_game = hades_analyzer._build_comparable_game_from_game_data(game_data, spy_data)

        if target_game:
            # Generate comparison table
            report = hades_analyzer.generate_comparison_table(
                target_game,
                hades_comparables,
                "Roguelike",
                "$15-$35",
                "2024"
            )
            print("\n" + report)

            # Identify success patterns
            higher_performers = [g for g in hades_comparables if g.overall_score > target_game.overall_score]
            if higher_performers:
                print("\n--- Success Patterns from Higher Performers ---")
                patterns = hades_analyzer.identify_success_patterns(target_game, higher_performers)
                print(f"Common missing tags: {patterns['common_tags_missing']}")
                print(f"Pricing insight: {patterns['price_insights']}")
                print(f"Actionable tactics:")
                for tactic in patterns['actionable_tactics']:
                    print(f"  - {tactic}")

    # Test 2: Lower-performing indie game
    # Using app_id 863550 (Slay the Spire) as a well-known roguelike for comparison
    print("\n\n" + "="*80)
    print("### TEST 2: Slay the Spire (646570) - For Comparison ###")
    print("="*80 + "\n")
    sts_analyzer, sts_comparables = test_analyzer("646570")

    if sts_comparables:
        print(f"\nFound {len(sts_comparables)} comparable games for Slay the Spire")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
