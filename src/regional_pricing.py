#!/usr/bin/env python3
"""
Regional Pricing Analyzer - Price parity and localization analysis
Provides data-driven regional pricing recommendations
"""

from typing import Dict, List, Any, Optional
import requests
from src.logger import get_logger
from src.cache_manager import get_cache

logger = get_logger(__name__)


class RegionalPricingAnalyzer:
    """Analyze regional pricing and provide localization recommendations"""

    # Steam supported regions with purchasing power parity data
    REGIONS = {
        'US': {'name': 'United States', 'currency': 'USD', 'ppp_multiplier': 1.0, 'market_size': 'very_large'},
        'EU': {'name': 'European Union', 'currency': 'EUR', 'ppp_multiplier': 0.92, 'market_size': 'very_large'},
        'GB': {'name': 'United Kingdom', 'currency': 'GBP', 'ppp_multiplier': 0.78, 'market_size': 'large'},
        'CA': {'name': 'Canada', 'currency': 'CAD', 'ppp_multiplier': 1.28, 'market_size': 'medium'},
        'AU': {'name': 'Australia', 'currency': 'AUD', 'ppp_multiplier': 1.45, 'market_size': 'medium'},
        'JP': {'name': 'Japan', 'currency': 'JPY', 'ppp_multiplier': 110.0, 'market_size': 'large'},
        'CN': {'name': 'China', 'currency': 'CNY', 'ppp_multiplier': 0.55, 'market_size': 'very_large'},
        'BR': {'name': 'Brazil', 'currency': 'BRL', 'ppp_multiplier': 0.45, 'market_size': 'large'},
        'RU': {'name': 'Russia', 'currency': 'RUB', 'ppp_multiplier': 0.40, 'market_size': 'large'},
        'IN': {'name': 'India', 'currency': 'INR', 'ppp_multiplier': 0.30, 'market_size': 'very_large'},
        'MX': {'name': 'Mexico', 'currency': 'MXN', 'ppp_multiplier': 0.50, 'market_size': 'medium'},
        'AR': {'name': 'Argentina', 'currency': 'ARS', 'ppp_multiplier': 0.25, 'market_size': 'small'},
        'TR': {'name': 'Turkey', 'currency': 'TRY', 'ppp_multiplier': 0.35, 'market_size': 'medium'},
        'KR': {'name': 'South Korea', 'currency': 'KRW', 'ppp_multiplier': 1150.0, 'market_size': 'medium'},
    }

    # Language localization ROI data
    LANGUAGE_ROI = {
        'en': {'language': 'English', 'cost': 0, 'market_reach': 100, 'roi_multiplier': 1.0},
        'zh-CN': {'language': 'Simplified Chinese', 'cost': 2000, 'market_reach': 35, 'roi_multiplier': 3.5},
        'ja': {'language': 'Japanese', 'cost': 2500, 'market_reach': 10, 'roi_multiplier': 2.8},
        'ko': {'language': 'Korean', 'cost': 2000, 'market_reach': 5, 'roi_multiplier': 2.2},
        'de': {'language': 'German', 'cost': 1500, 'market_reach': 8, 'roi_multiplier': 2.0},
        'fr': {'language': 'French', 'cost': 1500, 'market_reach': 7, 'roi_multiplier': 1.8},
        'es': {'language': 'Spanish', 'cost': 1500, 'market_reach': 12, 'roi_multiplier': 2.5},
        'pt-BR': {'language': 'Portuguese (Brazil)', 'cost': 1200, 'market_reach': 6, 'roi_multiplier': 2.3},
        'ru': {'language': 'Russian', 'cost': 1200, 'market_reach': 9, 'roi_multiplier': 2.1},
        'pl': {'language': 'Polish', 'cost': 1000, 'market_reach': 3, 'roi_multiplier': 1.6},
        'tr': {'language': 'Turkish', 'cost': 1000, 'market_reach': 3, 'roi_multiplier': 1.5},
    }

    def __init__(self):
        self.cache = get_cache()
        logger.info("RegionalPricingAnalyzer initialized")

    def analyze_pricing(self, base_price_usd: float,
                       current_regional_prices: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Analyze regional pricing strategy

        Args:
            base_price_usd: Base price in USD
            current_regional_prices: Dict of region_code -> price (optional)

        Returns:
            Pricing analysis with recommendations
        """
        logger.info(f"Analyzing regional pricing for ${base_price_usd} USD base price")

        if base_price_usd <= 0:
            logger.warning("Invalid base price, using $19.99 as default")
            base_price_usd = 19.99

        # Calculate recommended prices for each region
        recommended_prices = {}
        price_gaps = {}

        for region_code, region_data in self.REGIONS.items():
            # PPP-adjusted price
            ppp_price = base_price_usd * region_data['ppp_multiplier']

            # Round to regional price points
            recommended_price = self._round_to_price_point(ppp_price, region_data['currency'])

            recommended_prices[region_code] = {
                'currency': region_data['currency'],
                'recommended_price': recommended_price,
                'ppp_adjusted': ppp_price,
                'market_size': region_data['market_size'],
                'name': region_data['name']
            }

            # Calculate gap if current price provided
            if current_regional_prices and region_code in current_regional_prices:
                current = current_regional_prices[region_code]
                gap_percent = ((current - recommended_price) / recommended_price) * 100 if recommended_price > 0 else 0
                price_gaps[region_code] = {
                    'current': current,
                    'recommended': recommended_price,
                    'gap_percent': gap_percent,
                    'status': self._get_price_status(gap_percent)
                }

        # Generate recommendations
        recommendations = self._generate_pricing_recommendations(
            base_price_usd,
            recommended_prices,
            price_gaps
        )

        # Calculate revenue impact
        revenue_impact = self._calculate_revenue_impact(base_price_usd, recommended_prices)

        return {
            'base_price_usd': base_price_usd,
            'recommended_prices': recommended_prices,
            'price_gaps': price_gaps,
            'recommendations': recommendations,
            'revenue_impact': revenue_impact,
            'priority_regions': self._get_priority_regions(recommended_prices)
        }

    def _round_to_price_point(self, price: float, currency: str) -> float:
        """Round to psychological price points by currency"""

        # Price points by currency
        if currency == 'USD':
            # Round to .99 endings
            if price < 5:
                return round(price * 2) / 2 - 0.01  # $1.99, $2.99, etc.
            elif price < 20:
                return round(price) - 0.01  # $9.99, $14.99
            else:
                return round(price / 5) * 5 - 0.01  # $19.99, $24.99, $29.99

        elif currency == 'EUR':
            # Europeans prefer whole numbers
            if price < 10:
                return round(price)
            else:
                return round(price / 5) * 5

        elif currency == 'GBP':
            # Round to .99 endings
            if price < 10:
                return round(price) - 0.01
            else:
                return round(price / 5) * 5 - 0.01

        elif currency == 'JPY':
            # Round to 100s
            return round(price / 100) * 100

        elif currency == 'CNY':
            # Round to whole numbers
            return round(price)

        elif currency in ['BRL', 'RUB', 'INR', 'MXN', 'ARS', 'TRY']:
            # Emerging markets - round to 5s or 10s
            if price < 20:
                return round(price / 5) * 5
            else:
                return round(price / 10) * 10

        elif currency == 'KRW':
            # Round to 1000s
            return round(price / 1000) * 1000

        else:
            return round(price, 2)

    def _get_price_status(self, gap_percent: float) -> str:
        """Get status indicator for price gap"""
        if abs(gap_percent) < 5:
            return "optimal"
        elif abs(gap_percent) < 15:
            return "acceptable"
        elif gap_percent > 15:
            return "too_expensive"
        else:
            return "too_cheap"

    def _generate_pricing_recommendations(self, base_price: float,
                                         recommended_prices: Dict[str, Any],
                                         price_gaps: Dict[str, Any]) -> List[str]:
        """Generate actionable pricing recommendations"""
        recommendations = []

        # Priority regions with significant gaps
        if price_gaps:
            significant_gaps = {k: v for k, v in price_gaps.items()
                              if abs(v['gap_percent']) > 15}

            if significant_gaps:
                recommendations.append(
                    f"🔴 **Critical**: Adjust pricing in {len(significant_gaps)} regions "
                    f"(>15% gap from recommended)"
                )

                for region_code, gap_data in significant_gaps.items():
                    region_name = self.REGIONS[region_code]['name']
                    if gap_data['status'] == 'too_expensive':
                        recommendations.append(
                            f"   - Lower {region_name} price from "
                            f"{gap_data['current']:.2f} to {gap_data['recommended']:.2f} "
                            f"({gap_data['currency']}) for better conversion"
                        )
                    elif gap_data['status'] == 'too_cheap':
                        recommendations.append(
                            f"   - Increase {region_name} price from "
                            f"{gap_data['current']:.2f} to {gap_data['recommended']:.2f} "
                            f"({gap_data['currency']}) to capture value"
                        )

        # High-priority regions not priced
        very_large_markets = [k for k, v in recommended_prices.items()
                             if v['market_size'] == 'very_large']

        if price_gaps:
            missing_markets = [k for k in very_large_markets if k not in price_gaps]
        else:
            missing_markets = very_large_markets

        if missing_markets:
            market_names = [self.REGIONS[k]['name'] for k in missing_markets]
            recommendations.append(
                f"🟡 **High Priority**: Add regional pricing for: {', '.join(market_names)}"
            )

        # Base price evaluation
        if base_price < 10:
            recommendations.append(
                "💡 Consider bundle or DLC pricing strategy for low-priced games"
            )
        elif base_price > 40:
            recommendations.append(
                "💡 Premium pricing - ensure regional adjustments for emerging markets"
            )

        return recommendations

    def _calculate_revenue_impact(self, base_price: float,
                                  recommended_prices: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate potential revenue impact of regional pricing"""

        # Estimate market distribution (based on Steam data)
        market_distribution = {
            'very_large': 0.30,  # 30% of sales
            'large': 0.15,
            'medium': 0.08,
            'small': 0.02
        }

        # Calculate weighted revenue potential
        total_revenue_potential = 0
        revenue_by_region = {}

        for region_code, price_data in recommended_prices.items():
            market_size = price_data['market_size']
            market_weight = market_distribution.get(market_size, 0.01)

            # Estimate units sold per region
            estimated_units = market_weight * 1000  # per 1000 total units

            # Revenue in USD equivalent (approximate)
            if price_data['currency'] == 'USD':
                revenue = price_data['recommended_price'] * estimated_units
            else:
                # Use PPP to convert back to USD equivalent
                ppp = self.REGIONS[region_code]['ppp_multiplier']
                revenue = (price_data['recommended_price'] / ppp) * estimated_units

            revenue_by_region[region_code] = {
                'estimated_units': estimated_units,
                'revenue_usd_equivalent': revenue,
                'market_weight': market_weight
            }

            total_revenue_potential += revenue

        # Calculate impact vs US-only pricing
        us_only_revenue = base_price * 1000
        additional_revenue = total_revenue_potential - us_only_revenue
        revenue_increase_percent = (additional_revenue / us_only_revenue) * 100 if us_only_revenue > 0 else 0

        return {
            'total_revenue_potential': total_revenue_potential,
            'us_only_revenue': us_only_revenue,
            'additional_revenue': additional_revenue,
            'revenue_increase_percent': revenue_increase_percent,
            'revenue_by_region': revenue_by_region
        }

    def _get_priority_regions(self, recommended_prices: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get prioritized list of regions to focus on"""

        priority_list = []

        for region_code, price_data in recommended_prices.items():
            # Priority score based on market size
            priority_score = 0
            if price_data['market_size'] == 'very_large':
                priority_score = 4
            elif price_data['market_size'] == 'large':
                priority_score = 3
            elif price_data['market_size'] == 'medium':
                priority_score = 2
            else:
                priority_score = 1

            priority_list.append({
                'region_code': region_code,
                'region_name': price_data['name'],
                'priority_score': priority_score,
                'market_size': price_data['market_size'],
                'recommended_price': f"{price_data['recommended_price']:.2f} {price_data['currency']}"
            })

        # Sort by priority
        priority_list.sort(key=lambda x: x['priority_score'], reverse=True)

        return priority_list

    def analyze_localization_roi(self, base_price: float,
                                 current_languages: List[str],
                                 estimated_units: int = 1000) -> Dict[str, Any]:
        """
        Calculate ROI for adding language localizations

        Args:
            base_price: Game price in USD
            current_languages: List of currently supported language codes
            estimated_units: Estimated units to sell

        Returns:
            Localization ROI analysis
        """
        logger.info(f"Analyzing localization ROI for {len(current_languages)} current languages")

        # Find missing high-value languages
        missing_languages = []

        for lang_code, lang_data in self.LANGUAGE_ROI.items():
            if lang_code not in current_languages:
                # Calculate ROI
                additional_reach_percent = lang_data['market_reach']
                additional_units = (estimated_units * additional_reach_percent) / 100
                additional_revenue = additional_units * base_price
                localization_cost = lang_data['cost']

                roi = ((additional_revenue - localization_cost) / localization_cost) * 100 if localization_cost > 0 else 0
                payback_units = localization_cost / base_price if base_price > 0 else 0

                missing_languages.append({
                    'language_code': lang_code,
                    'language': lang_data['language'],
                    'localization_cost': localization_cost,
                    'additional_revenue': additional_revenue,
                    'roi_percent': roi,
                    'roi_multiplier': lang_data['roi_multiplier'],
                    'market_reach_percent': additional_reach_percent,
                    'payback_units': int(payback_units),
                    'priority': 'high' if roi > 200 else 'medium' if roi > 100 else 'low'
                })

        # Sort by ROI
        missing_languages.sort(key=lambda x: x['roi_percent'], reverse=True)

        # Generate recommendations
        recommendations = []

        high_priority_langs = [l for l in missing_languages if l['priority'] == 'high']
        if high_priority_langs:
            top_lang = high_priority_langs[0]
            recommendations.append(
                f"🎯 **Top Priority**: Add {top_lang['language']} localization "
                f"(${top_lang['localization_cost']:,} cost, "
                f"${top_lang['additional_revenue']:,.0f} potential revenue, "
                f"{top_lang['roi_percent']:.0f}% ROI)"
            )

        if len(high_priority_langs) > 1:
            recommendations.append(
                f"📈 Consider {len(high_priority_langs)} high-ROI languages total"
            )

        # Current coverage
        total_market_reach = sum([self.LANGUAGE_ROI[lang]['market_reach']
                                 for lang in current_languages if lang in self.LANGUAGE_ROI])

        recommendations.append(
            f"📊 Current language coverage: ~{total_market_reach}% of global Steam market"
        )

        return {
            'current_languages': current_languages,
            'current_market_reach_percent': total_market_reach,
            'missing_languages': missing_languages[:10],  # Top 10
            'recommendations': recommendations,
            'total_potential_revenue': sum([l['additional_revenue'] for l in missing_languages]),
            'total_localization_cost': sum([l['localization_cost'] for l in missing_languages])
        }


# Convenience function
def get_regional_pricing_analysis(base_price_usd: float,
                                  current_languages: List[str] = None) -> Dict[str, Any]:
    """
    Get complete regional pricing analysis

    Args:
        base_price_usd: Base price in USD
        current_languages: Currently supported languages

    Returns:
        Complete pricing and localization analysis
    """
    analyzer = RegionalPricingAnalyzer()

    # Price analysis
    pricing = analyzer.analyze_pricing(base_price_usd)

    # Localization ROI
    if current_languages is None:
        current_languages = ['en']

    localization = analyzer.analyze_localization_roi(base_price_usd, current_languages)

    return {
        'pricing': pricing,
        'localization': localization,
        'summary': {
            'revenue_increase_potential': f"{pricing['revenue_impact']['revenue_increase_percent']:.1f}%",
            'priority_regions': len(pricing['priority_regions']),
            'recommended_localizations': len([l for l in localization['missing_languages']
                                            if l['priority'] == 'high']),
            'total_market_reach': f"{localization['current_market_reach_percent']}%"
        }
    }
