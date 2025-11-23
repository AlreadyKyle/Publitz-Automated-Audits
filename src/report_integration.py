#!/usr/bin/env python3
"""
Report Integration - Combines Enhanced Structured Reports with AI Analysis
Bridges the new modular report system with existing AI generation
"""

from typing import Dict, List, Any, Tuple
import re
from src.logger import get_logger
from src.report_builder import ReportBuilder, CommunitySection, InfluencerSection, GlobalReachSection
from src.models import create_report_data, ReportType
from src.phase2_integration import collect_phase2_data
from src.confidence_scorecard_generator import generate_confidence_scorecard

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


def _extract_data_sources_info(
    game_data: Dict[str, Any],
    sales_data: Dict[str, Any],
    phase2_data: Dict[str, Any],
    steamdb_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Extract information about which data sources were used for confidence scorecard.

    Args:
        game_data: Game data from Steam
        sales_data: Sales/market data
        phase2_data: Phase 2 enrichment data
        steamdb_data: SteamDB scraper data

    Returns:
        Dict with data source availability information
    """
    # Review data - always available from Steam API
    review_data_available = bool(game_data.get('reviews_total', 0) > 0 or game_data.get('review_score'))

    # SteamSpy data - check if owner counts are available
    steamspy_available = bool(sales_data.get('owners_avg') or sales_data.get('owners_min'))

    # Revenue calculation method
    if sales_data.get('estimation_method') == 'enhanced':
        revenue_method = 'calculated'
    elif sales_data.get('estimated_revenue'):
        revenue_method = 'calculated'
    else:
        revenue_method = 'estimated'

    # Regional revenue - always industry average unless we have actual data
    regional_revenue_source = 'industry_average'

    # Sentiment analysis - check if we have real analyzed reviews
    sentiment_analyzed = False
    sentiment_sample_size = 0
    if phase2_data and 'sentiment' in phase2_data:
        sentiment_data = phase2_data['sentiment']
        if sentiment_data and 'sentiment_data' in sentiment_data:
            sentiment_analyzed = True
            sample_data = sentiment_data['sentiment_data'].get('sample_size', {})
            if isinstance(sample_data, dict):
                sentiment_sample_size = sample_data.get('positive', 0) + sample_data.get('negative', 0)
            else:
                sentiment_sample_size = 0

    # Competitor data - assume available if we have competitors
    competitor_data_available = True  # Usually available from Steam

    # Influencer data - check Phase 2 data
    influencer_data_available = False
    if phase2_data:
        twitch_data = phase2_data.get('twitch', {})
        youtube_data = phase2_data.get('youtube', {})
        # Check if we have real influencer data (not just fallback)
        if (twitch_data and twitch_data.get('streamers')) or (youtube_data and youtube_data.get('channels')):
            influencer_data_available = True

    # Regional pricing - check if we have PPP-based pricing
    regional_pricing_method = 'ppp'  # Default to PPP calculations
    if phase2_data and 'regional_pricing' in phase2_data:
        regional_pricing_method = 'ppp'  # We use PPP calculations in phase2

    return {
        'review_data_available': review_data_available,
        'steamspy_available': steamspy_available,
        'revenue_method': revenue_method,
        'regional_revenue_source': regional_revenue_source,
        'sentiment_analyzed': sentiment_analyzed,
        'sentiment_sample_size': sentiment_sample_size,
        'competitor_data_available': competitor_data_available,
        'influencer_data_available': influencer_data_available,
        'regional_pricing_method': regional_pricing_method
    }


def _inject_confidence_scorecard(ai_report: str, scorecard: str) -> str:
    """
    Inject confidence scorecard after Section 1 (Executive Summary) in AI report.

    Args:
        ai_report: The AI-generated report markdown
        scorecard: The confidence scorecard markdown

    Returns:
        Modified report with scorecard injected
    """
    # Find the end of Section 1 (Executive Summary)
    # Look for patterns like "## 2." or "2. **" or "##2." indicating Section 2
    pattern = r'((?:^|\n)(?:##\s*2\.|2\.\s*\*\*|##2\.))'

    match = re.search(pattern, ai_report, re.MULTILINE)

    if match:
        # Inject scorecard before Section 2
        insertion_point = match.start()
        modified_report = (
            ai_report[:insertion_point] +
            "\n\n" + scorecard + "\n\n" +
            ai_report[insertion_point:]
        )
        logger.info("Confidence scorecard injected after Executive Summary")

        # Now renumber sections 2 onwards to 3 onwards
        modified_report = _renumber_sections(modified_report)

        return modified_report
    else:
        # If we can't find Section 2, append at the end
        logger.warning("Could not find Section 2 in AI report, appending scorecard at end")
        return ai_report + "\n\n" + scorecard


def _renumber_sections(report: str) -> str:
    """
    Renumber sections starting from Section 2 onwards (shift by 1).
    Since we injected the scorecard as Section 2, we need to shift
    the original Section 2 to Section 3, Section 3 to Section 4, etc.

    Args:
        report: Report markdown with sections

    Returns:
        Report with renumbered sections
    """
    lines = report.split('\n')
    modified_lines = []
    section_shifted = False  # Track if we've passed the confidence scorecard

    for line in lines:
        # Check if this line contains "## 2. DATA CONFIDENCE ASSESSMENT"
        if '## 2. DATA CONFIDENCE ASSESSMENT' in line or 'DATA CONFIDENCE ASSESSMENT' in line:
            section_shifted = True
            modified_lines.append(line)
            continue

        # If we've shifted and this is a section header, renumber it
        if section_shifted:
            # Match patterns like "## 2." or "2. **" or "##2." (original section numbers)
            # We want to increment numbers >= 2
            match = re.match(r'^(##\s*)(\d+)(\.\s*.*)$', line)
            if match:
                prefix = match.group(1)
                section_num = int(match.group(2))
                suffix = match.group(3)

                # Increment section numbers >= 2 (the original Section 2 becomes Section 3, etc.)
                if section_num >= 2:
                    new_num = section_num + 1
                    modified_lines.append(f"{prefix}{new_num}{suffix}")
                else:
                    modified_lines.append(line)
            else:
                modified_lines.append(line)
        else:
            modified_lines.append(line)

    return '\n'.join(modified_lines)


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

    # INJECT CONFIDENCE SCORECARD: Extract data sources and generate scorecard
    logger.info("Generating confidence scorecard...")
    data_sources_info = _extract_data_sources_info(
        game_data, sales_data, phase2_data, steamdb_data
    )
    confidence_scorecard = generate_confidence_scorecard(data_sources_info)

    # Inject scorecard into AI report as Section 2 (after Executive Summary)
    logger.info("Injecting confidence scorecard into report...")
    ai_report = _inject_confidence_scorecard(ai_report, confidence_scorecard)

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
    # Add confidence scorecard metadata
    structured_data['confidence_info'] = data_sources_info

    logger.info("Complete report generated successfully with confidence scorecard")

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
