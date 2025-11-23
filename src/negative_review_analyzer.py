"""
Negative Review Analyzer

For struggling games (<80% positive reviews), extracts actionable insights from
negative reviews to determine what's broken and how to fix it.

Instead of generic advice, provides:
- Specific complaint categorization
- Fix-it plans with timelines
- Salvageability assessment (can this game be saved?)
"""

import logging
import requests
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import anthropic
import json

logger = logging.getLogger(__name__)


@dataclass
class ReviewComplaint:
    """A categorized complaint from reviews"""
    category: str
    severity: str  # 'critical', 'moderate', 'minor'
    fixability: str  # 'fixable', 'requires_resources', 'fundamental'
    frequency_percent: float
    count: int
    quotes: List[str]
    root_cause: str
    fix_immediate: List[str]
    fix_short_term: List[str]
    communication_plan: List[str]
    expected_impact: str


@dataclass
class SalvageabilityAssessment:
    """Assessment of whether a game can be saved"""
    verdict: str  # 'salvageable', 'borderline', 'consider_pivot'
    critical_percent: float
    design_percent: float
    polish_percent: float
    subjective_percent: float
    reasoning: str
    required_investment: str
    timeline: str
    probability_of_recovery: int
    pivot_recommendations: List[str]


class NegativeReviewAnalyzer:
    """
    Analyzes negative Steam reviews for struggling games to extract actionable insights.

    For games with <80% positive reviews, categorizes complaints and generates
    specific fix-it recommendations with salvageability assessment.
    """

    def __init__(self, claude_api_key: str):
        """Initialize with Claude API for analysis"""
        self.client = anthropic.Anthropic(api_key=claude_api_key)
        self.model = "claude-sonnet-4-20250514"

    def fetch_negative_reviews(
        self,
        app_id: str,
        count: int = 100,
        language: str = 'english'
    ) -> List[Dict[str, Any]]:
        """
        Fetch negative reviews from Steam API.

        Prioritizes:
        - Most helpful (voted helpful by community)
        - Recent (posted in last 6 months)
        - Detailed (longer reviews with substance)

        Args:
            app_id: Steam app ID
            count: Number of negative reviews to fetch
            language: Review language filter

        Returns:
            List of review dictionaries with text, votes, date, etc.
        """
        logger.info(f"Fetching negative reviews for app_id {app_id}")

        reviews = []
        cursor = "*"
        max_requests = 5  # Limit API calls

        try:
            for _ in range(max_requests):
                # Steam reviews API endpoint
                url = "https://store.steampowered.com/appreviews/" + str(app_id)
                params = {
                    'json': 1,
                    'filter': 'recent',  # Recent reviews
                    'language': language,
                    'review_type': 'negative',  # Only negative reviews
                    'purchase_type': 'all',
                    'num_per_page': 100,
                    'cursor': cursor
                }

                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                if not data.get('success'):
                    logger.warning(f"Steam API returned success=false for app_id {app_id}")
                    break

                batch_reviews = data.get('reviews', [])
                if not batch_reviews:
                    break

                # Filter for helpful and detailed reviews
                for review in batch_reviews:
                    # Extract review data
                    review_text = review.get('review', '')
                    votes_helpful = review.get('votes_up', 0)
                    votes_total = review.get('votes_up', 0) + review.get('votes_funny', 0)

                    # Skip very short reviews (likely not detailed enough)
                    if len(review_text) < 50:
                        continue

                    # Add helpful reviews
                    reviews.append({
                        'text': review_text,
                        'votes_helpful': votes_helpful,
                        'votes_total': votes_total,
                        'timestamp': review.get('timestamp_created', 0),
                        'playtime_forever': review.get('author', {}).get('playtime_forever', 0),
                        'playtime_at_review': review.get('author', {}).get('playtime_at_review', 0),
                        'helpful_score': votes_helpful if votes_total == 0 else votes_helpful / max(votes_total, 1)
                    })

                # Check if we have enough
                if len(reviews) >= count:
                    break

                # Get next cursor
                cursor = data.get('cursor')
                if not cursor:
                    break

                # Rate limiting
                time.sleep(0.5)

            # Sort by helpfulness and recency
            reviews.sort(key=lambda r: (r['votes_helpful'], r['timestamp']), reverse=True)

            # Return top N
            result = reviews[:count]
            logger.info(f"Fetched {len(result)} negative reviews for app_id {app_id}")

            return result

        except Exception as e:
            logger.error(f"Error fetching negative reviews: {e}")
            return []

    def categorize_complaints(
        self,
        reviews: List[Dict[str, Any]],
        game_name: str
    ) -> Dict[str, Any]:
        """
        Use Claude to categorize complaints from negative reviews.

        Categories:
        - Critical Issues (game-breaking): crashes, performance, save corruption
        - Design Problems (fundamental): boring gameplay, unfair difficulty, pacing
        - Polish Issues (fixable): UI/UX, tutorial, balance, QoL features
        - Expectation Mismatches (communication): price/content, misleading marketing
        - Subjective Preferences (accept/ignore): art style, genre preference

        Args:
            reviews: List of review dictionaries
            game_name: Name of the game for context

        Returns:
            Dictionary with categorized complaints and analysis
        """
        logger.info(f"Categorizing {len(reviews)} negative reviews using Claude")

        if not reviews:
            return {'error': 'No reviews to analyze'}

        # Build review text for analysis (use top 50 most helpful)
        review_texts = []
        for i, review in enumerate(reviews[:50], 1):
            playtime_hours = review['playtime_forever'] / 60 if review['playtime_forever'] > 0 else 0
            review_texts.append(
                f"Review {i} ({playtime_hours:.1f} hours played, {review['votes_helpful']} helpful votes):\n{review['text']}\n"
            )

        reviews_combined = "\n---\n".join(review_texts)

        # Claude analysis prompt
        prompt = f"""You are analyzing negative Steam reviews for the game "{game_name}" to extract actionable insights for the developers.

NEGATIVE REVIEWS TO ANALYZE:
{reviews_combined}

TASK: Categorize all complaints into these 5 categories:

1. **CRITICAL ISSUES** (game-breaking problems):
   - Crashes, freezes, won't launch
   - Severe performance problems (unplayable FPS)
   - Save file corruption or loss
   - Unplayable on advertised platforms
   - Major bugs that prevent progression

2. **DESIGN PROBLEMS** (fundamental gameplay issues):
   - Boring/repetitive gameplay loop
   - Unfair or poorly balanced difficulty
   - Poor progression pacing
   - Lack of content or replayability
   - Core mechanics not fun

3. **POLISH ISSUES** (fixable quality problems):
   - UI/UX problems (confusing menus, bad controls)
   - Missing tutorial or poor onboarding
   - Balance issues (weapons, enemies, economy)
   - Missing quality-of-life features
   - Minor bugs or glitches

4. **EXPECTATION MISMATCHES** (communication problems):
   - Price too high for amount of content
   - Misleading marketing or store page
   - Genre confusion (not what players expected)
   - Promised features missing or incomplete
   - Early Access concerns

5. **SUBJECTIVE PREFERENCES** (accept/ignore):
   - Art style or graphics preferences
   - Genre not their taste
   - Personal preferences (story, themes)
   - "Not for me" type feedback

For EACH category, provide:
- Percentage of negative reviews mentioning this category
- Count of reviews
- 2-3 representative quotes (exact text from reviews)
- Root cause analysis (why is this happening?)
- Severity rating (critical/moderate/minor)
- Fixability assessment (fixable/requires_resources/fundamental)

OUTPUT FORMAT (JSON):
{{
  "critical_issues": {{
    "percentage": 45,
    "count": 23,
    "severity": "critical",
    "fixability": "fixable",
    "quotes": ["exact quote 1", "exact quote 2"],
    "root_cause": "One sentence analysis",
    "top_complaints": ["specific complaint 1", "specific complaint 2", "specific complaint 3"]
  }},
  "design_problems": {{ ... }},
  "polish_issues": {{ ... }},
  "expectation_mismatches": {{ ... }},
  "subjective_preferences": {{ ... }},
  "summary": "2-3 sentence overall summary of what's broken"
}}

IMPORTANT: Be brutally honest. Don't sugarcoat fundamental problems. Developers need truth to make decisions.

Return ONLY valid JSON."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,  # Lower temperature for consistent categorization
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract response text
            response_text = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    response_text += content_block.text

            # Parse JSON response
            # Extract JSON from markdown code blocks if present
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()

            categorization = json.loads(response_text)

            logger.info("Successfully categorized complaints")
            return categorization

        except Exception as e:
            logger.error(f"Error categorizing complaints: {e}")
            return {'error': str(e)}

    def generate_fix_it_recommendations(
        self,
        categorization: Dict[str, Any],
        game_name: str,
        current_review_score: float
    ) -> str:
        """
        Generate specific fix-it recommendations for each complaint category.

        Args:
            categorization: Output from categorize_complaints()
            game_name: Name of the game
            current_review_score: Current review percentage (e.g., 65.5)

        Returns:
            Markdown formatted fix-it plan
        """
        logger.info("Generating fix-it recommendations")

        if 'error' in categorization:
            return f"## Error\n\nCould not generate recommendations: {categorization['error']}"

        # Build prompt for Claude to generate detailed fix-it plan
        prompt = f"""You are a game development consultant creating a fix-it plan for "{game_name}".

CURRENT SITUATION:
- Review Score: {current_review_score:.1f}% positive
- Game is struggling and needs intervention

COMPLAINT ANALYSIS:
{json.dumps(categorization, indent=2)}

TASK: For EACH category with >10% of complaints, create a detailed fix-it recommendation using this format:

## [Category Name]: [Specific Problem]

**Complaint Frequency**: [X]% of negative reviews ([count] reviews)
**Severity**: 🔴 Critical / 🟡 Moderate / 🟢 Minor
**Fixability**: ✅ Fixable / ⚠️ Requires Resources / ❌ Fundamental

**Representative Quotes**:
- "[Exact quote from analysis]"
- "[Another quote]"

**Root Cause Analysis**:
[Why this is happening - be specific and honest]

**Fix-It Plan**:

**Immediate (This Week)**:
1. [Emergency mitigation - even if temporary band-aid]
2. [Another immediate action]

**Short-Term (30 Days)**:
1. [Proper fix with specifics]
2. [Testing and validation approach]
3. [Rollout plan]

**Communication Plan**:
1. [How to acknowledge issue to community - specific messaging]
2. [What to promise in terms of timeline - be realistic]
3. [Where to communicate (Steam announcements, Discord, etc.)]

**Expected Impact**:
- Review score improvement: +[X-Y]% (from {current_review_score:.1f}% to [target]%)
- Estimated timeline: [X weeks/months]
- Confidence level: [High/Medium/Low]
- Success metrics: [How to measure if fix worked]

---

IMPORTANT:
- Be specific and actionable (not "improve performance" but "optimize shader compilation, reduce draw calls in level 3")
- Give realistic timelines
- Don't recommend fixes for fundamental design problems - flag those as "consider redesign"
- For subjective preferences, explain why to ignore them

Generate the full fix-it plan in markdown format."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=6000,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract response text
            fix_it_plan = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    fix_it_plan += content_block.text

            logger.info("Generated fix-it recommendations")
            return fix_it_plan

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return f"## Error\n\nFailed to generate recommendations: {str(e)}"

    def assess_salvageability(
        self,
        categorization: Dict[str, Any],
        current_review_score: float,
        game_name: str
    ) -> str:
        """
        Assess whether the game can be saved or should be pivoted.

        Decision logic:
        - If >40% fundamental design problems → consider pivot
        - If >60% fixable issues → salvageable
        - Otherwise → borderline, provide decision criteria

        Args:
            categorization: Output from categorize_complaints()
            current_review_score: Current review percentage
            game_name: Name of the game

        Returns:
            Markdown formatted salvageability assessment
        """
        logger.info("Assessing game salvageability")

        if 'error' in categorization:
            return f"## Error\n\nCould not assess salvageability: {categorization['error']}"

        # Extract percentages
        critical_pct = categorization.get('critical_issues', {}).get('percentage', 0)
        design_pct = categorization.get('design_problems', {}).get('percentage', 0)
        polish_pct = categorization.get('polish_issues', {}).get('percentage', 0)
        expectation_pct = categorization.get('expectation_mismatches', {}).get('percentage', 0)
        subjective_pct = categorization.get('subjective_preferences', {}).get('percentage', 0)

        # Calculate fixability
        fixable_pct = critical_pct + polish_pct + expectation_pct
        fundamental_pct = design_pct

        # Determine verdict
        if fundamental_pct > 40:
            verdict = "consider_pivot"
        elif fixable_pct > 60:
            verdict = "salvageable"
        else:
            verdict = "borderline"

        # Build prompt for detailed assessment
        prompt = f"""You are a game development consultant assessing whether "{game_name}" can be saved.

CURRENT METRICS:
- Review Score: {current_review_score:.1f}% positive
- Critical Issues: {critical_pct:.0f}%
- Design Problems: {design_pct:.0f}%
- Polish Issues: {polish_pct:.0f}%
- Expectation Mismatches: {expectation_pct:.0f}%
- Subjective Preferences: {subjective_pct:.0f}%

CATEGORIZATION DETAILS:
{json.dumps(categorization, indent=2)}

PRELIMINARY VERDICT: {verdict.upper().replace('_', ' ')}

TASK: Create a salvageability assessment using this format:

## Salvageability Assessment for {game_name}

**Issue Breakdown**:
- 🔴 Critical issues: {critical_pct:.0f}% (Must be fixed immediately)
- ⚠️ Design problems: {design_pct:.0f}% (Require major rework or acceptance)
- ✅ Polish issues: {polish_pct:.0f}% (Addressable with updates)
- 📢 Expectation mismatches: {expectation_pct:.0f}% (Communication/pricing fixes)
- ➖ Subjective preferences: {subjective_pct:.0f}% (Accept these)

**Verdict**: [Salvageable ✅ / Borderline ⚠️ / Consider Pivot 🔄]

**Reasoning**:
[3-4 sentences explaining the verdict based on the data]
[If >40% are fundamental design problems, explain why pivot is recommended]
[If >60% are fixable, explain why game can be saved]
[Be brutally honest about what's realistic]

**If You Persevere** (Fix Current Game):

**Required Investment**:
- Development time: [X person-weeks/months]
- Estimated cost: $[realistic range]
- Team size needed: [X developers, Y artists, etc.]

**Timeline to Meaningful Improvement**:
- Emergency fixes: [X weeks]
- Core fixes complete: [X months]
- Community sentiment shift: [X months]

**Probability of Recovery**: [X]%
- Best case: Review score improves to [Y]%
- Base case: Review score improves to [Y]%
- Worst case: Review score stays at {current_review_score:.1f}%

**Critical Success Factors**:
1. [Most important thing that must go right]
2. [Second most important]
3. [Third most important]

**If You Pivot** (Learn and Move On):

**Key Learnings to Carry Forward**:
1. [Specific lesson from failure]
2. [Another lesson]
3. [Third lesson]

**Pivot Recommendations**:
1. [Alternative approach if redesigning]
2. [Different genre/audience to consider]
3. [What to keep vs. what to abandon]

**Decision Framework**:
Choose PERSEVERE if:
- You have $[X] and [Y] months available
- You're emotionally ready for [Z months] of intense work
- You believe in the core concept despite execution issues

Choose PIVOT if:
- Budget is <$[X] or timeline is <[Y] months
- Core gameplay loop is fundamentally flawed (design problems >{design_pct:.0f}%)
- You've lost passion for this specific project

---

**Recommendation**: [Clear, direct recommendation based on the data]

Generate the assessment in markdown format. Be honest and direct - developers need truth to make hard decisions."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract response text
            assessment = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    assessment += content_block.text

            logger.info(f"Generated salvageability assessment: {verdict}")
            return assessment

        except Exception as e:
            logger.error(f"Error assessing salvageability: {e}")
            return f"## Error\n\nFailed to generate assessment: {str(e)}"

    def generate_full_analysis(
        self,
        app_id: str,
        game_name: str,
        current_review_score: float,
        review_count: int = 100
    ) -> str:
        """
        Generate complete negative review analysis report.

        Args:
            app_id: Steam app ID
            game_name: Name of the game
            current_review_score: Current review percentage
            review_count: Number of reviews to analyze

        Returns:
            Full markdown report with categorization, fixes, and salvageability
        """
        logger.info(f"Generating full negative review analysis for {game_name} (app_id: {app_id})")

        # Step 1: Fetch negative reviews
        reviews = self.fetch_negative_reviews(app_id, count=review_count)

        if not reviews:
            return f"## Negative Review Analysis\n\n**Error**: Could not fetch negative reviews for app_id {app_id}. The game may not have enough negative reviews, or the Steam API is unavailable."

        # Step 2: Categorize complaints
        categorization = self.categorize_complaints(reviews, game_name)

        if 'error' in categorization:
            return f"## Negative Review Analysis\n\n**Error**: {categorization['error']}"

        # Step 3: Generate fix-it recommendations
        fix_it_plan = self.generate_fix_it_recommendations(categorization, game_name, current_review_score)

        # Step 4: Assess salvageability
        salvageability = self.assess_salvageability(categorization, current_review_score, game_name)

        # Combine all sections
        report = f"""# Negative Review Analysis: {game_name}

**Current Review Score**: {current_review_score:.1f}% positive
**Reviews Analyzed**: {len(reviews)} negative reviews
**Analysis Date**: {time.strftime('%Y-%m-%d')}

---

## Executive Summary

{categorization.get('summary', 'Analysis complete.')}

**Breakdown by Category**:
- 🔴 Critical Issues: {categorization.get('critical_issues', {}).get('percentage', 0):.0f}%
- ⚠️ Design Problems: {categorization.get('design_problems', {}).get('percentage', 0):.0f}%
- ✅ Polish Issues: {categorization.get('polish_issues', {}).get('percentage', 0):.0f}%
- 📢 Expectation Mismatches: {categorization.get('expectation_mismatches', {}).get('percentage', 0):.0f}%
- ➖ Subjective Preferences: {categorization.get('subjective_preferences', {}).get('percentage', 0):.0f}%

---

{salvageability}

---

# Fix-It Recommendations

{fix_it_plan}

---

## Next Steps

1. **Immediate**: Address any critical issues flagged above (this week)
2. **Short-term**: Implement high-priority fixes (30 days)
3. **Communication**: Announce your fix-it roadmap to the community
4. **Measure**: Track review score weekly to validate improvements
5. **Reassess**: Re-run this analysis in 60 days to measure progress

---

*This analysis is based on {len(reviews)} negative reviews. For games with very few reviews, results may not be representative.*
"""

        return report


# Convenience function for testing
def test_analyzer(app_id: str, game_name: str, review_score: float, claude_api_key: str):
    """Test the negative review analyzer"""
    analyzer = NegativeReviewAnalyzer(claude_api_key)

    print(f"\n=== Testing Negative Review Analyzer ===")
    print(f"Game: {game_name}")
    print(f"App ID: {app_id}")
    print(f"Current Review Score: {review_score}%")

    # Generate full analysis
    report = analyzer.generate_full_analysis(app_id, game_name, review_score, review_count=50)

    print("\n" + "="*80)
    print(report)
    print("="*80 + "\n")

    return analyzer, report
