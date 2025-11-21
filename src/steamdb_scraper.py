import requests
from typing import Dict, Any, Optional
import time
from src.alternative_data_sources import AlternativeDataSource
from src.cache_manager import get_cache
from src.logger import get_logger

cache = get_cache()
logger = get_logger(__name__)

class SteamDBScraper:
    """Scraper for Steam sales and revenue data"""

    def __init__(self):
        self.steamspy_api_base = "https://steamspy.com/api.php"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.alternative_source = AlternativeDataSource()

    def get_sales_data(self, app_id: Any, game_name: str = None) -> Dict[str, Any]:
        """
        IMPROVED: Get sales and revenue estimates using multiple methods (WITH CACHING)

        Priority order:
        0. Cache (24-hour TTL)
        1. Alternative source (Steam store page scraping) - works when API is blocked
        2. RAWG API + Smart Estimation (when Steam is blocked and game_name provided)
        3. SteamSpy API - fallback if scraping fails
        4. Fallback estimates - last resort

        Args:
            app_id: Steam app ID
            game_name: Game name (optional, enables RAWG fallback)

        Returns:
            Dictionary with enhanced sales data including confidence ranges
        """
        if app_id == 'unknown' or app_id == 'fallback' or str(app_id).startswith('fallback'):
            return self._generate_fallback_sales_data()

        # Validate and convert app_id to int
        try:
            app_id_int = int(app_id)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid app_id format '{app_id}': {e}")
            return self._generate_fallback_sales_data()

        # Check cache first (24-hour freshness for sales data)
        cached_data = cache.get('sales_data', app_id_int, ttl_hours=24)
        if cached_data:
            logger.debug(f"Using cached sales data for App ID {app_id_int}")
            return cached_data

        # PRIORITY 1: Try alternative source (Steam store page scraping)
        try:
            logger.info(f"Fetching sales data from alternative source for App ID {app_id_int}...")
            alt_data = self.alternative_source.get_complete_game_data(app_id_int, game_name=game_name)

            if alt_data and alt_data.get('reviews_total', 0) > 0:
                logger.info(f"Successfully retrieved data from alternative source")
                # Convert alternative source data to our format
                sales_data = self._format_alternative_data(alt_data)
                # Cache the result
                cache.set('sales_data', app_id_int, sales_data)
                return sales_data
            else:
                logger.warning("Alternative source returned incomplete data, trying SteamSpy API...")
        except Exception as e:
            logger.warning(f"Alternative source failed: {e}, trying SteamSpy API...")

        # PRIORITY 2: Try SteamSpy API (original method)
        try:
            logger.info(f"Fetching sales data from SteamSpy API for App ID {app_id}...")
            response = requests.get(
                self.steamspy_api_base,
                params={'request': 'appdetails', 'appid': app_id},
                headers=self.headers,
                timeout=3  # Fast failure for blocked IPs
            )
            response.raise_for_status()

            # Check if we got "Access denied"
            if response.text == "Access denied":
                logger.warning("SteamSpy API returned 'Access denied' - IP may be blocked")
                raise Exception("Access denied by SteamSpy")

            data = response.json()
            logger.info(f"Successfully got data from SteamSpy API")

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

            # Determine confidence level based on data quality
            if total_reviews > 5000:
                confidence_level = 'high'
            elif total_reviews > 1000:
                confidence_level = 'medium-high'
            elif total_reviews > 100:
                confidence_level = 'medium'
            else:
                confidence_level = 'low-medium'

            sales_data = {
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
                'confidence': confidence_level,
                'data_source': 'SteamSpy API',
                'signals_used': ['ownership_data', 'review_count', 'review_score'],
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

            # Cache the result
            cache.set('sales_data', app_id_int, sales_data)

            return sales_data

        except Exception as e:
            logger.error(f"Error getting sales data: {e}", exc_info=True)
            return self._generate_fallback_sales_data()

    def _format_alternative_data(self, alt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert alternative source data to our standard format"""
        return {
            'app_id': alt_data.get('app_id'),
            'owners_min': alt_data.get('owners_min', 0),
            'owners_max': alt_data.get('owners_max', 0),
            'owners_avg': alt_data.get('owners_avg', 0),
            'owners_display': alt_data.get('owners_display', '0 .. 0'),
            'estimated_revenue': alt_data.get('estimated_revenue', '$0'),
            'estimated_revenue_raw': alt_data.get('estimated_revenue_raw', 0),
            'revenue_range': alt_data.get('revenue_range', '$0 - $0'),
            'revenue_confidence_low': alt_data.get('revenue_confidence_low', 0),
            'revenue_confidence_high': alt_data.get('revenue_confidence_high', 0),
            'estimation_method': alt_data.get('estimation_method', 'alternative_source'),
            'confidence': alt_data.get('confidence', 'medium'),
            'data_source': alt_data.get('data_source', 'Alternative Sources'),
            'signals_used': alt_data.get('signals_used', []),
            'quality_multiplier': alt_data.get('quality_multiplier', 1.0),
            'price': alt_data.get('price', '$0.00'),
            'price_raw': alt_data.get('price_raw', 0),
            'reviews_total': alt_data.get('reviews_total', 0),
            'reviews_positive': alt_data.get('reviews_positive', 0),
            'reviews_negative': alt_data.get('reviews_negative', 0),
            'review_score': alt_data.get('review_score', '0%'),
            'review_score_raw': alt_data.get('review_score_raw', 0),
            'players_2weeks': 0,  # Not available from alternative source
            'players_forever': 0,  # Not available from alternative source
            'average_playtime': 0,  # Not available from alternative source
            'median_playtime': 0,  # Not available from alternative source
            'ccu': 0,  # Not available from alternative source
            'tags': alt_data.get('tags', [])
        }

    def _parse_owners_range(self, owners_str: str) -> Dict[str, int]:
        """Parse owner range string like '20,000 .. 50,000'"""
        try:
            parts = owners_str.split('..')
            min_owners = int(parts[0].strip().replace(',', ''))
            max_owners = int(parts[1].strip().replace(',', ''))
            return {'min': min_owners, 'max': max_owners}
        except Exception as e:
            logger.warning(f"Error parsing owners range '{owners_str}': {e}")
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
            'confidence': 'low',
            'data_source': 'Generic Estimation (No API Data Available)',
            'signals_used': [],
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
        """
        Get review statistics including recent review data for velocity calculation

        Returns review stats with velocity score:
        - velocity_score = recent_reviews / total_reviews
        - Higher score = growing momentum
        - Lower score = declining/established game
        """
        sales_data = self.get_sales_data(app_id)

        # Get recent review data from Steam API
        recent_data = self._get_recent_reviews(app_id)

        total_reviews = sales_data.get('reviews_total', 0)
        recent_reviews = recent_data.get('recent_reviews', 0)

        # Calculate velocity score
        velocity_score = (recent_reviews / total_reviews) if total_reviews > 0 else 0

        # Interpret velocity
        if velocity_score > 0.05:
            velocity_status = "High momentum - actively growing"
        elif velocity_score > 0.02:
            velocity_status = "Moderate momentum"
        elif velocity_score > 0.01:
            velocity_status = "Steady state"
        else:
            velocity_status = "Declining or established game"

        return {
            'total': total_reviews,
            'positive': sales_data.get('reviews_positive', 0),
            'negative': sales_data.get('reviews_negative', 0),
            'score': sales_data.get('review_score', 'N/A'),
            'score_raw': sales_data.get('review_score_raw', 0),
            'recent_reviews': recent_reviews,
            'velocity_score': velocity_score,
            'velocity_percentage': f"{velocity_score * 100:.2f}%",
            'velocity_status': velocity_status
        }

    def _get_recent_reviews(self, app_id: Any) -> Dict[str, int]:
        """
        Get recent review count from Steam API
        Uses Steam's review endpoint with 'recent' filter (last 30 days)
        """
        if app_id == 'unknown' or app_id == 'fallback' or str(app_id).startswith('fallback'):
            return {'recent_reviews': 0}

        try:
            response = requests.get(
                f"https://store.steampowered.com/appreviews/{app_id}",
                params={
                    'json': 1,
                    'filter': 'recent',  # Last 30 days
                    'num_per_page': 0,   # We just want the count
                    'language': 'all'
                },
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            query_summary = data.get('query_summary', {})
            recent_reviews = query_summary.get('total_reviews', 0)

            return {'recent_reviews': recent_reviews}

        except Exception as e:
            logger.error(f"Error getting recent reviews: {e}")
            return {'recent_reviews': 0}
