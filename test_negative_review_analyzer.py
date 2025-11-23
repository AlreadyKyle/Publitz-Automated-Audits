#!/usr/bin/env python3
"""
Test script for negative review analyzer

Tests with real struggling Steam games to demonstrate the analysis capabilities.
"""

import sys
import os
sys.path.insert(0, '/home/user/Publitz-Automated-Audits')

from src.negative_review_analyzer import NegativeReviewAnalyzer


def main():
    print("\n" + "="*80)
    print("NEGATIVE REVIEW ANALYZER TEST")
    print("="*80)

    # Get Claude API key from environment
    claude_api_key = os.getenv('ANTHROPIC_API_KEY')
    if not claude_api_key:
        print("\nERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return

    # Initialize analyzer
    analyzer = NegativeReviewAnalyzer(claude_api_key)

    # Test with a struggling game
    # Using "The Day Before" (2719640) - infamous failed game with terrible reviews
    # Or we can use a different struggling indie game

    print("\n### TEST: Analyzing Struggling Game ###\n")

    # Example struggling game parameters
    # You can replace these with any game with <80% positive reviews
    test_cases = [
        {
            'app_id': '2719640',
            'name': 'The Day Before',
            'review_score': 15.0,  # Example - one of the worst reviewed games
            'description': 'Infamous failed MMO survival game'
        },
        {
            'app_id': '252950',
            'name': 'Rocket League',  # Using as fallback - well-reviewed game
            'review_score': 85.0,
            'description': 'For comparison - successful game (should have few negative reviews)'
        }
    ]

    # Test with first case (struggling game)
    test_case = test_cases[0]
    print(f"Testing with: {test_case['name']} ({test_case['description']})")
    print(f"App ID: {test_case['app_id']}")
    print(f"Review Score: {test_case['review_score']}%")
    print("\nFetching and analyzing negative reviews...")
    print("This may take 30-60 seconds as we call Claude API multiple times...\n")

    try:
        # Generate full analysis
        report = analyzer.generate_full_analysis(
            app_id=test_case['app_id'],
            game_name=test_case['name'],
            current_review_score=test_case['review_score'],
            review_count=50  # Analyze 50 negative reviews
        )

        # Save report to file
        output_file = f"negative_review_analysis_{test_case['app_id']}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print("="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print(f"\nFull report saved to: {output_file}")
        print("\nPreview (first 2000 characters):")
        print("-"*80)
        print(report[:2000])
        if len(report) > 2000:
            print("\n... (report continues) ...")
        print("-"*80)

    except Exception as e:
        print(f"\nERROR during analysis: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
