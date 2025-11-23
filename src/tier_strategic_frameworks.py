"""
Tier-Specific Strategic Frameworks for Publitz Audit Reports

Defines how report structure, tone, and focus should adapt based on game performance tier.
A 35/100 game (crisis) needs completely different analysis than an 88/100 game (exceptional).

Tier Definitions:
- Tier 1: Crisis (0-40/100) - Diagnosis & Triage
- Tier 2: Struggling (40-60/100) - Problem Identification & Fixing
- Tier 3: Solid (60-80/100) - Optimization & Growth
- Tier 4: Exceptional (80-100/100) - Scaling & Expansion
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class StrategicFramework:
    """Complete strategic framework for a performance tier."""
    tier_name: str
    score_range: str
    primary_frame: str
    key_question: str
    tone: str
    priority_sections: List[str]
    included_sections: List[str]
    excluded_sections: List[str]
    language_guidelines: List[str]
    section_rewrites: Dict[str, str]


# ============================================================================
# TIER 1: CRISIS (0-40/100) - Diagnosis & Triage
# ============================================================================

TIER_1_CRISIS = StrategicFramework(
    tier_name="Crisis",
    score_range="0-40/100",
    primary_frame="Diagnosis & Triage - Is this game salvageable?",
    key_question="Should you invest more resources into fixing this game, or cut your losses and pivot?",
    tone="Direct, honest, clinical. No sugar-coating. Focus on fundamental issues.",

    priority_sections=[
        "1. Executive Summary (harsh reality check)",
        "2. Data Confidence Assessment",
        "3. Critical Issues Analysis (why is it failing?)",
        "4. Negative Review Deep-Dive (fundamental vs. fixable issues)",
        "5. Emergency Action Plan (3 actions to stabilize)",
        "6. Pivot vs. Persevere Decision Framework",
        "7. Refund Rate Analysis (if available)",
        "8. Price vs. Perceived Value Assessment",
        "9. Store Page Analysis (are you misleading players?)",
        "10. Technical Issues Audit",
    ],

    included_sections=[
        "Executive Summary",
        "Data Confidence Assessment",
        "Critical Issues Analysis",
        "Negative Review Theme Analysis",
        "Refund Rate Analysis",
        "Price vs. Value Assessment",
        "Store Page Truth-in-Advertising Audit",
        "Technical Performance Analysis",
        "Emergency Action Plan (stabilization only)",
        "Pivot vs. Persevere Decision Framework",
        "Post-Mortem Preparation (if unfixable)",
    ],

    excluded_sections=[
        "Market Expansion Planning (premature)",
        "DLC Strategy (premature)",
        "Influencer Outreach Strategy (wrong priority - no one will cover a failing game)",
        "Community Growth Tactics (can't build community around broken product)",
        "Localization Recommendations (fix core product first)",
        "Console Port Evaluation (don't bring broken game to new platforms)",
        "Monetization Optimization (retention is the issue, not monetization)",
        "Content Roadmap (beyond critical fixes)",
    ],

    language_guidelines=[
        "✅ DO: Be brutally honest about fundamental issues",
        "✅ DO: Use clinical, diagnostic language (like a doctor delivering bad news)",
        "✅ DO: Acknowledge if game may not be fixable",
        "✅ DO: Provide concrete data on why it's failing",
        "✅ DO: Frame as 'triage' and 'diagnosis' not 'optimization'",
        "❌ DON'T: Use encouraging language if data doesn't support it",
        "❌ DON'T: Suggest minor optimizations when major overhaul needed",
        "❌ DON'T: Compare to successful games (unhelpful at this stage)",
        "❌ DON'T: Focus on missed opportunities (focus on core problems)",
        "❌ DON'T: Recommend scaling strategies (premature)",
    ],

    section_rewrites={
        "market_positioning": """## Critical Issues Analysis: Market Positioning

**Reality Check**: Your game is positioned in the Action Roguelite segment, one of Steam's most competitive categories. With a 62% review score, you're in the **bottom 30% of this category**. This isn't a positioning problem—it's an execution problem.

**What This Means**:
- Players in this genre have high quality standards (Hades, Dead Cells, Risk of Rain 2 all have 90%+ scores)
- Your game is being directly compared to genre-defining titles and falling short
- The market exists, but you're not meeting the quality bar

**Critical Question**: Are the issues preventing your game from reaching 75%+ reviews **fundamental to your design** or **fixable through updates**?

If fundamental (core gameplay loop, game feel, content volume), you may need to consider a pivot. If fixable (bugs, balance, missing features), see Emergency Action Plan.""",

        "sales_performance": """## Revenue Analysis: Understanding the Bleeding

**Current Revenue**: ~$18K [Confidence: ❌ Low - based on limited data]

**Why Revenue is Low**:
1. **Poor Conversion**: With a 62% review score, you're losing 60-70% of potential buyers who check reviews
2. **No Viral Growth**: Negative reviews prevent word-of-mouth
3. **High Refund Rate**: Players who do buy are likely refunding (check Steam Partner Dashboard)

**Realistic Revenue Trajectory Without Changes**:
- Conservative: -20% next 90 days (continued decline)
- Likely: Flat to -10% (bleeding stops but no growth)
- Optimistic: +10-20% if you immediately fix critical issues

**Bottom Line**: Revenue is a symptom, not the disease. Fix the review score first.""",

        "action_plan": """## Emergency Action Plan: Stabilization Mode

**Your Goal**: Stop the bleeding. Stabilize review score. Determine if game is salvageable.

**Week 1-2: Diagnosis**
1. **Analyze Top 50 Negative Reviews**
   - Categorize complaints: Bugs? Difficulty? Content? Core gameplay?
   - Identify recurring themes (appears in 20%+ of reviews)
   - Separate fixable issues from fundamental design problems

2. **Check Refund Rate** (Steamworks → Sales & Activations → Refunds)
   - >30% refund rate = fundamental issues
   - 15-30% = significant fixable issues
   - <15% = niche game, not broken

3. **Truth Test Your Store Page**
   - Does your trailer show actual gameplay or cherry-picked moments?
   - Are you promising features the game doesn't deliver?
   - Is pricing aligned with content volume?

**Week 3-4: Emergency Fixes (Only if Issues Are Fixable)**
- Address top 3 most-mentioned bugs/issues
- Post developer response to top 10 negative reviews
- If issues are fundamental: Begin pivot planning

**NOT on This List**: Marketing, influencer outreach, DLC, ports. None of that matters if the core product is broken.""",
    }
)


# ============================================================================
# TIER 2: STRUGGLING (40-60/100) - Problem Identification & Fixing
# ============================================================================

TIER_2_STRUGGLING = StrategicFramework(
    tier_name="Struggling",
    score_range="40-60/100",
    primary_frame="Problem Identification - What specific issues are blocking success?",
    key_question="What are the 3-5 fixable blockers preventing your game from crossing the 70% review threshold?",
    tone="Constructive, problem-focused, solution-oriented. Acknowledge struggle but emphasize fixability.",

    priority_sections=[
        "1. Executive Summary (realistic but hopeful)",
        "2. Data Confidence Assessment",
        "3. Quick Start: Your First 3 Actions",
        "4. Critical Blockers Analysis (what's preventing 70%+ reviews)",
        "5. Review Theme Breakdown (what players complain about most)",
        "6. Conversion Funnel Analysis (where are you losing players?)",
        "7. Store Page Optimization",
        "8. Pricing Strategy Assessment",
        "9. 90-Day Turnaround Roadmap",
        "10. Success Case Studies (games that recovered from similar scores)",
    ],

    included_sections=[
        "Executive Summary",
        "Data Confidence Assessment",
        "Quick Start Actions",
        "Critical Blockers Analysis",
        "Review Sentiment Deep-Dive",
        "Conversion Funnel Breakdown",
        "Store Page Optimization",
        "Pricing Strategy",
        "Tag & Discovery Optimization",
        "Core Gameplay Improvements (specific)",
        "Technical Performance Fixes",
        "90-Day Turnaround Roadmap",
        "Competitor Comparison (what are they doing right?)",
        "Success Stories (recovery examples)",
    ],

    excluded_sections=[
        "Market Expansion (fix core market first)",
        "DLC Strategy (premature until base game healthy)",
        "Console Ports (don't port struggling game)",
        "Localization (English market first)",
        "Advanced Monetization (retention > monetization)",
        "Community Management at Scale (no scale yet)",
        "Influencer Partnerships (wait until 75%+ reviews)",
    ],

    language_guidelines=[
        "✅ DO: Acknowledge the game has promise but specific issues",
        "✅ DO: Frame as 'fixable problems' not 'fundamental failures'",
        "✅ DO: Provide specific, actionable fixes",
        "✅ DO: Show examples of games that recovered from similar positions",
        "✅ DO: Set realistic expectations (3-6 months to turn around)",
        "❌ DON'T: Sugar-coat the severity of issues",
        "❌ DON'T: Recommend minor tweaks when major fixes needed",
        "❌ DON'T: Focus on growth tactics before fixing retention",
        "❌ DON'T: Ignore negative reviews in favor of positive framing",
        "❌ DON'T: Recommend expensive marketing (won't work with current reviews)",
    ],

    section_rewrites={
        "market_positioning": """## Market Analysis: You're in the Right Place, Wrong Execution

**Current Position**: Action Roguelite with 68% review score

**The Good News**: You're in a proven category with strong demand. The market wants what you're selling.

**The Challenge**: You're in "Mixed" territory when this genre demands "Mostly Positive" minimum. Players comparing you to Hades (93%), Dead Cells (90%), and Risk of Rain 2 (92%) are finding you lacking.

**Gap Analysis**:
- **Review Score Delta**: 68% (you) vs. 85% (genre average) = **-17 points**
- **What This Costs You**: ~40-50% of potential buyers check reviews and bounce
- **The Opportunity**: Every 5-point improvement in review score = ~20% increase in conversion

**Your Path Forward**: You don't need to beat Hades. You need to cross 75% ("Mostly Positive"). That's 32% of negative reviewers flipping to positive—achievable through addressing top complaints.""",

        "sales_performance": """## Revenue Analysis: Trapped by Review Score

**Current Revenue**: ~$85K [Confidence: ⚠️ Medium]
**Revenue Potential at 75% Reviews**: ~$180K-$220K (2-3x current)

**Why You're Underperforming**:
1. **Store Visit → Wishlist**: Likely 12-15% (should be 20-25% at 75% reviews)
2. **Wishlist → Purchase**: Healthy (~30-40%), but wishlist pool too small
3. **Post-Purchase**: 32% leave negative review, preventing word-of-mouth

**The Bottleneck**: Your review score is the primary limiter. Not your price, not your marketing, not your genre positioning.

**Revenue Projection (If You Fix Top 3 Issues)**:
- 3 months: +30-50% (early wins from responding to reviews, quick fixes)
- 6 months: +80-120% (major updates start changing review trend)
- 12 months: +150-200% (crossing 75% threshold triggers viral loop)

**Critical**: Every month you delay fixing core issues costs you ~$5K-8K in lost revenue.""",

        "action_plan": """## 90-Day Turnaround Roadmap

**Goal**: Cross 70% review threshold (75% target) and double revenue

**Month 1: Quick Wins & Community Repair**
1. **Respond to Top 20 Negative Reviews** (Week 1)
   - Acknowledge specific complaints
   - Commit to fixes with timeline
   - 20-30% will update reviews if you follow through

2. **Fix Top 3 Most-Mentioned Bugs** (Week 2-3)
   - Check review sentiment analysis for recurring technical issues
   - Deploy hotfixes, announce in community hub
   - Show you're listening and acting

3. **Store Page Optimization** (Week 4)
   - Rewrite first paragraph (benefit-focused)
   - Update screenshots to show improvements
   - Add "Frequently Updated" messaging

**Month 2: Major Fixes**
1. **Address Core Gameplay Complaints** (Week 5-7)
   - If reviews say "too grindy" → reduce grind 20-30%
   - If reviews say "too hard" → add difficulty options
   - If reviews say "repetitive" → add variety/content

2. **Launch "2.0" Update** (Week 8)
   - Bundle all fixes into major update
   - Write detailed patch notes
   - Encourage players to update reviews if satisfied

**Month 3: Building Momentum**
1. **Content Update** (Week 9-11)
   - New mode, weapons, or meaningful content
   - Target top wishlist features from community

2. **Measure & Adjust** (Week 12)
   - Check review score improvement
   - If 70%+: Begin influencer outreach
   - If <70%: Analyze what didn't work, iterate

**Success Metrics**:
- Week 4: 10-15 negative reviews updated to positive
- Week 8: Review score improves 3-5 points
- Week 12: Review score at 72-75%, revenue +50-80%""",
    }
)


# ============================================================================
# TIER 3: SOLID (60-80/100) - Optimization & Growth
# ============================================================================

TIER_3_SOLID = StrategicFramework(
    tier_name="Solid",
    score_range="60-80/100",
    primary_frame="Optimization - How do we maximize existing success?",
    key_question="What low-hanging fruit and strategic optimizations will drive 2-5x revenue growth?",
    tone="Encouraging, opportunity-focused, data-driven. Celebrate success while identifying clear upside.",

    priority_sections=[
        "1. Executive Summary (positive, opportunity-focused)",
        "2. Data Confidence Assessment",
        "3. Quick Start: Your First 3 Actions",
        "4. Hidden Revenue Opportunities (regional pricing, tags, etc.)",
        "5. Conversion Funnel Optimization",
        "6. Community Growth Strategies",
        "7. Influencer Outreach Playbook",
        "8. Content Roadmap (what will sustain/grow engagement)",
        "9. Market Expansion Evaluation",
        "10. Monetization Optimization",
    ],

    included_sections=[
        "Executive Summary",
        "Data Confidence Assessment",
        "Quick Start Actions",
        "Revenue Optimization Opportunities",
        "Regional Pricing Strategy",
        "Tag & Discovery Maximization",
        "Store Page A/B Testing Recommendations",
        "Influencer Outreach Strategy",
        "Community Building Tactics",
        "Content Roadmap",
        "DLC Feasibility Analysis",
        "Platform Expansion (console ports)",
        "Localization ROI Analysis",
        "Competitor Benchmarking (how do you compare?)",
        "Sustainability Planning (maintaining momentum)",
    ],

    excluded_sections=[
        "Crisis Management (not needed)",
        "Fundamental Fixes (core product is working)",
        "Pivot Decision Framework (not needed)",
        "Emergency Action Plans (not in crisis)",
    ],

    language_guidelines=[
        "✅ DO: Celebrate what's working well",
        "✅ DO: Frame as 'optimization' and 'scaling' not 'fixing'",
        "✅ DO: Focus on ROI and growth multipliers",
        "✅ DO: Provide data-driven recommendations",
        "✅ DO: Compare to best-in-class examples",
        "❌ DON'T: Imply there are major problems (there aren't)",
        "❌ DON'T: Recommend massive overhauls (incremental improvements)",
        "❌ DON'T: Focus on worst-case scenarios",
        "❌ DON'T: Be overly cautious (you can afford to be confident)",
        "❌ DON'T: Suggest they're failing (they're succeeding)",
    ],

    section_rewrites={
        "market_positioning": """## Market Position: Strong Player in Competitive Space

**Current Standing**: Action Roguelite with 81% review score

**Competitive Analysis**: You're in the **top 25% of your category**. Players are consistently recommending your game, putting you in "Very Positive" territory alongside successful indies.

**Market Comparison**:
- **Genre Leaders**: Hades (93%), Dead Cells (90%), Risk of Rain 2 (92%)
- **Successful Peers**: Wizard of Legend (82%), Flamekeeper (83%), Roboquest (85%)
- **You**: 81% - **Solidly in the "successful indie" tier**

**What This Means**:
- You've achieved product-market fit ✅
- Players are happily recommending to friends ✅
- You're not leaving money on the table due to quality issues ✅
- Growth comes from **reach** (more people finding you) not **retention** (you've solved that)

**Opportunity**: You don't need to improve quality significantly—you need to get in front of more qualified buyers. Regional pricing, influencer outreach, and platform expansion will drive growth.""",

        "sales_performance": """## Revenue Performance: Solid Foundation, Clear Growth Path

**Current Revenue**: ~$320K [Confidence: ✅ Medium-High]
**Revenue Potential (12 months)**: ~$650K-$900K (2-3x current)

**What's Working**:
- **Conversion Rate**: 22-28% (store visit → wishlist) - ✅ Healthy
- **Review Score**: 81% sustaining positive word-of-mouth ✅
- **Retention**: Players who buy are satisfied (81% positive) ✅

**Where You're Leaving Money**:
1. **Regional Pricing** (Not implemented)
   - Potential: +$64K-$96K/year from Brazil, Turkey, Argentina, India, Russia
   - Effort: 30 minutes to set up
   - ROI: Infinite (pure incremental revenue)

2. **Discovery Optimization** (11 tags, should have 15-20)
   - Potential: +10-15% impressions = +$32K-$48K/year
   - Effort: 1 hour
   - ROI: ~40-50x

3. **Influencer Reach** (Little to no coverage)
   - Potential: 1-2 videos from 10K-50K creators = +$40K-$80K/year
   - Effort: 2-3 hours of outreach
   - ROI: 20-40x

**Conservative 12-Month Projection**:
- Regional pricing: +$70K
- Discovery optimization: +$40K
- Influencer coverage: +$60K
- Organic growth (review score sustaining): +$80K
- **Total**: $320K → $570K (+78%)**""",

        "action_plan": """## Growth Acceleration Plan: Scaling What Works

**Your Situation**: You've built a quality game that players love. Now it's about multiplying reach.

**Next 90 Days: Low-Effort, High-Return Optimizations**

**Month 1: Quick Revenue Unlocks**
1. **Regional Pricing** (Week 1)
   - 30 minutes to implement
   - See first sales within 24-48 hours
   - Expected: +20-30% units from emerging markets

2. **Tag Optimization** (Week 2)
   - Add 5-8 high-traffic tags
   - Algorithm picks up in 3-7 days
   - Expected: +10-15% impressions

3. **Steam Deck Verification** (Week 3-4)
   - Submit for verification
   - Reviewed in 7-14 days
   - Expected: +12-18% wishlist rate from Deck users

**Month 2: Community & Influencer**
1. **Community Hub Activation** (Week 5-6)
   - 5 posts per week (roadmap, tips, challenges)
   - Respond to all comments within 24 hours
   - Expected: +8-12% wishlist conversion

2. **Micro-Influencer Outreach** (Week 7-8)
   - Email 10 creators (5K-50K followers)
   - 2-3 will cover it (your review score is credible)
   - Expected: 400-1,000 wishlists per video

**Month 3: Content & Sustainability**
1. **Content Update Planning** (Week 9-11)
   - Survey community for most-wanted features
   - Plan 3-month content roadmap
   - Announce publicly to sustain momentum

2. **Platform Expansion Evaluation** (Week 12)
   - Analyze console port ROI (you're low-risk with 81% reviews)
   - Consider EGS/GOG (often negotiate revenue guarantees for quality titles)

**Success Metrics**:
- Month 1: +25-35% revenue from regional pricing + tags
- Month 2: +15-20% from community engagement + influencers
- Month 3: Content roadmap announced, community excited for future""",
    }
)


# ============================================================================
# TIER 4: EXCEPTIONAL (80-100/100) - Scaling & Expansion
# ============================================================================

TIER_4_EXCEPTIONAL = StrategicFramework(
    tier_name="Exceptional",
    score_range="80-100/100",
    primary_frame="Scaling - How do we sustain and expand momentum?",
    key_question="How do you capitalize on exceptional quality to build a franchise and maximize lifetime value?",
    tone="Celebratory, strategic, forward-thinking. Focus on long-term value and platform-level opportunities.",

    priority_sections=[
        "1. Executive Summary (celebrate success, focus on strategy)",
        "2. Data Confidence Assessment",
        "3. Quick Start: Your First 3 Actions",
        "4. Market Dominance Analysis (where do you rank?)",
        "5. Platform Expansion Strategy (console, mobile, EGS)",
        "6. Premium Content & DLC Strategy",
        "7. Franchise Building Opportunities",
        "8. Strategic Partnerships (publishers, platforms)",
        "9. Community Sustainability (maintaining engagement)",
        "10. Long-Term Monetization (beyond initial purchase)",
    ],

    included_sections=[
        "Executive Summary",
        "Data Confidence Assessment",
        "Quick Start Actions",
        "Market Dominance Analysis",
        "Platform Expansion Strategy",
        "Console Port ROI Analysis",
        "Premium DLC Strategy",
        "Sequels & Franchise Potential",
        "Strategic Partnership Opportunities",
        "Community Sustainability Planning",
        "Influencer Partnership Programs (not outreach, partnerships)",
        "Esports/Competitive Scene Potential",
        "Merchandise & Brand Expansion",
        "International Market Deep-Dive",
        "Long-Term Monetization Strategy",
        "Team Scaling Recommendations",
    ],

    excluded_sections=[
        "Crisis Management (not relevant)",
        "Problem Diagnosis (no problems)",
        "Store Page Fixes (already optimized by definition)",
        "Technical Performance Issues (if scores are this high, not an issue)",
        "Price Sensitivity Testing (you've proven price works)",
    ],

    language_guidelines=[
        "✅ DO: Celebrate the achievement (top 10-15% of Steam)",
        "✅ DO: Frame as 'strategic expansion' and 'franchise building'",
        "✅ DO: Focus on long-term value and sustainability",
        "✅ DO: Discuss platform-level opportunities (featuring, partnerships)",
        "✅ DO: Compare to genre-defining successes",
        "❌ DON'T: Focus on basic optimizations (already done)",
        "❌ DON'T: Be cautious or conservative (you can be bold)",
        "❌ DON'T: Treat as 'indie' (you're AAA-quality, act like it)",
        "❌ DON'T: Recommend small-scale tactics (think bigger)",
        "❌ DON'T: Ignore the risk of complacency (momentum fades fast)",
    ],

    section_rewrites={
        "market_positioning": """## Market Dominance: Top 1% of Steam, Genre-Defining Quality

**Current Standing**: Action Roguelite with 96.5% review score

**Elite Status**: You are in the **top 1% of all Steam releases** and **top 5 in your category**. This isn't just "success"—this is **genre-defining quality**.

**Competitive Comparison**:
- **Hades**: 93% (your closest peer)
- **Dead Cells**: 90%
- **Risk of Rain 2**: 92%
- **YOU**: 96.5% - **Highest in category**

**What This Means**:
- You're not competing—you're **setting the standard**
- New Action Roguelites will be compared to YOU
- You have leverage for platform partnerships (Steam featured, console revenue guarantees)
- Players trust you for sequels/DLC (30-50% attach rate vs. 10-15% industry average)

**Strategic Implications**:
1. **You Can Command Premium Pricing** - Your quality justifies $29.99-$39.99 (if not already)
2. **Platform Holders Want You** - Sony/Nintendo/Xbox will negotiate for you
3. **You Have Franchise Potential** - Sequels, spin-offs, expanded universe
4. **Your Leverage is Time-Sensitive** - Act while momentum is hot""",

        "sales_performance": """## Revenue Performance: Exceptional Quality, Exceptional Returns

**Current Revenue**: ~$1.25M [Confidence: ✅ High]
**Revenue Potential (12-24 months)**: ~$2.5M-$5M+ (2-4x through expansion)

**What's Driving Success**:
- **Review Score**: 96.5% creates viral word-of-mouth loop ✅
- **Conversion Rate**: 35-45% (store visit → wishlist) - ✅ Elite tier
- **Retention**: Players become evangelists (96.5%!) ✅
- **Word-of-Mouth**: Organic discovery driving 60-70% of traffic ✅

**Revenue Breakdown**:
- **PC (Steam)**: $1.25M - Saturating initial market
- **Potential Console Ports**: $800K-$2M additional (Switch/PlayStation/Xbox)
- **Potential DLC** (30-50% attach): $375K-$625K
- **Potential EGS/GOG**: $250K-$400K (often offer revenue guarantees for quality titles)

**Platform Expansion Analysis**:

**Nintendo Switch** (Highest Priority)
- Indie roguelites thrive on Switch (Hades did $50M+ on Switch vs. $10M on PC)
- Your quality makes you low-risk for Nintendo featuring
- Conservative estimate: 50-70% of your Steam revenue (=$625K-$875K)

**PlayStation/Xbox**
- Combined console market ~40-60% of Steam
- Sony likely offers revenue guarantee for 95%+ reviewed titles
- Conservative estimate: $500K-$750K combined

**Epic Games Store**
- Often pays $100K-$500K revenue guarantee for 90%+ reviewed exclusives
- Even if guarantee, still sell on Steam after exclusivity

**Total Addressable Revenue (Next 24 Months)**: $3M-$5M+""",

        "action_plan": """## Strategic Expansion Plan: Building a Franchise

**Your Position**: You've won the indie game lottery. 96.5% reviews = top 1%. Now capitalize on it.

**Next 6 Months: Platform Expansion**

**Month 1-2: Console Port Planning**
1. **Evaluate Port Partners** (Week 1-2)
   - Contact 3-5 porting studios (get quotes: $50K-$150K typical)
   - Prioritize Switch (biggest ROI for indies)
   - Check if Sony offers revenue guarantee (they often do for 95%+ reviews)

2. **Begin Switch Port** (Week 3-8)
   - 3-4 month dev time typical
   - Nintendo often features high-quality indies in Indie World showcase
   - Target: Launch in Month 6

**Month 3-4: Premium Content Planning**
1. **Survey Community** (Week 9-10)
   - What content would they pay for?
   - DLC vs. Sequel preference?
   - Price sensitivity ($9.99 vs. $14.99 DLC)

2. **Plan Major DLC** (Week 11-16)
   - Target: 4-6 hours of new content
   - Price: $12.99-$14.99
   - Conservative attach rate: 30-35% (vs. 15% industry average)
   - Revenue: $125K-$175K

**Month 5-6: Strategic Partnerships**
1. **Platform Negotiations** (Week 17-20)
   - Approach EGS about exclusivity/guarantee (leverage 96.5% score)
   - Discuss Xbox Game Pass (upfront payment for inclusion)
   - Explore Apple Arcade if game is compatible

2. **Influencer Partnerships** (Week 21-24)
   - Move beyond one-off coverage to partnerships
   - Sponsor YouTubers/streamers for series (not one video)
   - Co-create content (speedrun competitions, tournaments)

**12-24 Month Vision: Franchise**
1. **Sequel Planning** (if community wants it)
   - Your 96.5% score = instant wishlist momentum for sequel
   - "From the creators of [Game]" is a powerful hook

2. **Expanded Universe**
   - Spin-off in different genre but same world?
   - Merchandise (if community is that engaged)

3. **Studio Building**
   - Hire to sustain multiple projects
   - Don't let success be one-hit wonder

**Risk Management**: Your biggest risk is complacency. Games at 96%+ can drop fast if:
- Development goes quiet (players assume abandoned)
- Quality drops in updates (one bad patch can hurt reviews)
- You chase trends instead of doubling down on what worked

**Keep momentum by**: Monthly updates, transparent communication, sustained quality.""",
    }
)


# ============================================================================
# FRAMEWORK SELECTOR & UTILITIES
# ============================================================================

TIER_FRAMEWORKS = {
    "crisis": TIER_1_CRISIS,
    "struggling": TIER_2_STRUGGLING,
    "solid": TIER_3_SOLID,
    "exceptional": TIER_4_EXCEPTIONAL,
}


def get_tier_from_score(overall_score: float) -> str:
    """
    Determine tier name from overall score.

    Args:
        overall_score: Game score (0-100)

    Returns:
        Tier name: "crisis", "struggling", "solid", or "exceptional"
    """
    if overall_score < 40:
        return "crisis"
    elif overall_score < 60:
        return "struggling"
    elif overall_score < 80:
        return "solid"
    else:
        return "exceptional"


def get_framework(overall_score: float) -> StrategicFramework:
    """
    Get the appropriate strategic framework for a given score.

    Args:
        overall_score: Game score (0-100)

    Returns:
        StrategicFramework object with all guidance
    """
    tier = get_tier_from_score(overall_score)
    return TIER_FRAMEWORKS[tier]


def get_section_inclusion_matrix() -> Dict[str, Dict[str, bool]]:
    """
    Generate a matrix showing which sections to include for each tier.

    Returns:
        Dict mapping section names to tier inclusion (True/False)
    """
    all_sections = set()
    for framework in TIER_FRAMEWORKS.values():
        all_sections.update(framework.included_sections)
        all_sections.update(framework.excluded_sections)

    matrix = {}
    for section in sorted(all_sections):
        matrix[section] = {
            "crisis": section in TIER_1_CRISIS.included_sections,
            "struggling": section in TIER_2_STRUGGLING.included_sections,
            "solid": section in TIER_3_SOLID.included_sections,
            "exceptional": section in TIER_4_EXCEPTIONAL.included_sections,
        }

    return matrix


def print_framework_summary(overall_score: float):
    """Print a summary of the framework for a given score."""
    framework = get_framework(overall_score)

    print(f"\n{'='*80}")
    print(f"STRATEGIC FRAMEWORK FOR SCORE: {overall_score:.1f}/100")
    print(f"{'='*80}\n")

    print(f"**Tier**: {framework.tier_name} ({framework.score_range})")
    print(f"**Strategic Frame**: {framework.primary_frame}")
    print(f"**Key Question**: {framework.key_question}")
    print(f"**Tone**: {framework.tone}\n")

    print(f"**Priority Sections** (in order):")
    for section in framework.priority_sections:
        print(f"  {section}")

    print(f"\n**Language Guidelines**:")
    for guideline in framework.language_guidelines[:6]:
        print(f"  {guideline}")

    print(f"\n{'='*80}\n")


# Example usage and testing
if __name__ == "__main__":
    # Test all 4 tiers
    test_scores = [35, 55, 72, 88]

    for score in test_scores:
        print_framework_summary(score)

    print("\n" + "="*80)
    print("SECTION INCLUSION MATRIX")
    print("="*80 + "\n")

    matrix = get_section_inclusion_matrix()

    # Print first 10 sections as example
    example_sections = list(matrix.keys())[:10]
    print(f"{'Section':<40} | Crisis | Struggling | Solid | Exceptional")
    print("-" * 90)

    for section in example_sections:
        crisis = "✅" if matrix[section]["crisis"] else "❌"
        struggling = "✅" if matrix[section]["struggling"] else "❌"
        solid = "✅" if matrix[section]["solid"] else "❌"
        exceptional = "✅" if matrix[section]["exceptional"] else "❌"

        print(f"{section:<40} | {crisis:^6} | {struggling:^10} | {solid:^5} | {exceptional:^11}")

    print("\n" + "="*80)
    print("EXAMPLE SECTION REWRITES")
    print("="*80 + "\n")

    print("MARKET POSITIONING - Crisis Tier (Score: 35)")
    print("-" * 80)
    print(TIER_1_CRISIS.section_rewrites["market_positioning"])

    print("\n\nMARKET POSITIONING - Exceptional Tier (Score: 88)")
    print("-" * 80)
    print(TIER_4_EXCEPTIONAL.section_rewrites["market_positioning"])
