# Negative Review Analyzer - Example Output

## Overview

For struggling games (<80% positive reviews), the Negative Review Analyzer extracts actionable insights from negative Steam reviews to determine what's broken and how to fix it.

Instead of generic advice like "improve your game", it provides:
- **Specific complaint categorization** with percentages
- **Fix-it plans** with immediate and short-term actions
- **Salvageability assessment** (can this game be saved?)

## When to Use

This analyzer is most valuable for:
- Games with **<80% positive reviews** (struggling/crisis tier)
- Games receiving complaints but you're unsure what to fix first
- Decision points: Should we fix this game or pivot to something new?

## Example Output

### Test Game: Struggling Indie Roguelike (65% Positive)

```markdown
# Negative Review Analysis: Dungeon Crawler X

**Current Review Score**: 65.0% positive
**Reviews Analyzed**: 50 negative reviews
**Analysis Date**: 2025-01-23

---

## Executive Summary

Players report three major issues: frequent crashes on level transitions (42% of negative reviews),
repetitive gameplay with only 3 enemy types (38%), and confusing UI with no tutorial (31%).
Critical technical issues are fixable within 30 days, but core content needs expansion.

**Breakdown by Category**:
- 🔴 Critical Issues: 42%
- ⚠️ Design Problems: 38%
- ✅ Polish Issues: 31%
- 📢 Expectation Mismatches: 15%
- ➖ Subjective Preferences: 8%

---

## Salvageability Assessment for Dungeon Crawler X

**Issue Breakdown**:
- 🔴 Critical issues: 42% (Must be fixed immediately)
- ⚠️ Design problems: 38% (Require major rework or acceptance)
- ✅ Polish issues: 31% (Addressable with updates)
- 📢 Expectation mismatches: 15% (Communication/pricing fixes)
- ➖ Subjective preferences: 8% (Accept these)

**Verdict**: Salvageable ✅

**Reasoning**:
While 42% of complaints are critical crashes, these are technical issues that can be debugged and fixed.
The 38% design complaints about repetitive gameplay are concerning but addressable through content updates.
Combined with fixable polish issues (31%), approximately 73% of problems can be resolved through dedicated development.
The game's core concept appears sound based on positive reviews - execution needs improvement.

**If You Persevere** (Fix Current Game):

**Required Investment**:
- Development time: 8-12 person-weeks
- Estimated cost: $15,000-$25,000 (assuming $100/hr contract rate)
- Team size needed: 1 senior dev (crash fixes), 1 content designer (enemy variety), 1 UI designer

**Timeline to Meaningful Improvement**:
- Emergency fixes: 2 weeks (crash fixes, emergency patches)
- Core fixes complete: 2 months (content expansion, UI overhaul)
- Community sentiment shift: 3-4 months (reviews take time to reflect improvements)

**Probability of Recovery**: 70%
- Best case: Review score improves to 82-85% (achievable with all fixes)
- Base case: Review score improves to 75-78% (crash fixes + some content)
- Worst case: Review score stays at 65% (if fixes don't address root causes)

**Critical Success Factors**:
1. Fix level transition crashes within 2 weeks - this is killing retention
2. Add 5+ new enemy types in next major update - variety is the #1 complaint
3. Create 10-minute interactive tutorial - 31% cite confusion as reason for negative review

**If You Pivot** (Learn and Move On):

**Key Learnings to Carry Forward**:
1. Ship with more content variety from day 1 - players expect 10+ enemy types, not 3
2. QA test on all advertised platforms thoroughly - level transition code was clearly not tested
3. Tutorial is not optional for complex roguelikes - assume players are new to genre

**Pivot Recommendations**:
1. Take the core combat system (which players praise) and build a different game type around it
2. Target casual roguelike audience instead of hardcore - they're more forgiving of content volume
3. Keep: tight controls and combat feel. Abandon: current level generation system (source of crashes)

**Decision Framework**:
Choose PERSEVERE if:
- You have $20,000 and 3 months available
- You're emotionally ready for 3 months of intense bugfixing and content creation
- You believe in the core concept despite execution issues

Choose PIVOT if:
- Budget is <$15,000 or timeline is <2 months
- Core gameplay loop is fundamentally flawed (it's not in this case)
- You've lost passion for this specific project

---

**Recommendation**: PERSEVERE with immediate focus on crash fixes (week 1-2),
followed by content expansion (weeks 3-8). The game's foundation is solid - execution needs work.

---

# Fix-It Recommendations

## Critical Issue: Level Transition Crashes

**Complaint Frequency**: 42% of negative reviews (21 reviews)
**Severity**: 🔴 Critical
**Fixability**: ✅ Fixable

**Representative Quotes**:
- "Game crashes every time I try to go to level 4. Literally unplayable past level 3."
- "Constant crashes when transitioning between dungeons. Lost 3 hours of progress."
- "Crashes 100% of the time on GTX 1060 when loading new floor"

**Root Cause Analysis**:
Memory leak or asset loading issue in level transition code. Likely related to improper cleanup
of previous level assets before loading new level. GPU-specific crashes suggest shader compilation
or VRAM management issue.

**Fix-It Plan**:

**Immediate (This Week)**:
1. Add auto-save before level transitions as emergency band-aid (prevents progress loss)
2. Add crash reporting to identify exact failure point (integrate Sentry or similar)
3. Disable level transition animations temporarily if they're the source

**Short-Term (30 Days)**:
1. Profile memory usage during level transitions - identify leak source
2. Implement proper asset unloading before new level load (dispose previous level completely)
3. Add GPU-specific shader pre-compilation for GTX 1060/1070 series (known issue)
4. Beta test with affected users before releasing patch
5. Roll out crash fix patch with detailed changelog

**Communication Plan**:
1. Post Steam announcement TODAY: "We're aware of level transition crashes and are investigating.
   Temporary fix coming this week (auto-save before transitions). Full fix ETA: 2 weeks."
2. Promise specific fix timeline: "Crash fix patch releasing [DATE]"
3. Follow up with beta branch announcement: "Help us test the crash fix on beta branch before release"

**Expected Impact**:
- Review score improvement: +8-12% (from 65% to 73-77%)
- Estimated timeline: 2 weeks for fix, 4 weeks for review score to reflect
- Confidence level: High (technical issue with clear solution path)
- Success metrics: Crash reports drop to <5% of sessions, negative review rate decreases by 50%

---

## Design Problem: Repetitive Gameplay Loop

**Complaint Frequency**: 38% of negative reviews (19 reviews)
**Severity**: 🟡 Moderate
**Fixability**: ⚠️ Requires Resources

**Representative Quotes**:
- "Only 3 enemy types. Gets boring after 30 minutes."
- "Every run feels exactly the same. No variety in encounters."
- "Needs more enemy types, more items, more EVERYTHING"

**Root Cause Analysis**:
Shipped with minimum viable content to meet launch deadline. Players expected roguelike depth
(10+ enemy types, 50+ items) but got roguelite breadth (3 enemies, 15 items). Fundamental
content volume issue, not design flaw.

**Fix-It Plan**:

**Immediate (This Week)**:
1. Can't fix content volume immediately - focus on communicating roadmap
2. Review positive reviews to understand what variety DOES exist that players like

**Short-Term (30 Days)**:
1. Design and implement 5 new enemy types with unique mechanics (not just stat variations)
2. Add 20 new items/weapons with meaningful gameplay changes
3. Create 3 new biome types with different visual themes and enemy compositions
4. Add procedural modifier system (random run modifiers like "enemies move 50% faster")
5. Beta test with engaged community members

**Communication Plan**:
1. Announce content roadmap: "We hear you. 5 new enemy types coming in v1.1 (DATE)"
2. Share dev blog with enemy concept art and mechanics descriptions
3. Create feedback loop: "Which enemy type should we add next? Vote in Discord"

**Expected Impact**:
- Review score improvement: +5-8% (from current to 70-73%)
- Estimated timeline: 6-8 weeks for content creation, 2-3 months for review impact
- Confidence level: Medium (content quality matters, not just quantity)
- Success metrics: Average session length increases by 40%, "boring" complaints drop by 60%

---

## Polish Issue: Confusing UI and No Tutorial

**Complaint Frequency**: 31% of negative reviews (16 reviews)
**Severity**: 🟢 Minor (but high impact)
**Fixability**: ✅ Fixable

**Representative Quotes**:
- "Took me 20 minutes to figure out how to upgrade weapons. No tutorial at all."
- "UI is confusing. Which stat does what? Game doesn't explain anything."
- "Quit after 10 minutes because I couldn't figure out the inventory system"

**Root Cause Analysis**:
Assumed players familiar with roguelike genre conventions. UI uses icons without labels.
No first-run tutorial or tooltips. Classic developer curse of knowledge.

**Fix-It Plan**:

**Immediate (This Week)**:
1. Add text labels to all UI icons (immediate clarity improvement)
2. Add hover tooltips explaining what each stat means
3. Add "?" help button to main UI screens

**Short-Term (30 Days)**:
1. Create 10-minute interactive tutorial (first-run only, skippable)
2. Tutorial teaches: movement, combat, upgrading, inventory management
3. Add "helpful hints" popup system for first 30 minutes of gameplay
4. Create in-game manual accessible from pause menu
5. A/B test tutorial skip rate (if >50% skip, it's too long)

**Communication Plan**:
1. Announce: "Tutorial update coming [DATE] - no more confusion!"
2. Create YouTube tutorial video as interim solution
3. Link tutorial video in Steam store page description

**Expected Impact**:
- Review score improvement: +3-5% (from current to 68-70%)
- Estimated timeline: 3 weeks for tutorial development
- Confidence level: High (clear problem, clear solution)
- Success metrics: Refund rate drops by 30%, "confusing" complaints drop by 70%

---

## Expectation Mismatch: Price vs. Content

**Complaint Frequency**: 15% of negative reviews (8 reviews)
**Severity**: 🟢 Minor
**Fixability**: ✅ Fixable

**Representative Quotes**:
- "$19.99 for 2 hours of content? That's a rip-off"
- "Not worth the asking price. Should be $9.99 max"
- "Wait for a sale. Not enough content for $20"

**Root Cause Analysis**:
Priced as a full roguelike ($19.99) but shipped with early access content volume.
Competitors offer 10+ hours at same price point. Either add more content or reduce price.

**Fix-It Plan**:

**Immediate (This Week)**:
1. Run 25% off sale this week ($14.99) to align price with current content
2. Update store page to clearly state "Early Access - more content coming"

**Short-Term (30 Days)**:
1. Decide: Add enough content to justify $19.99, or permanently reduce to $14.99
2. If keeping $19.99: Content roadmap must show clear path to 10+ hours
3. If reducing price: Communicate value honestly ("We listened to feedback on price")
4. Add "hours of content" estimate to store page (be honest: "3-5 hours current, 10+ hours planned")

**Communication Plan**:
1. If reducing price: "Based on community feedback, we're reducing price to $14.99 while we add more content"
2. If keeping price: "Major content update coming [DATE] - doubling gameplay hours"
3. Offer discount to current owners if price increases later

**Expected Impact**:
- Review score improvement: +2-3% (from current to 67-68%)
- Estimated timeline: 1 week for pricing change
- Confidence level: Medium (some will still complain regardless of price)
- Success metrics: "overpriced" complaints drop by 80%, conversion rate improves

---

## Subjective Preferences: Art Style

**Complaint Frequency**: 8% of negative reviews (4 reviews)
**Severity**: 🟢 Minor
**Fixability**: ❌ Fundamental (don't fix)

**Representative Quotes**:
- "Pixel art is ugly and lazy"
- "Looks like a mobile game"

**Root Cause Analysis**:
Stylistic preference. Some players don't like pixel art aesthetic regardless of execution quality.

**Fix-It Plan**:

**Immediate**: Ignore. 8% is noise level - every game has art style critics.

**Short-Term**: Don't change art style. Focus on making good use of current style (add animation polish, particles, etc.)

**Communication Plan**: Don't address. Changing art style would alienate current fans.

**Expected Impact**: None. Accept that 8-10% won't like your art - that's normal.

---

## Next Steps

1. **Immediate**: Address any critical issues flagged above (this week)
2. **Short-term**: Implement high-priority fixes (30 days)
3. **Communication**: Announce your fix-it roadmap to the community
4. **Measure**: Track review score weekly to validate improvements
5. **Reassess**: Re-run this analysis in 60 days to measure progress

---

*This analysis is based on 50 negative reviews. For games with very few reviews, results may not be representative.*
```

## Integration into Reports

### Usage in Main Report Generation

```python
from src.negative_review_analyzer import NegativeReviewAnalyzer

# For games with <80% positive reviews
if review_percentage < 80:
    analyzer = NegativeReviewAnalyzer(claude_api_key)

    # Generate negative review analysis
    negative_analysis = analyzer.generate_full_analysis(
        app_id=game_data['app_id'],
        game_name=game_data['name'],
        current_review_score=review_percentage,
        review_count=50  # Analyze 50 reviews
    )

    # Add as Section 7 or similar (after standard analysis)
    full_report += "\n\n---\n\n" + negative_analysis
```

### Configuration

The analyzer can be configured for:
- **Review count**: Analyze 50-200 negative reviews (default: 100)
- **Language**: Filter to specific language (default: 'english')
- **Temperature**: Adjust Claude's analysis style (default: 0.3 for categorization, 0.5 for recommendations)

## Key Features

### 1. Complaint Categorization

Automatically categorizes negative reviews into:
- **Critical Issues** (🔴): Game-breaking problems that need immediate fixes
- **Design Problems** (⚠️): Fundamental gameplay issues requiring major rework
- **Polish Issues** (✅): Quality problems that are fixable with updates
- **Expectation Mismatches** (📢): Communication or pricing issues
- **Subjective Preferences** (➖): Personal taste (ignore these)

### 2. Fix-It Plans

For each significant issue (>10% of complaints):
- Immediate actions (this week)
- Short-term fixes (30 days)
- Communication strategy
- Expected impact with confidence levels
- Success metrics

### 3. Salvageability Assessment

Determines if the game can be saved:
- **Salvageable** (>60% fixable issues): Keep working on it
- **Borderline** (mixed): Decision framework provided
- **Consider Pivot** (>40% fundamental problems): May not be worth fixing

Includes:
- Investment required (time, cost, team size)
- Timeline to recovery
- Probability of success
- Pivot recommendations if applicable

## Benefits

**Instead of Guessing**:
> "I think players don't like the difficulty..."

**You Get Facts**:
> "42% of negative reviews cite level transition crashes (critical), 38% cite repetitive enemy types (design), 31% cite confusing UI (polish). Fix crashes first (2-week timeline, high confidence), then add enemy variety (6-week timeline, medium confidence)."

## Testing

To test the analyzer:

```bash
# Set your Claude API key
export ANTHROPIC_API_KEY='your-key-here'

# Run test
python test_negative_review_analyzer.py
```

This will analyze a struggling game and generate a full report.

## Dependencies

- Steam API (for fetching reviews)
- Claude API (for analysis and categorization)
- No additional dependencies beyond existing project requirements

## Performance

- Fetching 50 reviews: ~5-10 seconds
- Claude analysis: ~20-30 seconds (3 API calls)
- Total time: ~30-45 seconds for complete analysis

## Limitations

1. **Requires negative reviews**: Games with very few reviews (<20 negative) won't have enough data
2. **English only** (default): Can analyze other languages by changing the parameter
3. **API costs**: Each analysis uses ~10K tokens ($0.03-$0.05 per analysis)
4. **Subjectivity**: Claude's assessment is AI-generated and should be validated

## Ideal Use Cases

Best for:
- Games with 50+ negative reviews and <80% positive score
- Teams deciding whether to fix current game or pivot
- Identifying the #1 issue to fix first (priority ranking)
- Understanding WHY players are leaving negative reviews

Not ideal for:
- Games with <20 negative reviews (not enough data)
- Games with >90% positive (waste of analysis - everything's working)
- Pre-launch games (no reviews yet)

## Next Steps

This analyzer provides the brutal truth about what's broken. Use it to:

1. **Make the fix/pivot decision** with data instead of emotions
2. **Prioritize fixes** based on frequency and fixability
3. **Set realistic expectations** for recovery timeline
4. **Communicate honestly** with your community about the path forward
