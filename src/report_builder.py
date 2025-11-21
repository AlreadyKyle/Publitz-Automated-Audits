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
            impact = rec['impact'] or 'medium'
            effort = rec['effort'] or 'medium'
            impact_icon = {"high": "⬆️", "medium": "➡️", "low": "⬇️"}.get(impact, "➡️")
            effort_icon = {"low": "✅", "medium": "⚠️", "high": "🔴"}.get(effort, "⚠️")

            markdown += f"| {i} | {rec['title'][:40]}{'...' if len(rec['title']) > 40 else ''} | {rec['category']} | {impact_icon} {impact.title()} | {effort_icon} {effort.title()} | {rec['time']} | {sequence} |\n"

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

        price_diff_pct = 0  # Initialize default
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


class ConversionFunnelSection(ReportSection):
    """Conversion funnel analysis with benchmarks and projections"""

    def analyze(self) -> Dict[str, Any]:
        """Analyze conversion funnel"""
        logger.info("Analyzing conversion funnel")

        from src.conversion_funnel import ConversionFunnelAnalyzer

        game_data = self.data.get('game_data', {})
        sales_data = self.data.get('sales_data', {})
        capsule_analysis = self.data.get('capsule_analysis')

        analyzer = ConversionFunnelAnalyzer()
        self.funnel_data = analyzer.analyze_funnel(game_data, sales_data, capsule_analysis)

        # Score based on overall efficiency
        self.score = self.funnel_data['overall_efficiency']['score']
        self.rating = self.get_rating()
        self.analyzed = True

        return {
            'score': self.score,
            'rating': self.rating
        }

    def generate_markdown(self) -> str:
        """Generate conversion funnel markdown"""
        if not self.analyzed:
            self.analyze()

        funnel = self.funnel_data
        stages = funnel['funnel_stages']
        benchmarks = funnel['genre_benchmarks']
        projections = funnel['projections']
        optimizations = funnel['optimizations']
        efficiency = funnel['overall_efficiency']

        rating_emoji = {'excellent': '✅', 'good': '🟢', 'fair': '🟡', 'poor': '🔴'}
        emoji = rating_emoji.get(self.rating, '⚪')

        vs_emoji = {'above': '✅', 'at': '➡️', 'below': '⚠️'}

        markdown = f"""## Conversion Funnel Analysis

**Overall Efficiency: {efficiency['score']}/100** {emoji} {efficiency['tier']}

Understanding your conversion funnel reveals where you're losing potential customers and where optimization efforts will have the biggest impact.

---

### Your Estimated Conversion Funnel

**Genre**: {funnel['genre'].title()} (benchmarks adjusted for genre performance)

| Stage | Your Rate | Genre Avg | Performance |
|-------|-----------|-----------|-------------|
| **Capsule CTR** (Impression → Visit) | {stages['capsule_ctr']['percentage']}% | {stages['capsule_ctr']['benchmark_percentage']}% | {vs_emoji.get(stages['capsule_ctr']['vs_benchmark'], '➡️')} {stages['capsule_ctr']['vs_benchmark'].upper()} |
| **Wishlist Conv** (Visit → Wishlist) | {stages['wishlist_conversion']['percentage']}% | {stages['wishlist_conversion']['benchmark_percentage']}% | {vs_emoji.get(stages['wishlist_conversion']['vs_benchmark'], '➡️')} {stages['wishlist_conversion']['vs_benchmark'].upper()} |
| **Purchase Conv** (Wishlist → Purchase) | {stages['purchase_conversion']['percentage']}% | {stages['purchase_conversion']['benchmark_percentage']}% | {vs_emoji.get(stages['purchase_conversion']['vs_benchmark'], '➡️')} {stages['purchase_conversion']['vs_benchmark'].upper()} |
| **Review Ratio** (Purchase → Review) | {stages['review_ratio']['percentage']}% | {stages['review_ratio']['benchmark_percentage']}% | {vs_emoji.get(stages['review_ratio']['vs_benchmark'], '➡️')} {stages['review_ratio']['vs_benchmark'].upper()} |

---

### Performance Projections

Here's what your current funnel efficiency projects at different traffic levels:

"""

        # Add projections table
        proj_100k = projections.get('100k_impressions', {})
        proj_250k = projections.get('250k_impressions', {})
        proj_500k = projections.get('500k_impressions', {})

        markdown += f"""| Impressions | Visits | Wishlists | Purchases | Reviews | Revenue |
|-------------|--------|-----------|-----------|---------|---------|
| 100,000 | {proj_100k.get('visits', 0):,} | {proj_100k.get('wishlists', 0):,} | {proj_100k.get('purchases', 0):,} | {proj_100k.get('reviews', 0)} | ${proj_100k.get('revenue', 0):,.0f} |
| 250,000 | {proj_250k.get('visits', 0):,} | {proj_250k.get('wishlists', 0):,} | {proj_250k.get('purchases', 0):,} | {proj_250k.get('reviews', 0)} | ${proj_250k.get('revenue', 0):,.0f} |
| 500,000 | {proj_500k.get('visits', 0):,} | {proj_500k.get('wishlists', 0):,} | {proj_500k.get('purchases', 0):,} | {proj_500k.get('reviews', 0)} | ${proj_500k.get('revenue', 0):,.0f} |

**Example**: With 100,000 impressions, your current funnel efficiency projects:
- **{proj_100k.get('visits', 0):,}** store page visits ({stages['capsule_ctr']['percentage']}% CTR)
- **{proj_100k.get('wishlists', 0):,}** wishlist adds ({stages['wishlist_conversion']['percentage']}% conversion)
- **{proj_100k.get('purchases', 0):,}** purchases ({stages['purchase_conversion']['percentage']}% conversion)
- **${proj_100k.get('revenue', 0):,.0f}** in revenue

---

### Optimization Opportunities

"""

        if optimizations:
            markdown += "Based on your current funnel vs. genre benchmarks, here are the highest-impact optimization opportunities:\n\n"

            for i, opp in enumerate(optimizations, 1):
                priority_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}
                emoji = priority_emoji.get(opp['priority'], '⚪')

                markdown += f"""#### {i}. {opp['stage']} Optimization {emoji} {opp['priority']} PRIORITY

**Current Performance**: {opp['current']}%
**Target (Genre Average)**: {opp['target']}%
**Gap**: +{opp['improvement_points']} percentage points

**Projected Impact** (at 100K impressions):
"""
                impact = opp['impact']
                if 'additional_wishlists' in impact:
                    markdown += f"- **+{impact['additional_wishlists']:,} wishlists**\n"
                if 'additional_purchases' in impact:
                    markdown += f"- **+{impact['additional_purchases']:,} purchases**\n"
                if 'additional_revenue' in impact:
                    markdown += f"- **+${impact['additional_revenue']:,.0f} revenue**\n"

                markdown += f"\n**Recommended Tactics**:\n"
                for tactic in opp.get('tactics', []):
                    markdown += f"- {tactic}\n"

                markdown += "\n"
        else:
            markdown += "✅ **Excellent!** Your funnel is performing at or above genre benchmarks across all stages. Focus on scaling traffic.\n\n"

        markdown += """---

### Stage-Specific Insights

"""

        # Capsule CTR insights
        ctr = stages['capsule_ctr']
        markdown += f"""**1. Capsule CTR ({ctr['percentage']}%)**
- Tier: {ctr['tier'].title()}
- Key factors: Capsule quality ({ctr['factors']['capsule_quality']:.2f}x), Genre fit ({ctr['factors']['genre_fit']:.2f}x), Tag effectiveness ({ctr['factors']['tag_effectiveness']:.2f}x)
"""
        if ctr['vs_benchmark'] == 'below':
            markdown += f"- ⚠️ Below genre average - capsule redesign should be top priority\n"
        elif ctr['vs_benchmark'] == 'above':
            markdown += f"- ✅ Above genre average - capsule is performing well\n"

        # Wishlist conversion insights
        wish = stages['wishlist_conversion']
        markdown += f"""
**2. Wishlist Conversion ({wish['percentage']}%)**
- Tier: {wish['tier'].title()}
- Key factors: Review quality ({wish['factors']['review_quality']:.2f}x), Price positioning ({wish['factors']['price_positioning']:.2f}x), Genre fit ({wish['factors']['genre_fit']:.2f}x)
"""
        if wish['vs_benchmark'] == 'below':
            markdown += f"- ⚠️ Below genre average - improve trailer, screenshots, or store description\n"
        elif wish['vs_benchmark'] == 'above':
            markdown += f"- ✅ Above genre average - store page is converting well\n"

        # Purchase conversion insights
        purch = stages['purchase_conversion']
        markdown += f"""
**3. Purchase Conversion ({purch['percentage']}%)**
- Tier: {purch['tier'].title()}
- Key factors: Review quality ({purch['factors']['review_quality']:.2f}x), Price point ({purch['factors']['price_point']:.2f}x), Genre fit ({purch['factors']['genre_fit']:.2f}x)
"""
        if purch['vs_benchmark'] == 'below':
            markdown += f"- ⚠️ Below genre average - focus on launch quality, pricing, or building hype\n"
        elif purch['vs_benchmark'] == 'above':
            markdown += f"- ✅ Above genre average - strong value proposition and trust signals\n"

        # Review ratio insights
        review = stages['review_ratio']
        markdown += f"""
**4. Review Ratio ({review['percentage']}%)**
- Tier: {review['tier'].title()}
- Key factors: Engagement level ({review['factors']['engagement_level']:.2f}x), Genre fit ({review['factors']['genre_fit']:.2f}x)
"""
        if review['vs_benchmark'] == 'below':
            markdown += f"- ⚠️ Below genre average - consider engagement hooks or review prompts\n"
        elif review['vs_benchmark'] == 'above':
            markdown += f"- ✅ Above genre average - strong player engagement\n"

        markdown += "\n---\n\n"

        return markdown


class VisibilityForecastSection(ReportSection):
    """Steam algorithm visibility forecast and discovery queue predictions"""

    def analyze(self) -> Dict[str, Any]:
        """Analyze visibility forecast"""
        logger.info("Analyzing visibility forecast")

        from src.visibility_forecast import VisibilityForecastAnalyzer

        game_data = self.data.get('game_data', {})
        sales_data = self.data.get('sales_data', {})
        capsule_analysis = self.data.get('capsule_analysis')

        analyzer = VisibilityForecastAnalyzer()
        self.visibility_data = analyzer.analyze_visibility(game_data, sales_data, capsule_analysis)

        # Score based on overall visibility score
        self.score = int(self.visibility_data['overall_score'])
        self.rating = self.get_rating()
        self.analyzed = True

        return {
            'score': self.score,
            'rating': self.rating
        }

    def generate_markdown(self) -> str:
        """Generate visibility forecast markdown"""
        if not self.analyzed:
            self.analyze()

        vis = self.visibility_data
        tier = vis['current_tier']
        score = vis['overall_score']
        components = vis['component_scores']
        discovery = vis['discovery_predictions']
        features = vis['feature_eligibility']
        improvement = vis['improvement_path']

        rating_emoji = {'excellent': '✅', 'good': '🟢', 'fair': '🟡', 'poor': '🔴'}
        emoji = rating_emoji.get(self.rating, '⚪')

        tier_emoji = {1: '👑', 2: '⭐', 3: '📊', 4: '📉'}
        t_emoji = tier_emoji.get(tier, '📊')

        markdown = f"""## Steam Algorithm Visibility Forecast

**Visibility Score: {score}/100** {emoji} {self.rating.title()}
**Current Tier: Tier {tier}** {t_emoji}

{vis['tier_description']}

---

### Component Scores

Your visibility score is calculated from four key factors:

| Component | Score | Weight | Impact |
|-----------|-------|--------|--------|
| **Wishlist Velocity** | {components['wishlist_velocity']}/100 | 40% | {'🔴 Critical' if components['wishlist_velocity'] < 60 else '🟡 Moderate' if components['wishlist_velocity'] < 75 else '🟢 Strong'} |
| **Tag Effectiveness** | {components['tag_effectiveness']}/100 | 25% | {'🔴 Weak' if components['tag_effectiveness'] < 60 else '🟡 Average' if components['tag_effectiveness'] < 75 else '🟢 Good'} |
| **Engagement Level** | {components['engagement']}/100 | 20% | {'🔴 Low' if components['engagement'] < 60 else '🟡 Medium' if components['engagement'] < 75 else '🟢 High'} |
| **Quality Signals** | {components['quality']}/100 | 15% | {'🔴 Poor' if components['quality'] < 60 else '🟡 Fair' if components['quality'] < 75 else '🟢 Excellent'} |

---

### Discovery Queue Predictions

Based on your Tier {tier} status, here's your estimated algorithmic distribution:

**Daily Impression Estimates:**
- Main Discovery Queue: ~{discovery['daily_impressions']['main']:,} impressions/day
- Genre-Specific Queues: ~{discovery['daily_impressions']['genre']:,} impressions/day
"""

        if discovery['daily_impressions']['featured'] > 0:
            markdown += f"- Featured Placements: ~{discovery['daily_impressions']['featured']:,} impressions/day\n"

        markdown += f"""
**Total: ~{discovery['total_daily_impressions']:,} impressions/day**
- Weekly: ~{discovery['weekly_impressions']:,} impressions
- Monthly: ~{discovery['monthly_impressions']:,} impressions

**Queue Types You're Likely Appearing In:**
"""

        for queue_type in discovery['queue_types']:
            markdown += f"- {queue_type}\n"

        markdown += "\n---\n\n### Steam Feature Eligibility\n\n"

        # Popular Upcoming
        pu = features['popular_upcoming']
        pu_status = "✅ ELIGIBLE" if pu['eligible'] else f"❌ NOT ELIGIBLE (need +{pu['gap']:.1f} points)"
        markdown += f"""**Popular Upcoming (Pre-Launch Feature)**
- Status: {pu_status}
- Probability: {pu['probability']:.0f}%
- Requirement: {pu['score_requirement']}+ visibility score
- Your Score: {pu['your_score']}

"""

        # Featured Placement
        feat = features['featured_placement']
        feat_status = "✅ ELIGIBLE" if feat['eligible'] else f"❌ NOT ELIGIBLE"
        if not feat['eligible']:
            reasons = []
            if feat['your_score'] < feat['score_requirement']:
                reasons.append(f"Score gap: +{feat['gap']:.1f} points needed")
            if feat['your_reviews'] < feat['review_requirement']:
                reasons.append(f"Need {feat['review_requirement'] - feat['your_reviews']} more reviews")
            feat_status += f" ({', '.join(reasons)})"

        markdown += f"""**Featured Placement**
- Status: {feat_status}
- Probability: {feat['probability']:.0f}%
- Requirements: {feat['score_requirement']}+ score, {feat['review_requirement']}+ reviews
- Your Metrics: {feat['your_score']} score, {feat['your_reviews']} reviews

"""

        # Daily Deal
        dd = features['daily_deal']
        dd_status = "✅ ELIGIBLE" if dd['eligible'] else "❌ NOT ELIGIBLE"
        markdown += f"""**Daily Deal**
- Status: {dd_status}
- Probability: {dd['probability']:.0f}%
- Requirements: {dd['requirements']['score']}+ score, {dd['requirements']['reviews']}+ reviews, {dd['requirements']['review_score']}%+ rating
- Your Metrics: {dd['your_metrics']['score']} score, {dd['your_metrics']['reviews']} reviews, {dd['your_metrics']['review_score']}% rating

"""

        # New & Trending
        nt = features['new_and_trending']
        nt_status = "✅ ELIGIBLE" if nt['eligible'] else f"❌ NOT ELIGIBLE (need +{max(0, nt['score_requirement'] - nt['your_score']):.1f} points)"
        markdown += f"""**New & Trending**
- Status: {nt_status}
- Probability: {nt['probability']:.0f}%
- Requirements: {nt['score_requirement']}+ score, {nt['review_requirement']}+ reviews
- Your Metrics: {nt['your_score']} score, {nt['your_reviews']} reviews

"""

        markdown += "---\n\n### Path to "

        if improvement['current_tier'] == 1:
            markdown += "Maintaining Elite Status\n\n"
            markdown += f"🎉 **Congratulations!** You're in Tier 1 (Top 1%).\n\n"
            markdown += f"**Focus**: Maintain your {improvement['current_score']}/100 score and scale traffic to this high-performing visibility tier.\n\n"
        else:
            markdown += f"Tier {improvement['next_tier']}\n\n"
            markdown += f"**Target**: {improvement['target_score']} points (you need **+{improvement['points_needed']} points**)\n\n"

            if improvement['points_needed'] > 0:
                markdown += f"**Weakest Areas** (biggest improvement opportunities):\n"
                for area in improvement['weakest_areas'][:3]:
                    area_name = area.replace('_', ' ').title()
                    markdown += f"- {area_name}\n"
                markdown += "\n"

        markdown += "**Prioritized Improvement Recommendations:**\n\n"

        for i, rec in enumerate(improvement['recommendations'], 1):
            priority_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}
            p_emoji = priority_emoji.get(rec['priority'], '⚪')

            markdown += f"""#### {i}. {rec['area']} {p_emoji} {rec['priority']} PRIORITY

**Current Score**: {rec['current_score']:.1f}/100
**Potential Impact**: {rec['impact']}

**Action Items**:
"""
            for action in rec['actions']:
                markdown += f"- {action}\n"

            markdown += "\n"

        # Projected outcome
        proj = improvement['projected_outcome']
        markdown += f"""---

### Projected Impact of Improvements

If you implement the top 2-3 recommendations above:

**Score Improvement**: {improvement['current_score']:.1f} → {proj['score_after_improvements']:.1f} (+{proj['score_after_improvements'] - improvement['current_score']:.1f} points)
**Tier Change**: Tier {improvement['current_tier']} → Tier {proj['tier_after_improvements']}
**Impression Increase**: +{proj['impression_increase_daily']:,} impressions/day (+{proj['impression_increase_monthly']:,}/month)

"""

        if proj['tier_after_improvements'] < improvement['current_tier']:
            markdown += f"🎯 **This would move you from Tier {improvement['current_tier']} to Tier {proj['tier_after_improvements']}** - significantly increasing your algorithmic distribution!\n\n"
        elif proj['score_after_improvements'] > improvement['current_score'] + 5:
            markdown += f"📈 **This would strengthen your position in Tier {improvement['current_tier']}** and move you closer to the next tier!\n\n"

        markdown += "---\n\n"

        return markdown


class GrowthStrategySection(ReportSection):
    """Growth strategy with launch timing, social proof roadmap, and creator hit list"""

    def analyze(self) -> Dict[str, Any]:
        """Analyze growth strategy"""
        logger.info("Analyzing growth strategy")

        from src.growth_strategy import GrowthStrategyAnalyzer

        game_data = self.data.get('game_data', {})
        sales_data = self.data.get('sales_data', {})
        target_launch_date = self.data.get('target_launch_date')

        analyzer = GrowthStrategyAnalyzer()
        self.growth_data = analyzer.analyze_growth_strategy(game_data, sales_data, target_launch_date)

        # Score based on actionability (always high value)
        self.score = 85
        self.rating = self.get_rating()
        self.analyzed = True

        return {
            'score': self.score,
            'rating': self.rating
        }

    def generate_markdown(self) -> str:
        """Generate growth strategy markdown"""
        if not self.analyzed:
            self.analyze()

        growth = self.growth_data
        is_pre_launch = growth['is_pre_launch']

        markdown = f"""## Growth Strategy & Traffic Tactics

"""

        if is_pre_launch and growth['launch_timing']:
            timing = growth['launch_timing']
            markdown += f"""### Launch Timing Intelligence

**Optimal Launch Windows:**

"""
            for i, window in enumerate(timing['optimal_windows'][:3], 1):
                rating_emoji = {'OPTIMAL': '🎯', 'GOOD': '✅', 'ACCEPTABLE': '🟡'}.get(window['rating'], '⚪')
                markdown += f"""**{i}. {window['window']}** {rating_emoji} {window['rating']}
- Dates: {window['dates']}
- Competition: {window['competition']}
- Reason: {window['reason']}

"""

            markdown += f"""**Windows to Avoid:**

"""
            for avoid in timing['avoid_windows']:
                markdown += f"""**{avoid['window']}** ❌ {avoid['rating']}
- Reason: {avoid['reason']}

"""

            markdown += f"""**Upcoming Steam Events:**

"""
            for event in timing['upcoming_steam_events']:
                markdown += f"""- **{event['name']}**: {event['dates']} ({event['type'].title()}, {event['traffic_multiplier']}x traffic)
"""

            markdown += f"""
**Recommended Strategy:** {timing['recommendation']['window']}
- {timing['recommendation']['reason']}

---

"""

        # Social Proof Roadmap
        social = growth['social_proof_roadmap']
        markdown += f"""### Social Proof Roadmap

**Current Status:**
- Steam Followers: {social['current']['steam_followers']:,}
- Discord Members: {social['current']['discord_members']:,}
- Reddit Subscribers: {social['current']['reddit_subscribers']:,}

"""

        if is_pre_launch:
            markdown += f"""**Tier 2 Visibility Targets** (90 days to launch):
- Steam Followers: {social['tier_2_targets']['steam_followers']:,} (need +{social['gaps']['steam_followers']:,})
- Discord Members: {social['tier_2_targets']['discord_members']:,} (need +{social['gaps']['discord_members']:,})
- Reddit Subscribers: {social['tier_2_targets']['reddit_subscribers']:,} (need +{social['gaps']['reddit_subscribers']:,})

**Daily Growth Needed:**
- Steam: +{social['daily_growth_needed']['steam_followers']:.1f} followers/day
- Discord: +{social['daily_growth_needed']['discord_members']:.1f} members/day
- Reddit: +{social['daily_growth_needed']['reddit_subscribers']:.1f} subscribers/day

**Milestones:**

"""
            for milestone in social['milestones']:
                markdown += f"""**Day {milestone['day']}:**
- Target Followers: {milestone['target_followers']:,}
- Target Discord: {milestone['target_discord']:,}
- Tactics: {', '.join(milestone['tactics'])}

"""
        else:
            markdown += f"""**Growth Targets** (Post-Launch):

"""
            for milestone in social['milestones']:
                markdown += f"""**Month {milestone['month']}:**
- Target Followers: {milestone['target_followers']:,}
- Target Discord: {milestone['target_discord']:,}
- Tactics: {', '.join(milestone['tactics'])}

"""

        markdown += "---\n\n### Creator & Influencer Hit List\n\n"

        creators = growth['creator_hit_list']
        budget = creators['budget_recommendation']

        markdown += f"""**Outreach Budget Recommendation:**
- Free Keys: {budget['free_keys']} creators
- Sponsored Coverage: {budget['sponsored_coverage']} creators
- Estimated Cost: {budget['estimated_cost']}
- Estimated Total Wishlists: {budget['estimated_total_wishlists']:,}
- Estimated Revenue Impact: ${budget['estimated_revenue_impact']:,}

**Outreach Timeline:**
"""
        for phase, desc in creators['outreach_timeline'].items():
            phase_name = phase.replace('_', ' ').title()
            markdown += f"- **{phase_name}**: {desc}\n"

        markdown += "\n**Tier 1 Priority Creators** (Highest Impact):\n\n"

        for i, creator in enumerate(creators['tier_1_priority'], 1):
            markdown += f"""**{i}. {creator['name']}** ({creator['subscribers']:,} subscribers)
- Average Views: {creator['avg_views']:,}
- Coverage Rate: {creator['coverage_rate']}%
- Estimated Wishlists: {creator['estimated_wishlists']}
- Offer: {creator['offer_type']} ({creator['cost_range']})
- Genre Fit: {creator['genre_fit'].title()}
- Revenue Impact: ${creator['estimated_revenue_impact']:,}

"""

        if creators['tier_2_priority']:
            markdown += f"\n**Tier 2 Priority Creators** (Medium Impact, {len(creators['tier_2_priority'])} total):\n\n"
            for i, creator in enumerate(creators['tier_2_priority'][:5], 1):
                markdown += f"{i}. **{creator['name']}** ({creator['subscribers']:,} subs) - {creator['estimated_wishlists']} wishlists\n"

        markdown += "\n---\n\n### Community Building Tactics\n\n"

        for i, tactic in enumerate(growth['community_tactics'], 1):
            markdown += f"""**{i}. {tactic['tactic']}**
- **Timeline**: {tactic['timeline']}
- **Expected Impact**: {tactic['expected_impact']}
- **Effort**: {tactic['effort']}

**Action Items:**
"""
            for action in tactic['actions']:
                markdown += f"- {action}\n"

            markdown += "\n"

        markdown += "---\n\n"

        return markdown


class TagInsightsSection(ReportSection):
    """Tag effectiveness with impression estimates"""

    def __init__(self, section_name: str, data: Dict[str, Any]):
        super().__init__(section_name, data)
        self.tag_analysis = None

    def analyze(self) -> Dict[str, Any]:
        """Analyze tags with impression estimates"""
        from src.tag_insights import TagInsightsAnalyzer

        game_data = self.data.get('game_data', {})
        sales_data = self.data.get('sales_data', {})

        analyzer = TagInsightsAnalyzer()
        self.tag_analysis = analyzer.analyze_tags(game_data, sales_data)

        # Score based on optimization potential
        self.score = self.tag_analysis.get('optimization_score', 50)

        if self.score >= 80:
            self.rating = 'excellent'
        elif self.score >= 65:
            self.rating = 'good'
        elif self.score >= 50:
            self.rating = 'fair'
        else:
            self.rating = 'poor'

        self.analyzed = True

        return {
            'score': self.score,
            'rating': self.rating,
            'tag_analysis': self.tag_analysis
        }

    def generate_markdown(self) -> str:
        """Generate markdown for tag insights"""
        if not self.analyzed:
            self.analyze()

        markdown = f"## {self.section_name}\n\n"
        markdown += f"**Tag Optimization Score:** {self.score}/100 ({self.rating.upper()})\n\n"

        # Current tags analysis
        markdown += "### Current Tags Performance\n\n"
        markdown += f"**Total Tags:** {self.tag_analysis['tag_count']}/20 (Steam allows up to 20 tags)\n\n"

        current_analysis = self.tag_analysis.get('current_analysis', [])
        if current_analysis:
            markdown += "| Tag | Tier | Traffic/Day | Your Impressions/Day | Status |\n"
            markdown += "|-----|------|-------------|---------------------|--------|\n"

            for tag_data in current_analysis[:15]:  # Top 15 tags
                tag = tag_data.get('tag', '')
                tier = tag_data.get('tier', 'unknown').upper()
                total_traffic = tag_data.get('total_daily_traffic', 0)
                your_impressions = tag_data.get('your_daily_impressions', 0)
                status = tag_data.get('status', 'unknown')

                status_emoji = {
                    'optimal': '🟢 Optimal',
                    'good': '🟡 Good',
                    'too_broad': '🔴 Too Broad',
                    'unknown': '⚪ Unknown'
                }.get(status, status)

                markdown += f"| {tag} | {tier} | {total_traffic:,} | {your_impressions:,} | {status_emoji} |\n"

            markdown += "\n"

        # Current impression totals
        impression_impact = self.tag_analysis.get('impression_impact', {})
        current_daily = impression_impact.get('current_daily_impressions', 0)
        current_monthly = impression_impact.get('current_monthly_impressions', 0)

        markdown += f"**Current Tag Impressions:**\n"
        markdown += f"- Daily: {current_daily:,} impressions\n"
        markdown += f"- Monthly: {current_monthly:,} impressions\n\n"

        # Suggested tag additions
        suggested_additions = self.tag_analysis.get('suggested_additions', [])
        if suggested_additions:
            markdown += "### Recommended Tags to Add\n\n"
            markdown += "| Tag | Priority | Tier | Reason | +Impressions/Day | +Impressions/Month |\n"
            markdown += "|-----|----------|------|--------|------------------|--------------------|\n"

            for suggestion in suggested_additions:
                tag = suggestion.get('tag', '')
                priority = suggestion.get('priority', 'MEDIUM')
                tier = suggestion.get('tier', 'unknown').upper()
                reason = suggestion.get('reason', '')
                daily = suggestion.get('estimated_additional_impressions_daily', 0)
                monthly = suggestion.get('estimated_additional_impressions_monthly', 0)

                priority_emoji = '🔴 HIGH' if priority == 'HIGH' else '🟡 MEDIUM'

                markdown += f"| {tag} | {priority_emoji} | {tier} | {reason} | +{daily:,} | +{monthly:,} |\n"

            markdown += "\n"

        # Suggested tag removals
        suggested_removals = self.tag_analysis.get('suggested_removals', [])
        if suggested_removals:
            markdown += "### Tags to Remove/Replace\n\n"
            markdown += "| Tag | Reason | Replacement Suggestion |\n"
            markdown += "|-----|--------|------------------------|\n"

            for removal in suggested_removals:
                tag = removal.get('tag', '')
                reason = removal.get('reason', '')
                replacement = removal.get('replacement_suggestion', '')

                markdown += f"| {tag} | {reason} | {replacement} |\n"

            markdown += "\n"

        # Impression impact summary
        if impression_impact:
            net_daily = impression_impact.get('net_daily_change', 0)
            net_monthly = impression_impact.get('net_monthly_change', 0)
            optimized_daily = impression_impact.get('optimized_daily_impressions', 0)
            optimized_monthly = impression_impact.get('optimized_monthly_impressions', 0)
            percent_improvement = impression_impact.get('percent_improvement', 0)

            markdown += "### Optimization Impact\n\n"
            markdown += f"**If you implement all tag recommendations:**\n\n"
            markdown += f"- **Current Daily Impressions:** {current_daily:,}\n"
            markdown += f"- **Optimized Daily Impressions:** {optimized_daily:,}\n"
            markdown += f"- **Net Change:** {'+' if net_daily >= 0 else ''}{net_daily:,}/day ({'+' if percent_improvement >= 0 else ''}{percent_improvement:.1f}%)\n\n"
            markdown += f"- **Current Monthly Impressions:** {current_monthly:,}\n"
            markdown += f"- **Optimized Monthly Impressions:** {optimized_monthly:,}\n"
            markdown += f"- **Net Change:** {'+' if net_monthly >= 0 else ''}{net_monthly:,}/month\n\n"

        # Key insights
        markdown += "### Tag Strategy Insights\n\n"

        if self.score >= 80:
            markdown += "✅ **Excellent tag optimization!** Your tags are well-chosen with strong specificity and traffic potential.\n\n"
        elif self.score >= 65:
            markdown += "✅ **Good tag optimization.** You have a solid tag foundation with room for minor improvements.\n\n"
        elif self.score >= 50:
            markdown += "⚠️ **Fair tag optimization.** Your tags are functional but missing some high-value opportunities.\n\n"
        else:
            markdown += "❌ **Poor tag optimization.** Significant improvements needed to maximize discovery potential.\n\n"

        markdown += "**Tag Selection Best Practices:**\n"
        markdown += "1. **Use 15-20 tags** - Steam allows up to 20, use them all\n"
        markdown += "2. **Balance broad and specific** - Mix high-traffic genre tags with niche mechanic tags\n"
        markdown += "3. **Prioritize high-specificity tags** - Detective > Adventure, Roguelike > Action\n"
        markdown += "4. **Include player count** - Singleplayer or Multiplayer (essential filter tag)\n"
        markdown += "5. **Add art style tag** - Pixel Art, 3D, Hand-Drawn, etc. (common search filter)\n"
        markdown += "6. **Remove unknown tags** - Misspelled or non-standard tags get zero traffic\n\n"

        return markdown


class ReviewVulnerabilitySection(ReportSection):
    """Review vulnerability and risk assessment"""

    def __init__(self, section_name: str, data: Dict[str, Any]):
        super().__init__(section_name, data)
        self.vulnerability_analysis = None

    def analyze(self) -> Dict[str, Any]:
        """Analyze review vulnerabilities"""
        from src.review_vulnerability import ReviewVulnerabilityAnalyzer

        game_data = self.data.get('game_data', {})
        sales_data = self.data.get('sales_data', {})
        competitor_data = self.data.get('competitor_data', [])

        analyzer = ReviewVulnerabilityAnalyzer()
        self.vulnerability_analysis = analyzer.analyze_vulnerabilities(
            game_data, sales_data, competitor_data
        )

        # Score based on risk (inverted: lower risk = higher score)
        risk_score = self.vulnerability_analysis.get('risk_score', 50)
        self.score = 100 - risk_score  # Invert so high score = low risk

        if self.score >= 75:
            self.rating = 'excellent'  # Minimal risk
        elif self.score >= 55:
            self.rating = 'good'  # Low risk
        elif self.score >= 35:
            self.rating = 'fair'  # Medium risk
        else:
            self.rating = 'poor'  # High risk

        self.analyzed = True

        return {
            'score': self.score,
            'rating': self.rating,
            'vulnerability_analysis': self.vulnerability_analysis
        }

    def generate_markdown(self) -> str:
        """Generate markdown for review vulnerability analysis"""
        if not self.analyzed:
            self.analyze()

        markdown = f"## {self.section_name}\n\n"

        risk_score = self.vulnerability_analysis.get('risk_score', 0)
        risk_tier = self.vulnerability_analysis.get('risk_tier', 'Unknown')

        # Risk overview
        markdown += f"**Risk Assessment Score:** {self.score}/100 ({risk_tier.upper()})\n\n"

        risk_emoji = {
            'Minimal Risk': '🟢',
            'Low Risk': '🟡',
            'Medium Risk': '🟠',
            'High Risk': '🔴'
        }.get(risk_tier, '⚪')

        markdown += f"{risk_emoji} **Status:** {risk_tier}\n"
        markdown += f"- **Your Risk Score:** {risk_score}/100 (lower is better)\n"
        markdown += f"- **Safety Score:** {self.score}/100 (higher is better)\n\n"

        # Predicted risks
        predicted_risks = self.vulnerability_analysis.get('predicted_risks', [])
        if predicted_risks:
            markdown += "### Top Predicted Vulnerabilities\n\n"
            markdown += "*Based on genre, pricing, and competitor negative review analysis*\n\n"
            markdown += "| Risk | Severity | Probability | Key Factors |\n"
            markdown += "|------|----------|-------------|-------------|\n"

            for risk in predicted_risks[:8]:  # Top 8 risks
                description = risk.get('description', '')
                severity = risk.get('severity', 'UNKNOWN')
                priority = risk.get('priority', 'UNKNOWN')
                probability = risk.get('probability', 0)
                risk_factors = risk.get('risk_factors', [])

                severity_emoji = {
                    'CRITICAL': '🔴 CRITICAL',
                    'HIGH': '🟠 HIGH',
                    'MEDIUM': '🟡 MEDIUM',
                    'LOW': '🟢 LOW'
                }.get(priority, priority)

                factors_text = risk_factors[0] if risk_factors else 'N/A'
                if len(risk_factors) > 1:
                    factors_text += f" (+{len(risk_factors)-1} more)"

                markdown += f"| {description} | {severity_emoji} | {probability:.0f}% | {factors_text} |\n"

            markdown += "\n"

        # Competitor review themes
        competitor_themes = self.vulnerability_analysis.get('competitor_themes', {})
        common_themes = competitor_themes.get('common_themes', {})

        if common_themes:
            markdown += "### Competitor Negative Review Themes\n\n"
            total_analyzed = competitor_themes.get('total_negative_reviews_analyzed', 0)
            markdown += f"*Analyzed {total_analyzed} competitors with negative reviews*\n\n"

            markdown += "| Theme | Prevalence | Severity | Description |\n"
            markdown += "|-------|------------|----------|-------------|\n"

            for theme_name, theme_data in sorted(common_themes.items(), key=lambda x: x[1]['percentage'], reverse=True):
                percentage = theme_data.get('percentage', 0)
                severity = theme_data.get('severity', 'UNKNOWN')
                description = theme_data.get('description', '')

                severity_emoji = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🟢'
                }.get(severity, '⚪')

                markdown += f"| {theme_name.replace('_', ' ').title()} | {percentage:.0f}% | {severity_emoji} {severity} | {description} |\n"

            markdown += "\n"

        # Mitigation strategies
        mitigation_strategies = self.vulnerability_analysis.get('mitigation_strategies', [])
        if mitigation_strategies:
            markdown += "### Risk Mitigation Strategies\n\n"
            markdown += "*Specific tactics to prevent these issues in your game*\n\n"

            for i, strategy in enumerate(mitigation_strategies[:5], 1):  # Top 5
                risk_desc = strategy.get('risk', '')
                priority = strategy.get('priority', 'UNKNOWN')
                probability = strategy.get('probability', 0)
                tactics = strategy.get('tactics', [])

                priority_emoji = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🟢'
                }.get(priority, '⚪')

                markdown += f"#### {i}. {risk_desc} {priority_emoji}\n"
                markdown += f"*{priority} priority | {probability:.0f}% probability*\n\n"

                markdown += "**Recommended Tactics:**\n"
                for tactic in tactics:
                    markdown += f"- {tactic}\n"
                markdown += "\n"

        # Early warning signs
        early_warnings = self.vulnerability_analysis.get('early_warning_signs', [])
        if early_warnings:
            markdown += "### Early Warning Signs to Monitor\n\n"
            markdown += "*Watch for these red flags in your first reviews:*\n\n"

            for warning in early_warnings:
                markdown += f"- {warning}\n"
            markdown += "\n"

            markdown += "**Action Plan:**\n"
            markdown += "1. **First 24 hours:** Read ALL reviews, respond to critical bugs immediately\n"
            markdown += "2. **First week:** Track review themes, prioritize fixes for most-mentioned issues\n"
            markdown += "3. **First month:** Analyze negative review patterns, plan content updates\n"
            markdown += "4. **Ongoing:** Maintain <72h response time to critical issues\n\n"

        # Key insights
        markdown += "### Risk Assessment Insights\n\n"

        if self.score >= 75:
            markdown += "✅ **Minimal Risk** - Your game has low vulnerability to common negative review themes. Maintain quality standards.\n\n"
        elif self.score >= 55:
            markdown += "✅ **Low Risk** - Your game has manageable risk exposure. Focus on the high-priority mitigations above.\n\n"
        elif self.score >= 35:
            markdown += "⚠️ **Medium Risk** - Several vulnerabilities detected. Implement mitigation strategies before launch.\n\n"
        else:
            markdown += "❌ **High Risk** - Critical vulnerabilities detected. Delay launch if needed to address CRITICAL priority issues.\n\n"

        markdown += "**Best Practices for Risk Prevention:**\n"
        markdown += "1. **Beta Test Extensively** - 50+ testers before launch, focus on bug hunting\n"
        markdown += "2. **Set Expectations Clearly** - Communicate playtime, content, features on store page\n"
        markdown += "3. **Price Competitively** - Research competitor pricing, consider launch discount\n"
        markdown += "4. **Monitor Reviews Daily** - First month is critical for reputation\n"
        markdown += "5. **Respond Quickly** - Patch critical bugs within 48h of discovery\n"
        markdown += "6. **Be Transparent** - Communicate roadmap, updates, and fixes publicly\n\n"

        return markdown


class CustomDashboardSection(ReportSection):
    """Custom tracking dashboard and tools"""

    def __init__(self, section_name: str, data: Dict[str, Any]):
        super().__init__(section_name, data)
        self.dashboard_data = None

    def analyze(self) -> Dict[str, Any]:
        """Generate custom dashboard"""
        from src.dashboard_generator import DashboardGenerator

        game_data = self.data.get('game_data', {})
        sales_data = self.data.get('sales_data', {})
        competitor_data = self.data.get('competitor_data', [])

        generator = DashboardGenerator()
        self.dashboard_data = generator.generate_dashboard(
            game_data, sales_data, competitor_data
        )

        # Dashboard always scores 100 (it's a tool, not evaluated)
        self.score = 100
        self.rating = 'excellent'
        self.analyzed = True

        return {
            'score': self.score,
            'rating': self.rating,
            'dashboard_data': self.dashboard_data
        }

    def generate_markdown(self) -> str:
        """Generate markdown for custom dashboard"""
        if not self.analyzed:
            self.analyze()

        markdown = f"## {self.section_name}\n\n"
        markdown += "**Copy these tracking templates to Google Sheets or Excel for daily monitoring.**\n\n"

        # Instructions
        instructions = self.dashboard_data.get('instructions', '')
        if instructions:
            markdown += instructions
            markdown += "\n---\n\n"

        # KPI Tracker
        kpi_tracker = self.dashboard_data.get('kpi_tracker', '')
        if kpi_tracker:
            markdown += kpi_tracker
            markdown += "\n---\n\n"

        # Conversion Calculator
        conversion_calc = self.dashboard_data.get('conversion_calculator', '')
        if conversion_calc:
            markdown += conversion_calc
            markdown += "\n---\n\n"

        # Launch Timeline
        launch_timeline = self.dashboard_data.get('launch_timeline', '')
        if launch_timeline:
            markdown += launch_timeline
            markdown += "\n---\n\n"

        # Competitor Tracker
        competitor_tracker = self.dashboard_data.get('competitor_tracker', '')
        if competitor_tracker:
            markdown += competitor_tracker
            markdown += "\n---\n\n"

        # Marketing Tracker
        marketing_tracker = self.dashboard_data.get('marketing_tracker', '')
        if marketing_tracker:
            markdown += marketing_tracker
            markdown += "\n"

        return markdown


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

        # Create conversion funnel section SECOND (hard data for projections)
        funnel_section = ConversionFunnelSection("Conversion Funnel", {
            'game_data': self.game_data,
            'sales_data': self.sales_data,
            'capsule_analysis': getattr(self, 'capsule_analysis', None)
        })
        self.add_section(funnel_section)

        # Create visibility forecast section THIRD (algorithm predictions)
        visibility_section = VisibilityForecastSection("Visibility Forecast", {
            'game_data': self.game_data,
            'sales_data': self.sales_data,
            'capsule_analysis': getattr(self, 'capsule_analysis', None)
        })
        self.add_section(visibility_section)

        # Create growth strategy section FOURTH (launch timing, creators, tactics)
        growth_section = GrowthStrategySection("Growth Strategy", {
            'game_data': self.game_data,
            'sales_data': self.sales_data,
            'target_launch_date': None  # Can be passed from app if known
        })
        self.add_section(growth_section)

        # Create tag insights section FIFTH (tag effectiveness with impression estimates)
        tag_section = TagInsightsSection("Tag Insights", {
            'game_data': self.game_data,
            'sales_data': self.sales_data
        })
        self.add_section(tag_section)

        # Create review vulnerability section SIXTH (risk assessment from competitor reviews)
        vulnerability_section = ReviewVulnerabilitySection("Review Vulnerability & Risk Assessment", {
            'game_data': self.game_data,
            'sales_data': self.sales_data,
            'competitor_data': self.competitor_data
        })
        self.add_section(vulnerability_section)

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

        # Create custom dashboard section LAST (tracking tools)
        dashboard_section = CustomDashboardSection("Custom Tracking Dashboard", {
            'game_data': self.game_data,
            'sales_data': self.sales_data,
            'competitor_data': self.competitor_data
        })
        self.add_section(dashboard_section)

        # Create executive summary (references other sections)
        self.executive_summary = ExecutiveSummarySection({
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
