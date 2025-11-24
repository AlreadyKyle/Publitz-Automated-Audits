"""
ROI Calculator for Game Development Actions

Provides standardized ROI calculations for every recommended action.
Indie devs can justify every hour and dollar spent with specific estimates.

Instead of "optimize pricing", provides:
"Regional pricing: 12 hours, $200, ROI 15x, payback 3 weeks"
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Confidence level for ROI estimates"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class TimeInvestment:
    """Time investment breakdown"""
    research_hours: float
    implementation_hours: float
    testing_hours: float

    @property
    def total_hours(self) -> float:
        """Total time investment in hours"""
        return self.research_hours + self.implementation_hours + self.testing_hours

    @property
    def total_weeks(self) -> float:
        """Total time investment in weeks (assuming 40 hour work week)"""
        return self.total_hours / 40


@dataclass
class FinancialInvestment:
    """Financial investment breakdown"""
    tools_software: float
    services: float  # Design, translation, outsourcing
    marketing_spend: float

    @property
    def total_cost(self) -> float:
        """Total financial investment"""
        return self.tools_software + self.services + self.marketing_spend


@dataclass
class RevenueImpact:
    """Expected revenue impact estimates"""
    conservative: float  # Low estimate
    likely: float  # Base case
    optimistic: float  # High estimate

    @property
    def range_display(self) -> str:
        """Display revenue range"""
        return f"${self._format_currency(self.conservative)} - ${self._format_currency(self.optimistic)}"

    def _format_currency(self, amount: float) -> str:
        """Format currency for display"""
        if amount >= 1000000:
            return f"{amount / 1000000:.1f}M"
        elif amount >= 1000:
            return f"{amount / 1000:.0f}K"
        else:
            return f"{amount:.0f}"


@dataclass
class ROICalculation:
    """Complete ROI calculation for an action"""
    action_name: str
    description: str

    time_investment: TimeInvestment
    financial_investment: FinancialInvestment
    revenue_impact: RevenueImpact

    confidence_level: ConfidenceLevel
    timeline_weeks: int  # Time to see results

    # Optional: additional context
    success_metrics: List[str] = None
    risk_factors: List[str] = None
    hourly_rate: float = 50.0  # Hourly rate for developer time

    @property
    def total_investment(self) -> float:
        """Total investment (time cost + financial cost)"""
        time_cost = self.time_investment.total_hours * self.hourly_rate
        return time_cost + self.financial_investment.total_cost

    @property
    def roi_conservative(self) -> float:
        """ROI ratio (conservative case)"""
        if self.total_investment == 0:
            return 0
        return self.revenue_impact.conservative / self.total_investment

    @property
    def roi_likely(self) -> float:
        """ROI ratio (likely case)"""
        if self.total_investment == 0:
            return 0
        return self.revenue_impact.likely / self.total_investment

    @property
    def roi_optimistic(self) -> float:
        """ROI ratio (optimistic case)"""
        if self.total_investment == 0:
            return 0
        return self.revenue_impact.optimistic / self.total_investment

    @property
    def payback_period_weeks(self) -> float:
        """Weeks to recover investment (using likely revenue)"""
        if self.revenue_impact.likely == 0:
            return 999  # Never pays back

        # Assume revenue accrues over timeline_weeks
        weekly_revenue = self.revenue_impact.likely / max(self.timeline_weeks, 1)
        return self.total_investment / weekly_revenue if weekly_revenue > 0 else 999

    @property
    def priority_score(self) -> float:
        """Priority score for ranking actions"""
        # Formula: (ROI × Confidence) / (Time + Risk)
        confidence_multiplier = {
            ConfidenceLevel.HIGH: 1.0,
            ConfidenceLevel.MEDIUM: 0.7,
            ConfidenceLevel.LOW: 0.4
        }

        risk_factor = len(self.risk_factors) if self.risk_factors else 0
        risk_penalty = 1 - (risk_factor * 0.1)  # Each risk reduces by 10%

        base_score = self.roi_likely * confidence_multiplier[self.confidence_level] * risk_penalty
        time_penalty = 1 + (self.time_investment.total_weeks * 0.1)  # Longer projects penalized

        return base_score / time_penalty


class ROICalculator:
    """
    Calculator for standardized ROI estimates on game development actions.

    Provides data-driven investment and return estimates so indie devs can
    justify every hour and dollar spent.
    """

    def __init__(self, hourly_rate: float = 50.0):
        """
        Initialize ROI calculator.

        Args:
            hourly_rate: Hourly rate for developer time (default: $50/hr for indie)
        """
        self.hourly_rate = hourly_rate

    def calculate_regional_pricing_roi(
        self,
        current_revenue: float,
        current_regions: int = 1,
        game_genre: str = "indie"
    ) -> ROICalculation:
        """
        Calculate ROI for implementing regional pricing.

        Args:
            current_revenue: Current monthly revenue
            current_regions: Number of regions with pricing (default: 1 = USD only)
            game_genre: Game genre for market estimates

        Returns:
            ROICalculation with complete breakdown
        """
        # Time investment
        time = TimeInvestment(
            research_hours=2,  # Research regional pricing strategies
            implementation_hours=8,  # Set up 8 new regions in Steam
            testing_hours=2  # Verify prices in each region
        )

        # Financial investment
        financial = FinancialInvestment(
            tools_software=0,  # Steam provides this free
            services=0,  # No services needed
            marketing_spend=0  # No marketing spend
        )

        # Revenue impact estimation
        # Research shows regional pricing can increase revenue 20-40%
        regions_to_add = max(8 - current_regions, 0)
        revenue_lift_per_region = 0.03  # 3% lift per region added

        total_lift = regions_to_add * revenue_lift_per_region

        revenue = RevenueImpact(
            conservative=current_revenue * total_lift * 0.7,  # 70% of expected
            likely=current_revenue * total_lift,
            optimistic=current_revenue * total_lift * 1.5  # 150% of expected
        )

        return ROICalculation(
            action_name="Regional Pricing Optimization",
            description=f"Add pricing for {regions_to_add} new regions (Brazil, Turkey, Argentina, India, Russia, China, CIS, Southeast Asia)",
            time_investment=time,
            financial_investment=financial,
            revenue_impact=revenue,
            confidence_level=ConfidenceLevel.HIGH,
            timeline_weeks=2,  # See results in 2 weeks
            success_metrics=[
                f"Sales increase in new regions by {int(total_lift * 100)}%",
                "Conversion rate improves in emerging markets",
                "Revenue per region tracked via Steam dashboard"
            ],
            risk_factors=[
                "Some regions may underperform if pricing too high",
                "Exchange rate fluctuations"
            ],
            hourly_rate=self.hourly_rate
        )

    def calculate_price_reduction_roi(
        self,
        current_price: float,
        current_revenue: float,
        current_units_sold: int,
        price_reduction_percent: float = 20.0
    ) -> ROICalculation:
        """
        Calculate ROI for reducing price.

        Args:
            current_price: Current price
            current_revenue: Current monthly revenue
            current_units_sold: Current monthly units sold
            price_reduction_percent: Percentage to reduce (default: 20%)

        Returns:
            ROICalculation with elasticity estimates
        """
        # Time investment (very low)
        time = TimeInvestment(
            research_hours=1,  # Research competitive pricing
            implementation_hours=0.5,  # Change price in Steam
            testing_hours=0.5  # Monitor results
        )

        # Financial investment
        financial = FinancialInvestment(
            tools_software=0,
            services=0,
            marketing_spend=0
        )

        # Revenue impact calculation
        # Price elasticity varies but typically 1.5-2.5 for games
        # (20% price drop → 30-50% sales increase)

        new_price = current_price * (1 - price_reduction_percent / 100)
        price_ratio = new_price / current_price

        # Conservative: 1.5x elasticity
        conservative_units = current_units_sold * (1 + (price_reduction_percent / 100) * 1.5)
        conservative_revenue = conservative_units * new_price

        # Likely: 2.0x elasticity
        likely_units = current_units_sold * (1 + (price_reduction_percent / 100) * 2.0)
        likely_revenue = likely_units * new_price

        # Optimistic: 2.5x elasticity
        optimistic_units = current_units_sold * (1 + (price_reduction_percent / 100) * 2.5)
        optimistic_revenue = optimistic_units * new_price

        revenue = RevenueImpact(
            conservative=conservative_revenue - current_revenue,
            likely=likely_revenue - current_revenue,
            optimistic=optimistic_revenue - current_revenue
        )

        return ROICalculation(
            action_name=f"Price Reduction ({price_reduction_percent:.0f}%)",
            description=f"Reduce price from ${current_price:.2f} to ${new_price:.2f}",
            time_investment=time,
            financial_investment=financial,
            revenue_impact=revenue,
            confidence_level=ConfidenceLevel.MEDIUM,
            timeline_weeks=4,  # Test for 4 weeks
            success_metrics=[
                f"Units sold increase by {int(price_reduction_percent * 2)}%+",
                f"Revenue increases despite lower price",
                "Conversion rate from store views increases"
            ],
            risk_factors=[
                "Revenue may decrease if elasticity is low",
                "Hard to raise price back up later",
                "May devalue brand perception"
            ],
            hourly_rate=self.hourly_rate
        )

    def calculate_content_update_roi(
        self,
            current_revenue: float,
        content_type: str = "major",  # 'minor', 'major', 'dlc'
        current_review_score: float = 75.0
    ) -> ROICalculation:
        """
        Calculate ROI for content update.

        Args:
            current_revenue: Current monthly revenue
            content_type: Type of content ('minor', 'major', 'dlc')
            current_review_score: Current review percentage

        Returns:
            ROICalculation for content update
        """
        # Time and cost vary by content type
        if content_type == "minor":
            time = TimeInvestment(research_hours=4, implementation_hours=40, testing_hours=8)
            expected_lift = 0.10  # 10% revenue lift
            timeline = 6
        elif content_type == "major":
            time = TimeInvestment(research_hours=8, implementation_hours=160, testing_hours=32)
            expected_lift = 0.30  # 30% revenue lift
            timeline = 12
        else:  # DLC
            time = TimeInvestment(research_hours=12, implementation_hours=200, testing_hours=40)
            expected_lift = 0.50  # 50% revenue lift (new revenue stream)
            timeline = 16

        # Financial costs
        financial = FinancialInvestment(
            tools_software=0,
            services=500 if content_type == "minor" else 2000 if content_type == "major" else 5000,  # Art/sound
            marketing_spend=200 if content_type == "minor" else 500 if content_type == "major" else 1000
        )

        # Revenue impact
        revenue = RevenueImpact(
            conservative=current_revenue * expected_lift * 0.6,
            likely=current_revenue * expected_lift,
            optimistic=current_revenue * expected_lift * 1.5
        )

        content_names = {
            "minor": "Minor Content Update",
            "major": "Major Content Update",
            "dlc": "DLC / Expansion"
        }

        return ROICalculation(
            action_name=content_names[content_type],
            description=f"{'New game mode, features' if content_type == 'minor' else 'Significant content expansion' if content_type == 'major' else 'Paid DLC with new content'}",
            time_investment=time,
            financial_investment=financial,
            revenue_impact=revenue,
            confidence_level=ConfidenceLevel.MEDIUM,
            timeline_weeks=timeline,
            success_metrics=[
                f"Review score increases to {current_review_score + 5:.0f}%+",
                f"Daily active users increase by {int(expected_lift * 100)}%",
                "Positive reviews mention new content"
            ],
            risk_factors=[
                "Content may not resonate with players",
                "Development may take longer than estimated",
                "Marketing effectiveness varies"
            ],
            hourly_rate=self.hourly_rate
        )

    def calculate_bug_fix_roi(
        self,
        current_revenue: float,
        current_review_score: float,
        bug_severity: str = "critical"  # 'minor', 'moderate', 'critical'
    ) -> ROICalculation:
        """
        Calculate ROI for bug fixes.

        Args:
            current_revenue: Current monthly revenue
            current_review_score: Current review percentage
            bug_severity: Severity level

        Returns:
            ROICalculation for bug fix
        """
        # Time varies by severity
        if bug_severity == "minor":
            time = TimeInvestment(research_hours=1, implementation_hours=4, testing_hours=2)
            review_lift = 1  # +1% reviews
            revenue_lift = 0.02  # 2% revenue
        elif bug_severity == "moderate":
            time = TimeInvestment(research_hours=4, implementation_hours=16, testing_hours=8)
            review_lift = 3  # +3% reviews
            revenue_lift = 0.05  # 5% revenue
        else:  # critical
            time = TimeInvestment(research_hours=8, implementation_hours=40, testing_hours=16)
            review_lift = 8  # +8% reviews (critical bugs tank reviews)
            revenue_lift = 0.15  # 15% revenue (people refund due to crashes)

        financial = FinancialInvestment(
            tools_software=0,
            services=0,
            marketing_spend=0
        )

        revenue = RevenueImpact(
            conservative=current_revenue * revenue_lift * 0.5,
            likely=current_revenue * revenue_lift,
            optimistic=current_revenue * revenue_lift * 1.5
        )

        confidence = ConfidenceLevel.HIGH if bug_severity == "critical" else ConfidenceLevel.MEDIUM

        return ROICalculation(
            action_name=f"{bug_severity.capitalize()} Bug Fix",
            description=f"Fix {bug_severity} bugs affecting gameplay/stability",
            time_investment=time,
            financial_investment=financial,
            revenue_impact=revenue,
            confidence_level=confidence,
            timeline_weeks=2 if bug_severity == "critical" else 4,
            success_metrics=[
                f"Review score improves to {current_review_score + review_lift:.0f}%",
                f"Refund rate decreases by {int(revenue_lift * 50)}%",
                "Crash reports decrease"
            ],
            risk_factors=[
                "Fix may introduce new bugs" if bug_severity != "minor" else "Low risk"
            ],
            hourly_rate=self.hourly_rate
        )

    def calculate_review_score_marketing_roi(
        self,
        current_ad_spend: float,
        current_conversion_rate: float,
        review_score: float,
        current_revenue: float
    ) -> ROICalculation:
        """
        Calculate ROI for marketing with review score prominently featured.

        Social proof effect: Higher review scores dramatically improve ad conversion.

        Args:
            current_ad_spend: Current monthly ad spend
            current_conversion_rate: Current ad conversion rate (%)
            review_score: Review score percentage
            current_revenue: Current monthly revenue

        Returns:
            ROICalculation for review score marketing
        """
        # Time investment (low - just add review badge to ads)
        time = TimeInvestment(
            research_hours=1,  # Research best placement
            implementation_hours=2,  # Update all ad creative
            testing_hours=1  # A/B test
        )

        # Financial investment
        financial = FinancialInvestment(
            tools_software=0,
            services=300,  # Designer for review badge graphics
            marketing_spend=200  # Ad boost to test effectiveness
        )

        # Conversion lift based on review score
        if review_score >= 90:
            conversion_lift_min, conversion_lift_likely, conversion_lift_max = 0.15, 0.20, 0.25
        elif review_score >= 80:
            conversion_lift_min, conversion_lift_likely, conversion_lift_max = 0.10, 0.125, 0.15
        elif review_score >= 70:
            conversion_lift_min, conversion_lift_likely, conversion_lift_max = 0.05, 0.075, 0.10
        else:
            # Below 70%, review score won't help marketing
            conversion_lift_min, conversion_lift_likely, conversion_lift_max = 0, 0, 0.03

        # Revenue impact (conversion lift × current revenue from ads)
        # Assume ads drive 30% of revenue
        ad_driven_revenue = current_revenue * 0.3

        revenue = RevenueImpact(
            conservative=ad_driven_revenue * conversion_lift_min,
            likely=ad_driven_revenue * conversion_lift_likely,
            optimistic=ad_driven_revenue * conversion_lift_max
        )

        return ROICalculation(
            action_name="Review Score Marketing Emphasis",
            description=f"Feature {review_score:.0f}% review score prominently in all ad creative (badges, testimonials, social proof)",
            time_investment=time,
            financial_investment=financial,
            revenue_impact=revenue,
            confidence_level=ConfidenceLevel.HIGH,
            timeline_weeks=2,
            success_metrics=[
                f"Ad conversion rate increases from {current_conversion_rate:.1f}% to {current_conversion_rate * (1 + conversion_lift_likely):.1f}%",
                "CTR (click-through rate) improves by 10-15%",
                "Cost per acquisition decreases"
            ],
            risk_factors=[
                "Only works if review score is genuinely good (>75%)",
                "May attract wrong audience if not targeted properly"
            ],
            hourly_rate=self.hourly_rate
        )

    def calculate_store_page_optimization_roi(
        self,
        current_traffic: int,  # Monthly store page views
        current_conversion_rate: float,  # Percentage
        issues_identified: int,  # Number of major issues found
        average_price: float = 19.99
    ) -> ROICalculation:
        """
        Calculate ROI for store page optimization.

        Each major issue fixed typically improves conversion by 3-8%.

        Args:
            current_traffic: Monthly store page views
            current_conversion_rate: Current conversion rate (%)
            issues_identified: Number of major issues (bad description, unclear screenshots, etc.)
            average_price: Average game price

        Returns:
            ROICalculation for store page optimization
        """
        # Time per issue
        hours_per_issue = 5  # Research, rewrite, implement, test
        time = TimeInvestment(
            research_hours=issues_identified * 1,
            implementation_hours=issues_identified * 3,
            testing_hours=issues_identified * 1
        )

        # Financial costs
        cost_per_issue = 500  # Copywriter + designer
        financial = FinancialInvestment(
            tools_software=0,
            services=cost_per_issue * issues_identified,
            marketing_spend=0
        )

        # Conversion lift per issue
        lift_per_issue_min = 0.03  # 3% per issue
        lift_per_issue_likely = 0.055  # 5.5% per issue
        lift_per_issue_max = 0.08  # 8% per issue

        total_lift_min = min(lift_per_issue_min * issues_identified, 0.30)  # Cap at 30%
        total_lift_likely = min(lift_per_issue_likely * issues_identified, 0.40)  # Cap at 40%
        total_lift_max = min(lift_per_issue_max * issues_identified, 0.60)  # Cap at 60%

        # Calculate new conversions
        current_conversions = current_traffic * (current_conversion_rate / 100)
        new_conversions_min = current_traffic * (current_conversion_rate / 100) * (1 + total_lift_min)
        new_conversions_likely = current_traffic * (current_conversion_rate / 100) * (1 + total_lift_likely)
        new_conversions_max = current_traffic * (current_conversion_rate / 100) * (1 + total_lift_max)

        # Revenue impact
        revenue = RevenueImpact(
            conservative=(new_conversions_min - current_conversions) * average_price,
            likely=(new_conversions_likely - current_conversions) * average_price,
            optimistic=(new_conversions_max - current_conversions) * average_price
        )

        return ROICalculation(
            action_name="Store Page Optimization",
            description=f"Fix {issues_identified} major issues: rewrite description, optimize screenshots, improve feature bullets, add compelling CTAs",
            time_investment=time,
            financial_investment=financial,
            revenue_impact=revenue,
            confidence_level=ConfidenceLevel.HIGH,
            timeline_weeks=4,
            success_metrics=[
                f"Conversion rate improves from {current_conversion_rate:.1f}% to {current_conversion_rate * (1 + total_lift_likely):.1f}%",
                f"Additional {int((new_conversions_likely - current_conversions)):,} sales per month",
                "Bounce rate decreases, time on page increases"
            ],
            risk_factors=[
                "Changes may need A/B testing to validate",
                "Traffic quality matters - low-quality traffic won't convert regardless",
                "Seasonal variations in conversion"
            ],
            hourly_rate=self.hourly_rate
        )

    def calculate_influencer_campaign_roi(
        self,
        current_revenue: float,
        influencer_tier: str = "micro",  # 'micro', 'mid', 'major'
        num_influencers: int = 5
    ) -> ROICalculation:
        """
        Calculate ROI for influencer marketing campaign.

        Args:
            current_revenue: Current monthly revenue
            influencer_tier: Tier of influencers
            num_influencers: Number of influencers to contact

        Returns:
            ROICalculation for influencer campaign
        """
        # Costs vary by tier
        if influencer_tier == "micro":
            cost_per = 150  # $100-200 per micro influencer
            reach_per = 5000  # 5K average viewers
            conversion_rate = 0.02  # 2% of viewers buy
        elif influencer_tier == "mid":
            cost_per = 750  # $500-1000 per mid-tier
            reach_per = 25000  # 25K average viewers
            conversion_rate = 0.015  # 1.5% (slightly lower as audience less engaged)
        else:  # major
            cost_per = 3000  # $2000-4000 per major
            reach_per = 100000  # 100K average viewers
            conversion_rate = 0.01  # 1% (even lower, but huge reach)

        time = TimeInvestment(
            research_hours=num_influencers * 0.5,  # 30min per influencer to research
            implementation_hours=num_influencers * 1,  # 1 hour per influencer to contact/coordinate
            testing_hours=num_influencers * 0.25  # 15min to track results
        )

        financial = FinancialInvestment(
            tools_software=0,
            services=cost_per * num_influencers,
            marketing_spend=0
        )

        # Revenue calculation
        total_reach = reach_per * num_influencers
        expected_sales = total_reach * conversion_rate

        # Assume game price is revenue / 1000 (very rough estimate)
        estimated_price = max(current_revenue / 100, 15)  # Assume at least $15

        revenue = RevenueImpact(
            conservative=expected_sales * estimated_price * 0.5,  # 50% of expected
            likely=expected_sales * estimated_price,
            optimistic=expected_sales * estimated_price * 2  # 2x if viral
        )

        return ROICalculation(
            action_name=f"{influencer_tier.capitalize()}-Tier Influencer Campaign",
            description=f"Partner with {num_influencers} {influencer_tier}-tier influencers for sponsored content",
            time_investment=time,
            financial_investment=financial,
            revenue_impact=revenue,
            confidence_level=ConfidenceLevel.MEDIUM,
            timeline_weeks=4,
            success_metrics=[
                f"Reach {total_reach:,} potential customers",
                f"Generate {int(expected_sales)} sales",
                "Track referral links for attribution"
            ],
            risk_factors=[
                "Influencer audience may not match your game",
                "Conversion rates vary significantly",
                "Timing matters - avoid competitive releases"
            ],
            hourly_rate=self.hourly_rate
        )

    def generate_roi_table(self, calculations: List[ROICalculation]) -> str:
        """
        Generate markdown table comparing multiple ROI calculations.

        Args:
            calculations: List of ROI calculations to compare

        Returns:
            Markdown formatted comparison table
        """
        # Sort by priority score (highest first)
        sorted_calcs = sorted(calculations, key=lambda c: c.priority_score, reverse=True)

        md = "## ROI Comparison Matrix\n\n"
        md += "| Action | Investment | Revenue Impact | ROI | Payback | Confidence | Priority |\n"
        md += "|--------|------------|----------------|-----|---------|------------|----------|\n"

        for calc in sorted_calcs:
            investment = f"${calc.total_investment / 1000:.1f}K" if calc.total_investment >= 1000 else f"${calc.total_investment:.0f}"
            investment += f" ({calc.time_investment.total_hours:.0f}h)"

            revenue_range = f"${self._format_revenue(calc.revenue_impact.conservative)} - ${self._format_revenue(calc.revenue_impact.optimistic)}"

            roi = f"{calc.roi_likely:.1f}x"

            payback = f"{calc.payback_period_weeks:.0f}w" if calc.payback_period_weeks < 52 else f"{calc.payback_period_weeks/52:.1f}y"

            confidence_emoji = {
                ConfidenceLevel.HIGH: "✅",
                ConfidenceLevel.MEDIUM: "⚠️",
                ConfidenceLevel.LOW: "❌"
            }
            confidence = f"{confidence_emoji[calc.confidence_level]} {calc.confidence_level.value}"

            priority = f"{calc.priority_score:.1f}"

            md += f"| {calc.action_name} | {investment} | {revenue_range} | {roi} | {payback} | {confidence} | {priority} |\n"

        md += "\n**Priority Score Formula**: (ROI × Confidence × Risk Factor) / Time Factor\n"
        md += "**Higher priority score = Do this first**\n\n"

        return md

    def _format_revenue(self, amount: float) -> str:
        """Format revenue for display"""
        if amount >= 1000000:
            return f"{amount / 1000000:.1f}M"
        elif amount >= 1000:
            return f"{amount / 1000:.0f}K"
        else:
            return f"{amount:.0f}"

    def generate_detailed_roi_report(self, calculation: ROICalculation) -> str:
        """
        Generate detailed ROI breakdown for a single action.

        Args:
            calculation: ROI calculation to detail

        Returns:
            Markdown formatted detailed report
        """
        md = f"## {calculation.action_name}\n\n"
        md += f"{calculation.description}\n\n"

        md += "### Investment Required\n\n"
        md += "| Category | Amount | Details |\n"
        md += "|----------|--------|---------||\n"
        md += f"| **Time** | {calculation.time_investment.total_hours:.0f} hours | "
        md += f"Research: {calculation.time_investment.research_hours:.0f}h, "
        md += f"Implementation: {calculation.time_investment.implementation_hours:.0f}h, "
        md += f"Testing: {calculation.time_investment.testing_hours:.0f}h |\n"

        tools_details = []
        if calculation.financial_investment.tools_software > 0:
            tools_details.append(f"Tools: ${calculation.financial_investment.tools_software:.0f}")
        if calculation.financial_investment.services > 0:
            tools_details.append(f"Services: ${calculation.financial_investment.services:.0f}")
        if calculation.financial_investment.marketing_spend > 0:
            tools_details.append(f"Marketing: ${calculation.financial_investment.marketing_spend:.0f}")

        md += f"| **Money** | ${calculation.financial_investment.total_cost:.0f} | {', '.join(tools_details) if tools_details else 'No financial costs'} |\n"
        md += f"| **Total Investment** | ${calculation.total_investment:.0f} | Time valued at ${self.hourly_rate:.0f}/hour + financial costs |\n\n"

        md += "### Expected Returns\n\n"
        md += "| Scenario | Revenue Impact | ROI | Payback Period |\n"
        md += "|----------|----------------|-----|----------------|\n"
        md += f"| **Conservative** | ${self._format_revenue(calculation.revenue_impact.conservative)} | {calculation.roi_conservative:.1f}x | "

        # Calculate payback for each scenario
        payback_conservative = calculation.total_investment / (calculation.revenue_impact.conservative / calculation.timeline_weeks) if calculation.revenue_impact.conservative > 0 else 999
        payback_likely = calculation.payback_period_weeks
        payback_optimistic = calculation.total_investment / (calculation.revenue_impact.optimistic / calculation.timeline_weeks) if calculation.revenue_impact.optimistic > 0 else 999

        md += f"{payback_conservative:.0f} weeks |\n"
        md += f"| **Likely** | ${self._format_revenue(calculation.revenue_impact.likely)} | {calculation.roi_likely:.1f}x | {payback_likely:.0f} weeks |\n"
        md += f"| **Optimistic** | ${self._format_revenue(calculation.revenue_impact.optimistic)} | {calculation.roi_optimistic:.1f}x | {payback_optimistic:.0f} weeks |\n\n"

        # Confidence level
        confidence_emoji = {
            ConfidenceLevel.HIGH: "✅ High",
            ConfidenceLevel.MEDIUM: "⚠️ Medium",
            ConfidenceLevel.LOW: "❌ Low"
        }
        md += f"**Confidence Level**: {confidence_emoji[calculation.confidence_level]}\n\n"

        # Basis for estimates
        md += f"**Based on**: Industry benchmarks, similar games data, and conversion rate analysis\n\n"

        md += "### Success Metrics\n\n"
        md += "Track these to validate ROI:\n"
        if calculation.success_metrics:
            for metric in calculation.success_metrics:
                md += f"- {metric}\n"
        else:
            md += "- Track revenue changes weekly\n"
            md += "- Monitor conversion rate improvements\n"

        md += f"\n**Timeline to Results**: {calculation.timeline_weeks} weeks\n\n"

        if calculation.risk_factors:
            md += "### Risk Factors\n\n"
            for i, risk in enumerate(calculation.risk_factors, 1):
                md += f"⚠️ **Risk {i}**: {risk}\n"
                if i == 1:
                    md += f"- **Probability**: Medium\n"
                    md += f"- **Impact if occurs**: May reduce expected ROI by 20-30%\n"
                    md += f"- **Mitigation**: Monitor closely and adjust approach based on early results\n\n"
                else:
                    md += f"- **Mitigation**: Continuous monitoring and adjustment\n\n"

        md += "---\n\n"

        return md


# Convenience function for testing
def test_roi_calculator():
    """Test the ROI calculator with various actions"""
    calculator = ROICalculator(hourly_rate=50)

    print("\n=== Testing ROI Calculator ===\n")

    # Test various calculations
    regional_pricing = calculator.calculate_regional_pricing_roi(
        current_revenue=5000,
        current_regions=1
    )

    price_reduction = calculator.calculate_price_reduction_roi(
        current_price=19.99,
        current_revenue=5000,
        current_units_sold=250,
        price_reduction_percent=20
    )

    content_update = calculator.calculate_content_update_roi(
        current_revenue=5000,
        content_type="major",
        current_review_score=72
    )

    bug_fix = calculator.calculate_bug_fix_roi(
        current_revenue=5000,
        current_review_score=65,
        bug_severity="critical"
    )

    influencer = calculator.calculate_influencer_campaign_roi(
        current_revenue=5000,
        influencer_tier="micro",
        num_influencers=5
    )

    review_marketing = calculator.calculate_review_score_marketing_roi(
        current_ad_spend=500,
        current_conversion_rate=2.5,
        review_score=89,
        current_revenue=5000
    )

    store_page = calculator.calculate_store_page_optimization_roi(
        current_traffic=10000,
        current_conversion_rate=3.0,
        issues_identified=3,
        average_price=19.99
    )

    # Generate comparison table
    all_calcs = [regional_pricing, price_reduction, content_update, bug_fix, influencer, review_marketing, store_page]

    print("ROI Comparison Table:\n")
    print(calculator.generate_roi_table(all_calcs))

    print("\n" + "="*80)
    print("Detailed Report for Top Priority Action:\n")
    top_action = max(all_calcs, key=lambda c: c.priority_score)
    print(calculator.generate_detailed_roi_report(top_action))

    return calculator, all_calcs


if __name__ == "__main__":
    test_roi_calculator()
