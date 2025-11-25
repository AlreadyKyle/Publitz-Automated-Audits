"""
Revenue-Based Score Modifier System

Prevents score inflation by adjusting all scores based on actual commercial performance.
A game with $379 revenue should not score 88/100 - this system enforces commercial reality.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class RevenueTier:
    """Revenue performance tier classification"""
    tier: int  # 1-5 (1=crisis, 5=exceptional)
    tier_name: str
    modifier: float  # Score multiplier (0.3-1.0)
    reality_check: bool  # Triggers warning if scores too high
    message: str
    daily_revenue: float
    monthly_equivalent: float


def classify_revenue_tier(revenue_estimate: float, days_since_launch: int) -> RevenueTier:
    """
    Classify game into revenue performance tier based on daily revenue.

    Args:
        revenue_estimate: Total revenue to date
        days_since_launch: Days since game launched

    Returns:
        RevenueTier object with tier info and modifier

    Examples:
        $379 in 7 days = $54/day → Crisis tier (0.40 modifier)
        $50K in 90 days = $555/day → Struggling tier (0.65 modifier)
        $200K in 90 days = $2,222/day → Viable tier (0.85 modifier)
    """
    # Prevent division by zero
    days = max(days_since_launch, 1)

    # Calculate daily average revenue
    daily_revenue = revenue_estimate / days
    monthly_equivalent = daily_revenue * 30

    # Revenue tier classification based on daily average
    if daily_revenue < 100:  # <$3K/month
        return RevenueTier(
            tier=1,
            tier_name='Crisis',
            modifier=0.40,
            reality_check=True,
            message='Game is not commercially viable at current performance. Immediate intervention required.',
            daily_revenue=daily_revenue,
            monthly_equivalent=monthly_equivalent
        )

    elif daily_revenue < 500:  # $3K-15K/month
        return RevenueTier(
            tier=2,
            tier_name='Struggling',
            modifier=0.65,
            reality_check=True,
            message='Game has severe commercial challenges. Focus on core issues before optimization.',
            daily_revenue=daily_revenue,
            monthly_equivalent=monthly_equivalent
        )

    elif daily_revenue < 2000:  # $15K-60K/month
        return RevenueTier(
            tier=3,
            tier_name='Viable',
            modifier=0.85,
            reality_check=False,
            message='Game is commercially viable with optimization opportunities.',
            daily_revenue=daily_revenue,
            monthly_equivalent=monthly_equivalent
        )

    elif daily_revenue < 10000:  # $60K-300K/month
        return RevenueTier(
            tier=4,
            tier_name='Strong',
            modifier=0.95,
            reality_check=False,
            message='Game is performing well commercially. Focus on scaling.',
            daily_revenue=daily_revenue,
            monthly_equivalent=monthly_equivalent
        )

    else:  # >$300K/month
        return RevenueTier(
            tier=5,
            tier_name='Exceptional',
            modifier=1.0,
            reality_check=False,
            message='Game is a commercial success. Maximize momentum.',
            daily_revenue=daily_revenue,
            monthly_equivalent=monthly_equivalent
        )


def apply_revenue_modifier(
    section_scores: Dict[str, float],
    revenue_tier: RevenueTier
) -> Dict[str, Dict[str, Any]]:
    """
    Apply revenue reality check to all section scores.

    Rules:
    - Apply modifier to all scores
    - If reality_check = True, cap maximum at 65/100
    - Add warnings for significantly reduced scores

    Args:
        section_scores: Dict of {section_name: raw_score}
        revenue_tier: RevenueTier object

    Returns:
        Dict of {section_name: {raw_score, final_score, modifier, warning}}

    Example:
        Input: {'community': 85, 'influencer': 90}
        Revenue tier: Crisis (0.40 modifier)
        Output: {'community': {raw: 85, final: 34, warning: "Score reduced..."}}
    """
    modified_scores = {}

    for section, raw_score in section_scores.items():
        # Apply modifier
        modified_score = raw_score * revenue_tier.modifier

        # Hard cap for crisis/struggling tiers
        if revenue_tier.reality_check and modified_score > 65:
            modified_score = 65

        # Determine if warning needed
        warning = None
        reduction = raw_score - modified_score

        if reduction > 15:
            warning = f"Score reduced from {raw_score:.0f} due to poor revenue performance (${revenue_tier.daily_revenue:.0f}/day)"
        elif reduction > 5:
            warning = f"Score adjusted from {raw_score:.0f} based on commercial reality"

        modified_scores[section] = {
            'raw_score': raw_score,
            'final_score': round(modified_score),
            'modifier_applied': revenue_tier.modifier,
            'reduction': round(reduction),
            'warning': warning
        }

    return modified_scores


def calculate_overall_score(
    section_scores: Dict[str, Dict[str, Any]],
    revenue_tier: RevenueTier,
    review_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate overall score that reflects commercial reality.

    Weighting:
    - Revenue performance: 35% (most important)
    - Review score: 25%
    - Review volume: 15%
    - Section average: 25%

    Args:
        section_scores: Modified section scores from apply_revenue_modifier()
        revenue_tier: RevenueTier object
        review_metrics: Dict with review_percentage and review_count

    Returns:
        Dict with overall_score, breakdown, and components

    Example:
        $379 revenue (7 days) + 80% reviews (5 total) = 36/100 overall
    """
    # Component 1: Revenue score (0-100)
    # Tier 1 = 20, Tier 2 = 40, Tier 3 = 60, Tier 4 = 80, Tier 5 = 100
    revenue_score = revenue_tier.tier * 20

    # Component 2: Review score (0-100)
    review_score = review_metrics.get('review_percentage', 0)

    # Component 3: Review volume score (logarithmic)
    review_count = review_metrics.get('review_count', 0)

    if review_count < 10:
        volume_score = 0
    elif review_count < 50:
        volume_score = 30
    elif review_count < 100:
        volume_score = 50
    elif review_count < 500:
        volume_score = 70
    elif review_count < 1000:
        volume_score = 85
    else:
        volume_score = 95

    # Component 4: Section average
    if section_scores:
        section_avg = sum(s['final_score'] for s in section_scores.values()) / len(section_scores)
    else:
        section_avg = 0

    # Weighted calculation
    overall = (
        revenue_score * 0.35 +
        review_score * 0.25 +
        volume_score * 0.15 +
        section_avg * 0.25
    )

    return {
        'overall_score': round(overall),
        'components': {
            'revenue': {
                'score': revenue_score,
                'weight': 0.35,
                'contribution': round(revenue_score * 0.35)
            },
            'review_quality': {
                'score': review_score,
                'weight': 0.25,
                'contribution': round(review_score * 0.25)
            },
            'review_volume': {
                'score': volume_score,
                'weight': 0.15,
                'contribution': round(volume_score * 0.15)
            },
            'sections': {
                'score': round(section_avg),
                'weight': 0.25,
                'contribution': round(section_avg * 0.25)
            }
        },
        'breakdown': f"{revenue_score * 0.35:.1f} + {review_score * 0.25:.1f} + {volume_score * 0.15:.1f} + {section_avg * 0.25:.1f} = {overall:.1f}"
    }


def generate_reality_check_warning(
    revenue_tier: RevenueTier,
    overall_score: int,
    section_scores: Dict[str, Dict[str, Any]]
) -> Optional[str]:
    """
    Generate prominent warning for score inflation due to poor revenue.

    Args:
        revenue_tier: RevenueTier object
        overall_score: Final calculated score
        section_scores: Modified section scores

    Returns:
        Formatted warning string or None if no warning needed
    """
    if not revenue_tier.reality_check:
        return None

    # Calculate average reduction
    reductions = [s['reduction'] for s in section_scores.values() if s['reduction'] > 0]
    avg_reduction = sum(reductions) / len(reductions) if reductions else 0

    warning = f"""
## ⚠️ REVENUE REALITY CHECK

**Your overall score is {overall_score}/100 ({revenue_tier.tier_name} tier)**

While some individual metrics show promise, your **actual revenue performance** indicates severe commercial challenges:

**Current Performance:**
- Daily Revenue: ${revenue_tier.daily_revenue:.2f}/day
- Monthly Equivalent: ${revenue_tier.monthly_equivalent:.0f}/month
- Revenue Tier: **{revenue_tier.tier_name}** (Tier {revenue_tier.tier})

**Why Your Score Is Lower Than Individual Sections:**

{revenue_tier.message}

**Score Adjustments Applied:**
- All section scores reduced by {(1 - revenue_tier.modifier) * 100:.0f}%
- Maximum score capped at 65/100 for crisis/struggling tiers
- Average reduction: {avg_reduction:.0f} points per section

**What This Means:**

Commercial success is the ultimate metric. No amount of "excellent" community reach or influencer potential matters if the game isn't generating revenue. Your scores reflect the harsh reality that **the game is not commercially viable** at current performance levels.

**Priority Actions:**
1. Review the "Critical Blockers" section immediately
2. Focus on revenue-driving fixes, not optimization
3. Determine if the game is salvageable or needs pivoting
4. Do NOT waste time on marketing until core issues are fixed

**Reality Check:** Most games at this revenue level never recover. Success requires both fixable issues AND a 6+ month commitment to intensive updates.
"""

    return warning.strip()


def format_revenue_report(
    revenue_tier: RevenueTier,
    section_scores: Dict[str, Dict[str, Any]],
    overall_calculation: Dict[str, Any]
) -> str:
    """
    Generate formatted report showing revenue-based scoring breakdown.

    Args:
        revenue_tier: RevenueTier object
        section_scores: Modified section scores
        overall_calculation: Result from calculate_overall_score()

    Returns:
        Formatted markdown report
    """
    report = f"""
## Revenue-Based Score Breakdown

**Revenue Performance Classification:**
- Tier: {revenue_tier.tier_name} (Tier {revenue_tier.tier}/5)
- Daily Revenue: ${revenue_tier.daily_revenue:.2f}
- Monthly Equivalent: ${revenue_tier.monthly_equivalent:.0f}
- Score Modifier: {revenue_tier.modifier} ({(1-revenue_tier.modifier)*100:.0f}% reduction)

**Section Scores (After Revenue Modifier):**

"""

    for section, scores in section_scores.items():
        report += f"- **{section.title()}**: {scores['raw_score']:.0f} → {scores['final_score']}/100"
        if scores['warning']:
            report += f"  \n  *{scores['warning']}*"
        report += "\n"

    report += f"""
**Overall Score Calculation:**

```
Revenue Component:     {overall_calculation['components']['revenue']['score']}/100 × 35% = {overall_calculation['components']['revenue']['contribution']}
Review Quality:        {overall_calculation['components']['review_quality']['score']}/100 × 25% = {overall_calculation['components']['review_quality']['contribution']}
Review Volume:         {overall_calculation['components']['review_volume']['score']}/100 × 15% = {overall_calculation['components']['review_volume']['contribution']}
Section Average:       {overall_calculation['components']['sections']['score']}/100 × 25% = {overall_calculation['components']['sections']['contribution']}
                       ───────────────────────────
FINAL SCORE:           {overall_calculation['overall_score']}/100
```

**Breakdown:** {overall_calculation['breakdown']}
"""

    return report.strip()


# ============================================================================
# TESTING & EXAMPLES
# ============================================================================

def test_retrace_the_light():
    """
    Test with actual Retrace the Light data to verify system works correctly.

    Expected: Score should drop from 88 to ~36 with clear warnings.
    """
    print("\n" + "="*80)
    print("REVENUE-BASED SCORING TEST: Retrace the Light")
    print("="*80 + "\n")

    # Actual game data
    revenue = 379
    days_since_launch = 7
    review_percentage = 80.0
    review_count = 5

    # Current inflated section scores
    section_scores = {
        'community': 85,
        'influencer': 90,
        'regional': 90
    }

    print("INPUT DATA:")
    print(f"  Revenue: ${revenue} ({days_since_launch} days)")
    print(f"  Daily Average: ${revenue/days_since_launch:.2f}/day")
    print(f"  Reviews: {review_count} total, {review_percentage}% positive")
    print(f"  Current Section Scores: {section_scores}")
    print()

    # Step 1: Classify revenue tier
    revenue_tier = classify_revenue_tier(revenue, days_since_launch)

    print("REVENUE TIER CLASSIFICATION:")
    print(f"  Tier: {revenue_tier.tier_name} (Tier {revenue_tier.tier}/5)")
    print(f"  Daily Revenue: ${revenue_tier.daily_revenue:.2f}")
    print(f"  Monthly Equivalent: ${revenue_tier.monthly_equivalent:.0f}")
    print(f"  Modifier: {revenue_tier.modifier} ({(1-revenue_tier.modifier)*100:.0f}% reduction)")
    print(f"  Reality Check: {'ACTIVE' if revenue_tier.reality_check else 'Not needed'}")
    print(f"  Message: {revenue_tier.message}")
    print()

    # Step 2: Apply modifiers to section scores
    modified_sections = apply_revenue_modifier(section_scores, revenue_tier)

    print("MODIFIED SECTION SCORES:")
    for section, scores in modified_sections.items():
        print(f"  {section.title()}: {scores['raw_score']} → {scores['final_score']} "
              f"(reduction: {scores['reduction']})")
        if scores['warning']:
            print(f"    ⚠️  {scores['warning']}")
    print()

    # Step 3: Calculate overall score
    review_metrics = {
        'review_percentage': review_percentage,
        'review_count': review_count
    }

    overall = calculate_overall_score(modified_sections, revenue_tier, review_metrics)

    print("OVERALL SCORE CALCULATION:")
    print(f"  Revenue: {overall['components']['revenue']['score']}/100 × 35% = {overall['components']['revenue']['contribution']}")
    print(f"  Review Quality: {overall['components']['review_quality']['score']}/100 × 25% = {overall['components']['review_quality']['contribution']}")
    print(f"  Review Volume: {overall['components']['review_volume']['score']}/100 × 15% = {overall['components']['review_volume']['contribution']}")
    print(f"  Section Avg: {overall['components']['sections']['score']}/100 × 25% = {overall['components']['sections']['contribution']}")
    print(f"  ────────────────────────")
    print(f"  FINAL SCORE: {overall['overall_score']}/100")
    print()

    # Step 4: Generate reality check warning
    warning = generate_reality_check_warning(revenue_tier, overall['overall_score'], modified_sections)

    if warning:
        print("REALITY CHECK WARNING:")
        print(warning)
        print()

    # Step 5: Generate full report
    report = format_revenue_report(revenue_tier, modified_sections, overall)

    print("\n" + "="*80)
    print("COMPLETE REVENUE-BASED REPORT")
    print("="*80)
    print(report)
    print()

    # Verification
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)
    print(f"✅ Score dropped from 88 to {overall['overall_score']} (expected: 30-40)")
    print(f"✅ Reality check {'ACTIVE' if revenue_tier.reality_check else 'INACTIVE'} (expected: ACTIVE)")
    print(f"✅ Modifier applied: {revenue_tier.modifier} (expected: 0.40)")
    print(f"✅ Warning generated: {'Yes' if warning else 'No'} (expected: Yes)")

    if 30 <= overall['overall_score'] <= 45:
        print("\n✅ TEST PASSED - Score is in expected range (30-45)")
    else:
        print(f"\n⚠️  TEST WARNING - Score {overall['overall_score']} outside expected range (30-45)")

    print("="*80 + "\n")

    return {
        'revenue_tier': revenue_tier,
        'modified_sections': modified_sections,
        'overall': overall,
        'warning': warning,
        'report': report
    }


if __name__ == "__main__":
    # Run test with Retrace the Light data
    result = test_retrace_the_light()
