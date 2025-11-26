#!/usr/bin/env python3
"""
Data Consistency Integration Test

Tests the complete data consistency validation system integrated into report orchestrator.
Verifies that:
1. Valid data passes validation
2. Invalid data is caught and reported
3. All numbers in reports are consistent
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.report_orchestrator import ReportOrchestrator
from src.data_consistency import GameMetrics, pre_flight_check


def test_valid_data():
    """Test with valid Retrace the Light data"""
    print("\n" + "="*80)
    print("TEST 1: VALID DATA (Retrace the Light)")
    print("="*80 + "\n")

    game_data = {
        'app_id': '1234567',
        'name': 'Retrace the Light',
        'revenue': 379,
        'days_since_launch': 7,
        'review_count': 5,
        'review_score': 80.0,
        'positive_reviews': 4,
        'negative_reviews': 1,
        'owners': 100,
        'price': 14.99,
        'release_date': '2024-11-18',
        'genres': ['Adventure', 'Indie']
    }

    print("INPUT DATA:")
    print(f"  Revenue: ${game_data['revenue']}")
    print(f"  Reviews: {game_data['review_count']} ({game_data['review_score']}% positive)")
    print(f"  Positive: {game_data['positive_reviews']}, Negative: {game_data['negative_reviews']}")
    print(f"  Owners: {game_data['owners']}")
    print(f"  Price: ${game_data['price']}")
    print()

    # Run pre-flight check
    is_valid, metrics, messages = pre_flight_check(game_data)

    print("PRE-FLIGHT CHECK:")
    print(f"  Status: {'✅ PASSED' if is_valid else '❌ FAILED'}")
    if messages:
        for msg in messages:
            print(f"  {msg}")
    print()

    if not is_valid:
        print("❌ TEST FAILED: Valid data should pass pre-flight check")
        return False

    # Generate report
    print("GENERATING REPORT...")
    orchestrator = ReportOrchestrator()
    report = orchestrator.generate_complete_report(game_data)

    metadata = report['metadata']

    print("\nREPORT METADATA:")
    print(f"  Overall Score: {metadata.overall_score}/100")
    print(f"  Performance Tier: {metadata.tier_name}")
    print(f"  Word Count (Tier 1): {metadata.word_count['tier_1']}")
    print()

    # Verify no data errors
    if metadata.tier_name == "Data Error":
        print("❌ TEST FAILED: Report should not have data errors")
        return False

    print("✅ TEST PASSED: Valid data accepted and report generated")
    print("="*80 + "\n")
    return True


def test_invalid_data_reviews_exceed_owners():
    """Test with invalid data: reviews > owners"""
    print("\n" + "="*80)
    print("TEST 2: INVALID DATA (Reviews Exceed Owners)")
    print("="*80 + "\n")

    game_data = {
        'app_id': '1234567',
        'name': 'Bad Data Game',
        'revenue': 1000,
        'days_since_launch': 7,
        'review_count': 500,  # More reviews than owners!
        'review_score': 80.0,
        'positive_reviews': 400,
        'negative_reviews': 100,
        'owners': 100,  # Only 100 owners but 500 reviews
        'price': 14.99,
        'release_date': '2024-11-18',
        'genres': ['Adventure', 'Indie']
    }

    print("INPUT DATA (INVALID):")
    print(f"  Reviews: {game_data['review_count']}")
    print(f"  Owners: {game_data['owners']}")
    print(f"  ❌ Reviews ({game_data['review_count']}) > Owners ({game_data['owners']})")
    print()

    # Run pre-flight check
    is_valid, metrics, messages = pre_flight_check(game_data)

    print("PRE-FLIGHT CHECK:")
    print(f"  Status: {'✅ PASSED' if is_valid else '❌ FAILED (expected)'}")
    if messages:
        for msg in messages:
            print(f"  {msg}")
    print()

    if is_valid:
        print("❌ TEST FAILED: Invalid data should be rejected")
        return False

    # Try to generate report
    print("ATTEMPTING REPORT GENERATION...")
    orchestrator = ReportOrchestrator()
    report = orchestrator.generate_complete_report(game_data)

    metadata = report['metadata']

    print("\nREPORT METADATA:")
    print(f"  Tier Name: {metadata.tier_name}")
    print()

    # Should get data error report
    if metadata.tier_name != "Data Error":
        print(f"❌ TEST FAILED: Expected 'Data Error' tier, got '{metadata.tier_name}'")
        return False

    # Check that error report explains the problem
    tier_1 = report['tier_1_executive']
    if "Review count" not in tier_1 and "owner count" not in tier_1:
        print("❌ TEST FAILED: Error report should mention review/owner mismatch")
        return False

    print("✅ TEST PASSED: Invalid data correctly rejected")
    print("="*80 + "\n")
    return True


def test_invalid_data_negative_revenue():
    """Test with invalid data: negative revenue"""
    print("\n" + "="*80)
    print("TEST 3: INVALID DATA (Negative Revenue)")
    print("="*80 + "\n")

    game_data = {
        'app_id': '1234567',
        'name': 'Negative Revenue Game',
        'revenue': -1000,  # Negative revenue!
        'days_since_launch': 7,
        'review_count': 5,
        'review_score': 80.0,
        'positive_reviews': 4,
        'negative_reviews': 1,
        'owners': 100,
        'price': 14.99,
        'release_date': '2024-11-18',
        'genres': ['Adventure', 'Indie']
    }

    print("INPUT DATA (INVALID):")
    print(f"  Revenue: ${game_data['revenue']}")
    print(f"  ❌ Revenue is negative")
    print()

    # Run pre-flight check
    is_valid, metrics, messages = pre_flight_check(game_data)

    print("PRE-FLIGHT CHECK:")
    print(f"  Status: {'✅ PASSED' if is_valid else '❌ FAILED (expected)'}")
    if messages:
        for msg in messages:
            print(f"  {msg}")
    print()

    if is_valid:
        print("❌ TEST FAILED: Negative revenue should be rejected")
        return False

    # Try to generate report
    orchestrator = ReportOrchestrator()
    report = orchestrator.generate_complete_report(game_data)

    metadata = report['metadata']

    if metadata.tier_name != "Data Error":
        print(f"❌ TEST FAILED: Expected 'Data Error' tier, got '{metadata.tier_name}'")
        return False

    print("✅ TEST PASSED: Negative revenue correctly rejected")
    print("="*80 + "\n")
    return True


def test_warning_case_low_review_rate():
    """Test with data that generates warnings but still passes"""
    print("\n" + "="*80)
    print("TEST 4: WARNING CASE (Low Review Rate)")
    print("="*80 + "\n")

    game_data = {
        'app_id': '1234567',
        'name': 'Low Review Rate Game',
        'revenue': 50000,
        'days_since_launch': 30,
        'review_count': 5,  # Only 5 reviews
        'review_score': 80.0,
        'positive_reviews': 4,
        'negative_reviews': 1,
        'owners': 10000,  # But 10,000 owners (0.05% review rate)
        'price': 14.99,
        'release_date': '2024-10-25',
        'genres': ['Adventure', 'Indie']
    }

    print("INPUT DATA:")
    print(f"  Reviews: {game_data['review_count']}")
    print(f"  Owners: {game_data['owners']}")
    print(f"  Review Rate: {(game_data['review_count'] / game_data['owners']) * 100:.2f}%")
    print(f"  ⚠️  Unusually low review rate (typical: 2-5%)")
    print()

    # Run pre-flight check
    is_valid, metrics, messages = pre_flight_check(game_data)

    print("PRE-FLIGHT CHECK:")
    print(f"  Status: {'✅ PASSED (with warnings)' if is_valid else '❌ FAILED'}")
    if messages:
        for msg in messages:
            print(f"  {msg}")
    print()

    if not is_valid:
        print("❌ TEST FAILED: Warning case should still pass validation")
        return False

    # Generate report should succeed
    orchestrator = ReportOrchestrator()
    report = orchestrator.generate_complete_report(game_data)

    metadata = report['metadata']

    if metadata.tier_name in ["Data Error", "Insufficient Data"]:
        print(f"❌ TEST FAILED: Report should generate despite warnings, got '{metadata.tier_name}'")
        return False

    print("✅ TEST PASSED: Warning case handled correctly (generates report with warnings)")
    print("="*80 + "\n")
    return True


def run_all_tests():
    """Run all data consistency tests"""
    print("\n" + "="*80)
    print("DATA CONSISTENCY INTEGRATION TEST SUITE")
    print("="*80)

    tests = [
        ("Valid Data", test_valid_data),
        ("Invalid: Reviews > Owners", test_invalid_data_reviews_exceed_owners),
        ("Invalid: Negative Revenue", test_invalid_data_negative_revenue),
        ("Warning: Low Review Rate", test_warning_case_low_review_rate)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ TEST CRASHED: {test_name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80 + "\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")
    print("="*80 + "\n")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
