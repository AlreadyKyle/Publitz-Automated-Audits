#!/usr/bin/env python3
"""
Report Orchestrator - Master assembly system for tiered game audit reports

This module orchestrates all report components and assembles them into
three tiered versions:
- Tier 1 Executive: 2-3 pages, essential insights only
- Tier 2 Strategic: 8-12 pages, strategic overview
- Tier 3 Deep-dive: 30-40 pages, complete analysis

Usage:
    orchestrator = ReportOrchestrator()
    reports = orchestrator.generate_complete_report(game_data)
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import re

from src.executive_summary_generator import generate_executive_summary
from src.roi_calculator import ROICalculator
from src.comparable_games_analyzer import ComparableGamesAnalyzer
from src.negative_review_analyzer import NegativeReviewAnalyzer
from src.game_search import GameSearch
from src.game_analyzer import GameAnalyzer
from src.api_verifier import APIVerifier, APIStatus
from src.revenue_based_scoring import (
    classify_revenue_tier,
    apply_revenue_modifier,
    calculate_overall_score as calculate_revenue_based_score,
    generate_reality_check_warning
)
from src.score_validation import (
    GameMetrics as ScoreGameMetrics,
    calculate_maximum_possible_score,
    enforce_score_cap,
    validate_before_generation,
    generate_cap_explanation_report
)
from src.data_consistency import (
    GameMetrics as DataGameMetrics,
    pre_flight_check,
    validate_report_consistency
)

logger = logging.getLogger(__name__)


@dataclass
class ReportMetadata:
    """Metadata about the generated report"""
    overall_score: float
    performance_tier: int
    tier_name: str
    generated_at: datetime
    game_name: str
    app_id: str
    confidence_level: str
    word_count: Dict[str, int]
    has_negative_reviews: bool
    has_comparables: bool
    revenue_tier: Optional[Any] = None  # RevenueTier object from revenue_based_scoring
    revenue_reality_check: Optional[str] = None  # Warning message if score was adjusted
    score_caps: Optional[Any] = None  # ScoreCaps object from score_validation
    was_capped: bool = False  # Whether score was capped by validation
    original_score: Optional[float] = None  # Score before capping
    cap_explanation: Optional[str] = None  # Explanation of why score was capped


@dataclass
class ReportComponents:
    """All generated report components"""
    executive_summary: str
    confidence_scorecard: str
    quick_start: str
    key_metrics_dashboard: str
    market_positioning: str
    comparable_games: str
    revenue_performance: str
    strategic_recommendations: str
    action_plan_30_day: str
    negative_review_analysis: Optional[str] = None
    salvageability_assessment: Optional[str] = None
    market_expansion: Optional[str] = None
    dlc_analysis: Optional[str] = None
    detailed_competitive: Optional[str] = None
    regional_breakdowns: Optional[str] = None
    store_optimization: Optional[str] = None
    methodology: Optional[str] = None


class ReportOrchestrator:
    """
    Master orchestrator for complete tiered report generation.

    Coordinates all report components and assembles them into
    appropriate tiers based on game performance.
    """

    def __init__(self, hourly_rate: float = 50.0, claude_api_key: Optional[str] = None):
        """
        Initialize orchestrator with all component generators.

        Args:
            hourly_rate: Developer hourly rate for ROI calculations
            claude_api_key: Optional Claude API key for negative review analysis.
                          If not provided, will try to load from environment.
        """
        import os

        self.roi_calculator = ROICalculator(hourly_rate=hourly_rate)
        self.comparable_analyzer = ComparableGamesAnalyzer()

        # Initialize negative analyzer with API key
        api_key = claude_api_key or os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            self.negative_analyzer = NegativeReviewAnalyzer(claude_api_key=api_key)
        else:
            logger.warning("No Claude API key provided - negative review analysis will be unavailable")
            self.negative_analyzer = None

        self.game_search = GameSearch()
        self.game_analyzer = GameAnalyzer()

        # Initialize API verifier for tracking data sources
        self.api_verifier = APIVerifier()

        logger.info("Report orchestrator initialized")

    def generate_complete_report(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assemble complete tiered report based on game performance.

        Args:
            game_data: Dict containing all game metrics including:
                - app_id: Steam app ID
                - name: Game name
                - price: Current price
                - review_score: Overall review percentage
                - review_count: Total review count
                - owners: Owner count estimate
                - revenue: Revenue estimate
                - genres: List of genre tags
                - release_date: Launch date
                - sales_data: Optional sales data dict

        Returns:
            Dict with three report versions and metadata:
            {
                'tier_1_executive': str (2-3 pages),
                'tier_2_strategic': str (8-12 pages),
                'tier_3_deepdive': str (30-40 pages),
                'metadata': ReportMetadata,
                'components': ReportComponents,
                'api_status': Dict with API verification results
            }
        """
        logger.info(f"Generating complete report for {game_data.get('name', 'Unknown')}")

        # Reset API verifier for this report
        self.api_verifier.reset()

        # Track data sources used in game_data input
        self._track_input_data_sources(game_data)

        # Step 0a: DATA CONSISTENCY VALIDATION - Check for contradictions
        logger.info("Running pre-flight data consistency check...")
        is_valid, data_metrics, consistency_messages = pre_flight_check(game_data)

        if not is_valid:
            logger.error(f"Data consistency check failed for {game_data.get('name')}")
            for msg in consistency_messages:
                logger.error(f"  {msg}")
            # Return error report
            error_message = "\n".join(consistency_messages)
            return self._generate_data_error_report(game_data, error_message)

        if consistency_messages:
            logger.warning(f"Data consistency warnings for {game_data.get('name')}:")
            for msg in consistency_messages:
                logger.warning(f"  {msg}")

        # Use validated metrics from here forward
        logger.info("Data consistency check passed")

        # Step 0b: SCORE VALIDATION - Check if report generation is appropriate
        game_metrics = ScoreGameMetrics(
            revenue=data_metrics.revenue_gross,
            days_since_launch=data_metrics.days_since_launch,
            review_count_total=data_metrics.review_count_total,
            review_percentage=data_metrics.review_percentage,
            owner_count=data_metrics.owner_count
        )

        should_generate, validation_warning = validate_before_generation(game_metrics)
        if not should_generate:
            logger.warning(f"Insufficient data for {game_data.get('name')}: {validation_warning[:100]}")
            # Return minimal report explaining why we can't generate
            return self._generate_insufficient_data_report(game_data, validation_warning)

        # Step 1: Calculate maximum possible score based on commercial reality
        score_caps = calculate_maximum_possible_score(game_metrics)
        logger.info(f"Maximum possible score: {score_caps.maximum_score}/100 (limited by {score_caps.limiting_factor})")

        # Step 2: Classify revenue tier (prevents score inflation)
        # Use validated data from data_metrics
        revenue_tier = classify_revenue_tier(
            revenue_estimate=data_metrics.revenue_gross,
            days_since_launch=data_metrics.days_since_launch
        )
        logger.info(f"Revenue tier: {revenue_tier.tier_name} (${revenue_tier.daily_revenue:.2f}/day)")

        # Step 3: Calculate old-style section scores (for comparison/adjustment)
        raw_score = self._calculate_overall_score(game_data)
        logger.info(f"Raw score (before revenue adjustment): {raw_score:.1f}/100")

        # Step 4: Apply revenue-based scoring to get realistic final score
        # This prevents games with $379 revenue from scoring 88/100
        section_scores = {
            'base_performance': raw_score
        }
        modified_sections = apply_revenue_modifier(section_scores, revenue_tier)

        # Calculate final revenue-adjusted overall score
        review_metrics = {
            'review_percentage': game_data.get('review_score', 0),
            'review_count': game_data.get('review_count', 0)
        }
        overall_calc = calculate_revenue_based_score(
            modified_sections,
            revenue_tier,
            review_metrics
        )
        calculated_score = overall_calc['overall_score']
        logger.info(f"Calculated score (after revenue adjustment): {calculated_score}/100")

        # Step 5: ENFORCE HARD CAPS - Score can NEVER exceed what reality justifies
        cap_result = enforce_score_cap(calculated_score, score_caps, game_metrics)
        score = cap_result['final_score']
        was_capped = cap_result['was_capped']

        if was_capped:
            logger.warning(f"Score CAPPED: {calculated_score}/100 → {score}/100 "
                          f"(limited by {score_caps.limiting_factor})")
        else:
            logger.info(f"Final score: {score}/100 (within cap of {score_caps.maximum_score}/100)")

        # Step 6: Determine performance tier based on final score
        tier = self._determine_tier(score)
        tier_name = self._get_tier_name(tier)
        logger.info(f"Performance tier: {tier} ({tier_name})")

        # Step 7: Generate reality check warning if needed
        reality_warning = generate_reality_check_warning(
            revenue_tier,
            score,
            modified_sections
        )
        if reality_warning:
            logger.warning(f"Reality check triggered for {game_data.get('name')}: Score reduced from {raw_score} to {score}")

        # Step 8: Generate cap explanation (always generate, will explain even if not capped)
        cap_explanation = generate_cap_explanation_report(
            score_caps,
            game_metrics,
            score,
            was_capped
        )

        # Step 9: Generate all components
        components = self._generate_all_components(game_data, tier, score)
        logger.info("All components generated")

        # Step 10: Assemble three report tiers (with cap explanation)
        tier_1_report = self._assemble_executive_brief(
            components, game_data, tier, reality_warning, cap_explanation
        )
        tier_2_report = self._assemble_strategic_overview(
            components, game_data, tier, reality_warning, cap_explanation
        )
        tier_3_report = self._assemble_full_report(
            components, game_data, tier, reality_warning, cap_explanation
        )

        # Step 11: Calculate metadata
        metadata = ReportMetadata(
            overall_score=score,
            performance_tier=tier,
            tier_name=tier_name,
            generated_at=datetime.now(),
            game_name=game_data.get('name', 'Unknown'),
            app_id=str(game_data.get('app_id', '')),
            confidence_level=self._calculate_report_confidence(components),
            word_count={
                'tier_1': self._count_words(tier_1_report),
                'tier_2': self._count_words(tier_2_report),
                'tier_3': self._count_words(tier_3_report)
            },
            has_negative_reviews=components.negative_review_analysis is not None,
            has_comparables=bool(components.comparable_games),
            revenue_tier=revenue_tier,
            revenue_reality_check=reality_warning,
            score_caps=score_caps,
            was_capped=was_capped,
            original_score=calculated_score if was_capped else None,
            cap_explanation=cap_result.get('cap_explanation') if was_capped else None
        )

        logger.info(f"Report generation complete - T1: {metadata.word_count['tier_1']} words, "
                   f"T2: {metadata.word_count['tier_2']} words, "
                   f"T3: {metadata.word_count['tier_3']} words")

        # Get API status summary
        api_status = self.api_verifier.get_summary_dict()
        logger.info(f"API Status: {api_status['successful']}/{api_status['total_calls']} successful")

        return {
            'tier_1_executive': tier_1_report,
            'tier_2_strategic': tier_2_report,
            'tier_3_deepdive': tier_3_report,
            'metadata': metadata,
            'components': components,
            'api_status': api_status
        }

    def _calculate_overall_score(self, game_data: Dict[str, Any]) -> float:
        """
        Calculate overall performance score (0-100).

        Formula: (review_percentage * 0.7) + owner_bonus
        - Owner bonus: 15 for 100K+, 10 for 50K-100K, 5 for 10K-50K
        """
        review_percentage = game_data.get('review_score', 0)
        review_count = game_data.get('review_count', 0)
        owners = game_data.get('owners', 0)

        # Base score from reviews (70% weight)
        base_score = review_percentage * 0.7

        # Owner bonus (30% weight max)
        owner_bonus = 0
        if owners >= 100000:
            owner_bonus = 15
        elif owners >= 50000:
            owner_bonus = 10
        elif owners >= 10000:
            owner_bonus = 5

        # Penalty for low review count (lack of validation)
        review_penalty = 0
        if review_count < 50:
            review_penalty = 5
        elif review_count < 100:
            review_penalty = 2

        overall_score = base_score + owner_bonus - review_penalty
        return min(100, max(0, overall_score))

    def _determine_tier(self, score: float) -> int:
        """
        Determine performance tier based on overall score.

        Returns:
            1: Crisis (0-40)
            2: Struggling (41-65)
            3: Solid (66-80)
            4: Exceptional (81-100)
        """
        if score >= 81:
            return 4  # Exceptional
        elif score >= 66:
            return 3  # Solid
        elif score >= 41:
            return 2  # Struggling
        else:
            return 1  # Crisis

    def _get_tier_name(self, tier: int) -> str:
        """Get human-readable tier name"""
        tier_names = {
            1: "Crisis",
            2: "Struggling",
            3: "Solid",
            4: "Exceptional"
        }
        return tier_names.get(tier, "Unknown")

    def _generate_all_components(
        self,
        game_data: Dict[str, Any],
        tier: int,
        score: float
    ) -> ReportComponents:
        """
        Generate all report components based on tier.

        All tiers get:
        - Executive summary
        - Confidence scorecard
        - Quick start
        - Key metrics dashboard
        - Market positioning
        - Comparable games
        - Revenue performance
        - Strategic recommendations
        - 30-day action plan

        Tiers 1-2 (Crisis/Struggling) also get:
        - Negative review analysis
        - Salvageability assessment

        Tiers 3-4 (Solid/Exceptional) also get:
        - Market expansion strategies
        - DLC viability analysis
        - Detailed competitive analysis
        - Regional breakdowns
        - Store optimization
        """
        logger.info("Generating report components...")

        # Universal components (all tiers)
        exec_summary = self._generate_executive_summary(game_data, tier, score)
        confidence_scorecard = self._generate_confidence_scorecard(game_data)
        quick_start = self._generate_quick_start(game_data, tier)
        key_metrics = self._generate_key_metrics_dashboard(game_data, score)
        market_positioning = self._generate_market_positioning(game_data, tier)
        comparable_games = self._generate_comparable_games(game_data)
        revenue_performance = self._generate_revenue_performance(game_data)
        strategic_recs = self._generate_strategic_recommendations(game_data, tier)
        action_plan = self._generate_action_plan_with_roi(game_data, tier)

        # Tier-specific components
        negative_review_analysis = None
        salvageability_assessment = None
        market_expansion = None
        dlc_analysis = None
        detailed_competitive = None
        regional_breakdowns = None
        store_optimization = None

        # Crisis/Struggling tiers: Focus on fixing problems
        if tier <= 2:
            review_score = game_data.get('review_score', 100)
            if review_score < 80:
                logger.info("Generating negative review analysis (struggling game)")
                negative_review_analysis = self._generate_negative_review_analysis(game_data)
                salvageability_assessment = self._generate_salvageability_assessment(
                    game_data, negative_review_analysis
                )

        # Solid/Exceptional tiers: Focus on growth
        if tier >= 3:
            logger.info("Generating growth components (solid/exceptional game)")
            market_expansion = self._generate_market_expansion(game_data)
            dlc_analysis = self._generate_dlc_analysis(game_data)
            detailed_competitive = self._generate_detailed_competitive(game_data)
            regional_breakdowns = self._generate_regional_breakdowns(game_data)
            store_optimization = self._generate_store_optimization(game_data)

        # Methodology (always included in Tier 3)
        methodology = self._generate_methodology()

        return ReportComponents(
            executive_summary=exec_summary,
            confidence_scorecard=confidence_scorecard,
            quick_start=quick_start,
            key_metrics_dashboard=key_metrics,
            market_positioning=market_positioning,
            comparable_games=comparable_games,
            revenue_performance=revenue_performance,
            strategic_recommendations=strategic_recs,
            action_plan_30_day=action_plan,
            negative_review_analysis=negative_review_analysis,
            salvageability_assessment=salvageability_assessment,
            market_expansion=market_expansion,
            dlc_analysis=dlc_analysis,
            detailed_competitive=detailed_competitive,
            regional_breakdowns=regional_breakdowns,
            store_optimization=store_optimization,
            methodology=methodology
        )

    def _assemble_executive_brief(
        self,
        components: ReportComponents,
        game_data: Dict[str, Any],
        tier: int,
        reality_warning: Optional[str] = None,
        cap_explanation: Optional[str] = None
    ) -> str:
        """
        Assemble Tier 1 Executive Brief (2-3 pages).

        Contents:
        1. Revenue Reality Check Warning (if applicable)
        2. Score Cap Explanation (always shown)
        3. Executive Summary
        4. Data Confidence Scorecard
        5. Quick Start (Top 3 Actions)
        6. Key Metrics Dashboard
        7. [Tier-specific critical section]
        """
        report = self._generate_report_header(game_data, tier, "Executive Brief")

        # CRITICAL: Add revenue reality check warning FIRST if applicable
        if reality_warning:
            report += "\n\n" + reality_warning + "\n\n---"

        # Add score cap explanation (always shown)
        if cap_explanation:
            report += "\n\n" + cap_explanation + "\n\n---"

        report += "\n\n" + components.executive_summary
        report += "\n\n" + components.confidence_scorecard
        report += "\n\n" + components.quick_start
        report += "\n\n" + components.key_metrics_dashboard

        # Add tier-specific critical section
        if tier <= 2 and components.salvageability_assessment:
            report += "\n\n## Critical Assessment\n\n"
            report += components.salvageability_assessment
        elif tier >= 3:
            report += "\n\n## Growth Opportunity Summary\n\n"
            report += self._generate_growth_summary(game_data)

        report += self._generate_report_footer("executive")

        return report

    def _assemble_strategic_overview(
        self,
        components: ReportComponents,
        game_data: Dict[str, Any],
        tier: int,
        reality_warning: Optional[str] = None,
        cap_explanation: Optional[str] = None
    ) -> str:
        """
        Assemble Tier 2 Strategic Overview (8-12 pages).

        Contents:
        - All of Tier 1 (with reality warning and cap explanation if applicable)
        - Market Positioning Analysis
        - Comparable Games Comparison
        - Revenue Performance
        - Strategic Recommendations
        - 30-Day Action Plan (with ROI)
        - [Tier-specific sections]
        """
        # Start with executive brief (pass reality warning and cap explanation)
        report = self._assemble_executive_brief(components, game_data, tier, reality_warning, cap_explanation)

        # Add strategic sections
        report += "\n\n---\n\n# Strategic Analysis\n\n"
        report += components.market_positioning
        report += "\n\n" + components.comparable_games
        report += "\n\n" + components.revenue_performance
        report += "\n\n" + components.strategic_recommendations
        report += "\n\n" + components.action_plan_30_day

        # Add tier-specific deep sections
        if tier <= 2 and components.negative_review_analysis:
            report += "\n\n## Negative Review Analysis\n\n"
            report += components.negative_review_analysis

        if tier >= 3 and components.market_expansion:
            report += "\n\n## Market Expansion Opportunities\n\n"
            report += components.market_expansion

        report += self._generate_report_footer("strategic")

        return report

    def _assemble_full_report(
        self,
        components: ReportComponents,
        game_data: Dict[str, Any],
        tier: int,
        reality_warning: Optional[str] = None,
        cap_explanation: Optional[str] = None
    ) -> str:
        """
        Assemble Tier 3 Deep-dive Report (30-40 pages).

        Contents:
        - All of Tier 1 & 2 (with reality warning and cap explanation if applicable)
        - Detailed Competitive Analysis
        - Regional Market Breakdowns
        - Store Asset Optimization
        - DLC Analysis (if tier 3-4)
        - Complete Methodology
        - Appendices
        """
        # Start with strategic overview (pass reality warning and cap explanation)
        report = self._assemble_strategic_overview(components, game_data, tier, reality_warning, cap_explanation)

        # Add deep-dive sections
        report += "\n\n---\n\n# Deep-Dive Analysis\n\n"

        if components.detailed_competitive:
            report += "\n\n" + components.detailed_competitive

        if components.regional_breakdowns:
            report += "\n\n" + components.regional_breakdowns

        if components.store_optimization:
            report += "\n\n" + components.store_optimization

        if components.dlc_analysis:
            report += "\n\n" + components.dlc_analysis

        # Always include methodology in full report
        report += "\n\n---\n\n# Methodology\n\n"
        report += components.methodology

        # Add appendices
        report += "\n\n---\n\n# Appendices\n\n"
        report += self._generate_appendices(game_data)

        report += self._generate_report_footer("deepdive")

        return report

    # ========================================================================
    # COMPONENT GENERATION METHODS
    # ========================================================================

    def _generate_executive_summary(
        self,
        game_data: Dict[str, Any],
        tier: int,
        score: float
    ) -> str:
        """Generate executive summary using function-based generator"""
        try:
            # Determine review velocity trend (simplified)
            review_velocity = "stable"  # Could be enhanced with historical data

            # Call the function-based executive summary generator
            summary = generate_executive_summary(
                overall_score=score,
                review_count=game_data.get('review_count', 0),
                review_percentage=game_data.get('review_score', 0),
                revenue_estimate=game_data.get('revenue', 0),
                review_velocity_trend=review_velocity,
                genre=game_data.get('genres', ['Unknown'])[0] if game_data.get('genres') else 'Unknown'
            )
            return summary
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return "# Executive Summary\n\n*Summary generation failed*"

    def _generate_confidence_scorecard(self, game_data: Dict[str, Any]) -> str:
        """Generate data confidence scorecard"""
        md = "## Data Confidence Scorecard\n\n"
        md += "*How reliable is this analysis?*\n\n"
        md += "| Data Source | Confidence | Notes |\n"
        md += "|-------------|------------|-------|\n"

        # Steam review data
        review_count = game_data.get('review_count', 0)
        if review_count >= 500:
            md += "| Steam Reviews | ✅ High | Large sample size ({:,} reviews) |\n".format(review_count)
        elif review_count >= 100:
            md += "| Steam Reviews | ⚠️ Medium | Moderate sample ({:,} reviews) |\n".format(review_count)
        else:
            md += "| Steam Reviews | ❌ Low | Small sample ({:,} reviews) |\n".format(review_count)

        # Sales data
        owners = game_data.get('owners', 0)
        if owners >= 10000:
            md += "| Sales Data | ✅ High | SteamSpy estimates (10K+ owners) |\n"
        elif owners >= 1000:
            md += "| Sales Data | ⚠️ Medium | SteamSpy estimates (1K-10K owners) |\n"
        else:
            md += "| Sales Data | ❌ Low | Limited data (<1K owners) |\n"

        # Market data
        has_sales_data = game_data.get('sales_data') is not None
        if has_sales_data:
            md += "| Market Analysis | ✅ High | Real sales data available |\n"
        else:
            md += "| Market Analysis | ⚠️ Medium | Based on public data only |\n"

        # Competitive analysis
        has_genre = bool(game_data.get('genres'))
        if has_genre:
            md += "| Competitive Data | ✅ High | Genre benchmarks available |\n"
        else:
            md += "| Competitive Data | ⚠️ Medium | Limited genre data |\n"

        return md

    def _generate_quick_start(self, game_data: Dict[str, Any], tier: int) -> str:
        """Generate Quick Start section with top 3 actions"""
        md = "## Quick Start: Top 3 Actions\n\n"
        md += "*Start here if you only have 30 minutes.*\n\n"

        # Generate top ROI actions
        actions = self._get_top_actions_for_tier(game_data, tier)

        for i, action in enumerate(actions[:3], 1):
            md += f"### {i}. {action['name']}\n\n"
            md += f"**Investment**: {action['time']} hours, ${action['cost']:,.0f}\n\n"
            md += f"**Expected Return**: ${action['revenue_min']:,.0f} - ${action['revenue_max']:,.0f}\n\n"
            md += f"**ROI**: {action['roi']:.1f}x | **Payback**: {action['payback']} | **Confidence**: {action['confidence']}\n\n"
            md += f"**What to do**: {action['description']}\n\n"

        return md

    def _generate_key_metrics_dashboard(self, game_data: Dict[str, Any], score: float) -> str:
        """Generate key metrics dashboard"""
        md = "## Key Metrics Dashboard\n\n"

        review_score = game_data.get('review_score', 0)
        review_count = game_data.get('review_count', 0)
        owners = game_data.get('owners', 0)
        revenue = game_data.get('revenue', 0)
        price = game_data.get('price', 0)

        md += "| Metric | Value | Benchmark |\n"
        md += "|--------|-------|----------|\n"
        md += f"| Overall Score | **{score:.0f}/100** | {self._get_score_benchmark(score)} |\n"
        md += f"| Review Score | {review_score:.0f}% | {self._get_review_benchmark(review_score)} |\n"
        md += f"| Review Count | {review_count:,} | {self._get_review_count_benchmark(review_count)} |\n"
        md += f"| Estimated Owners | {owners:,} | {self._get_owner_benchmark(owners)} |\n"
        md += f"| Estimated Revenue | ${revenue:,.0f} | {self._get_revenue_benchmark(revenue)} |\n"
        md += f"| Current Price | ${price:.2f} | {self._get_price_benchmark(price)} |\n"

        return md

    def _generate_market_positioning(self, game_data: Dict[str, Any], tier: int) -> str:
        """Generate market positioning analysis"""
        md = "## Market Positioning Analysis\n\n"

        review_score = game_data.get('review_score', 0)
        owners = game_data.get('owners', 0)

        md += "### Where You Stand\n\n"

        if review_score >= 90:
            md += "**Quality Position**: Top tier (90%+ positive reviews)\n\n"
            md += "Your game is loved by players. This is your strongest asset.\n\n"
        elif review_score >= 80:
            md += "**Quality Position**: Strong (80-90% positive reviews)\n\n"
            md += "Your game is well-received. Room for minor improvements.\n\n"
        elif review_score >= 70:
            md += "**Quality Position**: Acceptable (70-80% positive reviews)\n\n"
            md += "Your game is mixed. Significant improvements needed.\n\n"
        else:
            md += "**Quality Position**: Crisis (<70% positive reviews)\n\n"
            md += "Your game has serious issues that need immediate attention.\n\n"

        if owners >= 100000:
            md += "**Market Reach**: Excellent (100K+ owners)\n\n"
            md += "You've achieved significant market penetration.\n\n"
        elif owners >= 50000:
            md += "**Market Reach**: Good (50K-100K owners)\n\n"
            md += "Solid reach with room to grow.\n\n"
        elif owners >= 10000:
            md += "**Market Reach**: Moderate (10K-50K owners)\n\n"
            md += "Growing but needs stronger marketing.\n\n"
        else:
            md += "**Market Reach**: Limited (<10K owners)\n\n"
            md += "Visibility is your primary challenge.\n\n"

        return md

    def _generate_comparable_games(self, game_data: Dict[str, Any]) -> str:
        """Generate comparable games analysis"""
        try:
            # Use the comparable games analyzer
            app_id = str(game_data.get('app_id', ''))
            genres = game_data.get('genres', [])
            price = game_data.get('price', 0)
            release_date = game_data.get('release_date', '')
            owners = game_data.get('owners', 0)

            if not app_id or not genres:
                self.api_verifier.record_skipped(
                    "Comparable Games API",
                    "Steam search",
                    "Insufficient data (missing app_id or genres)"
                )
                return "## Comparable Games\n\n*Insufficient data for comparison*"

            # Track API call attempt
            try:
                comparable_games = self.comparable_analyzer.find_comparable_games(
                    target_game_id=app_id,
                    genre_tags=genres,
                    price=price,
                    launch_date=release_date,
                    owner_count=owners,
                    limit=10
                )

                if comparable_games:
                    self.api_verifier.record_success(
                        "Comparable Games API",
                        "Steam search & filtering"
                    )
                else:
                    self.api_verifier.record_failure(
                        "Comparable Games API",
                        "Steam search",
                        "No comparable games found in database"
                    )
            except Exception as api_error:
                self.api_verifier.record_failure(
                    "Comparable Games API",
                    "Steam search",
                    str(api_error)
                )
                comparable_games = []

            if not comparable_games:
                return "## Comparable Games\n\n*No comparable games found*"

            # Generate comparison table
            md = "## How You Compare to Similar Games\n\n"
            md += f"### Games Like Yours ({genres[0] if genres else 'Unknown'}, ${price:.2f}, Similar Launch)\n\n"
            md += "| Game | Score | Reviews | Est. Revenue | What They Did Right |\n"
            md += "|------|-------|---------|--------------|---------------------|\n"

            # Add target game
            target_score = self._calculate_overall_score(game_data)
            md += f"| **{game_data.get('name', 'Your Game')}** | **{target_score:.0f}/100** | "
            md += f"**{game_data.get('review_count', 0):,} ({game_data.get('review_score', 0):.0f}%)** | "
            md += f"**${game_data.get('revenue', 0):,.0f}** | Your baseline |\n"

            # Add comparable games
            for game in comparable_games[:7]:
                md += f"| {game.name} | {game.overall_score:.0f}/100 | "
                md += f"{game.review_count:,} ({game.review_percentage:.0f}%) | "
                md += f"{game.revenue_display} | "

                if game.overall_score > target_score + 10:
                    md += "Superior quality/execution |\n"
                elif game.overall_score > target_score:
                    md += "Better overall performance |\n"
                elif game.overall_score > target_score - 10:
                    md += "Similar trajectory |\n"
                else:
                    md += "Lower performance |\n"

            return md

        except Exception as e:
            logger.error(f"Error generating comparable games: {e}")
            return "## Comparable Games\n\n*Analysis unavailable*"

    def _generate_revenue_performance(self, game_data: Dict[str, Any]) -> str:
        """Generate revenue performance analysis"""
        md = "## Revenue Performance\n\n"

        revenue = game_data.get('revenue', 0)
        owners = game_data.get('owners', 0)
        price = game_data.get('price', 0)

        md += f"**Estimated Total Revenue**: ${revenue:,.0f}\n\n"
        md += f"**Est. Units Sold**: {owners:,}\n\n"
        md += f"**Average Price Point**: ${price:.2f}\n\n"

        # Revenue per owner (efficiency metric)
        if owners > 0:
            revenue_per_owner = revenue / owners
            md += f"**Revenue per Owner**: ${revenue_per_owner:.2f}\n\n"

            if revenue_per_owner >= price * 0.8:
                md += "✅ Strong monetization - most owners bought at full price\n\n"
            elif revenue_per_owner >= price * 0.5:
                md += "⚠️ Moderate monetization - significant discount sales\n\n"
            else:
                md += "❌ Weak monetization - heavy discounting or low conversion\n\n"

        return md

    def _generate_strategic_recommendations(self, game_data: Dict[str, Any], tier: int) -> str:
        """Generate strategic recommendations based on tier"""
        md = "## Strategic Recommendations\n\n"

        if tier == 1:  # Crisis
            md += "### Critical Priority: Stop the Bleeding\n\n"
            md += "1. **Fix Critical Bugs** - Review negative reviews and fix game-breaking issues\n\n"
            md += "2. **Communication Plan** - Acknowledge issues publicly and commit to fixes\n\n"
            md += "3. **Assess Salvageability** - Determine if recovery is viable\n\n"

        elif tier == 2:  # Struggling
            md += "### Primary Focus: Quality Improvement\n\n"
            md += "1. **Address Top Complaints** - Fix the most common negative review issues\n\n"
            md += "2. **Build Community Trust** - Engage with players and show commitment\n\n"
            md += "3. **Quick Wins** - Implement high-ROI, low-effort improvements\n\n"

        elif tier == 3:  # Solid
            md += "### Growth Strategy: Optimize and Expand\n\n"
            md += "1. **Market Expansion** - Regional pricing, new platforms, localization\n\n"
            md += "2. **Content Updates** - Keep existing players engaged\n\n"
            md += "3. **Visibility Campaigns** - Influencer partnerships, marketing pushes\n\n"

        else:  # Exceptional
            md += "### Scaling Strategy: Maximize Success\n\n"
            md += "1. **DLC Development** - Capitalize on strong player base\n\n"
            md += "2. **Global Expansion** - Full localization for major markets\n\n"
            md += "3. **Brand Building** - Sequels, merchandise, community events\n\n"

        return md

    def _generate_action_plan_with_roi(self, game_data: Dict[str, Any], tier: int) -> str:
        """Generate 30-day action plan with ROI calculations"""
        md = "## 30-Day Action Plan with ROI\n\n"
        md += "*Prioritized by ROI and quick wins*\n\n"

        # Get tier-appropriate actions
        actions = self._get_top_actions_for_tier(game_data, tier, limit=7)

        # Generate ROI calculations
        roi_calcs = []
        for action in actions:
            if action['type'] == 'regional_pricing':
                calc = self.roi_calculator.calculate_regional_pricing_roi(
                    current_revenue=game_data.get('revenue', 0) / 12,  # Monthly
                    current_regions=1
                )
            elif action['type'] == 'price_reduction':
                calc = self.roi_calculator.calculate_price_reduction_roi(
                    current_price=game_data.get('price', 19.99),
                    current_revenue=game_data.get('revenue', 0) / 12,
                    current_units_sold=game_data.get('owners', 0) // 12,
                    price_reduction_percent=20
                )
            elif action['type'] == 'bug_fix':
                calc = self.roi_calculator.calculate_bug_fix_roi(
                    current_revenue=game_data.get('revenue', 0) / 12,
                    current_review_score=game_data.get('review_score', 70),
                    bug_severity='critical' if tier <= 2 else 'moderate'
                )
            elif action['type'] == 'influencer':
                calc = self.roi_calculator.calculate_influencer_campaign_roi(
                    current_revenue=game_data.get('revenue', 0) / 12,
                    influencer_tier='micro',
                    num_influencers=5
                )
            else:
                continue

            roi_calcs.append(calc)

        # Generate comparison table
        if roi_calcs:
            md += self.roi_calculator.generate_roi_table(roi_calcs)

        return md

    def _generate_negative_review_analysis(self, game_data: Dict[str, Any]) -> str:
        """Generate negative review analysis"""
        try:
            app_id = str(game_data.get('app_id', ''))
            game_name = game_data.get('name', 'Unknown')

            if not app_id:
                self.api_verifier.record_skipped(
                    "Steam Reviews API",
                    "/appreviews (negative filtering)",
                    "Missing app_id"
                )
                return "*Negative review analysis unavailable*"

            if not self.negative_analyzer:
                self.api_verifier.record_not_configured(
                    "Claude API",
                    "Messages endpoint (review analysis)"
                )
                return "*Claude API not configured - negative review analysis unavailable*"

            # Track Steam API call for fetching reviews
            try:
                reviews = self.negative_analyzer.fetch_negative_reviews(app_id, count=100)

                if reviews:
                    self.api_verifier.record_success(
                        "Steam Reviews API",
                        f"/appreviews/{app_id} (negative filtering)"
                    )
                else:
                    self.api_verifier.record_failure(
                        "Steam Reviews API",
                        f"/appreviews/{app_id}",
                        "No negative reviews found"
                    )
                    return "*No negative reviews found*"

            except Exception as api_error:
                self.api_verifier.record_failure(
                    "Steam Reviews API",
                    f"/appreviews/{app_id}",
                    str(api_error)
                )
                return "*Failed to fetch negative reviews*"

            # Track Claude API call for categorization
            try:
                categorization = self.negative_analyzer.categorize_complaints(reviews, game_name)

                self.api_verifier.record_success(
                    "Claude API",
                    "Messages endpoint (complaint categorization)"
                )

                # Generate report
                report = self.negative_analyzer.generate_negative_review_report(
                    categorization, game_name
                )

                return report

            except Exception as claude_error:
                self.api_verifier.record_failure(
                    "Claude API",
                    "Messages endpoint",
                    str(claude_error)
                )
                return "*Claude API failed - could not categorize complaints*"

        except Exception as e:
            logger.error(f"Error analyzing negative reviews: {e}")
            return "*Negative review analysis failed*"

    def _generate_salvageability_assessment(
        self,
        game_data: Dict[str, Any],
        negative_analysis: Optional[str]
    ) -> str:
        """Generate salvageability assessment for struggling games"""
        try:
            if not negative_analysis or negative_analysis.startswith("*"):
                return "*Salvageability assessment unavailable*"

            if not self.negative_analyzer:
                self.api_verifier.record_not_configured(
                    "Claude API",
                    "Messages endpoint (salvageability)"
                )
                return "*Claude API not configured - salvageability assessment unavailable*"

            app_id = str(game_data.get('app_id', ''))
            game_name = game_data.get('name', 'Unknown')
            review_score = game_data.get('review_score', 0)

            # Fetch negative reviews again (could cache this)
            # Note: This is already tracked in _generate_negative_review_analysis
            reviews = self.negative_analyzer.fetch_negative_reviews(app_id, count=100)
            categorization = self.negative_analyzer.categorize_complaints(reviews, game_name)

            # Track Claude API call for salvageability assessment
            try:
                assessment = self.negative_analyzer.assess_salvageability(
                    categorization, review_score, game_name
                )

                self.api_verifier.record_success(
                    "Claude API",
                    "Messages endpoint (salvageability assessment)"
                )

                return assessment

            except Exception as claude_error:
                self.api_verifier.record_failure(
                    "Claude API",
                    "Messages endpoint (salvageability)",
                    str(claude_error)
                )
                return "*Claude API failed - could not assess salvageability*"

        except Exception as e:
            logger.error(f"Error generating salvageability assessment: {e}")
            return "*Salvageability assessment failed*"

    def _generate_market_expansion(self, game_data: Dict[str, Any]) -> str:
        """Generate market expansion strategies"""
        md = "### Market Expansion Opportunities\n\n"

        md += "**Regional Pricing**\n"
        md += "- Add pricing for: Brazil, Russia, China, India, Argentina\n"
        md += "- Expected lift: +15-25% revenue\n"
        md += "- Investment: 12 hours, minimal cost\n\n"

        md += "**Platform Expansion**\n"
        md += "- Consider: Epic Games Store, GOG, itch.io\n"
        md += "- Expected lift: +10-20% revenue\n"
        md += "- Investment: 20-40 hours per platform\n\n"

        md += "**Localization**\n"
        md += "- Priority languages: Chinese (Simplified), Japanese, German, French, Spanish\n"
        md += "- Expected lift: +20-40% revenue\n"
        md += "- Investment: $2K-5K per language\n\n"

        return md

    def _generate_dlc_analysis(self, game_data: Dict[str, Any]) -> str:
        """Generate DLC viability analysis"""
        md = "## DLC Viability Analysis\n\n"

        owners = game_data.get('owners', 0)
        review_score = game_data.get('review_score', 0)

        if review_score >= 85 and owners >= 50000:
            md += "✅ **Strong DLC Candidate**\n\n"
            md += f"With {owners:,} owners and {review_score:.0f}% positive reviews, "
            md += "your player base is engaged and willing to pay for more content.\n\n"

            md += "**DLC Recommendations**:\n"
            md += "- Story expansion: 20-30% attach rate expected\n"
            md += "- Cosmetic pack: 10-15% attach rate\n"
            md += "- Major content update: 25-40% attach rate\n\n"

            md += f"**Expected Revenue**: ${int(owners * 0.25 * 9.99):,} - ${int(owners * 0.4 * 14.99):,}\n\n"

        elif review_score >= 80:
            md += "⚠️ **Moderate DLC Potential**\n\n"
            md += "Your game has a positive reception, but may need more content depth before DLC.\n\n"

        else:
            md += "❌ **Not Recommended for DLC**\n\n"
            md += "Focus on improving the base game before considering DLC.\n\n"

        return md

    def _generate_detailed_competitive(self, game_data: Dict[str, Any]) -> str:
        """Generate detailed competitive analysis"""
        md = "## Detailed Competitive Analysis\n\n"
        md += "*Coming soon - detailed competitor breakdowns*\n\n"
        return md

    def _generate_regional_breakdowns(self, game_data: Dict[str, Any]) -> str:
        """Generate regional market breakdowns"""
        md = "## Regional Market Analysis\n\n"
        md += "*Coming soon - region-specific performance data*\n\n"
        return md

    def _generate_store_optimization(self, game_data: Dict[str, Any]) -> str:
        """Generate store page optimization recommendations"""
        md = "## Store Page Optimization\n\n"

        md += "### Key Areas to Review\n\n"
        md += "1. **Description**: Clear value proposition in first 2 sentences?\n"
        md += "2. **Screenshots**: Do they showcase core gameplay?\n"
        md += "3. **Trailer**: Hook in first 10 seconds?\n"
        md += "4. **Tags**: All relevant tags added?\n"
        md += "5. **Pricing**: Competitive for genre?\n\n"

        return md

    def _generate_methodology(self) -> str:
        """Generate methodology section"""
        md = "## Report Methodology\n\n"

        md += "### Data Sources\n\n"
        md += "- **Steam API**: Official review counts, scores, and metadata\n"
        md += "- **SteamSpy**: Owner estimates and demographic data\n"
        md += "- **Market Analysis**: Comparable games and competitive benchmarks\n"
        md += "- **ROI Calculations**: Industry benchmarks and historical data\n\n"

        md += "### Scoring System\n\n"
        md += "**Overall Score Formula**: `(review_percentage × 0.7) + owner_bonus - review_penalty`\n\n"
        md += "- Review percentage: 70% weight\n"
        md += "- Owner bonus: 15 (100K+), 10 (50K-100K), 5 (10K-50K)\n"
        md += "- Review penalty: 5 (<50 reviews), 2 (<100 reviews)\n\n"

        md += "### Performance Tiers\n\n"
        md += "- **Tier 4 (Exceptional)**: 81-100 points\n"
        md += "- **Tier 3 (Solid)**: 66-80 points\n"
        md += "- **Tier 2 (Struggling)**: 41-65 points\n"
        md += "- **Tier 1 (Crisis)**: 0-40 points\n\n"

        md += "### Confidence Levels\n\n"
        md += "- **High (>75%)**: Large sample sizes, proven strategies\n"
        md += "- **Medium (50-75%)**: Moderate data, reasonable estimates\n"
        md += "- **Low (<50%)**: Limited data, speculative estimates\n\n"

        return md

    def _generate_appendices(self, game_data: Dict[str, Any]) -> str:
        """Generate appendices"""
        md = "## Appendix A: Game Data Summary\n\n"

        md += f"**App ID**: {game_data.get('app_id', 'Unknown')}\n"
        md += f"**Name**: {game_data.get('name', 'Unknown')}\n"
        md += f"**Price**: ${game_data.get('price', 0):.2f}\n"
        md += f"**Release Date**: {game_data.get('release_date', 'Unknown')}\n"
        md += f"**Genres**: {', '.join(game_data.get('genres', ['Unknown']))}\n"
        md += f"**Owners**: {game_data.get('owners', 0):,}\n"
        md += f"**Reviews**: {game_data.get('review_count', 0):,} ({game_data.get('review_score', 0):.0f}% positive)\n"
        md += f"**Revenue**: ${game_data.get('revenue', 0):,}\n\n"

        return md

    def _generate_growth_summary(self, game_data: Dict[str, Any]) -> str:
        """Generate growth opportunity summary for solid/exceptional games"""
        md = f"Your game is performing well with {game_data.get('review_score', 0):.0f}% positive reviews "
        md += f"and {game_data.get('owners', 0):,} owners. Focus on scaling and maximizing this success.\n\n"

        md += "**Top Growth Opportunities**:\n"
        md += "1. Regional pricing expansion (+15-25% revenue)\n"
        md += "2. DLC development (+30-50% revenue)\n"
        md += "3. Influencer partnerships (+10-40% revenue)\n"

        return md

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _get_top_actions_for_tier(
        self,
        game_data: Dict[str, Any],
        tier: int,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Get top recommended actions for a given tier"""
        actions = []

        if tier == 1:  # Crisis
            actions = [
                {
                    'type': 'bug_fix',
                    'name': 'Fix Critical Bugs',
                    'time': 64,
                    'cost': 3200,
                    'revenue_min': 500,
                    'revenue_max': 1500,
                    'roi': 0.3,
                    'payback': '8-12 weeks',
                    'confidence': '✅ High',
                    'description': 'Review negative reviews, identify top 3 game-breaking bugs, and fix them'
                },
                {
                    'type': 'communication',
                    'name': 'Community Communication Plan',
                    'time': 4,
                    'cost': 0,
                    'revenue_min': 200,
                    'revenue_max': 800,
                    'roi': 1.5,
                    'payback': '4-6 weeks',
                    'confidence': '⚠️ Medium',
                    'description': 'Post public acknowledgment of issues and commit to fixes'
                },
                {
                    'type': 'salvage_assessment',
                    'name': 'Assess Salvageability',
                    'time': 2,
                    'cost': 0,
                    'revenue_min': 0,
                    'revenue_max': 0,
                    'roi': 0,
                    'payback': 'N/A',
                    'confidence': '✅ High',
                    'description': 'Determine if game can be saved or should be pivoted/abandoned'
                }
            ]

        elif tier == 2:  # Struggling
            actions = [
                {
                    'type': 'bug_fix',
                    'name': 'Address Top Complaints',
                    'time': 28,
                    'cost': 1400,
                    'revenue_min': 800,
                    'revenue_max': 2000,
                    'roi': 0.8,
                    'payback': '6-8 weeks',
                    'confidence': '✅ High',
                    'description': 'Fix moderate bugs and issues mentioned in negative reviews'
                },
                {
                    'type': 'price_reduction',
                    'name': 'Price Optimization Test',
                    'time': 2,
                    'cost': 100,
                    'revenue_min': 300,
                    'revenue_max': 1200,
                    'roi': 4.0,
                    'payback': '1-2 weeks',
                    'confidence': '⚠️ Medium',
                    'description': 'Test 15-20% price reduction to boost sales volume'
                },
                {
                    'type': 'regional_pricing',
                    'name': 'Regional Pricing',
                    'time': 12,
                    'cost': 600,
                    'revenue_min': 1000,
                    'revenue_max': 3000,
                    'roi': 2.5,
                    'payback': '2-4 weeks',
                    'confidence': '✅ High',
                    'description': 'Add regional pricing for Brazil, Russia, China, India'
                }
            ]

        elif tier == 3:  # Solid
            actions = [
                {
                    'type': 'influencer',
                    'name': 'Micro-Influencer Campaign',
                    'time': 9,
                    'cost': 1188,
                    'revenue_min': 12000,
                    'revenue_max': 50000,
                    'roi': 21.0,
                    'payback': '0-2 weeks',
                    'confidence': '⚠️ Medium',
                    'description': 'Partner with 5 micro-tier influencers for sponsored content'
                },
                {
                    'type': 'regional_pricing',
                    'name': 'Regional Pricing',
                    'time': 12,
                    'cost': 600,
                    'revenue_min': 2000,
                    'revenue_max': 5000,
                    'roi': 4.2,
                    'payback': '1-2 weeks',
                    'confidence': '✅ High',
                    'description': 'Expand to 8+ regional pricing tiers'
                },
                {
                    'type': 'content_update',
                    'name': 'Minor Content Update',
                    'time': 52,
                    'cost': 3300,
                    'revenue_min': 3000,
                    'revenue_max': 8000,
                    'roi': 1.2,
                    'payback': '4-6 weeks',
                    'confidence': '⚠️ Medium',
                    'description': 'Add new features or content to re-engage players'
                }
            ]

        else:  # Exceptional
            actions = [
                {
                    'type': 'influencer',
                    'name': 'Mid-Tier Influencer Campaign',
                    'time': 6,
                    'cost': 2550,
                    'revenue_min': 25000,
                    'revenue_max': 75000,
                    'roi': 19.0,
                    'payback': '0-1 weeks',
                    'confidence': '⚠️ Medium',
                    'description': 'Partner with 3 mid-tier influencers with 50K+ audiences'
                },
                {
                    'type': 'dlc',
                    'name': 'DLC Development',
                    'time': 252,
                    'cost': 18600,
                    'revenue_min': 30000,
                    'revenue_max': 100000,
                    'roi': 3.4,
                    'payback': '8-12 weeks',
                    'confidence': '✅ High',
                    'description': 'Develop paid DLC for existing player base'
                },
                {
                    'type': 'localization',
                    'name': 'Full Localization',
                    'time': 40,
                    'cost': 12000,
                    'revenue_min': 20000,
                    'revenue_max': 60000,
                    'roi': 2.8,
                    'payback': '6-10 weeks',
                    'confidence': '✅ High',
                    'description': 'Localize to Chinese, Japanese, German, French, Spanish'
                }
            ]

        return actions[:limit]

    def _calculate_report_confidence(self, components: ReportComponents) -> str:
        """Calculate overall confidence level for the report"""
        # Simplified confidence calculation
        # In production, would analyze data quality across all components
        return "High"

    def _count_words(self, text: str) -> int:
        """Count words in text"""
        # Remove markdown formatting
        clean_text = re.sub(r'[#*`_\[\](){}]', '', text)
        words = clean_text.split()
        return len(words)

    def _generate_report_header(self, game_data: Dict[str, Any], tier: int, report_type: str) -> str:
        """Generate report header"""
        tier_name = self._get_tier_name(tier)

        header = f"# Game Audit Report: {game_data.get('name', 'Unknown')}\n\n"
        header += f"**Report Type**: {report_type}\n"
        header += f"**Performance Tier**: {tier} - {tier_name}\n"
        header += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        header += f"**App ID**: {game_data.get('app_id', 'Unknown')}\n\n"
        header += "---\n"

        return header

    def _generate_report_footer(self, report_type: str) -> str:
        """Generate report footer"""
        footer = "\n\n---\n\n"
        footer += "*This report was generated by Publitz Automated Game Audits*\n\n"

        if report_type == "executive":
            footer += "*For the full strategic overview, see the Tier 2 report.*\n"
        elif report_type == "strategic":
            footer += "*For the complete deep-dive analysis, see the Tier 3 report.*\n"

        return footer

    def _get_score_benchmark(self, score: float) -> str:
        """Get benchmark description for overall score"""
        if score >= 81:
            return "🏆 Top 10%"
        elif score >= 66:
            return "✅ Above Average"
        elif score >= 41:
            return "⚠️ Below Average"
        else:
            return "❌ Bottom 20%"

    def _get_review_benchmark(self, review_score: float) -> str:
        """Get benchmark for review score"""
        if review_score >= 90:
            return "🏆 Excellent"
        elif review_score >= 80:
            return "✅ Good"
        elif review_score >= 70:
            return "⚠️ Mixed"
        else:
            return "❌ Poor"

    def _get_review_count_benchmark(self, review_count: int) -> str:
        """Get benchmark for review count"""
        if review_count >= 5000:
            return "🏆 Viral"
        elif review_count >= 1000:
            return "✅ Strong"
        elif review_count >= 100:
            return "⚠️ Moderate"
        else:
            return "❌ Limited"

    def _get_owner_benchmark(self, owners: int) -> str:
        """Get benchmark for owner count"""
        if owners >= 500000:
            return "🏆 Blockbuster"
        elif owners >= 100000:
            return "✅ Hit"
        elif owners >= 10000:
            return "⚠️ Modest"
        else:
            return "❌ Niche"

    def _get_revenue_benchmark(self, revenue: int) -> str:
        """Get benchmark for revenue"""
        if revenue >= 5000000:
            return "🏆 $5M+ Club"
        elif revenue >= 1000000:
            return "✅ $1M+ Club"
        elif revenue >= 100000:
            return "⚠️ $100K+ Club"
        else:
            return "❌ <$100K"

    def _get_price_benchmark(self, price: float) -> str:
        """Get benchmark for price"""
        if price >= 30:
            return "Premium"
        elif price >= 15:
            return "Mid-tier"
        elif price >= 5:
            return "Budget"
        else:
            return "Ultra-budget"

    def _track_input_data_sources(self, game_data: Dict[str, Any]) -> None:
        """
        Track which APIs were used to fetch the input game_data.

        This records the data sources that were used before report generation.
        """
        # Check for Steam Store API data (basic game info)
        if game_data.get('name') and game_data.get('price'):
            self.api_verifier.record_success(
                "Steam Store API",
                "/api/appdetails",
                response_time_ms=None
            )
        else:
            self.api_verifier.record_failure(
                "Steam Store API",
                "/api/appdetails",
                "Game data incomplete - missing basic info"
            )

        # Check for SteamSpy data (owner counts)
        if game_data.get('owners'):
            self.api_verifier.record_success(
                "SteamSpy API",
                "/api.php?request=appdetails",
                response_time_ms=None
            )
        else:
            self.api_verifier.record_failure(
                "SteamSpy API",
                "/api.php?request=appdetails",
                "Owner count unavailable"
            )

        # Check for Steam Reviews data
        if game_data.get('review_score') and game_data.get('review_count'):
            self.api_verifier.record_success(
                "Steam Reviews API",
                f"/appreviews/{game_data.get('app_id', 'unknown')}",
                response_time_ms=None
            )
        else:
            self.api_verifier.record_failure(
                "Steam Reviews API",
                f"/appreviews/{game_data.get('app_id', 'unknown')}",
                "Review data unavailable"
            )

    def _generate_insufficient_data_report(
        self,
        game_data: Dict[str, Any],
        validation_warning: str
    ) -> Dict[str, Any]:
        """
        Generate minimal report for games with insufficient data.

        Args:
            game_data: Game data dict (incomplete)
            validation_warning: Warning message from validation system

        Returns:
            Report dict with error message
        """
        error_report = f"""# Game Audit Report: {game_data.get('name', 'Unknown')}

**Report Type**: Insufficient Data
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**App ID**: {game_data.get('app_id', 'Unknown')}

---

{validation_warning}

---

*This report was generated by Publitz Automated Game Audits*
"""

        metadata = ReportMetadata(
            overall_score=0,
            performance_tier=0,
            tier_name="Insufficient Data",
            generated_at=datetime.now(),
            game_name=game_data.get('name', 'Unknown'),
            app_id=str(game_data.get('app_id', '')),
            confidence_level="N/A",
            word_count={
                'tier_1': self._count_words(error_report),
                'tier_2': self._count_words(error_report),
                'tier_3': self._count_words(error_report)
            },
            has_negative_reviews=False,
            has_comparables=False
        )

        return {
            'tier_1_executive': error_report,
            'tier_2_strategic': error_report,
            'tier_3_deepdive': error_report,
            'metadata': metadata,
            'components': None,
            'api_status': self.api_verifier.get_summary_dict()
        }

    def _generate_data_error_report(
        self,
        game_data: Dict[str, Any],
        error_message: str
    ) -> Dict[str, Any]:
        """
        Generate error report for games with data consistency errors.

        Args:
            game_data: Game data dict with inconsistencies
            error_message: Detailed error messages from validation

        Returns:
            Report dict with error explanation
        """
        error_report = f"""# Game Audit Report: {game_data.get('name', 'Unknown')}

**Report Type**: Data Consistency Error
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**App ID**: {game_data.get('app_id', 'Unknown')}

---

## ❌ DATA CONSISTENCY ERRORS

The provided game data contains critical inconsistencies that prevent report generation:

{error_message}

**What This Means:**

The data contains contradictions (e.g., review count exceeds owner count, negative revenue,
mathematical impossibilities). These errors must be fixed at the data source before a report
can be generated.

**Next Steps:**

1. Verify data sources (Steam API, SteamSpy, etc.)
2. Check for data collection errors
3. Ensure all metrics are from the same time period
4. Re-run data collection and try again

**Common Causes:**

- Mixing data from different time periods
- API errors or rate limiting
- Manual data entry mistakes
- Cached stale data

---

*This report was generated by Publitz Automated Game Audits*
"""

        metadata = ReportMetadata(
            overall_score=0,
            performance_tier=0,
            tier_name="Data Error",
            generated_at=datetime.now(),
            game_name=game_data.get('name', 'Unknown'),
            app_id=str(game_data.get('app_id', '')),
            confidence_level="N/A",
            word_count={
                'tier_1': self._count_words(error_report),
                'tier_2': self._count_words(error_report),
                'tier_3': self._count_words(error_report)
            },
            has_negative_reviews=False,
            has_comparables=False
        )

        return {
            'tier_1_executive': error_report,
            'tier_2_strategic': error_report,
            'tier_3_deepdive': error_report,
            'metadata': metadata,
            'components': None,
            'api_status': self.api_verifier.get_summary_dict()
        }


# ========================================================================
# QUALITY VALIDATION
# ========================================================================

def validate_report(report_dict: Dict[str, Any], tier: int) -> List[str]:
    """
    Run quality checks before delivery.

    Args:
        report_dict: Complete report dict from generate_complete_report()
        tier: Performance tier (1-4)

    Returns:
        List of issues found (empty if no issues)
    """
    issues = []

    tier_1 = report_dict.get('tier_1_executive', '')
    tier_2 = report_dict.get('tier_2_strategic', '')
    tier_3 = report_dict.get('tier_3_deepdive', '')
    metadata = report_dict.get('metadata')

    # Check 1: Reports exist
    if not tier_1:
        issues.append("Tier 1 executive report is empty")
    if not tier_2:
        issues.append("Tier 2 strategic report is empty")
    if not tier_3:
        issues.append("Tier 3 deep-dive report is empty")

    # Check 2: Executive summary exists and is reasonable length
    if 'Executive Summary' not in tier_1:
        issues.append("Executive summary missing from Tier 1")

    # Check 3: Word counts are reasonable
    if metadata:
        t1_words = metadata.word_count.get('tier_1', 0)
        t2_words = metadata.word_count.get('tier_2', 0)
        t3_words = metadata.word_count.get('tier_3', 0)

        if t1_words < 300:
            issues.append(f"Tier 1 too short ({t1_words} words, expect 500-1000)")
        elif t1_words > 2000:
            issues.append(f"Tier 1 too long ({t1_words} words, expect 500-1000)")

        if t2_words < t1_words:
            issues.append(f"Tier 2 ({t2_words} words) should be longer than Tier 1 ({t1_words} words)")

        if t3_words < t2_words:
            issues.append(f"Tier 3 ({t3_words} words) should be longer than Tier 2 ({t2_words} words)")

    # Check 4: Confidence levels are marked
    if '✅' not in tier_1 and '⚠️' not in tier_1 and '❌' not in tier_1:
        issues.append("No confidence indicators found in Tier 1")

    # Check 5: Quick Start actions are present
    if 'Quick Start' not in tier_1:
        issues.append("Quick Start section missing from Tier 1")

    # Check 6: ROI calculations present in Tier 2
    if 'ROI' not in tier_2:
        issues.append("ROI calculations missing from Tier 2")

    # Check 7: Tier-specific sections
    if tier <= 2:
        # Crisis/Struggling should have negative review analysis
        if metadata and metadata.has_negative_reviews:
            if 'Negative Review' not in tier_2:
                issues.append("Negative review analysis missing for struggling game")

    if tier >= 3:
        # Solid/Exceptional should have growth strategies
        if 'Expansion' not in tier_2 and 'DLC' not in tier_2:
            issues.append("Growth strategies missing for solid/exceptional game")

    # Check 8: Methodology present in Tier 3
    if 'Methodology' not in tier_3:
        issues.append("Methodology section missing from Tier 3")

    # Check 9: No placeholder text
    for text in [tier_1, tier_2, tier_3]:
        if '*Coming soon*' in text:
            issues.append("Placeholder text found - incomplete sections")
        if '*unavailable*' in text or '*failed*' in text:
            issues.append("Component generation failures detected")

    return issues


# ========================================================================
# TESTING FRAMEWORK
# ========================================================================

def create_mock_data(test_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Create mock game data for testing"""
    return {
        'app_id': '999999',
        'name': test_spec.get('name', 'Test Game'),
        'price': test_spec.get('price', 19.99),
        'review_score': test_spec.get('review_pct', 75),
        'review_count': test_spec.get('reviews', 100),
        'owners': test_spec.get('owners', 10000),
        'revenue': test_spec.get('revenue', 150000),
        'genres': ['Indie', 'Action'],
        'release_date': '2024-01-15'
    }


def test_report_generation():
    """
    Test report generation across all score tiers.

    Tests 4 scenarios:
    1. Crisis game (score < 40)
    2. Struggling game (score 41-65)
    3. Solid game (score 66-80)
    4. Exceptional game (score 81-100)
    """
    print("\n" + "="*80)
    print("REPORT GENERATION TEST SUITE")
    print("="*80 + "\n")

    test_cases = [
        {
            'name': 'Crisis Game',
            'price': 14.99,
            'reviews': 123,
            'review_pct': 58,
            'owners': 5000,
            'revenue': 37000,
            'expected_tier': 1,
            'expected_sections': ['negative_review_analysis', 'salvageability'],
            'should_not_include': ['market_expansion', 'dlc_analysis'],
            'tone': 'urgent'
        },
        {
            'name': 'Struggling Game',
            'price': 19.99,
            'reviews': 487,
            'review_pct': 72,
            'owners': 15000,
            'revenue': 180000,
            'expected_tier': 2,
            'expected_sections': ['negative_review_analysis', 'quick_wins'],
            'should_not_include': ['dlc_analysis'],
            'tone': 'constructive'
        },
        {
            'name': 'Solid Game',
            'price': 24.99,
            'reviews': 2847,
            'review_pct': 85,
            'owners': 75000,
            'revenue': 1400000,
            'expected_tier': 3,
            'expected_sections': ['market_expansion', 'optimization'],
            'should_not_include': ['salvageability'],
            'tone': 'encouraging'
        },
        {
            'name': 'Exceptional Game',
            'price': 29.99,
            'reviews': 50302,
            'review_pct': 96.5,
            'owners': 500000,
            'revenue': 12000000,
            'expected_tier': 4,
            'expected_sections': ['dlc_analysis', 'scaling'],
            'should_not_include': ['salvageability', 'crisis'],
            'tone': 'celebratory'
        }
    ]

    orchestrator = ReportOrchestrator()

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_cases)}: {test['name']}")
        print(f"{'='*80}\n")

        # Create mock data
        game_data = create_mock_data(test)

        print(f"Game: {game_data['name']}")
        print(f"Reviews: {game_data['review_count']} ({game_data['review_score']}% positive)")
        print(f"Owners: {game_data['owners']:,}")
        print(f"Revenue: ${game_data['revenue']:,}")
        print(f"Expected Tier: {test['expected_tier']}\n")

        # Generate report
        try:
            report = orchestrator.generate_complete_report(game_data)

            # Validate
            print("✅ Report generated successfully")
            print(f"Actual Tier: {report['metadata'].performance_tier}")
            print(f"Tier Name: {report['metadata'].tier_name}")
            print(f"Overall Score: {report['metadata'].overall_score:.1f}/100")
            print(f"\nWord Counts:")
            print(f"  - Tier 1 Executive: {report['metadata'].word_count['tier_1']:,} words")
            print(f"  - Tier 2 Strategic: {report['metadata'].word_count['tier_2']:,} words")
            print(f"  - Tier 3 Deep-dive: {report['metadata'].word_count['tier_3']:,} words")

            # Run quality validation
            issues = validate_report(report, test['expected_tier'])

            if issues:
                print(f"\n⚠️  Quality Issues Found ({len(issues)}):")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print("\n✅ All quality checks passed")

            # Check tier matches
            if report['metadata'].performance_tier != test['expected_tier']:
                print(f"\n❌ TIER MISMATCH: Expected {test['expected_tier']}, "
                      f"got {report['metadata'].performance_tier}")
            else:
                print(f"\n✅ Tier classification correct")

        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_report_generation()
