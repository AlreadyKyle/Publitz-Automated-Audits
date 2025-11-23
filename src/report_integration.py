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
from src.executive_summary_generator import generate_executive_summary
from src.quick_start_generator import generate_quick_start
from src.tier_strategic_frameworks import get_framework, get_tier_from_score

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


def _extract_executive_summary_metrics(
    game_data: Dict[str, Any],
    sales_data: Dict[str, Any],
    phase2_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Extract metrics needed for executive summary generator.

    Args:
        game_data: Game data from Steam
        sales_data: Sales/market data
        phase2_data: Phase 2 enrichment data

    Returns:
        Dict with executive summary parameters
    """
    # Calculate overall score (simplified - could be more sophisticated)
    review_score_raw = float(game_data.get('review_score_raw', 70))
    owners_avg = sales_data.get('owners_avg', 0)

    # Simple scoring: weight review score heavily, add bonus for high owners
    overall_score = review_score_raw * 0.7
    if owners_avg > 100000:
        overall_score += 15
    elif owners_avg > 50000:
        overall_score += 10
    elif owners_avg > 10000:
        overall_score += 5

    overall_score = min(100, max(0, overall_score))

    # Review velocity trend
    # Simplified - would need historical data for real trend
    review_velocity_trend = "stable"  # Default

    return {
        'overall_score': overall_score,
        'review_count': game_data.get('reviews_total', 0),
        'review_percentage': review_score_raw,
        'revenue_estimate': sales_data.get('estimated_revenue', 0),
        'review_velocity_trend': review_velocity_trend,
        'genre': game_data.get('genres', ['Indie'])[0] if game_data.get('genres') else 'Indie'
    }


def _extract_quick_start_metrics(
    game_data: Dict[str, Any],
    sales_data: Dict[str, Any],
    phase2_data: Dict[str, Any],
    overall_score: float
) -> Dict[str, Any]:
    """
    Extract metrics needed for quick start action generator.

    Args:
        game_data: Game data from Steam
        sales_data: Sales/market data
        phase2_data: Phase 2 enrichment data
        overall_score: Overall game score calculated earlier

    Returns:
        Dict with quick start parameters
    """
    # Extract regional pricing info from phase2_data
    regional_pricing_present = False
    if phase2_data and 'regional_pricing' in phase2_data:
        regional_data = phase2_data.get('regional_pricing', {})
        if regional_data and 'recommended_prices' in regional_data:
            # Check if more than just USD pricing exists
            regional_pricing_present = len(regional_data.get('recommended_prices', {})) > 1

    # Pricing vs competitors (simplified - could analyze competitor data)
    base_price = game_data.get('price', 0)
    pricing_vs_competitors = 1.0  # Default: same price
    # Could enhance: compare to competitor_data average price

    # Tag count
    tag_count = len(game_data.get('tags', []))

    # Steam Deck info (would need to check game data)
    steam_deck_verified = game_data.get('steam_deck_verified', False)
    steam_deck_compatible = game_data.get('steam_deck_compatible', False)

    # Community activity (simplified)
    has_active_community = False  # Would need to check community hub activity

    # Developer response to reviews (simplified)
    responds_to_reviews = False  # Would need to check review responses

    return {
        'overall_score': overall_score,
        'review_percentage': float(game_data.get('review_score_raw', 70)),
        'review_count': game_data.get('reviews_total', 0),
        'store_page_quality_score': 5,  # Default - could analyze description
        'pricing_vs_competitors': pricing_vs_competitors,
        'regional_pricing_present': regional_pricing_present,
        'steam_deck_verified': steam_deck_verified,
        'steam_deck_compatible': steam_deck_compatible,
        'tag_count': tag_count,
        'capsule_quality_score': 5,  # Default - could analyze capsule image
        'has_active_community': has_active_community,
        'responds_to_reviews': responds_to_reviews,
        'trailer_thumbnail_quality': 5  # Default
    }


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


def _inject_all_dynamic_sections(
    ai_report: str,
    executive_summary: str,
    confidence_scorecard: str,
    quick_start: str
) -> str:
    """
    Inject all dynamic sections into AI report:
    - Replace Section 1 with dynamic Executive Summary
    - Add Section 2: Data Confidence Assessment
    - Add Section 3: Quick Start Actions
    - Renumber original Section 2+ to Section 4+

    Args:
        ai_report: The AI-generated report markdown
        executive_summary: Dynamic executive summary markdown
        confidence_scorecard: Confidence scorecard markdown
        quick_start: Quick start actions markdown

    Returns:
        Modified report with all sections injected
    """
    # Step 1: Find and replace Section 1 (Executive Summary)
    # Look for Section 1 start and Section 2 start
    section_1_pattern = r'(##\s*1\.|1\.\s*\*\*|##1\.)'
    section_2_pattern = r'(##\s*2\.|2\.\s*\*\*|##2\.)'

    section_1_match = re.search(section_1_pattern, ai_report, re.MULTILINE)
    section_2_match = re.search(section_2_pattern, ai_report, re.MULTILINE)

    if section_1_match and section_2_match:
        # Replace everything between Section 1 and Section 2 with our executive summary
        before_section_1 = ai_report[:section_1_match.start()]
        after_section_2 = ai_report[section_2_match.start():]

        # Build new report structure
        modified_report = (
            before_section_1 +
            "\n\n" + executive_summary +
            "\n\n" + confidence_scorecard +
            "\n\n" + quick_start +
            "\n\n" + after_section_2
        )

        logger.info("Injected dynamic Executive Summary, Confidence Scorecard, and Quick Start")

        # Step 2: Renumber original Section 2+ to Section 4+
        modified_report = _renumber_sections_comprehensive(modified_report)

        return modified_report

    elif section_2_match:
        # If we can't find Section 1 but found Section 2, inject before Section 2
        insertion_point = section_2_match.start()
        modified_report = (
            ai_report[:insertion_point] +
            "\n\n" + executive_summary +
            "\n\n" + confidence_scorecard +
            "\n\n" + quick_start +
            "\n\n" + ai_report[insertion_point:]
        )

        logger.info("Injected all sections before Section 2 (no Section 1 found)")
        modified_report = _renumber_sections_comprehensive(modified_report)
        return modified_report

    else:
        # If we can't find sections, append at the end
        logger.warning("Could not find section markers, appending dynamic sections at end")
        return (
            ai_report +
            "\n\n" + executive_summary +
            "\n\n" + confidence_scorecard +
            "\n\n" + quick_start
        )


def _renumber_sections_comprehensive(report: str) -> str:
    """
    Renumber sections accounting for 3 new sections at the top:
    - Section 1: Executive Summary (dynamic)
    - Section 2: Data Confidence Assessment (new)
    - Section 3: Quick Start (new)
    - Original Section 2 → Section 4
    - Original Section 3 → Section 5
    - etc.

    Args:
        report: Report markdown with sections

    Returns:
        Report with renumbered sections
    """
    lines = report.split('\n')
    modified_lines = []
    found_quick_start = False  # Track if we've passed the Quick Start section

    for line in lines:
        # Check if this line contains "Quick Start" heading
        if 'Quick Start' in line or 'QUICK START' in line:
            found_quick_start = True
            modified_lines.append(line)
            continue

        # If we've found Quick Start and this is a section header, renumber it
        if found_quick_start:
            # Match patterns like "## 2." or "2. **" or "##2."
            match = re.match(r'^(##\s*)(\d+)(\.\s*.*)$', line)
            if match:
                prefix = match.group(1)
                section_num = int(match.group(2))
                suffix = match.group(3)

                # Increment section numbers >= 2 by 2 (to account for 2 new sections)
                # Original Section 2 → Section 4, Section 3 → Section 5, etc.
                if section_num >= 2:
                    new_num = section_num + 2
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

    # CALCULATE OVERALL SCORE to determine tier framework
    logger.info("Calculating overall score to determine strategic tier...")
    review_score_raw = float(game_data.get('review_score_raw', 70))
    owners_avg = sales_data.get('owners_avg', 0)

    # Simple scoring: weight review score heavily, add bonus for high owners
    overall_score = review_score_raw * 0.7
    if owners_avg > 100000:
        overall_score += 15
    elif owners_avg > 50000:
        overall_score += 10
    elif owners_avg > 10000:
        overall_score += 5

    overall_score = min(100, max(0, overall_score))

    # Get tier framework
    tier_name = get_tier_from_score(overall_score)
    tier_framework = get_framework(overall_score)
    logger.info(f"Game score: {overall_score:.1f}/100 → Tier: {tier_name.upper()} ({tier_framework.score_range})")
    logger.info(f"Strategic frame: {tier_framework.primary_frame}")

    # Generate AI strategic analysis (now with phase2_data + tier framework for adaptive tone/focus)
    logger.info("Generating AI strategic analysis with Phase 2 data and tier framework...")
    ai_report, audit_results = ai_generator.generate_report_with_audit(
        game_data,
        sales_data,
        competitor_data,
        steamdb_data,
        report_type,
        review_stats,
        capsule_analysis,
        phase2_data=phase2_data,  # Pass phase2_data to AI generator
        tier_framework=tier_framework  # NEW: Pass tier framework for adaptive analysis
    )

    # GENERATE DYNAMIC SECTIONS: Executive Summary, Confidence Scorecard, Quick Start
    logger.info("Generating dynamic Executive Summary...")
    exec_summary_metrics = _extract_executive_summary_metrics(
        game_data, sales_data, phase2_data
    )
    executive_summary = generate_executive_summary(**exec_summary_metrics)

    logger.info("Generating Data Confidence Scorecard...")
    data_sources_info = _extract_data_sources_info(
        game_data, sales_data, phase2_data, steamdb_data
    )
    confidence_scorecard = generate_confidence_scorecard(data_sources_info)

    logger.info("Generating Quick Start actions...")
    quick_start_metrics = _extract_quick_start_metrics(
        game_data, sales_data, phase2_data, exec_summary_metrics['overall_score']
    )
    quick_start = generate_quick_start(quick_start_metrics)

    # INJECT ALL DYNAMIC SECTIONS into AI report
    logger.info("Injecting Executive Summary, Confidence Scorecard, and Quick Start into report...")
    ai_report = _inject_all_dynamic_sections(
        ai_report, executive_summary, confidence_scorecard, quick_start
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
    # Add dynamic sections metadata
    structured_data['confidence_info'] = data_sources_info
    structured_data['exec_summary_metrics'] = exec_summary_metrics
    structured_data['quick_start_metrics'] = quick_start_metrics

    logger.info("Complete report generated successfully with all dynamic sections")

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
