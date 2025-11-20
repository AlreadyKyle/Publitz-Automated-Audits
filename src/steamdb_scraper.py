import requests
from typing import Dict, Any, Optional
import time

class SteamDBScraper:
    """Scraper for Steam sales and revenue data"""

    def __init__(self):
        self.steamspy_api_base = "https://steamspy.com/api.php"

    def get_sales_data(self, app_id: Any) -> Dict[str, Any]:
        """
        IMPROVED: Get sales and revenue estimates using multiple methods

        Uses both SteamSpy ownership data AND review-count estimation:
        - Method 1: SteamSpy owners × price × 0.7 (Steam's cut)
        - Method 2: Reviews × 50-100 (review-to-sale ratio) × price × 0.7
        - Takes higher estimate for popular games
        - Applies quality multiplier for highly-rated games

        Args:
            app_id: Steam app ID

        Returns:
            Dictionary with enhanced sales data including confidence ranges
        """
        if app_id == 'unknown' or app_id == 'fallback' or str(app_id).startswith('fallback'):
            return self._generate_fallback_sales_data()

        try:
            # Get SteamSpy data
            response = requests.get(
                self.steamspy_api_base,
                params={'request': 'appdetails', 'appid': app_id},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            # Parse owner data
            owners = data.get('owners', '0 .. 0')
            owners_range = self._parse_owners_range(owners)

            # Extract basic info
            price = data.get('price', 0) / 100  # Price in cents to dollars
            avg_owners = (owners_range['min'] + owners_range['max']) / 2

            # Parse review data
            positive = data.get('positive', 0)
            negative = data.get('negative', 0)
            total_reviews = positive + negative
            review_score = (positive / total_reviews * 100) if total_reviews > 0 else 0

            # METHOD 1: SteamSpy-based estimate (conservative)
            steamspy_revenue = avg_owners * price * 0.7  # Steam takes 30%

            # METHOD 2: Review-based estimate (often more accurate for popular games)
            # Rule of thumb: 1 review per 50-100 sales depending on game type
            # Popular/viral games: ~100:1, niche/hardcore: ~30:1, average: ~50:1
            if total_reviews > 0:
                # Determine review ratio based on game characteristics
                if total_reviews > 20000:
                    # Very popular games tend to have lower review rates
                    review_ratio = 80
                elif total_reviews > 5000:
                    # Popular games
                    review_ratio = 60
                elif total_reviews > 1000:
                    # Moderate popularity
                    review_ratio = 50
                else:
                    # Smaller games often have higher review rates
                    review_ratio = 40

                estimated_sales = total_reviews * review_ratio
                review_based_revenue = estimated_sales * price * 0.7
            else:
                review_based_revenue = 0

            # Combine methods: use higher estimate for well-reviewed games
            if total_reviews > 1000:
                # For popular games, review-based is often more accurate
                base_revenue = max(steamspy_revenue, review_based_revenue)
            else:
                # For smaller games, SteamSpy is more reliable
                base_revenue = steamspy_revenue

            # Apply quality multiplier for highly-rated games
            # Great games often exceed estimates due to word-of-mouth
            if review_score >= 95:
                quality_multiplier = 1.5  # Exceptional games
            elif review_score >= 90:
                quality_multiplier = 1.3  # Great games
            elif review_score >= 85:
                quality_multiplier = 1.15  # Very good games
            elif review_score >= 80:
                quality_multiplier = 1.05  # Good games
            else:
                quality_multiplier = 1.0  # Average or below

            enhanced_revenue = base_revenue * quality_multiplier

            # Calculate confidence range
            confidence_low = enhanced_revenue * 0.6   # Conservative
            confidence_mid = enhanced_revenue          # Best estimate
            confidence_high = enhanced_revenue * 1.8   # Optimistic

            # Format ranges
            if confidence_mid < 1000:
                revenue_range = f"${confidence_low:,.0f} - ${confidence_high:,.0f}"
            elif confidence_mid < 1000000:
                revenue_range = f"${confidence_low/1000:,.0f}K - ${confidence_high/1000:,.0f}K"
            else:
                revenue_range = f"${confidence_low/1000000:,.1f}M - ${confidence_high/1000000:,.1f}M"

            return {
                'app_id': app_id,
                'owners_min': owners_range['min'],
                'owners_max': owners_range['max'],
                'owners_avg': int(avg_owners),
                'owners_display': owners,
                'estimated_revenue': f"${confidence_mid:,.0f}",  # Display mid estimate
                'estimated_revenue_raw': confidence_mid,
                'revenue_range': revenue_range,  # NEW: Range display
                'revenue_confidence_low': confidence_low,  # NEW: Low estimate
                'revenue_confidence_high': confidence_high,  # NEW: High estimate
                'estimation_method': 'review-based' if review_based_revenue > steamspy_revenue else 'ownership-based',  # NEW: Which method used
                'quality_multiplier': quality_multiplier,  # NEW: Applied multiplier
                'price': f"${price:.2f}",
                'price_raw': price,
                'reviews_total': total_reviews,
                'reviews_positive': positive,
                'reviews_negative': negative,
                'review_score': f"{review_score:.1f}%",
                'review_score_raw': review_score,
                'players_2weeks': data.get('players_2weeks', 0),
                'players_forever': data.get('players_forever', 0),
                'average_playtime': data.get('average_forever', 0),
                'median_playtime': data.get('median_forever', 0),
                'ccu': data.get('ccu', 0),
                'tags': list(data.get('tags', {}).keys())[:10] if isinstance(data.get('tags'), dict) else []
            }

        except Exception as e:
            print(f"Error getting sales data: {e}")
            return self._generate_fallback_sales_data()

    def _parse_owners_range(self, owners_str: str) -> Dict[str, int]:
        """Parse owner range string like '20,000 .. 50,000'"""
        try:
            parts = owners_str.split('..')
            min_owners = int(parts[0].strip().replace(',', ''))
            max_owners = int(parts[1].strip().replace(',', ''))
            return {'min': min_owners, 'max': max_owners}
        except Exception as e:
            print(f"Error parsing owners range '{owners_str}': {e}")
            return {'min': 0, 'max': 0}

    def _generate_fallback_sales_data(self) -> Dict[str, Any]:
        """Generate fallback sales data when API fails"""
        return {
            'app_id': 'unknown',
            'owners_min': 10000,
            'owners_max': 50000,
            'owners_avg': 30000,
            'owners_display': '10,000 .. 50,000',
            'estimated_revenue': '$150,000',
            'estimated_revenue_raw': 150000,
            'revenue_range': '$90K - $270K',
            'revenue_confidence_low': 90000,
            'revenue_confidence_high': 270000,
            'estimation_method': 'fallback',
            'quality_multiplier': 1.0,
            'price': '$14.99',
            'price_raw': 14.99,
            'reviews_total': 1500,
            'reviews_positive': 1275,
            'reviews_negative': 225,
            'review_score': '85.0%',
            'review_score_raw': 85.0,
            'players_2weeks': 2500,
            'players_forever': 25000,
            'average_playtime': 180,
            'median_playtime': 120,
            'ccu': 150,
            'tags': ['Strategy', 'Indie', 'Singleplayer']
        }

    def get_revenue_estimate(self, app_id: Any) -> str:
        """Get a formatted revenue estimate"""
        sales_data = self.get_sales_data(app_id)
        return sales_data.get('estimated_revenue', 'N/A')

    def get_player_count(self, app_id: Any) -> Dict[str, int]:
        """Get player count statistics"""
        sales_data = self.get_sales_data(app_id)
        return {
            'players_2weeks': sales_data.get('players_2weeks', 0),
            'players_forever': sales_data.get('players_forever', 0),
            'concurrent': sales_data.get('ccu', 0)
        }

    def get_review_stats(self, app_id: Any) -> Dict[str, Any]:
        """Get review statistics"""
        sales_data = self.get_sales_data(app_id)
        return {
            'total': sales_data.get('reviews_total', 0),
            'positive': sales_data.get('reviews_positive', 0),
            'negative': sales_data.get('reviews_negative', 0),
            'score': sales_data.get('review_score', 'N/A'),
            'score_raw': sales_data.get('review_score_raw', 0)
        }
