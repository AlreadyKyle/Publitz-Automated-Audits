#!/usr/bin/env python3
"""
Scoring Framework - Quantitative Metrics Evaluation
Provides standardized scoring for various game metrics with benchmarking
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from src.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ScoreResult:
    """Standardized score result"""
    score: int  # 0-100
    rating: str  # 'excellent', 'good', 'fair', 'poor'
    reason: str  # Explanation
    benchmark: Dict[str, Any]  # Reference data
    confidence: float = 1.0  # 0-1, confidence in scoring


class MetricScorer:
    """Calculate scores for various metrics"""

    # Rating thresholds
    EXCELLENT_THRESHOLD = 80
    GOOD_THRESHOLD = 65
    FAIR_THRESHOLD = 50

    @staticmethod
    def _get_rating(score: int) -> str:
        """Convert numeric score to rating label"""
        if score >= MetricScorer.EXCELLENT_THRESHOLD:
            return "excellent"
        elif score >= MetricScorer.GOOD_THRESHOLD:
            return "good"
        elif score >= MetricScorer.FAIR_THRESHOLD:
            return "fair"
        else:
            return "poor"

    @staticmethod
    def score_price_positioning(price: float, genre_avg: float,
                               genre_median: float, genre_low: float,
                               genre_high: float) -> ScoreResult:
        """
        Score price positioning relative to genre

        Args:
            price: Game price
            genre_avg: Average price in genre
            genre_median: Median price in genre
            genre_low: 25th percentile price
            genre_high: 75th percentile price

        Returns:
            ScoreResult with pricing assessment
        """
        logger.debug(f"Scoring price: ${price} vs genre avg ${genre_avg}")

        # Calculate how well price fits in genre range
        if genre_low <= price <= genre_high:
            # Within IQR (interquartile range) - good positioning
            score = 85

            if abs(price - genre_median) / genre_median < 0.1:
                # Very close to median - excellent
                score = 95
                reason = f"Price ${price:.2f} is well-positioned at genre median (${genre_median:.2f})"
            else:
                reason = f"Price ${price:.2f} fits comfortably in genre range (${genre_low:.2f}-${genre_high:.2f})"

        elif price < genre_low:
            # Below range - may be underpriced
            discount_pct = ((genre_low - price) / genre_low) * 100

            if discount_pct < 15:
                score = 75
                reason = f"Price ${price:.2f} is {discount_pct:.0f}% below genre range - competitive positioning"
            else:
                score = 50
                reason = f"Price ${price:.2f} is {discount_pct:.0f}% below genre range - may be significantly undervalued"

        else:  # price > genre_high
            # Above range - premium pricing
            premium_pct = ((price - genre_high) / genre_high) * 100

            if premium_pct < 20:
                score = 70
                reason = f"Price ${price:.2f} is {premium_pct:.0f}% above genre range - premium positioning"
            else:
                score = 40
                reason = f"Price ${price:.2f} is {premium_pct:.0f}% above genre range - may limit sales volume"

        return ScoreResult(
            score=score,
            rating=MetricScorer._get_rating(score),
            reason=reason,
            benchmark={
                'genre_avg': genre_avg,
                'genre_median': genre_median,
                'genre_range': f"${genre_low:.2f}-${genre_high:.2f}",
                'your_price': price
            }
        )

    @staticmethod
    def score_wishlist_count(count: int, days_until_launch: int,
                            genre_benchmarks: Dict[str, int]) -> ScoreResult:
        """
        Score wishlist count relative to launch timeline and genre

        Args:
            count: Current wishlist count
            days_until_launch: Days remaining until launch (negative if launched)
            genre_benchmarks: Dict with 'low', 'median', 'high' wishlist counts

        Returns:
            ScoreResult with wishlist assessment
        """
        logger.debug(f"Scoring {count} wishlists with {days_until_launch} days to launch")

        median = genre_benchmarks.get('median', 10000)
        low = genre_benchmarks.get('low', 2000)
        high = genre_benchmarks.get('high', 50000)

        # Adjust expectations based on timeline
        if days_until_launch > 180:  # 6+ months out
            target = median * 0.3
        elif days_until_launch > 90:  # 3-6 months out
            target = median * 0.6
        elif days_until_launch > 30:  # 1-3 months out
            target = median * 0.9
        elif days_until_launch > 0:  # Less than 1 month
            target = median
        else:  # Already launched
            target = median * 1.2  # Should be growing post-launch

        # Calculate score
        performance_ratio = count / target if target > 0 else 0

        if performance_ratio >= 1.5:
            score = 95
            reason = f"{count:,} wishlists - {(performance_ratio - 1) * 100:.0f}% above target for timeline"
        elif performance_ratio >= 1.0:
            score = 85
            reason = f"{count:,} wishlists - on track for genre benchmarks"
        elif performance_ratio >= 0.7:
            score = 65
            reason = f"{count:,} wishlists - {(1 - performance_ratio) * 100:.0f}% below target but recoverable"
        elif performance_ratio >= 0.4:
            score = 45
            reason = f"{count:,} wishlists - significantly below target, marketing push needed"
        else:
            score = 25
            reason = f"{count:,} wishlists - critical gap vs genre expectations"

        return ScoreResult(
            score=score,
            rating=MetricScorer._get_rating(score),
            reason=reason,
            benchmark={
                'current': count,
                'target_for_timeline': int(target),
                'genre_median_at_launch': median,
                'genre_range': f"{low:,}-{high:,}",
                'days_to_launch': days_until_launch
            },
            confidence=0.8  # Moderate confidence due to timeline adjustments
        )

    @staticmethod
    def score_store_page_completeness(game_data: Dict[str, Any]) -> ScoreResult:
        """
        Score store page completeness and quality

        Args:
            game_data: Game data from Steam API

        Returns:
            ScoreResult with store page assessment
        """
        logger.debug("Scoring store page completeness")

        score = 0
        elements = []
        missing = []

        # Description (10 points)
        if game_data.get('short_description'):
            score += 10
            elements.append("Short description")
        else:
            missing.append("Short description")

        # Long description (10 points)
        detailed_desc = game_data.get('detailed_description', '')
        if len(detailed_desc) > 200:
            score += 10
            elements.append("Detailed description")
        else:
            missing.append("Detailed description (or too short)")

        # Screenshots (20 points)
        screenshots = game_data.get('screenshots', [])
        screenshot_count = len(screenshots)
        if screenshot_count >= 5:
            score += 20
            elements.append(f"{screenshot_count} screenshots")
        elif screenshot_count >= 3:
            score += 10
            missing.append(f"Only {screenshot_count}/5 screenshots")
        else:
            missing.append(f"Only {screenshot_count}/5 screenshots (minimum 5 recommended)")

        # Videos/Trailers (15 points)
        movies = game_data.get('movies', [])
        if len(movies) >= 1:
            score += 15
            elements.append(f"{len(movies)} video(s)")
        else:
            missing.append("Trailer/gameplay video")

        # Genres (10 points)
        genres = game_data.get('genres', [])
        if len(genres) >= 2:
            score += 10
            elements.append(f"{len(genres)} genres")
        else:
            missing.append("Additional genres (minimum 2)")

        # Categories (features) (10 points)
        categories = game_data.get('categories', [])
        if len(categories) >= 3:
            score += 10
            elements.append(f"{len(categories)} features")
        elif len(categories) >= 1:
            score += 5
            missing.append(f"Only {len(categories)}/3 feature tags")
        else:
            missing.append("Feature tags (achievements, multiplayer, etc)")

        # Supported languages (10 points)
        languages = game_data.get('supported_languages', '')
        if 'English' in languages and len(languages) > 50:  # Multiple languages
            score += 10
            elements.append("Multiple languages")
        elif 'English' in languages:
            score += 5
            missing.append("Additional language support")
        else:
            missing.append("Language support information")

        # Developers/Publishers (5 points)
        if game_data.get('developers') and game_data.get('publishers'):
            score += 5
            elements.append("Developer/Publisher info")
        else:
            missing.append("Developer/Publisher information")

        # Release date (5 points)
        if game_data.get('release_date', {}).get('date'):
            score += 5
            elements.append("Release date set")
        else:
            missing.append("Release date")

        # Platform support (5 points)
        platforms = game_data.get('platforms', {})
        platform_count = sum(1 for p in ['windows', 'mac', 'linux'] if platforms.get(p))
        if platform_count >= 2:
            score += 5
            elements.append(f"{platform_count} platforms")
        elif platform_count == 1:
            score += 2
            missing.append("Additional platform support")

        # Generate reason
        if score >= 80:
            reason = "Store page is well-optimized with all essential elements"
        elif score >= 65:
            reason = "Store page is good but missing some recommended elements"
        elif score >= 50:
            reason = "Store page needs improvement in several areas"
        else:
            reason = "Store page requires significant optimization"

        return ScoreResult(
            score=score,
            rating=MetricScorer._get_rating(score),
            reason=reason,
            benchmark={
                'present': elements,
                'missing': missing,
                'completeness': f"{score}/100"
            }
        )

    @staticmethod
    def score_tag_optimization(current_tags: List[str], max_tags: int = 20) -> ScoreResult:
        """
        Score tag usage

        Args:
            current_tags: List of current tags
            max_tags: Maximum allowed tags (Steam allows 20)

        Returns:
            ScoreResult with tag optimization assessment
        """
        tag_count = len(current_tags)
        optimal_min = 15  # Recommended minimum

        if tag_count >= optimal_min:
            score = 90
            reason = f"Using {tag_count}/{max_tags} tags - good coverage"
        elif tag_count >= 10:
            score = 70
            gap = optimal_min - tag_count
            reason = f"Using {tag_count}/{max_tags} tags - add {gap} more for better discoverability"
        elif tag_count >= 5:
            score = 50
            gap = optimal_min - tag_count
            reason = f"Using {tag_count}/{max_tags} tags - significantly underutilized, add {gap} more"
        else:
            score = 30
            reason = f"Using only {tag_count}/{max_tags} tags - critically underutilized"

        return ScoreResult(
            score=score,
            rating=MetricScorer._get_rating(score),
            reason=reason,
            benchmark={
                'current_count': tag_count,
                'optimal_min': optimal_min,
                'maximum': max_tags,
                'gap': max(0, optimal_min - tag_count)
            }
        )


class OverallScorer:
    """Calculate weighted overall score from section scores"""

    # Default weights for different sections
    DEFAULT_WEIGHTS = {
        'store_page': 0.30,
        'pricing': 0.15,
        'competitive_position': 0.25,
        'marketing_readiness': 0.20,
        'community': 0.10
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize with custom or default weights

        Args:
            weights: Optional custom weights dict
        """
        self.weights = weights or self.DEFAULT_WEIGHTS
        logger.debug(f"OverallScorer initialized with weights: {self.weights}")

    def calculate_overall(self, section_scores: Dict[str, int]) -> int:
        """
        Calculate weighted overall score

        Args:
            section_scores: Dict mapping section names to scores (0-100)

        Returns:
            Overall weighted score (0-100)
        """
        weighted_sum = 0
        total_weight = 0

        for section, score in section_scores.items():
            # Normalize section name to match weight keys
            section_key = section.lower().replace(' ', '_')

            weight = self.weights.get(section_key, 0.1)  # Default 0.1 if not in weights
            weighted_sum += score * weight
            total_weight += weight

            logger.debug(f"Section '{section}': score={score}, weight={weight}")

        if total_weight == 0:
            logger.warning("Total weight is 0, returning 0 score")
            return 0

        overall = int(weighted_sum / total_weight)
        logger.info(f"Overall score calculated: {overall}/100")

        return overall

    def get_section_weight(self, section_name: str) -> float:
        """Get weight for a specific section"""
        section_key = section_name.lower().replace(' ', '_')
        return self.weights.get(section_key, 0.1)


# Convenience functions
def score_metric(metric_name: str, value: Any, benchmark_data: Dict[str, Any]) -> ScoreResult:
    """
    Score any metric by name

    Args:
        metric_name: Name of metric to score
        value: Current value
        benchmark_data: Benchmark/comparison data

    Returns:
        ScoreResult
    """
    if metric_name == 'price':
        return MetricScorer.score_price_positioning(
            value,
            benchmark_data.get('avg'),
            benchmark_data.get('median'),
            benchmark_data.get('low'),
            benchmark_data.get('high')
        )
    elif metric_name == 'wishlists':
        return MetricScorer.score_wishlist_count(
            value,
            benchmark_data.get('days_to_launch', 0),
            benchmark_data.get('genre_benchmarks', {})
        )
    elif metric_name == 'store_page':
        return MetricScorer.score_store_page_completeness(value)
    elif metric_name == 'tags':
        return MetricScorer.score_tag_optimization(value)
    else:
        logger.warning(f"Unknown metric: {metric_name}")
        return ScoreResult(
            score=0,
            rating='unknown',
            reason=f"Unknown metric: {metric_name}",
            benchmark={}
        )
