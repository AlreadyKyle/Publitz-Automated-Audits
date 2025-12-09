#!/usr/bin/env python3
"""
Simple network diagnostic test
Run this on your Mac to see what's actually working
"""

import requests
import sys

def test_url(name, url):
    """Test if a URL is reachable"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('-'*60)

    try:
        response = requests.get(url, timeout=10)
        print(f"✅ SUCCESS - Status: {response.status_code}")
        print(f"   Response size: {len(response.content)} bytes")
        return True
    except requests.exceptions.ProxyError as e:
        print(f"❌ PROXY ERROR: {e}")
        print("   ^ Your system is using a proxy that's blocking this")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR: {e}")
        print("   ^ Cannot reach this server")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT - Server took too long to respond")
        return False
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("PUBLITZ AUDIT SYSTEM - NETWORK DIAGNOSTIC TEST")
    print("="*60)
    print("\nThis will test if your Mac can reach the required APIs")
    print("Run this directly on your Mac (not through Claude Code)")

    results = {}

    # Test each required API
    results['Steam Store'] = test_url(
        "Steam Store API",
        "https://store.steampowered.com/api/appdetails?appids=1091500"
    )

    results['SteamSpy'] = test_url(
        "SteamSpy API",
        "https://steamspy.com/api.php?request=appdetails&appid=1091500"
    )

    results['RAWG'] = test_url(
        "RAWG API",
        "https://api.rawg.io/api/games?key=5353e48dc2a4446489ec7c0bbb1ce9e9&search=Hades&page_size=1"
    )

    results['Claude AI'] = test_url(
        "Claude AI API",
        "https://api.anthropic.com/"
    )

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, success in results.items():
        status = "✅ WORKING" if success else "❌ BLOCKED"
        print(f"{status:12} - {name}")

    print(f"\nResult: {passed}/{total} APIs reachable")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Your system can reach all required APIs!")
        print("The audit system should work on your Mac.")
        sys.exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nNext steps:")
        print("1. Check if you have proxy settings in System Settings → Network")
        print("2. Try running on a different WiFi network")
        print("3. Share this output with me so I can help debug")
        sys.exit(1)

if __name__ == "__main__":
    main()
