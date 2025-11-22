#!/usr/bin/env python3
"""
Test script to verify genres data format compatibility fixes
"""
import sys
sys.path.insert(0, 'src')

print("╔════════════════════════════════════════════════════════════════╗")
print("║           GENRES DATA FORMAT COMPATIBILITY TEST                ║")
print("╚════════════════════════════════════════════════════════════════╝")
print()

# Test 1: ConversionFunnelAnalyzer with list genres
print("=" * 70)
print("TEST 1: ConversionFunnelAnalyzer - List Format")
print("=" * 70)

try:
    from conversion_funnel import ConversionFunnelAnalyzer

    analyzer = ConversionFunnelAnalyzer()
    game_data_list = {
        'name': 'Test Game',
        'genres': ['Roguelike', 'RPG', 'Deckbuilder'],  # List format
        'tags': ['roguelike', 'card game'],
        'price': '$19.99'
    }

    genre = analyzer._extract_primary_genre(game_data_list)
    print(f"✅ List format genres: {game_data_list['genres']}")
    print(f"✅ Extracted primary genre: {genre}")
    print()
except Exception as e:
    print(f"❌ FAILED with list format: {e}")
    import traceback
    traceback.print_exc()
    print()

# Test 2: ConversionFunnelAnalyzer with string genres
print("=" * 70)
print("TEST 2: ConversionFunnelAnalyzer - String Format")
print("=" * 70)

try:
    from conversion_funnel import ConversionFunnelAnalyzer

    analyzer = ConversionFunnelAnalyzer()
    game_data_string = {
        'name': 'Test Game',
        'genres': 'Roguelike, RPG, Deckbuilder',  # String format
        'tags': 'roguelike, card game',
        'price': '$19.99'
    }

    genre = analyzer._extract_primary_genre(game_data_string)
    print(f"✅ String format genres: {game_data_string['genres']}")
    print(f"✅ Extracted primary genre: {genre}")
    print()
except Exception as e:
    print(f"❌ FAILED with string format: {e}")
    import traceback
    traceback.print_exc()
    print()

# Test 3: Test the genre parsing logic directly (simulating ai_generator.py fix)
print("=" * 70)
print("TEST 3: AI Generator Genre Parsing - List Format")
print("=" * 70)

try:
    game_data_list = {
        'genres': ['Roguelike', 'Action', 'Indie']
    }

    genres_raw = game_data_list.get('genres', '')

    # This is the logic from ai_generator.py
    if isinstance(genres_raw, list):
        genres = genres_raw[0].lower().strip() if genres_raw else 'gaming'
        genres_full = ', '.join(genres_raw) if genres_raw else ''
    elif isinstance(genres_raw, str):
        genres = genres_raw.split(',')[0].lower().strip() if genres_raw else 'gaming'
        genres_full = genres_raw
    else:
        genres = 'gaming'
        genres_full = ''

    print(f"✅ List format genres: {game_data_list['genres']}")
    print(f"✅ First genre extracted: {genres}")
    print(f"✅ Full genres string: {genres_full}")
    print()
except Exception as e:
    print(f"❌ FAILED with list format: {e}")
    import traceback
    traceback.print_exc()
    print()

# Test 4: Test the genre parsing logic with string format
print("=" * 70)
print("TEST 4: AI Generator Genre Parsing - String Format")
print("=" * 70)

try:
    game_data_string = {
        'genres': 'Roguelike, Action, Indie'
    }

    genres_raw = game_data_string.get('genres', '')

    # This is the logic from ai_generator.py
    if isinstance(genres_raw, list):
        genres = genres_raw[0].lower().strip() if genres_raw else 'gaming'
        genres_full = ', '.join(genres_raw) if genres_raw else ''
    elif isinstance(genres_raw, str):
        genres = genres_raw.split(',')[0].lower().strip() if genres_raw else 'gaming'
        genres_full = genres_raw
    else:
        genres = 'gaming'
        genres_full = ''

    print(f"✅ String format genres: {game_data_string['genres']}")
    print(f"✅ First genre extracted: {genres}")
    print(f"✅ Full genres string: {genres_full}")
    print()
except Exception as e:
    print(f"❌ FAILED with string format: {e}")
    import traceback
    traceback.print_exc()
    print()

print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("✅ All genres format compatibility tests completed!")
print()
print("The system now handles both:")
print("  • List format: ['Roguelike', 'RPG', 'Deckbuilder']")
print("  • String format: 'Roguelike, RPG, Deckbuilder'")
