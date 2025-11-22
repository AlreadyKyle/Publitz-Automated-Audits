"""
Growth Strategy Module

Provides actionable growth tactics including:
- Launch timing intelligence (competitive calendar)
- Social proof roadmap (follower/Discord targets)
- Creator/influencer hit list with estimated impact

Helps developers maximize visibility and wishlists before/after launch.
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import random


class GrowthStrategyAnalyzer:
    """Analyzes growth opportunities and provides tactical roadmap"""

    # High-impact YouTubers/streamers by genre (curated list)
    CREATOR_DATABASE = {
        'roguelike': [
            {'name': 'SplatterCat', 'subscribers': 250000, 'avg_views': 20000, 'coverage_rate': 0.8},
            {'name': 'Wanderbots', 'subscribers': 180000, 'avg_views': 15000, 'coverage_rate': 0.7},
            {'name': 'Retromation', 'subscribers': 140000, 'avg_views': 12000, 'coverage_rate': 0.75},
            {'name': 'Northernlion', 'subscribers': 1000000, 'avg_views': 80000, 'coverage_rate': 0.3},
            {'name': 'Olexa', 'subscribers': 95000, 'avg_views': 8000, 'coverage_rate': 0.65},
        ],
        'strategy': [
            {'name': 'Pravus Gaming', 'subscribers': 280000, 'avg_views': 25000, 'coverage_rate': 0.7},
            {'name': 'Many A True Nerd', 'subscribers': 520000, 'avg_views': 40000, 'coverage_rate': 0.5},
            {'name': 'Quill18', 'subscribers': 450000, 'avg_views': 35000, 'coverage_rate': 0.6},
        ],
        'horror': [
            {'name': 'Markiplier', 'subscribers': 36000000, 'avg_views': 500000, 'coverage_rate': 0.2},
            {'name': 'IGP', 'subscribers': 3800000, 'avg_views': 120000, 'coverage_rate': 0.6},
            {'name': 'insym', 'subscribers': 850000, 'avg_views': 60000, 'coverage_rate': 0.7},
            {'name': 'John Wolfe', 'subscribers': 900000, 'avg_views': 70000, 'coverage_rate': 0.65},
        ],
        'indie': [
            {'name': 'SplatterCat', 'subscribers': 250000, 'avg_views': 20000, 'coverage_rate': 0.85},
            {'name': 'Wanderbots', 'subscribers': 180000, 'avg_views': 15000, 'coverage_rate': 0.75},
            {'name': 'EnterElysium', 'subscribers': 150000, 'avg_views': 12000, 'coverage_rate': 0.7},
            {'name': 'Blitz', 'subscribers': 950000, 'avg_views': 45000, 'coverage_rate': 0.5},
        ],
        'rpg': [
            {'name': 'Mortismal Gaming', 'subscribers': 420000, 'avg_views': 35000, 'coverage_rate': 0.65},
            {'name': 'Fextralife', 'subscribers': 2100000, 'avg_views': 85000, 'coverage_rate': 0.5},
            {'name': 'ChristopherOdd', 'subscribers': 380000, 'avg_views': 28000, 'coverage_rate': 0.6},
        ],
        'detective': [
            {'name': 'Gab Smolders', 'subscribers': 3500000, 'avg_views': 95000, 'coverage_rate': 0.4},
            {'name': 'John Wolfe', 'subscribers': 900000, 'avg_views': 70000, 'coverage_rate': 0.5},
        ],
        'deckbuilder': [
            {'name': 'Retromation', 'subscribers': 140000, 'avg_views': 12000, 'coverage_rate': 0.8},
            {'name': 'Wanderbots', 'subscribers': 180000, 'avg_views': 15000, 'coverage_rate': 0.75},
            {'name': 'Northernlion', 'subscribers': 1000000, 'avg_views': 80000, 'coverage_rate': 0.4},
        ],
        'simulation': [
            {'name': 'Blitz', 'subscribers': 950000, 'avg_views': 45000, 'coverage_rate': 0.6},
            {'name': 'Biffa2001', 'subscribers': 280000, 'avg_views': 22000, 'coverage_rate': 0.55},
            {'name': 'Pravus Gaming', 'subscribers': 280000, 'avg_views': 25000, 'coverage_rate': 0.5},
        ],
    }

    # Steam events calendar (2024-2025)
    STEAM_EVENTS = [
        {'name': 'Steam Next Fest', 'dates': 'February 5-12, 2024', 'type': 'demo', 'traffic_multiplier': 3.0},
        {'name': 'Spring Sale', 'dates': 'March 14-21, 2024', 'type': 'sale', 'traffic_multiplier': 2.5},
        {'name': 'Steam Next Fest', 'dates': 'June 10-17, 2024', 'type': 'demo', 'traffic_multiplier': 3.0},
        {'name': 'Summer Sale', 'dates': 'June 27 - July 11, 2024', 'type': 'sale', 'traffic_multiplier': 4.0},
        {'name': 'Steam Next Fest', 'dates': 'October 14-21, 2024', 'type': 'demo', 'traffic_multiplier': 3.0},
        {'name': 'Autumn Sale', 'dates': 'November 27 - December 4, 2024', 'type': 'sale', 'traffic_multiplier': 3.5},
        {'name': 'Winter Sale', 'dates': 'December 19, 2024 - January 2, 2025', 'type': 'sale', 'traffic_multiplier': 4.5},
    ]

    def __init__(self):
        """Initialize the growth strategy analyzer"""
        pass

    def analyze_growth_strategy(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        target_launch_date: str = None
    ) -> Dict[str, Any]:
        """
        Analyze complete growth strategy

        Args:
            game_data: Game information
            sales_data: Sales and review data
            target_launch_date: Planned launch date (YYYY-MM-DD) or None for post-launch

        Returns:
            Complete growth strategy with timing, social proof, and creator recommendations
        """
        # Determine if pre-launch or post-launch
        is_pre_launch = target_launch_date is not None

        # Launch timing analysis
        launch_timing = self._analyze_launch_timing(game_data, target_launch_date) if is_pre_launch else None

        # Social proof roadmap
        social_proof = self._calculate_social_proof_roadmap(sales_data, is_pre_launch)

        # Creator hit list
        creator_list = self._generate_creator_hit_list(game_data, sales_data)

        # Community building tactics
        community_tactics = self._generate_community_tactics(sales_data, is_pre_launch)

        return {
            'is_pre_launch': is_pre_launch,
            'launch_timing': launch_timing,
            'social_proof_roadmap': social_proof,
            'creator_hit_list': creator_list,
            'community_tactics': community_tactics,
            'steam_events': self.STEAM_EVENTS
        }

    def _analyze_launch_timing(
        self,
        game_data: Dict[str, Any],
        target_date: str
    ) -> Dict[str, Any]:
        """
        Analyze optimal launch timing

        Considers:
        - Competitive release calendar
        - Steam event timing
        - Seasonal traffic patterns
        """
        # For demo purposes, we'll analyze relative to current date
        # In production, this would scrape SteamDB for actual competitive releases

        genre = game_data.get('genres', 'indie').lower()

        # Recommended launch windows (avoiding major AAA releases and maximizing Steam event proximity)
        optimal_windows = [
            {
                'window': 'Early February (before Steam Next Fest)',
                'dates': 'February 1-4, 2024',
                'reason': 'Launch just before Steam Next Fest for maximum demo traffic boost',
                'competition': 'Low - post-holiday lull',
                'rating': 'OPTIMAL'
            },
            {
                'window': 'Early April (post-Spring Sale)',
                'dates': 'April 1-15, 2024',
                'reason': 'Low competition window, audience has spending fatigue relief',
                'competition': 'Low',
                'rating': 'GOOD'
            },
            {
                'window': 'Early June (before Summer Sale)',
                'dates': 'June 1-9, 2024',
                'reason': 'Build wishlists before biggest sale of year',
                'competition': 'Medium - some AAA titles',
                'rating': 'GOOD'
            },
            {
                'window': 'Mid-September (back-to-school)',
                'dates': 'September 15-30, 2024',
                'reason': 'Students back, less summer travel, moderate competition',
                'competition': 'Medium',
                'rating': 'ACCEPTABLE'
            },
        ]

        # Windows to avoid
        avoid_windows = [
            {
                'window': 'November-December',
                'reason': 'AAA holiday releases dominate, Steam Autumn/Winter Sales create discount expectations',
                'rating': 'AVOID'
            },
            {
                'window': 'Mid-June to early July',
                'reason': 'Summer Sale discounting period, users wait for deals',
                'rating': 'AVOID'
            },
        ]

        # Next Steam events
        upcoming_events = [event for event in self.STEAM_EVENTS][:3]

        return {
            'optimal_windows': optimal_windows,
            'avoid_windows': avoid_windows,
            'upcoming_steam_events': upcoming_events,
            'recommendation': optimal_windows[0],
            'competitive_analysis': {
                'genre': genre,
                'note': 'Launch timing optimized for indie games in this genre',
                'traffic_pattern': 'Higher engagement during Fall/Winter, lower in Summer'
            }
        }

    def _calculate_social_proof_roadmap(
        self,
        sales_data: Dict[str, Any],
        is_pre_launch: bool
    ) -> Dict[str, Any]:
        """
        Calculate social proof milestones needed for algorithm boost

        Targets for visibility tiers:
        - Tier 1: 5,000+ Steam followers, 1,000+ Discord, 500+ Reddit
        - Tier 2: 1,500+ Steam followers, 500+ Discord, 200+ Reddit
        - Tier 3: 500+ Steam followers, 150+ Discord, 50+ Reddit
        """
        reviews_total = sales_data.get('reviews_total', 0)

        # Current estimated social proof (based on review count as proxy)
        if reviews_total > 1000:
            current_followers = 2500 + (reviews_total - 1000) * 2
            current_discord = 600 + (reviews_total - 1000) * 0.4
            current_reddit = 300
        elif reviews_total > 200:
            current_followers = 800 + (reviews_total - 200) * 2
            current_discord = 200 + (reviews_total - 200) * 0.5
            current_reddit = 100
        else:
            current_followers = reviews_total * 4
            current_discord = reviews_total * 1
            current_reddit = 0

        # Tier targets
        tier_2_targets = {
            'steam_followers': 1500,
            'discord_members': 500,
            'reddit_subscribers': 200,
            'twitter_followers': 1000
        }

        tier_1_targets = {
            'steam_followers': 5000,
            'discord_members': 1000,
            'reddit_subscribers': 500,
            'twitter_followers': 3000
        }

        # Calculate gaps
        tier_2_gap = {
            'steam_followers': max(0, tier_2_targets['steam_followers'] - current_followers),
            'discord_members': max(0, tier_2_targets['discord_members'] - current_discord),
            'reddit_subscribers': max(0, tier_2_targets['reddit_subscribers'] - current_reddit),
        }

        # Daily growth rates needed
        days_to_launch = 90 if is_pre_launch else 0

        if days_to_launch > 0:
            daily_growth_needed = {
                'steam_followers': tier_2_gap['steam_followers'] / days_to_launch,
                'discord_members': tier_2_gap['discord_members'] / days_to_launch,
                'reddit_subscribers': tier_2_gap['reddit_subscribers'] / days_to_launch,
            }
        else:
            daily_growth_needed = None

        # Milestones
        milestones = []

        if is_pre_launch:
            milestones = [
                {
                    'day': 30,
                    'target_followers': int(current_followers + tier_2_gap['steam_followers'] * 0.33),
                    'target_discord': int(current_discord + tier_2_gap['discord_members'] * 0.33),
                    'tactics': ['Reddit AMAs', 'Dev blog launch', 'Discord server creation', 'Twitter announcement thread']
                },
                {
                    'day': 60,
                    'target_followers': int(current_followers + tier_2_gap['steam_followers'] * 0.66),
                    'target_discord': int(current_discord + tier_2_gap['discord_members'] * 0.66),
                    'tactics': ['Demo launch at Steam Next Fest', 'Influencer key distribution', 'Weekly dev updates', 'Screenshot Saturdays']
                },
                {
                    'day': 90,
                    'target_followers': tier_2_targets['steam_followers'],
                    'target_discord': tier_2_targets['discord_members'],
                    'tactics': ['Launch preparation', 'Community event', 'Final trailer release', 'Press outreach']
                },
            ]
        else:
            milestones = [
                {
                    'month': 1,
                    'target_followers': int(current_followers * 1.5),
                    'target_discord': int(current_discord * 1.5) if current_discord > 0 else 150,
                    'tactics': ['Post-launch content updates', 'Community events', 'Discount during next Steam sale']
                },
                {
                    'month': 3,
                    'target_followers': int(current_followers * 2),
                    'target_discord': int(current_discord * 2) if current_discord > 0 else 350,
                    'tactics': ['Major content update', 'DLC or expansion announcement', 'YouTube creator push']
                },
            ]

        return {
            'current': {
                'steam_followers': int(current_followers),
                'discord_members': int(current_discord),
                'reddit_subscribers': int(current_reddit)
            },
            'tier_2_targets': tier_2_targets,
            'tier_1_targets': tier_1_targets,
            'gaps': tier_2_gap,
            'daily_growth_needed': daily_growth_needed,
            'milestones': milestones,
            'days_to_launch': days_to_launch
        }

    def _generate_creator_hit_list(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate prioritized list of YouTubers/streamers to contact

        Estimates wishlist impact based on:
        - Channel size
        - Genre fit
        - Coverage rate
        - Typical conversion rates
        """
        genres = game_data.get('genres', 'indie').lower()
        tags = game_data.get('tags', '').lower()
        estimated_revenue = sales_data.get('estimated_revenue', 50000)

        # Determine best genre match
        genre_matches = []
        for genre_key in self.CREATOR_DATABASE.keys():
            if genre_key in genres or genre_key in tags:
                genre_matches.append(genre_key)

        if not genre_matches:
            genre_matches = ['indie']  # Default fallback

        # Get relevant creators
        all_creators = []
        for genre in genre_matches:
            creators = self.CREATOR_DATABASE.get(genre, [])
            for creator in creators:
                # Estimate wishlist impact
                # Formula: (avg_views * coverage_rate * wishlist_conversion_rate)
                # Wishlist conversion: 1-3% of views typically
                wishlist_conversion = 0.015  # 1.5% average

                estimated_wishlists_min = int(creator['avg_views'] * creator['coverage_rate'] * wishlist_conversion * 0.7)
                estimated_wishlists_max = int(creator['avg_views'] * creator['coverage_rate'] * wishlist_conversion * 1.3)

                # Cost estimate (for sponsored content)
                if creator['subscribers'] > 1000000:
                    cost_range = '$1,500-3,000'
                    cost_min = 1500
                elif creator['subscribers'] > 500000:
                    cost_range = '$800-1,500'
                    cost_min = 800
                elif creator['subscribers'] > 200000:
                    cost_range = '$400-800'
                    cost_min = 400
                else:
                    cost_range = '$200-400'
                    cost_min = 200

                # ROI calculation
                # Assume $20 game, 15% wishlist-to-purchase conversion
                purchase_conversion = 0.15
                avg_wishlists = (estimated_wishlists_min + estimated_wishlists_max) / 2
                estimated_revenue_impact = avg_wishlists * purchase_conversion * 20

                # Determine if should offer sponsorship or just free key
                budget_percent = (cost_min / estimated_revenue) if estimated_revenue > 0 else 1
                offer_sponsorship = budget_percent < 0.05 and creator['subscribers'] > 200000

                all_creators.append({
                    'name': creator['name'],
                    'subscribers': creator['subscribers'],
                    'avg_views': creator['avg_views'],
                    'coverage_rate': int(creator['coverage_rate'] * 100),
                    'estimated_wishlists': f"{estimated_wishlists_min:,}-{estimated_wishlists_max:,}",
                    'estimated_wishlists_avg': int(avg_wishlists),
                    'cost_range': cost_range,
                    'offer_type': 'Sponsored Coverage' if offer_sponsorship else 'Free Key',
                    'genre_fit': genre,
                    'estimated_revenue_impact': int(estimated_revenue_impact),
                    'roi': estimated_revenue_impact / cost_min if offer_sponsorship else None
                })

        # Sort by estimated wishlist impact (descending)
        all_creators.sort(key=lambda x: x['estimated_wishlists_avg'], reverse=True)

        # Tier 1: Top priority (free keys + sponsorship consideration)
        tier_1 = [c for c in all_creators if c['estimated_wishlists_avg'] > 150][:5]

        # Tier 2: Medium priority (free keys)
        tier_2 = [c for c in all_creators if 50 <= c['estimated_wishlists_avg'] <= 150][:10]

        # Budget allocation recommendation
        # FIX: Safely parse cost range with error handling
        def safe_parse_cost(cost_range):
            try:
                return int(cost_range.split('-')[0].replace('$', '').replace(',', ''))
            except (ValueError, IndexError, KeyError, AttributeError):
                return 0

        total_sponsored_cost = sum(
            safe_parse_cost(c.get('cost_range', '0'))
            for c in tier_1 if c.get('offer_type') == 'Sponsored Coverage'
        )

        budget_recommendation = {
            'free_keys': len(tier_1) + len(tier_2),
            'sponsored_coverage': len([c for c in tier_1 if c['offer_type'] == 'Sponsored Coverage']),
            'estimated_cost': f"${total_sponsored_cost:,}",
            'estimated_total_wishlists': sum(c['estimated_wishlists_avg'] for c in tier_1 + tier_2),
            'estimated_revenue_impact': sum(c['estimated_revenue_impact'] for c in tier_1 + tier_2),
        }

        return {
            'tier_1_priority': tier_1,
            'tier_2_priority': tier_2,
            'total_creators': len(tier_1) + len(tier_2),
            'budget_recommendation': budget_recommendation,
            'outreach_timeline': {
                '90_days_before': 'Contact Tier 1, discuss sponsorship',
                '60_days_before': 'Contact Tier 2, send free keys',
                '30_days_before': 'Follow-ups, provide early access builds',
                'launch_week': 'Coordinate coverage timing for launch boost'
            }
        }

    def _generate_community_tactics(
        self,
        sales_data: Dict[str, Any],
        is_pre_launch: bool
    ) -> List[Dict[str, Any]]:
        """Generate specific community building tactics"""

        reviews_total = sales_data.get('reviews_total', 0)

        tactics = []

        if is_pre_launch:
            tactics = [
                {
                    'tactic': 'Reddit Strategy',
                    'timeline': 'Weeks 1-12 before launch',
                    'actions': [
                        'Post in r/indiegaming, r/gaming, r/pcgaming (check subreddit rules)',
                        'Share dev diaries, GIFs, and behind-the-scenes content',
                        'Do AMA 30 days before launch',
                        'Target 5 posts/week for maximum visibility'
                    ],
                    'expected_impact': '+300-800 wishlists over 90 days',
                    'effort': 'Medium (2-3 hours/week)'
                },
                {
                    'tactic': 'Discord Community',
                    'timeline': 'Launch 60 days before release',
                    'actions': [
                        'Create server with channels: #announcements, #general, #feedback, #bug-reports',
                        'Post invite link in all marketing materials',
                        'Host weekly dev Q&A sessions (Fridays 3pm EST)',
                        'Offer beta keys to most active members (top 50)'
                    ],
                    'expected_impact': '500-1,000 members at launch',
                    'effort': 'Medium-High (1 hour/day)'
                },
                {
                    'tactic': 'Steam Next Fest Demo',
                    'timeline': 'Submit 2 weeks before festival',
                    'actions': [
                        'Prepare polished 30-60 minute demo',
                        'Add demo-specific feedback collection',
                        'Monitor forums during festival 24/7',
                        'Update demo based on real-time feedback'
                    ],
                    'expected_impact': '+2,000-5,000 wishlists per festival',
                    'effort': 'High (full-time during festival week)'
                },
            ]
        else:
            # Post-launch tactics
            tactics = [
                {
                    'tactic': 'Content Update Strategy',
                    'timeline': 'Every 30-60 days',
                    'actions': [
                        'Release meaningful updates (new features, not just bug fixes)',
                        'Announce updates 1 week in advance',
                        'Create update trailer/GIF for social media',
                        'Reach out to YouTubers who previously covered the game'
                    ],
                    'expected_impact': f"+{int(reviews_total * 0.15)}-{int(reviews_total * 0.25)} reviews per update",
                    'effort': 'High (requires dev time)'
                },
                {
                    'tactic': 'Community Engagement',
                    'timeline': 'Ongoing',
                    'actions': [
                        'Respond to Steam reviews (especially negative ones)',
                        'Active in Steam forums daily',
                        'Share user-generated content',
                        'Run community events/contests'
                    ],
                    'expected_impact': 'Improved review score, +5-10% positive sentiment',
                    'effort': 'Medium (30 min/day)'
                },
                {
                    'tactic': 'Sale Strategy',
                    'timeline': 'Major Steam sales',
                    'actions': [
                        'Participate in all major Steam sales',
                        'Discount 20-30% (not more)',
                        'Announce sale on social media 2 days before',
                        'Create sale-specific trailer/graphic'
                    ],
                    'expected_impact': '+200-500% sales during sale week',
                    'effort': 'Low (just setup)'
                },
            ]

        return tactics
