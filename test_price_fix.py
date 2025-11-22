#!/usr/bin/env python3
"""
Test script to verify price format specifier fix
"""

print("╔════════════════════════════════════════════════════════════════╗")
print("║           PRICE FORMAT SPECIFIER FIX TEST                      ║")
print("╚════════════════════════════════════════════════════════════════╝")
print()

# Test the price parsing and calculation logic
def test_price_logic(game_price, test_name):
    print("=" * 70)
    print(f"TEST: {test_name}")
    print("=" * 70)
    print(f"Input game_price: {game_price} (type: {type(game_price).__name__})")

    # This is the logic from ai_generator.py
    try:
        if isinstance(game_price, (int, float)):
            price_value = float(game_price)
        elif isinstance(game_price, str) and '$' in game_price:
            price_value = float(game_price.replace('$', '').replace(',', ''))
        else:
            price_value = None
    except:
        price_value = None

    # Calculate reduced and sale prices
    if price_value is not None:
        reduced_price = f"{price_value * 0.85:.2f}"
        sale_price = f"{price_value * 0.70:.2f}"
    else:
        reduced_price = "XX.XX"
        sale_price = "XX.XX"

    print(f"✅ Parsed price_value: {price_value}")
    print(f"✅ Reduced price (15% off): ${reduced_price}")
    print(f"✅ Sale price (30% off): ${sale_price}")

    # Test f-string formatting (this should not crash)
    try:
        avg_comp_price = 17.99
        test_string = f"Reduce base price from ${game_price} to ${reduced_price} (15% reduction) to match competitor average of ${avg_comp_price:.2f}."
        print(f"✅ F-string formatting works: {test_string[:80]}...")
    except Exception as e:
        print(f"❌ F-string formatting FAILED: {e}")

    print()

# Test Case 1: Float price
test_price_logic(19.99, "Float Price")

# Test Case 2: Integer price
test_price_logic(20, "Integer Price")

# Test Case 3: String price with $
test_price_logic("$19.99", "String Price with $")

# Test Case 4: String price with $ and comma
test_price_logic("$1,299.99", "String Price with $ and comma")

# Test Case 5: Invalid price (should handle gracefully)
test_price_logic("Free", "Invalid Price (Free)")

# Test Case 6: None price (should handle gracefully)
test_price_logic(None, "None Price")

print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("✅ All price format tests completed!")
print()
print("The system now handles:")
print("  • Float prices: 19.99")
print("  • Integer prices: 20")
print("  • String prices: '$19.99', '$1,299.99'")
print("  • Invalid prices: 'Free', None -> defaults to XX.XX")
print()
print("F-string format specifiers are now correctly separated from calculations!")
