#!/usr/bin/env python3
"""
Data Models - Structured Data Types for Reports
Provides dataclasses for type-safe report data handling
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import json


class Priority(Enum):
    """Recommendation priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ImpactLevel(Enum):
    """Expected impact of recommendations"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReportType(Enum):
    """Type of audit report"""
    PRE_LAUNCH = "Pre-Launch"
    POST_LAUNCH = "Post-Launch"


class EffortLevel(Enum):
    """Effort required for recommendations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Recommendation:
    """Structured recommendation with actionable details"""
    title: str
    description: str
    priority: Priority
    impact: ImpactLevel
    category: str  # "store_page", "pricing", "marketing", etc.

    # Optional fields for enhanced recommendations
    effort: Optional[EffortLevel] = None
    effort_description: Optional[str] = None
    time_estimate: Optional[str] = None  # "1-2 weeks", "1 day", etc.
    implementation_steps: Optional[List[str]] = None  # Step-by-step how-to
    estimated_cost: Optional[str] = None  # "$0", "$50-100", "Free", etc.
    expected_result: Optional[str] = None  # What outcome to expect

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'description': self.description,
            'priority': self.priority.value if isinstance(self.priority, Priority) else self.priority,
            'impact': self.impact.value if isinstance(self.impact, ImpactLevel) else self.impact,
            'category': self.category,
            'effort': self.effort.value if isinstance(self.effort, EffortLevel) and self.effort else None,
            'effort_description': self.effort_description,
            'time_estimate': self.time_estimate,
            'implementation_steps': self.implementation_steps,
            'estimated_cost': self.estimated_cost,
            'expected_result': self.expected_result
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Recommendation':
        """Create from dictionary"""
        effort_val = data.get('effort')
        effort = EffortLevel(effort_val) if effort_val and isinstance(effort_val, str) else effort_val

        return Recommendation(
            title=data['title'],
            description=data['description'],
            priority=Priority(data['priority']) if isinstance(data['priority'], str) else data['priority'],
            impact=ImpactLevel(data['impact']) if isinstance(data['impact'], str) else data['impact'],
            category=data['category'],
            effort=effort,
            effort_description=data.get('effort_description'),
            time_estimate=data.get('time_estimate'),
            implementation_steps=data.get('implementation_steps'),
            estimated_cost=data.get('estimated_cost'),
            expected_result=data.get('expected_result')
        )


@dataclass
class SectionScore:
    """Score and analysis for a report section"""
    name: str
    score: int  # 0-100
    rating: str  # "excellent", "good", "fair", "poor"
    recommendations: List[Recommendation] = field(default_factory=list)
    benchmarks: Dict[str, Any] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'score': self.score,
            'rating': self.rating,
            'recommendations': [r.to_dict() for r in self.recommendations],
            'benchmarks': self.benchmarks,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SectionScore':
        """Create from dictionary"""
        return SectionScore(
            name=data['name'],
            score=data['score'],
            rating=data['rating'],
            recommendations=[Recommendation.from_dict(r) for r in data.get('recommendations', [])],
            benchmarks=data.get('benchmarks', {}),
            strengths=data.get('strengths', []),
            weaknesses=data.get('weaknesses', [])
        )


@dataclass
class GameInfo:
    """Basic game information"""
    app_id: int
    name: str
    release_date: Optional[str] = None
    developers: List[str] = field(default_factory=list)
    publishers: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    price: Optional[float] = None
    platforms: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @staticmethod
    def from_steam_data(game_data: Dict[str, Any]) -> 'GameInfo':
        """Create from Steam API data"""
        return GameInfo(
            app_id=game_data.get('steam_appid', 0),
            name=game_data.get('name', 'Unknown'),
            release_date=game_data.get('release_date', {}).get('date'),
            developers=game_data.get('developers', []),
            publishers=game_data.get('publishers', []),
            genres=[g.get('description', '') for g in game_data.get('genres', [])],
            tags=game_data.get('tags', []),
            price=game_data.get('price_overview', {}).get('final') / 100 if game_data.get('price_overview') else None,
            platforms=[p for p, enabled in game_data.get('platforms', {}).items() if enabled]
        )


@dataclass
class CompetitorInfo:
    """Competitor game information"""
    app_id: int
    name: str
    price: Optional[float] = None
    release_date: Optional[str] = None
    score: Optional[int] = None  # Metacritic or similar
    review_count: Optional[int] = None
    positive_percentage: Optional[int] = None
    estimated_owners: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class MarketData:
    """Market and sales data"""
    wishlist_count: Optional[int] = None
    owners_min: Optional[int] = None
    owners_max: Optional[int] = None
    owners_avg: Optional[int] = None
    review_count: Optional[int] = None
    positive_percentage: Optional[float] = None
    estimated_revenue: Optional[str] = None
    genre_averages: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ReportMetadata:
    """Report metadata and context"""
    generated_at: datetime
    report_type: ReportType
    version: str = "2.0"
    generator: str = "Publitz Automated Audits"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'generated_at': self.generated_at.isoformat(),
            'report_type': self.report_type.value if isinstance(self.report_type, ReportType) else self.report_type,
            'version': self.version,
            'generator': self.generator
        }


@dataclass
class ReportData:
    """Complete structured report data"""
    metadata: ReportMetadata
    game_info: GameInfo
    overall_score: int  # 0-100
    overall_rating: str  # "excellent", "good", "fair", "poor"
    sections: List[SectionScore] = field(default_factory=list)
    market_data: Optional[MarketData] = None
    competitors: List[CompetitorInfo] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export"""
        return {
            'metadata': self.metadata.to_dict(),
            'game_info': self.game_info.to_dict(),
            'overall_score': self.overall_score,
            'overall_rating': self.overall_rating,
            'sections': [s.to_dict() for s in self.sections],
            'market_data': self.market_data.to_dict() if self.market_data else None,
            'competitors': [c.to_dict() for c in self.competitors]
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ReportData':
        """Create from dictionary"""
        return ReportData(
            metadata=ReportMetadata(
                generated_at=datetime.fromisoformat(data['metadata']['generated_at']),
                report_type=ReportType(data['metadata']['report_type']),
                version=data['metadata'].get('version', '2.0'),
                generator=data['metadata'].get('generator', 'Publitz')
            ),
            game_info=GameInfo(**data['game_info']),
            overall_score=data['overall_score'],
            overall_rating=data['overall_rating'],
            sections=[SectionScore.from_dict(s) for s in data.get('sections', [])],
            market_data=MarketData(**data['market_data']) if data.get('market_data') else None,
            competitors=[CompetitorInfo(**c) for c in data.get('competitors', [])]
        )


# Helper functions
def create_report_data(game_data: Dict[str, Any], sales_data: Dict[str, Any],
                      competitor_data: List[Dict[str, Any]], report_type: str,
                      overall_score: int, sections: List[SectionScore]) -> ReportData:
    """
    Factory function to create ReportData from raw inputs

    Args:
        game_data: Raw game data from Steam
        sales_data: Sales/market data
        competitor_data: List of competitor data
        report_type: "Pre-Launch" or "Post-Launch"
        overall_score: Calculated overall score
        sections: List of analyzed sections

    Returns:
        ReportData instance
    """
    return ReportData(
        metadata=ReportMetadata(
            generated_at=datetime.now(),
            report_type=ReportType(report_type) if isinstance(report_type, str) else report_type
        ),
        game_info=GameInfo.from_steam_data(game_data),
        overall_score=overall_score,
        overall_rating=_score_to_rating(overall_score),
        sections=sections,
        market_data=MarketData(
            wishlist_count=sales_data.get('wishlist_count'),
            owners_min=sales_data.get('owners_min'),
            owners_max=sales_data.get('owners_max'),
            owners_avg=sales_data.get('owners_avg'),
            review_count=sales_data.get('review_count'),
            positive_percentage=sales_data.get('positive_percentage'),
            estimated_revenue=sales_data.get('estimated_revenue')
        ),
        competitors=[
            CompetitorInfo(
                app_id=c.get('app_id', 0),
                name=c.get('name', 'Unknown'),
                price=c.get('price_overview', {}).get('final', 0) / 100 if c.get('price_overview') else None,
                release_date=c.get('release_date', {}).get('date')
            )
            for c in competitor_data
        ]
    )


def _score_to_rating(score: int) -> str:
    """Convert numeric score to rating label"""
    if score >= 80:
        return "excellent"
    elif score >= 65:
        return "good"
    elif score >= 50:
        return "fair"
    else:
        return "poor"
