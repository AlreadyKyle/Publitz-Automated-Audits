#!/usr/bin/env python3
"""
API Health Check - Diagnostic Tool for System Administrator

This tool verifies all APIs are working correctly BEFORE generating client reports.
Run this regularly to ensure your system is operational.

Usage:
    python diagnostics/api_health_check.py

Output:
    - Console report showing which APIs are working
    - Saved to diagnostics/api_health_report.txt
"""

import os
import sys
import requests
from datetime import datetime
from typing import Dict, Tuple, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def test_steam_store_api() -> Tuple[bool, str, Optional[float]]:
    """Test Steam Store API (FREE, no key needed)"""
    try:
        import time
        start = time.time()

        # Test with Hades II app ID
        url = "https://store.steampowered.com/api/appdetails?appids=1145350"
        response = requests.get(url, timeout=10)

        elapsed = (time.time() - start) * 1000  # ms

        if response.status_code == 200:
            data = response.json()
            if '1145350' in data and data['1145350']['success']:
                return True, "Successfully retrieved game data", elapsed
            else:
                return False, "Invalid response format", elapsed
        else:
            return False, f"HTTP {response.status_code}", elapsed

    except Exception as e:
        return False, str(e), None


def test_steam_web_api() -> Tuple[bool, str, Optional[float]]:
    """Test Steam Web API (FREE, requires key)"""
    try:
        import time

        api_key = os.getenv('STEAM_WEB_API_KEY')
        if not api_key:
            return False, "API key not configured in .env", None

        start = time.time()

        # Test GetAppList endpoint
        url = f"https://api.steampowered.com/ISteamApps/GetAppList/v2/?key={api_key}"
        response = requests.get(url, timeout=10)

        elapsed = (time.time() - start) * 1000

        if response.status_code == 200:
            data = response.json()
            if 'applist' in data and 'apps' in data['applist']:
                app_count = len(data['applist']['apps'])
                return True, f"Successfully retrieved {app_count:,} apps", elapsed
            else:
                return False, "Invalid response format", elapsed
        else:
            return False, f"HTTP {response.status_code}", elapsed

    except Exception as e:
        return False, str(e), None


def test_steamspy_api() -> Tuple[bool, str, Optional[float]]:
    """Test SteamSpy API (FREE, no key needed)"""
    try:
        import time
        start = time.time()

        # Test with Hades II
        url = "https://steamspy.com/api.php?request=appdetails&appid=1145350"
        response = requests.get(url, timeout=10)

        elapsed = (time.time() - start) * 1000

        if response.status_code == 200:
            data = response.json()
            if data.get('name'):
                owners = data.get('owners', 'Unknown')
                return True, f"Retrieved owner data: {owners}", elapsed
            else:
                return False, "Invalid response format", elapsed
        else:
            return False, f"HTTP {response.status_code}", elapsed

    except Exception as e:
        return False, str(e), None


def test_steam_reviews_api() -> Tuple[bool, str, Optional[float]]:
    """Test Steam Reviews API (FREE, no key needed)"""
    try:
        import time
        start = time.time()

        url = "https://store.steampowered.com/appreviews/1145350?json=1&filter=recent&num_per_page=10"
        response = requests.get(url, timeout=10)

        elapsed = (time.time() - start) * 1000

        if response.status_code == 200:
            data = response.json()
            if data.get('success') == 1:
                review_count = len(data.get('reviews', []))
                return True, f"Retrieved {review_count} recent reviews", elapsed
            else:
                return False, "API returned success=0", elapsed
        else:
            return False, f"HTTP {response.status_code}", elapsed

    except Exception as e:
        return False, str(e), None


def test_anthropic_api() -> Tuple[bool, str, Optional[float]]:
    """Test Anthropic/Claude API (PAID, requires key)"""
    try:
        import time

        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return False, "API key not configured in .env", None

        start = time.time()

        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        # Simple test message
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=20,
            messages=[{"role": "user", "content": "Respond with: API test successful"}]
        )

        elapsed = (time.time() - start) * 1000

        response_text = message.content[0].text
        return True, f"Response: {response_text[:50]}", elapsed

    except Exception as e:
        return False, str(e), None


def test_steamcharts_scraping() -> Tuple[bool, str, Optional[float]]:
    """Test SteamCharts access (FREE, web scraping)"""
    try:
        import time
        start = time.time()

        url = "https://steamcharts.com/app/1145350"
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        elapsed = (time.time() - start) * 1000

        if response.status_code == 200:
            # Check if page contains expected data
            if 'Concurrent Steam Users' in response.text or 'Peak Players' in response.text:
                return True, "Successfully accessed player data", elapsed
            else:
                return False, "Page structure may have changed", elapsed
        else:
            return False, f"HTTP {response.status_code}", elapsed

    except Exception as e:
        return False, str(e), None


def generate_health_report() -> Dict:
    """Run all API health checks and generate report"""

    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}API HEALTH CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    tests = {
        'Steam Store API': {
            'function': test_steam_store_api,
            'category': 'CRITICAL',
            'cost': 'FREE',
            'description': 'Basic game info (name, price, description)'
        },
        'Steam Web API': {
            'function': test_steam_web_api,
            'category': 'RECOMMENDED',
            'cost': 'FREE',
            'description': 'Additional official endpoints (app list, player stats)'
        },
        'SteamSpy API': {
            'function': test_steamspy_api,
            'category': 'CRITICAL',
            'cost': 'FREE',
            'description': 'Owner counts (ONLY source for this data)'
        },
        'Steam Reviews API': {
            'function': test_steam_reviews_api,
            'category': 'CRITICAL',
            'cost': 'FREE',
            'description': 'Individual reviews for sentiment analysis'
        },
        'Anthropic/Claude API': {
            'function': test_anthropic_api,
            'category': 'RECOMMENDED',
            'cost': 'PAID',
            'description': 'AI-powered review categorization (your differentiator)'
        },
        'SteamCharts': {
            'function': test_steamcharts_scraping,
            'category': 'OPTIONAL',
            'cost': 'FREE',
            'description': 'Historical player count data'
        }
    }

    results = {}

    for api_name, config in tests.items():
        print(f"Testing {api_name}... ", end='', flush=True)

        success, message, elapsed = config['function']()

        results[api_name] = {
            'success': success,
            'message': message,
            'elapsed_ms': elapsed,
            'category': config['category'],
            'cost': config['cost'],
            'description': config['description']
        }

        if success:
            status = f"{GREEN}✓ PASS{RESET}"
            if elapsed:
                status += f" ({elapsed:.0f}ms)"
        else:
            status = f"{RED}✗ FAIL{RESET}"

        print(status)

        # Show details for failures
        if not success:
            print(f"  {YELLOW}└─ {message}{RESET}")

    return results


def print_summary(results: Dict):
    """Print summary of results"""

    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}SUMMARY{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    # Count by category
    critical = [name for name, r in results.items() if r['category'] == 'CRITICAL']
    critical_pass = [name for name in critical if results[name]['success']]

    recommended = [name for name, r in results.items() if r['category'] == 'RECOMMENDED']
    recommended_pass = [name for name in recommended if results[name]['success']]

    optional = [name for name, r in results.items() if r['category'] == 'OPTIONAL']
    optional_pass = [name for name in optional if results[name]['success']]

    print(f"CRITICAL APIs:     {len(critical_pass)}/{len(critical)} operational")
    print(f"RECOMMENDED APIs:  {len(recommended_pass)}/{len(recommended)} operational")
    print(f"OPTIONAL APIs:     {len(optional_pass)}/{len(optional)} operational")
    print()

    # System status
    critical_ok = len(critical_pass) == len(critical)

    if critical_ok:
        print(f"{GREEN}✓ SYSTEM READY{RESET} - All critical APIs operational")
        print(f"\nYou can generate client reports with full functionality.")
    else:
        print(f"{RED}✗ SYSTEM NOT READY{RESET} - Critical APIs are down")
        print(f"\n{YELLOW}Failed critical APIs:{RESET}")
        for name in critical:
            if not results[name]['success']:
                print(f"  - {name}: {results[name]['message']}")
        print(f"\n{YELLOW}You should NOT generate client reports until critical APIs are fixed.{RESET}")

    # Detailed breakdown
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}DETAILED STATUS{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    for api_name, result in results.items():
        status_icon = f"{GREEN}✓{RESET}" if result['success'] else f"{RED}✗{RESET}"
        category_color = {
            'CRITICAL': RED,
            'RECOMMENDED': YELLOW,
            'OPTIONAL': BLUE
        }.get(result['category'], RESET)

        print(f"{status_icon} {api_name}")
        print(f"   Category: {category_color}{result['category']}{RESET} | Cost: {result['cost']}")
        print(f"   Purpose: {result['description']}")
        print(f"   Status: {result['message']}")
        if result['elapsed_ms']:
            print(f"   Response Time: {result['elapsed_ms']:.0f}ms")
        print()


def save_report(results: Dict):
    """Save report to file"""

    os.makedirs('diagnostics', exist_ok=True)

    report_path = 'diagnostics/api_health_report.txt'

    with open(report_path, 'w') as f:
        f.write(f"API HEALTH CHECK REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*80}\n\n")

        for api_name, result in results.items():
            status = "PASS" if result['success'] else "FAIL"
            f.write(f"[{status}] {api_name}\n")
            f.write(f"  Category: {result['category']}\n")
            f.write(f"  Cost: {result['cost']}\n")
            f.write(f"  Description: {result['description']}\n")
            f.write(f"  Status: {result['message']}\n")
            if result['elapsed_ms']:
                f.write(f"  Response Time: {result['elapsed_ms']:.0f}ms\n")
            f.write("\n")

        # Summary
        critical = [name for name, r in results.items() if r['category'] == 'CRITICAL']
        critical_pass = [name for name in critical if results[name]['success']]

        f.write(f"{'='*80}\n")
        f.write(f"SUMMARY\n")
        f.write(f"{'='*80}\n\n")
        f.write(f"Critical APIs: {len(critical_pass)}/{len(critical)} operational\n")

        if len(critical_pass) == len(critical):
            f.write(f"\nSYSTEM READY - All critical APIs operational\n")
        else:
            f.write(f"\nSYSTEM NOT READY - Critical APIs are down\n")

    print(f"\n{BLUE}Report saved to: {report_path}{RESET}\n")


def main():
    """Run API health check"""

    # Run all tests
    results = generate_health_report()

    # Print summary
    print_summary(results)

    # Save report
    save_report(results)

    # Exit code
    critical = [name for name, r in results.items() if r['category'] == 'CRITICAL']
    critical_pass = [name for name in critical if results[name]['success']]

    return 0 if len(critical_pass) == len(critical) else 1


if __name__ == "__main__":
    exit(main())
