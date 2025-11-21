#!/usr/bin/env python3
"""
Visualizations - Markdown-based Charts and Tables
Provides visual comparison tools for reports
"""

from typing import Dict, List, Any, Optional
from src.logger import get_logger

logger = get_logger(__name__)


class ReportVisualizer:
    """Generate markdown tables and visualizations for reports"""

    def __init__(self):
        logger.debug("ReportVisualizer initialized")

    def create_comparison_table(self, your_game: Dict[str, Any],
                                competitors: List[Dict[str, Any]],
                                metrics: List[str] = None) -> str:
        """
        Create comparison table showing your game vs competitors

        Args:
            your_game: Your game data
            competitors: List of competitor data
            metrics: List of metrics to compare (default: price, reviews, etc)

        Returns:
            Markdown table
        """
        logger.debug(f"Creating comparison table for {len(competitors)} competitors")

        if not metrics:
            metrics = ['name', 'price', 'release_date', 'positive_reviews', 'tags_count']

        # Calculate competitor averages
        comp_prices = [c.get('price_overview', {}).get('final', 0) / 100
                      for c in competitors if c.get('price_overview')]
        comp_review_counts = [c.get('review_count', 0) for c in competitors]

        avg_price = sum(comp_prices) / len(comp_prices) if comp_prices else 0
        avg_reviews = sum(comp_review_counts) / len(comp_review_counts) if comp_review_counts else 0

        # Build table
        markdown = "### Competitive Comparison\n\n"
        markdown += "| Metric | Your Game | Competitor Avg | Status |\n"
        markdown += "|--------|-----------|----------------|--------|\n"

        # Price comparison
        your_price = your_game.get('price_overview', {}).get('final', 0) / 100 if your_game.get('price_overview') else 0
        price_status = "✅" if abs(your_price - avg_price) / avg_price < 0.15 else "⚠️"
        markdown += f"| Price | ${your_price:.2f} | ${avg_price:.2f} | {price_status} |\n"

        # Review count comparison
        your_reviews = your_game.get('review_count', 0)
        review_status = "✅" if your_reviews >= avg_reviews * 0.8 else "⚠️"
        markdown += f"| Reviews | {your_reviews:,} | {int(avg_reviews):,} | {review_status} |\n"

        # Screenshot count
        your_screenshots = len(your_game.get('screenshots', []))
        comp_screenshots = [len(c.get('screenshots', [])) for c in competitors]
        avg_screenshots = sum(comp_screenshots) / len(comp_screenshots) if comp_screenshots else 0
        screenshot_status = "✅" if your_screenshots >= avg_screenshots * 0.9 else "⚠️"
        markdown += f"| Screenshots | {your_screenshots} | {avg_screenshots:.1f} | {screenshot_status} |\n"

        # Video count
        your_videos = len(your_game.get('movies', []))
        comp_videos = [len(c.get('movies', [])) for c in competitors]
        avg_videos = sum(comp_videos) / len(comp_videos) if comp_videos else 0
        video_status = "✅" if your_videos >= avg_videos * 0.8 else "⚠️"
        markdown += f"| Videos | {your_videos} | {avg_videos:.1f} | {video_status} |\n"

        markdown += "\n**Status**: ✅ = Competitive, ⚠️ = Below Average\n\n"

        return markdown

    def create_score_card(self, section_name: str, score: int,
                         rating: str, details: Dict[str, Any] = None) -> str:
        """
        Create visual score card

        Args:
            section_name: Name of section
            score: Score (0-100)
            rating: Rating label
            details: Optional additional details

        Returns:
            Formatted markdown score card
        """
        rating_emoji = {
            'excellent': '✅',
            'good': '🟢',
            'fair': '🟡',
            'poor': '🔴'
        }

        emoji = rating_emoji.get(rating, '⚪')

        # Create progress bar
        progress_bar = self._create_progress_bar(score)

        markdown = f"""
#### {section_name}

**Score: {score}/100** {emoji} {rating.title()}

{progress_bar}

"""

        if details:
            for key, value in details.items():
                markdown += f"- **{key}**: {value}\n"

        return markdown

    def create_priority_matrix(self, recommendations: List[Dict[str, Any]]) -> str:
        """
        Create 2x2 priority matrix visualization

        Args:
            recommendations: List of recommendations with priority and impact

        Returns:
            ASCII priority matrix
        """
        logger.debug(f"Creating priority matrix for {len(recommendations)} recommendations")

        # Categorize recommendations
        high_priority_high_impact = []
        high_priority_low_impact = []
        low_priority_high_impact = []
        low_priority_low_impact = []

        for rec in recommendations:
            priority = rec.get('priority', 'medium')
            impact = rec.get('impact', 'medium')

            if hasattr(rec, 'priority'):
                priority = rec.priority.value if hasattr(rec.priority, 'value') else rec.priority
            if hasattr(rec, 'impact'):
                impact = rec.impact.value if hasattr(rec.impact, 'value') else rec.impact

            is_high_priority = priority in ['critical', 'high']
            is_high_impact = impact == 'high'

            if is_high_priority and is_high_impact:
                high_priority_high_impact.append(rec)
            elif is_high_priority and not is_high_impact:
                high_priority_low_impact.append(rec)
            elif not is_high_priority and is_high_impact:
                low_priority_high_impact.append(rec)
            else:
                low_priority_low_impact.append(rec)

        markdown = """
### Priority Matrix

```
High Impact ↑
│
│  🔴 CRITICAL              │  🟡 STRATEGIC
│  (Do First)               │  (Plan & Schedule)
│  ─────────────────────────┼─────────────────────
"""

        # Add critical items
        for rec in high_priority_high_impact[:3]:
            title = rec.title if hasattr(rec, 'title') else rec.get('title', 'Action')
            markdown += f"│  • {title[:25]:<25} │\n"

        markdown += """│  ─────────────────────────┼─────────────────────
│  🟢 QUICK WINS            │  ⚪ LOW PRIORITY
│  (Easy improvements)      │  (If time permits)
"""

        # Add quick wins
        for rec in low_priority_high_impact[:2]:
            title = rec.title if hasattr(rec, 'title') else rec.get('title', 'Action')
            markdown += f"│  • {title[:25]:<25} │\n"

        markdown += """│
└────────────────────────────────────────> High Effort
```

"""

        return markdown

    def create_funnel_analysis(self, metrics: Dict[str, Any]) -> str:
        """
        Create conversion funnel visualization

        Args:
            metrics: Dict with impressions, visits, wishlists, sales

        Returns:
            Funnel visualization
        """
        impressions = metrics.get('impressions', 100000)
        page_visits = metrics.get('page_visits', 2500)
        wishlists = metrics.get('wishlists', 2500)
        estimated_sales = metrics.get('estimated_sales', 500)

        # Calculate conversion rates
        ctr = (page_visits / impressions * 100) if impressions > 0 else 0
        wishlist_rate = (wishlists / page_visits * 100) if page_visits > 0 else 0
        conversion_rate = (estimated_sales / wishlists * 100) if wishlists > 0 else 0

        # Benchmarks
        avg_ctr = 2.5
        avg_wishlist_rate = 25
        avg_conversion = 20

        markdown = """
### Conversion Funnel

```
┌─────────────────────────────────────────────┐
│  👁  {impressions:,} Impressions
└─────────────────────────────────────────────┘
            ↓ {ctr:.1f}% CTR {ctr_status}
┌─────────────────────────────────────────────┐
│  🖱  {page_visits:,} Page Visits
└─────────────────────────────────────────────┘
            ↓ {wishlist_rate:.1f}% Wishlist {wishlist_status}
┌─────────────────────────────────────────────┐
│  ❤️  {wishlists:,} Wishlists
└─────────────────────────────────────────────┘
            ↓ {conversion_rate:.1f}% Purchase {conversion_status}
┌─────────────────────────────────────────────┐
│  💰 {estimated_sales:,} Sales (Est.)
└─────────────────────────────────────────────┘
```

**Benchmarks:**
- CTR: {ctr:.1f}% (Genre avg: {avg_ctr}%) {ctr_status}
- Wishlist Rate: {wishlist_rate:.1f}% (Genre avg: {avg_wishlist_rate}%) {wishlist_status}
- Conversion: {conversion_rate:.1f}% (Genre avg: {avg_conversion}%) {conversion_status}

""".format(
            impressions=impressions,
            page_visits=page_visits,
            wishlists=wishlists,
            estimated_sales=estimated_sales,
            ctr=ctr,
            wishlist_rate=wishlist_rate,
            conversion_rate=conversion_rate,
            avg_ctr=avg_ctr,
            avg_wishlist_rate=avg_wishlist_rate,
            avg_conversion=avg_conversion,
            ctr_status="✅" if ctr >= avg_ctr * 0.9 else "⚠️",
            wishlist_status="✅" if wishlist_rate >= avg_wishlist_rate * 0.9 else "⚠️",
            conversion_status="✅" if conversion_rate >= avg_conversion * 0.9 else "⚠️"
        )

        return markdown

    def create_competitor_highlights(self, competitors: List[Dict[str, Any]],
                                    top_n: int = 5) -> str:
        """
        Create highlighted competitor summary

        Args:
            competitors: List of competitor data
            top_n: Number of top competitors to highlight

        Returns:
            Markdown summary
        """
        if not competitors:
            return "No competitor data available.\n\n"

        markdown = "### Top Competitors\n\n"

        for i, comp in enumerate(competitors[:top_n], 1):
            name = comp.get('name', 'Unknown')
            price = comp.get('price_overview', {}).get('final', 0) / 100 if comp.get('price_overview') else 0
            positive = comp.get('positive_percentage', 0)
            release_date = comp.get('release_date', {}).get('date', 'Unknown')

            markdown += f"{i}. **{name}**\n"
            markdown += f"   - Price: ${price:.2f}\n"
            markdown += f"   - Reviews: {positive}% positive\n"
            markdown += f"   - Released: {release_date}\n\n"

        return markdown

    def _create_progress_bar(self, score: int, width: int = 30) -> str:
        """
        Create ASCII progress bar

        Args:
            score: Score (0-100)
            width: Width of bar in characters

        Returns:
            Progress bar string
        """
        filled = int((score / 100) * width)
        empty = width - filled

        bar = '█' * filled + '░' * empty

        return f"`{bar}` {score}%"

    def create_section_breakdown_chart(self, sections: Dict[str, Dict[str, Any]]) -> str:
        """
        Create visual breakdown of section scores

        Args:
            sections: Dict of section names to score data

        Returns:
            Visual chart
        """
        markdown = "### Section Breakdown\n\n"

        rating_emoji = {
            'excellent': '✅',
            'good': '🟢',
            'fair': '🟡',
            'poor': '🔴'
        }

        for section_name, section_data in sections.items():
            score = section_data.get('score', 0)
            rating = section_data.get('rating', 'unknown')
            emoji = rating_emoji.get(rating, '⚪')

            progress = self._create_progress_bar(score)

            markdown += f"**{section_name}** {emoji}\n"
            markdown += f"{progress}\n\n"

        return markdown


# Convenience functions
def create_comparison_table(your_game: Dict[str, Any],
                           competitors: List[Dict[str, Any]]) -> str:
    """Quick function to create comparison table"""
    viz = ReportVisualizer()
    return viz.create_comparison_table(your_game, competitors)


def create_funnel_analysis(metrics: Dict[str, Any]) -> str:
    """Quick function to create funnel analysis"""
    viz = ReportVisualizer()
    return viz.create_funnel_analysis(metrics)


def create_priority_matrix(recommendations: List[Dict[str, Any]]) -> str:
    """Quick function to create priority matrix"""
    viz = ReportVisualizer()
    return viz.create_priority_matrix(recommendations)
