#!/usr/bin/env python3
"""
Alternative Steam Data Sources
Fetches game data from multiple sources when Steam API is blocked
"""

import requests
import json
import re
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup


class AlternativeDataSource:
    """Fetches Steam game data from alternative sources"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Import data source APIs individually for graceful degradation
        self.rawg = None
        self.igdb = None
        self.trends = None
        self.youtube = None
        self.steam = None
        self.hltb = None
        self.estimator = None
        self.use_smart_estimation = False

        # Try to import each API separately
        try:
            from src.rawg_api import RAWGApi
            self.rawg = RAWGApi()
            print("✓ RAWG API initialized")
        except ImportError as e:
            print(f"⚠️ RAWG API unavailable: {e}")

        try:
            from src.igdb_api import IGDBApi
            self.igdb = IGDBApi()
            print("✓ IGDB API initialized")
        except ImportError as e:
            print(f"⚠️ IGDB API unavailable: {e}")

        try:
            from src.trends_api import TrendsApi
            self.trends = TrendsApi()
            print("✓ Google Trends API initialized")
        except ImportError as e:
            print(f"⚠️ Google Trends API unavailable: {e}")

        try:
            from src.youtube_api import YouTubeApi
            self.youtube = YouTubeApi()
            print("✓ YouTube API initialized")
        except ImportError as e:
            print(f"⚠️ YouTube API unavailable: {e}")

        try:
            from src.steam_api import SteamWebApi
            self.steam = SteamWebApi()
            print("✓ Steam Web API initialized")
        except ImportError as e:
            print(f"⚠️ Steam Web API unavailable: {e}")

        try:
            from src.hltb_api import HLTBApi
            self.hltb = HLTBApi()
            print("✓ HowLongToBeat initialized")
        except ImportError as e:
            print(f"⚠️ HowLongToBeat unavailable: {e}")

        try:
            from src.smart_estimator import SmartEstimator
            self.estimator = SmartEstimator()
            self.use_smart_estimation = True
            print("✓ Smart Estimator initialized")
        except ImportError as e:
            print(f"⚠️ Smart Estimator unavailable: {e}")
            self.use_smart_estimation = False

    def get_game_data_from_store_page(self, app_id: int) -> Dict[str, Any]:
        """
        Scrape game data directly from Steam store page
        This often works when API endpoints are blocked
        """
        try:
            url = f"https://store.steampowered.com/app/{app_id}"

            # Add age gate bypass cookies (birthtime = Jan 1, 1990)
            cookies = {
                'birthtime': '631152000',  # Timestamp for age verification
                'mature_content': '1'
            }

            print(f"Fetching Steam store page for app {app_id}...")
            response = self.session.get(url, cookies=cookies, timeout=3)  # Fast failure for blocked IPs
            response.raise_for_status()

            print(f"Parsing HTML (length: {len(response.text)} chars)...")
            soup = BeautifulSoup(response.text, 'html.parser')  # Use html.parser for reliability

            # Check if we got an age gate or error page
            if 'Please enter your birth date' in response.text or 'agegate' in response.text.lower():
                print("Warning: Age gate detected despite cookies")
                # Try to continue anyway with limited data

            # Extract JSON data embedded in the page
            game_data = self._extract_game_data_from_html(soup, app_id)

            if not game_data.get('name'):
                print(f"Warning: Could not extract game name from HTML")
                return {}

            print(f"Found game: {game_data.get('name')}")

            # Get review data from Steam review widget
            review_data = self._get_reviews_from_store_page(app_id)

            # Merge data
            if review_data:
                game_data.update(review_data)
                print(f"Got {review_data.get('reviews_total', 0):,} reviews")
            else:
                print("Warning: No review data found")

            return game_data

        except requests.Timeout:
            print(f"Timeout fetching Steam store page for app {app_id}")
            return {}
        except Exception as e:
            print(f"Error scraping Steam store page: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _extract_game_data_from_html(self, soup: BeautifulSoup, app_id: int) -> Dict[str, Any]:
        """Extract game data from Steam store page HTML"""
        data = {'app_id': app_id}

        try:
            # Game name - try multiple selectors
            name_elem = (soup.find('div', class_='apphub_AppName') or
                        soup.find('div', id='appHubAppName') or
                        soup.find('div', class_='page_title_area'))

            if name_elem:
                # Clean up the name
                name_text = name_elem.get_text(strip=True)
                data['name'] = name_text
            else:
                # Try to get from page title
                title = soup.find('title')
                if title:
                    title_text = title.text
                    if ' on Steam' in title_text:
                        data['name'] = title_text.replace(' on Steam', '').strip()

            # Price - try multiple selectors
            price_elem = (soup.find('div', class_='game_purchase_price') or
                         soup.find('div', class_='discount_final_price') or
                         soup.find('div', class_='game_area_purchase_game'))

            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # Extract numeric price
                price_match = re.search(r'[\$€£]?\s*(\d+[.,]\d{2})', price_text)
                if price_match:
                    price_str = price_match.group(1).replace(',', '.')
                    data['price'] = price_text
                    data['price_raw'] = float(price_str)

            # If price not found, might be free
            if 'price_raw' not in data:
                if 'Free to Play' in str(soup) or 'Play for Free' in str(soup):
                    data['price'] = 'Free'
                    data['price_raw'] = 0.0

            # Description
            desc_elem = soup.find('div', class_='game_description_snippet')
            if desc_elem:
                data['description'] = desc_elem.get_text(strip=True)

            # Developer/Publisher
            dev_elem = soup.find('div', id='developers_list')
            if dev_elem:
                dev_link = dev_elem.find('a')
                if dev_link:
                    data['developer'] = dev_link.get_text(strip=True)

            pub_elem = soup.find('div', class_='dev_row')
            if pub_elem and 'Publisher:' in pub_elem.text:
                pub_link = pub_elem.find('a')
                if pub_link:
                    data['publisher'] = pub_link.get_text(strip=True)

            # Release date
            release_elem = soup.find('div', class_='release_date')
            if release_elem:
                date_elem = release_elem.find('div', class_='date')
                if date_elem:
                    data['release_date'] = date_elem.get_text(strip=True)

            # Tags
            tags = []
            tag_elements = soup.find_all('a', class_='app_tag')
            for tag in tag_elements[:15]:
                tag_text = tag.get_text(strip=True)
                if tag_text:
                    tags.append(tag_text)
            data['tags'] = tags

            # Genres
            genres = []
            genre_elements = soup.find_all('a', href=re.compile(r'genre'))
            for genre in genre_elements[:10]:
                genres.append(genre.text.strip())
            data['genres'] = list(set(genres))  # Remove duplicates

            # Categories (multiplayer, controller support, etc.)
            categories = []
            category_elements = soup.find_all('a', href=re.compile(r'category'))
            for cat in category_elements[:10]:
                categories.append(cat.text.strip())
            data['categories'] = list(set(categories))

        except Exception as e:
            print(f"Error parsing HTML data: {e}")

        return data

    def _get_reviews_from_store_page(self, app_id: int) -> Dict[str, Any]:
        """Get review statistics from Steam store page review widget"""
        try:
            print(f"Fetching reviews for app {app_id}...")
            url = f"https://store.steampowered.com/appreviews/{app_id}?json=1&num_per_page=0"
            response = self.session.get(url, timeout=3)  # Fast failure for blocked IPs
            response.raise_for_status()

            data = response.json()
            query_summary = data.get('query_summary', {})

            total = query_summary.get('total_reviews', 0)
            positive = query_summary.get('total_positive', 0)
            negative = query_summary.get('total_negative', 0)

            print(f"Found {total:,} total reviews ({positive:,} positive, {negative:,} negative)")

            return {
                'reviews_total': total,
                'reviews_positive': positive,
                'reviews_negative': negative,
                'review_score_raw': (positive / total * 100) if total > 0 else 0,
                'review_score': f"{(positive / total * 100):.1f}%" if total > 0 else "N/A"
            }
        except requests.Timeout:
            print(f"Timeout getting review data for app {app_id}")
            return {}
        except Exception as e:
            print(f"Error getting review data: {e}")
            return {}

    def get_ownership_estimates(self, app_id: int, review_count: int) -> Dict[str, Any]:
        """
        Estimate ownership based on review count using industry ratios
        Average review rate: 1-2% of owners leave reviews
        """
        if review_count < 10:
            return self._get_minimal_ownership_estimate()

        # Use conservative 1.5% review rate for estimation
        estimated_owners = int(review_count / 0.015)

        # Create ranges
        owners_min = int(estimated_owners * 0.7)
        owners_max = int(estimated_owners * 1.5)

        return {
            'owners_min': owners_min,
            'owners_max': owners_max,
            'owners_avg': estimated_owners,
            'owners_display': f'{owners_min:,} .. {owners_max:,}',
            'estimation_method': 'review_ratio',
            'confidence': 'medium'
        }

    def estimate_revenue(self, owners_avg: int, price_raw: float, review_score: float) -> Dict[str, Any]:
        """Estimate revenue based on ownership and price"""
        if owners_avg < 100 or price_raw <= 0:
            return self._get_minimal_revenue_estimate()

        # FIX: Ensure review_score is numeric (defensive programming)
        try:
            review_score_numeric = float(review_score) if review_score is not None else 0.0
        except (ValueError, TypeError):
            review_score_numeric = 0.0

        # Account for:
        # - Regional pricing (avg 70% of base price globally)
        # - Steam's 30% cut
        # - Refunds (~5-10% depending on quality)
        # - Sales/discounts over time (~20% revenue reduction)

        regional_multiplier = 0.70  # Regional pricing
        steam_cut = 0.70  # After Steam's 30%
        refund_rate = 0.08 if review_score_numeric >= 80 else 0.12  # Lower refunds for good games
        discount_factor = 0.85  # Average discount impact over time

        effective_price = price_raw * regional_multiplier * steam_cut * (1 - refund_rate) * discount_factor

        revenue_estimate = int(owners_avg * effective_price)
        revenue_low = int(revenue_estimate * 0.6)
        revenue_high = int(revenue_estimate * 1.8)

        return {
            'estimated_revenue': f'${revenue_estimate:,}',
            'estimated_revenue_raw': revenue_estimate,
            'revenue_range': f'${revenue_low//1000}K - ${revenue_high//1000}K',
            'revenue_confidence_low': revenue_low,
            'revenue_confidence_high': revenue_high,
            'estimation_method': 'calculated',
            'confidence': 'medium'
        }

    def _get_minimal_ownership_estimate(self) -> Dict[str, Any]:
        """Return minimal ownership estimate for games with very few reviews"""
        return {
            'owners_min': 100,
            'owners_max': 5000,
            'owners_avg': 1000,
            'owners_display': '100 .. 5,000',
            'estimation_method': 'minimal',
            'confidence': 'low'
        }

    def _get_minimal_revenue_estimate(self) -> Dict[str, Any]:
        """Return minimal revenue estimate"""
        return {
            'estimated_revenue': '$5,000',
            'estimated_revenue_raw': 5000,
            'revenue_range': '$1K - $15K',
            'revenue_confidence_low': 1000,
            'revenue_confidence_high': 15000,
            'estimation_method': 'minimal',
            'confidence': 'low'
        }

    def get_complete_game_data(self, app_id: int, game_name: str = None) -> Dict[str, Any]:
        """
        Get complete game data from alternative sources

        Priority order:
        1. Steam store page scraping (best if it works)
        2. RAWG API + smart estimation (when Steam is blocked)
        3. Minimal fallback (last resort)

        This is the main entry point that orchestrates data fetching
        """
        print(f"Fetching data for app_id {app_id} using alternative sources...")

        # PRIORITY 1: Try Steam store page
        game_data = self.get_game_data_from_store_page(app_id)

        # FIX: Safely check reviews_total (defensive programming)
        reviews_total_check = game_data.get('reviews_total', 0) if game_data else 0
        try:
            reviews_total_numeric = int(reviews_total_check) if reviews_total_check is not None else 0
        except (ValueError, TypeError):
            reviews_total_numeric = 0

        if game_data and reviews_total_numeric > 0:
            print("✓ Got data from Steam store page")
            # Estimate ownership based on reviews
            review_count = reviews_total_numeric
            ownership_data = self.get_ownership_estimates(app_id, review_count)
            game_data.update(ownership_data)
        else:
            print("✗ Steam store page failed or returned no data")

            # PRIORITY 2: Try RAWG API + Smart Estimation
            if self.use_smart_estimation and game_name:
                print(f"Trying RAWG API fallback for: {game_name}")
                rawg_data = None
                if self.rawg:
                    rawg_data = self.rawg.search_game(game_name)

                if rawg_data:
                    print(f"✓ Got data from RAWG: {rawg_data['name']}")
                    # Use smart estimation based on RAWG data
                    game_data = self._build_from_rawg(app_id, rawg_data)
                else:
                    print("✗ RAWG API failed or no results")
                    # PRIORITY 3: Minimal fallback
                    return {}
            else:
                print("✗ Smart estimation not available or no game name provided")
                return {}

        # Estimate revenue
        price = game_data.get('price_raw', 0)
        review_score_raw = game_data.get('review_score_raw', 0)
        owners = game_data.get('owners_avg', 0)

        # FIX: Ensure review_score is numeric before comparisons
        try:
            review_score = float(review_score_raw) if review_score_raw is not None else 0.0
        except (ValueError, TypeError):
            review_score = 0.0

        revenue_data = self.estimate_revenue(owners, price, review_score)
        game_data.update(revenue_data)

        # Add quality multiplier based on review score
        if review_score >= 90:
            game_data['quality_multiplier'] = 1.3
        elif review_score >= 80:
            game_data['quality_multiplier'] = 1.1
        elif review_score >= 70:
            game_data['quality_multiplier'] = 1.0
        else:
            game_data['quality_multiplier'] = 0.9

        # FIX: Ensure review_count is numeric for formatting
        review_count_raw = game_data.get('reviews_total', 0)
        try:
            review_count = int(review_count_raw) if review_count_raw is not None else 0
        except (ValueError, TypeError):
            review_count = 0

        print(f"Successfully fetched data: {game_data.get('name')} - {review_count:,} reviews")
        return game_data

    def _build_from_rawg(self, app_id: int, rawg_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build game data from ALL data sources + smart estimation

        Fetches from: RAWG, IGDB, Google Trends, YouTube
        Uses multi-signal analysis to estimate ownership and revenue
        """
        game_name = rawg_data.get('name', 'Unknown')

        # Fetch from additional sources for cross-validation
        igdb_data = None
        trends_data = None
        youtube_data = None
        steam_data = None
        hltb_data = None

        if self.igdb:
            igdb_data = self.igdb.get_multiple_signals(game_name)
            if igdb_data:
                print(f"✓ Got IGDB data for {game_name}")

        if self.trends:
            trends_data = self.trends.get_comprehensive_metrics(game_name)
            if trends_data:
                print(f"✓ Got Google Trends data for {game_name}")

        if self.youtube:
            youtube_data = self.youtube.get_comprehensive_metrics(game_name)
            if youtube_data:
                print(f"✓ Got YouTube data for {game_name}")

        if self.steam:
            steam_data = self.steam.get_comprehensive_metrics(app_id)
            if steam_data:
                print(f"✓ Got Steam Web API data for app {app_id}")

        if self.hltb:
            hltb_data = self.hltb.get_comprehensive_metrics(game_name)
            if hltb_data:
                print(f"✓ Got HowLongToBeat data for {game_name}")

        # Use smart estimator with ALL available signals
        ownership_data = self.estimator.estimate_ownership(
            {},
            rawg_data,
            igdb_data,
            trends_data,
            youtube_data,
            steam_data,
            hltb_data
        )

        # Estimate reviews from RAWG ratings (rough conversion)
        # RAWG ratings ≈ 10-20% of Steam reviews typically
        estimated_reviews = int(rawg_data.get('ratings_count', 0) * 0.15)

        # FIX: Ensure positive_percent is always numeric (RAWG API might return string)
        positive_percent_raw = rawg_data.get('positive_rating_percent', 75)
        try:
            positive_percent = float(positive_percent_raw) if positive_percent_raw is not None else 75.0
        except (ValueError, TypeError):
            positive_percent = 75.0

        estimated_positive = int(estimated_reviews * (positive_percent / 100))
        estimated_negative = estimated_reviews - estimated_positive

        # Build comprehensive game data
        game_data = {
            'app_id': app_id,
            'name': rawg_data.get('name'),
            'developer': 'Unknown',  # RAWG doesn't always have this
            'publisher': 'Unknown',
            'release_date': rawg_data.get('released', 'Unknown'),
            'genres': rawg_data.get('genres', []),
            'tags': rawg_data.get('tags', []),
            'description': rawg_data.get('description', '')[:200] if rawg_data.get('description') else '',

            # Price - we don't have this from RAWG, use genre average
            'price': '$29.99',  # Default assumption
            'price_raw': 29.99,

            # Reviews (estimated from RAWG ratings)
            'reviews_total': estimated_reviews,
            'reviews_positive': estimated_positive,
            'reviews_negative': estimated_negative,
            'review_score': f"{positive_percent:.1f}%",
            'review_score_raw': positive_percent,

            # Ownership (from smart estimation)
            'owners_min': ownership_data['owners_min'],
            'owners_max': ownership_data['owners_max'],
            'owners_avg': ownership_data['owners_avg'],
            'owners_display': ownership_data['owners_display'],
            'estimation_method': f"rawg_smart_estimation",
            'confidence': ownership_data['confidence'],

            # Metadata
            'quality_multiplier': ownership_data.get('total_multiplier', 1.0),
            'data_source': self._build_data_source_string(rawg_data, igdb_data, trends_data, youtube_data, steam_data, hltb_data),
            'signals_used': ownership_data.get('signals_used', []),

            # RAWG-specific enrichment
            'metacritic': rawg_data.get('metacritic'),
            'average_playtime': rawg_data.get('playtime', 0),
            'rawg_rating': rawg_data.get('rating', 0),
            'rawg_ratings_count': rawg_data.get('ratings_count', 0),

            # IGDB enrichment (if available)
            'igdb_follows': igdb_data.get('follows', 0) if igdb_data else 0,
            'igdb_rating': igdb_data.get('user_rating', 0) if igdb_data else 0,
            'igdb_critic_score': igdb_data.get('critic_rating', 0) if igdb_data else 0,

            # Google Trends enrichment (if available)
            'trends_interest': trends_data.get('current_interest', 0) if trends_data else 0,
            'trends_direction': trends_data.get('trend_direction', 'unknown') if trends_data else 'unknown',

            # YouTube enrichment (if available)
            'youtube_views': youtube_data.get('total_views', 0) if youtube_data else 0,
            'youtube_videos': youtube_data.get('video_count', 0) if youtube_data else 0,

            # Steam Web API enrichment (if available)
            'steam_current_players': steam_data.get('current_players', 0) if steam_data else 0,

            # HowLongToBeat enrichment (if available)
            'hltb_main_story': hltb_data.get('main_story_hours', 0) if hltb_data else 0,
            'hltb_completionist': hltb_data.get('completionist_hours', 0) if hltb_data else 0,
        }

        # Estimate revenue
        revenue_data = self.estimator.estimate_revenue(
            ownership_data,
            game_data['price_raw'],
            positive_percent
        )
        game_data.update(revenue_data)

        print(f"Built game data from multiple sources: {game_data['name']}")
        print(f"  Ownership: {ownership_data['owners_display']}")
        print(f"  Confidence: {ownership_data['confidence']}")
        print(f"  Signals: {', '.join(ownership_data['signals_used'])}")
        print(f"  Data Sources: {game_data['data_source']}")

        return game_data

    def _build_data_source_string(
        self,
        rawg_data: Optional[Dict[str, Any]],
        igdb_data: Optional[Dict[str, Any]],
        trends_data: Optional[Dict[str, Any]],
        youtube_data: Optional[Dict[str, Any]],
        steam_data: Optional[Dict[str, Any]],
        hltb_data: Optional[Dict[str, Any]]
    ) -> str:
        """Build a human-readable string showing which data sources were used"""
        sources = []

        if rawg_data:
            sources.append("RAWG API")
        if igdb_data:
            sources.append("IGDB API")
        if trends_data:
            sources.append("Google Trends")
        if youtube_data:
            sources.append("YouTube Data")
        if steam_data:
            sources.append("Steam Web API")
        if hltb_data:
            sources.append("HowLongToBeat")

        if len(sources) == 0:
            return "Generic Estimation"
        elif len(sources) == 1:
            return f"{sources[0]} + Smart Estimation"
        else:
            return f"{' + '.join(sources)} + Smart Estimation"


def test_alternative_source():
    """Test function for alternative data source"""
    source = AlternativeDataSource()

    # Test with Hades 2
    app_id = 1145350
    data = source.get_complete_game_data(app_id)

    print("\n=== Game Data ===")
    print(f"Name: {data.get('name')}")
    print(f"Price: {data.get('price')}")
    print(f"Reviews: {data.get('reviews_total'):,} ({data.get('review_score')})")
    print(f"Estimated Owners: {data.get('owners_display')}")
    print(f"Estimated Revenue: {data.get('revenue_range')}")
    print(f"Tags: {', '.join(data.get('tags', [])[:5])}")

    return data


if __name__ == "__main__":
    test_alternative_source()
