"""
Price Analysis System

Detects and flags catastrophic pricing errors that kill revenue potential.
Overrides optimistic scores when base price is fundamentally broken.

CRITICAL: A game priced at $0.99 CANNOT have a good regional pricing score.
The base price is catastrophic and must be fixed FIRST.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
import statistics

logger = logging.getLogger(__name__)


@dataclass
class PriceTier:
    """Price tier classification"""
    tier: str                    # 'catastrophic_low', 'too_low', 'optimal', 'premium', 'too_high'
    severity: Optional[str]      # 'CRITICAL', 'HIGH', 'MEDIUM', None
    message: str                 # Human-readable explanation
    recommended_min: Optional[float] = None
    recommended_max: Optional[float] = None
    impact_on_sales: int = 0     # Percentage impact (-70 means 70% revenue loss)
    is_viable: bool = True       # False for catastrophic pricing


@dataclass
class CompetitorComparison:
    """Comparison to competitor pricing"""
    issue: Optional[str]         # 'severe_underpricing', 'overpricing_vs_quality', None
    message: str
    price_ratio: float          # your_price / avg_competitor_price
    quality_ratio: float        # your_quality / avg_competitor_quality
    lost_revenue_estimate: Optional[float] = None
    recommendation: str = ""


@dataclass
class PriceOverride:
    """Score override for catastrophic pricing"""
    original_score: int
    overridden_score: int
    was_overridden: bool
    reason: Optional[str]
    warning: Optional[str]
    lost_revenue: Optional[float] = None


def classify_price_tier(
    price_usd: float,
    genre_tags: Optional[List[str]] = None,
    is_early_access: bool = False
) -> PriceTier:
    """
    Classify price into tiers based on indie game market standards.

    Args:
        price_usd: Current price in USD
        genre_tags: List of genre tags (for context)
        is_early_access: Whether game is early access (allows lower pricing)

    Returns:
        PriceTier object with classification and recommendations

    Examples:
        >>> tier = classify_price_tier(0.99)
        >>> tier.tier
        'catastrophic_low'
        >>> tier.severity
        'CRITICAL'
    """

    # Free to play
    if price_usd == 0:
        return PriceTier(
            tier='free_to_play',
            severity=None,
            message='Free-to-play model - monetization should come from MTX/DLC',
            is_viable=True
        )

    # CATASTROPHIC: Below viability threshold
    if price_usd < 2.00:
        return PriceTier(
            tier='catastrophic_low',
            severity='CRITICAL',
            message=f'${price_usd:.2f} price is below viability threshold - signals shovelware/asset flip',
            recommended_min=4.99,
            recommended_max=14.99,
            impact_on_sales=-70,  # Losing 70% of potential revenue
            is_viable=False
        )

    # PROBLEMATIC LOW: Under $5
    if price_usd < 5.00:
        return PriceTier(
            tier='too_low',
            severity='HIGH',
            message=f'${price_usd:.2f} price signals lack of confidence or quality concerns to players',
            recommended_min=7.99,
            recommended_max=14.99,
            impact_on_sales=-40,
            is_viable=True
        )

    # ACCEPTABLE LOW: $5-7.99 (okay for small games or early access)
    if price_usd < 8.00:
        if is_early_access:
            return PriceTier(
                tier='acceptable_low',
                severity=None,
                message=f'${price_usd:.2f} is acceptable for early access small indie game',
                impact_on_sales=-15,
                is_viable=True
            )
        else:
            return PriceTier(
                tier='acceptable_low',
                severity='LOW',
                message=f'${price_usd:.2f} is on the low end - consider ${8:.2f}-${12:.2f} for full release',
                recommended_min=7.99,
                recommended_max=12.99,
                impact_on_sales=-20,
                is_viable=True
            )

    # OPTIMAL: $8-20 (sweet spot for indie games)
    if price_usd <= 20.00:
        return PriceTier(
            tier='optimal',
            severity=None,
            message=f'${price_usd:.2f} is in optimal indie game pricing range',
            impact_on_sales=0,
            is_viable=True
        )

    # PREMIUM: $20-30 (high-end indie)
    if price_usd <= 30.00:
        return PriceTier(
            tier='premium',
            severity=None,
            message=f'${price_usd:.2f} is premium indie pricing - justified if quality/content is exceptional',
            impact_on_sales=-10,
            is_viable=True
        )

    # TOO HIGH: $30-60
    if price_usd <= 60.00:
        return PriceTier(
            tier='too_high',
            severity='MEDIUM',
            message=f'${price_usd:.2f} is AAA pricing - may limit indie game market reach',
            recommended_max=24.99,
            impact_on_sales=-25,
            is_viable=True
        )

    # EXTREMELY HIGH: >$60
    return PriceTier(
        tier='extremely_high',
        severity='HIGH',
        message=f'${price_usd:.2f} is above standard game pricing - significant market resistance expected',
        recommended_max=29.99,
        impact_on_sales=-50,
        is_viable=True
    )


def compare_to_competitors(
    your_price: float,
    your_review_score: float,
    competitor_prices: List[float],
    competitor_review_scores: List[float],
    estimated_units_sold: int = 0
) -> CompetitorComparison:
    """
    Compare your pricing to competitors and determine if it makes sense.

    Args:
        your_price: Your game's price
        your_review_score: Your review percentage (0-100)
        competitor_prices: List of competitor prices
        competitor_review_scores: List of competitor review percentages
        estimated_units_sold: Estimated units sold (for revenue loss calc)

    Returns:
        CompetitorComparison with issue diagnosis

    Examples:
        >>> comp = compare_to_competitors(
        ...     your_price=0.99,
        ...     your_review_score=80.0,
        ...     competitor_prices=[12.99, 14.99, 9.99],
        ...     competitor_review_scores=[75.0, 78.0, 72.0],
        ...     estimated_units_sold=380
        ... )
        >>> comp.issue
        'severe_underpricing'
        >>> comp.lost_revenue_estimate
        4560.0  # Approximately ($12.66 - $0.99) * 380
    """

    if not competitor_prices or not competitor_review_scores:
        return CompetitorComparison(
            issue=None,
            message='No competitor data available for comparison',
            price_ratio=1.0,
            quality_ratio=1.0
        )

    avg_competitor_price = statistics.mean(competitor_prices)
    avg_competitor_score = statistics.mean(competitor_review_scores)

    price_ratio = your_price / avg_competitor_price if avg_competitor_price > 0 else 1.0
    quality_ratio = your_review_score / avg_competitor_score if avg_competitor_score > 0 else 1.0

    # SEVERE UNDERPRICING: Much cheaper than competitors despite similar/better quality
    if price_ratio < 0.4 and quality_ratio >= 0.8:
        lost_revenue_per_unit = avg_competitor_price - your_price
        lost_revenue = lost_revenue_per_unit * estimated_units_sold if estimated_units_sold > 0 else None

        return CompetitorComparison(
            issue='severe_underpricing',
            message=f'You are {(1-price_ratio)*100:.0f}% cheaper than competitors (${your_price:.2f} vs ${avg_competitor_price:.2f} avg) '
                   f'despite {"better" if quality_ratio > 1.0 else "similar"} quality '
                   f'({your_review_score:.0f}% vs {avg_competitor_score:.0f}% avg)',
            price_ratio=price_ratio,
            quality_ratio=quality_ratio,
            lost_revenue_estimate=lost_revenue,
            recommendation=f'Increase price to ${avg_competitor_price * 0.7:.2f}-${avg_competitor_price * 0.9:.2f} '
                          f'to capture lost revenue while remaining competitive'
        )

    # MODERATE UNDERPRICING: Cheaper than competitors with similar quality
    if price_ratio < 0.7 and quality_ratio >= 0.9:
        lost_revenue_per_unit = avg_competitor_price * 0.8 - your_price
        lost_revenue = lost_revenue_per_unit * estimated_units_sold if estimated_units_sold > 0 else None

        return CompetitorComparison(
            issue='moderate_underpricing',
            message=f'You are {(1-price_ratio)*100:.0f}% cheaper than competitors with comparable quality',
            price_ratio=price_ratio,
            quality_ratio=quality_ratio,
            lost_revenue_estimate=lost_revenue,
            recommendation=f'Consider pricing at ${avg_competitor_price * 0.8:.2f} to increase revenue without sacrificing competitiveness'
        )

    # OVERPRICING VS QUALITY: More expensive despite lower quality
    if price_ratio > 1.3 and quality_ratio < 0.9:
        return CompetitorComparison(
            issue='overpricing_vs_quality',
            message=f'You are {(price_ratio-1)*100:.0f}% more expensive than competitors '
                   f'(${your_price:.2f} vs ${avg_competitor_price:.2f} avg) '
                   f'despite lower quality ({your_review_score:.0f}% vs {avg_competitor_score:.0f}% avg)',
            price_ratio=price_ratio,
            quality_ratio=quality_ratio,
            recommendation=f'Either lower price to ${avg_competitor_price * 1.1:.2f} or improve quality to justify ${your_price:.2f} premium'
        )

    # JUSTIFIED PREMIUM: More expensive but better quality
    if price_ratio > 1.2 and quality_ratio >= 1.1:
        return CompetitorComparison(
            issue=None,
            message=f'Premium pricing justified by superior quality: '
                   f'{(price_ratio-1)*100:.0f}% higher price, '
                   f'{(quality_ratio-1)*100:.0f}% better reviews',
            price_ratio=price_ratio,
            quality_ratio=quality_ratio,
            recommendation='Current pricing aligns with quality positioning'
        )

    # COMPETITIVE PRICING: Price aligns with quality
    return CompetitorComparison(
        issue=None,
        message=f'Pricing aligns with competitive positioning (${your_price:.2f} vs ${avg_competitor_price:.2f} avg, '
               f'{your_review_score:.0f}% vs {avg_competitor_score:.0f}% avg)',
        price_ratio=price_ratio,
        quality_ratio=quality_ratio,
        recommendation='Current pricing is competitive'
    )


def override_score_for_catastrophic_pricing(
    base_score: int,
    score_name: str,
    price_tier: PriceTier,
    actual_revenue: Optional[float] = None,
    potential_revenue: Optional[float] = None
) -> PriceOverride:
    """
    Override scores when base price is catastrophic.

    If price is $0.99, even a "perfect" regional pricing implementation gets a low score
    because the BASE PRICE is the problem, not regional pricing.

    Args:
        base_score: Original calculated score (e.g., 90 for regional pricing)
        score_name: Name of score being overridden (for messaging)
        price_tier: PriceTier classification
        actual_revenue: Actual revenue earned
        potential_revenue: Revenue potential at correct price

    Returns:
        PriceOverride with new score and explanation

    Examples:
        >>> tier = classify_price_tier(0.99)
        >>> override = override_score_for_catastrophic_pricing(90, "Regional Pricing", tier)
        >>> override.overridden_score
        15
        >>> override.was_overridden
        True
    """

    # CATASTROPHIC PRICING: Override to crisis level
    if price_tier.tier == 'catastrophic_low':
        lost_revenue = (potential_revenue - actual_revenue) if (potential_revenue and actual_revenue) else None

        warning = f"""🚨 CATASTROPHIC PRICING ERROR

Your base price is DESTROYING your revenue potential.

**The Reality:**
- Your {score_name} score was {base_score}/100
- BUT: Your ${price_tier.recommended_min}-${price_tier.recommended_max} BASE PRICE is catastrophic
- No amount of {score_name.lower()} optimization can fix a broken base price

**Why This Matters:**
A $0.99-$1.99 price signals to players:
- "This is shovelware or an asset flip"
- "The developer has no confidence in their game"
- "This game is worth less than a coffee"

Result: {abs(price_tier.impact_on_sales)}% revenue loss from price-conscious AND quality-conscious buyers.

**IMMEDIATE ACTION REQUIRED:**

1. **Increase base price to ${price_tier.recommended_min}-${price_tier.recommended_max}**
   - This is the #1 priority
   - Do this BEFORE any other optimizations

2. **Then optimize {score_name.lower()}**
   - After fixing base price, THEN work on regional pricing
   - After fixing base price, THEN work on sales strategy

3. **Understand the market psychology:**
   - Indie games at $10-15 sell BETTER than at $0.99
   - Players associate low price with low quality
   - You're leaving 70%+ of potential revenue on the table

**Lost Revenue Impact:**"""

        if lost_revenue:
            warning += f"\n   Estimated lost revenue: ${lost_revenue:,.0f}\n   Fix price = Recover most of this revenue"
        else:
            warning += f"\n   Impact: {abs(price_tier.impact_on_sales)}% revenue reduction\n   Your revenue could be 3-4x higher at proper pricing"

        warning += f"""

**Bottom Line:**
{score_name} optimization is useless when your base price is killing you.
Fix the foundation FIRST.
"""

        return PriceOverride(
            original_score=base_score,
            overridden_score=15,  # Force to crisis level
            was_overridden=True,
            reason=f'Base price is catastrophic - {score_name.lower()} cannot compensate for broken pricing',
            warning=warning,
            lost_revenue=lost_revenue
        )

    # PROBLEMATIC LOW PRICING: Cap score at 50
    elif price_tier.tier == 'too_low':
        adjusted_score = min(base_score, 50)
        was_overridden = adjusted_score < base_score

        if was_overridden:
            warning = f"""⚠️ PRICING WARNING

Your ${price_tier.recommended_min}-${price_tier.recommended_max} base price is limiting {score_name.lower()} effectiveness.

**Current Situation:**
- {score_name} score: {base_score}/100 → {adjusted_score}/100 (capped)
- Base price is too low: {price_tier.message}
- Impact: {abs(price_tier.impact_on_sales)}% revenue loss

**Why The Cap:**
Even excellent {score_name.lower()} implementation is constrained by a weak base price.
Your score is capped at {adjusted_score}/100 until base pricing improves.

**Recommendation:**
Increase base price to ${price_tier.recommended_min}-${price_tier.recommended_max} to unlock full {score_name.lower()} potential.
"""
        else:
            warning = None

        return PriceOverride(
            original_score=base_score,
            overridden_score=adjusted_score,
            was_overridden=was_overridden,
            reason='Base price is too low - limits effectiveness of pricing optimizations' if was_overridden else None,
            warning=warning
        )

    # ACCEPTABLE LOW: Minor penalty
    elif price_tier.tier == 'acceptable_low':
        adjusted_score = min(base_score, 75)
        was_overridden = adjusted_score < base_score

        warning = None
        if was_overridden:
            warning = f"Note: {score_name} score capped at {adjusted_score}/100 due to low base price. " \
                     f"Increase to ${price_tier.recommended_min}+ to unlock full potential."

        return PriceOverride(
            original_score=base_score,
            overridden_score=adjusted_score,
            was_overridden=was_overridden,
            reason='Base price is acceptable but low - minor score cap applied' if was_overridden else None,
            warning=warning
        )

    # OPTIMAL/PREMIUM/TOO HIGH: No override needed
    else:
        return PriceOverride(
            original_score=base_score,
            overridden_score=base_score,
            was_overridden=False,
            reason=None,
            warning=None
        )


def analyze_price_comprehensive(
    price_usd: float,
    review_score: float,
    revenue: float,
    units_sold: int,
    competitor_prices: Optional[List[float]] = None,
    competitor_review_scores: Optional[List[float]] = None,
    genre_tags: Optional[List[str]] = None,
    is_early_access: bool = False
) -> Dict[str, Any]:
    """
    Comprehensive price analysis combining all checks.

    Args:
        price_usd: Current price
        review_score: Review percentage
        revenue: Actual revenue
        units_sold: Units sold
        competitor_prices: List of competitor prices
        competitor_review_scores: List of competitor review scores
        genre_tags: Genre tags
        is_early_access: Early access flag

    Returns:
        Dict with complete analysis
    """

    # Step 1: Classify price tier
    price_tier = classify_price_tier(price_usd, genre_tags, is_early_access)

    # Step 2: Compare to competitors (if data available)
    competitor_comparison = None
    if competitor_prices and competitor_review_scores:
        competitor_comparison = compare_to_competitors(
            your_price=price_usd,
            your_review_score=review_score,
            competitor_prices=competitor_prices,
            competitor_review_scores=competitor_review_scores,
            estimated_units_sold=units_sold
        )

    # Step 3: Calculate potential revenue at optimal price
    potential_price = None
    potential_revenue = None

    if price_tier.recommended_min and price_tier.recommended_max:
        # Use midpoint of recommended range
        potential_price = (price_tier.recommended_min + price_tier.recommended_max) / 2
        # Assume 20% lower volume at higher price (conservative)
        potential_units = units_sold * 0.8
        potential_revenue = potential_price * potential_units

    elif competitor_comparison and competitor_comparison.issue == 'severe_underpricing':
        # Use competitive price
        avg_competitor_price = statistics.mean(competitor_prices)
        potential_price = avg_competitor_price * 0.8
        potential_units = units_sold * 0.85
        potential_revenue = potential_price * potential_units

    # Step 4: Log analysis
    logger.info(f"Price Analysis: ${price_usd:.2f} classified as '{price_tier.tier}'")
    if price_tier.severity:
        logger.warning(f"Price severity: {price_tier.severity} - {price_tier.message}")
    if competitor_comparison and competitor_comparison.issue:
        logger.warning(f"Competitor comparison: {competitor_comparison.issue}")

    return {
        'price_tier': price_tier,
        'competitor_comparison': competitor_comparison,
        'potential_price': potential_price,
        'potential_revenue': potential_revenue,
        'lost_revenue': (potential_revenue - revenue) if potential_revenue else None,
        'is_critical': price_tier.severity == 'CRITICAL',
        'requires_immediate_action': price_tier.tier in ['catastrophic_low', 'too_low']
    }


# ============================================================================
# TESTING
# ============================================================================

def test_catastrophic_pricing():
    """Test with $0.99 game"""
    print("\n" + "="*80)
    print("PRICE ANALYSIS TEST: Catastrophic Pricing ($0.99)")
    print("="*80 + "\n")

    # $0.99 game with good reviews
    price = 0.99
    review_score = 80.0
    revenue = 375  # 380 units * $0.99
    units_sold = 380

    # Competitors priced properly
    competitor_prices = [12.99, 14.99, 9.99, 11.99]
    competitor_review_scores = [75.0, 78.0, 72.0, 77.0]

    print("INPUT:")
    print(f"  Your Price: ${price}")
    print(f"  Your Review Score: {review_score}%")
    print(f"  Your Revenue: ${revenue:,.0f} ({units_sold} units)")
    print(f"  Competitor Avg Price: ${statistics.mean(competitor_prices):.2f}")
    print(f"  Competitor Avg Score: {statistics.mean(competitor_review_scores):.0f}%")
    print()

    # Comprehensive analysis
    analysis = analyze_price_comprehensive(
        price_usd=price,
        review_score=review_score,
        revenue=revenue,
        units_sold=units_sold,
        competitor_prices=competitor_prices,
        competitor_review_scores=competitor_review_scores
    )

    print("PRICE TIER:")
    tier = analysis['price_tier']
    print(f"  Classification: {tier.tier}")
    print(f"  Severity: {tier.severity}")
    print(f"  Message: {tier.message}")
    print(f"  Recommended: ${tier.recommended_min}-${tier.recommended_max}")
    print(f"  Impact on Sales: {tier.impact_on_sales}%")
    print(f"  Is Viable: {tier.is_viable}")
    print()

    print("COMPETITOR COMPARISON:")
    comp = analysis['competitor_comparison']
    print(f"  Issue: {comp.issue}")
    print(f"  Price Ratio: {comp.price_ratio:.2f}x (you / competitors)")
    print(f"  Quality Ratio: {comp.quality_ratio:.2f}x (you / competitors)")
    print(f"  Lost Revenue: ${comp.lost_revenue_estimate:,.0f}" if comp.lost_revenue_estimate else "  Lost Revenue: N/A")
    print(f"  Message: {comp.message}")
    print(f"  Recommendation: {comp.recommendation}")
    print()

    print("POTENTIAL AT CORRECT PRICE:")
    print(f"  Optimal Price: ${analysis['potential_price']:.2f}")
    print(f"  Potential Revenue: ${analysis['potential_revenue']:,.0f}")
    print(f"  Lost Revenue: ${analysis['lost_revenue']:,.0f}")
    print(f"  Revenue Multiplier: {analysis['potential_revenue'] / revenue:.1f}x")
    print()

    # Test score override
    print("SCORE OVERRIDE TEST:")
    print("  Scenario: Regional pricing scored 90/100")
    print()

    override = override_score_for_catastrophic_pricing(
        base_score=90,
        score_name="Regional Pricing",
        price_tier=tier,
        actual_revenue=revenue,
        potential_revenue=analysis['potential_revenue']
    )

    print(f"  Original Score: {override.original_score}/100")
    print(f"  Overridden Score: {override.overridden_score}/100")
    print(f"  Was Overridden: {override.was_overridden}")
    print(f"  Reason: {override.reason}")
    print()

    if override.warning:
        print("  WARNING MESSAGE:")
        print("  " + "\n  ".join(override.warning.split('\n')))
    print()

    print("="*80)
    print("VERIFICATION:")
    print(f"  ✅ Price classified as catastrophic: {tier.tier == 'catastrophic_low'}")
    print(f"  ✅ Score overridden to crisis level: {override.overridden_score == 15}")
    print(f"  ✅ Lost revenue calculated: ${analysis['lost_revenue']:,.0f}")
    print(f"  ✅ Warning generated: {override.warning is not None}")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_catastrophic_pricing()
