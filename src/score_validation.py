"""
Score Validation and Hard Cap System

Ensures that overall scores can NEVER exceed what revenue/reviews actually justify.
No game with $379 revenue and 5 reviews should ever score above 50/100.

This system enforces commercial reality through hard caps based on:
- Daily revenue performance
- Review volume (data sufficiency)
- Review quality (player satisfaction)

The final score is capped at the MINIMUM of all three caps.
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class GameMetrics:
    """Core metrics for validation"""
    revenue: float
    days_since_launch: int
    review_count_total: int
    review_percentage: float
    owner_count: Optional[int] = None

    @property
    def daily_revenue(self) -> float:
        """Calculate average daily revenue"""
        return self.revenue / max(self.days_since_launch, 1)


@dataclass
class ScoreCaps:
    """Hard caps for score validation"""
    revenue_cap: int
    revenue_reason: str
    review_volume_cap: int
    review_volume_reason: str
    review_quality_cap: int
    review_quality_reason: str
    maximum_score: int
    limiting_factor: str
    limiting_reason: str


def calculate_maximum_possible_score(game_metrics: GameMetrics) -> ScoreCaps:
    """
    Calculate the absolute maximum score a game can receive based on reality.

    The final cap is the MINIMUM of all three caps (revenue, review volume, review quality).
    This prevents games from scoring high on speculation when actual performance is poor.

    Args:
        game_metrics: GameMetrics object with revenue, reviews, etc.

    Returns:
        ScoreCaps object with maximum score and reasoning

    Examples:
        >>> # Retrace the Light: $379 (7 days), 5 reviews, 80%
        >>> metrics = GameMetrics(revenue=379, days_since_launch=7,
        ...                        review_count_total=5, review_percentage=80.0)
        >>> caps = calculate_maximum_possible_score(metrics)
        >>> caps.maximum_score
        40  # Capped by revenue ($54/day = crisis tier)
    """

    caps = {}

    # ========================================================================
    # CAP 1: REVENUE-BASED CAP (Commercial Reality)
    # ========================================================================
    daily_revenue = game_metrics.daily_revenue

    if daily_revenue < 100:
        # Crisis tier: Not commercially viable
        caps['revenue_cap'] = 40
        caps['revenue_reason'] = f"Daily revenue ${daily_revenue:.0f}/day (under $100 = crisis tier)"
    elif daily_revenue < 500:
        # Struggling: Severe commercial challenges
        caps['revenue_cap'] = 60
        caps['revenue_reason'] = f"Daily revenue ${daily_revenue:.0f}/day (under $500 = struggling)"
    elif daily_revenue < 2000:
        # Viable: Has potential
        caps['revenue_cap'] = 75
        caps['revenue_reason'] = f"Daily revenue ${daily_revenue:.0f}/day (under $2K = viable)"
    elif daily_revenue < 10000:
        # Strong: Performing well
        caps['revenue_cap'] = 90
        caps['revenue_reason'] = f"Daily revenue ${daily_revenue:.0f}/day ($2K-10K = strong)"
    else:
        # Exceptional: Commercial success
        caps['revenue_cap'] = 100
        caps['revenue_reason'] = f"Daily revenue ${daily_revenue:.0f}/day (>$10K = exceptional)"

    # ========================================================================
    # CAP 2: REVIEW VOLUME CAP (Data Sufficiency)
    # ========================================================================
    review_count = game_metrics.review_count_total

    if review_count < 10:
        # Insufficient data for reliable assessment
        caps['review_volume_cap'] = 45
        caps['review_volume_reason'] = f"{review_count} reviews (under 10 = insufficient data)"
    elif review_count < 50:
        # Limited validation
        caps['review_volume_cap'] = 65
        caps['review_volume_reason'] = f"{review_count} reviews (under 50 = limited validation)"
    elif review_count < 100:
        # Early stage but meaningful
        caps['review_volume_cap'] = 80
        caps['review_volume_reason'] = f"{review_count} reviews (under 100 = early stage)"
    elif review_count < 500:
        # Well-validated
        caps['review_volume_cap'] = 90
        caps['review_volume_reason'] = f"{review_count} reviews (100-500 = well-validated)"
    else:
        # Extensively validated
        caps['review_volume_cap'] = 100
        caps['review_volume_reason'] = f"{review_count} reviews (>500 = extensive validation)"

    # ========================================================================
    # CAP 3: REVIEW QUALITY CAP (Player Satisfaction)
    # ========================================================================
    review_pct = game_metrics.review_percentage

    if review_pct < 70:
        # Quality issues evident
        caps['review_quality_cap'] = 50
        caps['review_quality_reason'] = f"{review_pct:.0f}% positive (under 70% = quality issues)"
    elif review_pct < 80:
        # Mixed reception
        caps['review_quality_cap'] = 70
        caps['review_quality_reason'] = f"{review_pct:.0f}% positive (under 80% = mixed reception)"
    elif review_pct < 90:
        # Good reception
        caps['review_quality_cap'] = 85
        caps['review_quality_reason'] = f"{review_pct:.0f}% positive (80-90% = good reception)"
    else:
        # Excellent reception
        caps['review_quality_cap'] = 100
        caps['review_quality_reason'] = f"{review_pct:.0f}% positive (>90% = excellent reception)"

    # ========================================================================
    # DETERMINE OVERALL CAP (Minimum of all caps)
    # ========================================================================
    overall_cap = min(
        caps['revenue_cap'],
        caps['review_volume_cap'],
        caps['review_quality_cap']
    )

    # Identify which metric is most limiting
    if overall_cap == caps['revenue_cap']:
        limiting_factor = 'revenue'
        limiting_reason = caps['revenue_reason']
    elif overall_cap == caps['review_volume_cap']:
        limiting_factor = 'review_volume'
        limiting_reason = caps['review_volume_reason']
    else:
        limiting_factor = 'review_quality'
        limiting_reason = caps['review_quality_reason']

    logger.info(f"Score caps calculated: Revenue={caps['revenue_cap']}, "
                f"Volume={caps['review_volume_cap']}, Quality={caps['review_quality_cap']}")
    logger.info(f"Maximum possible score: {overall_cap}/100 (limited by {limiting_factor})")

    return ScoreCaps(
        revenue_cap=caps['revenue_cap'],
        revenue_reason=caps['revenue_reason'],
        review_volume_cap=caps['review_volume_cap'],
        review_volume_reason=caps['review_volume_reason'],
        review_quality_cap=caps['review_quality_cap'],
        review_quality_reason=caps['review_quality_reason'],
        maximum_score=overall_cap,
        limiting_factor=limiting_factor,
        limiting_reason=limiting_reason
    )


def enforce_score_cap(calculated_score: int, caps: ScoreCaps, game_metrics: GameMetrics) -> Dict[str, Any]:
    """
    Force score under cap and explain why.

    If the calculated score exceeds the maximum possible score based on reality,
    this function caps it and provides detailed explanation.

    Args:
        calculated_score: The score calculated by normal scoring logic
        caps: ScoreCaps object from calculate_maximum_possible_score()
        game_metrics: GameMetrics object for improvement path

    Returns:
        Dict with final_score, was_capped, and explanation

    Examples:
        >>> # Game calculated 88/100 but reality says max 40/100
        >>> result = enforce_score_cap(88, caps, metrics)
        >>> result['final_score']
        40
        >>> result['was_capped']
        True
    """

    if calculated_score <= caps.maximum_score:
        logger.info(f"Score {calculated_score}/100 within cap of {caps.maximum_score}/100")
        return {
            'final_score': calculated_score,
            'was_capped': False,
            'original_score': calculated_score,
            'maximum_possible': caps.maximum_score,
            'caps_detail': caps
        }

    # Score exceeds what reality justifies - enforce cap
    logger.warning(f"Score capped: {calculated_score}/100 → {caps.maximum_score}/100 "
                   f"(limited by {caps.limiting_factor})")

    return {
        'final_score': caps.maximum_score,
        'was_capped': True,
        'original_score': calculated_score,
        'maximum_possible': caps.maximum_score,
        'reduction': calculated_score - caps.maximum_score,
        'cap_explanation': f"Score capped at {caps.maximum_score}/100 due to {caps.limiting_factor}: {caps.limiting_reason}",
        'improvement_path': generate_improvement_path(caps, game_metrics),
        'caps_detail': caps
    }


def generate_improvement_path(caps: ScoreCaps, game_metrics: GameMetrics) -> str:
    """
    Tell developer exactly what to fix to raise their cap.

    Args:
        caps: ScoreCaps object showing current limitations
        game_metrics: GameMetrics for current performance

    Returns:
        Formatted markdown string with improvement guidance
    """

    bottleneck = caps.limiting_factor

    if bottleneck == 'revenue':
        # Determine next revenue threshold
        daily_rev = game_metrics.daily_revenue
        if daily_rev < 100:
            next_threshold = "$100/day"
            new_cap = 60
        elif daily_rev < 500:
            next_threshold = "$500/day"
            new_cap = 75
        elif daily_rev < 2000:
            next_threshold = "$2,000/day"
            new_cap = 90
        else:
            next_threshold = "$10,000/day"
            new_cap = 100

        return f"""
**To raise your score above {caps.maximum_score}/100:**

Your score is limited by revenue performance. Current: ${daily_rev:.0f}/day

**Immediate Goal:** Reach {next_threshold} to unlock {new_cap}/100 cap

**Action Plan:**
1. Review "Critical Blockers" section for revenue-killing issues
2. Fix core gameplay/quality problems before marketing
3. Optimize pricing and visibility on Steam
4. Track daily revenue and iterate on fixes

**Reality Check:** Most games at this revenue level never recover. Focus on whether the game is salvageable before investing more time.
"""

    elif bottleneck == 'review_volume':
        # Determine next review threshold
        review_count = game_metrics.review_count_total
        if review_count < 10:
            next_threshold = "10 reviews"
            new_cap = 65
        elif review_count < 50:
            next_threshold = "50 reviews"
            new_cap = 80
        elif review_count < 100:
            next_threshold = "100 reviews"
            new_cap = 90
        else:
            next_threshold = "500 reviews"
            new_cap = 100

        return f"""
**To raise your score above {caps.maximum_score}/100:**

Your score is limited by insufficient review data. Current: {review_count} reviews

**Immediate Goal:** Reach {next_threshold} to unlock {new_cap}/100 cap

**Action Plan:**
1. Focus on player outreach and community building
2. Implement review prompts at natural engagement points (NOT manipulative)
3. Engage with streamers/content creators for exposure
4. Ensure game quality justifies asking for reviews

**Warning:** Do NOT artificially inflate reviews. Focus on genuine player acquisition.
"""

    else:  # review_quality
        # Determine next quality threshold
        review_pct = game_metrics.review_percentage
        if review_pct < 70:
            next_threshold = "70%"
            new_cap = 70
        elif review_pct < 80:
            next_threshold = "80%"
            new_cap = 85
        else:
            next_threshold = "90%"
            new_cap = 100

        return f"""
**To raise your score above {caps.maximum_score}/100:**

Your score is limited by player satisfaction. Current: {review_pct:.0f}% positive

**Immediate Goal:** Reach {next_threshold} positive to unlock {new_cap}/100 cap

**Action Plan:**
1. Analyze negative reviews for common complaints (see Negative Review Analysis section)
2. Fix top 3 most-mentioned issues immediately
3. Respond to negative reviews showing you're listening
4. Update game and announce fixes to community

**Reality Check:** Raising review scores requires fixing actual problems, not marketing. See "Critical Blockers" for fix-it recommendations.
"""


def validate_before_generation(game_metrics: GameMetrics) -> Tuple[bool, str]:
    """
    Check if report generation is even appropriate.

    Prevents generating reports for games with literally zero data,
    which would be 90% speculation.

    Args:
        game_metrics: GameMetrics object

    Returns:
        Tuple of (should_generate: bool, warning_message: str)

    Examples:
        >>> # Game with 0 reviews and 30 owners
        >>> metrics = GameMetrics(revenue=0, days_since_launch=5,
        ...                        review_count_total=0, review_percentage=0, owner_count=30)
        >>> should_generate, msg = validate_before_generation(metrics)
        >>> should_generate
        False
    """

    # Check for literally zero market validation
    if game_metrics.review_count_total == 0 and (game_metrics.owner_count or 0) < 50:
        warning = """
⚠️  INSUFFICIENT DATA FOR MEANINGFUL AUDIT

This game has insufficient data for a reliable audit:
- **0 reviews** (need at least 10 for basic analysis)
- **Under 50 owners** (insufficient market validation)
- **No commercial performance data**

**Why This Matters:**
An audit with this little data would be 90% speculation based on store page metadata.
The recommendations would lack validation from actual player behavior.

**RECOMMENDATION:**
1. Complete your first 30 days post-launch
2. Reach at least 10 reviews (preferably 50+)
3. Then request an audit for actionable insights

**Alternative:**
If you need pre-launch advice, consider:
- Store page optimization review
- Pricing strategy consultation
- Launch planning guidance

These services analyze planning/positioning rather than performance data.
"""
        logger.warning("Insufficient data for report generation: 0 reviews, <50 owners")
        return False, warning

    # Check for very early stage (warn but allow)
    if game_metrics.review_count_total < 5:
        warning = f"""
⚠️  LIMITED DATA WARNING

This game has very limited data ({game_metrics.review_count_total} reviews).
The audit will be generated but should be considered preliminary.

**Limitations:**
- Scores based on limited validation
- Recommendations may shift as more data arrives
- Some sections may lack statistical significance

**Best Used For:**
- Identifying obvious critical issues
- Early course correction
- Planning near-term improvements

Consider requesting a follow-up audit after reaching 50+ reviews.
"""
        logger.info(f"Limited data warning: only {game_metrics.review_count_total} reviews")
        return True, warning

    # Sufficient data
    logger.info(f"Data validation passed: {game_metrics.review_count_total} reviews, "
                f"${game_metrics.daily_revenue:.0f}/day")
    return True, ""


def generate_cap_explanation_report(caps: ScoreCaps, game_metrics: GameMetrics,
                                   final_score: int, was_capped: bool) -> str:
    """
    Generate detailed explanation of how caps affected the score.

    This appears in the report to explain score limitations to clients.

    Args:
        caps: ScoreCaps object
        game_metrics: GameMetrics object
        final_score: The final score after capping
        was_capped: Whether the score was reduced by caps

    Returns:
        Formatted markdown explanation
    """

    if not was_capped:
        # Score wasn't capped, but still show what the limits are
        return f"""
## Score Validation

Your overall score of **{final_score}/100** is within the maximum possible score based on your current metrics.

**Current Score Caps:**
- **Revenue Cap:** {caps.revenue_cap}/100 — {caps.revenue_reason}
- **Review Volume Cap:** {caps.review_volume_cap}/100 — {caps.review_volume_reason}
- **Review Quality Cap:** {caps.review_quality_cap}/100 — {caps.review_quality_reason}

**Maximum Possible Score:** {caps.maximum_score}/100 (limited by {caps.limiting_factor})

Your score of {final_score}/100 reflects your actual performance without artificial inflation.
"""

    # Score was capped - explain in detail
    return f"""
## ⚠️  Score Cap Applied

Your calculated score was reduced to **{final_score}/100** due to commercial reality constraints.

**Why Your Score Is Capped:**

Your game's current performance limits the maximum achievable score:

| Metric | Cap | Reason |
|--------|-----|--------|
| **Revenue** | {caps.revenue_cap}/100 | {caps.revenue_reason} |
| **Review Volume** | {caps.review_volume_cap}/100 | {caps.review_volume_reason} |
| **Review Quality** | {caps.review_quality_cap}/100 | {caps.review_quality_reason} |

**Overall Maximum:** {caps.maximum_score}/100 (limited by **{caps.limiting_factor}**)

**What This Means:**

No game can score higher than what its commercial performance justifies. Your game is currently limited by **{caps.limiting_factor}**.

Even if other metrics improve (community reach, influencer potential, etc.), your overall score cannot exceed **{caps.maximum_score}/100** until you address the limiting factor.

**How to Raise Your Cap:**

{generate_improvement_path(caps, game_metrics)}

**Philosophy:**

We enforce these caps to prevent score inflation. A game with ${game_metrics.daily_revenue:.0f}/day revenue and {game_metrics.review_count_total} reviews cannot score 80+/100 regardless of hypothetical potential. Scores must reflect **actual market performance**, not speculation.
"""


# ============================================================================
# TESTING & EXAMPLES
# ============================================================================

def test_retrace_the_light():
    """
    Test validation system with Retrace the Light data.

    Expected behavior:
    - Revenue cap: 40 ($54/day = crisis)
    - Review volume cap: 45 (5 reviews = insufficient data)
    - Review quality cap: 70 (80% positive = good)
    - Overall cap: 40 (limited by revenue)

    If calculated score is 88, it should be capped at 40.
    """
    print("\n" + "="*80)
    print("SCORE VALIDATION TEST: Retrace the Light")
    print("="*80 + "\n")

    # Actual game data
    metrics = GameMetrics(
        revenue=379,
        days_since_launch=7,
        review_count_total=5,
        review_percentage=80.0,
        owner_count=100
    )

    print("INPUT DATA:")
    print(f"  Revenue: ${metrics.revenue} ({metrics.days_since_launch} days) = ${metrics.daily_revenue:.2f}/day")
    print(f"  Reviews: {metrics.review_count_total} total, {metrics.review_percentage}% positive")
    print(f"  Owners: {metrics.owner_count}")
    print()

    # Step 1: Validate data sufficiency
    should_generate, warning = validate_before_generation(metrics)
    print(f"DATA VALIDATION: {'PASS' if should_generate else 'FAIL'}")
    if warning:
        print(f"Warning: {warning[:100]}...")
    print()

    # Step 2: Calculate caps
    caps = calculate_maximum_possible_score(metrics)

    print("CALCULATED CAPS:")
    print(f"  Revenue Cap: {caps.revenue_cap}/100 — {caps.revenue_reason}")
    print(f"  Review Volume Cap: {caps.review_volume_cap}/100 — {caps.review_volume_reason}")
    print(f"  Review Quality Cap: {caps.review_quality_cap}/100 — {caps.review_quality_reason}")
    print()
    print(f"  MAXIMUM POSSIBLE SCORE: {caps.maximum_score}/100")
    print(f"  Limiting Factor: {caps.limiting_factor}")
    print(f"  Reason: {caps.limiting_reason}")
    print()

    # Step 3: Test with inflated score
    calculated_score = 88  # What the old system would give

    print(f"SCENARIO: Calculated score is {calculated_score}/100")
    print()

    result = enforce_score_cap(calculated_score, caps, metrics)

    print("ENFORCEMENT RESULT:")
    print(f"  Original Score: {result['original_score']}/100")
    print(f"  Final Score: {result['final_score']}/100")
    print(f"  Was Capped: {result['was_capped']}")
    if result['was_capped']:
        print(f"  Reduction: {result['reduction']} points")
        print(f"  Explanation: {result['cap_explanation']}")
    print()

    # Step 4: Show improvement path
    if result['was_capped']:
        print("IMPROVEMENT PATH:")
        print(result['improvement_path'])

    # Verification
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)
    print(f"✅ Maximum cap calculated: {caps.maximum_score}/100 (expected: 40)")
    print(f"✅ Score enforced at: {result['final_score']}/100 (expected: 40)")
    print(f"✅ Was capped: {result['was_capped']} (expected: True)")
    print(f"✅ Limiting factor: {caps.limiting_factor} (expected: revenue)")

    if result['final_score'] == 40 and result['was_capped'] and caps.limiting_factor == 'revenue':
        print("\n✅ TEST PASSED - Validation system working correctly")
    else:
        print("\n⚠️  TEST WARNING - Unexpected results")

    print("="*80 + "\n")

    return result


if __name__ == "__main__":
    # Run test with Retrace the Light data
    test_retrace_the_light()
