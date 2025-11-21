#!/usr/bin/env python3
"""
Smart Game Metrics Estimator
Uses multiple signals to estimate ownership, revenue when APIs are blocked
"""

from typing import Dict, Any, Optional
from datetime import datetime
import re


class SmartEstimator:
    """Intelligent game metrics estimation using multiple signals"""

    # Genre-based ownership benchmarks (median owners)
    GENRE_BENCHMARKS = {
        'action': 250000,
        'indie': 50000,
        'rpg': 180000,
        'strategy': 100000,
        'simulation': 120000,
        'adventure': 90000,
        'mmo': 1500000,
        'mmorpg': 2000000,
        'fps': 300000,
        'shooter': 280000,
        'racing': 150000,
        'sports': 200000,
        'platformer': 80000,
        'puzzle': 60000,
        'casual': 100000,
        'arcade': 70000,
        'fighting': 120000,
        'roguelike': 90000,
        'roguelite': 95000,
        'survival': 180000,
        'horror': 110000,
        'default': 100000
    }

    def estimate_ownership(
        self,
        game_data: Dict[str, Any],
        rawg_data: Optional[Dict[str, Any]] = None,
        igdb_data: Optional[Dict[str, Any]] = None,
        trends_data: Optional[Dict[str, Any]] = None,
        youtube_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Estimate game ownership using multiple signals from all data sources

        Signals used:
        1. Genre (benchmark ranges)
        2. Metacritic/IGDB score (quality multiplier)
        3. RAWG/IGDB ratings count (popularity proxy)
        4. Release date (age factor)
        5. Playtime (engagement multiplier)
        6. RAWG "added" count / IGDB follows (library adds)
        7. Google Trends interest (marketing momentum)
        8. YouTube views/engagement (content creator activity)
        9. IGDB hypes (pre-release buzz)
        """

        # Start with genre-based baseline
        genre = self._get_primary_genre(game_data, rawg_data)
        base_estimate = self.GENRE_BENCHMARKS.get(genre.lower(), self.GENRE_BENCHMARKS['default'])

        print(f"Base estimate for genre '{genre}': {base_estimate:,}")

        # Apply multipliers based on available signals
        multiplier = 1.0
        signals_used = ['genre']

        # Signal 1: Metacritic score (quality)
        if rawg_data and rawg_data.get('metacritic'):
            metacritic = rawg_data['metacritic']
            quality_mult = self._metacritic_multiplier(metacritic)
            multiplier *= quality_mult
            signals_used.append(f'metacritic_{metacritic}')
            print(f"  Quality multiplier (Metacritic {metacritic}): {quality_mult}x")

        # Signal 2: RAWG ratings count (popularity)
        if rawg_data and rawg_data.get('ratings_count'):
            ratings_count = rawg_data['ratings_count']
            popularity_mult = self._ratings_count_multiplier(ratings_count)
            multiplier *= popularity_mult
            signals_used.append(f'ratings_{ratings_count}')
            print(f"  Popularity multiplier ({ratings_count:,} ratings): {popularity_mult}x")

        # Signal 3: Release date (age factor)
        release_date = None
        if rawg_data and rawg_data.get('released'):
            release_date = rawg_data['released']
        elif game_data.get('release_date'):
            release_date = game_data['release_date']

        if release_date:
            age_mult = self._age_multiplier(release_date)
            multiplier *= age_mult
            signals_used.append(f'age')
            print(f"  Age multiplier (released {release_date}): {age_mult}x")

        # Signal 4: Average playtime (engagement)
        if rawg_data and rawg_data.get('playtime', 0) > 0:
            playtime = rawg_data['playtime']
            engagement_mult = self._playtime_multiplier(playtime)
            multiplier *= engagement_mult
            signals_used.append(f'playtime_{playtime}h')
            print(f"  Engagement multiplier ({playtime}h playtime): {engagement_mult}x")

        # Signal 5: RAWG "added" count (times added to libraries)
        if rawg_data and rawg_data.get('added', 0) > 0:
            added = rawg_data['added']
            # "Added" is a strong signal - directly correlates with ownership
            library_mult = self._library_adds_multiplier(added)
            multiplier *= library_mult
            signals_used.append(f'library_adds_{added}')
            print(f"  Library adds multiplier ({added:,} adds): {library_mult}x")

        # Signal 6: IGDB follows/rating count (community engagement)
        if igdb_data:
            # IGDB follows (similar to library adds)
            if igdb_data.get('follows', 0) > 0:
                follows = igdb_data['follows']
                follows_mult = self._igdb_follows_multiplier(follows)
                multiplier *= follows_mult
                signals_used.append(f'igdb_follows_{follows}')
                print(f"  IGDB follows multiplier ({follows:,} follows): {follows_mult}x")

            # IGDB rating count (cross-validate with RAWG)
            if igdb_data.get('rating_count', 0) > 0:
                rating_count = igdb_data['rating_count']
                igdb_rating_mult = self._igdb_rating_multiplier(rating_count)
                multiplier *= igdb_rating_mult
                signals_used.append(f'igdb_ratings_{rating_count}')
                print(f"  IGDB rating count multiplier ({rating_count:,} ratings): {igdb_rating_mult}x")

            # IGDB critic score (cross-validate with Metacritic)
            if igdb_data.get('critic_rating', 0) > 0:
                critic = int(igdb_data['critic_rating'])
                critic_mult = self._metacritic_multiplier(critic)  # Use same scale
                multiplier *= critic_mult
                signals_used.append(f'igdb_critic_{critic}')
                print(f"  IGDB critic multiplier ({critic}/100): {critic_mult}x")

        # Signal 7: Google Trends interest (marketing momentum)
        if trends_data:
            current_interest = trends_data.get('current_interest', 0)
            trend_direction = trends_data.get('trend_direction', 'unknown')

            if current_interest > 0:
                trends_mult = self._trends_multiplier(current_interest, trend_direction)
                multiplier *= trends_mult
                signals_used.append(f'trends_{current_interest}_{trend_direction}')
                print(f"  Google Trends multiplier (interest: {current_interest}, {trend_direction}): {trends_mult}x")

        # Signal 8: YouTube engagement (content creator activity)
        if youtube_data:
            total_views = youtube_data.get('total_views', 0)
            video_count = youtube_data.get('video_count', 0)

            if total_views > 0:
                youtube_mult = self._youtube_multiplier(total_views, video_count)
                multiplier *= youtube_mult
                signals_used.append(f'youtube_{total_views}_views')
                print(f"  YouTube multiplier ({total_views:,} views, {video_count} videos): {youtube_mult}x")

        # Calculate final estimate
        final_estimate = int(base_estimate * multiplier)

        # Create confidence range (wider if fewer signals)
        confidence_width = 2.5 - (len(signals_used) * 0.2)  # More signals = tighter range
        confidence_width = max(1.5, min(3.0, confidence_width))

        print(f"Final estimate: {final_estimate:,} (multiplier: {multiplier:.2f}x, signals: {len(signals_used)})")

        return {
            'owners_min': int(final_estimate / confidence_width),
            'owners_max': int(final_estimate * confidence_width),
            'owners_avg': final_estimate,
            'owners_display': f'{int(final_estimate / confidence_width):,} .. {int(final_estimate * confidence_width):,}',
            'estimation_method': 'multi_signal_intelligence',
            'confidence': self._calculate_confidence(signals_used),
            'signals_used': signals_used,
            'base_genre_estimate': base_estimate,
            'total_multiplier': multiplier
        }

    def estimate_revenue(
        self,
        ownership_data: Dict[str, Any],
        price: float,
        review_score: float
    ) -> Dict[str, Any]:
        """
        Estimate revenue based on ownership and price

        Accounts for:
        - Regional pricing variations (70% of base price globally)
        - Steam's 30% cut
        - Refund rates (varies by quality)
        - Discount impact over time (15% average)
        """
        owners_avg = ownership_data.get('owners_avg', 0)

        if owners_avg < 100 or price <= 0:
            return self._minimal_revenue_estimate()

        # Regional pricing factor (average global price is ~70% of US price)
        regional_factor = 0.70

        # Steam takes 30%
        steam_cut = 0.70

        # Refund rate varies by quality
        if review_score >= 90:
            refund_rate = 0.05  # 5% refunds for exceptional games
        elif review_score >= 80:
            refund_rate = 0.08  # 8% for good games
        elif review_score >= 70:
            refund_rate = 0.12  # 12% for average
        else:
            refund_rate = 0.18  # 18% for poor quality

        # Discount factor (games go on sale, avg ~15% revenue reduction)
        discount_factor = 0.85

        # Calculate effective price per sale
        effective_price = price * regional_factor * steam_cut * (1 - refund_rate) * discount_factor

        # Revenue estimates
        revenue_estimate = int(owners_avg * effective_price)
        revenue_low = int(ownership_data['owners_min'] * effective_price * 0.8)  # Conservative
        revenue_high = int(ownership_data['owners_max'] * effective_price * 1.2)  # Optimistic

        # Format display
        if revenue_estimate < 1000:
            revenue_str = f'${revenue_estimate:,}'
            range_str = f'${revenue_low:,} - ${revenue_high:,}'
        elif revenue_estimate < 1000000:
            revenue_str = f'${revenue_estimate/1000:.0f}K'
            range_str = f'${revenue_low/1000:.0f}K - ${revenue_high/1000:.0f}K'
        else:
            revenue_str = f'${revenue_estimate/1000000:.1f}M'
            range_str = f'${revenue_low/1000000:.1f}M - ${revenue_high/1000000:.1f}M'

        return {
            'estimated_revenue': revenue_str,
            'estimated_revenue_raw': revenue_estimate,
            'revenue_range': range_str,
            'revenue_confidence_low': revenue_low,
            'revenue_confidence_high': revenue_high,
            'estimation_method': 'calculated',
            'calculation_factors': {
                'regional_pricing': regional_factor,
                'steam_cut': steam_cut,
                'refund_rate': refund_rate,
                'discount_factor': discount_factor,
                'effective_price_per_sale': round(effective_price, 2)
            }
        }

    def _get_primary_genre(self, game_data: Dict[str, Any], rawg_data: Optional[Dict[str, Any]]) -> str:
        """Extract primary genre from available data"""
        # Try RAWG genres first
        if rawg_data and rawg_data.get('genres'):
            return rawg_data['genres'][0].lower()

        # Try game_data genres
        if game_data.get('genres') and isinstance(game_data['genres'], list):
            return game_data['genres'][0].lower()

        # Try tags as fallback
        if rawg_data and rawg_data.get('tags'):
            for tag in rawg_data['tags'][:3]:
                tag_lower = tag.lower()
                if tag_lower in self.GENRE_BENCHMARKS:
                    return tag_lower

        return 'default'

    def _metacritic_multiplier(self, score: int) -> float:
        """Quality multiplier based on Metacritic score"""
        if score >= 95:
            return 4.0  # Legendary games
        elif score >= 90:
            return 3.0  # Exceptional games sell 3x
        elif score >= 85:
            return 2.0  # Great games sell 2x
        elif score >= 80:
            return 1.5  # Good games
        elif score >= 75:
            return 1.2
        elif score >= 70:
            return 1.0
        elif score >= 60:
            return 0.7
        else:
            return 0.5  # Poor quality

    def _ratings_count_multiplier(self, ratings_count: int) -> float:
        """Popularity multiplier based on RAWG ratings count"""
        if ratings_count > 100000:
            return 3.5  # Massive popularity (e.g., Witcher 3, GTA V)
        elif ratings_count > 50000:
            return 2.5  # Very popular
        elif ratings_count > 20000:
            return 2.0  # Popular
        elif ratings_count > 10000:
            return 1.5  # Well-known
        elif ratings_count > 5000:
            return 1.2  # Known
        elif ratings_count > 1000:
            return 1.0  # Average
        else:
            return 0.8  # Niche

    def _age_multiplier(self, release_date: str) -> float:
        """Age multiplier - older games have accumulated more sales"""
        try:
            # Try to parse date (YYYY-MM-DD or various formats)
            year_match = re.search(r'(\d{4})', release_date)
            if not year_match:
                return 1.0

            release_year = int(year_match.group(1))
            current_year = datetime.now().year
            years_old = current_year - release_year

            # Age curve: newer games haven't had time to accumulate sales
            if years_old <= 0:
                return 0.3  # Not released yet or this year
            elif years_old == 1:
                return 0.6  # Recent release
            elif years_old == 2:
                return 1.0  # Standard
            elif years_old == 3:
                return 1.3
            elif years_old <= 5:
                return 1.6  # Sweet spot
            elif years_old <= 8:
                return 2.0  # Accumulated significant sales
            else:
                return 2.5  # Classic/legacy title (cap at 2.5x)

        except (ValueError, AttributeError, TypeError) as e:
            print(f"Error parsing release date '{release_date}': {e}")
            return 1.0

    def _playtime_multiplier(self, playtime_hours: int) -> float:
        """Engagement multiplier based on average playtime"""
        if playtime_hours > 100:
            return 1.4  # Deep games with high engagement
        elif playtime_hours > 50:
            return 1.3
        elif playtime_hours > 20:
            return 1.2
        elif playtime_hours > 10:
            return 1.1
        else:
            return 1.0

    def _library_adds_multiplier(self, added_count: int) -> float:
        """
        Multiplier based on RAWG "added" count (times added to libraries)
        This is a STRONG signal for ownership estimation
        """
        if added_count > 1000000:
            return 3.0  # Mega-hit
        elif added_count > 500000:
            return 2.5
        elif added_count > 200000:
            return 2.0
        elif added_count > 100000:
            return 1.7
        elif added_count > 50000:
            return 1.4
        elif added_count > 20000:
            return 1.2
        else:
            return 1.0

    def _igdb_follows_multiplier(self, follows: int) -> float:
        """Multiplier based on IGDB follows (community interest)"""
        if follows > 100000:
            return 2.5  # Massive following
        elif follows > 50000:
            return 2.0
        elif follows > 20000:
            return 1.6
        elif follows > 10000:
            return 1.3
        elif follows > 1000:
            return 1.1
        else:
            return 1.0

    def _igdb_rating_multiplier(self, rating_count: int) -> float:
        """Multiplier based on IGDB rating count (cross-validation with RAWG)"""
        # IGDB tends to have lower counts than RAWG, so adjust thresholds
        if rating_count > 10000:
            return 1.8
        elif rating_count > 5000:
            return 1.5
        elif rating_count > 1000:
            return 1.3
        elif rating_count > 500:
            return 1.1
        else:
            return 1.0

    def _trends_multiplier(self, current_interest: int, trend_direction: str) -> float:
        """
        Multiplier based on Google Trends search interest

        Args:
            current_interest: 0-100 scale
            trend_direction: 'rising', 'falling', 'stable', 'unknown'
        """
        # Base multiplier from current interest
        if current_interest >= 80:
            base = 2.0  # Viral/trending
        elif current_interest >= 50:
            base = 1.5  # High interest
        elif current_interest >= 25:
            base = 1.2  # Moderate interest
        elif current_interest >= 10:
            base = 1.0  # Some interest
        else:
            base = 0.9  # Low interest

        # Adjust based on trend direction
        if trend_direction == 'rising':
            return base * 1.2  # Growing momentum
        elif trend_direction == 'falling':
            return base * 0.9  # Declining interest
        else:
            return base

    def _youtube_multiplier(self, total_views: int, video_count: int) -> float:
        """
        Multiplier based on YouTube engagement

        High view counts indicate strong content creator interest and
        marketing reach, which correlates with sales
        """
        if total_views > 50_000_000:
            return 2.5  # Massive YouTube presence
        elif total_views > 10_000_000:
            return 2.0  # Very strong
        elif total_views > 5_000_000:
            return 1.6  # Strong
        elif total_views > 1_000_000:
            return 1.3  # Good
        elif total_views > 100_000:
            return 1.1  # Moderate
        else:
            return 1.0

    def _calculate_confidence(self, signals: list) -> str:
        """Calculate confidence level based on number of signals (up to 9+)"""
        signal_count = len(signals)

        if signal_count >= 8:
            return 'very-high'  # Multiple sources cross-validating
        elif signal_count >= 6:
            return 'high'
        elif signal_count >= 4:
            return 'medium-high'
        elif signal_count >= 3:
            return 'medium'
        elif signal_count >= 2:
            return 'low-medium'
        else:
            return 'low'

    def _minimal_revenue_estimate(self) -> Dict[str, Any]:
        """Return minimal revenue estimate for edge cases"""
        return {
            'estimated_revenue': '$5,000',
            'estimated_revenue_raw': 5000,
            'revenue_range': '$1K - $15K',
            'revenue_confidence_low': 1000,
            'revenue_confidence_high': 15000,
            'estimation_method': 'minimal_fallback',
            'calculation_factors': {}
        }


def test_estimator():
    """Test the estimator with sample data"""
    estimator = SmartEstimator()

    # Simulate RAWG data for a mid-tier indie game
    rawg_data = {
        'name': 'Test Game',
        'genres': ['Action', 'Indie'],
        'metacritic': 85,
        'ratings_count': 15000,
        'released': '2023-05-15',
        'playtime': 25,
        'added': 75000
    }

    game_data = {
        'name': 'Test Game',
        'price_raw': 24.99
    }

    # Estimate ownership
    ownership = estimator.estimate_ownership(game_data, rawg_data)
    print("\n=== Ownership Estimate ===")
    print(f"Range: {ownership['owners_display']}")
    print(f"Average: {ownership['owners_avg']:,}")
    print(f"Confidence: {ownership['confidence']}")
    print(f"Signals: {', '.join(ownership['signals_used'])}")

    # Estimate revenue
    revenue = estimator.estimate_revenue(ownership, 24.99, 85)
    print("\n=== Revenue Estimate ===")
    print(f"Range: {revenue['revenue_range']}")
    print(f"Midpoint: {revenue['estimated_revenue']}")


if __name__ == "__main__":
    test_estimator()
