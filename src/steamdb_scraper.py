"""SteamDB scraper for competitive and market data."""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
import re
from src.utils import clean_text, parse_price


class SteamDBScraper:
    """Scraper for SteamDB data."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.base_url = "https://steamdb.info"

    def scrape_game_data(self, app_id: str) -> Dict[str, Any]:
        """
        Scrape SteamDB data for a game.

        Args:
            app_id: Steam application ID

        Returns:
            Dictionary containing SteamDB data
        """
        url = f"{self.base_url}/app/{app_id}/"

        try:
            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            data = {
                'app_id': app_id,
                'followers': self._get_followers(soup),
                'peak_players': self._get_peak_players(soup),
                'price_history': self._get_price_history(soup),
                'rating': self._get_rating(soup),
                'tag_rankings': self._get_tag_rankings(soup),
            }

            return data

        except Exception as e:
            print(f"Error scraping SteamDB: {e}")
            return {'app_id': app_id, 'error': str(e)}

    def search_similar_games(self, tags: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar games based on tags.

        Args:
            tags: List of game tags
            limit: Maximum number of results

        Returns:
            List of similar games with metadata
        """
        similar_games = []

        # Use the first few tags to search
        search_tags = tags[:3] if len(tags) > 3 else tags

        for tag in search_tags:
            try:
                # Search by tag
                search_url = f"{self.base_url}/search/?q={tag.replace(' ', '+')}&type=app"
                response = self.session.get(search_url)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    results = self._parse_search_results(soup, limit=limit)
                    similar_games.extend(results)

                    if len(similar_games) >= limit:
                        break

            except Exception as e:
                print(f"Error searching for tag '{tag}': {e}")
                continue

        # Remove duplicates and limit
        seen_ids = set()
        unique_games = []
        for game in similar_games:
            if game['app_id'] not in seen_ids:
                seen_ids.add(game['app_id'])
                unique_games.append(game)

            if len(unique_games) >= limit:
                break

        return unique_games

    def get_tag_data(self, tag_name: str) -> Dict[str, Any]:
        """
        Get data about a specific tag.

        Args:
            tag_name: Name of the tag

        Returns:
            Tag data including follower count and top games
        """
        try:
            # SteamDB tag pages
            tag_url = f"{self.base_url}/tag/{tag_name.lower().replace(' ', '-')}/"
            response = self.session.get(tag_url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                return {
                    'tag_name': tag_name,
                    'follower_count': self._extract_follower_count(soup),
                    'total_games': self._extract_total_games(soup),
                }

        except Exception as e:
            print(f"Error getting tag data: {e}")

        return {'tag_name': tag_name, 'follower_count': None, 'total_games': None}

    def get_upcoming_releases(self, genre: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get upcoming game releases.

        Args:
            genre: Optional genre filter
            days: Number of days to look ahead

        Returns:
            List of upcoming games
        """
        upcoming = []

        try:
            url = f"{self.base_url}/upcoming/"
            response = self.session.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                upcoming = self._parse_upcoming_releases(soup, limit=20)

        except Exception as e:
            print(f"Error getting upcoming releases: {e}")

        return upcoming

    def _get_followers(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract follower/wishlist count."""
        # Look for followers/wishlist data
        followers_elem = soup.find('span', {'itemprop': 'aggregateRating'})
        if followers_elem:
            text = followers_elem.get_text()
            numbers = re.findall(r'[\d,]+', text)
            if numbers:
                try:
                    return int(numbers[0].replace(',', ''))
                except ValueError:
                    pass

        # Alternative: look in stats table
        stats_table = soup.find('table', class_='table-products')
        if stats_table:
            for row in stats_table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label = clean_text(cells[0].text).lower()
                    if 'follower' in label or 'wishlist' in label:
                        value_text = cells[1].text
                        numbers = re.findall(r'[\d,]+', value_text)
                        if numbers:
                            try:
                                return int(numbers[0].replace(',', ''))
                            except ValueError:
                                pass

        return None

    def _get_peak_players(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract peak player counts."""
        peak_data = {
            'all_time': None,
            'last_24h': None
        }

        # Look for player count data
        player_elems = soup.find_all('div', class_='header-thing')
        for elem in player_elems:
            text = elem.get_text().lower()
            if 'peak' in text or 'players' in text:
                numbers = re.findall(r'[\d,]+', text)
                if numbers:
                    try:
                        count = int(numbers[0].replace(',', ''))
                        if 'all' in text or 'time' in text:
                            peak_data['all_time'] = count
                        else:
                            peak_data['last_24h'] = count
                    except ValueError:
                        pass

        return peak_data

    def _get_price_history(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract price history information."""
        price_data = {
            'lowest_price': None,
            'highest_discount': None,
            'last_discount': None
        }

        # Price information is often in charts/tables
        price_section = soup.find('div', class_='prices')
        if price_section:
            # Extract price information
            price_texts = price_section.find_all('span', class_='price')
            for price_elem in price_texts:
                price = parse_price(price_elem.text)
                if price:
                    if price_data['lowest_price'] is None or price < price_data['lowest_price']:
                        price_data['lowest_price'] = price

        return price_data

    def _get_rating(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract SteamDB rating if available."""
        rating_elem = soup.find('span', class_='rating')
        if rating_elem:
            return clean_text(rating_elem.text)

        return None

    def _get_tag_rankings(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Extract tag rankings (position in tag leaderboards)."""
        rankings = {}

        # Look for tag links with rankings
        tag_links = soup.find_all('a', href=re.compile(r'/tag/'))
        for link in tag_links:
            tag_name = clean_text(link.text)
            # Look for ranking number near the tag
            parent = link.parent
            if parent:
                rank_text = parent.get_text()
                rank_match = re.search(r'#(\d+)', rank_text)
                if rank_match:
                    rankings[tag_name] = int(rank_match.group(1))

        return rankings

    def _parse_search_results(self, soup: BeautifulSoup, limit: int = 5) -> List[Dict[str, Any]]:
        """Parse search results page."""
        results = []

        # Find result rows
        result_rows = soup.find_all('tr', class_='app')[:limit]

        for row in result_rows:
            app_link = row.find('a', href=re.compile(r'/app/\d+/'))
            if app_link:
                app_id_match = re.search(r'/app/(\d+)/', app_link['href'])
                if app_id_match:
                    app_id = app_id_match.group(1)

                    # Extract name
                    name = clean_text(app_link.text)

                    # Extract price if available
                    price_elem = row.find('td', class_='price')
                    price = None
                    if price_elem:
                        price = parse_price(price_elem.text)

                    results.append({
                        'app_id': app_id,
                        'name': name,
                        'price': price,
                        'url': f"https://store.steampowered.com/app/{app_id}/"
                    })

        return results

    def _extract_follower_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract follower count from tag page."""
        # Look for follower statistics
        stat_elem = soup.find('span', class_='followers')
        if stat_elem:
            text = stat_elem.get_text()
            numbers = re.findall(r'[\d,]+', text)
            if numbers:
                try:
                    return int(numbers[0].replace(',', ''))
                except ValueError:
                    pass

        return None

    def _extract_total_games(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract total games count from tag page."""
        # Look for game count
        count_elem = soup.find('span', class_='tag-count')
        if count_elem:
            text = count_elem.get_text()
            numbers = re.findall(r'[\d,]+', text)
            if numbers:
                try:
                    return int(numbers[0].replace(',', ''))
                except ValueError:
                    pass

        return None

    def _parse_upcoming_releases(self, soup: BeautifulSoup, limit: int = 20) -> List[Dict[str, Any]]:
        """Parse upcoming releases page."""
        upcoming = []

        # Find upcoming game rows
        game_rows = soup.find_all('tr', class_='app')[:limit]

        for row in game_rows:
            app_link = row.find('a', href=re.compile(r'/app/\d+/'))
            if app_link:
                app_id_match = re.search(r'/app/(\d+)/', app_link['href'])
                if app_id_match:
                    app_id = app_id_match.group(1)
                    name = clean_text(app_link.text)

                    # Extract release date
                    date_elem = row.find('td', class_='date')
                    release_date = None
                    if date_elem:
                        release_date = clean_text(date_elem.text)

                    # Extract follower estimate
                    follower_elem = row.find('td', class_='followers')
                    followers = None
                    if follower_elem:
                        follower_text = follower_elem.get_text()
                        numbers = re.findall(r'[\d,]+', follower_text)
                        if numbers:
                            try:
                                followers = int(numbers[0].replace(',', ''))
                            except ValueError:
                                pass

                    upcoming.append({
                        'app_id': app_id,
                        'name': name,
                        'release_date': release_date,
                        'estimated_followers': followers,
                        'url': f"https://store.steampowered.com/app/{app_id}/"
                    })

        return upcoming
