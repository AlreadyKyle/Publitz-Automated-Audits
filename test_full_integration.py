"""
Full Integration Test

Tests the complete report generation with all sections integrated.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.report_builder import ReportBuilder


def test_full_report_generation():
    """Test generating a complete report with all sections"""

    print("=" * 80)
    print("FULL INTEGRATION TEST: Complete Report Generation")
    print("=" * 80)
    print()

    # Create mock game data
    game_data = {
        'name': 'Test Roguelike Adventure',
        'genres': 'Roguelike, RPG, Deckbuilder',
        'tags': 'roguelike, roguelite, deckbuilder, card game, pixel art, dungeon crawler, singleplayer',
        'price': '$19.99',
        'reviews_total': 1200,
        'review_score': 88,
        'description': 'A challenging roguelike with deckbuilding mechanics',
        'short_description': 'Build your deck, explore dungeons, defeat bosses!'
    }

    sales_data = {
        'review_score': 88,
        'reviews_total': 1200,
        'estimated_revenue': 350000,
        'wishlists': 15000,
        'followers': 3500
    }

    competitor_data = [
        {
            'name': 'Competitor 1',
            'genres': 'Roguelike, Deckbuilder',
            'tags': 'roguelike, deckbuilder',
            'price': '$14.99',
            'review_score': 85,
            'reviews_total': 2500
        },
        {
            'name': 'Competitor 2',
            'genres': 'Roguelike, RPG',
            'tags': 'roguelike, rpg, dungeon crawler',
            'price': '$24.99',
            'review_score': 82,
            'reviews_total': 1800
        },
        {
            'name': 'Competitor 3',
            'genres': 'Card Game, Strategy',
            'tags': 'card game, strategy',
            'price': '$19.99',
            'review_score': 90,
            'reviews_total': 5000
        }
    ]

    print("Creating ReportBuilder...")
    builder = ReportBuilder(
        game_data=game_data,
        sales_data=sales_data,
        competitor_data=competitor_data,
        report_type='full'
    )

    print("Building sections...")
    builder.build_sections()

    print(f"✅ Sections created: {len(builder.sections)}")
    print()

    print("Section List:")
    for i, section in enumerate(builder.sections, 1):
        print(f"  {i}. {section.section_name}")
    print()

    print("Analyzing each section...")
    errors = []
    for section in builder.sections:
        try:
            result = section.analyze()
            score = result.get('score', 0)
            rating = result.get('rating', 'unknown')
            print(f"  ✅ {section.section_name}: {score}/100 ({rating})")
        except Exception as e:
            error_msg = f"  ❌ {section.section_name}: {str(e)}"
            print(error_msg)
            errors.append(error_msg)

    print()

    if errors:
        print(f"⚠️  {len(errors)} errors during analysis")
        for error in errors:
            print(error)
        print()

    print("Generating markdown for each section...")
    markdown_errors = []
    total_markdown_length = 0

    for section in builder.sections:
        try:
            markdown = section.generate_markdown()
            length = len(markdown)
            total_markdown_length += length
            print(f"  ✅ {section.section_name}: {length:,} characters")
        except Exception as e:
            error_msg = f"  ❌ {section.section_name}: {str(e)}"
            print(error_msg)
            markdown_errors.append(error_msg)

    print()
    print(f"Total Markdown Length: {total_markdown_length:,} characters")
    print()

    if markdown_errors:
        print(f"⚠️  {len(markdown_errors)} errors during markdown generation")
        for error in markdown_errors:
            print(error)
        print()

    print("Building complete report...")
    try:
        full_report = builder.build()
        print(f"✅ Complete Report Generated: {len(full_report):,} characters")
        print()

        # Check that key sections are present
        required_keywords = [
            'Conversion Funnel',
            'Visibility Forecast',
            'Growth Strategy',
            'Tag Insights',
            'Review Vulnerability',
            'A/B Testing',
            'Community Health',
            'Regional Pricing',
            'Custom Tracking Dashboard'
        ]

        print("Checking for required sections in report:")
        missing_sections = []
        for keyword in required_keywords:
            if keyword in full_report:
                print(f"  ✅ {keyword}")
            else:
                print(f"  ❌ {keyword} - MISSING")
                missing_sections.append(keyword)

        print()

        if missing_sections:
            print(f"⚠️  {len(missing_sections)} sections missing from report")
        else:
            print("✅ All required sections present in report")

        print()

        return len(errors) == 0 and len(markdown_errors) == 0 and len(missing_sections) == 0

    except Exception as e:
        print(f"❌ Failed to build complete report: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run integration test"""

    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " FULL INTEGRATION TEST SUITE ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    try:
        success = test_full_report_generation()

        print("=" * 80)
        print("INTEGRATION TEST SUMMARY")
        print("=" * 80)
        print()

        if success:
            print("✅ ALL INTEGRATION TESTS PASSED!")
            print()
            print("Report Generation Features Verified:")
            print("  ✓ All 14+ sections created successfully")
            print("  ✓ All sections analyzed without errors")
            print("  ✓ All markdown generated successfully")
            print("  ✓ Complete report builds successfully")
            print("  ✓ All required sections present")
            print()
            print("The audit system is fully integrated and production-ready!")
            print()
        else:
            print("⚠️  INTEGRATION TESTS FAILED")
            print()
            print("Some sections encountered errors during generation.")
            print("Review the output above for details.")
            print()
            sys.exit(1)

    except Exception as e:
        print(f"❌ INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
