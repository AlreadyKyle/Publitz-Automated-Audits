"""Steam store page scraper for collecting game data."""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
import re
import json
from src.utils import clean_text, parse_price


class SteamScraper:
    """Scraper for Steam store pages."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        # Bypass age gate
        self.session.cookies.set('birthtime', '283993201', domain='store.steampowered.com')
        self.session.cookies.set('mature_content', '1', domain='store.steampowered.com')

    def scrape_game(self, app_id: str) -> Dict[str, Any]:
        """
        Scrape comprehensive data from a Steam store page.

        Args:
            app_id: Steam application ID

        Returns:
            Dictionary containing all scraped game data
        """
        store_url = f"https://store.steampowered.com/app/{app_id}/"

        # Get the HTML page
        response = self.session.get(store_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract data
        data = {
            'app_id': app_id,
            'store_url': store_url,
            'name': self._get_game_name(soup),
            'description': self._get_description(soup),
            'short_description': self._get_short_description(soup),
            'release_date': self._get_release_date(soup),
            'coming_soon': self._is_coming_soon(soup),
            'price': self._get_price(soup),
            'genres': self._get_genres(soup),
            'tags': self._get_tags(soup),
            'features': self._get_features(soup),
            'languages': self._get_languages(soup),
            'developers': self._get_developers(soup),
            'publishers': self._get_publishers(soup),
            'screenshots': self._get_screenshots(soup),
            'videos': self._get_videos(soup),
            'reviews': self._get_review_summary(soup),
            'system_requirements': self._get_system_requirements(soup),
            'capsule_image': self._get_capsule_image(app_id),
        }

        # Try to get additional data from Steam API
        api_data = self._get_api_data(app_id)
        if api_data:
            data.update(api_data)

        return data

    def _get_game_name(self, soup: BeautifulSoup) -> str:
        """Extract game name."""
        name_elem = soup.find('div', class_='apphub_AppName')
        if name_elem:
            return clean_text(name_elem.text)

        # Fallback to page title
        title_elem = soup.find('title')
        if title_elem:
            title = title_elem.text
            # Remove "on Steam" suffix
            title = re.sub(r'\s*on Steam\s*$', '', title)
            return clean_text(title)

        return "Unknown Game"

    def _get_description(self, soup: BeautifulSoup) -> str:
        """Extract full game description."""
        desc_elem = soup.find('div', class_='game_description_snippet')
        if not desc_elem:
            desc_elem = soup.find('div', id='game_area_description')

        if desc_elem:
            return clean_text(desc_elem.get_text())

        return ""

    def _get_short_description(self, soup: BeautifulSoup) -> str:
        """Extract short description."""
        desc_elem = soup.find('div', class_='game_description_snippet')
        if desc_elem:
            return clean_text(desc_elem.get_text())

        return ""

    def _get_release_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract release date."""
        date_elem = soup.find('div', class_='date')
        if date_elem:
            return clean_text(date_elem.text)

        return None

    def _is_coming_soon(self, soup: BeautifulSoup) -> bool:
        """Check if game is coming soon."""
        coming_soon = soup.find('div', class_='game_area_comingsoon')
        if coming_soon:
            return True

        release_elem = soup.find('div', class_='release_date')
        if release_elem:
            text = release_elem.get_text().lower()
            return 'coming soon' in text or 'to be announced' in text

        return False

    def _get_price(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract pricing information."""
        price_data = {
            'currency': 'USD',
            'base_price': None,
            'discount_price': None,
            'discount_percent': None,
            'is_free': False
        }

        # Check if free
        free_elem = soup.find('div', class_='game_purchase_price')
        if free_elem and 'free' in free_elem.text.lower():
            price_data['is_free'] = True
            return price_data

        # Check for discount
        discount_elem = soup.find('div', class_='discount_block')
        if discount_elem:
            # Has discount
            discount_pct = discount_elem.find('div', class_='discount_pct')
            if discount_pct:
                pct_text = discount_pct.text.strip()
                price_data['discount_percent'] = int(re.sub(r'[^\d]', '', pct_text))

            original_price = discount_elem.find('div', class_='discount_original_price')
            if original_price:
                price_data['base_price'] = parse_price(original_price.text)

            final_price = discount_elem.find('div', class_='discount_final_price')
            if final_price:
                price_data['discount_price'] = parse_price(final_price.text)
        else:
            # No discount
            price_elem = soup.find('div', class_='game_purchase_price')
            if price_elem:
                price_data['base_price'] = parse_price(price_elem.text)

        return price_data

    def _get_genres(self, soup: BeautifulSoup) -> List[str]:
        """Extract game genres."""
        genres = []
        genre_links = soup.find_all('a', href=re.compile(r'/genre/'))

        for link in genre_links:
            genre = clean_text(link.text)
            if genre and genre not in genres:
                genres.append(genre)

        return genres

    def _get_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract user tags."""
        tags = []
        tag_elems = soup.find_all('a', class_='app_tag')

        for tag_elem in tag_elems[:20]:  # Limit to top 20 tags
            tag = clean_text(tag_elem.text)
            if tag and tag not in tags:
                tags.append(tag)

        return tags

    def _get_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract game features (single-player, multiplayer, etc.)."""
        features = []
        feature_elems = soup.find_all('a', class_='game_area_details_specs_ctn')

        for elem in feature_elems:
            feature = clean_text(elem.text)
            if feature:
                features.append(feature)

        return features

    def _get_languages(self, soup: BeautifulSoup) -> List[str]:
        """Extract supported languages."""
        languages = []
        lang_table = soup.find('table', class_='game_language_options')

        if lang_table:
            rows = lang_table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cells = row.find_all('td')
                if cells:
                    lang = clean_text(cells[0].text)
                    if lang:
                        languages.append(lang)

        return languages

    def _get_developers(self, soup: BeautifulSoup) -> List[str]:
        """Extract developer names."""
        developers = []
        dev_links = soup.find_all('a', href=re.compile(r'/developer/|/publisher/'))

        # Also look in the details section
        details = soup.find('div', class_='details_block')
        if details:
            dev_section = details.find('div', id='developers_list')
            if dev_section:
                dev_links.extend(dev_section.find_all('a'))

        for link in dev_links:
            dev = clean_text(link.text)
            if dev and dev not in developers:
                developers.append(dev)

        return developers if developers else ["Unknown"]

    def _get_publishers(self, soup: BeautifulSoup) -> List[str]:
        """Extract publisher names."""
        # Often same as developers for indie games
        return self._get_developers(soup)

    def _get_screenshots(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract screenshot URLs."""
        screenshots = []
        screenshot_elems = soup.find_all('a', class_='highlight_screenshot_link')

        for elem in screenshot_elems:
            img = elem.find('img')
            if img and img.get('src'):
                screenshots.append({
                    'thumbnail': img['src'],
                    'full': elem.get('href', img['src'])
                })

        return screenshots

    def _get_videos(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract video information."""
        videos = []

        # Look for video elements
        video_section = soup.find('div', class_='highlight_player_item')
        if video_section:
            video_elem = video_section.find('div', {'data-webm-source': True})
            if video_elem:
                videos.append({
                    'type': 'webm',
                    'url': video_elem.get('data-webm-source', ''),
                    'mp4_url': video_elem.get('data-mp4-source', '')
                })

        return videos

    def _get_review_summary(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract review summary information."""
        review_data = {
            'summary': None,
            'total_reviews': 0,
            'positive_percent': None
        }

        # Find review summary
        review_elem = soup.find('span', class_='game_review_summary')
        if review_elem:
            review_data['summary'] = clean_text(review_elem.text)

        # Find review count
        review_count_elem = soup.find('meta', {'itemprop': 'reviewCount'})
        if review_count_elem and review_count_elem.get('content'):
            try:
                review_data['total_reviews'] = int(review_count_elem['content'])
            except ValueError:
                pass

        return review_data

    def _get_system_requirements(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract system requirements."""
        requirements = {}

        req_sections = soup.find_all('div', class_='game_area_sys_req')
        for section in req_sections:
            platform = 'windows'  # Default
            title = section.find('div', class_='sysreq_tab')
            if title:
                platform = clean_text(title.text).lower()

            req_text = clean_text(section.get_text())
            requirements[platform] = req_text

        return requirements

    def _get_capsule_image(self, app_id: str) -> str:
        """Get main capsule image URL."""
        return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"

    def _get_api_data(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get additional data from Steam API."""
        try:
            url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
            response = self.session.get(url)
            data = response.json()

            if data.get(app_id, {}).get('success'):
                api_data = data[app_id]['data']
                return {
                    'api_genres': [g['description'] for g in api_data.get('genres', [])],
                    'api_categories': [c['description'] for c in api_data.get('categories', [])],
                    'metacritic_score': api_data.get('metacritic', {}).get('score'),
                    'recommendations': api_data.get('recommendations', {}).get('total'),
                }
        except Exception as e:
            print(f"Error fetching API data: {e}")

        return None
