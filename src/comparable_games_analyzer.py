"""
Comparable Games Analyzer

Finds and analyzes comparable games to provide meaningful competitive context.
Instead of abstract percentiles, shows specific games and actionable tactics.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import requests
from dataclasses import dataclass
import time

from src.game_search import GameSearch
from src.game_analyzer import GameAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class ComparableGame:
    """Data class for a comparable game with all comparison metrics"""
    app_id: str
    name: str
    overall_score: float
    review_count: int
    review_percentage: float
    estimated_revenue: int
    revenue_display: str
    tags: List[str]
    launch_date: str
    price: float
    owners_avg: int
    success_tactics: List[str] = None
    key_differences: Dict[str, Any] = None


@dataclass
class RecoveryStory:
    """Data class for a game that improved over time"""
    app_id: str
    name: str
    before_score: float
    after_score: float
    before_reviews: int
    after_reviews: int
    before_percentage: float
    after_percentage: float
    timeframe_months: int
    changes_made: List[str]
    key_takeaway: str
    how_to_apply: str


class ComparableGamesAnalyzer:
    """
    Finds and analyzes comparable games to provide actionable competitive insights.

    Instead of "You're in the 45th percentile", provides:
    "Game X is similar to yours but has 3x revenue because they did Y"
    """

    def __init__(self):
        """Initialize with game search capabilities"""
        self.game_search = GameSearch()
        self.analyzer = GameAnalyzer()

    def find_comparable_games(
        self,
        target_game_id: str,
        genre_tags: List[str],
        price: float,
        launch_date: str,
        owner_count: int,
        limit: int = 15
    ) -> List[ComparableGame]:
        """
        Find comparable games using strict matching criteria.

        Matching criteria (all must match):
        - Same primary genre tag
        - Similar price point (±$10)
        - Similar launch window (±6 months)
        - Similar owner count tier (within same order of magnitude)

        Args:
            target_game_id: Steam app ID of the target game
            genre_tags: List of genre tags (first is primary)
            price: Game price in USD
            launch_date: Launch date string (YYYY-MM-DD or similar)
            owner_count: Number of owners
            limit: Maximum number of comparable games to return

        Returns:
            List of ComparableGame objects
        """
        logger.info(f"Finding comparable games for app_id {target_game_id}")
        logger.info(f"Criteria: Genre={genre_tags[0] if genre_tags else 'N/A'}, Price=${price}, Owners={owner_count:,}")

        # Parse launch date
        try:
            target_launch = self._parse_date(launch_date)
        except Exception as e:
            logger.warning(f"Could not parse launch date '{launch_date}': {e}")
            target_launch = datetime.now()

        # Determine owner count tier (order of magnitude)
        owner_tier = self._get_owner_tier(owner_count)

        # Get primary genre for matching
        primary_genre = genre_tags[0].lower() if genre_tags else None
        if not primary_genre:
            logger.warning("No genre tags provided, matching will be less accurate")

        # Search for games using SteamSpy (better for bulk searches)
        comparable_games = []

        # Try to find games by genre tag using existing game_search methods
        if primary_genre:
            logger.info(f"Searching for {primary_genre} games...")
            # Use the game_search._find_by_genre method
            genre_games = self.game_search._find_by_genre(primary_genre, limit * 3)
            tag_games = self._filter_by_criteria(genre_games, price, target_launch, owner_tier, target_game_id)
            comparable_games.extend(tag_games)

        # If we don't have enough, try tag search
        if len(comparable_games) < limit and genre_list:
            logger.info(f"Found {len(comparable_games)} games, trying tag search...")
            tag = genre_list[0] if isinstance(genre_list[0], str) else genre_list[0].get('description', '')
            tag_results = self.game_search._find_by_tag(tag, limit * 2)
            additional_games = self._filter_by_criteria(tag_results, price, target_launch, owner_tier, target_game_id)
            comparable_games.extend(additional_games)

        # Remove duplicates by app_id
        seen_ids = set()
        unique_games = []
        for game in comparable_games:
            if game.app_id not in seen_ids and game.app_id != target_game_id:
                seen_ids.add(game.app_id)
                unique_games.append(game)

        # Sort by relevance (score descending)
        unique_games.sort(key=lambda g: g.overall_score, reverse=True)

        # Return top N
        result = unique_games[:limit]
        logger.info(f"Found {len(result)} comparable games")

        return result

    def _filter_by_criteria(
        self,
        games: List[Dict[str, Any]],
        target_price: float,
        target_launch: datetime,
        target_owner_tier: str,
        exclude_app_id: str
    ) -> List[ComparableGame]:
        """
        Filter games by matching criteria and convert to ComparableGame objects.

        Filters:
        - Price within ±$10
        - Owner tier matches
        - Launch date within ±6 months
        """
        filtered_games = []

        for game_data in games:
            try:
                app_id = str(game_data.get('app_id', ''))

                # Skip target game
                if app_id == str(exclude_app_id):
                    continue

                # Get game price
                game_price = game_data.get('price_raw', 0)
                if isinstance(game_price, str):
                    try:
                        game_price = float(game_price.replace('$', '').replace(',', ''))
                    except:
                        game_price = 0

                # Price filter (±$10)
                if abs(game_price - target_price) > 10:
                    continue

                # Get owners from SteamSpy data
                spy_data = self.game_search.get_steamspy_data(int(app_id))
                owners_str = spy_data.get('owners', '0 .. 0')
                owners_avg = self._parse_owners_range(owners_str)
                game_tier = self._get_owner_tier(owners_avg)

                # Owner tier filter
                if game_tier != target_owner_tier:
                    continue

                # Launch date filter (±6 months)
                release_date = game_data.get('release_date', '')
                try:
                    game_launch = self._parse_date(release_date)
                    months_diff = abs((game_launch - target_launch).days / 30)
                    if months_diff > 6:
                        continue
                except:
                    # If we can't parse date, be lenient
                    pass

                # Build ComparableGame object
                comparable = self._build_comparable_game_from_game_data(game_data, spy_data)
                if comparable:
                    filtered_games.append(comparable)

            except Exception as e:
                logger.debug(f"Error filtering game: {e}")
                continue

        return filtered_games

    def _build_comparable_game_from_game_data(
        self,
        game_data: Dict[str, Any],
        spy_data: Dict[str, Any]
    ) -> Optional[ComparableGame]:
        """Build a ComparableGame object from game_search data"""
        try:
            app_id = str(game_data.get('app_id', ''))
            name = game_data.get('name', 'Unknown')

            # Get review data from game_data (already formatted by game_search)
            review_percentage = game_data.get('review_score_raw', 0)
            review_count = game_data.get('review_count', 0)

            # If we don't have review data, try spy_data
            if review_count == 0 and spy_data:
                positive = spy_data.get('positive', 0)
                negative = spy_data.get('negative', 0)
                review_count = positive + negative
                review_percentage = (positive / review_count * 100) if review_count > 0 else 0

            # Get owners
            owners_str = spy_data.get('owners', '0 .. 0')
            owners_avg = self._parse_owners_range(owners_str)

            # Calculate overall score using same system as target game
            overall_score = review_percentage * 0.7
            if owners_avg > 100000:
                overall_score += 15
            elif owners_avg > 50000:
                overall_score += 10
            elif owners_avg > 10000:
                overall_score += 5
            overall_score = min(100, max(0, overall_score))

            # Get price
            price = game_data.get('price_raw', 0)
            if isinstance(price, str):
                try:
                    price = float(price.replace('$', '').replace(',', ''))
                except:
                    price = 0

            # Estimate revenue (simplified)
            estimated_revenue = int(owners_avg * price * 0.5)  # Assume 50% bought at full price

            # Format revenue
            if estimated_revenue >= 1000000:
                revenue_display = f"${estimated_revenue / 1000000:.1f}M"
            elif estimated_revenue >= 1000:
                revenue_display = f"${estimated_revenue / 1000:.0f}K"
            else:
                revenue_display = f"${estimated_revenue}"

            # Get tags (already formatted by game_search)
            tags = game_data.get('tags', [])
            if isinstance(tags, list):
                tag_list = [str(t) for t in tags[:10]]
            else:
                tag_list = []

            # Launch date
            launch_date = game_data.get('release_date', 'Unknown')

            return ComparableGame(
                app_id=app_id,
                name=name,
                overall_score=overall_score,
                review_count=review_count,
                review_percentage=review_percentage,
                estimated_revenue=estimated_revenue,
                revenue_display=revenue_display,
                tags=tag_list,
                launch_date=launch_date,
                price=price,
                owners_avg=owners_avg
            )

        except Exception as e:
            logger.debug(f"Error building comparable game: {e}")
            return None

    def _parse_owners_range(self, owners_str: str) -> int:
        """Parse SteamSpy owners range (e.g., '10000 .. 20000') to average"""
        try:
            if '..' in owners_str:
                parts = owners_str.split('..')
                low = int(parts[0].strip().replace(',', ''))
                high = int(parts[1].strip().replace(',', ''))
                return (low + high) // 2
            else:
                return int(owners_str.replace(',', ''))
        except:
            return 0

    def _get_owner_tier(self, owner_count: int) -> str:
        """Determine owner tier (order of magnitude)"""
        if owner_count >= 1000000:
            return "1M+"
        elif owner_count >= 500000:
            return "500K-1M"
        elif owner_count >= 100000:
            return "100K-500K"
        elif owner_count >= 50000:
            return "50K-100K"
        elif owner_count >= 10000:
            return "10K-50K"
        elif owner_count >= 5000:
            return "5K-10K"
        elif owner_count >= 1000:
            return "1K-5K"
        else:
            return "<1K"

    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats to datetime"""
        if not date_str:
            return datetime.now()

        # Try common formats
        formats = [
            '%Y-%m-%d',
            '%b %d, %Y',
            '%B %d, %Y',
            '%d %b, %Y',
            '%d %B, %Y',
            '%Y/%m/%d',
            '%m/%d/%Y'
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except:
                continue

        # If all fail, return current date
        logger.debug(f"Could not parse date: {date_str}")
        return datetime.now()

    def generate_comparison_table(
        self,
        target_game: ComparableGame,
        comparable_games: List[ComparableGame],
        genre: str,
        price_range: str,
        year: str
    ) -> str:
        """
        Generate markdown comparison table showing how target compares to similar games.

        Args:
            target_game: The target game to compare
            comparable_games: List of comparable games
            genre: Genre for context (e.g., "Roguelike")
            price_range: Price range for context (e.g., "$15-$25")
            year: Launch year for context

        Returns:
            Markdown formatted comparison analysis
        """
        # Separate into higher and lower performers
        higher_performers = [g for g in comparable_games if g.overall_score > target_game.overall_score + 5]
        similar_performers = [g for g in comparable_games if abs(g.overall_score - target_game.overall_score) <= 5]
        lower_performers = [g for g in comparable_games if g.overall_score < target_game.overall_score - 5]

        # Sort
        higher_performers.sort(key=lambda g: g.overall_score, reverse=True)
        lower_performers.sort(key=lambda g: g.overall_score, reverse=True)

        # Build markdown
        md = f"""## How You Compare to Similar Games

### Games Like Yours ({genre}, {price_range}, {year} Launch)

| Game | Score | Reviews | Est. Revenue | What They Did Right |
|------|-------|---------|--------------|---------------------|
| **{target_game.name}** | **{target_game.overall_score:.0f}/100** | **{target_game.review_count:,} ({target_game.review_percentage:.0f}%)** | **{target_game.revenue_display}** | Your baseline |
"""

        # Add top performers
        for game in higher_performers[:3]:
            tactic = self._infer_success_tactic(game, target_game)
            md += f"| {game.name} | {game.overall_score:.0f}/100 | {game.review_count:,} ({game.review_percentage:.0f}%) | {game.revenue_display} | {tactic} |\n"

        # Add similar performers
        for game in similar_performers[:2]:
            md += f"| {game.name} | {game.overall_score:.0f}/100 | {game.review_count:,} ({game.review_percentage:.0f}%) | {game.revenue_display} | Similar trajectory |\n"

        # Add lower performers
        for game in lower_performers[:2]:
            warning = self._infer_warning_sign(game, target_game)
            md += f"| {game.name} | {game.overall_score:.0f}/100 | {game.review_count:,} ({game.review_percentage:.0f}%) | {game.revenue_display} | {warning} |\n"

        # Add detailed analysis for top performers
        if higher_performers:
            md += "\n### Key Learnings from Higher Performers\n\n"

            for i, game in enumerate(higher_performers[:2], 1):
                revenue_multiplier = game.estimated_revenue / target_game.estimated_revenue if target_game.estimated_revenue > 0 else 0
                md += f"**What {game.name} ({game.overall_score:.0f}/100) did that you haven't**:\n"
                md += f"- They have {revenue_multiplier:.1f}x your revenue (${game.revenue_display} vs {target_game.revenue_display})\n"
                md += f"- Review score: {game.review_percentage:.0f}% vs your {target_game.review_percentage:.0f}% (+{game.review_percentage - target_game.review_percentage:.0f} points)\n"
                md += f"- Review volume: {game.review_count:,} vs your {target_game.review_count:,} ({game.review_count / target_game.review_count if target_game.review_count > 0 else 0:.1f}x more engagement)\n"

                # Identify tag differences
                target_tags_set = set(target_game.tags)
                game_tags_set = set(game.tags)
                unique_tags = game_tags_set - target_tags_set
                if unique_tags:
                    md += f"- Tags they use that you don't: {', '.join(list(unique_tags)[:5])}\n"

                md += f"- [View their store page](https://store.steampowered.com/app/{game.app_id})\n\n"

        # Add warnings from lower performers
        if lower_performers:
            md += "### Warning Signs from Lower Performers\n\n"

            for game in lower_performers[:1]:
                md += f"**{game.name} ({game.overall_score:.0f}/100) made these mistakes**:\n"
                md += f"- Review score only {game.review_percentage:.0f}% (vs your {target_game.review_percentage:.0f}%)\n"
                md += f"- Limited market traction: {game.review_count:,} reviews\n"
                md += f"- Revenue estimate: {game.revenue_display} (you're doing better)\n"
                md += f"- **How to avoid**: Maintain your review quality and continue engagement efforts\n\n"

        return md

    def _infer_success_tactic(self, game: ComparableGame, target: ComparableGame) -> str:
        """Infer what made a higher-performing game successful"""
        # Compare metrics to infer tactics
        if game.review_percentage > target.review_percentage + 10:
            return "Superior quality/polish"
        elif game.review_count > target.review_count * 3:
            return "Strong marketing/visibility"
        elif game.price < target.price * 0.7:
            return "Aggressive pricing"
        else:
            return "Better execution overall"

    def _infer_warning_sign(self, game: ComparableGame, target: ComparableGame) -> str:
        """Infer what went wrong with a lower-performing game"""
        if game.review_percentage < 70:
            return "Quality issues (low reviews)"
        elif game.review_count < 100:
            return "Poor visibility/marketing"
        elif game.price > target.price * 1.5:
            return "Overpriced for market"
        else:
            return "Weak execution"

    def identify_success_patterns(
        self,
        target_game: ComparableGame,
        higher_performers: List[ComparableGame]
    ) -> Dict[str, Any]:
        """
        Identify patterns from games scoring 15-25 points higher.

        Analyzes:
        - Tag differences
        - Price positioning
        - Review velocity patterns
        - Store page differences

        Returns actionable tactics to copy.
        """
        patterns = {
            'common_tags_missing': [],
            'price_insights': {},
            'review_velocity_patterns': [],
            'actionable_tactics': []
        }

        # Filter to games 15-25 points higher
        significantly_higher = [
            g for g in higher_performers
            if 15 <= (g.overall_score - target_game.overall_score) <= 25
        ]

        if not significantly_higher:
            # Broaden to any higher performers
            significantly_higher = [g for g in higher_performers if g.overall_score > target_game.overall_score + 10]

        if not significantly_higher:
            return patterns

        # Analyze tags
        target_tags = set(target_game.tags)
        tag_frequency = {}

        for game in significantly_higher:
            for tag in game.tags:
                if tag not in target_tags:
                    tag_frequency[tag] = tag_frequency.get(tag, 0) + 1

        # Find tags that appear in >50% of higher performers
        threshold = len(significantly_higher) * 0.5
        common_missing_tags = [tag for tag, count in tag_frequency.items() if count >= threshold]
        patterns['common_tags_missing'] = common_missing_tags[:5]

        # Analyze pricing
        avg_price = sum(g.price for g in significantly_higher) / len(significantly_higher)
        patterns['price_insights'] = {
            'average_price': avg_price,
            'target_price': target_game.price,
            'recommendation': 'lower' if target_game.price > avg_price * 1.2 else 'maintain' if abs(target_game.price - avg_price) < avg_price * 0.2 else 'raise'
        }

        # Analyze review velocity (review count as proxy)
        avg_reviews = sum(g.review_count for g in significantly_higher) / len(significantly_higher)
        velocity_ratio = avg_reviews / target_game.review_count if target_game.review_count > 0 else 0

        patterns['review_velocity_patterns'] = {
            'average_reviews': int(avg_reviews),
            'target_reviews': target_game.review_count,
            'velocity_ratio': velocity_ratio,
            'interpretation': f"Higher performers have {velocity_ratio:.1f}x more reviews on average"
        }

        # Generate actionable tactics
        tactics = []

        if common_missing_tags:
            tactics.append(f"Add these high-performing tags: {', '.join(common_missing_tags)}")

        if patterns['price_insights']['recommendation'] == 'lower':
            tactics.append(f"Consider lowering price from ${target_game.price:.2f} to ${avg_price:.2f} (market average)")

        if velocity_ratio > 2:
            tactics.append(f"Increase visibility efforts - competitors have {velocity_ratio:.1f}x more engagement")

        # Add specific game examples
        top_performer = significantly_higher[0]
        tactics.append(f"Study {top_performer.name}'s store page: https://store.steampowered.com/app/{top_performer.app_id}")

        patterns['actionable_tactics'] = tactics

        return patterns

    def find_recovery_stories(
        self,
        target_score: float,
        genre_tags: List[str],
        limit: int = 3
    ) -> List[RecoveryStory]:
        """
        Find games that started with similar scores but improved significantly.

        This is challenging with SteamSpy data as we don't have historical snapshots.
        We'll use heuristics based on review score distribution and volume.

        Args:
            target_score: Current score of target game
            genre_tags: Genre tags to filter by
            limit: Number of recovery stories to find

        Returns:
            List of RecoveryStory objects
        """
        # Note: This is a simplified implementation
        # A full implementation would require historical data from SteamDB or similar

        logger.info(f"Searching for recovery stories (target score: {target_score:.0f})")

        recovery_stories = []

        # For now, return placeholder structure
        # In production, you'd query a database with historical snapshots

        # Example recovery story (template)
        example = RecoveryStory(
            app_id="placeholder",
            name="Example Recovery Game",
            before_score=target_score - 10,
            after_score=target_score + 15,
            before_reviews=500,
            after_reviews=2500,
            before_percentage=65,
            after_percentage=82,
            timeframe_months=6,
            changes_made=[
                "Major content update (2 new game modes)",
                "Community feedback implementation (UI overhaul)",
                "Influencer partnership campaign (10 mid-tier streamers)",
                "Regional pricing optimization (8 new regions)"
            ],
            key_takeaway="Community engagement and content updates drove 400% review growth",
            how_to_apply="Prioritize community requests in your roadmap and partner with 5-10 genre-specific influencers"
        )

        # TODO: Implement actual historical data querying
        # This would require:
        # 1. Database of historical SteamSpy/SteamDB snapshots
        # 2. Query for games with similar starting scores
        # 3. Identify games that improved >15 points
        # 4. Analyze what changed (requires scraping patch notes, news, etc.)

        return [example] if limit > 0 else []

    def generate_full_comparison_report(
        self,
        target_game_id: str,
        target_game_data: Dict[str, Any],
        sales_data: Dict[str, Any]
    ) -> str:
        """
        Generate complete comparison analysis report.

        Args:
            target_game_id: Steam app ID
            target_game_data: Game data from Steam API
            sales_data: Sales data from revenue estimator

        Returns:
            Full markdown report
        """
        logger.info(f"Generating comparison report for {target_game_id}")

        # Extract target game info
        genre_tags = target_game_data.get('genres', [])
        if isinstance(genre_tags, list) and len(genre_tags) > 0:
            if isinstance(genre_tags[0], dict):
                genre_list = [g.get('description', '') for g in genre_tags]
            else:
                genre_list = genre_tags
        else:
            genre_list = ['Unknown']

        price = float(target_game_data.get('price', 0))
        launch_date = target_game_data.get('release_date', '')
        owner_count = int(sales_data.get('owners_avg', 0))

        # Build target game object
        review_percentage = float(sales_data.get('review_score_raw', 70))
        review_count = int(sales_data.get('reviews_total', 0))

        # Calculate overall score
        overall_score = review_percentage * 0.7
        if owner_count > 100000:
            overall_score += 15
        elif owner_count > 50000:
            overall_score += 10
        elif owner_count > 10000:
            overall_score += 5
        overall_score = min(100, max(0, overall_score))

        target_game = ComparableGame(
            app_id=target_game_id,
            name=target_game_data.get('name', 'Unknown'),
            overall_score=overall_score,
            review_count=review_count,
            review_percentage=review_percentage,
            estimated_revenue=int(sales_data.get('estimated_revenue_raw', 0)),
            revenue_display=sales_data.get('estimated_revenue', '$0'),
            tags=target_game_data.get('tags', []),
            launch_date=launch_date,
            price=price,
            owners_avg=owner_count
        )

        # Find comparable games
        comparable_games = self.find_comparable_games(
            target_game_id,
            genre_list,
            price,
            launch_date,
            owner_count,
            limit=15
        )

        if not comparable_games:
            return "## Comparable Games Analysis\n\nNo comparable games found matching the criteria."

        # Generate comparison table
        year = launch_date[:4] if len(launch_date) >= 4 else 'Recent'
        price_range = f"${max(0, price - 10):.0f}-${price + 10:.0f}"

        comparison_table = self.generate_comparison_table(
            target_game,
            comparable_games,
            genre_list[0],
            price_range,
            year
        )

        # Identify success patterns
        higher_performers = [g for g in comparable_games if g.overall_score > target_game.overall_score]
        patterns = self.identify_success_patterns(target_game, higher_performers)

        # Build patterns section
        patterns_md = "\n### Success Patterns from Higher Performers\n\n"

        if patterns['actionable_tactics']:
            patterns_md += "**Specific tactics to copy**:\n"
            for tactic in patterns['actionable_tactics']:
                patterns_md += f"- {tactic}\n"
            patterns_md += "\n"

        if patterns['common_tags_missing']:
            patterns_md += f"**Tags to add**: {', '.join(patterns['common_tags_missing'])}\n\n"

        if patterns['price_insights']:
            price_info = patterns['price_insights']
            patterns_md += f"**Pricing insight**: Higher performers average ${price_info['average_price']:.2f} "
            patterns_md += f"(you're at ${price_info['target_price']:.2f}) - "
            patterns_md += f"Recommendation: {price_info['recommendation'].upper()}\n\n"

        # Find recovery stories
        recovery_stories = self.find_recovery_stories(target_game.overall_score, genre_list, limit=1)

        recovery_md = ""
        if recovery_stories:
            recovery_md = "\n### Recovery Success Stories\n\n"
            for story in recovery_stories:
                recovery_md += f"#### {story.name}\n\n"
                recovery_md += f"**Before**: {story.before_score:.0f}/100 ({story.before_reviews:,} reviews at {story.before_percentage:.0f}% positive)\n"
                recovery_md += f"**After**: {story.after_score:.0f}/100 ({story.after_reviews:,} reviews at {story.after_percentage:.0f}% positive)\n"
                recovery_md += f"**Timeframe**: {story.timeframe_months} months\n\n"
                recovery_md += "**What They Changed**:\n"
                for i, change in enumerate(story.changes_made, 1):
                    recovery_md += f"{i}. {change}\n"
                recovery_md += f"\n**Key Takeaway**: {story.key_takeaway}\n"
                recovery_md += f"**How You Can Apply This**: {story.how_to_apply}\n\n"

        # Combine all sections
        full_report = comparison_table + patterns_md + recovery_md

        return full_report


# Convenience function for testing
def test_analyzer(app_id: str):
    """Test the analyzer with a specific game"""
    analyzer = ComparableGamesAnalyzer()

    # For testing, we need to fetch game data first
    # This is a simplified test - in production, this integrates with main report flow

    print(f"\n=== Testing Comparable Games Analyzer ===")
    print(f"Target Game ID: {app_id}")
    print("Fetching game data...")

    try:
        # Fetch target game data
        game_data = analyzer.game_search.get_game_details(int(app_id))
        print(f"Game: {game_data.get('name')}")
        print(f"Price: {game_data.get('price')}")
        print(f"Genres: {game_data.get('genres')}")

        # Get SteamSpy data for owners
        spy_data = analyzer.game_search.get_steamspy_data(int(app_id))
        print(f"Owners: {spy_data.get('owners', 'Unknown')}")

        print("\n Searching for comparable games...")

        # Find comparable games
        comparable_games = analyzer.find_comparable_games(
            target_game_id=app_id,
            genre_tags=game_data.get('genres', []),
            price=game_data.get('price_raw', 0),
            launch_date=game_data.get('release_date', ''),
            owner_count=analyzer._parse_owners_range(spy_data.get('owners', '0 .. 0')),
            limit=10
        )

        print(f"\nFound {len(comparable_games)} comparable games:")
        for i, game in enumerate(comparable_games[:5], 1):
            print(f"{i}. {game.name} - Score: {game.overall_score:.0f}/100, Revenue: {game.revenue_display}")

        return analyzer, comparable_games

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return analyzer, []
