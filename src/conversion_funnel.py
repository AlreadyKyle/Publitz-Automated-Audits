"""
Conversion Funnel Analysis Module

Estimates and analyzes the 4-stage Steam conversion funnel:
1. Capsule Impression → Store Page Visit (Capsule CTR)
2. Store Page Visit → Wishlist Add (Wishlist Conversion)
3. Wishlist → Purchase (Purchase Conversion)
4. Purchase → Review (Review Ratio)

Provides genre benchmarks, optimization opportunities, and revenue projections.
"""

from typing import Dict, Any, List, Tuple
import json


class ConversionFunnelAnalyzer:
    """Analyzes Steam conversion funnel with genre-specific benchmarks"""

    # Genre-specific benchmark modifiers (multipliers applied to base rates)
    GENRE_MODIFIERS = {
        # High-converting genres
        'roguelike': {'capsule_ctr': 1.3, 'wishlist_conv': 1.2, 'purchase_conv': 1.1, 'review_ratio': 1.4},
        'roguelite': {'capsule_ctr': 1.3, 'wishlist_conv': 1.2, 'purchase_conv': 1.1, 'review_ratio': 1.4},
        'deckbuilder': {'capsule_ctr': 1.2, 'wishlist_conv': 1.3, 'purchase_conv': 1.2, 'review_ratio': 1.5},
        'card game': {'capsule_ctr': 1.2, 'wishlist_conv': 1.3, 'purchase_conv': 1.2, 'review_ratio': 1.5},

        # Medium-converting genres
        'rpg': {'capsule_ctr': 1.1, 'wishlist_conv': 1.1, 'purchase_conv': 1.0, 'review_ratio': 1.2},
        'strategy': {'capsule_ctr': 1.0, 'wishlist_conv': 1.1, 'purchase_conv': 1.0, 'review_ratio': 1.3},
        'simulation': {'capsule_ctr': 1.0, 'wishlist_conv': 1.0, 'purchase_conv': 0.95, 'review_ratio': 1.1},
        'puzzle': {'capsule_ctr': 1.1, 'wishlist_conv': 1.0, 'purchase_conv': 0.9, 'review_ratio': 1.0},

        # Lower-converting genres
        'action': {'capsule_ctr': 0.9, 'wishlist_conv': 0.9, 'purchase_conv': 0.95, 'review_ratio': 0.9},
        'adventure': {'capsule_ctr': 0.85, 'wishlist_conv': 0.9, 'purchase_conv': 0.9, 'review_ratio': 0.8},
        'casual': {'capsule_ctr': 0.8, 'wishlist_conv': 0.85, 'purchase_conv': 0.8, 'review_ratio': 0.7},

        # Niche genres
        'horror': {'capsule_ctr': 1.2, 'wishlist_conv': 1.1, 'purchase_conv': 0.9, 'review_ratio': 1.3},
        'detective': {'capsule_ctr': 1.0, 'wishlist_conv': 1.0, 'purchase_conv': 0.95, 'review_ratio': 1.2},
        'mystery': {'capsule_ctr': 1.0, 'wishlist_conv': 1.0, 'purchase_conv': 0.95, 'review_ratio': 1.2},
        'visual novel': {'capsule_ctr': 0.9, 'wishlist_conv': 1.1, 'purchase_conv': 1.0, 'review_ratio': 1.4},
        'dating sim': {'capsule_ctr': 0.9, 'wishlist_conv': 1.2, 'purchase_conv': 1.1, 'review_ratio': 1.3},
    }

    # Base conversion rates (industry averages)
    BASE_RATES = {
        'capsule_ctr': {
            'excellent': 0.045,  # 4.5% - Top 10%
            'good': 0.030,       # 3.0% - Above average
            'average': 0.020,    # 2.0% - Average
            'poor': 0.010,       # 1.0% - Below average
        },
        'wishlist_conv': {
            'excellent': 0.38,   # 38% - Top 10%
            'good': 0.28,        # 28% - Above average
            'average': 0.20,     # 20% - Average
            'poor': 0.12,        # 12% - Below average
        },
        'purchase_conv': {
            'excellent': 0.24,   # 24% - Top 10%
            'good': 0.16,        # 16% - Above average
            'average': 0.12,     # 12% - Average
            'poor': 0.08,        # 8% - Below average
        },
        'review_ratio': {
            'excellent': 0.045,  # 4.5% - High engagement
            'good': 0.025,       # 2.5% - Above average
            'average': 0.015,    # 1.5% - Average
            'poor': 0.008,       # 0.8% - Low engagement
        }
    }

    def __init__(self):
        """Initialize the conversion funnel analyzer"""
        pass

    def analyze_funnel(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        capsule_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze the complete conversion funnel for a game

        Args:
            game_data: Game information including genre, tags
            sales_data: Sales and review data
            capsule_analysis: Capsule image analysis results

        Returns:
            Complete funnel analysis with benchmarks and projections
        """
        # Extract genre for modifiers
        genre = self._extract_primary_genre(game_data)
        genre_modifier = self.GENRE_MODIFIERS.get(genre.lower(), {
            'capsule_ctr': 1.0, 'wishlist_conv': 1.0,
            'purchase_conv': 1.0, 'review_ratio': 1.0
        })

        # Calculate each stage of the funnel
        capsule_ctr = self._estimate_capsule_ctr(game_data, capsule_analysis, genre_modifier)
        wishlist_conv = self._estimate_wishlist_conversion(game_data, sales_data, genre_modifier)
        purchase_conv = self._estimate_purchase_conversion(game_data, sales_data, genre_modifier)
        review_ratio = self._estimate_review_ratio(sales_data, genre_modifier)

        # Get genre benchmarks
        benchmarks = self._get_genre_benchmarks(genre, genre_modifier)

        # Calculate projections
        projections = self._calculate_projections(
            capsule_ctr, wishlist_conv, purchase_conv, review_ratio, game_data
        )

        # Identify optimization opportunities
        optimizations = self._identify_optimizations(
            capsule_ctr, wishlist_conv, purchase_conv, review_ratio,
            benchmarks, projections, game_data
        )

        return {
            'funnel_stages': {
                'capsule_ctr': capsule_ctr,
                'wishlist_conversion': wishlist_conv,
                'purchase_conversion': purchase_conv,
                'review_ratio': review_ratio
            },
            'genre': genre,
            'genre_benchmarks': benchmarks,
            'projections': projections,
            'optimizations': optimizations,
            'overall_efficiency': self._calculate_overall_efficiency(
                capsule_ctr, wishlist_conv, purchase_conv, review_ratio, benchmarks
            )
        }

    def _extract_primary_genre(self, game_data: Dict[str, Any]) -> str:
        """Extract primary genre from game data"""
        genres_raw = game_data.get('genres', '')
        tags_raw = game_data.get('tags', '')

        # Handle genres as either list or string
        if isinstance(genres_raw, list):
            genres = ', '.join(genres_raw).lower() if genres_raw else ''
        else:
            genres = str(genres_raw).lower() if genres_raw else ''

        # Handle tags as either list or string
        if isinstance(tags_raw, list):
            tags = ', '.join(tags_raw).lower() if tags_raw else ''
        else:
            tags = str(tags_raw).lower() if tags_raw else ''

        # Check for specific high-priority genres first
        priority_genres = ['roguelike', 'roguelite', 'deckbuilder', 'card game']
        for genre in priority_genres:
            if genre in genres or genre in tags:
                return genre

        # Check other genres
        for genre in self.GENRE_MODIFIERS.keys():
            if genre in genres or genre in tags:
                return genre

        # Default to first genre or 'indie'
        if genres:
            first_genre = genres.split(',')[0].strip()
            return first_genre if first_genre else 'indie'

        return 'indie'

    def _estimate_capsule_ctr(
        self,
        game_data: Dict[str, Any],
        capsule_analysis: Dict[str, Any],
        genre_modifier: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Estimate capsule click-through rate (Impression → Visit)

        Factors:
        - Capsule quality score (if available)
        - Tag effectiveness
        - Genre baseline
        """
        base_rate = self.BASE_RATES['capsule_ctr']['average']

        # Factor 1: Capsule quality (40% weight)
        if capsule_analysis and capsule_analysis.get('overall_ctr_score'):
            quality_score = capsule_analysis['overall_ctr_score'] / 10.0  # 0-1 scale
            quality_multiplier = 0.5 + (quality_score * 1.0)  # 0.5x to 1.5x
        else:
            quality_multiplier = 1.0  # Neutral if no analysis

        # Factor 2: Genre modifier (30% weight)
        genre_mult = genre_modifier.get('capsule_ctr', 1.0)

        # Factor 3: Tag effectiveness proxy (30% weight)
        # More reviews = better tag placement historically
        reviews_total = game_data.get('reviews_total', 0) if isinstance(game_data.get('reviews_total'), int) else 0
        if reviews_total > 1000:
            tag_multiplier = 1.2
        elif reviews_total > 500:
            tag_multiplier = 1.1
        elif reviews_total > 100:
            tag_multiplier = 1.0
        else:
            tag_multiplier = 0.9

        # Combined calculation
        estimated_ctr = base_rate * (
            (quality_multiplier * 0.4) + (genre_mult * 0.3) + (tag_multiplier * 0.3)
        ) / (0.4 + 0.3 + 0.3)  # Weighted average

        # Determine performance tier
        tier = self._get_performance_tier(estimated_ctr, 'capsule_ctr')
        benchmark = self.BASE_RATES['capsule_ctr'][tier]

        return {
            'rate': round(estimated_ctr, 4),
            'percentage': round(estimated_ctr * 100, 2),
            'tier': tier,
            'benchmark': round(benchmark, 4),
            'benchmark_percentage': round(benchmark * 100, 2),
            'vs_benchmark': 'above' if estimated_ctr > benchmark else 'below' if estimated_ctr < benchmark else 'at',
            'factors': {
                'capsule_quality': quality_multiplier,
                'genre_fit': genre_mult,
                'tag_effectiveness': tag_multiplier
            }
        }

    def _estimate_wishlist_conversion(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        genre_modifier: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Estimate wishlist conversion rate (Visit → Wishlist)

        Factors:
        - Review score (quality signal)
        - Price positioning
        - Genre baseline
        """
        base_rate = self.BASE_RATES['wishlist_conv']['average']

        # Factor 1: Review score (50% weight)
        # FIX: Use review_score_raw (numeric) instead of review_score (string)
        review_score_raw = sales_data.get('review_score_raw', sales_data.get('review_score', 75))
        try:
            review_score = float(review_score_raw) if review_score_raw is not None else 75
        except (ValueError, TypeError):
            review_score = 75

        if review_score >= 90:
            quality_mult = 1.3
        elif review_score >= 80:
            quality_mult = 1.15
        elif review_score >= 70:
            quality_mult = 1.0
        else:
            quality_mult = 0.85

        # Factor 2: Price positioning (30% weight)
        price_str = game_data.get('price', '$19.99')
        try:
            price = float(str(price_str).replace('$', '').replace(',', ''))
            if price < 10:
                price_mult = 1.2  # Low price = higher conversion
            elif price < 20:
                price_mult = 1.1
            elif price < 30:
                price_mult = 1.0
            else:
                price_mult = 0.9
        except:
            price_mult = 1.0

        # Factor 3: Genre modifier (20% weight)
        genre_mult = genre_modifier.get('wishlist_conv', 1.0)

        # Combined calculation
        estimated_conv = base_rate * (
            (quality_mult * 0.5) + (price_mult * 0.3) + (genre_mult * 0.2)
        )

        tier = self._get_performance_tier(estimated_conv, 'wishlist_conv')
        benchmark = self.BASE_RATES['wishlist_conv'][tier]

        return {
            'rate': round(estimated_conv, 4),
            'percentage': round(estimated_conv * 100, 2),
            'tier': tier,
            'benchmark': round(benchmark, 4),
            'benchmark_percentage': round(benchmark * 100, 2),
            'vs_benchmark': 'above' if estimated_conv > benchmark else 'below' if estimated_conv < benchmark else 'at',
            'factors': {
                'review_quality': quality_mult,
                'price_positioning': price_mult,
                'genre_fit': genre_mult
            }
        }

    def _estimate_purchase_conversion(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        genre_modifier: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Estimate purchase conversion rate (Wishlist → Purchase)

        Factors:
        - Review score (quality/trust signal)
        - Price point
        - Launch quality (review count as proxy)
        """
        base_rate = self.BASE_RATES['purchase_conv']['average']

        # Factor 1: Review score (40% weight)
        # FIX: Use review_score_raw (numeric) instead of review_score (string)
        review_score_raw = sales_data.get('review_score_raw', sales_data.get('review_score', 75))
        try:
            review_score = float(review_score_raw) if review_score_raw is not None else 75
        except (ValueError, TypeError):
            review_score = 75

        if review_score >= 85:
            quality_mult = 1.3
        elif review_score >= 75:
            quality_mult = 1.1
        elif review_score >= 65:
            quality_mult = 1.0
        else:
            quality_mult = 0.8

        # Factor 2: Price (35% weight)
        price_str = game_data.get('price', '$19.99')
        try:
            price = float(str(price_str).replace('$', '').replace(',', ''))
            if price < 15:
                price_mult = 1.2
            elif price < 25:
                price_mult = 1.0
            else:
                price_mult = 0.85
        except:
            price_mult = 1.0

        # Factor 3: Genre modifier (25% weight)
        genre_mult = genre_modifier.get('purchase_conv', 1.0)

        # Combined calculation
        estimated_conv = base_rate * (
            (quality_mult * 0.4) + (price_mult * 0.35) + (genre_mult * 0.25)
        )

        tier = self._get_performance_tier(estimated_conv, 'purchase_conv')
        benchmark = self.BASE_RATES['purchase_conv'][tier]

        return {
            'rate': round(estimated_conv, 4),
            'percentage': round(estimated_conv * 100, 2),
            'tier': tier,
            'benchmark': round(benchmark, 4),
            'benchmark_percentage': round(benchmark * 100, 2),
            'vs_benchmark': 'above' if estimated_conv > benchmark else 'below' if estimated_conv < benchmark else 'at',
            'factors': {
                'review_quality': quality_mult,
                'price_point': price_mult,
                'genre_fit': genre_mult
            }
        }

    def _estimate_review_ratio(
        self,
        sales_data: Dict[str, Any],
        genre_modifier: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Estimate review ratio (Purchase → Review)

        Factors:
        - Review count (engagement proxy)
        - Genre (some genres review more)
        """
        base_rate = self.BASE_RATES['review_ratio']['average']

        # Factor 1: Review engagement (60% weight)
        reviews_total = sales_data.get('reviews_total', 0)
        if reviews_total > 1000:
            engagement_mult = 1.4
        elif reviews_total > 500:
            engagement_mult = 1.2
        elif reviews_total > 100:
            engagement_mult = 1.0
        else:
            engagement_mult = 0.8

        # Factor 2: Genre modifier (40% weight)
        genre_mult = genre_modifier.get('review_ratio', 1.0)

        # Combined calculation
        estimated_ratio = base_rate * (
            (engagement_mult * 0.6) + (genre_mult * 0.4)
        )

        tier = self._get_performance_tier(estimated_ratio, 'review_ratio')
        benchmark = self.BASE_RATES['review_ratio'][tier]

        return {
            'rate': round(estimated_ratio, 4),
            'percentage': round(estimated_ratio * 100, 2),
            'tier': tier,
            'benchmark': round(benchmark, 4),
            'benchmark_percentage': round(benchmark * 100, 2),
            'vs_benchmark': 'above' if estimated_ratio > benchmark else 'below' if estimated_ratio < benchmark else 'at',
            'factors': {
                'engagement_level': engagement_mult,
                'genre_fit': genre_mult
            }
        }

    def _get_performance_tier(self, rate: float, rate_type: str) -> str:
        """Determine which performance tier a rate falls into"""
        tiers = self.BASE_RATES[rate_type]

        if rate >= tiers['excellent'] * 0.9:  # Within 10% of excellent
            return 'excellent'
        elif rate >= tiers['good'] * 0.95:    # Within 5% of good
            return 'good'
        elif rate >= tiers['average'] * 0.9:  # Within 10% of average
            return 'average'
        else:
            return 'poor'

    def _get_genre_benchmarks(self, genre: str, genre_modifier: Dict[str, float]) -> Dict[str, Any]:
        """Get genre-specific benchmarks"""
        return {
            'genre': genre,
            'capsule_ctr_avg': round(self.BASE_RATES['capsule_ctr']['average'] * genre_modifier.get('capsule_ctr', 1.0), 4),
            'wishlist_conv_avg': round(self.BASE_RATES['wishlist_conv']['average'] * genre_modifier.get('wishlist_conv', 1.0), 4),
            'purchase_conv_avg': round(self.BASE_RATES['purchase_conv']['average'] * genre_modifier.get('purchase_conv', 1.0), 4),
            'review_ratio_avg': round(self.BASE_RATES['review_ratio']['average'] * genre_modifier.get('review_ratio', 1.0), 4)
        }

    def _calculate_projections(
        self,
        capsule_ctr: Dict[str, Any],
        wishlist_conv: Dict[str, Any],
        purchase_conv: Dict[str, Any],
        review_ratio: Dict[str, Any],
        game_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate funnel projections at different impression volumes"""

        price_str = game_data.get('price', '$19.99')
        try:
            price = float(str(price_str).replace('$', '').replace(',', ''))
        except:
            price = 19.99

        projections = {}

        for impressions in [10000, 50000, 100000, 250000, 500000]:
            visits = int(impressions * capsule_ctr['rate'])
            wishlists = int(visits * wishlist_conv['rate'])
            purchases = int(wishlists * purchase_conv['rate'])
            reviews = int(purchases * review_ratio['rate'])
            revenue = purchases * price

            projections[f'{impressions // 1000}k_impressions'] = {
                'impressions': impressions,
                'visits': visits,
                'wishlists': wishlists,
                'purchases': purchases,
                'reviews': reviews,
                'revenue': round(revenue, 2)
            }

        return projections

    def _identify_optimizations(
        self,
        capsule_ctr: Dict[str, Any],
        wishlist_conv: Dict[str, Any],
        purchase_conv: Dict[str, Any],
        review_ratio: Dict[str, Any],
        benchmarks: Dict[str, Any],
        projections: Dict[str, Any],
        game_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify optimization opportunities with impact projections"""

        opportunities = []

        # Use 100K impressions as baseline for impact calculations
        baseline = projections.get('100k_impressions', {})
        baseline_wishlists = baseline.get('wishlists', 0)
        baseline_purchases = baseline.get('purchases', 0)
        baseline_revenue = baseline.get('revenue', 0)

        price_str = game_data.get('price', '$19.99')
        try:
            price = float(str(price_str).replace('$', '').replace(',', ''))
        except:
            price = 19.99

        # Opportunity 1: Capsule CTR improvement
        if capsule_ctr['vs_benchmark'] == 'below':
            target_ctr = benchmarks['capsule_ctr_avg']
            current_ctr = capsule_ctr['rate']
            improvement = target_ctr - current_ctr

            # Calculate impact
            new_visits = int(100000 * target_ctr)
            current_visits = int(100000 * current_ctr)
            additional_visits = new_visits - current_visits
            additional_wishlists = int(additional_visits * wishlist_conv['rate'])
            additional_purchases = int(additional_wishlists * purchase_conv['rate'])
            additional_revenue = additional_purchases * price

            opportunities.append({
                'stage': 'Capsule CTR',
                'current': capsule_ctr['percentage'],
                'target': round(target_ctr * 100, 2),
                'improvement_points': round(improvement * 100, 2),
                'impact': {
                    'additional_wishlists': additional_wishlists,
                    'additional_purchases': additional_purchases,
                    'additional_revenue': round(additional_revenue, 2)
                },
                'priority': 'HIGH' if improvement > 0.01 else 'MEDIUM',
                'tactics': [
                    'Redesign capsule to improve clarity and contrast',
                    'A/B test capsule variants',
                    'Optimize for small thumbnail sizes',
                    'Increase text readability by 30-40%'
                ]
            })

        # Opportunity 2: Wishlist conversion improvement
        if wishlist_conv['vs_benchmark'] == 'below':
            target_conv = benchmarks['wishlist_conv_avg']
            current_conv = wishlist_conv['rate']
            improvement = target_conv - current_conv

            visits = baseline.get('visits', 0)
            additional_wishlists = int(visits * improvement)
            additional_purchases = int(additional_wishlists * purchase_conv['rate'])
            additional_revenue = additional_purchases * price

            opportunities.append({
                'stage': 'Wishlist Conversion',
                'current': wishlist_conv['percentage'],
                'target': round(target_conv * 100, 2),
                'improvement_points': round(improvement * 100, 2),
                'impact': {
                    'additional_wishlists': additional_wishlists,
                    'additional_purchases': additional_purchases,
                    'additional_revenue': round(additional_revenue, 2)
                },
                'priority': 'HIGH' if improvement > 0.05 else 'MEDIUM',
                'tactics': [
                    'Improve trailer hook (first 10 seconds)',
                    'Optimize screenshot sequence',
                    'Enhance store description clarity',
                    'Add compelling social proof (review quotes)'
                ]
            })

        # Opportunity 3: Purchase conversion improvement
        if purchase_conv['vs_benchmark'] == 'below':
            target_conv = benchmarks['purchase_conv_avg']
            current_conv = purchase_conv['rate']
            improvement = target_conv - current_conv

            wishlists = baseline.get('wishlists', 0)
            additional_purchases = int(wishlists * improvement)
            additional_revenue = additional_purchases * price

            opportunities.append({
                'stage': 'Purchase Conversion',
                'current': purchase_conv['percentage'],
                'target': round(target_conv * 100, 2),
                'improvement_points': round(improvement * 100, 2),
                'impact': {
                    'additional_purchases': additional_purchases,
                    'additional_revenue': round(additional_revenue, 2)
                },
                'priority': 'HIGH' if additional_revenue > 1000 else 'MEDIUM',
                'tactics': [
                    'Launch with strong review score (85%+ target)',
                    'Optimize pricing strategy',
                    'Build pre-launch hype and community',
                    'Ensure polished, bug-free launch'
                ]
            })

        return sorted(opportunities, key=lambda x: x['impact'].get('additional_revenue', 0), reverse=True)

    def _calculate_overall_efficiency(
        self,
        capsule_ctr: Dict[str, Any],
        wishlist_conv: Dict[str, Any],
        purchase_conv: Dict[str, Any],
        review_ratio: Dict[str, Any],
        benchmarks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall funnel efficiency score"""

        # Calculate efficiency vs benchmarks
        ctr_efficiency = capsule_ctr['rate'] / benchmarks['capsule_ctr_avg']
        wish_efficiency = wishlist_conv['rate'] / benchmarks['wishlist_conv_avg']
        purch_efficiency = purchase_conv['rate'] / benchmarks['purchase_conv_avg']
        review_efficiency = review_ratio['rate'] / benchmarks['review_ratio_avg']

        # Overall efficiency (weighted average)
        overall = (
            (ctr_efficiency * 0.3) +      # Capsule CTR is critical
            (wish_efficiency * 0.35) +    # Wishlist conv is most important
            (purch_efficiency * 0.25) +   # Purchase conv matters
            (review_efficiency * 0.1)     # Review ratio is nice-to-have
        )

        # Convert to 100-point scale
        efficiency_score = int(overall * 100)

        if efficiency_score >= 110:
            tier = 'Excellent - Top 10%'
        elif efficiency_score >= 95:
            tier = 'Good - Above Average'
        elif efficiency_score >= 85:
            tier = 'Average'
        else:
            tier = 'Below Average - Needs Optimization'

        return {
            'score': efficiency_score,
            'tier': tier,
            'stage_efficiencies': {
                'capsule_ctr': round(ctr_efficiency, 2),
                'wishlist_conversion': round(wish_efficiency, 2),
                'purchase_conversion': round(purch_efficiency, 2),
                'review_ratio': round(review_efficiency, 2)
            }
        }
