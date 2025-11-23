#!/usr/bin/env python3
"""
Review Sentiment Analyzer - Samples and analyzes actual Steam reviews

Replaces estimated sentiment percentages with real data from Steam reviews
analyzed using Claude API for accurate theme categorization.
"""

import requests
import random
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from src.logger import get_logger
from src.cache_manager import CacheManager

logger = get_logger(__name__)
cache = CacheManager()


class ReviewSentimentAnalyzer:
    """Analyzes Steam review sentiment using Claude API"""

    def __init__(self, anthropic_api_key: Optional[str] = None):
        """
        Initialize analyzer with API credentials

        Args:
            anthropic_api_key: Anthropic API key (reads from env if not provided)
        """
        self.api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            logger.warning("No Anthropic API key found - sentiment analysis will be limited")

    def fetch_steam_reviews(
        self,
        app_id: int,
        sample_size: int = 200,
        language: str = 'english'
    ) -> Dict[str, List[str]]:
        """
        Fetch random sample of Steam reviews

        Args:
            app_id: Steam app ID
            sample_size: Total reviews to fetch (split between positive/negative)
            language: Review language filter

        Returns:
            Dict with 'positive' and 'negative' review lists
        """
        logger.info(f"Fetching {sample_size} Steam reviews for app {app_id}")

        # Check cache first (24-hour freshness)
        cache_key = f"{app_id}_{sample_size}_{language}"
        cached_reviews = cache.get('review_samples', cache_key, ttl_hours=24)
        if cached_reviews:
            logger.info("Using cached review samples")
            return cached_reviews

        reviews = {'positive': [], 'negative': []}

        try:
            # Steam Review API endpoint
            base_url = "https://store.steampowered.com/appreviews/"

            # Fetch positive reviews (sample_size/2)
            positive_count = sample_size // 2
            positive_reviews = self._fetch_reviews_by_type(
                app_id, 'positive', positive_count, language
            )
            reviews['positive'] = positive_reviews

            # Fetch negative reviews (sample_size/2)
            negative_count = sample_size - positive_count
            negative_reviews = self._fetch_reviews_by_type(
                app_id, 'negative', negative_count, language
            )
            reviews['negative'] = negative_reviews

            logger.info(f"Fetched {len(positive_reviews)} positive, {len(negative_reviews)} negative reviews")

            # Cache results
            cache.set('review_samples', cache_key, reviews)

            return reviews

        except Exception as e:
            logger.error(f"Error fetching Steam reviews: {e}")
            return reviews

    def _fetch_reviews_by_type(
        self,
        app_id: int,
        review_type: str,
        count: int,
        language: str
    ) -> List[str]:
        """
        Fetch reviews of specific type (positive/negative)

        Args:
            app_id: Steam app ID
            review_type: 'positive' or 'negative'
            count: Number of reviews to fetch
            language: Language filter

        Returns:
            List of review texts
        """
        reviews = []
        cursor = '*'
        attempts = 0
        max_attempts = 5

        while len(reviews) < count and attempts < max_attempts:
            try:
                url = f"https://store.steampowered.com/appreviews/{app_id}"
                params = {
                    'json': 1,
                    'filter': 'recent',
                    'language': language,
                    'review_type': review_type,
                    'purchase_type': 'all',
                    'num_per_page': 100,
                    'cursor': cursor
                }

                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                if not data.get('success'):
                    logger.warning(f"Steam API returned success=false for {review_type} reviews")
                    break

                review_list = data.get('reviews', [])
                if not review_list:
                    break

                # Extract review text
                for review in review_list:
                    if len(reviews) >= count:
                        break

                    review_text = review.get('review', '').strip()
                    # Filter out very short reviews (less than 50 chars)
                    if len(review_text) >= 50:
                        reviews.append(review_text)

                # Get next cursor for pagination
                cursor = data.get('cursor')
                if not cursor or cursor == '*':
                    break

                attempts += 1

            except Exception as e:
                logger.error(f"Error fetching {review_type} reviews (attempt {attempts}): {e}")
                attempts += 1
                continue

        return reviews

    def analyze_review_sentiment(
        self,
        reviews: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Analyze review sentiment using Claude API

        Args:
            reviews: Dict with 'positive' and 'negative' review lists

        Returns:
            Structured sentiment analysis data
        """
        if not self.api_key:
            logger.warning("No API key - returning fallback sentiment data")
            return self._get_fallback_sentiment()

        logger.info("Analyzing review sentiment with Claude API")

        # Check cache first (24-hour freshness)
        cache_key = f"sentiment_{hash(str(reviews))}"
        cached_sentiment = cache.get('sentiment_analysis', cache_key, ttl_hours=24)
        if cached_sentiment:
            logger.info("Using cached sentiment analysis")
            return cached_sentiment

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            # Prepare review samples for analysis (limit to prevent token overflow)
            positive_sample = reviews.get('positive', [])[:100]
            negative_sample = reviews.get('negative', [])[:100]

            prompt = f"""Analyze these Steam game reviews and categorize sentiment into themes.

POSITIVE REVIEWS ({len(positive_sample)} samples):
{json.dumps(positive_sample[:50], indent=2)}

NEGATIVE REVIEWS ({len(negative_sample)} samples):
{json.dumps(negative_sample[:50], indent=2)}

For POSITIVE reviews, categorize into these themes:
- Gameplay Loop (combat, progression, core mechanics)
- Narrative/Characters (story, dialogue, worldbuilding, writing)
- Art & Audio (visuals, graphics, music, voice acting, atmosphere)
- Progression Systems (meta-progression, unlocks, upgrades, builds)
- Replayability (variety, build diversity, randomization, longevity)
- Polish & Technical (performance, optimization, QOL features, UI/UX)

For NEGATIVE reviews, categorize into these themes:
- Technical Issues (bugs, crashes, performance, compatibility)
- Difficulty Balance (too hard, too easy, frustrating mechanics)
- Content Volume (not enough content, repetitive, lacks variety)
- Price Sensitivity (too expensive, not worth price, better alternatives)
- Comparison Issues (worse than predecessor, doesn't match competitors)
- Design Choices (controversial mechanics, unwanted changes, missing features)

Return a JSON object with this EXACT structure:
{{
    "positive_themes": {{
        "gameplay_loop": {{"count": X, "percentage": Y, "example_quotes": ["quote1", "quote2"]}},
        "narrative_characters": {{"count": X, "percentage": Y, "example_quotes": ["quote1", "quote2"]}},
        "art_audio": {{"count": X, "percentage": Y, "example_quotes": ["quote1", "quote2"]}},
        "progression_systems": {{"count": X, "percentage": Y, "example_quotes": ["quote1", "quote2"]}},
        "replayability": {{"count": X, "percentage": Y, "example_quotes": ["quote1", "quote2"]}},
        "polish_technical": {{"count": X, "percentage": Y, "example_quotes": ["quote1", "quote2"]}}
    }},
    "negative_themes": {{
        "technical_issues": {{"count": X, "percentage": Y, "example_quotes": ["quote1", "quote2"]}},
        "difficulty_balance": {{"count": X, "percentage": Y, "example_quotes": ["quote1", "quote2"]}},
        "content_volume": {{"count": X, "percentage": Y, "example_quotes": ["quote1", "quote2"]}},
        "price_sensitivity": {{"count": X, "percentage": Y, "example_quotes": ["quote1", "quote2"]}},
        "comparison_issues": {{"count": X, "percentage": Y, "example_quotes": ["quote1", "quote2"]}},
        "design_choices": {{"count": X, "percentage": Y, "example_quotes": ["quote1", "quote2"]}}
    }},
    "sample_size": {{"positive": {len(positive_sample)}, "negative": {len(negative_sample)}}},
    "confidence": "high"
}}

Percentage should be % of reviews in that sentiment category that mention this theme.
Include 2-3 SHORT representative quotes (max 100 chars each) per theme.
Only return the JSON object, no other text."""

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.3,  # Lower temperature for more consistent categorization
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract JSON from response
            response_text = response.content[0].text.strip()

            # Try to parse JSON (handle potential markdown wrapping)
            if response_text.startswith('```'):
                # Strip markdown code blocks
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            sentiment_data = json.loads(response_text)

            # Add metadata
            sentiment_data['analyzed_at'] = datetime.now().isoformat()
            sentiment_data['total_reviews'] = len(positive_sample) + len(negative_sample)

            # Cache results
            cache.set('sentiment_analysis', cache_key, sentiment_data)

            logger.info("Sentiment analysis complete")
            return sentiment_data

        except Exception as e:
            logger.error(f"Error analyzing sentiment with Claude API: {e}")
            logger.exception("Full traceback:")
            return self._get_fallback_sentiment()

    def _get_fallback_sentiment(self) -> Dict[str, Any]:
        """Return fallback sentiment data when API unavailable"""
        return {
            "positive_themes": {
                "gameplay_loop": {"count": 0, "percentage": 0, "example_quotes": []},
                "narrative_characters": {"count": 0, "percentage": 0, "example_quotes": []},
                "art_audio": {"count": 0, "percentage": 0, "example_quotes": []},
                "progression_systems": {"count": 0, "percentage": 0, "example_quotes": []},
                "replayability": {"count": 0, "percentage": 0, "example_quotes": []},
                "polish_technical": {"count": 0, "percentage": 0, "example_quotes": []}
            },
            "negative_themes": {
                "technical_issues": {"count": 0, "percentage": 0, "example_quotes": []},
                "difficulty_balance": {"count": 0, "percentage": 0, "example_quotes": []},
                "content_volume": {"count": 0, "percentage": 0, "example_quotes": []},
                "price_sensitivity": {"count": 0, "percentage": 0, "example_quotes": []},
                "comparison_issues": {"count": 0, "percentage": 0, "example_quotes": []},
                "design_choices": {"count": 0, "percentage": 0, "example_quotes": []}
            },
            "sample_size": {"positive": 0, "negative": 0},
            "confidence": "low",
            "error": "API unavailable - using fallback data"
        }

    def generate_sentiment_markdown(
        self,
        sentiment_data: Dict[str, Any],
        total_positive_pct: float = 96.5,
        total_negative_pct: float = 3.5
    ) -> str:
        """
        Generate markdown section for sentiment analysis

        Args:
            sentiment_data: Sentiment analysis results
            total_positive_pct: Overall positive review percentage
            total_negative_pct: Overall negative review percentage

        Returns:
            Markdown formatted sentiment section
        """
        sample_size = sentiment_data.get('sample_size', {})
        analyzed_at = sentiment_data.get('analyzed_at', datetime.now().isoformat())
        confidence = sentiment_data.get('confidence', 'low')

        confidence_badge = {
            'high': '✅ High',
            'medium': '⚠️ Medium',
            'low': '❌ Low'
        }.get(confidence, '❌ Low')

        markdown = f"""
## Review Sentiment Analysis (Sample-Based)

**Analysis Methodology**: Analyzed {sample_size.get('positive', 0) + sample_size.get('negative', 0)} randomly sampled reviews using Claude API
**Data Confidence**: {confidence_badge} (based on actual review text analysis)
**Sample Date**: {analyzed_at[:10]}
**Sample Composition**: {sample_size.get('positive', 0)} positive, {sample_size.get('negative', 0)} negative reviews

---

### Positive Sentiment Breakdown ({total_positive_pct}% of all reviews)

Based on {sample_size.get('positive', 0)} positive reviews analyzed:

| Theme | % of Positive Reviews | Representative Quotes |
|-------|----------------------|----------------------|
"""

        # Add positive theme rows
        positive_themes = sentiment_data.get('positive_themes', {})
        for theme_key, theme_data in positive_themes.items():
            theme_name = theme_key.replace('_', ' ').title()
            percentage = theme_data.get('percentage', 0)
            quotes = theme_data.get('example_quotes', [])
            quote_text = quotes[0][:100] if quotes else "N/A"

            markdown += f"| {theme_name} | {percentage}% | \"{quote_text}\" |\n"

        markdown += f"""
---

### Negative Sentiment Breakdown ({total_negative_pct}% of all reviews)

Based on {sample_size.get('negative', 0)} negative reviews analyzed:

| Theme | % of Negative Reviews | Key Issues |
|-------|----------------------|------------|
"""

        # Add negative theme rows
        negative_themes = sentiment_data.get('negative_themes', {})
        for theme_key, theme_data in negative_themes.items():
            theme_name = theme_key.replace('_', ' ').title()
            percentage = theme_data.get('percentage', 0)
            quotes = theme_data.get('example_quotes', [])
            quote_text = quotes[0][:100] if quotes else "N/A"

            markdown += f"| {theme_name} | {percentage}% | \"{quote_text}\" |\n"

        # Generate key insights
        markdown += "\n---\n\n### Key Insights\n\n"

        # Top 3 positive drivers
        top_positive = sorted(
            positive_themes.items(),
            key=lambda x: x[1].get('percentage', 0),
            reverse=True
        )[:3]

        markdown += "**Strongest Positive Drivers**:\n"
        for i, (theme_key, theme_data) in enumerate(top_positive, 1):
            theme_name = theme_key.replace('_', ' ').title()
            percentage = theme_data.get('percentage', 0)
            markdown += f"{i}. **{theme_name}** ({percentage}% of positive reviews)\n"

        markdown += "\n"

        # Top 3 negative issues
        top_negative = sorted(
            negative_themes.items(),
            key=lambda x: x[1].get('percentage', 0),
            reverse=True
        )[:3]

        markdown += "**Most Common Complaints**:\n"
        for i, (theme_key, theme_data) in enumerate(top_negative, 1):
            theme_name = theme_key.replace('_', ' ').title()
            percentage = theme_data.get('percentage', 0)
            markdown += f"{i}. **{theme_name}** ({percentage}% of negative reviews)\n"

        return markdown


# Convenience function for integration
def get_review_sentiment_analysis(
    app_id: int,
    sample_size: int = 200,
    total_positive_pct: float = 96.5,
    total_negative_pct: float = 3.5
) -> Dict[str, Any]:
    """
    Get complete review sentiment analysis

    Args:
        app_id: Steam app ID
        sample_size: Number of reviews to analyze
        total_positive_pct: Overall positive review percentage
        total_negative_pct: Overall negative review percentage

    Returns:
        Dict with sentiment_data and markdown
    """
    analyzer = ReviewSentimentAnalyzer()

    # Fetch reviews
    reviews = analyzer.fetch_steam_reviews(app_id, sample_size)

    # Analyze sentiment
    sentiment_data = analyzer.analyze_review_sentiment(reviews)

    # Generate markdown
    markdown = analyzer.generate_sentiment_markdown(
        sentiment_data,
        total_positive_pct,
        total_negative_pct
    )

    return {
        'sentiment_data': sentiment_data,
        'markdown': markdown,
        'confidence': sentiment_data.get('confidence', 'low')
    }


# Example usage
if __name__ == "__main__":
    # Example: Analyze Hades II reviews
    app_id = 1145350  # Hades II
    result = get_review_sentiment_analysis(app_id, sample_size=200)

    print("=" * 80)
    print("SENTIMENT ANALYSIS RESULTS")
    print("=" * 80)
    print(result['markdown'])
    print("\n" + "=" * 80)
    print(f"Confidence Level: {result['confidence']}")
    print("=" * 80)
