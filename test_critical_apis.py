#!/usr/bin/env python3
"""
Critical API Test - Quick validation of essential components
"""

import sys
sys.path.insert(0, '/home/user/Publitz-Automated-Audits')

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_dependencies():
    """Test that all required dependencies are installed"""
    print("\n" + "="*80)
    print("DEPENDENCY CHECK")
    print("="*80 + "\n")

    deps = {
        'beautifulsoup4': 'bs4',
        'anthropic': 'anthropic',
        'requests': 'requests',
        'aiohttp': 'aiohttp',
    }

    all_installed = True
    for name, module in deps.items():
        try:
            __import__(module)
            print(f"✅ {name} installed")
        except ImportError:
            print(f"❌ {name} NOT installed")
            all_installed = False

    return all_installed


def test_environment_variables():
    """Test that API keys are configured"""
    print("\n" + "="*80)
    print("ENVIRONMENT VARIABLES CHECK")
    print("="*80 + "\n")

    keys = {
        'ANTHROPIC_API_KEY': 'Claude/Anthropic',
        'RAWG_API_KEY': 'RAWG (optional)',
        'YOUTUBE_API_KEY': 'YouTube (optional)',
        'TWITCH_CLIENT_ID': 'Twitch (optional)',
    }

    results = {}
    for key, description in keys.items():
        value = os.getenv(key)
        if value:
            print(f"✅ {key} set ({description})")
            if key == 'ANTHROPIC_API_KEY':
                print(f"   Length: {len(value)} chars")
                print(f"   Prefix: {value[:12]}...")
            results[key] = True
        else:
            if 'optional' in description:
                print(f"⚠️  {key} not set ({description})")
            else:
                print(f"❌ {key} NOT set ({description})")
            results[key] = False

    return results.get('ANTHROPIC_API_KEY', False)


def test_roi_calculator():
    """Test ROI Calculator (no external APIs required)"""
    print("\n" + "="*80)
    print("ROI CALCULATOR TEST")
    print("="*80 + "\n")

    try:
        from src.roi_calculator import ROICalculator

        # Test with default hourly rate
        calc = ROICalculator(hourly_rate=50.0)
        result = calc.calculate_regional_pricing_roi(
            current_revenue=25000.0,  # $25K/month
            current_regions=1,
            game_genre="indie"
        )

        print(f"✅ ROI Calculator working!")
        print(f"   Action: {result.action_name}")
        print(f"   Total Investment: ${result.total_investment:,.0f}")
        print(f"   ROI Ratio (likely): {result.roi_likely:.1f}x")
        print(f"   Payback Period: {result.payback_period_weeks:.1f} weeks")

        # Test custom hourly rate
        calc2 = ROICalculator(hourly_rate=100.0)
        result2 = calc2.calculate_regional_pricing_roi(
            current_revenue=25000.0,
            current_regions=1,
            game_genre="indie"
        )

        if result2.total_investment == result.total_investment * 2:
            print(f"✅ Custom hourly rate working correctly!")
        else:
            print(f"❌ Custom hourly rate NOT working")
            return False

        return True

    except Exception as e:
        print(f"❌ ROI Calculator error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_claude_api_connection():
    """Test Claude API connection"""
    print("\n" + "="*80)
    print("CLAUDE API CONNECTION TEST")
    print("="*80 + "\n")

    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        return False

    try:
        import anthropic

        # Initialize client
        client = anthropic.Anthropic(api_key=api_key)

        print(f"✅ Claude client initialized")
        print(f"   API key configured: {api_key[:12]}...")

        # Try a minimal API call
        print("\n   Testing API call...")
        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=50,
                messages=[
                    {"role": "user", "content": "Say 'API test successful' and nothing else."}
                ]
            )

            response_text = message.content[0].text
            print(f"✅ Claude API call successful!")
            print(f"   Response: {response_text}")
            return True

        except Exception as api_err:
            print(f"❌ Claude API call failed: {api_err}")
            return False

    except Exception as e:
        print(f"❌ Claude API error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_report_orchestrator():
    """Test Report Orchestrator initialization"""
    print("\n" + "="*80)
    print("REPORT ORCHESTRATOR TEST")
    print("="*80 + "\n")

    try:
        from src.report_orchestrator import ReportOrchestrator

        orchestrator = ReportOrchestrator(hourly_rate=50.0)

        print(f"✅ Report Orchestrator initialized!")
        print(f"   ROI Calculator: Ready")
        print(f"   Comparable Games Analyzer: Ready")
        print(f"   Negative Review Analyzer: Ready")
        print(f"   Game Search: Ready")

        return True

    except Exception as e:
        print(f"❌ Report Orchestrator error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_executive_summary():
    """Test Executive Summary Generator"""
    print("\n" + "="*80)
    print("EXECUTIVE SUMMARY GENERATOR TEST")
    print("="*80 + "\n")

    try:
        from src.executive_summary_generator import generate_executive_summary

        summary = generate_executive_summary(
            overall_score=85.0,
            review_count=5000,
            review_percentage=92.0,
            revenue_estimate=1500000,
            review_velocity_trend="increasing",
            genre="Roguelike"
        )

        if summary and len(summary) > 100:
            print(f"✅ Executive Summary generated!")
            print(f"   Length: {len(summary)} characters")
            print(f"   Contains sections: {summary.count('###')} headers")
            return True
        else:
            print(f"❌ Executive Summary too short or empty")
            return False

    except Exception as e:
        print(f"❌ Executive Summary error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all critical API tests"""
    print("\n" + "="*80)
    print("PUBLITZ CRITICAL API TEST SUITE")
    print("="*80)

    results = {}

    # Test 1: Dependencies
    results['dependencies'] = test_dependencies()

    # Test 2: Environment variables
    results['env_vars'] = test_environment_variables()

    # Test 3: ROI Calculator
    results['roi_calc'] = test_roi_calculator()

    # Test 4: Executive Summary
    results['exec_summary'] = test_executive_summary()

    # Test 5: Claude API (only if key is set)
    if results['env_vars']:
        results['claude_api'] = test_claude_api_connection()
    else:
        results['claude_api'] = False
        print("\n⚠️  Skipping Claude API test (no API key)")

    # Test 6: Report Orchestrator
    results['orchestrator'] = test_report_orchestrator()

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80 + "\n")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All critical systems operational!")
        print("\n✅ SYSTEM STATUS: READY FOR REPORT GENERATION")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("\n📋 NEXT STEPS:")
        if not results['dependencies']:
            print("   - Install missing dependencies")
        if not results['env_vars']:
            print("   - Set ANTHROPIC_API_KEY environment variable")
        if not results['claude_api']:
            print("   - Verify Claude API key is valid")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
