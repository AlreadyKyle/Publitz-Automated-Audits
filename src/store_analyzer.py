#!/usr/bin/env python3
"""
Store Page Analyzer - Deep Analysis of Steam Store Page Elements
Provides specific, actionable recommendations for store optimization
"""

from typing import Dict, List, Any, Optional, Tuple
from src.logger import get_logger
from src.models import Recommendation, Priority, ImpactLevel
from src.scoring import MetricScorer, ScoreResult

logger = get_logger(__name__)


class StorePageAnalyzer:
    """Analyze Steam store page elements for optimization opportunities"""

    # Optimal ranges based on Steam best practices
    OPTIMAL_TAG_COUNT = 15
    MAX_TAG_COUNT = 20
    OPTIMAL_SCREENSHOT_COUNT = 8
    MIN_SCREENSHOT_COUNT = 5
    OPTIMAL_DESCRIPTION_LENGTH = 400  # words
    MIN_DESCRIPTION_LENGTH = 150

    # Common genre tags for recommendations
    GENRE_TAG_DATABASE = {
        'roguelike': ['Roguelike', 'Roguelite', 'Procedural Generation', 'Difficult', 'Replay Value',
                      'Permadeath', 'Action Roguelike', 'Traditional Roguelike'],
        'strategy': ['Strategy', 'Turn-Based Strategy', 'Real-Time Strategy', 'Grand Strategy',
                     'Tower Defense', 'Tactical', '4X', 'Wargame'],
        'rpg': ['RPG', 'JRPG', 'Action RPG', 'Turn-Based Combat', 'Character Customization',
                'Choices Matter', 'Story Rich', 'Open World'],
        'puzzle': ['Puzzle', 'Logic', 'Minimalist', 'Relaxing', 'Casual', 'Abstract'],
        'action': ['Action', 'Fast-Paced', 'Arcade', 'Shooter', 'Beat \'em up', 'Hack and Slash'],
        'indie': ['Indie', 'Pixel Graphics', 'Retro', '2D', 'Stylized', 'Colorful'],
        'simulation': ['Simulation', 'Realistic', 'Management', 'Building', 'Economy'],
        'adventure': ['Adventure', 'Exploration', 'Atmospheric', 'Story Rich', 'Walking Simulator']
    }

    def __init__(self):
        logger.info("StorePageAnalyzer initialized")

    def analyze_complete(self, game_data: Dict[str, Any],
                        competitor_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Complete store page analysis

        Args:
            game_data: Game data from Steam API
            competitor_data: Optional competitor data for benchmarking

        Returns:
            Complete analysis with scores and recommendations
        """
        logger.info(f"Analyzing store page for {game_data.get('name', 'Unknown')}")

        results = {
            'overall_score': 0,
            'overall_rating': 'unknown',
            'sections': {},
            'recommendations': [],
            'strengths': [],
            'weaknesses': []
        }

        # Analyze each component
        tag_analysis = self.analyze_tags(game_data, competitor_data)
        screenshot_analysis = self.analyze_screenshots(game_data, competitor_data)
        description_analysis = self.analyze_description(game_data)
        media_analysis = self.analyze_media(game_data)
        regional_analysis = self.analyze_regional_support(game_data, competitor_data)

        # Store section results
        results['sections'] = {
            'tags': tag_analysis,
            'screenshots': screenshot_analysis,
            'description': description_analysis,
            'media': media_analysis,
            'regional': regional_analysis
        }

        # Calculate weighted overall score
        weights = {
            'tags': 0.25,
            'screenshots': 0.20,
            'description': 0.20,
            'media': 0.20,
            'regional': 0.15
        }

        weighted_score = sum(
            results['sections'][section]['score'] * weights[section]
            for section in weights.keys()
        )
        results['overall_score'] = int(weighted_score)
        results['overall_rating'] = self._score_to_rating(results['overall_score'])

        # Collect all recommendations
        for section in results['sections'].values():
            results['recommendations'].extend(section.get('recommendations', []))

        # Collect strengths and weaknesses
        for section_name, section in results['sections'].items():
            if section['score'] >= 80:
                results['strengths'].append(f"{section_name.title()}: {section['reason']}")
            elif section['score'] < 60:
                results['weaknesses'].append(f"{section_name.title()}: {section['reason']}")

        logger.info(f"Store page analysis complete. Score: {results['overall_score']}/100")

        return results

    def analyze_tags(self, game_data: Dict[str, Any],
                    competitor_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze tag usage and provide recommendations

        Args:
            game_data: Game data
            competitor_data: Competitor data for tag comparison

        Returns:
            Tag analysis with recommendations
        """
        logger.debug("Analyzing tags")

        # Extract current tags
        current_tags = []
        if 'tags' in game_data:
            current_tags = game_data['tags'] if isinstance(game_data['tags'], list) else []

        tag_count = len(current_tags)

        # Score based on tag count
        score_result = MetricScorer.score_tag_optimization(current_tags, self.MAX_TAG_COUNT)

        # Generate recommendations
        recommendations = []
        missing_tags = []

        # Suggest tags based on genres
        genres = game_data.get('genres', [])
        genre_names = [g.get('description', '').lower() for g in genres if isinstance(g, dict)]

        for genre in genre_names:
            for db_genre, tags in self.GENRE_TAG_DATABASE.items():
                if db_genre in genre:
                    # Find tags not currently used
                    for tag in tags:
                        if tag not in current_tags and tag.lower() not in [t.lower() for t in current_tags]:
                            missing_tags.append(tag)

        # Limit to top missing tags
        missing_tags = list(set(missing_tags))[:self.MAX_TAG_COUNT - tag_count]

        if missing_tags:
            recommendations.append(Recommendation(
                title=f"Add {len(missing_tags)} missing tags for better discoverability",
                description=f"Add these relevant tags: {', '.join(missing_tags[:5])}{'...' if len(missing_tags) > 5 else ''}",
                priority=Priority.HIGH if tag_count < 10 else Priority.MEDIUM,
                impact=ImpactLevel.HIGH if tag_count < 10 else ImpactLevel.MEDIUM,
                category="store_page",
                time_estimate="5-10 minutes"
            ))

        # Analyze competitor tags if available
        if competitor_data:
            competitor_tags = self._extract_competitor_tags(competitor_data)
            popular_missing = [tag for tag in competitor_tags[:10] if tag not in current_tags]

            if popular_missing:
                recommendations.append(Recommendation(
                    title="Add popular tags used by competitors",
                    description=f"Competitors commonly use: {', '.join(popular_missing[:5])}",
                    priority=Priority.MEDIUM,
                    impact=ImpactLevel.MEDIUM,
                    category="store_page",
                    time_estimate="5 minutes"
                ))

        return {
            'score': score_result.score,
            'rating': score_result.rating,
            'reason': score_result.reason,
            'current_count': tag_count,
            'optimal_count': self.OPTIMAL_TAG_COUNT,
            'missing_tags': missing_tags,
            'recommendations': recommendations,
            'benchmark': score_result.benchmark
        }

    def analyze_screenshots(self, game_data: Dict[str, Any],
                          competitor_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze screenshot count and provide recommendations

        Args:
            game_data: Game data
            competitor_data: Competitor data for comparison

        Returns:
            Screenshot analysis with recommendations
        """
        logger.debug("Analyzing screenshots")

        screenshots = game_data.get('screenshots', [])
        screenshot_count = len(screenshots)

        # Score based on count
        if screenshot_count >= self.OPTIMAL_SCREENSHOT_COUNT:
            score = 90
            reason = f"{screenshot_count} screenshots - excellent coverage"
        elif screenshot_count >= self.MIN_SCREENSHOT_COUNT:
            score = 75
            reason = f"{screenshot_count} screenshots - good, add {self.OPTIMAL_SCREENSHOT_COUNT - screenshot_count} more for optimal"
        elif screenshot_count >= 3:
            score = 50
            reason = f"Only {screenshot_count} screenshots - add {self.OPTIMAL_SCREENSHOT_COUNT - screenshot_count} more"
        else:
            score = 30
            reason = f"Only {screenshot_count} screenshots - critically low, need {self.MIN_SCREENSHOT_COUNT} minimum"

        recommendations = []

        if screenshot_count < self.OPTIMAL_SCREENSHOT_COUNT:
            gap = self.OPTIMAL_SCREENSHOT_COUNT - screenshot_count
            recommendations.append(Recommendation(
                title=f"Add {gap} more screenshots",
                description=f"Increase from {screenshot_count} to {self.OPTIMAL_SCREENSHOT_COUNT} for optimal conversion. Show key features, gameplay variety, and visual highlights.",
                priority=Priority.HIGH if screenshot_count < 5 else Priority.MEDIUM,
                impact=ImpactLevel.HIGH if screenshot_count < 5 else ImpactLevel.MEDIUM,
                category="store_page",
                effort_description="Take high-quality screenshots showing diverse gameplay",
                time_estimate="1-2 hours"
            ))

        # Compare to competitors
        if competitor_data:
            comp_counts = [len(c.get('screenshots', [])) for c in competitor_data if c.get('screenshots')]
            if comp_counts:
                avg_comp_screenshots = sum(comp_counts) / len(comp_counts)
                if screenshot_count < avg_comp_screenshots * 0.8:
                    recommendations.append(Recommendation(
                        title="Match competitor screenshot counts",
                        description=f"Competitors average {int(avg_comp_screenshots)} screenshots. You have {screenshot_count}.",
                        priority=Priority.MEDIUM,
                        impact=ImpactLevel.MEDIUM,
                        category="store_page"
                    ))

        return {
            'score': score,
            'rating': self._score_to_rating(score),
            'reason': reason,
            'current_count': screenshot_count,
            'optimal_count': self.OPTIMAL_SCREENSHOT_COUNT,
            'recommendations': recommendations
        }

    def analyze_description(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze description quality

        Args:
            game_data: Game data

        Returns:
            Description analysis
        """
        logger.debug("Analyzing description")

        short_desc = game_data.get('short_description', '')
        detailed_desc = game_data.get('detailed_description', '')

        # Word count (approximate - strip HTML tags)
        import re
        detailed_clean = re.sub(r'<[^>]+>', '', detailed_desc)
        word_count = len(detailed_clean.split())

        # Score based on length and completeness
        if word_count >= self.OPTIMAL_DESCRIPTION_LENGTH:
            score = 90
            reason = f"{word_count} words - comprehensive description"
        elif word_count >= self.MIN_DESCRIPTION_LENGTH:
            score = 70
            reason = f"{word_count} words - adequate but could be expanded"
        elif word_count >= 50:
            score = 45
            reason = f"Only {word_count} words - too brief, expand to {self.OPTIMAL_DESCRIPTION_LENGTH}+ words"
        else:
            score = 25
            reason = f"Only {word_count} words - critically lacking detail"

        recommendations = []

        if not short_desc:
            recommendations.append(Recommendation(
                title="Add short description",
                description="Short description is missing - this appears in search results and is critical for first impressions",
                priority=Priority.CRITICAL,
                impact=ImpactLevel.HIGH,
                category="store_page"
            ))

        if word_count < self.MIN_DESCRIPTION_LENGTH:
            recommendations.append(Recommendation(
                title="Expand detailed description",
                description=f"Expand from {word_count} to {self.OPTIMAL_DESCRIPTION_LENGTH}+ words. Include: gameplay features, story hook, unique mechanics, target audience.",
                priority=Priority.HIGH,
                impact=ImpactLevel.HIGH,
                category="store_page",
                time_estimate="1-2 hours"
            ))

        return {
            'score': score,
            'rating': self._score_to_rating(score),
            'reason': reason,
            'word_count': word_count,
            'has_short_description': bool(short_desc),
            'recommendations': recommendations
        }

    def analyze_media(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze video/trailer presence

        Args:
            game_data: Game data

        Returns:
            Media analysis
        """
        logger.debug("Analyzing media")

        movies = game_data.get('movies', [])
        video_count = len(movies)

        if video_count >= 2:
            score = 95
            reason = f"{video_count} videos - excellent multimedia presence"
        elif video_count == 1:
            score = 80
            reason = "1 video present - consider adding gameplay footage or feature highlights"
        else:
            score = 30
            reason = "No videos - trailer is critical for conversions"

        recommendations = []

        if video_count == 0:
            recommendations.append(Recommendation(
                title="Add gameplay trailer",
                description="Games with trailers convert 3-5x better. Create a 30-60 second trailer showing core gameplay within first 10 seconds.",
                priority=Priority.CRITICAL,
                impact=ImpactLevel.HIGH,
                category="store_page",
                effort_description="Record, edit, and upload gameplay trailer",
                time_estimate="4-8 hours for professional quality"
            ))
        elif video_count == 1:
            recommendations.append(Recommendation(
                title="Add additional gameplay videos",
                description="Consider adding: feature spotlight, gameplay montage, or dev commentary",
                priority=Priority.LOW,
                impact=ImpactLevel.MEDIUM,
                category="store_page"
            ))

        return {
            'score': score,
            'rating': self._score_to_rating(score),
            'reason': reason,
            'video_count': video_count,
            'recommendations': recommendations
        }

    def analyze_regional_support(self, game_data: Dict[str, Any],
                                 competitor_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze language and regional support

        Args:
            game_data: Game data
            competitor_data: Competitor data

        Returns:
            Regional analysis
        """
        logger.debug("Analyzing regional support")

        supported_languages = game_data.get('supported_languages', '')

        # Count languages (rough estimate)
        language_count = supported_languages.count(',') + 1 if supported_languages else 0

        # Key markets
        has_english = 'English' in supported_languages
        has_chinese = 'Chinese' in supported_languages or '中文' in supported_languages
        has_spanish = 'Spanish' in supported_languages
        has_japanese = 'Japanese' in supported_languages
        has_german = 'German' in supported_languages

        # Score
        score = 50  # Base
        if has_english:
            score += 20
        if has_chinese:
            score += 15
        if has_spanish:
            score += 5
        if has_japanese:
            score += 5
        if has_german:
            score += 5

        reason = f"{language_count} languages supported"

        recommendations = []

        # Recommend key markets
        if not has_chinese:
            recommendations.append(Recommendation(
                title="Add Simplified Chinese localization",
                description="China is the largest PC gaming market. Chinese localization can increase sales by 40-60%.",
                priority=Priority.HIGH,
                impact=ImpactLevel.HIGH,
                category="regional",
                effort_description="Professional translation + testing",
                time_estimate="2-4 weeks, ~$600-1200 cost"
            ))

        if not has_japanese and language_count < 3:
            recommendations.append(Recommendation(
                title="Consider Japanese localization",
                description="Japan represents 10-15% of Steam revenue. Strong ROI for many genres.",
                priority=Priority.MEDIUM,
                impact=ImpactLevel.MEDIUM,
                category="regional"
            ))

        return {
            'score': min(score, 100),
            'rating': self._score_to_rating(min(score, 100)),
            'reason': reason,
            'language_count': language_count,
            'key_markets': {
                'english': has_english,
                'chinese': has_chinese,
                'spanish': has_spanish,
                'japanese': has_japanese,
                'german': has_german
            },
            'recommendations': recommendations
        }

    def _extract_competitor_tags(self, competitor_data: List[Dict[str, Any]]) -> List[str]:
        """Extract and rank tags from competitors by frequency"""
        tag_counts = {}

        for comp in competitor_data:
            comp_tags = comp.get('tags', [])
            if isinstance(comp_tags, list):
                for tag in comp_tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Sort by frequency
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, count in sorted_tags]

    def _score_to_rating(self, score: int) -> str:
        """Convert score to rating label"""
        if score >= 80:
            return "excellent"
        elif score >= 65:
            return "good"
        elif score >= 50:
            return "fair"
        else:
            return "poor"
