#!/usr/bin/env python3
"""
Game Performance Analyzer
Detects success levels and provides context for AI analysis
"""

from typing import Dict, Any


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
            game_data
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
        game_data: Dict = None
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
