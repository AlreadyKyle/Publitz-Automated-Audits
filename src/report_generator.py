"""
Report Generator - Generate comprehensive audit reports using Claude AI

This module takes collected data and generates a professional 9-section
pre-launch Steam audit report worth $800 in value.
"""

import json
import os
from typing import Dict, Any, Optional
from anthropic import Anthropic
from pathlib import Path

from config import Config


class ReportGenerator:
    """
    Generate comprehensive audit reports using Claude AI.

    Takes collected game data and generates a 35-45 page audit report
    following the Publitz audit methodology.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize report generator with Claude API.

        Args:
            api_key: Anthropic API key (uses Config.ANTHROPIC_API_KEY if not provided)
        """
        self.api_key = api_key or Config.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("Anthropic API key required for report generation")

        self.client = Anthropic(api_key=self.api_key)
        self.model = Config.CLAUDE_MODEL

        # Load master prompt template
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Load the master audit prompt template"""
        template_path = Config.TEMPLATE_DIR / "audit_prompt.txt"

        if template_path.exists():
            return template_path.read_text()
        else:
            # Return embedded default prompt if template file doesn't exist
            return self._get_default_prompt()

    def generate_full_report(
        self,
        data: Dict[str, Any],
        inputs: Any  # ClientInputs from input_processor
    ) -> str:
        """
        Generate complete audit report using Claude AI.

        Args:
            data: Collected game/competitor/research data
            inputs: ClientInputs with intake form and strategy notes

        Returns:
            Complete markdown report (35-45 pages)
        """
        print("\n" + "="*80)
        print("🤖 CLAUDE AI REPORT GENERATION")
        print("="*80)

        # Build comprehensive prompt with all data
        prompt = self._build_prompt(data, inputs)

        print(f"\n📝 Prompt size: {len(prompt):,} characters")
        print(f"🎯 Model: {self.model}")
        print(f"⚙️  Max tokens: {Config.CLAUDE_MAX_TOKENS}")
        print("\n⏳ Generating report (this may take 2-3 minutes)...\n")

        # Call Claude API
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=Config.CLAUDE_MAX_TOKENS,
                temperature=Config.CLAUDE_TEMPERATURE,
                system=self._get_system_message(),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract report from response
            report = response.content[0].text

            print(f"✅ Report generated successfully!")
            print(f"📊 Report length: {len(report):,} characters (~{len(report.split())} words)")

            return report

        except Exception as e:
            print(f"\n❌ Error generating report: {e}")
            raise

    def _build_prompt(self, data: Dict[str, Any], inputs: Any) -> str:
        """
        Build comprehensive prompt with all collected data.

        This formats all game data, competitor data, research, and client
        context into a structured prompt for Claude.
        """
        game = data.get('game', {})
        competitors = data.get('competitors', [])
        research = data.get('external_research', {})
        context = data.get('client_context', {})

        prompt = f"""Generate a comprehensive Pre-Launch Steam Audit report.

# CLIENT INFORMATION

**Client Name:** {inputs.intake_form.get('client_name', 'Unknown')}
**Game Name:** {inputs.intake_form.get('game_name', game.get('name', 'Unknown'))}
**Launch Date:** {inputs.intake_form.get('launch_date', 'TBD')}
**Target Price:** ${inputs.intake_form.get('target_price', 'TBD')}
**Days Until Launch:** {context.get('days_until_launch', 'N/A')}

**Client Context:**
- Team Size: {context.get('team_size', 'Unknown')} ({context.get('team_category', 'unknown')})
- Budget: {context.get('budget_tier', 'unknown').title()}
- Development Stage: {inputs.intake_form.get('development_stage', 'Unknown')}
- Main Concerns: {inputs.intake_form.get('main_concerns', 'Not specified')}

# STRATEGY CALL NOTES

{inputs.strategy_notes}

# GAME DATA

**Steam App ID:** {game.get('app_id', 'Unknown')}
**Current Price:** ${game.get('price', 0):.2f}
**Genres:** {', '.join(game.get('genres', ['Unknown']))}
**Release Date:** {game.get('release_date', 'Unknown')}
**Tags:** {', '.join(game.get('tags', [])[:10])}

**Reviews:**
- Score: {game.get('review_score', 0)}% positive
- Count: {game.get('review_count', 0):,} reviews

**Estimated Performance:**
- Owners: {game.get('owners', 0):,}
- Estimated Revenue: ${game.get('revenue', 0):,.0f}

**Store Page Assets:**
- Description Length: {len(game.get('detailed_description', ''))} characters
- Screenshot Count: {len(game.get('screenshots', []))}
- Has Trailer: {'Yes' if game.get('movies') else 'No'}

# COMPETITOR ANALYSIS DATA

**{len(competitors)} Competitors Analyzed:**

"""

        # Add competitor data
        for i, comp in enumerate(competitors[:10], 1):
            prompt += f"""
### Competitor {i}: {comp.get('name', 'Unknown')}

- **Price:** ${comp.get('price', 0):.2f}
- **Reviews:** {comp.get('review_score', 0)}% ({comp.get('review_count', 0):,} reviews)
- **Release Date:** {comp.get('release_date', 'Unknown')}
- **Genres:** {', '.join(comp.get('genres', []))}
- **Estimated Owners:** {comp.get('owners', 0):,}
- **Estimated Revenue:** ${comp.get('revenue', 0):,.0f}
"""

            # Add playtime data if available
            if comp.get('playtime', {}).get('found'):
                pt = comp['playtime']
                prompt += f"- **Playtime:** {pt.get('main_story', 0):.1f}h main, {pt.get('main_extras', 0):.1f}h main+extras\n"

        # Add external research
        prompt += f"""

# EXTERNAL RESEARCH

## Reddit Insights
{self._format_reddit_insights(research.get('reddit', {}))}

## HowLongToBeat Data
{self._format_hltb_data(research.get('hltb', {}))}

## Launch Window Analysis
{self._format_launch_conflicts(research.get('launch_conflicts', []))}

# REPORT REQUIREMENTS

Generate a comprehensive Pre-Launch Steam Audit following this EXACT structure:

## Report Structure (35-45 pages)

1. **Cover Page**
   - Game name, client name, date
   - Launch readiness badge (✅/⚠️/🚨/❌)

2. **Executive Summary** (2-3 pages)
   - Overall launch readiness tier
   - Star ratings (Store Quality, Competitive Position, Launch Timing)
   - Top 3 priority actions
   - Biggest risk and opportunity

3. **Section 1: Compliance Audit** (3-4 pages)
   - Steam page checklist with ✅/⚠️/❌ status
   - Critical issues flagged
   - Specific actions with time estimates

4. **Section 2: Store Page Optimization** (5-6 pages)
   - Capsule analysis (readability, contrast)
   - Description rewrite with strong hook
   - Tag optimization (high-traffic recommendations)
   - Screenshot strategy
   - Trailer review (if applicable)

5. **Section 3: Regional Pricing Strategy** (3-4 pages)
   - Recommended base price with justification
   - Tier 1/2/3 market tables
   - Pricing philosophy
   - Competitive price positioning

6. **Section 4: Competitive Analysis** (4-5 pages)
   - Individual competitor breakdown
   - Competitive matrix table
   - Pattern analysis
   - Differentiation opportunities

7. **Section 5: Launch Timing Analysis** (3-4 pages)
   - Launch window assessment
   - Major conflicts identified
   - Calendar considerations
   - Keep/delay recommendation

8. **Section 6: Implementation Roadmap** (4-5 pages)
   - Week 1: Critical actions (3-4 items)
   - Week 2-3: Important optimizations
   - Timeline Gantt view
   - Emergency recovery plan

9. **Section 7: First-Year Sales Strategy** (3-4 pages)
   - Launch discount decision
   - Discount calendar (never >50% in Year 1)
   - Steam seasonal sales plan
   - Bundle strategy

10. **Section 8: Multi-Storefront Strategy** (3-4 pages)
    - Epic/GOG/Console assessment
    - Effort vs return analysis
    - Launch sequencing recommendation

11. **Section 9: 90-Day Post-Launch** (3-4 pages)
    - Week 1-2: Survival mode
    - Month 2-3: First major update
    - Sales frequency guide
    - Community engagement calendar

12. **Next Steps & Resources** (2 pages)

# CRITICAL GUIDELINES

**Tone:** Match client's emotional state from strategy notes (supportive for stressed, direct for pragmatic)

**Specificity:**
- ❌ "Improve your capsule"
- ✅ "Increase logo size from 60px to 120px, move to left-third"

**Recommendations:**
- Include exact steps, time estimates, and impact
- Format: What / Why / How / Time / Impact
- NO dollar amount projections (qualitative only)

**Star Ratings (1-5 stars):**
- ⭐ Store Quality: Technical + visual + content effectiveness
- ⭐ Competitive Position: Price + differentiation + market fit
- ⭐ Launch Timing: Window + calendar + preparation time

**Overall Tier:**
- ✅ LAUNCH READY: Mostly 4-5 stars
- ⚠️ LAUNCH VIABLE: Mix of 3-5 stars
- 🚨 HIGH RISK: Multiple 2-3 stars
- ❌ NOT READY: Any 1-star or multiple 2-stars

Generate the complete report now in markdown format.
"""

        return prompt

    def _format_reddit_insights(self, reddit_data: Dict[str, Any]) -> str:
        """Format Reddit research data"""
        if not reddit_data or not reddit_data.get('subreddit'):
            return "- No Reddit insights available"

        output = f"- **Subreddit:** r/{reddit_data['subreddit']}\n"

        discussions = reddit_data.get('top_discussions', [])
        if discussions:
            output += "- **Top Discussions:**\n"
            for disc in discussions[:3]:
                output += f"  - {disc['title']} ({disc['score']} upvotes)\n"

        return output

    def _format_hltb_data(self, hltb_data: Dict[str, Any]) -> str:
        """Format HowLongToBeat data"""
        if not hltb_data or not hltb_data.get('found'):
            return "- Playtime data not available"

        return f"""- **Main Story:** {hltb_data.get('main_story', 0):.1f} hours
- **Main + Extras:** {hltb_data.get('main_extras', 0):.1f} hours
- **Completionist:** {hltb_data.get('completionist', 0):.1f} hours"""

    def _format_launch_conflicts(self, conflicts: list) -> str:
        """Format launch window conflicts"""
        if not conflicts:
            return "- No major conflicts detected in launch window"

        output = "- **Conflicts Detected:**\n"
        for conflict in conflicts[:5]:
            output += f"  - {conflict.get('name', 'Unknown')} ({conflict.get('date', 'TBD')})\n"

        return output

    def _get_system_message(self) -> str:
        """
        Get system message with audit methodology and best practices.

        This embeds the Publitz audit knowledge into Claude's system prompt.
        """
        return """You are an expert Steam game audit consultant with 20+ years of AAA publishing experience (EA, Disney, Web3). You specialize in helping indie developers optimize their Steam launches.

Your task is to generate comprehensive, actionable Pre-Launch Steam Audit reports worth $800 in value.

# YOUR EXPERTISE

- Steam algorithm and visibility mechanics
- Competitive positioning and pricing strategy
- Store page optimization (capsules, descriptions, tags)
- Launch timing and calendar planning
- Regional pricing and localization
- Post-launch sales and DLC strategy
- Multi-platform expansion analysis

# METHODOLOGY

**Conservative Approach:**
- Under-promise, over-deliver
- Round scores down when uncertain
- Base recommendations on data, not assumptions
- No revenue projections (qualitative improvements only)

**Specificity:**
- Every recommendation must be actionable
- Include exact steps, measurements, time estimates
- "Increase logo to 120px" not "make logo bigger"
- "Add tag 'Roguelike' (500K followers)" not "improve tags"

**Tone Calibration:**
- Match client's emotional state from strategy notes
- Stressed client → Empathetic, break into small steps
- Confident client → Direct, data-driven
- Burned out client → Permission to simplify, focus on essentials

**Quality Standards:**
- 35-45 pages comprehensive
- Specific, not generic
- Actionable within client's bandwidth
- Competitive analysis uses actual data
- Recommendations prioritized by impact

# STAR RATING SYSTEM

**Store Quality (1-5 ⭐):**
- 5: All assets present, high quality, genre-appropriate
- 4: All present, minor improvements needed
- 3: Weak quality, needs work
- 2: Missing assets or very poor quality
- 1: Critical assets missing or unusable

**Competitive Position (1-5 ⭐):**
- 5: Price within $3, clear differentiation, quality matches price
- 4: Price within $5, some differentiation
- 3: Price within $10, weak differentiation
- 2: Price $10+ off or no differentiation
- 1: Price completely wrong or identical to existing game

**Launch Timing (1-5 ⭐):**
- 5: Clean window (no conflicts), 30+ days prep
- 4: Moderate window (1-2 conflicts), 14-29 days
- 3: Crowded (3-4 conflicts), 7-13 days
- 2: Very crowded (5+ conflicts), <7 days
- 1: Same day as major AAA or <3 days prep

**Overall Tier:**
- ✅ LAUNCH READY: Mostly 4-5 stars, enthusiastic tone
- ⚠️ LAUNCH VIABLE: Mix 3-5 stars, encouraging but constructive
- 🚨 HIGH RISK: Multiple 2-3 stars, direct about risks, suggest delay
- ❌ NOT READY: Any 1-star, honest about readiness, strongly suggest delay

# OUTPUT FORMAT

- Use markdown formatting
- Include tables where appropriate
- Use emojis sparingly for visual hierarchy
- Structure exactly as requested in prompt
- Be comprehensive but concise (no fluff)

Generate professional, actionable reports that clients feel are worth $800 in value."""

    def _get_default_prompt(self) -> str:
        """Return default embedded prompt if template file not found"""
        return "Generate a comprehensive Pre-Launch Steam Audit report."


if __name__ == "__main__":
    """Test report generator"""
    print("Report Generator Module")
    print("=" * 80)
    print("\nThis module generates comprehensive audit reports using Claude AI.")
    print("\nUsage:")
    print("  from src.report_generator import ReportGenerator")
    print("  generator = ReportGenerator()")
    print("  report = generator.generate_full_report(data, inputs)")
    print("\nRequires:")
    print("  - ANTHROPIC_API_KEY in .env")
    print("  - Collected data dict from simple_data_collector")
    print("  - ClientInputs from input_processor")
