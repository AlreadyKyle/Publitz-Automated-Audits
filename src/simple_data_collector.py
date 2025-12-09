"""
Simplified Data Collector - Gather all data needed for audit report

Uses existing Steam API integrations but simplified flow:
1. Fetch game data from Steam
2. Fetch competitor data
3. External research (Reddit, HLTB, SteamDB)
4. Vision analysis (capsule/screenshots)
"""

import requests
import time
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Import existing Steam utilities
from src.game_search import GameSearch
from src.steamdb_scraper import SteamDBScraper
from config import Config


class SimpleDataCollector:
    """Simplified data collection for audit generation"""

    def __init__(self):
        self.game_search = GameSearch()
        self.steamdb_scraper = SteamDBScraper()

    def collect_all_data(
        self,
        steam_url: str,
        app_id: str,
        competitors: List[str],
        intake_form: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Collect all data needed for the audit report.

        Returns comprehensive dict with:
        - game: Main game data
        - competitors: List of competitor data
        - external_research: Reddit, HLTB, SteamDB insights
        - client_context: Intake form + derived info
        """
        print("\n" + "="*80)
        print("📊 DATA COLLECTION PHASE")
        print("="*80)

        data = {}

        # 1. Fetch main game data
        print("\n[1/4] Fetching main game data...")
        data['game'] = self._fetch_game_data(steam_url, app_id)
        print(f"✅ Loaded: {data['game']['name']}")

        # 2. Fetch competitor data
        print(f"\n[2/4] Fetching {len(competitors)} competitors...")
        data['competitors'] = self._fetch_competitors(competitors)
        print(f"✅ Loaded {len(data['competitors'])} competitor games")

        # 3. External research
        print("\n[3/4] Conducting external research...")
        data['external_research'] = self._external_research(
            data['game'],
            data['competitors'],
            intake_form
        )
        print("✅ External research complete")

        # 4. Client context
        print("\n[4/4] Processing client context...")
        data['client_context'] = self._process_client_context(
            intake_form,
            data['game']
        )
        print("✅ Client context processed")

        print("\n" + "="*80)
        print("✅ DATA COLLECTION COMPLETE")
        print("="*80 + "\n")

        return data

    def _fetch_game_data(self, steam_url: str, app_id: str) -> Dict[str, Any]:
        """Fetch comprehensive data for the main game"""
        # Use existing GameSearch to get game data
        game_data = self.game_search.get_game_from_url(steam_url)

        if not game_data:
            raise ValueError(f"Could not fetch game data from Steam (App ID: {app_id})")

        # Get additional data from SteamDB scraper
        try:
            sales_data = self.steamdb_scraper.get_sales_data(app_id)
            game_data['sales_data'] = sales_data
        except Exception as e:
            print(f"⚠️  Warning: Could not fetch sales data: {e}")
            game_data['sales_data'] = {}

        # Get review stats
        try:
            review_stats = self.steamdb_scraper.get_review_stats(app_id)
            game_data['review_stats'] = review_stats
        except Exception as e:
            print(f"⚠️  Warning: Could not fetch review stats: {e}")
            game_data['review_stats'] = {}

        return game_data

    def _fetch_competitors(self, competitor_names: List[str]) -> List[Dict[str, Any]]:
        """Fetch data for all competitors"""
        competitors = []

        for i, comp_name in enumerate(competitor_names, 1):
            print(f"  [{i}/{len(competitor_names)}] {comp_name}...", end=" ")

            try:
                # Search for competitor by name
                comp_data = self.game_search.search_game_by_name(comp_name)

                if comp_data:
                    # Get additional data
                    app_id = comp_data.get('app_id')
                    if app_id:
                        try:
                            sales_data = self.steamdb_scraper.get_sales_data(str(app_id))
                            comp_data['sales_data'] = sales_data
                        except:
                            comp_data['sales_data'] = {}

                    # Get HLTB data
                    comp_data['playtime'] = self._fetch_howlongtobeat(comp_name)

                    competitors.append(comp_data)
                    print("✅")
                else:
                    print("❌ Not found")

            except Exception as e:
                print(f"❌ Error: {e}")

            # Rate limiting
            time.sleep(1)

        return competitors

    def _external_research(
        self,
        game_data: Dict[str, Any],
        competitors: List[Dict[str, Any]],
        intake_form: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Conduct external research using free APIs.

        Gathers:
        - Reddit genre insights
        - HLTB playtime data
        - SteamDB launch conflicts
        - Tag popularity
        """
        research = {}

        # Get genres for research
        genres = game_data.get('genres', [])
        main_genre = genres[0] if genres else 'indie'

        # 1. Reddit insights
        print("  - Reddit genre insights...", end=" ")
        try:
            research['reddit'] = self._fetch_reddit_insights(main_genre)
            print("✅")
        except Exception as e:
            print(f"⚠️  {e}")
            research['reddit'] = {}

        # 2. HowLongToBeat for main game
        print("  - HowLongToBeat data...", end=" ")
        try:
            research['hltb'] = self._fetch_howlongtobeat(game_data['name'])
            print("✅")
        except Exception as e:
            print(f"⚠️  {e}")
            research['hltb'] = {}

        # 3. Launch window conflicts
        print("  - Launch window analysis...", end=" ")
        try:
            launch_date = intake_form.get('launch_date')
            if launch_date:
                research['launch_conflicts'] = self._check_launch_conflicts(
                    launch_date,
                    genres
                )
                print("✅")
            else:
                print("⚠️  No launch date provided")
                research['launch_conflicts'] = []
        except Exception as e:
            print(f"⚠️  {e}")
            research['launch_conflicts'] = []

        # 4. Tag analysis
        print("  - Tag popularity analysis...", end=" ")
        try:
            tags = game_data.get('tags', [])
            research['tag_analysis'] = self._analyze_tags(tags)
            print("✅")
        except Exception as e:
            print(f"⚠️  {e}")
            research['tag_analysis'] = {}

        return research

    def _fetch_reddit_insights(self, genre: str) -> Dict[str, Any]:
        """
        Fetch genre insights from Reddit.

        Free API: https://www.reddit.com/r/{subreddit}/search.json
        """
        # Map genre to likely subreddit
        genre_lower = genre.lower()
        subreddit = f"{genre_lower}gaming"

        # Try specific genre subreddit first, fall back to IndieGaming
        subreddits = [subreddit, 'IndieGaming', 'gaming']

        insights = {
            'subreddit': None,
            'top_discussions': [],
            'common_themes': []
        }

        for sr in subreddits:
            try:
                url = f"https://www.reddit.com/r/{sr}/search.json"
                params = {
                    'q': f'{genre} game',
                    'sort': 'top',
                    'limit': 10,
                    't': 'month'
                }
                headers = {'User-Agent': 'Publitz Audit Bot 1.0'}

                response = requests.get(url, params=params, headers=headers, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])

                    if posts:
                        insights['subreddit'] = sr
                        insights['top_discussions'] = [
                            {
                                'title': post['data']['title'],
                                'score': post['data']['score'],
                                'url': f"https://reddit.com{post['data']['permalink']}"
                            }
                            for post in posts[:5]
                        ]
                        break

            except Exception as e:
                continue

        return insights

    def _fetch_howlongtobeat(self, game_name: str) -> Dict[str, Any]:
        """
        Fetch playtime data from HowLongToBeat.

        Note: HLTB doesn't have a public API, so this scrapes their search.
        """
        try:
            # Search HLTB
            search_url = "https://howlongtobeat.com/api/search"
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/json'
            }
            payload = {
                'searchType': 'games',
                'searchTerms': [game_name],
                'searchPage': 1,
                'size': 1
            }

            response = requests.post(search_url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                games = data.get('data', [])

                if games:
                    game = games[0]
                    return {
                        'found': True,
                        'main_story': game.get('comp_main', 0) / 3600,  # Convert seconds to hours
                        'main_extras': game.get('comp_plus', 0) / 3600,
                        'completionist': game.get('comp_100', 0) / 3600
                    }

        except Exception as e:
            pass

        return {'found': False}

    def _check_launch_conflicts(
        self,
        launch_date: str,
        genres: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Check for launch window conflicts on SteamDB.

        Looks for games launching ±2 weeks in same genre.
        """
        conflicts = []

        try:
            # Parse launch date
            launch = datetime.strptime(launch_date, '%Y-%m-%d')
            window_start = launch - timedelta(days=14)
            window_end = launch + timedelta(days=14)

            # Note: SteamDB /upcoming doesn't have a free API
            # This would require web scraping or manual input
            # For MVP, return empty list

            # TODO: Implement SteamDB upcoming scraper
            # url = "https://steamdb.info/upcoming/"
            # ... scrape and filter by date range and genres

        except Exception as e:
            print(f"⚠️  Launch conflict check failed: {e}")

        return conflicts

    def _analyze_tags(self, tags: List[str]) -> Dict[str, Any]:
        """
        Analyze tag popularity and relevance.

        Returns high-traffic tags vs low-traffic tags.
        """
        # This would ideally query SteamDB for tag follower counts
        # For MVP, return basic analysis

        return {
            'tags_provided': tags,
            'tag_count': len(tags),
            'analysis': 'Tag analysis requires SteamDB scraping (not implemented in MVP)'
        }

    def _process_client_context(
        self,
        intake_form: Dict[str, Any],
        game_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process client context from intake form.

        Calculates days until launch, budget tier, team size category, etc.
        """
        context = {**intake_form}  # Copy all intake form data

        # Calculate days until launch
        if 'launch_date' in intake_form:
            try:
                launch = datetime.strptime(intake_form['launch_date'], '%Y-%m-%d')
                today = datetime.now()
                days_until = (launch - today).days
                context['days_until_launch'] = days_until

                if days_until < 0:
                    context['launch_status'] = 'post-launch'
                    context['days_since_launch'] = abs(days_until)
                elif days_until < 7:
                    context['launch_status'] = 'imminent'
                elif days_until < 30:
                    context['launch_status'] = 'near-term'
                else:
                    context['launch_status'] = 'pre-launch'

            except ValueError:
                context['days_until_launch'] = None
                context['launch_status'] = 'unknown'

        # Classify budget tier
        budget = intake_form.get('marketing_budget', 'Limited')
        if 'Limited' in budget or '<' in budget:
            context['budget_tier'] = 'limited'
        elif '>10' in budget or 'Large' in budget:
            context['budget_tier'] = 'large'
        else:
            context['budget_tier'] = 'moderate'

        # Classify team size
        team_size = intake_form.get('team_size', 1)
        if team_size == 1:
            context['team_category'] = 'solo'
        elif team_size <= 3:
            context['team_category'] = 'micro'
        elif team_size <= 10:
            context['team_category'] = 'small'
        else:
            context['team_category'] = 'medium'

        return context


if __name__ == "__main__":
    """Test data collector"""
    from src.input_processor import InputProcessor
    from pathlib import Path

    try:
        # Load example inputs
        inputs = InputProcessor.load_inputs_from_directory(
            Path("inputs/example-client")
        )

        # Collect data
        collector = SimpleDataCollector()
        data = collector.collect_all_data(
            steam_url=inputs.steam_url,
            app_id=inputs.app_id,
            competitors=inputs.competitors[:3],  # Limit to 3 for testing
            intake_form=inputs.intake_form
        )

        print("\n✅ Data collection successful!")
        print(f"\nGame: {data['game']['name']}")
        print(f"Competitors collected: {len(data['competitors'])}")
        print(f"Launch status: {data['client_context']['launch_status']}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
