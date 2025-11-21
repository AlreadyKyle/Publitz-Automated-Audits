"""
Algorithm Visibility Forecast Module

Predicts Steam algorithm behavior and discovery queue placement based on:
- Wishlist velocity
- Tag effectiveness
- Engagement metrics
- Quality signals

Classifies games into visibility tiers (1-4) and provides actionable path to improvement.
"""

from typing import Dict, Any, List, Tuple
import math


class VisibilityForecastAnalyzer:
    """Analyzes and predicts Steam algorithm visibility"""

    # Visibility tier thresholds (0-100 score)
    TIER_THRESHOLDS = {
        'tier_1': 85,  # Top 1% - Featured placement, Popular Upcoming
        'tier_2': 70,  # Top 10% - Regular discovery queues, occasional features
        'tier_3': 50,  # Top 30% - Standard discovery, genre-specific queues
        'tier_4': 0,   # Bottom 70% - Minimal algorithmic distribution
    }

    # Discovery queue impression estimates (daily)
    DISCOVERY_IMPRESSIONS = {
        'tier_1': {'main': 8000, 'genre': 2000, 'featured': 5000},
        'tier_2': {'main': 3000, 'genre': 800, 'featured': 0},
        'tier_3': {'main': 500, 'genre': 200, 'featured': 0},
        'tier_4': {'main': 50, 'genre': 50, 'featured': 0},
    }

    def __init__(self):
        """Initialize the visibility forecast analyzer"""
        pass

    def analyze_visibility(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        capsule_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze current visibility tier and forecast algorithm behavior

        Args:
            game_data: Game information including tags, genre
            sales_data: Sales and review data
            capsule_analysis: Capsule image analysis results

        Returns:
            Complete visibility forecast with tier, predictions, and path to improvement
        """
        # Calculate component scores
        wishlist_velocity_score = self._calculate_wishlist_velocity_score(sales_data)
        tag_effectiveness_score = self._calculate_tag_effectiveness_score(game_data, sales_data)
        engagement_score = self._calculate_engagement_score(sales_data)
        quality_score = self._calculate_quality_score(game_data, sales_data, capsule_analysis)

        # Calculate overall visibility score (weighted)
        overall_score = (
            (wishlist_velocity_score * 0.40) +   # Velocity is critical
            (tag_effectiveness_score * 0.25) +   # Tag placement matters
            (engagement_score * 0.20) +          # Engagement signals
            (quality_score * 0.15)               # Quality baseline
        )

        overall_score = round(overall_score, 1)

        # Determine current tier
        current_tier = self._get_tier_from_score(overall_score)

        # Get discovery queue predictions
        discovery_predictions = self._predict_discovery_queues(current_tier, overall_score)

        # Calculate feature eligibility
        feature_eligibility = self._calculate_feature_eligibility(overall_score, sales_data)

        # Identify path to next tier
        path_to_improvement = self._calculate_improvement_path(
            overall_score, current_tier, wishlist_velocity_score,
            tag_effectiveness_score, engagement_score, quality_score,
            sales_data, game_data
        )

        return {
            'overall_score': overall_score,
            'current_tier': current_tier,
            'tier_description': self._get_tier_description(current_tier),
            'component_scores': {
                'wishlist_velocity': round(wishlist_velocity_score, 1),
                'tag_effectiveness': round(tag_effectiveness_score, 1),
                'engagement': round(engagement_score, 1),
                'quality': round(quality_score, 1)
            },
            'discovery_predictions': discovery_predictions,
            'feature_eligibility': feature_eligibility,
            'improvement_path': path_to_improvement
        }

    def _calculate_wishlist_velocity_score(self, sales_data: Dict[str, Any]) -> float:
        """
        Calculate wishlist velocity score (0-100)

        Uses review velocity as proxy:
        - Review count and review score as signals
        - Estimated from review count patterns
        """
        reviews_total = sales_data.get('reviews_total', 0)
        review_score = sales_data.get('review_score', 75)

        # Estimate wishlist velocity from review count
        # Typical ratio: 1 review per 50-100 purchases, 1 purchase per 5-10 wishlists
        # So roughly 1 review per 250-1000 wishlists
        # Assume review_to_wishlist_ratio of 1:500 as middle ground

        estimated_wishlists = reviews_total * 500

        # Daily wishlist velocity tiers (estimated)
        # Top 1%: 100+ wishlists/day
        # Top 10%: 20-100 wishlists/day
        # Top 30%: 5-20 wishlists/day
        # Bottom 70%: <5 wishlists/day

        # For pre-launch or early launch, use review count as proxy
        if reviews_total >= 2000:
            # Tier 1 level
            base_score = 90
        elif reviews_total >= 500:
            # Tier 2 level
            base_score = 75
        elif reviews_total >= 100:
            # Tier 3 level
            base_score = 55
        elif reviews_total >= 20:
            # Lower Tier 3
            base_score = 45
        else:
            # Tier 4
            base_score = 30

        # Adjust for review score (quality signal)
        if review_score >= 90:
            quality_mult = 1.1
        elif review_score >= 80:
            quality_mult = 1.05
        elif review_score >= 70:
            quality_mult = 1.0
        else:
            quality_mult = 0.95

        return min(100, base_score * quality_mult)

    def _calculate_tag_effectiveness_score(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any]
    ) -> float:
        """
        Calculate tag effectiveness score (0-100)

        Factors:
        - Number of tags used
        - Tag relevance (generic vs specific)
        - Tag traffic potential
        """
        tags = game_data.get('tags', '')
        genres = game_data.get('genres', '')

        # Count tags (Steam allows ~20 tags)
        tag_list = [t.strip().lower() for t in str(tags).split(',') if t.strip()]
        genre_list = [g.strip().lower() for g in str(genres).split(',') if g.strip()]

        all_tags = set(tag_list + genre_list)
        tag_count = len(all_tags)

        # Base score from tag count
        if tag_count >= 15:
            base_score = 80
        elif tag_count >= 10:
            base_score = 65
        elif tag_count >= 5:
            base_score = 50
        else:
            base_score = 30

        # High-traffic tags (bonus points)
        high_traffic_tags = [
            'roguelike', 'roguelite', 'indie', 'rpg', 'action',
            'strategy', 'pixel art', 'deckbuilder', 'card game',
            'horror', 'multiplayer', '2d', '3d', 'singleplayer'
        ]

        high_traffic_count = sum(1 for tag in all_tags if tag in high_traffic_tags)
        high_traffic_bonus = min(15, high_traffic_count * 3)

        # Niche tags (good for targeting, but less traffic)
        niche_tags = [
            'detective', 'mystery', 'visual novel', 'dating sim',
            'management', 'colony sim', 'city builder', 'tower defense'
        ]

        niche_count = sum(1 for tag in all_tags if tag in niche_tags)
        niche_bonus = min(5, niche_count * 2)

        # Review count as engagement signal (tags working)
        reviews_total = sales_data.get('reviews_total', 0)
        if reviews_total > 500:
            engagement_bonus = 10
        elif reviews_total > 100:
            engagement_bonus = 5
        else:
            engagement_bonus = 0

        total_score = base_score + high_traffic_bonus + niche_bonus + engagement_bonus

        return min(100, total_score)

    def _calculate_engagement_score(self, sales_data: Dict[str, Any]) -> float:
        """
        Calculate engagement score (0-100)

        Factors:
        - Review count (absolute engagement)
        - Review score (quality of engagement)
        - Review velocity
        """
        reviews_total = sales_data.get('reviews_total', 0)
        review_score = sales_data.get('review_score', 75)

        # Review count contribution (70% weight)
        if reviews_total >= 1000:
            count_score = 90
        elif reviews_total >= 500:
            count_score = 75
        elif reviews_total >= 200:
            count_score = 60
        elif reviews_total >= 50:
            count_score = 45
        else:
            count_score = 25

        # Review score contribution (30% weight)
        if review_score >= 90:
            quality_score = 95
        elif review_score >= 80:
            quality_score = 80
        elif review_score >= 70:
            quality_score = 65
        elif review_score >= 60:
            quality_score = 50
        else:
            quality_score = 30

        engagement = (count_score * 0.7) + (quality_score * 0.3)

        return round(engagement, 1)

    def _calculate_quality_score(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        capsule_analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate quality score (0-100)

        Factors:
        - Review score
        - Capsule quality
        - Estimated refund rate (from review sentiment)
        """
        review_score = sales_data.get('review_score', 75)

        # Review score is primary quality signal (60% weight)
        if review_score >= 95:
            review_quality = 95
        elif review_score >= 90:
            review_quality = 85
        elif review_score >= 85:
            review_quality = 75
        elif review_score >= 80:
            review_quality = 65
        elif review_score >= 75:
            review_quality = 55
        elif review_score >= 70:
            review_quality = 45
        else:
            review_quality = 30

        # Capsule quality (40% weight)
        if capsule_analysis and capsule_analysis.get('overall_ctr_score'):
            capsule_score = capsule_analysis['overall_ctr_score'] * 10  # 0-10 scale to 0-100
        else:
            capsule_score = 60  # Neutral if no analysis

        quality = (review_quality * 0.6) + (capsule_score * 0.4)

        return round(quality, 1)

    def _get_tier_from_score(self, score: float) -> int:
        """Determine tier from overall score"""
        if score >= self.TIER_THRESHOLDS['tier_1']:
            return 1
        elif score >= self.TIER_THRESHOLDS['tier_2']:
            return 2
        elif score >= self.TIER_THRESHOLDS['tier_3']:
            return 3
        else:
            return 4

    def _get_tier_description(self, tier: int) -> str:
        """Get human-readable tier description"""
        descriptions = {
            1: "Top 1% - Featured Placement, Popular Upcoming, Maximum Discovery",
            2: "Top 10% - Regular Discovery Queues, Occasional Features",
            3: "Top 30% - Standard Discovery, Genre-Specific Queues",
            4: "Bottom 70% - Minimal Algorithmic Distribution"
        }
        return descriptions.get(tier, "Unknown")

    def _predict_discovery_queues(self, tier: int, score: float) -> Dict[str, Any]:
        """Predict discovery queue placement and impressions"""
        impressions = self.DISCOVERY_IMPRESSIONS[f'tier_{tier}']

        # Adjust impressions based on score within tier
        tier_min = self.TIER_THRESHOLDS.get(f'tier_{tier}', 0)
        tier_max = self.TIER_THRESHOLDS.get(f'tier_{tier - 1}', 100) if tier > 1 else 100

        # Score position within tier (0-1)
        if tier_max > tier_min:
            tier_position = (score - tier_min) / (tier_max - tier_min)
        else:
            tier_position = 0.5

        # Adjust impressions based on position in tier
        adjustment = 0.8 + (tier_position * 0.4)  # 0.8x to 1.2x

        adjusted_impressions = {
            'main': int(impressions['main'] * adjustment),
            'genre': int(impressions['genre'] * adjustment),
            'featured': int(impressions['featured'] * adjustment)
        }

        total_daily = sum(adjusted_impressions.values())

        return {
            'tier': tier,
            'daily_impressions': adjusted_impressions,
            'total_daily_impressions': total_daily,
            'weekly_impressions': total_daily * 7,
            'monthly_impressions': total_daily * 30,
            'queue_types': self._get_queue_types_for_tier(tier)
        }

    def _get_queue_types_for_tier(self, tier: int) -> List[str]:
        """Get which discovery queue types a tier qualifies for"""
        queues = {
            1: [
                "Main Discovery Queue (high frequency)",
                "Genre-Specific Queues",
                "Popular Upcoming (if pre-launch)",
                "Featured & Recommended",
                "New & Trending",
                "Top Sellers (if performing well)"
            ],
            2: [
                "Main Discovery Queue (medium frequency)",
                "Genre-Specific Queues",
                "New & Trending (occasionally)",
                "Recommended (for interested users)"
            ],
            3: [
                "Main Discovery Queue (low frequency)",
                "Genre-Specific Queues",
                "More Like This (related game pages)"
            ],
            4: [
                "Main Discovery Queue (rare)",
                "Genre-Specific Queues (minimal)",
                "Related Games (if tags match user history)"
            ]
        }
        return queues.get(tier, [])

    def _calculate_feature_eligibility(self, score: float, sales_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate eligibility for Steam features"""

        reviews_total = sales_data.get('reviews_total', 0)
        review_score = sales_data.get('review_score', 75)

        features = {}

        # Popular Upcoming (pre-launch feature)
        popular_upcoming_threshold = 72
        features['popular_upcoming'] = {
            'eligible': score >= popular_upcoming_threshold,
            'score_requirement': popular_upcoming_threshold,
            'your_score': score,
            'gap': max(0, popular_upcoming_threshold - score),
            'probability': min(100, max(0, (score - 60) * 5)) if score >= 60 else 0
        }

        # Featured Placement
        featured_threshold = 80
        features['featured_placement'] = {
            'eligible': score >= featured_threshold and reviews_total >= 50,
            'score_requirement': featured_threshold,
            'review_requirement': 50,
            'your_score': score,
            'your_reviews': reviews_total,
            'gap': max(0, featured_threshold - score),
            'probability': min(100, max(0, (score - 70) * 3)) if score >= 70 and reviews_total >= 50 else 0
        }

        # Daily Deal
        daily_deal_threshold = 75
        features['daily_deal'] = {
            'eligible': score >= daily_deal_threshold and reviews_total >= 100 and review_score >= 80,
            'requirements': {
                'score': daily_deal_threshold,
                'reviews': 100,
                'review_score': 80
            },
            'your_metrics': {
                'score': score,
                'reviews': reviews_total,
                'review_score': review_score
            },
            'probability': min(100, max(0, (score - 65) * 2)) if reviews_total >= 100 and review_score >= 80 else 0
        }

        # New & Trending
        trending_threshold = 70
        features['new_and_trending'] = {
            'eligible': score >= trending_threshold and reviews_total >= 20,
            'score_requirement': trending_threshold,
            'review_requirement': 20,
            'your_score': score,
            'your_reviews': reviews_total,
            'probability': min(100, max(0, (score - 60) * 4)) if reviews_total >= 20 else 0
        }

        return features

    def _calculate_improvement_path(
        self,
        current_score: float,
        current_tier: int,
        wishlist_velocity_score: float,
        tag_effectiveness_score: float,
        engagement_score: float,
        quality_score: float,
        sales_data: Dict[str, Any],
        game_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate actionable path to next tier"""

        # Determine next tier target
        if current_tier == 1:
            next_tier = 1
            target_score = 95  # Maintain/improve
            message = "You're in Tier 1! Focus on maintaining this elite status."
        else:
            next_tier = current_tier - 1
            target_score = self.TIER_THRESHOLDS[f'tier_{next_tier}']
            message = f"Path to Tier {next_tier}"

        points_needed = max(0, target_score - current_score)

        # Identify weakest areas (biggest improvement opportunities)
        component_gaps = {
            'wishlist_velocity': 100 - wishlist_velocity_score,
            'tag_effectiveness': 100 - tag_effectiveness_score,
            'engagement': 100 - engagement_score,
            'quality': 100 - quality_score
        }

        # Sort by gap (largest first)
        sorted_gaps = sorted(component_gaps.items(), key=lambda x: x[1], reverse=True)

        # Generate specific recommendations
        recommendations = []

        # Wishlist velocity recommendations
        if wishlist_velocity_score < 70:
            reviews_total = sales_data.get('reviews_total', 0)
            if reviews_total < 100:
                target_wishlists = 500
            elif reviews_total < 500:
                target_wishlists = 2500
            else:
                target_wishlists = 10000

            recommendations.append({
                'area': 'Wishlist Velocity',
                'current_score': wishlist_velocity_score,
                'impact': f"+{int((100 - wishlist_velocity_score) * 0.4)} points" if wishlist_velocity_score < 100 else "Maximized",
                'actions': [
                    f"Target {target_wishlists:,}+ wishlists in next 30 days",
                    "Run Steam Next Fest demo campaign",
                    "Launch Reddit/Discord community building",
                    "Contact 10-15 YouTubers/streamers for coverage"
                ],
                'priority': 'HIGH' if wishlist_velocity_score < 60 else 'MEDIUM'
            })

        # Tag effectiveness recommendations
        if tag_effectiveness_score < 75:
            tags = game_data.get('tags', '')
            tag_list = [t.strip() for t in str(tags).split(',') if t.strip()]

            recommendations.append({
                'area': 'Tag Effectiveness',
                'current_score': tag_effectiveness_score,
                'impact': f"+{int((100 - tag_effectiveness_score) * 0.25)} points",
                'actions': [
                    f"Add high-traffic tags (currently using {len(tag_list)} tags, target 15+)",
                    "Include: 'Roguelike', 'Pixel Art', 'Singleplayer' if applicable",
                    "Add niche targeting tags for your specific genre",
                    "Remove overly generic tags like 'Adventure' if not core"
                ],
                'priority': 'MEDIUM'
            })

        # Engagement recommendations
        if engagement_score < 70:
            reviews_total = sales_data.get('reviews_total', 0)

            recommendations.append({
                'area': 'Engagement',
                'current_score': engagement_score,
                'impact': f"+{int((100 - engagement_score) * 0.20)} points",
                'actions': [
                    f"Increase review count from {reviews_total} to {reviews_total + 200}+",
                    "Maintain 80%+ positive review score",
                    "Engage with community (respond to reviews, forums)",
                    "Regular content updates to boost engagement"
                ],
                'priority': 'MEDIUM' if reviews_total < 200 else 'LOW'
            })

        # Quality recommendations
        if quality_score < 75:
            review_score = sales_data.get('review_score', 75)

            recommendations.append({
                'area': 'Quality Signals',
                'current_score': quality_score,
                'impact': f"+{int((100 - quality_score) * 0.15)} points",
                'actions': [
                    f"Improve review score from {review_score}% to 85%+",
                    "Redesign capsule to score 8+/10",
                    "Address top negative review themes",
                    "Polish game based on player feedback"
                ],
                'priority': 'HIGH' if review_score < 75 else 'MEDIUM'
            })

        # Calculate projected tier with improvements
        projected_score = current_score
        if recommendations:
            # If top 2 recommendations are executed, estimate impact
            projected_score += sum(
                float(rec['impact'].split('+')[1].split()[0])
                for rec in recommendations[:2]
                if '+' in rec['impact']
            )

        projected_tier = self._get_tier_from_score(projected_score)

        # Estimate impression increase
        current_impressions = self.DISCOVERY_IMPRESSIONS[f'tier_{current_tier}']
        projected_impressions = self.DISCOVERY_IMPRESSIONS[f'tier_{projected_tier}']

        current_daily = current_impressions['main'] + current_impressions['genre'] + current_impressions['featured']
        projected_daily = projected_impressions['main'] + projected_impressions['genre'] + projected_impressions['featured']

        impression_increase = projected_daily - current_daily

        return {
            'current_tier': current_tier,
            'next_tier': next_tier,
            'target_score': target_score,
            'current_score': current_score,
            'points_needed': round(points_needed, 1),
            'message': message,
            'weakest_areas': [area for area, gap in sorted_gaps if gap > 20],
            'recommendations': recommendations,
            'projected_outcome': {
                'score_after_improvements': round(projected_score, 1),
                'tier_after_improvements': projected_tier,
                'impression_increase_daily': impression_increase,
                'impression_increase_monthly': impression_increase * 30
            }
        }
