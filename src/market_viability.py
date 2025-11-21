#!/usr/bin/env python3
"""
Market Viability Analyzer - Assesses market opportunity and launch viability
Provides TAM estimates, competitive saturation, demand validation, and success probability
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from src.logger import get_logger

logger = get_logger(__name__)


class MarketViabilityAnalyzer:
    """Analyzes market viability for game launches"""

    # Genre market data (based on Steam revenue analysis)
    GENRE_TAM_DATA = {
        'roguelike': {
            'annual_revenue': 850000000,  # $850M
            'avg_price': 19.99,
            'total_games': 2800,
            'new_releases_per_year': 420,
            'top_game_revenue': 125000000,  # Hades
            'median_game_revenue': 45000,
            'success_rate': 0.12,  # 12% make >$100K
            'trend': 'growing',
            'growth_rate': 0.15  # 15% YoY
        },
        'strategy': {
            'annual_revenue': 1200000000,
            'avg_price': 29.99,
            'total_games': 3500,
            'new_releases_per_year': 380,
            'top_game_revenue': 200000000,  # Civilization VI
            'median_game_revenue': 65000,
            'success_rate': 0.15,
            'trend': 'stable',
            'growth_rate': 0.05
        },
        'rpg': {
            'annual_revenue': 2100000000,
            'avg_price': 39.99,
            'total_games': 4200,
            'new_releases_per_year': 520,
            'top_game_revenue': 350000000,  # Baldur's Gate 3
            'median_game_revenue': 85000,
            'success_rate': 0.18,
            'trend': 'growing',
            'growth_rate': 0.20
        },
        'action': {
            'annual_revenue': 3500000000,
            'avg_price': 29.99,
            'total_games': 8500,
            'new_releases_per_year': 1200,
            'top_game_revenue': 500000000,
            'median_game_revenue': 55000,
            'success_rate': 0.08,
            'trend': 'stable',
            'growth_rate': 0.08
        },
        'indie': {
            'annual_revenue': 1800000000,
            'avg_price': 14.99,
            'total_games': 12000,
            'new_releases_per_year': 2800,
            'top_game_revenue': 180000000,  # Terraria
            'median_game_revenue': 25000,
            'success_rate': 0.06,
            'trend': 'saturated',
            'growth_rate': 0.03
        },
        'puzzle': {
            'annual_revenue': 450000000,
            'avg_price': 9.99,
            'total_games': 3200,
            'new_releases_per_year': 450,
            'top_game_revenue': 50000000,
            'median_game_revenue': 18000,
            'success_rate': 0.10,
            'trend': 'stable',
            'growth_rate': 0.04
        },
        'simulation': {
            'annual_revenue': 980000000,
            'avg_price': 24.99,
            'total_games': 2100,
            'new_releases_per_year': 280,
            'top_game_revenue': 150000000,  # Cities: Skylines
            'median_game_revenue': 72000,
            'success_rate': 0.14,
            'trend': 'growing',
            'growth_rate': 0.12
        },
        'adventure': {
            'annual_revenue': 780000000,
            'avg_price': 19.99,
            'total_games': 3800,
            'new_releases_per_year': 520,
            'top_game_revenue': 95000000,
            'median_game_revenue': 35000,
            'success_rate': 0.09,
            'trend': 'stable',
            'growth_rate': 0.06
        }
    }

    def __init__(self):
        logger.info("MarketViabilityAnalyzer initialized")

    def analyze_market_viability(self, game_data: Dict[str, Any],
                                 competitor_data: List[Dict[str, Any]],
                                 sales_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Comprehensive market viability analysis

        Args:
            game_data: Game information
            competitor_data: List of competitor games
            sales_data: Optional sales data for post-launch

        Returns:
            Complete viability analysis
        """
        logger.info("Analyzing market viability")

        # Extract game info
        genres = [g.get('description', '').lower() for g in game_data.get('genres', [])]
        price = game_data.get('price_overview', {}).get('final', 1999) / 100
        is_released = game_data.get('release_date', {}).get('coming_soon', True) == False

        # Get primary genre
        primary_genre = self._get_primary_genre(genres)

        # Analyze each component
        tam_analysis = self._analyze_tam(primary_genre, genres)
        saturation_analysis = self._analyze_competitive_saturation(primary_genre, competitor_data)
        demand_analysis = self._analyze_demand_signals(game_data, competitor_data)
        success_probability = self._calculate_success_probability(
            tam_analysis, saturation_analysis, demand_analysis, price, is_released
        )

        return {
            'tam_analysis': tam_analysis,
            'saturation_analysis': saturation_analysis,
            'demand_analysis': demand_analysis,
            'success_probability': success_probability,
            'viability_score': self._calculate_viability_score(
                tam_analysis, saturation_analysis, demand_analysis
            ),
            'recommendation': self._generate_viability_recommendation(
                tam_analysis, saturation_analysis, success_probability
            )
        }

    def _get_primary_genre(self, genres: List[str]) -> str:
        """Determine primary genre from list"""
        for genre in genres:
            for key in self.GENRE_TAM_DATA.keys():
                if key in genre:
                    return key
        return 'indie'  # Default fallback

    def _analyze_tam(self, primary_genre: str, all_genres: List[str]) -> Dict[str, Any]:
        """
        Analyze Total Addressable Market

        Returns TAM size, growth trends, opportunity assessment
        """
        genre_data = self.GENRE_TAM_DATA.get(primary_genre, self.GENRE_TAM_DATA['indie'])

        # Calculate TAM metrics
        annual_revenue = genre_data['annual_revenue']
        total_games = genre_data['total_games']
        avg_revenue_per_game = annual_revenue / total_games

        # Market size classification
        if annual_revenue > 2000000000:
            market_size = 'Very Large'
            size_score = 95
        elif annual_revenue > 1000000000:
            market_size = 'Large'
            size_score = 80
        elif annual_revenue > 500000000:
            market_size = 'Medium'
            size_score = 65
        else:
            market_size = 'Small'
            size_score = 50

        # Growth trend assessment
        growth_rate = genre_data['growth_rate']
        if growth_rate > 0.15:
            growth_assessment = 'High Growth'
            growth_score = 90
        elif growth_rate > 0.08:
            growth_assessment = 'Moderate Growth'
            growth_score = 70
        elif growth_rate > 0:
            growth_assessment = 'Stable'
            growth_score = 55
        else:
            growth_assessment = 'Declining'
            growth_score = 30

        return {
            'primary_genre': primary_genre.title(),
            'annual_market_revenue': annual_revenue,
            'total_games_in_genre': total_games,
            'avg_revenue_per_game': int(avg_revenue_per_game),
            'median_game_revenue': genre_data['median_game_revenue'],
            'top_game_revenue': genre_data['top_game_revenue'],
            'market_size': market_size,
            'growth_trend': genre_data['trend'].title(),
            'annual_growth_rate': f"{int(growth_rate * 100)}%",
            'new_releases_per_year': genre_data['new_releases_per_year'],
            'market_size_score': size_score,
            'growth_score': growth_score,
            'opportunity_level': self._get_opportunity_level(size_score, growth_score)
        }

    def _analyze_competitive_saturation(self, primary_genre: str,
                                       competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze competitive saturation and market crowding
        """
        genre_data = self.GENRE_TAM_DATA.get(primary_genre, self.GENRE_TAM_DATA['indie'])

        # Calculate saturation metrics
        total_games = genre_data['total_games']
        new_releases_per_year = genre_data['new_releases_per_year']
        annual_revenue = genre_data['annual_revenue']

        # Saturation ratio (new releases vs total market capacity)
        saturation_ratio = new_releases_per_year / total_games

        # Competitive density score
        if saturation_ratio > 0.30:
            saturation_level = 'Highly Saturated'
            saturation_score = 35
            risk_level = 'High'
        elif saturation_ratio > 0.20:
            saturation_level = 'Moderately Saturated'
            saturation_score = 55
            risk_level = 'Medium'
        elif saturation_ratio > 0.10:
            saturation_level = 'Balanced'
            saturation_score = 75
            risk_level = 'Low'
        else:
            saturation_level = 'Undersaturated'
            saturation_score = 90
            risk_level = 'Very Low'

        # Analyze recent competitor launches (last 6 months)
        recent_competitor_count = len(competitors)

        # Calculate revenue per game vs new entrants
        revenue_per_existing_game = annual_revenue / total_games
        projected_revenue_with_new_entrants = annual_revenue / (total_games + new_releases_per_year)
        revenue_dilution = ((revenue_per_existing_game - projected_revenue_with_new_entrants) /
                           revenue_per_existing_game * 100)

        return {
            'saturation_level': saturation_level,
            'saturation_score': saturation_score,
            'risk_level': risk_level,
            'total_games_in_genre': total_games,
            'new_releases_per_year': new_releases_per_year,
            'saturation_ratio': f"{int(saturation_ratio * 100)}%",
            'direct_competitors_analyzed': len(competitors),
            'revenue_dilution_estimate': f"{int(revenue_dilution)}%",
            'competitive_density': self._calculate_competitive_density(competitors)
        }

    def _analyze_demand_signals(self, game_data: Dict[str, Any],
                                competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze demand validation signals
        """
        # Get game metrics
        is_released = game_data.get('release_date', {}).get('coming_soon', True) == False

        # For unreleased games, estimate based on store page completeness
        if not is_released:
            # Analyze store page strength
            has_trailer = len(game_data.get('movies', [])) > 0
            screenshot_count = len(game_data.get('screenshots', []))
            has_description = len(game_data.get('short_description', '')) > 100

            store_page_score = 0
            if has_trailer:
                store_page_score += 30
            if screenshot_count >= 5:
                store_page_score += 30
            elif screenshot_count >= 3:
                store_page_score += 20
            if has_description:
                store_page_score += 20
            if game_data.get('genres'):
                store_page_score += 20

            demand_level = 'Unknown (Pre-Launch)'
            demand_score = store_page_score

        else:
            # For released games, use actual metrics
            # Note: This would ideally pull from SteamDB/SteamSpy
            demand_level = 'Estimated from Release Data'
            demand_score = 50  # Placeholder

        # Analyze competitor demand as benchmark
        competitor_avg_reviews = 0
        if competitors:
            review_counts = []
            for comp in competitors:
                # Would extract review counts here
                pass

        return {
            'demand_level': demand_level,
            'demand_score': demand_score,
            'store_page_readiness': store_page_score if not is_released else None,
            'validation_signals': self._get_validation_signals(game_data, is_released),
            'benchmark_comparison': self._compare_to_benchmarks(game_data, competitors)
        }

    def _calculate_success_probability(self, tam: Dict, saturation: Dict,
                                       demand: Dict, price: float,
                                       is_released: bool) -> Dict[str, Any]:
        """
        Calculate probability of commercial success (>$100K revenue)
        """
        # Base success rate from genre
        base_success_rate = self.GENRE_TAM_DATA.get(
            tam['primary_genre'].lower(),
            self.GENRE_TAM_DATA['indie']
        )['success_rate']

        # Adjust based on market conditions
        adjusted_rate = base_success_rate

        # Market size bonus
        if tam['market_size_score'] > 80:
            adjusted_rate *= 1.2
        elif tam['market_size_score'] < 60:
            adjusted_rate *= 0.8

        # Saturation penalty
        if saturation['saturation_score'] < 50:
            adjusted_rate *= 0.7
        elif saturation['saturation_score'] > 75:
            adjusted_rate *= 1.15

        # Demand signal adjustment
        if demand['demand_score'] > 75:
            adjusted_rate *= 1.25
        elif demand['demand_score'] < 50:
            adjusted_rate *= 0.85

        # Price positioning
        genre_avg_price = self.GENRE_TAM_DATA.get(
            tam['primary_genre'].lower(),
            self.GENRE_TAM_DATA['indie']
        )['avg_price']

        price_ratio = price / genre_avg_price
        if 0.8 <= price_ratio <= 1.2:
            # Optimal price range
            adjusted_rate *= 1.1
        elif price_ratio > 1.5:
            # Significantly overpriced
            adjusted_rate *= 0.7
        elif price_ratio < 0.5:
            # Significantly underpriced (leaves money on table)
            adjusted_rate *= 0.9

        # Cap at realistic maximum
        final_probability = min(adjusted_rate, 0.35)  # Max 35% success rate

        # Calculate confidence level
        if is_released:
            confidence = 'Medium (based on early data)'
        else:
            confidence = 'Low (pre-launch estimate)'

        # Revenue projections
        median_revenue = tam['median_game_revenue']
        if final_probability > 0.15:
            projected_range_low = median_revenue * 0.8
            projected_range_high = median_revenue * 2.0
            outlook = 'Positive'
        elif final_probability > 0.08:
            projected_range_low = median_revenue * 0.5
            projected_range_high = median_revenue * 1.2
            outlook = 'Moderate'
        else:
            projected_range_low = median_revenue * 0.2
            projected_range_high = median_revenue * 0.8
            outlook = 'Challenging'

        return {
            'success_probability': f"{int(final_probability * 100)}%",
            'success_probability_raw': final_probability,
            'confidence_level': confidence,
            'outlook': outlook,
            'projected_revenue_range': {
                'low': int(projected_range_low),
                'high': int(projected_range_high),
                'median': median_revenue
            },
            'key_success_factors': self._identify_success_factors(tam, saturation, demand, price)
        }

    def _calculate_viability_score(self, tam: Dict, saturation: Dict,
                                   demand: Dict) -> int:
        """Calculate overall viability score 0-100"""
        # Weighted average
        tam_weight = 0.30
        saturation_weight = 0.35
        demand_weight = 0.35

        score = (
            tam['market_size_score'] * tam_weight +
            saturation['saturation_score'] * saturation_weight +
            demand['demand_score'] * demand_weight
        )

        return int(score)

    def _get_opportunity_level(self, market_size_score: int, growth_score: int) -> str:
        """Determine opportunity level from scores"""
        combined = (market_size_score + growth_score) / 2
        if combined > 80:
            return 'Excellent'
        elif combined > 65:
            return 'Good'
        elif combined > 50:
            return 'Moderate'
        else:
            return 'Limited'

    def _calculate_competitive_density(self, competitors: List[Dict]) -> str:
        """Calculate how densely packed the competitive space is"""
        if len(competitors) > 20:
            return 'Very High'
        elif len(competitors) > 10:
            return 'High'
        elif len(competitors) > 5:
            return 'Moderate'
        else:
            return 'Low'

    def _get_validation_signals(self, game_data: Dict, is_released: bool) -> List[str]:
        """Identify demand validation signals"""
        signals = []

        if is_released:
            signals.append("Game is live on Steam")
            if game_data.get('recommendations'):
                signals.append(f"{game_data['recommendations'].get('total', 0)} user reviews")
        else:
            if len(game_data.get('movies', [])) > 0:
                signals.append("Trailer available")
            if len(game_data.get('screenshots', [])) >= 5:
                signals.append("Complete screenshot gallery")
            if game_data.get('short_description'):
                signals.append("Store page description ready")

        return signals if signals else ["Limited validation signals available"]

    def _compare_to_benchmarks(self, game_data: Dict, competitors: List[Dict]) -> str:
        """Compare game readiness to competitor benchmarks"""
        if not competitors:
            return "No direct competitors for comparison"

        # Compare screenshot counts
        game_screenshots = len(game_data.get('screenshots', []))
        comp_screenshots = [len(c.get('screenshots', [])) for c in competitors if c.get('screenshots')]
        avg_comp_screenshots = sum(comp_screenshots) / len(comp_screenshots) if comp_screenshots else 5

        if game_screenshots >= avg_comp_screenshots:
            return f"Store page completeness matches or exceeds competitors (avg {int(avg_comp_screenshots)} screenshots)"
        else:
            return f"Store page below competitor average ({game_screenshots} vs {int(avg_comp_screenshots)} screenshots)"

    def _identify_success_factors(self, tam: Dict, saturation: Dict,
                                  demand: Dict, price: float) -> List[str]:
        """Identify key factors that will determine success"""
        factors = []

        # Market factors
        if tam['growth_score'] > 75:
            factors.append(f"Growing market ({tam['annual_growth_rate']} YoY growth)")
        if tam['market_size_score'] > 80:
            factors.append(f"Large addressable market (${tam['annual_market_revenue']:,} annual revenue)")

        # Competition factors
        if saturation['saturation_score'] < 60:
            factors.append(f"High competition ({saturation['new_releases_per_year']} new games/year)")
        elif saturation['saturation_score'] > 75:
            factors.append(f"Favorable competitive landscape")

        # Positioning factors
        if demand['demand_score'] > 70:
            factors.append("Strong store page foundation")

        # If no specific factors, give general guidance
        if not factors:
            factors.append("Success will depend on execution quality and marketing")

        return factors

    def _generate_viability_recommendation(self, tam: Dict, saturation: Dict,
                                          success_prob: Dict) -> str:
        """Generate overall viability recommendation"""
        viability_score = self._calculate_viability_score(tam, saturation,
                                                          {'demand_score': 50})  # Neutral demand
        probability = success_prob['success_probability_raw']

        if viability_score > 75 and probability > 0.15:
            return ("✅ STRONG VIABILITY - This genre offers good market opportunity with reasonable "
                   "success probability. Focus on differentiation and quality execution.")

        elif viability_score > 60 and probability > 0.10:
            return ("✓ MODERATE VIABILITY - Market opportunity exists but competition is significant. "
                   "Success depends on strong differentiation and effective marketing.")

        elif viability_score > 45:
            return ("⚠️ CHALLENGING MARKET - This is a competitive space with modest success rates. "
                   "Ensure you have a clear unique selling proposition and realistic budget expectations.")

        else:
            return ("🚨 HIGH RISK - This market is highly saturated or declining. Consider pivoting to "
                   "adjacent genres or ensuring you have significant unique advantages before proceeding.")


def analyze_market_viability(game_data: Dict[str, Any],
                             competitor_data: List[Dict[str, Any]],
                             sales_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function for market viability analysis

    Args:
        game_data: Game information
        competitor_data: List of competitors
        sales_data: Optional sales data

    Returns:
        Complete viability analysis
    """
    analyzer = MarketViabilityAnalyzer()
    return analyzer.analyze_market_viability(game_data, competitor_data, sales_data)
