#!/usr/bin/env python3
"""
Report Builder - Modular Report Generation System
Orchestrates the creation of structured audit reports with scoring and recommendations
"""

from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from src.logger import get_logger

logger = get_logger(__name__)


class ReportSection(ABC):
    """Base class for report sections"""

    def __init__(self, section_name: str, data: Dict[str, Any]):
        self.section_name = section_name
        self.data = data
        self.score = 0
        self.rating = "unknown"
        self.recommendations = []
        self.benchmarks = {}
        self.analyzed = False

    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze the section data and generate insights

        Returns:
            Dict with: {
                'score': 0-100,
                'rating': 'excellent'|'good'|'fair'|'poor',
                'strengths': [list],
                'weaknesses': [list],
                'recommendations': [list],
                'benchmarks': dict
            }
        """
        pass

    @abstractmethod
    def generate_markdown(self) -> str:
        """
        Generate markdown output for this section

        Returns:
            Formatted markdown string
        """
        pass

    def get_score(self) -> int:
        """Get section score (0-100)"""
        if not self.analyzed:
            self.analyze()
        return self.score

    def get_rating(self) -> str:
        """Get rating label based on score"""
        if self.score >= 80:
            return "excellent"
        elif self.score >= 65:
            return "good"
        elif self.score >= 50:
            return "fair"
        else:
            return "poor"


class ExecutiveSummarySection(ReportSection):
    """Executive summary with overall score and priority actions"""

    def __init__(self, data: Dict[str, Any], all_sections: List[ReportSection] = None):
        super().__init__("Executive Summary", data)
        self.all_sections = all_sections or []
        self.priority_actions = []
        self.overall_score = 0
        self.section_breakdown = {}

    def analyze(self) -> Dict[str, Any]:
        """Analyze all sections and create executive summary"""
        logger.info("Generating executive summary")

        # Calculate overall score from all sections
        if self.all_sections:
            section_scores = [s.get_score() for s in self.all_sections if hasattr(s, 'get_score')]
            self.overall_score = int(sum(section_scores) / len(section_scores)) if section_scores else 0

            # Build section breakdown
            for section in self.all_sections:
                if hasattr(section, 'section_name'):
                    self.section_breakdown[section.section_name] = {
                        'score': section.get_score(),
                        'rating': section.get_rating()
                    }
        else:
            self.overall_score = 0

        # Collect all recommendations from all sections
        all_recommendations = []
        for section in self.all_sections:
            if hasattr(section, 'recommendations'):
                all_recommendations.extend(section.recommendations)

        # Select priority actions
        self.priority_actions = self._select_priority_actions(all_recommendations)

        self.score = self.overall_score
        self.rating = self.get_rating()
        self.analyzed = True

        logger.info(f"Executive summary generated: Score {self.overall_score}/100, {len(self.priority_actions)} priority actions")

        return {
            'score': self.score,
            'rating': self.rating,
            'overall_score': self.overall_score,
            'priority_actions': self.priority_actions,
            'section_breakdown': self.section_breakdown
        }

    def _select_priority_actions(self, recommendations: List) -> List:
        """
        Select top priority actions from all recommendations

        Algorithm:
        1. All CRITICAL priority items
        2. High impact + High/Medium priority
        3. Sort by impact level
        4. Return top 5

        Args:
            recommendations: List of Recommendation objects

        Returns:
            List of top priority recommendations
        """
        if not recommendations:
            return []

        priority_actions = []

        # Helper to get priority value
        def get_priority_value(rec):
            if hasattr(rec, 'priority'):
                if hasattr(rec.priority, 'value'):
                    return rec.priority.value
                return rec.priority
            return 'medium'

        # Helper to get impact value
        def get_impact_value(rec):
            if hasattr(rec, 'impact'):
                if hasattr(rec.impact, 'value'):
                    return rec.impact.value
                return rec.impact
            return 'medium'

        # Priority 1: All critical items
        critical_items = [r for r in recommendations if get_priority_value(r) == 'critical']
        priority_actions.extend(critical_items)

        # Priority 2: High impact + high priority
        high_items = [r for r in recommendations
                     if get_priority_value(r) == 'high' and get_impact_value(r) == 'high']
        priority_actions.extend(high_items)

        # Priority 3: High impact + medium priority
        if len(priority_actions) < 5:
            medium_high_items = [r for r in recommendations
                                if get_priority_value(r) == 'medium' and get_impact_value(r) == 'high']
            priority_actions.extend(medium_high_items)

        # Remove duplicates and limit to top 5
        seen = set()
        unique_actions = []
        for action in priority_actions[:8]:  # Check up to 8 to ensure 5 unique
            action_id = f"{action.title}_{action.category}" if hasattr(action, 'title') else str(action)
            if action_id not in seen:
                seen.add(action_id)
                unique_actions.append(action)
                if len(unique_actions) >= 5:
                    break

        return unique_actions

    def generate_markdown(self) -> str:
        """Generate executive summary markdown"""
        if not self.analyzed:
            self.analyze()

        rating_emoji = {
            'excellent': '✅',
            'good': '🟢',
            'fair': '🟡',
            'poor': '🔴'
        }

        emoji = rating_emoji.get(self.rating, '⚪')

        # Header
        markdown = f"""# 📊 EXECUTIVE SUMMARY

## Overall Assessment

**Overall Score: {self.overall_score}/100** {emoji} **{self.rating.upper()}**

*Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*

"""

        # Add interpretation
        if self.overall_score >= 80:
            markdown += "\n✨ **Excellent foundation.** Your store page is well-optimized. Focus on fine-tuning and marketing execution.\n\n"
        elif self.overall_score >= 65:
            markdown += "\n👍 **Solid foundation with room for improvement.** Address the priority actions below to maximize your launch potential.\n\n"
        elif self.overall_score >= 50:
            markdown += "\n⚠️ **Significant gaps identified.** Critical improvements needed before launch. Priority actions below will have major impact.\n\n"
        else:
            markdown += "\n🚨 **Store page needs major work.** Multiple critical issues must be addressed. Start with priority actions immediately.\n\n"

        markdown += "---\n\n"

        # Section breakdown
        if self.section_breakdown:
            markdown += "## Section Scores\n\n"
            markdown += "| Section | Score | Rating |\n"
            markdown += "|---------|-------|--------|\n"

            for section_name, section_data in self.section_breakdown.items():
                score = section_data['score']
                rating = section_data['rating']
                section_emoji = rating_emoji.get(rating, '⚪')

                markdown += f"| {section_name} | {score}/100 | {section_emoji} {rating.title()} |\n"

            markdown += "\n---\n\n"

        # Priority actions
        if self.priority_actions:
            markdown += "## 🎯 Priority Actions\n\n"
            markdown += "*Top recommendations ranked by impact and urgency*\n\n"

            for i, action in enumerate(self.priority_actions, 1):
                # Get priority and impact
                priority_val = action.priority.value if hasattr(action.priority, 'value') else action.priority
                impact_val = action.impact.value if hasattr(action.impact, 'value') else action.impact

                priority_emoji = {
                    'critical': '🔴',
                    'high': '🟡',
                    'medium': '🟢',
                    'low': '⚪'
                }

                impact_label = impact_val.upper() if isinstance(impact_val, str) else str(impact_val)
                emoji_icon = priority_emoji.get(priority_val, '⚪')

                markdown += f"### {i}. {emoji_icon} {action.title}\n\n"
                markdown += f"**Priority:** {priority_val.title()} | **Impact:** {impact_label}"

                # Add effort and cost if available
                if hasattr(action, 'effort') and action.effort:
                    effort_val = action.effort.value if hasattr(action.effort, 'value') else action.effort
                    markdown += f" | **Effort:** {effort_val.title()}"
                if hasattr(action, 'estimated_cost') and action.estimated_cost:
                    markdown += f" | **Cost:** {action.estimated_cost}"
                if hasattr(action, 'time_estimate') and action.time_estimate:
                    markdown += f" | **Time:** {action.time_estimate}"

                markdown += "\n\n"
                markdown += f"{action.description}\n\n"

                # Add implementation steps if available
                if hasattr(action, 'implementation_steps') and action.implementation_steps:
                    markdown += "**How to implement:**\n"
                    for step_num, step in enumerate(action.implementation_steps, 1):
                        markdown += f"{step_num}. {step}\n"
                    markdown += "\n"

                # Add expected result if available
                if hasattr(action, 'expected_result') and action.expected_result:
                    markdown += f"**Expected result:** {action.expected_result}\n\n"

            markdown += "---\n\n"

        # Impact vs Effort Matrix
        if self.priority_actions:
            markdown += self._generate_impact_effort_matrix()

        return markdown

    def _generate_impact_effort_matrix(self) -> str:
        """Generate impact vs effort matrix for all recommendations"""
        markdown = "## 📊 Impact vs. Effort Matrix\n\n"
        markdown += "*All recommendations organized by implementation priority*\n\n"

        # Collect all recommendations from all sections
        all_recs = []
        for section in self.all_sections:
            if hasattr(section, 'recommendations'):
                for rec in section.recommendations:
                    # Get values
                    priority = rec.priority.value if hasattr(rec.priority, 'value') else rec.priority
                    impact = rec.impact.value if hasattr(rec.impact, 'value') else rec.impact
                    effort = getattr(rec, 'effort', self._estimate_effort(rec))
                    time_est = getattr(rec, 'time_estimate', self._estimate_time(rec))

                    all_recs.append({
                        'title': rec.title,
                        'category': rec.category if hasattr(rec, 'category') else 'General',
                        'priority': priority,
                        'impact': impact,
                        'effort': effort,
                        'time': time_est,
                        'description': rec.description if hasattr(rec, 'description') else ''
                    })

        if not all_recs:
            return ""

        # Sort: High Impact/Low Effort first
        priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        impact_order = {'high': 3, 'medium': 2, 'low': 1}
        effort_order = {'low': 3, 'medium': 2, 'high': 1}  # Inverted - low effort is better

        all_recs.sort(
            key=lambda x: (
                impact_order.get(x['impact'], 0),
                effort_order.get(x['effort'], 0),
                priority_order.get(x['priority'], 0)
            ),
            reverse=True
        )

        # Build matrix table
        markdown += "| # | Recommendation | Category | Impact | Effort | Est. Time | Sequence |\n"
        markdown += "|---|----------------|----------|--------|--------|-----------|----------|\n"

        for i, rec in enumerate(all_recs[:15], 1):  # Limit to top 15
            # Determine sequence suggestion
            if i <= 3:
                sequence = "🔴 Do First"
            elif i <= 8:
                sequence = "🟡 Do Next"
            else:
                sequence = "🟢 Do Later"

            # Format impact/effort
            impact_icon = {"high": "⬆️", "medium": "➡️", "low": "⬇️"}.get(rec['impact'], "➡️")
            effort_icon = {"low": "✅", "medium": "⚠️", "high": "🔴"}.get(rec['effort'], "⚠️")

            markdown += f"| {i} | {rec['title'][:40]}{'...' if len(rec['title']) > 40 else ''} | {rec['category']} | {impact_icon} {rec['impact'].title()} | {effort_icon} {rec['effort'].title()} | {rec['time']} | {sequence} |\n"

        markdown += "\n**Legend:**\n"
        markdown += "- **Impact**: ⬆️ High | ➡️ Medium | ⬇️ Low\n"
        markdown += "- **Effort**: ✅ Low (quick win) | ⚠️ Medium | 🔴 High (major work)\n"
        markdown += "- **Sequence**: 🔴 Critical path | 🟡 High value | 🟢 Future optimization\n\n"

        markdown += "💡 **Strategy**: Focus on HIGH impact + LOW/MEDIUM effort items first (quick wins), then tackle HIGH effort items only if impact justifies investment.\n\n"

        markdown += "---\n\n"

        return markdown

    def _estimate_effort(self, rec) -> str:
        """Estimate effort level from recommendation if not provided"""
        title_lower = rec.title.lower() if hasattr(rec, 'title') else ''

        # High effort keywords
        if any(word in title_lower for word in ['rebuild', 'overhaul', 'complete', 'full', 'extensive']):
            return 'high'
        # Low effort keywords
        elif any(word in title_lower for word in ['add', 'update', 'adjust', 'tweak', 'optimize']):
            return 'low'
        else:
            return 'medium'

    def _estimate_time(self, rec) -> str:
        """Estimate time from recommendation if not provided"""
        effort = self._estimate_effort(rec)

        if effort == 'high':
            return '1-2 weeks'
        elif effort == 'low':
            return '1-4 hours'
        else:
            return '1-3 days'


class StorePageSection(ReportSection):
    """Store page optimization analysis"""

    def analyze(self) -> Dict[str, Any]:
        """Analyze store page elements using StorePageAnalyzer"""
        logger.info("Analyzing store page")

        from src.store_analyzer import StorePageAnalyzer

        game_data = self.data.get('game_data', {})
        competitor_data = self.data.get('competitors', [])

        analyzer = StorePageAnalyzer()
        analysis = analyzer.analyze_complete(game_data, competitor_data)

        self.score = analysis['overall_score']
        self.rating = analysis['overall_rating']
        self.recommendations = analysis['recommendations']
        self.benchmarks = analysis.get('sections', {})
        self.analyzed = True

        return {
            'score': self.score,
            'rating': self.rating,
            'recommendations': self.recommendations,
            'sections': analysis['sections'],
            'strengths': analysis['strengths'],
            'weaknesses': analysis['weaknesses']
        }

    def generate_markdown(self) -> str:
        """Generate store page analysis markdown"""
        if not self.analyzed:
            self.analyze()

        rating_emoji = {'excellent': '✅', 'good': '🟢', 'fair': '🟡', 'poor': '🔴'}
        emoji = rating_emoji.get(self.rating, '⚪')

        markdown = f"""## Store Page Optimization

**Overall Score: {self.score}/100** {emoji} {self.rating.title()}

"""

        # Section breakdown
        if self.benchmarks:
            markdown += "### Component Scores\n\n"
            for section_name, section_data in self.benchmarks.items():
                section_score = section_data.get('score', 0)
                section_rating = section_data.get('rating', 'unknown')
                section_emoji = rating_emoji.get(section_rating, '⚪')

                markdown += f"- **{section_name.title()}**: {section_score}/100 {section_emoji}\n"
                markdown += f"  - {section_data.get('reason', 'No details')}\n"

            markdown += "\n"

        # Recommendations
        if self.recommendations:
            markdown += "### Recommendations\n\n"

            # Group by priority
            critical = [r for r in self.recommendations if r.priority == 'critical' or (hasattr(r, 'priority') and r.priority.value == 'critical')]
            high = [r for r in self.recommendations if r.priority == 'high' or (hasattr(r, 'priority') and r.priority.value == 'high')]
            medium = [r for r in self.recommendations if r.priority == 'medium' or (hasattr(r, 'priority') and r.priority.value == 'medium')]

            if critical:
                markdown += "#### 🔴 Critical Priority\n\n"
                for rec in critical:
                    markdown += f"**{rec.title}**\n"
                    markdown += f"{rec.description}\n\n"

            if high:
                markdown += "#### 🟡 High Priority\n\n"
                for rec in high:
                    markdown += f"**{rec.title}**\n"
                    markdown += f"{rec.description}\n\n"

            if medium:
                markdown += "#### 🟢 Medium Priority\n\n"
                for rec in medium[:3]:  # Limit to top 3 medium priority
                    markdown += f"**{rec.title}**\n"
                    markdown += f"{rec.description}\n\n"

        markdown += "---\n\n"

        return markdown


class CompetitorSection(ReportSection):
    """Competitor analysis and benchmarking"""

    def analyze(self) -> Dict[str, Any]:
        """Analyze competitive position"""
        logger.info("Analyzing competitors")

        competitors = self.data.get('competitors', [])
        game_data = self.data.get('game_data', {})

        # Score based on competitive positioning
        if len(competitors) >= 5:
            self.score = 80
            self.rating = "good"
        elif len(competitors) >= 3:
            self.score = 65
            self.rating = "fair"
        else:
            self.score = 40
            self.rating = "poor"

        # Analyze pricing vs competitors
        your_price = game_data.get('price_overview', {}).get('final', 0) / 100
        comp_prices = [c.get('price_overview', {}).get('final', 0) / 100
                      for c in competitors if c.get('price_overview')]

        if comp_prices:
            avg_comp_price = sum(comp_prices) / len(comp_prices)
            price_diff_pct = abs(your_price - avg_comp_price) / avg_comp_price * 100 if avg_comp_price > 0 else 0

            # Adjust score based on pricing
            if price_diff_pct < 15:  # Within 15% of average
                self.score += 10
            elif price_diff_pct > 30:  # More than 30% different
                self.score -= 5

        self.score = min(100, max(0, self.score))
        self.rating = self.get_rating()
        self.analyzed = True

        return {
            'score': self.score,
            'rating': self.rating,
            'competitor_count': len(competitors),
            'price_positioning': 'competitive' if price_diff_pct < 15 else 'divergent'
        }

    def generate_markdown(self) -> str:
        """Generate competitor analysis markdown with visualizations"""
        if not self.analyzed:
            self.analyze()

        from src.visualizations import ReportVisualizer

        competitors = self.data.get('competitors', [])
        game_data = self.data.get('game_data', {})

        rating_emoji = {'excellent': '✅', 'good': '🟢', 'fair': '🟡', 'poor': '🔴'}
        emoji = rating_emoji.get(self.rating, '⚪')

        markdown = f"""## Competitive Analysis

**Score: {self.score}/100** {emoji} {self.rating.title()}

Analyzed {len(competitors)} direct competitors in your genre.

---

"""

        # Add comparison table
        if competitors and game_data:
            viz = ReportVisualizer()
            markdown += viz.create_comparison_table(game_data, competitors)
            markdown += "\n"

        # Add top competitors highlight
        if competitors:
            viz = ReportVisualizer()
            markdown += viz.create_competitor_highlights(competitors, top_n=5)

        # Add insights
        markdown += "### Key Insights\n\n"

        if competitors:
            # Price analysis
            your_price = game_data.get('price_overview', {}).get('final', 0) / 100
            comp_prices = [c.get('price_overview', {}).get('final', 0) / 100
                          for c in competitors if c.get('price_overview')]

            if comp_prices:
                avg_price = sum(comp_prices) / len(comp_prices)
                if your_price < avg_price * 0.85:
                    markdown += f"- 💰 **Pricing**: Your price (${your_price:.2f}) is **{((avg_price - your_price) / avg_price * 100):.0f}% below** competitors (${avg_price:.2f}). Consider if you're undervaluing.\n"
                elif your_price > avg_price * 1.15:
                    markdown += f"- 💰 **Pricing**: Your price (${your_price:.2f}) is **{((your_price - avg_price) / avg_price * 100):.0f}% above** competitors (${avg_price:.2f}). Ensure premium positioning is justified.\n"
                else:
                    markdown += f"- 💰 **Pricing**: Your price (${your_price:.2f}) is **well-positioned** vs competitors (${avg_price:.2f}).\n"

            # Screenshot comparison
            your_screenshots = len(game_data.get('screenshots', []))
            comp_screenshots = [len(c.get('screenshots', [])) for c in competitors]
            avg_screenshots = sum(comp_screenshots) / len(comp_screenshots) if comp_screenshots else 0

            if your_screenshots < avg_screenshots * 0.8:
                markdown += f"- 📸 **Screenshots**: You have {your_screenshots} screenshots. Competitors average {avg_screenshots:.0f}. **Add {int(avg_screenshots - your_screenshots)} more**.\n"
            else:
                markdown += f"- 📸 **Screenshots**: Your {your_screenshots} screenshots match competitor standards ({avg_screenshots:.0f} avg).\n"

        markdown += "\n---\n\n"

        return markdown


class PricingSection(ReportSection):
    """Pricing strategy analysis"""

    def analyze(self) -> Dict[str, Any]:
        """Analyze pricing strategy"""
        logger.info("Analyzing pricing")

        # Placeholder - will be enhanced
        self.score = 75
        self.rating = self.get_rating()
        self.analyzed = True

        return {
            'score': self.score,
            'rating': self.rating
        }

    def generate_markdown(self) -> str:
        """Generate pricing analysis markdown"""
        if not self.analyzed:
            self.analyze()

        return f"""## Pricing Analysis

**Score: {self.score}/100** - {self.rating.title()}

[Detailed pricing analysis will be added in Phase 1]

"""


class MarketingSection(ReportSection):
    """Marketing readiness analysis"""

    def analyze(self) -> Dict[str, Any]:
        """Analyze marketing readiness"""
        logger.info("Analyzing marketing readiness")

        # Placeholder - will be enhanced
        self.score = 60
        self.rating = self.get_rating()
        self.analyzed = True

        return {
            'score': self.score,
            'rating': self.rating
        }

    def generate_markdown(self) -> str:
        """Generate marketing analysis markdown"""
        if not self.analyzed:
            self.analyze()

        return f"""## Marketing Readiness

**Score: {self.score}/100** - {self.rating.title()}

[Detailed marketing analysis will be added in Phase 2]

"""


class CommunitySection(ReportSection):
    """Community and social media analysis"""

    def analyze(self) -> Dict[str, Any]:
        """Analyze community presence"""
        logger.info("Analyzing community presence")

        reddit_data = self.data.get('reddit', {})
        subreddits = reddit_data.get('subreddits', [])

        # Score based on subreddit reach
        total_reach = reddit_data.get('total_reach', 0)

        if total_reach > 1000000:
            self.score = 85
        elif total_reach > 500000:
            self.score = 75
        elif total_reach > 100000:
            self.score = 65
        else:
            self.score = 50

        self.rating = self.get_rating()
        self.analyzed = True

        return {
            'score': self.score,
            'rating': self.rating,
            'subreddit_count': len(subreddits),
            'total_reach': total_reach
        }

    def generate_markdown(self) -> str:
        """Generate community analysis markdown"""
        if not self.analyzed:
            self.analyze()

        reddit_data = self.data.get('reddit', {})
        subreddits = reddit_data.get('subreddits', [])
        recommendations = reddit_data.get('recommendations', [])

        rating_emoji = {'excellent': '✅', 'good': '🟢', 'fair': '🟡', 'poor': '🔴'}
        emoji = rating_emoji.get(self.rating, '⚪')

        markdown = f"""## Community & Social Presence

**Score: {self.score}/100** {emoji} {self.rating.title()}

### Reddit Communities

Found {len(subreddits)} relevant subreddits with {reddit_data.get('total_reach', 0):,} combined subscribers.

"""

        # Top subreddits table
        if subreddits:
            markdown += "| Subreddit | Subscribers | Description |\n"
            markdown += "|-----------|-------------|-------------|\n"

            for sub in subreddits[:5]:
                markdown += f"| r/{sub['name']} | {sub.get('subscribers', 0):,} | {sub.get('description', 'N/A')[:50]}... |\n"

            markdown += "\n"

        # Recommendations
        if recommendations:
            markdown += "### Recommendations\n\n"
            for rec in recommendations:
                markdown += f"- {rec}\n"
            markdown += "\n"

        markdown += "---\n\n"

        return markdown


class InfluencerSection(ReportSection):
    """Influencer and content creator outreach analysis"""

    def analyze(self) -> Dict[str, Any]:
        """Analyze influencer opportunities"""
        logger.info("Analyzing influencer opportunities")

        twitch_data = self.data.get('twitch', {})
        youtube_data = self.data.get('youtube', {})
        curator_data = self.data.get('curators', {})

        # Calculate score based on total reach potential
        total_reach = 0
        total_reach += sum(s.get('followers', 0) for s in twitch_data.get('streamers', []))
        total_reach += sum(c.get('subscribers', 0) for c in youtube_data.get('channels', []))
        total_reach += sum(c.get('followers', 0) for c in curator_data.get('curators', []))

        if total_reach > 5000000:
            self.score = 90
        elif total_reach > 2000000:
            self.score = 80
        elif total_reach > 500000:
            self.score = 70
        else:
            self.score = 60

        self.rating = self.get_rating()
        self.analyzed = True

        return {
            'score': self.score,
            'rating': self.rating,
            'total_reach': total_reach
        }

    def generate_markdown(self) -> str:
        """Generate influencer outreach markdown"""
        if not self.analyzed:
            self.analyze()

        twitch_data = self.data.get('twitch', {})
        youtube_data = self.data.get('youtube', {})
        curator_data = self.data.get('curators', {})

        rating_emoji = {'excellent': '✅', 'good': '🟢', 'fair': '🟡', 'poor': '🔴'}
        emoji = rating_emoji.get(self.rating, '⚪')

        markdown = f"""## Influencer Outreach Strategy

**Score: {self.score}/100** {emoji} {self.rating.title()}

### Twitch Streamers

"""
        streamers = twitch_data.get('streamers', [])
        if streamers:
            markdown += f"Found {len(streamers)} relevant streamers.\n\n"
            markdown += "| Streamer | Followers | Priority | ROI Score |\n"
            markdown += "|----------|-----------|----------|----------|\n"

            for streamer in streamers[:5]:
                markdown += f"| {streamer['name']} | {streamer.get('followers', 0):,} | {streamer.get('priority', 'medium').title()} | {streamer.get('roi_score', 0):.0f} |\n"

            markdown += "\n"
        else:
            markdown += "No streamer data available.\n\n"

        # YouTube
        markdown += "### YouTube Channels\n\n"
        channels = youtube_data.get('channels', [])
        if channels:
            markdown += f"Found {len(channels)} relevant channels.\n\n"
            markdown += "| Channel | Subscribers | Priority | ROI Score |\n"
            markdown += "|---------|-------------|----------|----------|\n"

            for channel in channels[:5]:
                markdown += f"| {channel.get('name', 'Unknown')} | {channel.get('subscribers', 0):,} | {channel.get('outreach_priority', 'medium').title()} | {channel.get('roi_score', 0):.0f} |\n"

            markdown += "\n"
        else:
            markdown += "No YouTube data available.\n\n"

        # Steam Curators
        markdown += "### Steam Curators\n\n"
        curators = curator_data.get('curators', [])
        if curators:
            outreach_plan = curator_data.get('outreach_plan', {})
            markdown += f"Found {len(curators)} relevant curators with {outreach_plan.get('estimated_total_reach', 0):,} total reach.\n\n"

            markdown += "**Top Priority Curators:**\n\n"
            markdown += "| Curator | Followers | Response Rate | Priority |\n"
            markdown += "|---------|-----------|---------------|----------|\n"

            for curator in curators[:5]:
                markdown += f"| {curator['name']} | {curator.get('followers', 0):,} | {curator.get('response_rate', 'Medium')} | {curator.get('priority', 0):.0f} |\n"

            markdown += "\n"
        else:
            markdown += "No curator data available.\n\n"

        markdown += "---\n\n"

        return markdown


class GlobalReachSection(ReportSection):
    """Regional pricing and localization analysis"""

    def analyze(self) -> Dict[str, Any]:
        """Analyze global market readiness"""
        logger.info("Analyzing global market readiness")

        pricing_data = self.data.get('regional_pricing', {})
        localization_data = self.data.get('localization', {})

        # Score based on market coverage
        current_reach = localization_data.get('current_market_reach_percent', 0)

        if current_reach >= 80:
            self.score = 90
        elif current_reach >= 60:
            self.score = 75
        elif current_reach >= 40:
            self.score = 65
        else:
            self.score = 50

        self.rating = self.get_rating()
        self.analyzed = True

        return {
            'score': self.score,
            'rating': self.rating,
            'market_coverage': current_reach
        }

    def generate_markdown(self) -> str:
        """Generate global reach analysis markdown"""
        if not self.analyzed:
            self.analyze()

        pricing_data = self.data.get('regional_pricing', {})
        localization_data = self.data.get('localization', {})

        rating_emoji = {'excellent': '✅', 'good': '🟢', 'fair': '🟡', 'poor': '🔴'}
        emoji = rating_emoji.get(self.rating, '⚪')

        markdown = f"""## Global Market Readiness

**Score: {self.score}/100** {emoji} {self.rating.title()}

### Regional Pricing

"""

        if pricing_data:
            revenue_impact = pricing_data.get('revenue_impact', {})
            markdown += f"**Revenue Potential**: {revenue_impact.get('revenue_increase_percent', 0):.1f}% increase with optimized regional pricing\n\n"

            priority_regions = pricing_data.get('priority_regions', [])
            if priority_regions:
                markdown += "**Priority Regions:**\n\n"
                markdown += "| Region | Recommended Price | Market Size |\n"
                markdown += "|--------|-------------------|-------------|\n"

                for region in priority_regions[:8]:
                    markdown += f"| {region['region_name']} | {region['recommended_price']} | {region['market_size'].title()} |\n"

                markdown += "\n"

            # Recommendations
            recommendations = pricing_data.get('recommendations', [])
            if recommendations:
                markdown += "**Pricing Recommendations:**\n\n"
                for rec in recommendations:
                    markdown += f"- {rec}\n"
                markdown += "\n"
        else:
            markdown += "No regional pricing data available.\n\n"

        # Localization
        markdown += "### Localization Strategy\n\n"

        if localization_data:
            current_languages = localization_data.get('current_languages', [])
            current_reach = localization_data.get('current_market_reach_percent', 0)

            markdown += f"**Current Coverage**: {len(current_languages)} languages, ~{current_reach}% of global market\n\n"

            missing_languages = localization_data.get('missing_languages', [])
            if missing_languages:
                markdown += "**High-ROI Language Opportunities:**\n\n"
                markdown += "| Language | Cost | Potential Revenue | ROI % |\n"
                markdown += "|----------|------|-------------------|-------|\n"

                for lang in missing_languages[:5]:
                    if lang.get('priority') == 'high':
                        markdown += f"| {lang['language']} | ${lang['localization_cost']:,} | ${lang['additional_revenue']:,.0f} | {lang['roi_percent']:.0f}% |\n"

                markdown += "\n"

            # Recommendations
            loc_recommendations = localization_data.get('recommendations', [])
            if loc_recommendations:
                markdown += "**Localization Recommendations:**\n\n"
                for rec in loc_recommendations:
                    markdown += f"- {rec}\n"
                markdown += "\n"
        else:
            markdown += "No localization data available.\n\n"

        markdown += "---\n\n"

        return markdown


class MarketViabilitySection(ReportSection):
    """Market viability and TAM analysis"""

    def analyze(self) -> Dict[str, Any]:
        """Analyze market viability"""
        logger.info("Analyzing market viability")

        from src.market_viability import analyze_market_viability

        game_data = self.data.get('game_data', {})
        competitor_data = self.data.get('competitors', [])
        sales_data = self.data.get('sales_data')

        analysis = analyze_market_viability(game_data, competitor_data, sales_data)

        # Score based on viability score
        self.score = analysis['viability_score']
        self.rating = self.get_rating()
        self.analyzed = True

        self.viability_data = analysis

        return {
            'score': self.score,
            'rating': self.rating
        }

    def generate_markdown(self) -> str:
        """Generate market viability markdown"""
        if not self.analyzed:
            self.analyze()

        viability = self.viability_data
        tam = viability['tam_analysis']
        saturation = viability['saturation_analysis']
        demand = viability['demand_analysis']
        success = viability['success_probability']

        rating_emoji = {'excellent': '✅', 'good': '🟢', 'fair': '🟡', 'poor': '🔴'}
        emoji = rating_emoji.get(self.rating, '⚪')

        markdown = f"""## Market Viability & Opportunity

**Score: {self.score}/100** {emoji} {self.rating.title()}

{viability['recommendation']}

---

### Total Addressable Market (TAM)

**Genre**: {tam['primary_genre']}
**Annual Market Size**: ${tam['annual_market_revenue']:,}
**Market Classification**: {tam['market_size']} market
**Growth Trend**: {tam['growth_trend']} ({tam['annual_growth_rate']} annual growth)

**Market Metrics**:
- Total games in genre: {tam['total_games_in_genre']:,}
- New releases per year: {tam['new_releases_per_year']:,}
- Average revenue per game: ${tam['avg_revenue_per_game']:,}
- Median game revenue: ${tam['median_game_revenue']:,}
- Top performer revenue: ${tam['top_game_revenue']:,}

**Opportunity Level**: {tam['opportunity_level']}

---

### Competitive Saturation

**Saturation Level**: {saturation['saturation_level']}
**Competition Risk**: {saturation['risk_level']}
**Market Density**: {saturation['competitive_density']}

**Saturation Analysis**:
- Current games in genre: {saturation['total_games_in_genre']:,}
- Annual new releases: {saturation['new_releases_per_year']:,}
- Saturation ratio: {saturation['saturation_ratio']}
- Direct competitors analyzed: {saturation['direct_competitors_analyzed']}
- Estimated revenue dilution: {saturation['revenue_dilution_estimate']}

{self._get_saturation_insight(saturation)}

---

### Success Probability

**Estimated Success Rate**: {success['success_probability']} (for games earning >$100K)
**Outlook**: {success['outlook']}
**Confidence**: {success['confidence_level']}

**Projected Revenue Range**:
- Conservative: ${success['projected_revenue_range']['low']:,}
- Median: ${success['projected_revenue_range']['median']:,}
- Optimistic: ${success['projected_revenue_range']['high']:,}

**Key Success Factors**:
"""
        for factor in success['key_success_factors']:
            markdown += f"- {factor}\n"

        markdown += "\n---\n\n### Demand Signals\n\n"

        markdown += f"**Demand Level**: {demand['demand_level']}  \n"
        markdown += f"**Validation Score**: {demand['demand_score']}/100\n\n"

        markdown += "**Current Validation Signals**:\n"
        for signal in demand['validation_signals']:
            markdown += f"- {signal}\n"

        markdown += f"\n**Benchmark Comparison**: {demand['benchmark_comparison']}\n\n"

        markdown += "---\n\n"

        return markdown

    def _get_saturation_insight(self, saturation: Dict) -> str:
        """Generate insight text based on saturation level"""
        if saturation['saturation_score'] > 75:
            return "💡 **Insight**: Market has room for new entrants. Focus on quality differentiation."
        elif saturation['saturation_score'] > 55:
            return "⚠️ **Insight**: Moderate competition. Clear unique selling proposition required."
        else:
            return "🚨 **Insight**: Highly competitive market. Strong differentiation and marketing budget essential."


class ReportBuilder:
    """Orchestrates report generation from multiple sections"""

    def __init__(self, game_data: Dict[str, Any], sales_data: Dict[str, Any],
                 competitor_data: List[Dict[str, Any]], report_type: str):
        self.game_data = game_data
        self.sales_data = sales_data
        self.competitor_data = competitor_data
        self.report_type = report_type

        self.sections: List[ReportSection] = []
        self.executive_summary: Optional[ExecutiveSummarySection] = None
        self.overall_score = 0

        logger.info(f"ReportBuilder initialized for {game_data.get('name', 'Unknown Game')}")

    def add_section(self, section: ReportSection):
        """Add a section to the report"""
        self.sections.append(section)
        logger.debug(f"Added section: {section.section_name}")

    def build_sections(self):
        """Build all standard sections"""
        logger.info("Building report sections")

        # Create market viability section FIRST (most important for decision-making)
        viability_section = MarketViabilitySection("Market Viability", {
            'game_data': self.game_data,
            'competitors': self.competitor_data,
            'sales_data': self.sales_data
        })
        self.add_section(viability_section)

        # Create standard sections
        competitor_section = CompetitorSection("Competitors", {
            'competitors': self.competitor_data,
            'game_data': self.game_data
        })
        self.add_section(competitor_section)

        store_section = StorePageSection("Store Page", {
            'game_data': self.game_data,
            'competitors': self.competitor_data
        })
        self.add_section(store_section)

        pricing_section = PricingSection("Pricing", {
            'game_data': self.game_data,
            'sales_data': self.sales_data,
            'competitors': self.competitor_data
        })
        self.add_section(pricing_section)

        marketing_section = MarketingSection("Marketing", {
            'game_data': self.game_data,
            'report_type': self.report_type
        })
        self.add_section(marketing_section)

        # Create executive summary (references other sections)
        self.executive_summary = ExecutiveSummarySection("Executive Summary", {
            'game_data': self.game_data,
            'report_type': self.report_type
        }, all_sections=self.sections)

        logger.info(f"Built {len(self.sections)} sections + executive summary")

    def calculate_overall_score(self) -> int:
        """Calculate weighted overall score"""
        if not self.sections:
            return 0

        # Weights for different sections
        weights = {
            'Store Page': 0.30,
            'Competitors': 0.25,
            'Pricing': 0.20,
            'Marketing': 0.25
        }

        weighted_score = 0
        total_weight = 0

        for section in self.sections:
            weight = weights.get(section.section_name, 0.1)
            weighted_score += section.get_score() * weight
            total_weight += weight

        self.overall_score = int(weighted_score / total_weight) if total_weight > 0 else 0
        logger.info(f"Overall score calculated: {self.overall_score}/100")

        return self.overall_score

    def build(self) -> str:
        """
        Generate complete report

        Returns:
            Complete markdown report
        """
        logger.info("Building complete report")

        # Build all sections if not already built
        if not self.sections:
            self.build_sections()

        # Calculate overall score
        self.calculate_overall_score()

        # Build report markdown
        report_parts = []

        # Add executive summary first
        if self.executive_summary:
            report_parts.append(self.executive_summary.generate_markdown())

        # Add all other sections
        for section in self.sections:
            report_parts.append(section.generate_markdown())

        # Add footer
        report_parts.append(self._generate_footer())

        report = "\n\n".join(report_parts)

        logger.info(f"Report built successfully ({len(report)} characters)")

        return report

    def _generate_footer(self) -> str:
        """Generate report footer"""
        game_name = self.game_data.get('name', 'Unknown Game')

        return f"""---

## Data Sources & Methodology

This report aggregates data from multiple authoritative sources to provide comprehensive market intelligence:

### Primary Data Sources
- **Steam Store API**: Game metadata, pricing, store page elements, supported languages
- **Steam Community**: Review data, community features, discussion activity
- **SteamSpy**: Sales estimates, player statistics, market performance data
- **SteamDB**: Historical pricing, concurrent players, regional availability

### Market Intelligence Sources
- **Reddit API**: Community size, engagement metrics, self-promotion policies (r/indiegaming, r/gamedev, etc.)
- **Genre Market Data**: TAM estimates, growth trends, competitive saturation metrics
- **Regional Economic Data**: PPP (Purchasing Power Parity) multipliers, currency conversions
- **Localization Benchmarks**: Industry-standard translation costs, market reach percentages

### Influencer & Outreach Data
- **Twitch**: Streamer databases, viewership benchmarks, genre-specific engagement rates
- **YouTube**: Content creator discovery, subscriber metrics, engagement analysis
- **Steam Curators**: Curator databases, follower counts, review focus areas, response patterns

### Analysis Methodology
- **Competitive Analysis**: Genre-based similarity matching, price positioning analysis
- **AI Vision Analysis**: Claude 4.5 Sonnet capsule image evaluation across 10 dimensions
- **Market Viability**: TAM sizing, competitive saturation modeling, success probability calculations
- **ROI Modeling**: Regional pricing optimization, localization cost-benefit analysis

**Data Freshness**: All data collected on {datetime.now().strftime('%Y-%m-%d at %I:%M %p')}
**Report Version:** 2.1 (Enhanced with Market Viability + Impact Matrix)
**Analysis Type:** {self.report_type}
**Overall Score:** {self.overall_score}/100

---

## About Publitz Automated Audits

Professional game market intelligence powered by AI and real-time data aggregation.

For questions or support: support@publitz.com

---

*This report contains confidential market intelligence and is intended solely for {game_name}.
Data accuracy is dependent on third-party API availability and may contain estimates where actual data is unavailable.*
"""

    def get_structured_data(self) -> Dict[str, Any]:
        """
        Get structured report data for exports

        Returns:
            Complete report data as dictionary
        """
        if not self.sections:
            self.build_sections()
            self.calculate_overall_score()

        return {
            'game_name': self.game_data.get('name', 'Unknown'),
            'report_type': self.report_type,
            'generated_at': datetime.now().isoformat(),
            'overall_score': self.overall_score,
            'sections': [
                {
                    'name': section.section_name,
                    'score': section.get_score(),
                    'rating': section.get_rating(),
                    'analyzed': section.analyzed
                }
                for section in self.sections
            ]
        }


# Convenience function for backward compatibility
def build_enhanced_report(game_data: Dict[str, Any], sales_data: Dict[str, Any],
                         competitor_data: List[Dict[str, Any]], report_type: str) -> str:
    """
    Build enhanced report with new modular system

    Args:
        game_data: Game information from Steam
        sales_data: Sales/revenue data
        competitor_data: List of competitor games
        report_type: "Pre-Launch" or "Post-Launch"

    Returns:
        Complete markdown report
    """
    builder = ReportBuilder(game_data, sales_data, competitor_data, report_type)
    return builder.build()
