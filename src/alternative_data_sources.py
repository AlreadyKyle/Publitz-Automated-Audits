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
            response = self.session.get(url, cookies=cookies, timeout=8)  # Reduced timeout
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
            response = self.session.get(url, timeout=5)  # Shorter timeout
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

        # Account for:
        # - Regional pricing (avg 70% of base price globally)
        # - Steam's 30% cut
        # - Refunds (~5-10% depending on quality)
        # - Sales/discounts over time (~20% revenue reduction)

        regional_multiplier = 0.70  # Regional pricing
        steam_cut = 0.70  # After Steam's 30%
        refund_rate = 0.08 if review_score >= 80 else 0.12  # Lower refunds for good games
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

    def get_complete_game_data(self, app_id: int) -> Dict[str, Any]:
        """
        Get complete game data from alternative sources

        This is the main entry point that orchestrates data fetching
        """
        print(f"Fetching data for app_id {app_id} using alternative sources...")

        # Get base game data from store page
        game_data = self.get_game_data_from_store_page(app_id)

        if not game_data or 'reviews_total' not in game_data:
            print("Failed to get game data from store page")
            return {}

        # Estimate ownership based on reviews
        review_count = game_data.get('reviews_total', 0)
        ownership_data = self.get_ownership_estimates(app_id, review_count)
        game_data.update(ownership_data)

        # Estimate revenue
        price = game_data.get('price_raw', 0)
        review_score = game_data.get('review_score_raw', 0)
        owners = game_data.get('owners_avg', 0)

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

        print(f"Successfully fetched data: {game_data.get('name')} - {review_count:,} reviews")
        return game_data


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
