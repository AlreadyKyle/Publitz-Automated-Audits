#!/usr/bin/env python3
"""
Game Performance Analyzer
Detects success levels and provides context for AI analysis
"""

from typing import Dict, Any, List


class GameAnalyzer:
    """Analyzes game performance to detect success levels"""

    def __init__(self):
        # Success thresholds
        self.REVIEW_THRESHOLDS = {
            'massive': 50000,      # 50k+ reviews = massive success
            'very_high': 20000,    # 20k+ reviews = very high engagement
            'high': 10000,         # 10k+ reviews = high engagement
            'strong': 5000,        # 5k+ reviews = strong engagement
            'moderate': 1000,      # 1k+ reviews = moderate engagement
            'low': 100             # <100 reviews = low engagement
        }

        self.SCORE_THRESHOLDS = {
            'exceptional': 95,     # 95%+ = exceptional quality
            'outstanding': 90,     # 90%+ = outstanding quality
            'very_good': 85,       # 85%+ = very good quality
            'good': 80,            # 80%+ = good quality
            'average': 70          # 70%+ = average quality
        }

        self.OWNER_THRESHOLDS = {
            'blockbuster': 10000000,   # 10M+ = blockbuster
            'major_hit': 5000000,      # 5M+ = major hit
            'hit': 1000000,            # 1M+ = hit game
            'successful': 500000,      # 500k+ = successful
            'moderate': 100000,        # 100k+ = moderate success
            'niche': 10000             # 10k+ = niche success
        }

    def analyze_success_level(self, game_data: Dict[str, Any], sales_data: Dict[str, Any], review_stats: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze game's success level based on multiple metrics

        Args:
            game_data: Game information from Steam
            sales_data: Sales and review data from SteamSpy
            review_stats: Review statistics including velocity data

        Returns:
            Dictionary with success analysis including:
            - overall_success: string (massive_success, highly_successful, successful, etc.)
            - engagement_level: based on review count
            - quality_level: based on review score
            - market_performance: based on owners
            - success_score: numeric 0-100
            - review_velocity: review momentum analysis
            - context_for_ai: string with analysis guidelines
        """
        # Extract metrics
        review_count = sales_data.get('reviews_total', 0)
        review_score = sales_data.get('review_score_raw', 0)
        owners_avg = sales_data.get('owners_avg', 0)

        # Extract velocity data if available
        velocity_score = review_stats.get('velocity_score', 0) if review_stats else 0
        velocity_status = review_stats.get('velocity_status', 'Unknown') if review_stats else 'Unknown'
        recent_reviews = review_stats.get('recent_reviews', 0) if review_stats else 0

        # Analyze each dimension
        engagement = self._analyze_engagement(review_count)
        quality = self._analyze_quality(review_score)
        market = self._analyze_market_performance(owners_avg)

        # Calculate overall success score (0-100)
        success_score = self._calculate_success_score(
            review_count, review_score, owners_avg
        )

        # Determine overall success level
        overall_success = self._determine_overall_success(
            engagement['level'],
            quality['level'],
            market['level'],
            success_score
        )

        # Analyze pricing (NEW)
        pricing_analysis = self._analyze_pricing(game_data, sales_data)

        # Analyze tag effectiveness (NEW)
        tag_analysis = self._analyze_tag_effectiveness(game_data, sales_data, engagement['level'], quality['level'])

        # Generate AI context
        ai_context = self._generate_ai_context(
            overall_success,
            engagement,
            quality,
            market,
            review_count,
            review_score,
            owners_avg,
            velocity_score,
            velocity_status,
            recent_reviews,
            game_data,
            pricing_analysis,
            tag_analysis
        )

        return {
            'overall_success': overall_success,
            'success_score': success_score,
            'engagement_level': engagement['level'],
            'engagement_description': engagement['description'],
            'quality_level': quality['level'],
            'quality_description': quality['description'],
            'market_performance': market['level'],
            'market_description': market['description'],
            'velocity_score': velocity_score,
            'velocity_status': velocity_status,
            'recent_reviews': recent_reviews,
            'pricing_analysis': pricing_analysis,
            'tag_analysis': tag_analysis,
            'context_for_ai': ai_context,
            'is_highly_successful': success_score >= 75,
            'is_successful': success_score >= 60,
            'needs_improvement': success_score < 40
        }

    def _analyze_engagement(self, review_count: int) -> Dict[str, str]:
        """Analyze engagement level based on review count"""
        if review_count >= self.REVIEW_THRESHOLDS['massive']:
            return {
                'level': 'massive',
                'description': f'Massive community engagement with {review_count:,} reviews'
            }
        elif review_count >= self.REVIEW_THRESHOLDS['very_high']:
            return {
                'level': 'very_high',
                'description': f'Very high community engagement with {review_count:,} reviews'
            }
        elif review_count >= self.REVIEW_THRESHOLDS['high']:
            return {
                'level': 'high',
                'description': f'High community engagement with {review_count:,} reviews'
            }
        elif review_count >= self.REVIEW_THRESHOLDS['strong']:
            return {
                'level': 'strong',
                'description': f'Strong community engagement with {review_count:,} reviews'
            }
        elif review_count >= self.REVIEW_THRESHOLDS['moderate']:
            return {
                'level': 'moderate',
                'description': f'Moderate community engagement with {review_count:,} reviews'
            }
        else:
            return {
                'level': 'low',
                'description': f'Limited community engagement with {review_count:,} reviews'
            }

    def _analyze_quality(self, review_score: float) -> Dict[str, str]:
        """Analyze quality level based on review score"""
        if review_score >= self.SCORE_THRESHOLDS['exceptional']:
            return {
                'level': 'exceptional',
                'description': f'Exceptional quality with {review_score:.1f}% positive reviews'
            }
        elif review_score >= self.SCORE_THRESHOLDS['outstanding']:
            return {
                'level': 'outstanding',
                'description': f'Outstanding quality with {review_score:.1f}% positive reviews'
            }
        elif review_score >= self.SCORE_THRESHOLDS['very_good']:
            return {
                'level': 'very_good',
                'description': f'Very good quality with {review_score:.1f}% positive reviews'
            }
        elif review_score >= self.SCORE_THRESHOLDS['good']:
            return {
                'level': 'good',
                'description': f'Good quality with {review_score:.1f}% positive reviews'
            }
        elif review_score >= self.SCORE_THRESHOLDS['average']:
            return {
                'level': 'average',
                'description': f'Average quality with {review_score:.1f}% positive reviews'
            }
        else:
            return {
                'level': 'below_average',
                'description': f'Below average quality with {review_score:.1f}% positive reviews'
            }

    def _analyze_market_performance(self, owners: int) -> Dict[str, str]:
        """Analyze market performance based on ownership"""
        if owners >= self.OWNER_THRESHOLDS['blockbuster']:
            return {
                'level': 'blockbuster',
                'description': f'Blockbuster performance with {owners:,} owners'
            }
        elif owners >= self.OWNER_THRESHOLDS['major_hit']:
            return {
                'level': 'major_hit',
                'description': f'Major hit with {owners:,} owners'
            }
        elif owners >= self.OWNER_THRESHOLDS['hit']:
            return {
                'level': 'hit',
                'description': f'Hit game with {owners:,} owners'
            }
        elif owners >= self.OWNER_THRESHOLDS['successful']:
            return {
                'level': 'successful',
                'description': f'Successful with {owners:,} owners'
            }
        elif owners >= self.OWNER_THRESHOLDS['moderate']:
            return {
                'level': 'moderate',
                'description': f'Moderate success with {owners:,} owners'
            }
        else:
            return {
                'level': 'niche',
                'description': f'Niche game with {owners:,} owners'
            }

    def _calculate_success_score(self, review_count: int, review_score: float, owners: int) -> int:
        """
        Calculate overall success score (0-100)

        Weighting:
        - Review Score: 40% (quality is most important)
        - Engagement (reviews): 30% (community validation)
        - Market Performance (owners): 30% (commercial success)
        """
        # Quality score (0-40 points)
        quality_score = (review_score / 100) * 40

        # Engagement score (0-30 points)
        if review_count >= 50000:
            engagement_score = 30
        elif review_count >= 20000:
            engagement_score = 27
        elif review_count >= 10000:
            engagement_score = 24
        elif review_count >= 5000:
            engagement_score = 20
        elif review_count >= 1000:
            engagement_score = 15
        elif review_count >= 100:
            engagement_score = 10
        else:
            engagement_score = 5

        # Market performance score (0-30 points)
        if owners >= 10000000:
            market_score = 30
        elif owners >= 5000000:
            market_score = 27
        elif owners >= 1000000:
            market_score = 24
        elif owners >= 500000:
            market_score = 20
        elif owners >= 100000:
            market_score = 15
        elif owners >= 10000:
            market_score = 10
        else:
            market_score = 5

        total_score = quality_score + engagement_score + market_score
        return int(total_score)

    def _determine_overall_success(
        self,
        engagement: str,
        quality: str,
        market: str,
        success_score: int
    ) -> str:
        """Determine overall success level"""
        if success_score >= 85:
            return 'massive_success'
        elif success_score >= 75:
            return 'highly_successful'
        elif success_score >= 65:
            return 'successful'
        elif success_score >= 50:
            return 'moderately_successful'
        elif success_score >= 35:
            return 'underperforming'
        else:
            return 'struggling'

    def _analyze_pricing(self, game_data: Dict[str, Any], sales_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze pricing using Price-to-Content Index

        Formula: Price / Median Hours = $/hour
        - Excellent: < $0.50/hour
        - Good: $0.50-$1/hour
        - Fair: $1-$2/hour
        - Poor: $2-$5/hour
        - Overpriced: > $5/hour
        """
        price = game_data.get('price_raw', 0) or sales_data.get('price_raw', 0)
        median_playtime_minutes = sales_data.get('median_playtime', 0)
        median_playtime_hours = median_playtime_minutes / 60 if median_playtime_minutes > 0 else 0

        # Calculate price-to-content index
        if median_playtime_hours > 0 and price > 0:
            price_per_hour = price / median_playtime_hours
        else:
            price_per_hour = 0

        # Determine value rating
        if price == 0:
            value_rating = "Free-to-Play"
            value_level = "free"
            recommendation = "N/A for F2P games"
        elif median_playtime_hours == 0:
            value_rating = "Insufficient playtime data"
            value_level = "unknown"
            recommendation = "Cannot assess value without playtime data"
        elif price_per_hour < 0.50:
            value_rating = "Excellent value"
            value_level = "excellent"
            recommendation = f"Great value at ${price_per_hour:.2f}/hour - pricing is very competitive"
        elif price_per_hour < 1.00:
            value_rating = "Good value"
            value_level = "good"
            recommendation = f"Good value at ${price_per_hour:.2f}/hour - pricing is fair"
        elif price_per_hour < 2.00:
            value_rating = "Fair value"
            value_level = "fair"
            recommendation = f"Fair value at ${price_per_hour:.2f}/hour - consider slight price reduction"
        elif price_per_hour < 5.00:
            value_rating = "Below average value"
            value_level = "poor"
            recommendation = f"${price_per_hour:.2f}/hour is high - consider 20-30% price reduction"
        else:
            value_rating = "Overpriced"
            value_level = "overpriced"
            recommendation = f"${price_per_hour:.2f}/hour is very high - significant price reduction recommended"

        return {
            'price': price,
            'median_hours': median_playtime_hours,
            'price_per_hour': price_per_hour,
            'value_rating': value_rating,
            'value_level': value_level,
            'recommendation': recommendation
        }

    def _analyze_tag_effectiveness(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        engagement_level: str,
        quality_level: str
    ) -> Dict[str, Any]:
        """
        Analyze tag effectiveness by comparing performance to tag category expectations

        Different tag categories (Indie, AAA, F2P, etc.) have different performance expectations.
        This analyzes if the game's performance matches what we'd expect for its tags.
        """
        tags = game_data.get('tags', sales_data.get('tags', []))
        if not tags:
            return {
                'effectiveness': 'unknown',
                'primary_category': 'Unknown',
                'expectation_match': 'unknown',
                'recommendation': 'No tag data available'
            }

        # Get top 5 tags
        top_tags = tags[:5] if isinstance(tags, list) else list(tags.keys())[:5]

        # Categorize game based on tags
        tag_category = self._categorize_by_tags(top_tags)

        # Expected performance for category
        expected_engagement = self._get_expected_engagement(tag_category)

        # Compare actual vs expected
        expectation_match = self._compare_to_expectations(
            engagement_level, quality_level, expected_engagement
        )

        # Generate recommendations
        if expectation_match == 'exceeding':
            effectiveness = 'highly_effective'
            recommendation = f"Tags are working exceptionally well for a {tag_category} game. " \
                           f"Consider leveraging similar tags in marketing campaigns."
        elif expectation_match == 'meeting':
            effectiveness = 'effective'
            recommendation = f"Tags are performing as expected for a {tag_category} game. " \
                           f"Tags are appropriate and discoverable."
        elif expectation_match == 'below':
            effectiveness = 'underperforming'
            recommendation = f"Performance is below expectations for a {tag_category} game. " \
                           f"Consider: 1) Adding more specific genre tags, 2) Reviewing tag relevance, " \
                           f"3) Analyzing top performers with similar tags for insights."
        else:
            effectiveness = 'unknown'
            recommendation = "Unable to assess tag effectiveness"

        return {
            'effectiveness': effectiveness,
            'primary_category': tag_category,
            'top_tags': top_tags,
            'expectation_match': expectation_match,
            'expected_engagement': expected_engagement,
            'actual_engagement': engagement_level,
            'recommendation': recommendation
        }

    def _categorize_by_tags(self, tags: List[str]) -> str:
        """Categorize game by its primary tags"""
        tags_lower = [t.lower() if isinstance(t, str) else str(t).lower() for t in tags]

        # Check for major categories
        if any(tag in tags_lower for tag in ['free to play', 'f2p', 'free']):
            return 'Free-to-Play'
        elif any(tag in tags_lower for tag in ['indie', 'casual']):
            return 'Indie'
        elif any(tag in tags_lower for tag in ['aaa', 'action', 'fps', 'multiplayer', 'mmo']):
            return 'AAA/Mainstream'
        elif any(tag in tags_lower for tag in ['strategy', 'simulation', 'management']):
            return 'Strategy/Simulation'
        elif any(tag in tags_lower for tag in ['rpg', 'adventure', 'story rich']):
            return 'RPG/Adventure'
        elif any(tag in tags_lower for tag in ['puzzle', 'platformer', 'arcade']):
            return 'Casual/Puzzle'
        else:
            return 'General'

    def _get_expected_engagement(self, category: str) -> str:
        """Get expected engagement level for a category"""
        expectations = {
            'Free-to-Play': 'very_high',  # F2P games typically have high engagement
            'AAA/Mainstream': 'very_high',  # AAA games should have high engagement
            'Indie': 'moderate',  # Indie games vary widely
            'Strategy/Simulation': 'high',  # Strategy games have dedicated audiences
            'RPG/Adventure': 'high',  # RPGs typically have engaged audiences
            'Casual/Puzzle': 'moderate',  # Casual games have variable engagement
            'General': 'moderate'
        }
        return expectations.get(category, 'moderate')

    def _compare_to_expectations(
        self,
        actual_engagement: str,
        quality_level: str,
        expected_engagement: str
    ) -> str:
        """Compare actual performance to expectations"""
        # Map engagement levels to numeric scores for comparison
        engagement_scores = {
            'massive': 6,
            'very_high': 5,
            'high': 4,
            'strong': 3,
            'moderate': 2,
            'low': 1
        }

        actual_score = engagement_scores.get(actual_engagement, 2)
        expected_score = engagement_scores.get(expected_engagement, 2)

        # Adjust for quality (high quality games should exceed expectations)
        quality_bonus = 1 if quality_level in ['exceptional', 'outstanding', 'very_good'] else 0
        adjusted_actual = actual_score + quality_bonus

        if adjusted_actual > expected_score + 1:
            return 'exceeding'
        elif adjusted_actual >= expected_score:
            return 'meeting'
        else:
            return 'below'

    def _generate_ai_context(
        self,
        overall_success: str,
        engagement: Dict,
        quality: Dict,
        market: Dict,
        review_count: int,
        review_score: float,
        owners: int,
        velocity_score: float = 0,
        velocity_status: str = 'Unknown',
        recent_reviews: int = 0,
        game_data: Dict = None,
        pricing_analysis: Dict = None,
        tag_analysis: Dict = None
    ) -> str:
        """Generate context string for AI prompts"""
        context_parts = []

        # Overall assessment
        if overall_success in ['massive_success', 'highly_successful']:
            context_parts.append(
                f"⚠️ IMPORTANT: This game is {overall_success.replace('_', ' ').upper()}. "
                f"Do NOT suggest major fixes or imply failure. Focus on OPTIMIZATION and "
                f"maintaining success, not problem-solving."
            )

        # Review velocity context (NEW)
        if velocity_score > 0:
            context_parts.append(
                f"📊 Review Momentum: {velocity_status} "
                f"({recent_reviews} reviews in last 30 days = {velocity_score*100:.1f}% of total). "
                f"{'This shows ACTIVE GROWTH - game is gaining traction.' if velocity_score > 0.03 else ''}"
                f"{'Game is in steady state - focus on retention and conversion.' if 0.01 < velocity_score <= 0.03 else ''}"
                f"{'Review rate is declining - may need marketing push or content update.' if velocity_score <= 0.01 else ''}"
            )

        # Steam Deck readiness context (NEW)
        if game_data and 'steam_deck_compatibility' in game_data:
            deck_data = game_data['steam_deck_compatibility']
            readiness_level = deck_data.get('readiness_level', 'Unknown')
            readiness_score = deck_data.get('readiness_score', 0)

            if readiness_score >= 60:
                context_parts.append(
                    f"🎮 Steam Deck: {readiness_level} compatibility ({readiness_score}/100). "
                    f"{deck_data.get('summary', '')} This is POSITIVE for 2025 market reach."
                )
            else:
                context_parts.append(
                    f"⚠ Steam Deck: {readiness_level} compatibility ({readiness_score}/100). "
                    f"{deck_data.get('summary', '')} Consider: {', '.join(deck_data.get('issues', [])[:2])}"
                )

        # Price-to-Content Index context (NEW)
        if pricing_analysis:
            value_level = pricing_analysis.get('value_level', 'unknown')
            if value_level in ['excellent', 'good']:
                context_parts.append(
                    f"💰 Pricing: {pricing_analysis.get('value_rating', 'N/A')} "
                    f"(${pricing_analysis.get('price_per_hour', 0):.2f}/hour for {pricing_analysis.get('median_hours', 0):.1f} hours). "
                    f"{pricing_analysis.get('recommendation', '')}"
                )
            elif value_level in ['poor', 'overpriced']:
                context_parts.append(
                    f"⚠ Pricing: {pricing_analysis.get('value_rating', 'N/A')} "
                    f"(${pricing_analysis.get('price_per_hour', 0):.2f}/hour is high). "
                    f"{pricing_analysis.get('recommendation', '')} This may impact sales velocity."
                )
            elif value_level == 'fair':
                context_parts.append(
                    f"💰 Pricing: {pricing_analysis.get('value_rating', 'N/A')} "
                    f"(${pricing_analysis.get('price_per_hour', 0):.2f}/hour). "
                    f"{pricing_analysis.get('recommendation', '')}"
                )

        # Tag Effectiveness context (NEW)
        if tag_analysis:
            effectiveness = tag_analysis.get('effectiveness', 'unknown')
            category = tag_analysis.get('primary_category', 'Unknown')
            expectation_match = tag_analysis.get('expectation_match', 'unknown')

            if effectiveness == 'highly_effective':
                context_parts.append(
                    f"🏷️ Tags: Highly effective for {category} category. "
                    f"Tags: {', '.join(tag_analysis.get('top_tags', [])[:3])}. "
                    f"{tag_analysis.get('recommendation', '')}"
                )
            elif effectiveness == 'effective':
                context_parts.append(
                    f"🏷️ Tags: Working well for {category} category. "
                    f"Performance is meeting expectations. Tags are appropriate."
                )
            elif effectiveness == 'underperforming':
                context_parts.append(
                    f"⚠ Tags: Underperforming for {category} category. "
                    f"Expected {tag_analysis.get('expected_engagement', 'N/A')} engagement, "
                    f"got {tag_analysis.get('actual_engagement', 'N/A')}. "
                    f"{tag_analysis.get('recommendation', '')}"
                )

        # Engagement context
        if engagement['level'] in ['massive', 'very_high', 'high']:
            context_parts.append(
                f"✓ Community Engagement: {engagement['description']}. "
                f"This indicates STRONG discoverability and tag effectiveness. "
                f"Do not flag engagement or discoverability as issues."
            )
        elif engagement['level'] == 'low':
            context_parts.append(
                f"⚠ Community Engagement: {engagement['description']}. "
                f"This may indicate discoverability or marketing issues worth addressing."
            )

        # Quality context
        if quality['level'] in ['exceptional', 'outstanding', 'very_good']:
            context_parts.append(
                f"✓ Quality Level: {quality['description']}. "
                f"The game is well-received. Focus on maintaining quality and expanding reach."
            )
        elif quality['level'] in ['below_average']:
            context_parts.append(
                f"⚠ Quality Level: {quality['description']}. "
                f"Quality improvements should be a priority."
            )

        # Market performance context
        if market['level'] in ['blockbuster', 'major_hit', 'hit']:
            context_parts.append(
                f"✓ Market Performance: {market['description']}. "
                f"Commercial success is strong. Revenue estimates should be treated as MINIMUMS."
            )

        # Analysis guidelines
        context_parts.append(
            "\n📊 ANALYSIS GUIDELINES:\n"
            f"- Success Score: {overall_success.replace('_', ' ').title()}\n"
        )

        if overall_success in ['massive_success', 'highly_successful']:
            context_parts.append(
                "- Approach: OPTIMIZATION not PROBLEM-SOLVING\n"
                "- Tag Effectiveness: Clearly WORKING (high engagement proves it)\n"
                "- KPI Status: Most KPIs should show GREEN/WORKING\n"
                "- Recommendations: Focus on scaling, not fixing\n"
            )
        elif overall_success in ['successful', 'moderately_successful']:
            context_parts.append(
                "- Approach: BALANCED - acknowledge success AND opportunities\n"
                "- Tag Effectiveness: Generally working but room for optimization\n"
                "- KPI Status: Mix of working and opportunities\n"
                "- Recommendations: Incremental improvements to scale up\n"
            )
        else:
            context_parts.append(
                "- Approach: IMPROVEMENT-FOCUSED - identify issues and solutions\n"
                "- Tag Effectiveness: May need review and optimization\n"
                "- KPI Status: Likely areas needing attention\n"
                "- Recommendations: Actionable fixes to improve performance\n"
            )

        return '\n\n'.join(context_parts)

    def get_performance_context(self, game_data: Dict[str, Any], sales_data: Dict[str, Any]) -> str:
        """
        Get a concise performance context string for AI prompts

        This is a simpler version of analyze_success_level that returns
        just the context string.
        """
        analysis = self.analyze_success_level(game_data, sales_data)
        return analysis['context_for_ai']
