#!/usr/bin/env python3
"""
Publitz Automated Audit Generator
Main CLI entry point for generating customer-facing audit reports.

Usage:
    python generate_audit.py --client <client-name>
    python generate_audit.py --test  # Generate test report
"""

import argparse
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from src.input_processor import InputProcessor, ClientInputs
from src.simple_data_collector import SimpleDataCollector


def print_banner():
    """Print application banner"""
    print("\n" + "="*80)
    print("  ___  _   _ ___ _    ___ _____ _____   _   _   _ ___ ___ _____  ___ ")
    print(" | _ \\| | | | _ ) |  |_ _|_   _|_  / | | | | | |   \\_ _|_   _|/ __|")
    print(" |  _/| |_| | _ \\ |__ | |  | |  / /  | |_| |_| | |) | |  | |  \\__ \\")
    print(" |_|   \\___/|___/____|___| |_| /___|  \\___/\\___/|___/___| |_|  |___/")
    print("="*80)
    print("\n🎮 Automated Steam Game Audit Generator")
    print("💰 Professional $800-value reports in minutes")
    print("="*80 + "\n")


def setup_test_client():
    """Create example test client for testing"""
    print("🧪 Setting up test client...")

    test_client_dir = Config.INPUT_DIR / "test-client"

    # Create example inputs
    InputProcessor.create_example_inputs(Config.INPUT_DIR, "test-client")

    return "test-client"


def generate_audit(client_name: str):
    """
    Main audit generation flow.

    Args:
        client_name: Name of the client folder in inputs/
    """
    start_time = time.time()

    # Get client directories
    input_dir = Config.get_client_input_dir(client_name)
    output_dir = Config.get_client_output_dir(client_name)

    print(f"📂 Client: {client_name}")
    print(f"   Input: {input_dir}")
    print(f"   Output: {output_dir}\n")

    # ========================================================================
    # PHASE 1: Load and Validate Inputs
    # ========================================================================
    print("=" * 80)
    print("PHASE 1: INPUT VALIDATION")
    print("=" * 80)

    try:
        inputs = InputProcessor.load_inputs_from_directory(input_dir)
        print("\n✅ All inputs validated successfully\n")
    except Exception as e:
        print(f"\n❌ Input validation failed: {e}\n")
        print("💡 Required files in inputs/<client-name>/:")
        print("   - steam_url.txt")
        print("   - competitors.txt")
        print("   - intake_form.json")
        print("   - strategy_notes.txt")
        print("\n   Run with --test flag to create example inputs")
        sys.exit(1)

    # ========================================================================
    # PHASE 2: Data Collection
    # ========================================================================
    print("=" * 80)
    print("PHASE 2: DATA COLLECTION")
    print("=" * 80)

    try:
        collector = SimpleDataCollector()
        data = collector.collect_all_data(
            steam_url=inputs.steam_url,
            app_id=inputs.app_id,
            competitors=inputs.competitors[:Config.MAX_COMPETITORS],
            intake_form=inputs.intake_form
        )
        print("\n✅ Data collection completed\n")
    except Exception as e:
        print(f"\n❌ Data collection failed: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # ========================================================================
    # PHASE 3: Report Generation
    # ========================================================================
    print("=" * 80)
    print("PHASE 3: REPORT GENERATION")
    print("=" * 80)

    try:
        from src.report_generator import ReportGenerator

        generator = ReportGenerator()
        report_markdown = generator.generate_full_report(data, inputs)

    except ImportError as e:
        print(f"\n⚠️  Report generator not available: {e}")
        print("   Falling back to placeholder report\n")
        report_markdown = create_placeholder_report(data, inputs)
    except Exception as e:
        print(f"\n❌ Report generation failed: {e}")
        print("   Falling back to placeholder report\n")
        report_markdown = create_placeholder_report(data, inputs)

    # Save markdown
    markdown_path = output_dir / f"{client_name}_audit_{datetime.now().strftime('%Y%m%d')}.md"
    markdown_path.write_text(report_markdown)
    print(f"✅ Markdown saved: {markdown_path}\n")

    # ========================================================================
    # PHASE 4: PDF Export
    # ========================================================================
    print("=" * 80)
    print("PHASE 4: PDF EXPORT")
    print("=" * 80)

    try:
        from src.export_pdf import export_report_to_pdf

        pdf_path = export_report_to_pdf(
            markdown_path=markdown_path,
            game_name=data['game']['name'],
            client_name=inputs.intake_form.get('client_name', 'Unknown'),
            output_dir=output_dir
        )
        print(f"✅ PDF export complete: {pdf_path}\n")
    except ImportError as e:
        print(f"\n⚠️  PDF export not available: {e}")
        print("   Install dependencies: pip install markdown weasyprint jinja2")
        print("   Markdown report still available at: {markdown_path}\n")
    except Exception as e:
        print(f"\n⚠️  PDF export failed: {e}")
        print(f"   Markdown report still available at: {markdown_path}\n")
        import traceback
        traceback.print_exc()

    # ========================================================================
    # Complete
    # ========================================================================
    elapsed = time.time() - start_time

    print("=" * 80)
    print("✅ AUDIT GENERATION COMPLETE")
    print("=" * 80)
    print(f"\n⏱️  Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print(f"📊 Generated for: {data['game']['name']}")
    print(f"📁 Output directory: {output_dir}")
    print(f"\n📄 Generated files:")
    print(f"   - Markdown: {markdown_path.name}")
    if 'pdf_path' in locals():
        print(f"   - PDF: {pdf_path.name}")
    print("\n💡 Next steps:")
    print("   1. Review the generated report")
    print("   2. Verify all recommendations are accurate")
    print("   3. Deliver PDF to client")
    print("   4. Follow up with implementation support\n")
    print("🎉 Report ready for delivery!\n")


def create_placeholder_report(data: Dict, inputs: ClientInputs) -> str:
    """
    Create a placeholder report showing collected data.
    This will be replaced by Claude-generated report in Phase 2.
    """
    game = data['game']
    competitors = data['competitors']
    research = data['external_research']
    context = data['client_context']

    report = f"""# Pre-Launch Steam Audit Report
## {game['name']}

**Prepared for:** {inputs.intake_form['client_name']}
**Generated:** {datetime.now().strftime('%B %d, %Y')}
**Status:** Phase 1 Complete - Data Collection

---

## Executive Summary

**🎮 Game:** {game['name']}
**📅 Launch Date:** {inputs.intake_form.get('launch_date', 'TBD')}
**⏱️  Days Until Launch:** {context.get('days_until_launch', 'N/A')}
**💰 Target Price:** ${inputs.intake_form.get('target_price', 'TBD')}

---

## Data Collected

### Game Information

- **App ID:** {game.get('app_id', 'N/A')}
- **Current Price:** ${game.get('price', 'N/A')}
- **Genres:** {', '.join(game.get('genres', []))}
- **Release Date:** {game.get('release_date', 'N/A')}
- **Review Score:** {game.get('review_score', 'N/A')}% ({game.get('review_count', 0)} reviews)

### Competitive Landscape

**Analyzed {len(competitors)} competitors:**

"""

    for i, comp in enumerate(competitors, 1):
        report += f"{i}. **{comp['name']}**\n"
        report += f"   - Price: ${comp.get('price', 'N/A')}\n"
        report += f"   - Reviews: {comp.get('review_score', 'N/A')}% ({comp.get('review_count', 0)})\n"
        if comp.get('playtime', {}).get('found'):
            pt = comp['playtime']
            report += f"   - Playtime: {pt.get('main_story', 0):.1f}h (main story)\n"
        report += "\n"

    report += f"""### External Research

**Reddit Insights:**
- Subreddit: r/{research.get('reddit', {}).get('subreddit', 'N/A')}
- Top discussions: {len(research.get('reddit', {}).get('top_discussions', []))} found

**HowLongToBeat:**
- Data found: {'Yes' if research.get('hltb', {}).get('found') else 'No'}

**Launch Window:**
- Conflicts detected: {len(research.get('launch_conflicts', []))}

### Client Context

- **Team Size:** {context.get('team_size', 'N/A')} ({context.get('team_category', 'N/A')})
- **Budget Tier:** {context.get('budget_tier', 'N/A').title()}
- **Launch Status:** {context.get('launch_status', 'N/A').title()}
- **Main Concerns:** {inputs.intake_form.get('main_concerns', 'N/A')}

---

## Strategy Call Notes

{inputs.strategy_notes}

---

## Next Steps

This is a **Phase 1 placeholder report** showing all collected data.

**Phase 2** will use Claude AI to generate the full 9-section audit:
1. Compliance Audit
2. Store Page Optimization
3. Regional Pricing Strategy
4. Competitive Analysis
5. Launch Timing Analysis
6. Implementation Roadmap
7. First-Year Sales Strategy
8. Multi-Storefront Strategy
9. 90-Day Post-Launch Catalogue Management

**Phase 3** will export this as a beautifully formatted PDF.

---

*Generated by Publitz Automated Audits - Phase 1 MVP*
"""

    return report


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Generate professional Steam game audit reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_audit.py --client my-client-name
  python generate_audit.py --test  # Create and run test client
  python generate_audit.py --create-example my-client  # Create input template
        """
    )

    parser.add_argument(
        '--client',
        type=str,
        help='Client name (folder in inputs/ directory)'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Run with test/example client data'
    )

    parser.add_argument(
        '--create-example',
        type=str,
        metavar='CLIENT_NAME',
        help='Create example input files for a new client'
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ Configuration Error:\n{e}\n")
        sys.exit(1)

    # Handle commands
    if args.create_example:
        InputProcessor.create_example_inputs(Config.INPUT_DIR, args.create_example)
        print(f"\n✅ Example inputs created for client: {args.create_example}")
        print(f"📂 Location: {Config.INPUT_DIR / args.create_example}")
        print("\n💡 Edit the files with your client's data, then run:")
        print(f"   python generate_audit.py --client {args.create_example}\n")
        sys.exit(0)

    elif args.test:
        client_name = setup_test_client()
        generate_audit(client_name)

    elif args.client:
        generate_audit(args.client)

    else:
        parser.print_help()
        print("\n💡 Quick start:")
        print("   python generate_audit.py --test")
        print("   python generate_audit.py --create-example my-client")
        sys.exit(1)


if __name__ == "__main__":
    main()
