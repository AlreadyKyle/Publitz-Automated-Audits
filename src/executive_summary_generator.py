"""
Dynamic Executive Summary Generator for Publitz Audit Reports

Generates tier-specific executive summaries based on game performance metrics.
Adapts strategy and priorities based on score ranges:
- 0-40: Crisis/recovery mode
- 40-60: Struggling with fixable issues
- 60-80: Solid performance, optimization opportunities
- 80-100: Exceptional, scaling mode
"""

from typing import Dict, Any, Tuple


def generate_executive_summary(
    overall_score: float,
    review_count: int,
    review_percentage: float,
    revenue_estimate: int,
    review_velocity_trend: str,
    genre: str
) -> str:
    """
    Generate a performance-tier-specific executive summary.

    Args:
        overall_score: Game performance score (0-100)
        review_count: Total number of Steam reviews
        review_percentage: Positive review percentage (0-100)
        revenue_estimate: Estimated revenue in dollars
        review_velocity_trend: One of "increasing", "stable", "declining"
        genre: Game genre (e.g., "Roguelike", "RPG", "Strategy")

    Returns:
        Markdown-formatted executive summary string
    """
    # Determine performance tier
    tier = _get_performance_tier(overall_score)

    # Calculate percentile ranking
    percentile = _calculate_percentile(overall_score)

    # Get tier-specific content
    bottom_line = _get_bottom_line(tier, overall_score)
    score_meaning = _get_score_meaning(tier, percentile, genre, overall_score)
    situation_numbers = _get_situation_numbers(
        revenue_estimate, review_count, review_percentage, review_velocity_trend, tier
    )
    priorities = _get_top_priorities(tier, review_percentage, review_count)
    ignore_list = _get_ignore_list(tier)
    goals_90day = _get_realistic_goals(tier, revenue_estimate, review_count)

    # Build the markdown
    summary = f"""## 1. EXECUTIVE SUMMARY

### Bottom Line

{bottom_line}

---

### What Your Score Means

{score_meaning}

---

### Your Situation in Numbers

{situation_numbers}

---

### Top 3 Priorities (Next 30 Days)

{priorities}

---

### What to Ignore (For Now)

{ignore_list}

---

### Realistic 90-Day Goals

{goals_90day}
"""

    return summary


def _get_performance_tier(score: float) -> str:
    """Determine performance tier from score."""
    if score < 40:
        return "crisis"
    elif score < 60:
        return "struggling"
    elif score < 80:
        return "solid"
    else:
        return "exceptional"


def _calculate_percentile(score: float) -> int:
    """
    Calculate approximate percentile ranking.
    Based on Steam distribution where median game scores ~55-65.
    """
    # Approximate percentile mapping
    if score >= 90:
        return 95
    elif score >= 85:
        return 90
    elif score >= 80:
        return 85
    elif score >= 75:
        return 75
    elif score >= 70:
        return 65
    elif score >= 65:
        return 55
    elif score >= 60:
        return 45
    elif score >= 55:
        return 35
    elif score >= 50:
        return 25
    elif score >= 40:
        return 15
    elif score >= 30:
        return 8
    else:
        return 3


def _format_currency(amount: int) -> str:
    """Format currency with K/M suffix."""
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.0f}K"
    else:
        return f"${amount:,}"


def _get_confidence_badge(tier: str) -> str:
    """Get confidence badge based on tier."""
    if tier in ["solid", "exceptional"]:
        return "✅ Medium-High"
    elif tier == "struggling":
        return "⚠️ Medium"
    else:
        return "❌ Low"


def _get_bottom_line(tier: str, score: float) -> str:
    """Generate tier-specific bottom line statement."""
    score_display = f"**Overall Score: {score:.0f}/100**"

    if tier == "crisis":
        return f"{score_display}\n\n**Your game is struggling significantly and requires immediate intervention.** Without major changes to address fundamental issues, recovery will be extremely difficult. This report focuses on triage and determining if the game is salvageable."

    elif tier == "struggling":
        return f"{score_display}\n\n**Your game shows promise but has critical issues limiting success.** The foundation exists for a turnaround, but specific blockers are preventing players from recommending it. This report identifies fixable problems and a path to positive momentum."

    elif tier == "solid":
        return f"{score_display}\n\n**Your game is performing solidly with clear optimization opportunities.** You've achieved product-market fit and positive reception. This report focuses on scaling what's working and capturing untapped revenue potential."

    else:  # exceptional
        return f"{score_display}\n\n**Your game is exceptional and ready for scaling strategies.** You're in the top 10-15% of Steam releases. This report focuses on market expansion, sustaining momentum, and maximizing lifetime value from your success."


def _get_score_meaning(tier: str, percentile: int, genre: str, score: float) -> str:
    """Explain what the score means with genre context."""

    base = f"**Percentile Ranking:** Top {percentile}% of Steam games (estimated)\n\n"

    if tier == "crisis":
        context = f"""**What This Means:**
- Your game is underperforming compared to {100 - percentile}% of Steam releases
- For {genre} games, this score indicates fundamental design or technical issues
- Players are actively warning others not to purchase
- Organic discovery has likely stopped completely

**Reality Check:**
At this tier, focus on diagnosis over optimization. Understand whether issues are:
1. **Fixable** (bugs, balance, missing features) → Invest in recovery
2. **Fundamental** (core gameplay, market fit) → Consider pivot or sunset

Most games in this range cannot be salvaged through marketing or polish alone."""

    elif tier == "struggling":
        context = f"""**What This Means:**
- Your game is below average but within reach of "Mixed" or "Mostly Positive" territory
- For {genre} games, this suggests good ideas with poor execution or critical gaps
- Some players enjoy it, but consistent complaints prevent recommendations
- You're likely losing 60-70% of potential buyers at the store page or first hour

**Reality Check:**
Games at this tier often need 2-3 major updates addressing top complaints. Success stories typically see:
- 10-20% review score improvement over 3-6 months
- 2-3x revenue increase as word-of-mouth turns positive
- Breakthrough moment when review score crosses 70% threshold"""

    elif tier == "solid":
        context = f"""**What This Means:**
- Your game is performing better than {percentile}% of Steam releases
- For {genre} games, you've achieved clear product-market fit
- Players are recommending it, but you're not capturing full market potential
- You're in the "safe zone" - unlikely to fail, but leaving money on the table

**Reality Check:**
Games at this tier typically have:
- 70-85% review scores → room to push toward "Very Positive"
- 5,000-50,000 owners → expansion opportunities exist
- Positive word-of-mouth → need better discovery and conversion
- Typical upside: 2-5x revenue through optimization (not heroics)"""

    else:  # exceptional
        context = f"""**What This Means:**
- Your game is outperforming {percentile}% of Steam releases
- For {genre} games, you're in elite company (top 10-15%)
- Players are enthusiastically recommending to friends
- You've likely hit saturation in your initial target market

**Reality Check:**
Games at this tier face different challenges:
- Growth comes from expansion (new regions, platforms) not fixes
- Risk of complacency - momentum can fade quickly without updates
- Opportunity for premium content, sequels, or franchise building
- Typical strategy: Maintain quality while scaling reach"""

    return base + context


def _get_situation_numbers(
    revenue: int,
    review_count: int,
    review_pct: float,
    velocity: str,
    tier: str
) -> str:
    """Format situation in numbers with interpretation."""

    revenue_fmt = _format_currency(revenue)
    confidence = _get_confidence_badge(tier)

    # Velocity interpretation
    if velocity == "increasing":
        velocity_icon = "✅"
        velocity_text = "Growing momentum - gaining positive reviews over time"
    elif velocity == "stable":
        velocity_icon = "⚠️"
        velocity_text = "Flat momentum - review rate has plateaued"
    else:  # declining
        velocity_icon = "❌"
        velocity_text = "Declining momentum - fewer reviews and likely fewer sales"

    # Review interpretation
    if review_pct >= 85:
        review_assessment = f"Exceptional ({review_pct:.0f}%) - Top 10% territory"
    elif review_pct >= 80:
        review_assessment = f"Very Strong ({review_pct:.0f}%) - Clear product-market fit"
    elif review_pct >= 70:
        review_assessment = f"Solid ({review_pct:.0f}%) - Positive but room for improvement"
    elif review_pct >= 60:
        review_assessment = f"Mixed ({review_pct:.0f}%) - Polarizing reception"
    else:
        review_assessment = f"Concerning ({review_pct:.0f}%) - Major issues evident"

    # Review count context
    if review_count > 10000:
        review_context = "Statistically significant sample - high confidence in metrics"
    elif review_count > 1000:
        review_context = "Good sample size - metrics are reliable"
    elif review_count > 100:
        review_context = "Moderate sample - trends are directional"
    else:
        review_context = "Limited sample - metrics may shift significantly"

    return f"""**Revenue Performance:**
- **Estimated Revenue:** {revenue_fmt} [Confidence: {confidence}]
- This places you in the {_get_revenue_tier_description(revenue, tier)} category

**Review Metrics:**
- **Review Score:** {review_assessment}
- **Total Reviews:** {review_count:,} reviews ({review_context})
- **Momentum:** {velocity_icon} {velocity_text}

**What This Tells Us:**
{_get_numbers_interpretation(tier, review_count, review_pct, velocity)}"""


def _get_revenue_tier_description(revenue: int, tier: str) -> str:
    """Describe revenue tier."""
    if revenue >= 1_000_000:
        return "major success (>$1M)"
    elif revenue >= 500_000:
        return "strong commercial success ($500K-$1M)"
    elif revenue >= 100_000:
        return "moderate commercial success ($100K-$500K)"
    elif revenue >= 50_000:
        return "modest success ($50K-$100K)"
    else:
        return "early stage or struggling (<$50K)"


def _get_numbers_interpretation(tier: str, review_count: int, review_pct: float, velocity: str) -> str:
    """Interpret what the numbers mean for this tier."""

    if tier == "crisis":
        return f"""The low review score ({review_pct:.0f}%) is your primary crisis. Even with {review_count:,} reviews providing clear feedback, the game hasn't resonated with players. Revenue will remain severely limited until fundamental issues are addressed. {velocity.capitalize()} momentum suggests {'the bleeding may be slowing' if velocity == 'stable' else 'continued decline' if velocity == 'declining' else 'some recent improvements'}."""

    elif tier == "struggling":
        return f"""Your {review_pct:.0f}% review score is the bottleneck. Players are finding the game, but ~{100 - review_pct:.0f}% leave negative reviews. With {review_count:,} reviews, you have clear signal on what to fix. {velocity.capitalize()} momentum {'indicates recent changes are working' if velocity == 'increasing' else 'shows you need to accelerate improvements' if velocity == 'declining' else 'suggests the game has stabilized at this quality level'}."""

    elif tier == "solid":
        return f"""Your {review_pct:.0f}% review score is strong but not exceptional. The {review_count:,} reviews show consistent positive reception. {velocity.capitalize()} momentum {'suggests continued growth potential' if velocity == 'increasing' else 'indicates market saturation in current channels' if velocity == 'declining' else 'shows stable but not growing market presence'}. Revenue upside comes from better monetization of your existing reputation, not fixing major flaws."""

    else:  # exceptional
        return f"""Your {review_pct:.0f}% review score is elite. With {review_count:,} reviews maintaining this quality, you've proven exceptional product-market fit. {velocity.capitalize()} momentum {'shows continued strong performance' if velocity in ['increasing', 'stable'] else 'suggests natural market saturation in initial audience'}. Focus on sustaining quality while expanding reach."""


def _get_top_priorities(tier: str, review_pct: float, review_count: int) -> str:
    """Generate tier-specific top 3 priorities."""

    if tier == "crisis":
        return """**Priority 1: Diagnose Root Cause**
- Analyze top 50 negative reviews for recurring themes
- Identify if issues are technical (fixable) vs. design (fundamental)
- Decision point: Is this game worth saving or should you pivot?
- **Timeline:** 1 week | **Cost:** $0 (your time) | **ROI:** Prevents wasting months on unfixable game

**Priority 2: Emergency Store Page Audit**
- Review store page for misleading expectations or poor presentation
- Test if trailer/screenshots accurately represent actual gameplay
- Check if price point is dramatically misaligned with content
- **Timeline:** 3 days | **Cost:** $0-500 (if hiring designer) | **ROI:** May reduce refund rate 10-20%

**Priority 3: Consider Radical Update or Free Weekend**
- If fixable issues identified, plan major "2.0" update addressing all top complaints
- Consider free weekend to get fresh reviews after fixes
- Alternative: Pivot to F2P if monetization model is the core issue
- **Timeline:** 4-12 weeks | **Cost:** $5K-20K (dev time) | **ROI:** Last chance at recovery"""

    elif tier == "struggling":
        return f"""**Priority 1: Fix Critical Blockers (Top 3 Negative Themes)**
- {review_pct:.0f}% positive means ~{100 - review_pct:.0f}% are citing fixable issues
- Pull negative reviews, categorize complaints, fix top 3 recurring issues
- Target: Push review score from {review_pct:.0f}% to 75%+ (crosses "Mostly Positive" threshold)
- **Timeline:** 4-8 weeks | **Investment:** $3K-8K (dev time) | **ROI:** 2-3x revenue increase

**Priority 2: Store Page Optimization**
- Current conversion rate likely 15-25% (should be 30-40% for {review_pct:.0f}% score)
- Rewrite description to address top objections head-on
- Update screenshots to show improvements from Priority 1
- **Timeline:** 1 week | **Investment:** $500-1K (copywriter/designer) | **ROI:** +20-30% conversion

**Priority 3: Price-Value Alignment**
- Negative reviews often cite "not worth the price" at this tier
- Analyze similar games - are you priced 20%+ above comparable titles?
- Test regional pricing in 2-3 emerging markets
- **Timeline:** 2 weeks | **Investment:** $0 (pricing test) | **ROI:** +15-25% units sold"""

    elif tier == "solid":
        return f"""**Priority 1: Regional Pricing Optimization**
- With {review_pct:.0f}% score, conversion isn't the issue - reach is
- Implement PPP-based pricing in Brazil, Turkey, Argentina, Southeast Asia
- Conservative estimate: +20-30% unit sales from emerging markets
- **Timeline:** 1 week | **Investment:** $0 (pricing adjustment) | **ROI:** +$10K-50K depending on base

**Priority 2: Influencer Outreach Campaign**
- {review_pct:.0f}% score is credible - influencers will actually recommend it
- Target 10-15 micro-influencers (5K-50K followers) in your genre
- Provide keys, ask for honest coverage (not sponsored posts)
- **Timeline:** 4 weeks | **Investment:** $1K-2K (outreach tools) | **ROI:** 5-10x through impressions

**Priority 3: Community Engagement Scaling**
- With {review_count:,} reviews, you have an active community
- Launch Discord/subreddit if not existing, or scale existing community
- Weekly dev updates, community highlights, feedback loops
- **Timeline:** Ongoing | **Investment:** 5 hrs/week | **ROI:** Sustains momentum, reduces churn"""

    else:  # exceptional
        return f"""**Priority 1: Market Expansion (Platforms/Regions)**
- {review_pct:.0f}% score makes you low-risk for platform holders
- Evaluate console ports (Switch/PlayStation/Xbox) or EGS/GOG
- Alternatively, expand to LATAM/Asia with localization
- **Timeline:** 3-6 months | **Investment:** $15K-50K | **ROI:** 2-5x through new markets

**Priority 2: Premium Content/DLC Planning**
- With {review_count:,} enthusiastic reviews, players want more content
- Survey community for most-requested features/content
- Plan $5-15 DLC or major free update (sustains engagement)
- **Timeline:** 3-6 months | **Investment:** $10K-30K | **ROI:** 30-50% attach rate at 50% margins

**Priority 3: Sustaining Momentum Through Updates**
- {review_pct:.0f}% scores can drop if game feels abandoned
- Commit to monthly/quarterly content updates for next 12 months
- Consider seasonal events, community contests, speedrun support
- **Timeline:** Ongoing | **Investment:** 10-20 hrs/month | **ROI:** Maintains sales velocity, prevents drop-off"""


def _get_ignore_list(tier: str) -> str:
    """List what to ignore for this tier."""

    if tier == "crisis":
        return """At your current performance level, **ignore these common distractions:**

❌ **Influencer marketing** - No one will promote a poorly-reviewed game
❌ **Paid advertising** - Throwing money at ads won't fix fundamental issues
❌ **SEO/ASO optimization** - Discovery isn't your problem; retention is
❌ **Social media growth** - Building audience for a broken product wastes time
❌ **DLC or content updates** - Fix the base game before adding more

**Focus 100% on:** Understanding why players are leaving negative reviews and determining if those issues are fixable."""

    elif tier == "struggling":
        return """At your current performance level, **ignore these premature optimizations:**

❌ **Influencer campaigns** - Wait until review score crosses 75% threshold
❌ **Major advertising spend** - Fix conversion rate first (store page + reviews)
❌ **Platform expansion** - Don't bring a struggling game to new platforms
❌ **Community building** - Hard to build community when 30-40% of players are unhappy
❌ **Premium DLC** - Players won't buy DLC for a game they're ambivalent about

**Focus on:** Fixing the core issues preventing recommendations, then amplifying success."""

    elif tier == "solid":
        return """At your current performance level, **these are lower priority:**

⚠️ **Major gameplay overhauls** - Don't fix what isn't broken
⚠️ **Review score obsession** - Chasing 95%+ has diminishing returns
⚠️ **Viral marketing tactics** - You need steady growth, not lottery tickets
⚠️ **Competitor comparison** - Focus on your strengths, not matching others
⚠️ **Feature bloat** - More isn't better; focus on what players love

**Focus on:** Scaling what's working (reach, pricing, community) rather than fundamental changes."""

    else:  # exceptional
        return """At your elite performance level, **avoid these traps:**

⚠️ **Chasing perfection** - 95%+ scores are hard to maintain; focus on momentum
⚠️ **Feature creep** - Don't dilute what made the game special
⚠️ **Discounting too aggressively** - Preserve brand value; you've earned premium pricing
⚠️ **Ignoring existing community** - Chasing new players at expense of loyalists backfires
⚠️ **Resting on laurels** - Momentum fades fast without sustained effort

**Focus on:** Strategic expansion and sustaining the quality that got you here."""


def _get_realistic_goals(tier: str, revenue: int, review_count: int) -> str:
    """Set realistic 90-day goals based on tier."""

    if tier == "crisis":
        conservative_revenue = int(revenue * 0.8)
        likely_revenue = int(revenue * 1.0)
        optimistic_revenue = int(revenue * 1.3)

        return f"""Based on {_format_currency(revenue)} current revenue and crisis-tier performance:

**Conservative (60% probability):**
- Revenue: {_format_currency(conservative_revenue)} (-20% as situation stabilizes or worsens)
- Review Score: Stays flat or drops 2-3 points
- Outcome: Determine if game is salvageable; plan next steps

**Likely (30% probability):**
- Revenue: {_format_currency(likely_revenue)} (flat - bleeding stops)
- Review Score: Improves 3-5 points if major fixes deployed
- Outcome: Begin slow recovery with clear improvement signals

**Optimistic (10% probability):**
- Revenue: {_format_currency(optimistic_revenue)} (+30% from turnaround update)
- Review Score: Jumps 8-10 points from "2.0" style relaunch
- Outcome: Successful recovery story; featured in "games that improved" lists

**Reality Check:** Most games at this tier don't recover. Success requires both fixable issues AND commitment to 6+ months of intensive updates."""

    elif tier == "struggling":
        conservative_revenue = int(revenue * 1.3)
        likely_revenue = int(revenue * 1.8)
        optimistic_revenue = int(revenue * 2.5)

        return f"""Based on {_format_currency(revenue)} current revenue and struggling-tier performance:

**Conservative (50% probability):**
- Revenue: {_format_currency(conservative_revenue)} (+30% from incremental fixes)
- Review Score: Improves 5-8 points
- Outcome: Still "Mixed" but trending positive; slower growth

**Likely (35% probability):**
- Revenue: {_format_currency(likely_revenue)} (+80% as word-of-mouth turns)
- Review Score: Crosses 70-75% threshold ("Mostly Positive")
- Outcome: Breaking into positive territory; sales acceleration begins

**Optimistic (15% probability):**
- Revenue: {_format_currency(optimistic_revenue)} (+150% from breakthrough moment)
- Review Score: Reaches 75-80% range
- Outcome: Turnaround success story; featured in "overlooked gems" coverage

**Reality Check:** Expect 3-6 months before seeing major results. Quick wins are rare at this tier."""

    elif tier == "solid":
        conservative_revenue = int(revenue * 1.5)
        likely_revenue = int(revenue * 2.2)
        optimistic_revenue = int(revenue * 3.5)

        return f"""Based on {_format_currency(revenue)} current revenue and solid-tier performance:

**Conservative (40% probability):**
- Revenue: {_format_currency(conservative_revenue)} (+50% from regional pricing alone)
- Review Count: +{int(review_count * 0.3):,} reviews
- Outcome: Steady growth; no breakthroughs but consistent performance

**Likely (40% probability):**
- Revenue: {_format_currency(likely_revenue)} (+120% from pricing + influencer reach)
- Review Count: +{int(review_count * 0.5):,} reviews
- Outcome: Clear acceleration; crossing into "successful indie" territory

**Optimistic (20% probability):**
- Revenue: {_format_currency(optimistic_revenue)} (+250% from viral moment or platform featuring)
- Review Count: +{int(review_count * 0.8):,} reviews
- Outcome: Breakout success; top seller in genre for a period

**Reality Check:** You're in the "safe zone" - growth is about capturing opportunity, not survival."""

    else:  # exceptional
        conservative_revenue = int(revenue * 1.3)
        likely_revenue = int(revenue * 1.6)
        optimistic_revenue = int(revenue * 2.5)

        return f"""Based on {_format_currency(revenue)} current revenue and exceptional-tier performance:

**Conservative (50% probability):**
- Revenue: {_format_currency(conservative_revenue)} (+30% from sustained momentum)
- Review Count: +{int(review_count * 0.2):,} reviews
- Outcome: Maintain elite status; natural market saturation in primary market

**Likely (30% probability):**
- Revenue: {_format_currency(likely_revenue)} (+60% from expansion efforts)
- Review Count: +{int(review_count * 0.35):,} reviews
- Outcome: Successful expansion to new markets/platforms

**Optimistic (20% probability):**
- Revenue: {_format_currency(optimistic_revenue)} (+150% from DLC/sequel hype or major featuring)
- Review Count: +{int(review_count * 0.5):,} reviews
- Outcome: Franchise potential; industry recognition (awards, press coverage)

**Reality Check:** You've "won" - now the challenge is sustaining success and expanding strategically. Avoid complacency."""


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("EXAMPLE 1: Crisis Tier (Score: 35)")
    print("=" * 80)
    result1 = generate_executive_summary(
        overall_score=35,
        review_count=450,
        review_percentage=42,
        revenue_estimate=18000,
        review_velocity_trend="declining",
        genre="Action RPG"
    )
    print(result1)

    print("\n\n")
    print("=" * 80)
    print("EXAMPLE 2: Struggling Tier (Score: 55)")
    print("=" * 80)
    result2 = generate_executive_summary(
        overall_score=55,
        review_count=1200,
        review_percentage=68,
        revenue_estimate=85000,
        review_velocity_trend="stable",
        genre="Puzzle Platformer"
    )
    print(result2)

    print("\n\n")
    print("=" * 80)
    print("EXAMPLE 3: Solid Tier (Score: 72)")
    print("=" * 80)
    result3 = generate_executive_summary(
        overall_score=72,
        review_count=3500,
        review_percentage=81,
        revenue_estimate=320000,
        review_velocity_trend="increasing",
        genre="Roguelike"
    )
    print(result3)

    print("\n\n")
    print("=" * 80)
    print("EXAMPLE 4: Exceptional Tier (Score: 88)")
    print("=" * 80)
    result4 = generate_executive_summary(
        overall_score=88,
        review_count=8200,
        review_percentage=94,
        revenue_estimate=1250000,
        review_velocity_trend="stable",
        genre="Strategy"
    )
    print(result4)
