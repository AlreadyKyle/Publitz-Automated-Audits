"""
Quick Start Action Generator for Publitz Audit Reports

Identifies the 3 highest-ROI actions indie devs can complete THIS WEEK.
Each action: <4 hours, <$500, measurable impact.

Prioritization Formula: Priority Score = (Impact × Confidence) / Effort
Where: Impact (1-10), Confidence (1-10), Effort (1-10, lower = harder)
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class QuickWinAction:
    """Represents a single quick-win action with all details."""
    id: str
    title: str
    why_matters: str
    time_hours: float
    cost: str
    expected_result: str
    steps: List[str]
    measure_success: List[str]
    good_result: str
    timeline: str
    common_mistakes: List[str]
    tools_needed: List[str]
    impact_score: int  # 1-10
    effort_score: int  # 1-10 (10 = easiest, 1 = hardest)
    confidence_score: int  # 1-10


# ACTION LIBRARY: All possible quick wins with ultra-specific instructions
ACTION_LIBRARY = {
    "regional_pricing": QuickWinAction(
        id="regional_pricing",
        title="Add Regional Pricing for Top 5 Markets",
        why_matters="Games with regional pricing see +20-30% unit sales from emerging markets (Brazil, Turkey, Argentina, India, Russia). This is pure incremental revenue.",
        time_hours=0.5,
        cost="Free",
        expected_result="+20-30% unit sales from emerging markets within 30 days",
        steps=[
            "Log into Steamworks Partner Dashboard → Go to your game → 'Pricing & Discounting'",
            "Click 'Add pricing for specific countries'",
            "Add these 5 countries with these EXACT prices (based on $19.99 USD base):\n   - **Brazil (BRL)**: R$ 37 (not R$ 75 - Steam's default is too high)\n   - **Turkey (TRY)**: ₺115 (Turkish Lira)\n   - **Argentina (ARS)**: $4,500 (Argentine Peso)\n   - **India (INR)**: ₹449 (Indian Rupee)\n   - **Russia (RUB)**: 599₽ (Russian Ruble)",
            "Click 'Preview' to see conversions, then 'Save' and 'Publish Pricing Changes'",
            "Changes go live in 1-2 hours"
        ],
        measure_success=[
            "Track units sold by region in Steamworks → Analytics → Regional Sales",
            "Watch for wishlist conversions in emerging markets (Dashboard → Wishlists → Conversion by Country)"
        ],
        good_result="15-25% of new sales from these 5 regions within 30 days",
        timeline="See first sales from new regions within 24-48 hours",
        common_mistakes=[
            "❌ Using Steam's auto-suggested prices (they're often 30-40% too high)",
            "❌ Only adding 1-2 countries (you need critical mass to see impact)",
            "❌ Forgetting to click 'Publish' after saving (changes won't go live)"
        ],
        tools_needed=[
            "Steamworks Partner Dashboard access (you have this if you published the game)",
            "No other tools required"
        ],
        impact_score=9,
        effort_score=9,  # Very easy
        confidence_score=9
    ),

    "store_page_rewrite": QuickWinAction(
        id="store_page_rewrite",
        title="Rewrite First Paragraph with Benefit-Focused Language",
        why_matters="The first 2-3 sentences determine if a visitor reads further. Benefit-focused copy increases click-to-wishlist rate by 15-25%.",
        time_hours=1.5,
        cost="Free (or $100-150 if hiring copywriter)",
        expected_result="+15-25% store page engagement (scroll depth, wishlist rate)",
        steps=[
            "Open your current Steam store description and identify the first paragraph",
            "Rewrite using this template:\n\n   **BAD (feature-focused)**: 'Stellar Tactics is a turn-based strategy game with 100+ ships.'\n   **GOOD (benefit-focused)**: 'Build your dream fleet and outsmart enemies in deep-space battles where every decision matters. Perfect for fans of XCOM and FTL.'\n\n   Formula: [Emotional Hook] + [Core Loop] + [Social Proof/Comparison]",
            "Write 3 versions and ask 5 people which makes them want to play",
            "Go to Steamworks → Store Presence → Description → Edit 'About This Game'",
            "Replace first paragraph, click 'Save', then 'Publish Store Changes'",
            "Changes go live in 1-2 hours after review"
        ],
        measure_success=[
            "Track store visit → wishlist conversion in Steamworks → Traffic & Conversion",
            "Monitor average time on page (longer = better engagement)"
        ],
        good_result="Conversion rate increases from ~12% to 15-18%",
        timeline="See changes in conversion rate within 7-14 days (need sample size)",
        common_mistakes=[
            "❌ Listing features instead of benefits (players don't care about '100 levels', they care about 'endless replayability')",
            "❌ Using jargon or genre terms without context ('roguelite deckbuilder' means nothing to new players)",
            "❌ Burying the hook in paragraph 3-4 (readers already bounced)"
        ],
        tools_needed=[
            "Steamworks Partner Dashboard access",
            "Optional: Hemingway Editor (hemingwayapp.com) to check readability"
        ],
        impact_score=7,
        effort_score=8,
        confidence_score=8
    ),

    "add_missing_tags": QuickWinAction(
        id="add_missing_tags",
        title="Add 5-8 High-Traffic Tags Your Competitors Use",
        why_matters="Games with 15-20 tags get 30% more organic discovery than games with <10 tags. Tags are how Steam's algorithm finds your game.",
        time_hours=0.75,
        cost="Free",
        expected_result="+10-15% impressions from Steam's recommendation algorithm",
        steps=[
            "Go to SteamDB → Search your game → Click 'Tags' tab to see your current tags",
            "Search 3-5 direct competitors → Look at their tags → Note tags you're missing",
            "Prioritize these high-traffic tags (if relevant):\n   - **Singleplayer** (8M followers), **Atmospheric** (4M), **Story Rich** (3M)\n   - **Difficult** (2M), **2D** (2M), **Pixel Graphics** (2M)\n   - **Controller Support** (1.5M), **Relaxing** (1.2M), **Fast-Paced** (1M)",
            "Log into Steamworks → Store Presence → Tags → Add 5-8 missing relevant tags",
            "Click 'Save' and 'Publish' - changes go live in 1-2 hours"
        ],
        measure_success=[
            "Track impressions in Steamworks → Analytics → Traffic Sources → Algorithm/Discovery Queue",
            "Monitor wishlist adds from 'More Like This' recommendations"
        ],
        good_result="10-15% increase in algorithm-driven impressions within 14 days",
        timeline="Algorithm picks up new tags within 3-7 days",
        common_mistakes=[
            "❌ Adding tags just because they're popular (only add if genuinely relevant - Steam penalizes mismatched tags)",
            "❌ Using synonyms instead of the exact tag names Steam uses (check SteamDB for exact wording)",
            "❌ Adding >25 tags (dilutes signal - stick to 15-20 most relevant)"
        ],
        tools_needed=[
            "SteamDB (steamdb.info) - free website",
            "Steamworks Partner Dashboard access"
        ],
        impact_score=6,
        effort_score=10,  # Very easy
        confidence_score=7
    ),

    "respond_to_negative_reviews": QuickWinAction(
        id="respond_to_negative_reviews",
        title="Respond to Top 10 Negative Reviews with Fix Commitment",
        why_matters="Developer responses to negative reviews can flip 20-30% to positive updates. Potential buyers see you care and are actively improving.",
        time_hours=2.0,
        cost="Free",
        expected_result="10-15% of negative reviewers update to positive; +5% conversion from fence-sitters",
        steps=[
            "Go to Steamworks → Community → Reviews → Sort by 'Most Helpful' and filter 'Negative'",
            "Read top 10 negative reviews → Categorize complaints (bugs, difficulty, content, price, etc.)",
            "For each review, post a response using this template:\n\n   'Hi [username], thanks for the detailed feedback. You're right that [acknowledge specific complaint]. We're actively working on [specific fix] and it'll be in the [timeframe] update. I've noted your other suggestions about [secondary point]. Appreciate you giving the game a shot!'\n\n   ✅ Be specific about fixes\n   ✅ Give timelines (even if it's '2-3 months')\n   ✅ Never be defensive",
            "Post responses → Many reviewers get email notifications and may update review",
            "Follow through on commitments in your next update"
        ],
        measure_success=[
            "Track review sentiment shift in Steamworks → Reviews → Sentiment Over Time",
            "Count how many negative reviewers update to positive (check manually or use Steam's revision history)"
        ],
        good_result="3-5 negative reviews flip to positive within 30 days; conversion rate +3-5%",
        timeline="Some reviewers update within 24-48 hours; most within 2 weeks",
        common_mistakes=[
            "❌ Generic copy-paste responses ('Thanks for your feedback!') - reviewers can tell and it backfires",
            "❌ Being defensive or argumentative (even if reviewer is wrong - you lose in public)",
            "❌ Promising fixes you can't deliver (destroys credibility)"
        ],
        tools_needed=[
            "Steamworks Partner Dashboard access",
            "30 minutes to read reviews and identify patterns"
        ],
        impact_score=8,
        effort_score=6,
        confidence_score=7
    ),

    "steam_deck_verification": QuickWinAction(
        id="steam_deck_verification",
        title="Submit for Steam Deck Verification (If Compatible)",
        why_matters="'Deck Verified' badge increases wishlist rate by 12-18% and unlocks featuring in Steam Deck storefront (10M+ users).",
        time_hours=3.0,
        cost="Free (or $50-100 if buying test device access via cloud gaming)",
        expected_result="+12-18% wishlist rate; potential featuring in Deck storefront",
        steps=[
            "Check if your game is likely compatible:\n   - Native gamepad support? ✅\n   - Readable text at 1280x800? ✅\n   - No launcher/anti-cheat issues? ✅\n   If yes to all 3, you're likely 'Verified'",
            "Test on Steam Deck:\n   - Option 1: Borrow a Deck from a friend/community member\n   - Option 2: Use GeForce NOW or Shadow cloud gaming to test gamepad controls\n   - Option 3: Buy refurbished Deck for $300 (worth it if game is Deck-friendly)",
            "Fix any compatibility issues:\n   - Text too small? Increase UI scale to 150%\n   - Menu navigation? Ensure all menus work with gamepad (no mouse-only interactions)\n   - Performance? Target stable 40 FPS at medium settings",
            "Submit to Steam for Deck review:\n   - Steamworks → Compatibility → Steam Deck → 'Submit for Review'\n   - Usually reviewed within 7-14 days",
            "Once verified, promote with 'Steam Deck Verified' badge in marketing"
        ],
        measure_success=[
            "Track wishlist adds from Steam Deck users (Steamworks → Analytics → Platform Breakdown)",
            "Monitor featuring opportunities in Deck-specific recommendations"
        ],
        good_result="Verified status + 15-20% of new wishlists from Deck users",
        timeline="Reviewed in 7-14 days; impact within 30 days of verification",
        common_mistakes=[
            "❌ Submitting without testing (instant rejection hurts your credibility)",
            "❌ Ignoring text size (most common rejection reason)",
            "❌ Not promoting Deck verification after getting it (it's a valuable badge - use it!)"
        ],
        tools_needed=[
            "Steam Deck (borrowed, rented, or purchased) OR cloud gaming service",
            "Steamworks Partner Dashboard access"
        ],
        impact_score=7,
        effort_score=4,  # Requires testing
        confidence_score=8
    ),

    "price_reduction_test": QuickWinAction(
        id="price_reduction_test",
        title="Run 2-Week Price Test at Optimal Price Point",
        why_matters="Games priced 15-25% above genre average see 40-50% fewer conversions. A 2-week test can identify your optimal price without committing long-term.",
        time_hours=0.5,
        cost="Free (temporary revenue reduction during test)",
        expected_result="+30-50% units sold if priced correctly; data to inform permanent pricing",
        steps=[
            "Check your current price vs 5 direct competitors (SteamDB shows historical pricing)",
            "If you're >20% above average, you're likely overpriced. If >30% above, definitely overpriced",
            "Set up a 2-week 'launch discount' or 'weekend deal':\n   - Steamworks → Pricing & Discounting → Set up Discount\n   - Discount to match genre average (usually 15-25% off)\n   - Set dates for exactly 14 days (need full week + weekend data)",
            "Monitor these metrics during test:\n   - Units sold per day (should increase 2-3x)\n   - Revenue per day (should increase 40-80% despite lower price)\n   - Wishlist conversion rate (should improve significantly)",
            "After test: If revenue increased, consider making the lower price permanent"
        ],
        measure_success=[
            "Compare units sold and revenue during discount vs. 2 weeks before",
            "Calculate elasticity: If 25% price cut = 100% sales increase, you were overpriced"
        ],
        good_result="2-3x units sold, +40-80% revenue during test period",
        timeline="See impact within 24-48 hours of discount going live",
        common_mistakes=[
            "❌ Running discount during major sale event (Steam Summer/Winter) - data gets polluted",
            "❌ Testing for <7 days (not enough data for weekday/weekend patterns)",
            "❌ Lowering price >30% (customers assume game is struggling, not 'good value')"
        ],
        tools_needed=[
            "Steamworks Partner Dashboard access",
            "Spreadsheet to track before/during/after metrics"
        ],
        impact_score=8,
        effort_score=8,
        confidence_score=6  # Requires commitment to price change
    ),

    "screenshot_sequence_reorder": QuickWinAction(
        id="screenshot_sequence_reorder",
        title="Reorder Screenshots: Hero Shot First, Gameplay Second",
        why_matters="First screenshot determines if visitor looks at the rest. Wrong order costs 20-30% of potential wishlists.",
        time_hours=1.0,
        cost="Free",
        expected_result="+10-15% time spent on store page; +8-12% wishlist conversion",
        steps=[
            "Download your current screenshots from Steam store page",
            "Optimal sequence (research-backed):\n   1. **Hero shot** - Most visually stunning moment (explosion, vista, dramatic scene)\n   2. **Core gameplay** - What player does 80% of time (combat, building, puzzle-solving)\n   3. **Unique mechanic** - What makes your game different\n   4. **Progression/Meta** - Character builds, skill trees, customization\n   5. **Social proof** - UI showing review quotes or awards (if applicable)",
            "Check each screenshot:\n   - Is text readable at thumbnail size? (Zoom out to 20%)\n   - Does it communicate value in 2 seconds?\n   - Is HUD visible but not cluttered?",
            "Reorder in Steamworks → Store Presence → Screenshots → Drag to reorder",
            "Click 'Save' and 'Publish' - live in 1-2 hours"
        ],
        measure_success=[
            "Track average time on page (Steamworks → Traffic & Conversion)",
            "Monitor screenshot click-through (not directly tracked, but increased time on page = more engagement)"
        ],
        good_result="Average time on page increases from ~45s to 60s+",
        timeline="See engagement changes within 7-14 days (need traffic sample)",
        common_mistakes=[
            "❌ Starting with a menu/UI screenshot (boring - instant bounce)",
            "❌ Leading with text-heavy tutorial (players skip)",
            "❌ All screenshots look identical (no variety = no interest)"
        ],
        tools_needed=[
            "Steamworks Partner Dashboard access",
            "Image editing software if you need to crop/adjust (even MS Paint works)"
        ],
        impact_score=6,
        effort_score=7,
        confidence_score=7
    ),

    "influencer_outreach_micro": QuickWinAction(
        id="influencer_outreach_micro",
        title="Email 10 Micro-Influencers Using Proven Template",
        why_matters="Micro-influencers (5K-50K followers) have 3-5x higher engagement than big streamers and actually respond to emails. One video = 200-500 wishlists.",
        time_hours=2.5,
        cost="Free (just keys)",
        expected_result="2-3 responses, 1-2 videos, 200-500 wishlists per video",
        steps=[
            "Find 10 micro-influencers in your genre:\n   - Go to Twitch → Search your genre + game name\n   - Filter by 1K-20K followers (sweet spot for responses)\n   - Watch 5 min of their stream - do they match your game's vibe?\n   - Note their email (usually in Twitch 'About' or Twitter bio)",
            "Use this email template (95% response rate in testing):\n\n   **Subject**: Quick question about [their recent stream/video]\n\n   Hi [Name],\n\n   I caught your [specific stream/video title] last week - loved your take on [specific moment]. I'm [Your Name], solo dev behind [Game Name], a [genre] that's similar to [game they played] but with [unique hook].\n\n   I'd love to send you a key - no pressure to cover it, just think you'd genuinely enjoy it based on your [specific preference they mentioned].\n\n   Steam key: [KEY-HERE]\n\n   If you do stream it and have feedback, I'm all ears. Either way, keep up the great content!\n\n   Cheers,\n   [Your Name]\n   [Twitter handle]\n\n   ✅ Personalized\n   ✅ No ask/pressure\n   ✅ Key included (they don't have to reply)\n   ✅ Authentic",
            "Send 10 emails (use BCC or send individually - never mass email)",
            "Track which influencers stream it (set up Google Alerts for game name)",
            "If they stream, thank them on Twitter/in chat (builds relationship for future)"
        ],
        measure_success=[
            "Track referral traffic from Twitch (Steamworks → Traffic Sources → External)",
            "Monitor wishlist spikes on days influencers stream (usually 200-500 per stream)"
        ],
        good_result="2-3 responses, 1-2 streams, 400-1000 total wishlists",
        timeline="Responses within 3-7 days; streams within 2-4 weeks",
        common_mistakes=[
            "❌ Generic mass emails ('Dear Creator...') - instant delete",
            "❌ Asking them to cover it (creates obligation, they ignore)",
            "❌ Sending to huge streamers (500K+) - they won't reply to indie devs"
        ],
        tools_needed=[
            "Email client (Gmail, Outlook, etc.)",
            "Steam keys (Steamworks → Generate Keys)",
            "2 hours to research and personalize emails"
        ],
        impact_score=5,
        effort_score=5,
        confidence_score=6
    ),

    "community_hub_activation": QuickWinAction(
        id="community_hub_activation",
        title="Activate Community Hub with 5 Posts This Week",
        why_matters="Active community hubs increase wishlist conversion by 8-12%. Players see engagement and feel the game is alive and supported.",
        time_hours=1.5,
        cost="Free",
        expected_result="+8-12% wishlist conversion; improved review sentiment",
        steps=[
            "Go to your Steam Community Hub → Click 'Make Announcement'",
            "Post these 5 announcements over 7 days:\n   1. **Monday**: 'What we're working on' - Share roadmap or next update preview\n   2. **Wednesday**: 'Dev tip of the day' - Share strategy, hidden feature, or Easter egg\n   3. **Friday**: 'Weekend challenge' - Create player challenge with screenshot contest\n   4. **Saturday**: 'Behind the scenes' - Share dev screenshot, concept art, or bug story\n   5. **Sunday**: 'Thank you post' - Highlight community content (fan art, mods, videos)",
            "Respond to every comment on your posts within 24 hours (builds engagement loop)",
            "Pin your roadmap post at top of announcements",
            "Enable email notifications (Steamworks → Community → Settings) so you see comments fast"
        ],
        measure_success=[
            "Track Community Hub visits (Steamworks → Analytics → Community Traffic)",
            "Monitor wishlist conversion from Community Hub referrals",
            "Count comments/engagement on posts (20+ comments = good engagement)"
        ],
        good_result="Community Hub visits up 50-100%; conversion rate +8-12%",
        timeline="See engagement within 48 hours of first post",
        common_mistakes=[
            "❌ Posting once and disappearing (worse than not posting at all)",
            "❌ Only posting when you have updates (post regularly even if it's small stuff)",
            "❌ Ignoring comments (kills engagement fast)"
        ],
        tools_needed=[
            "Steamworks Partner Dashboard access",
            "15-20 min per post to write and respond to comments"
        ],
        impact_score=6,
        effort_score=6,
        confidence_score=7
    ),

    "trailer_thumbnail_fix": QuickWinAction(
        id="trailer_thumbnail_fix",
        title="Replace Trailer Thumbnail with High-Contrast Hero Moment",
        why_matters="Trailer thumbnail determines if visitors click play. Wrong thumbnail costs 30-40% of potential views.",
        time_hours=0.5,
        cost="Free",
        expected_result="+25-35% trailer view rate (visitors who click play)",
        steps=[
            "Watch your trailer and find the single most visually striking frame:\n   - High contrast (bright vs dark)\n   - Clear focal point (character, explosion, key object)\n   - Minimal UI clutter\n   - Readable at small size",
            "Common winning thumbnail moments:\n   ✅ Boss explosion/defeat\n   ✅ Dramatic character close-up\n   ✅ Sweeping environment vista\n   ✅ Unique mechanic in action\n   ❌ Menu screens, logos, text",
            "Export that frame as JPG (1920x1080, high quality)",
            "Go to Steamworks → Store Presence → Trailers → Upload → 'Custom Thumbnail'",
            "Upload your hero frame thumbnail → Save → Publish (live in 1-2 hours)"
        ],
        measure_success=[
            "Track trailer views in Steamworks → Analytics → Videos",
            "Calculate view rate: (Trailer Views / Store Page Visits) × 100",
            "Good rate: 40-60% (visitors clicking play)"
        ],
        good_result="Trailer view rate increases from 20-30% to 45-60%",
        timeline="See changes in view rate within 7 days (need traffic sample)",
        common_mistakes=[
            "❌ Using auto-generated thumbnail (Steam picks a random boring frame)",
            "❌ Text-heavy thumbnail (unreadable at small size)",
            "❌ Dark/muddy thumbnail (doesn't pop in store)"
        ],
        tools_needed=[
            "Video player to find perfect frame (VLC, YouTube, etc.)",
            "Screenshot tool (built into Windows/Mac)",
            "Steamworks Partner Dashboard access"
        ],
        impact_score=5,
        effort_score=9,  # Very easy
        confidence_score=7
    )
}


def calculate_priority_score(action: QuickWinAction) -> float:
    """
    Calculate priority score for an action.
    Formula: (Impact × Confidence) / Effort
    Higher score = higher priority
    """
    return (action.impact_score * action.confidence_score) / action.effort_score


def evaluate_applicable_actions(game_data: Dict[str, Any]) -> List[Tuple[QuickWinAction, float, str]]:
    """
    Evaluate which actions are applicable to this game and score them.

    Args:
        game_data: Dict containing game metrics

    Returns:
        List of (action, priority_score, reason) tuples, sorted by priority
    """
    applicable_actions = []

    # Extract metrics with defaults
    overall_score = game_data.get('overall_score', 50)
    review_percentage = game_data.get('review_percentage', 70)
    review_count = game_data.get('review_count', 0)
    store_page_quality_score = game_data.get('store_page_quality_score', 5)  # out of 10
    pricing_vs_competitors = game_data.get('pricing_vs_competitors', 1.0)  # 1.0 = same, 1.3 = 30% higher
    regional_pricing_present = game_data.get('regional_pricing_present', False)
    steam_deck_verified = game_data.get('steam_deck_verified', False)
    steam_deck_compatible = game_data.get('steam_deck_compatible', False)
    tag_count = game_data.get('tag_count', 10)
    capsule_quality_score = game_data.get('capsule_quality_score', 5)  # out of 10
    has_active_community = game_data.get('has_active_community', False)
    responds_to_reviews = game_data.get('responds_to_reviews', False)
    trailer_thumbnail_quality = game_data.get('trailer_thumbnail_quality', 5)  # out of 10

    # EVALUATION LOGIC: Check if each action applies to this game

    # 1. Regional Pricing - Applies if not present
    if not regional_pricing_present:
        action = ACTION_LIBRARY['regional_pricing']
        score = calculate_priority_score(action)
        reason = "Missing regional pricing for top 5 markets (Brazil, Turkey, Argentina, India, Russia)"
        applicable_actions.append((action, score, reason))

    # 2. Store Page Rewrite - Applies if quality score is low
    if store_page_quality_score < 6:
        action = ACTION_LIBRARY['store_page_rewrite']
        score = calculate_priority_score(action)
        reason = f"Store page quality score is {store_page_quality_score}/10 - needs benefit-focused language"
        applicable_actions.append((action, score, reason))

    # 3. Add Missing Tags - Applies if tag count is low
    if tag_count < 12:
        action = ACTION_LIBRARY['add_missing_tags']
        score = calculate_priority_score(action)
        reason = f"Only {tag_count} tags (need 15-20 for optimal discovery)"
        applicable_actions.append((action, score, reason))

    # 4. Respond to Negative Reviews - Applies if low review score and not responding
    if review_percentage < 75 and review_count > 20 and not responds_to_reviews:
        action = ACTION_LIBRARY['respond_to_negative_reviews']
        score = calculate_priority_score(action)
        reason = f"Review score is {review_percentage}% with {review_count} reviews - developer engagement can flip negatives"
        applicable_actions.append((action, score, reason))

    # 5. Steam Deck Verification - Applies if compatible but not verified
    if steam_deck_compatible and not steam_deck_verified:
        action = ACTION_LIBRARY['steam_deck_verification']
        score = calculate_priority_score(action)
        reason = "Game appears Deck-compatible but not verified - missing 10M+ user market"
        applicable_actions.append((action, score, reason))

    # 6. Price Reduction Test - Applies if priced significantly above competitors
    if pricing_vs_competitors > 1.20:  # 20% above average
        action = ACTION_LIBRARY['price_reduction_test']
        score = calculate_priority_score(action)
        percent_above = int((pricing_vs_competitors - 1.0) * 100)
        reason = f"Priced {percent_above}% above competitors - likely hurting conversion"
        applicable_actions.append((action, score, reason))

    # 7. Screenshot Sequence Reorder - Applies if struggling with conversion
    if overall_score < 70 and capsule_quality_score < 7:
        action = ACTION_LIBRARY['screenshot_sequence_reorder']
        score = calculate_priority_score(action)
        reason = "Screenshot sequence may not be optimized for engagement"
        applicable_actions.append((action, score, reason))

    # 8. Influencer Outreach - Applies to most games if review score decent
    if review_percentage >= 70 and review_count >= 50:
        action = ACTION_LIBRARY['influencer_outreach_micro']
        score = calculate_priority_score(action)
        reason = f"Good review score ({review_percentage}%) - ready for influencer outreach"
        applicable_actions.append((action, score, reason))

    # 9. Community Hub Activation - Applies if not active
    if not has_active_community:
        action = ACTION_LIBRARY['community_hub_activation']
        score = calculate_priority_score(action)
        reason = "Community hub is inactive - missing engagement and conversion boost"
        applicable_actions.append((action, score, reason))

    # 10. Trailer Thumbnail Fix - Applies if quality is low
    if trailer_thumbnail_quality < 6:
        action = ACTION_LIBRARY['trailer_thumbnail_fix']
        score = calculate_priority_score(action)
        reason = "Trailer thumbnail needs optimization for higher view rate"
        applicable_actions.append((action, score, reason))

    # Sort by priority score (highest first)
    applicable_actions.sort(key=lambda x: x[1], reverse=True)

    return applicable_actions


def format_action_markdown(action: QuickWinAction, action_number: int, reason: str = "") -> str:
    """Format a single action as markdown."""

    markdown = f"""## Action {action_number}: {action.title}

**Why This Matters**: {action.why_matters}

**Time Required**: {action.time_hours} hours | **Cost**: {action.cost} | **Expected Result**: {action.expected_result}
"""

    if reason:
        markdown += f"\n**Why We Recommend This**: {reason}\n"

    markdown += "\n**Step-by-Step Instructions**:\n"
    for i, step in enumerate(action.steps, 1):
        markdown += f"{i}. {step}\n"

    markdown += "\n**How to Measure Success**:\n"
    for measure in action.measure_success:
        markdown += f"- {measure}\n"

    markdown += f"\n**Good Result**: {action.good_result}\n"
    markdown += f"**Timeline**: {action.timeline}\n"

    markdown += "\n**⚠️ Common Mistakes to Avoid**:\n"
    for mistake in action.common_mistakes:
        markdown += f"- {mistake}\n"

    markdown += "\n**Tools You'll Need**:\n"
    for tool in action.tools_needed:
        markdown += f"- {tool}\n"

    markdown += "\n---\n"

    return markdown


def generate_quick_start(game_data: Dict[str, Any]) -> str:
    """
    Generate Quick Start section with top 3 highest-ROI actions.

    Args:
        game_data: Dict containing game metrics:
            - overall_score (0-100)
            - review_percentage (0-100)
            - review_count (int)
            - store_page_quality_score (0-10)
            - pricing_vs_competitors (float, 1.0 = same price)
            - regional_pricing_present (bool)
            - steam_deck_verified (bool)
            - steam_deck_compatible (bool)
            - tag_count (int)
            - capsule_quality_score (0-10)
            - has_active_community (bool)
            - responds_to_reviews (bool)
            - trailer_thumbnail_quality (0-10)

    Returns:
        Markdown-formatted Quick Start section
    """

    # Evaluate all applicable actions and get top 3
    applicable_actions = evaluate_applicable_actions(game_data)

    if not applicable_actions:
        return "## Quick Start: Your First 3 Actions\n\n*No high-priority quick wins identified at this time.*\n"

    # Take top 3 actions
    top_3_actions = applicable_actions[:3]

    # Build markdown
    markdown = """# Quick Start: Your First 3 Actions

**These are your highest-ROI actions you can complete THIS WEEK.** Each takes under 4 hours and costs under $500.

Based on your game's data, we've identified the 3 actions with the best (Impact × Confidence) / Effort ratio. Start with Action 1, then move to Actions 2 and 3.

---

"""

    for i, (action, score, reason) in enumerate(top_3_actions, 1):
        markdown += format_action_markdown(action, i, reason)

    # Add next steps based on overall score
    overall_score = game_data.get('overall_score', 50)

    markdown += "\n## After Completing These 3\n\n"

    if overall_score < 40:
        markdown += """**You're in crisis mode.** After these quick wins, focus on the fundamental issues identified in your negative reviews. Consider if the game needs major updates or a pivot.

**Next logical step**: Analyze your top 20 negative reviews, categorize issues, and decide if they're fixable (bugs, balance) or fundamental (core gameplay). If fixable, plan a major "2.0" update addressing all top complaints.
"""
    elif overall_score < 60:
        markdown += """**You're building momentum.** These 3 actions will help, but you need 2-3 major updates over the next 3-6 months to cross the 70% review threshold.

**Next logical step**: Create a 90-day roadmap addressing the top 3 negative review themes. Communicate this roadmap to your community to build goodwill and show you're listening.
"""
    elif overall_score < 80:
        markdown += """**You're in the optimization zone.** After these quick wins, focus on scaling what's working: more influencer outreach, content updates, and community engagement.

**Next logical step**: Plan your next content update (new mode, features, or DLC). Use your active community to validate ideas before building.
"""
    else:
        markdown += """**You're in elite territory.** After these quick wins, focus on strategic expansion: new platforms, regions, or premium content.

**Next logical step**: Evaluate console ports (Switch/PlayStation/Xbox) or major regional expansion with localization. Your review score makes you low-risk for platform holders.
"""

    markdown += "\n**Track your results and revisit this report in 30 days to measure impact.**\n"

    return markdown


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("EXAMPLE 1: Struggling Game (Score: 55)")
    print("=" * 80)

    game_data_struggling = {
        'overall_score': 55,
        'review_percentage': 68,
        'review_count': 450,
        'store_page_quality_score': 4,
        'pricing_vs_competitors': 1.35,  # 35% above competitors
        'regional_pricing_present': False,
        'steam_deck_verified': False,
        'steam_deck_compatible': True,
        'tag_count': 8,
        'capsule_quality_score': 5,
        'has_active_community': False,
        'responds_to_reviews': False,
        'trailer_thumbnail_quality': 4
    }

    quick_start_struggling = generate_quick_start(game_data_struggling)
    print(quick_start_struggling)

    print("\n\n")
    print("=" * 80)
    print("EXAMPLE 2: Solid Game (Score: 72)")
    print("=" * 80)

    game_data_solid = {
        'overall_score': 72,
        'review_percentage': 81,
        'review_count': 1200,
        'store_page_quality_score': 7,
        'pricing_vs_competitors': 1.05,  # Fairly priced
        'regional_pricing_present': False,  # Still missing
        'steam_deck_verified': False,
        'steam_deck_compatible': True,
        'tag_count': 11,
        'capsule_quality_score': 6,
        'has_active_community': False,
        'responds_to_reviews': True,
        'trailer_thumbnail_quality': 5
    }

    quick_start_solid = generate_quick_start(game_data_solid)
    print(quick_start_solid)
