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
        self.roi_projection = {}

    def analyze(self) -> Dict[str, Any]:
        """Analyze all sections and create executive summary"""
        logger.info("Generating executive summary")

        # Calculate overall score from all sections
        if self.all_sections:
            section_scores = [s.get_score() for s in self.all_sections if hasattr(s, 'get_score')]
            self.overall_score = int(sum(section_scores) / len(section_scores)) if section_scores else 0
        else:
            self.overall_score = 0

        self.score = self.overall_score
        self.rating = self.get_rating()
        self.analyzed = True

        return {
            'score': self.score,
            'rating': self.rating,
            'overall_score': self.overall_score,
            'priority_actions': self.priority_actions
        }

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

        markdown = f"""# EXECUTIVE SUMMARY

## Overall Assessment
**Score: {self.overall_score}/100** {emoji} {self.rating.title()}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""

        if self.priority_actions:
            markdown += "## Priority Actions\n\n"
            for i, action in enumerate(self.priority_actions[:5], 1):
                markdown += f"{i}. **{action.get('title', 'Action')}**\n"
                markdown += f"   - {action.get('description', 'No description')}\n\n"

        return markdown


class StorePageSection(ReportSection):
    """Store page optimization analysis"""

    def analyze(self) -> Dict[str, Any]:
        """Analyze store page elements"""
        logger.info("Analyzing store page")

        # Placeholder scoring logic - will be enhanced in Phase 1
        game_data = self.data.get('game_data', {})

        # Basic scoring based on available data
        scores = {
            'has_description': 10 if game_data.get('short_description') else 0,
            'has_screenshots': 10 if game_data.get('screenshots') else 0,
            'has_movies': 10 if game_data.get('movies') else 0,
            'has_genres': 10 if game_data.get('genres') else 0,
        }

        self.score = sum(scores.values())
        self.rating = self.get_rating()
        self.analyzed = True

        return {
            'score': self.score,
            'rating': self.rating,
            'scores': scores
        }

    def generate_markdown(self) -> str:
        """Generate store page analysis markdown"""
        if not self.analyzed:
            self.analyze()

        return f"""## Store Page Analysis

**Score: {self.score}/100** - {self.rating.title()}

### Current Status
[Detailed analysis will be added in Phase 1]

"""


class CompetitorSection(ReportSection):
    """Competitor analysis and benchmarking"""

    def analyze(self) -> Dict[str, Any]:
        """Analyze competitive position"""
        logger.info("Analyzing competitors")

        competitors = self.data.get('competitors', [])

        # Basic scoring - will be enhanced
        self.score = 70 if len(competitors) >= 3 else 40
        self.rating = self.get_rating()
        self.analyzed = True

        return {
            'score': self.score,
            'rating': self.rating,
            'competitor_count': len(competitors)
        }

    def generate_markdown(self) -> str:
        """Generate competitor analysis markdown"""
        if not self.analyzed:
            self.analyze()

        competitors = self.data.get('competitors', [])

        markdown = f"""## Competitive Analysis

**Score: {self.score}/100** - {self.rating.title()}

Found {len(competitors)} competitors for analysis.

"""
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

        # Create standard sections
        store_section = StorePageSection("Store Page", {
            'game_data': self.game_data
        })
        self.add_section(store_section)

        competitor_section = CompetitorSection("Competitors", {
            'competitors': self.competitor_data,
            'game_data': self.game_data
        })
        self.add_section(competitor_section)

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
        return f"""---

## About This Report

This audit report was generated by Publitz Automated Audits on {datetime.now().strftime('%Y-%m-%d at %I:%M %p')}.

**Report Version:** 2.0 (Enhanced)
**Analysis Type:** {self.report_type}
**Overall Score:** {self.overall_score}/100

For questions or support, contact: support@publitz.com

---

*This report is confidential and intended for the recipient only.*
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
