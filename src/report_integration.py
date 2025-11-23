#!/usr/bin/env python3
"""
Report Integration - Combines Enhanced Structured Reports with AI Analysis
Bridges the new modular report system with existing AI generation
"""

from typing import Dict, List, Any, Tuple
from src.logger import get_logger
from src.report_builder import ReportBuilder, CommunitySection, InfluencerSection, GlobalReachSection
from src.models import create_report_data, ReportType
from src.phase2_integration import collect_phase2_data

logger = get_logger(__name__)


def generate_enhanced_report(game_data: Dict[str, Any],
                             sales_data: Dict[str, Any],
                             competitor_data: List[Dict[str, Any]],
                             report_type: str,
                             ai_report: str = None,
                             include_phase2: bool = True) -> Tuple[str, Dict[str, Any]]:
    """
    Generate enhanced report with structured analysis + AI insights + Phase 2 enrichment

    Args:
        game_data: Game data from Steam
        sales_data: Sales/market data
        competitor_data: Competitor information
        report_type: "Pre-Launch" or "Post-Launch"
        ai_report: Optional existing AI-generated report to append
        include_phase2: Whether to include Phase 2 enrichment data

    Returns:
        Tuple of (complete_markdown_report, structured_data)
    """
    logger.info(f"Generating enhanced report for {game_data.get('name', 'Unknown')}")

    # Step 1: Build structured report using new system
    builder = ReportBuilder(game_data, sales_data, competitor_data, report_type)

    # Step 2: Collect Phase 2 enrichment data if requested
    if include_phase2:
        logger.info("Collecting Phase 2 enrichment data...")
        phase2_data = collect_phase2_data(game_data)

        # Add Phase 2 sections to report
        community_section = CommunitySection("Community", phase2_data)
        builder.add_section(community_section)

        influencer_section = InfluencerSection("Influencers", phase2_data)
        builder.add_section(influencer_section)

        global_reach_section = GlobalReachSection("Global Reach", phase2_data)
        builder.add_section(global_reach_section)

        logger.info("Phase 2 sections added to report")

    # Step 3: Build complete structured report
    structured_report = builder.build()

    # Step 4: Get structured data for exports
    structured_data = builder.get_structured_data()
    if include_phase2:
        structured_data['phase2_data'] = phase2_data

    # Step 5: Combine with AI report if provided
    if ai_report:
        # Extract sections from AI report (everything after the intro)
        # The AI report typically starts with game overview
        # We want to keep the detailed strategic analysis from AI

        complete_report = structured_report + "\n\n" + _extract_ai_strategic_sections(ai_report)
        logger.info("Combined structured report with AI strategic analysis")
    else:
        complete_report = structured_report
        logger.info("Using structured report only (no AI analysis)")

    return complete_report, structured_data


def _extract_ai_strategic_sections(ai_report: str) -> str:
    """
    Extract strategic analysis sections from AI report

    Args:
        ai_report: Full AI-generated report

    Returns:
        Strategic sections only
    """
    # The AI report has deep strategic analysis we want to keep
    # Look for market analysis, recommendations, strategy sections

    lines = ai_report.split('\n')
    strategic_start = 0

    # Find where strategic content starts (skip basic info)
    keywords = ['market analysis', 'competitive landscape', 'recommendations',
                'strategy', 'positioning', 'marketing plan', 'go-to-market']

    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in keywords):
            strategic_start = max(0, i - 2)  # Include section header
            break

    if strategic_start > 0:
        strategic_content = '\n'.join(lines[strategic_start:])
        return f"""

---

# 🎯 DETAILED STRATEGIC ANALYSIS

*The following sections provide deep strategic insights powered by AI analysis*

---

{strategic_content}
"""
    else:
        # If we can't find strategic sections, return full AI report
        return f"""

---

# 🎯 DETAILED ANALYSIS

{ai_report}
"""


def create_report_with_ai(game_data: Dict[str, Any],
                         sales_data: Dict[str, Any],
                         competitor_data: List[Dict[str, Any]],
                         steamdb_data: Dict[str, Any],
                         report_type: str,
                         ai_generator,
                         review_stats: Dict[str, Any] = None,
                         capsule_analysis: str = None) -> Tuple[str, Dict[str, Any]]:
    """
    Generate complete report: Structured analysis + AI strategic insights

    This is the main function to call from app.py

    Args:
        game_data: Game data from Steam
        sales_data: Sales/market data
        competitor_data: Competitor information
        steamdb_data: SteamDB scraper data
        report_type: "Pre-Launch" or "Post-Launch"
        ai_generator: AIGenerator instance for strategic analysis
        review_stats: Optional review statistics
        capsule_analysis: Optional capsule image analysis

    Returns:
        Tuple of (markdown_report, structured_data)
    """
    logger.info("Creating complete report with structured analysis and AI insights")

    # ENHANCED: Collect Phase 2 data BEFORE AI generation to pass real influencer/community data
    logger.info("Collecting Phase 2 enrichment data...")
    phase2_data = collect_phase2_data(game_data)
    logger.info(f"Phase 2 data collected: {', '.join(phase2_data.keys())}")

    # Generate AI strategic analysis (now with phase2_data for real influencer/community sections)
    logger.info("Generating AI strategic analysis with Phase 2 data...")
    ai_report, audit_results = ai_generator.generate_report_with_audit(
        game_data,
        sales_data,
        competitor_data,
        steamdb_data,
        report_type,
        review_stats,
        capsule_analysis,
        phase2_data=phase2_data  # NEW: Pass phase2_data to AI generator
    )

    # Generate enhanced structured report (reuse already-collected phase2_data)
    logger.info("Generating structured analysis...")
    complete_report, structured_data = generate_enhanced_report(
        game_data,
        sales_data,
        competitor_data,
        report_type,
        ai_report=ai_report,
        include_phase2=True  # Will reuse cached phase2_data collection
    )

    # Add audit results to structured data
    structured_data['audit_results'] = audit_results
    # Ensure phase2_data is in structured_data
    structured_data['phase2_data'] = phase2_data

    logger.info("Complete report generated successfully")

    return complete_report, structured_data


# Convenience function for backward compatibility
def generate_report(game_data: Dict[str, Any],
                   sales_data: Dict[str, Any],
                   competitor_data: List[Dict[str, Any]],
                   report_type: str) -> str:
    """
    Simple report generation without AI (structured only)

    Args:
        game_data: Game data
        sales_data: Sales data
        competitor_data: Competitors
        report_type: Report type

    Returns:
        Markdown report
    """
    report, _ = generate_enhanced_report(game_data, sales_data, competitor_data, report_type)
    return report
