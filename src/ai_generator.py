"""AI report generation using Claude API."""

import anthropic
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
import json

load_dotenv()


class AIReportGenerator:
    """Generate audit reports using Claude AI."""

    def __init__(self, api_key: str = None):
        """
        Initialize AI generator.

        Args:
            api_key: Anthropic API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def generate_pre_launch_report(self, game_data: Dict[str, Any],
                                   competitor_data: List[Dict[str, Any]],
                                   steamdb_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive pre-launch audit report.

        Args:
            game_data: Data scraped from Steam store page
            competitor_data: Data about competitor games
            steamdb_data: Data from SteamDB

        Returns:
            Structured report data
        """
        # Build the prompt from the template
        prompt = self._build_pre_launch_prompt(game_data, competitor_data, steamdb_data)

        # Generate report with Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=16000,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse the response
        report_text = response.content[0].text

        return {
            'report_type': 'pre_launch',
            'game_name': game_data.get('name'),
            'generated_at': None,  # Will be set by caller
            'report_text': report_text,
            'structured_data': self._parse_report_structure(report_text)
        }

    def generate_post_launch_report(self, game_data: Dict[str, Any],
                                    sales_data: Dict[str, Any],
                                    competitor_data: List[Dict[str, Any]],
                                    steamdb_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive post-launch performance report.

        Args:
            game_data: Data scraped from Steam store page
            sales_data: Sales and performance data
            competitor_data: Data about competitor games
            steamdb_data: Data from SteamDB

        Returns:
            Structured report data
        """
        # Build the prompt from the template
        prompt = self._build_post_launch_prompt(
            game_data, sales_data, competitor_data, steamdb_data
        )

        # Generate report with Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=16000,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse the response
        report_text = response.content[0].text

        return {
            'report_type': 'post_launch',
            'game_name': game_data.get('name'),
            'generated_at': None,  # Will be set by caller
            'report_text': report_text,
            'structured_data': self._parse_report_structure(report_text)
        }

    def _build_pre_launch_prompt(self, game_data: Dict[str, Any],
                                 competitor_data: List[Dict[str, Any]],
                                 steamdb_data: Dict[str, Any]) -> str:
        """Build the pre-launch prompt from template and data."""

        # Format competitor data
        competitor_text = ""
        for i, comp in enumerate(competitor_data[:2], 1):
            competitor_text += f"""
Competitor {i} Name: {comp.get('name', 'Unknown')}
Competitor {i} Steam URL: {comp.get('url', 'N/A')}
Competitor {i} Current USD Price: ${comp.get('price', 0):.2f}
Competitor {i} Screenshot Count: {len(comp.get('screenshots', []))}
"""

        # Format tags with follower counts (simulated if not available)
        tags_text = ", ".join(game_data.get('tags', [])[:15])

        prompt = f"""You are a 20-year veteran of game publishing, acting as a Steam launch strategist.
Your task is to perform a comprehensive audit for a new client.

Use all the information provided in the CLIENT DATA INPUT section below to complete the following tasks.

[CLIENT DATA INPUT - FILLED AUTOMATICALLY]

Game Name: {game_data.get('name', 'Unknown')}
Steam URL: {game_data.get('store_url', 'N/A')}
Genre: {', '.join(game_data.get('genres', ['Unknown']))}
Unique Mechanics: {game_data.get('short_description', 'N/A')}
Polish Level: AA Indie
Planned Base USD: ${game_data.get('price', {}).get('base_price', 0) or 19.99:.2f}
Planned Launch Window: {game_data.get('release_date', 'TBA')}
Current Tags: {tags_text}

Current Capsule Description: [Visual analysis of header image at {game_data.get('capsule_image', 'N/A')}]

Current Screenshot Descriptions:
{"".join([f"{i+1}. Screenshot {i+1}\\n" for i in range(len(game_data.get('screenshots', [])))])}

{competitor_text}

High-Value Competitor Tags (from SteamDB): {", ".join(game_data.get('tags', [])[:10])}

Current Full Description: {game_data.get('description', 'N/A')}

[AI ANALYSIS TASKS]

Provide a structured response completing each task:

TASK 1: CAPSULE IMAGE ANALYSIS
Analyze the game's main capsule image. Provide:
1. Readability at Thumbnail Size (1-10 Score)
2. Genre Clarity: Does it instantly communicate the genre?
3. Visual Hierarchy: What should be the focal point?
4. Competitive Differentiation: How to stand out
5. Top 3 Specific Issues
6. Top 3 Specific Fixes

TASK 2: DESCRIPTION OPTIMIZATION
Analyze the current description. Provide:
1. Current Description Analysis (3 sentences)
2. Rewritten First Paragraph (Hook) - 2-3 sentences max
3. Recommended Full Structure (outline)
4. Top 3 Keyword Opportunities

TASK 3: TAGS & DISCOVERABILITY
Analyze current tags. Provide:
1. High-Traffic Tags (KEEP): List good current tags
2. Low-Value Tags (REPLACE): List tags to replace with better alternatives
3. Recommended New Tags (ADD): 5-10 new relevant tags

TASK 4: SCREENSHOT STRATEGY
Provide:
1. Current Sequence Assessment
2. Recommended 8-Shot Sequence with specific descriptions
3. Specific Actions for improvement

TASK 5: COMPETITIVE BENCHMARK
Create a comparison table with:
- Capsule clarity score
- Description hook assessment
- Screenshot count
- Tag optimization
- Price positioning
Provide clear recommendations for each element.

TASK 6: PRICING STRATEGY
Provide:
1. Recommended Base USD price
2. 1-Sentence Reasoning
3. Pricing Philosophy (Competitive/Value/Premium)
4. Top 10 Regions pricing table

TASK 7: LAUNCH TIMING ANALYSIS
Provide:
1. Optimal Launch Date
2. Why This Date (3 bullet points)
3. Backup Launch Date
4. Major Releases to Avoid
5. Dates to ABSOLUTELY AVOID

Format your response as a complete, structured report with clear sections and actionable recommendations."""

        return prompt

    def _build_post_launch_prompt(self, game_data: Dict[str, Any],
                                  sales_data: Dict[str, Any],
                                  competitor_data: List[Dict[str, Any]],
                                  steamdb_data: Dict[str, Any]) -> str:
        """Build the post-launch prompt from template and data."""

        # Extract review data
        reviews = game_data.get('reviews', {})
        review_summary = reviews.get('summary', 'No reviews')
        review_count = reviews.get('total_reviews', 0)

        # Format competitor data
        competitor_text = ""
        for i, comp in enumerate(competitor_data[:2], 1):
            competitor_text += f"""
Competitor {i}:
Name: {comp.get('name', 'Unknown')}
Steam URL: {comp.get('url', 'N/A')}
Current Price: ${comp.get('price', 0):.2f}
Review Score: {comp.get('review_score', 'N/A')}
Screenshot Count: {len(comp.get('screenshots', []))}
"""

        prompt = f"""You are a 20-year veteran of game publishing, specializing in post-launch revenue recovery.
Your task is to analyze this launched game's performance and create an actionable recovery plan.

[CLIENT DATA INPUT]

BASIC INFO
Game Name: {game_data.get('name', 'Unknown')}
Steam URL: {game_data.get('store_url', 'N/A')}
Steam App ID: {game_data.get('app_id', 'N/A')}
Genre: {', '.join(game_data.get('genres', ['Unknown']))}
Launch Date: {game_data.get('release_date', 'Unknown')}
Current Base USD Price: ${game_data.get('price', {}).get('base_price', 0) or 19.99:.2f}

REVIEW DATA
Current Review Score: {review_summary}
Total Reviews: {review_count}
Recommendations: {game_data.get('recommendations', 'N/A')}

STORE PAGE DATA
Current Tags: {", ".join(game_data.get('tags', [])[:15])}
Screenshot Count: {len(game_data.get('screenshots', []))}
Video Count: {len(game_data.get('videos', []))}
Current Description: {game_data.get('short_description', 'N/A')}

STEAMDB DATA
Followers/Wishlists: {steamdb_data.get('followers', 'N/A')}
Peak Players (24h): {steamdb_data.get('peak_players', {}).get('last_24h', 'N/A')}

{competitor_text}

[AI ANALYSIS TASKS]

Provide a structured response completing each task:

TASK 1: PERFORMANCE DIAGNOSIS
Provide:
1. Revenue Trajectory Assessment (3 sentences)
2. Conversion Funnel Analysis
3. Regional Performance Red Flags

TASK 2: STORE PAGE OPTIMIZATION (Data-Driven)
Provide:
1. Capsule Performance Analysis with CTR assessment
2. Description Hook Analysis with rewrite
3. Tag Optimization recommendations

TASK 3: REVIEW SCORE RECOVERY PLAN
Provide:
1. Review Score Impact Analysis
2. Complaint Resolution Priority
3. Review Response Strategy with templates

TASK 4: PRICING RECOVERY STRATEGY
Provide:
1. Base Price Assessment
2. Regional Pricing Opportunities
3. Sale Strategy with 90-day calendar

TASK 5: CONTENT & COMMUNITY ROADMAP
Provide:
1. Content Update Priorities
2. Community Engagement Plan
3. Creator Outreach Opportunities

TASK 6: 90-DAY REVENUE PROJECTION
Create a revenue projection table with:
- Baseline scenario (do nothing)
- With This Plan scenario
- Monthly breakdown by revenue source

TASK 7: CRITICAL ISSUES SUMMARY
Provide prioritized list of top 5 "revenue killers" with:
- Impact ($ cost)
- Fix Difficulty
- Timeline
- Recommended fix

Format your response as a complete, structured report with clear sections, data-driven insights, and actionable recommendations."""

        return prompt

    def _parse_report_structure(self, report_text: str) -> Dict[str, Any]:
        """
        Parse the generated report into structured sections.

        Args:
            report_text: Full report text from Claude

        Returns:
            Dictionary with structured report sections
        """
        # Split into sections based on headers
        sections = {}
        current_section = None
        current_content = []

        for line in report_text.split('\n'):
            # Check if line is a section header
            if line.startswith('##') or line.startswith('TASK'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()

                current_section = line.strip('#').strip()
                current_content = []
            else:
                current_content.append(line)

        # Add last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections
