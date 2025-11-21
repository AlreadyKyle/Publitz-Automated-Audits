"""
Community Health Scoring

Analyzes Discord/Reddit community health and provides
growth strategies and moderation recommendations.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta


class CommunityHealthAnalyzer:
    """Analyzes community health across Discord and Reddit"""

    # Community health score components
    HEALTH_COMPONENTS = {
        'size': {'weight': 0.20, 'description': 'Total community size'},
        'engagement': {'weight': 0.30, 'description': 'Active participation rate'},
        'growth': {'weight': 0.25, 'description': 'Growth velocity'},
        'sentiment': {'weight': 0.15, 'description': 'Positive vs negative ratio'},
        'moderation': {'weight': 0.10, 'description': 'Spam/toxicity control'}
    }

    # Benchmarks by game development stage
    STAGE_BENCHMARKS = {
        'pre_announcement': {
            'discord': {'members': 50, 'daily_active': 5, 'messages_per_day': 20},
            'reddit': {'subscribers': 100, 'daily_posts': 1, 'comments_per_post': 3}
        },
        'announced': {
            'discord': {'members': 500, 'daily_active': 50, 'messages_per_day': 200},
            'reddit': {'subscribers': 500, 'daily_posts': 3, 'comments_per_post': 8}
        },
        'demo_available': {
            'discord': {'members': 2000, 'daily_active': 200, 'messages_per_day': 800},
            'reddit': {'subscribers': 1500, 'daily_posts': 5, 'comments_per_post': 12}
        },
        'pre_launch': {
            'discord': {'members': 5000, 'daily_active': 500, 'messages_per_day': 2000},
            'reddit': {'subscribers': 3000, 'daily_posts': 8, 'comments_per_post': 15}
        },
        'post_launch': {
            'discord': {'members': 10000, 'daily_active': 800, 'messages_per_day': 3500},
            'reddit': {'subscribers': 5000, 'daily_posts': 12, 'comments_per_post': 20}
        }
    }

    def __init__(self):
        """Initialize the community health analyzer"""
        pass

    def analyze_health(
        self,
        game_data: Dict[str, Any],
        community_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze community health across platforms

        Args:
            game_data: Game information
            community_data: Optional community metrics (Discord/Reddit)

        Returns:
            Community health analysis with recommendations
        """
        # Default community data if not provided
        if community_data is None:
            community_data = {
                'discord': {},
                'reddit': {},
                'development_stage': 'announced'
            }

        development_stage = community_data.get('development_stage', 'announced')

        # Analyze Discord
        discord_analysis = self._analyze_discord(
            community_data.get('discord', {}),
            development_stage
        )

        # Analyze Reddit
        reddit_analysis = self._analyze_reddit(
            community_data.get('reddit', {}),
            development_stage
        )

        # Calculate overall health score
        overall_score = self._calculate_overall_health(discord_analysis, reddit_analysis)

        # Generate growth strategies
        growth_strategies = self._generate_growth_strategies(
            discord_analysis, reddit_analysis, development_stage, game_data
        )

        # Generate moderation recommendations
        moderation_recs = self._generate_moderation_recommendations(
            discord_analysis, reddit_analysis
        )

        return {
            'overall_health_score': overall_score,
            'health_tier': self._get_health_tier(overall_score),
            'discord_analysis': discord_analysis,
            'reddit_analysis': reddit_analysis,
            'growth_strategies': growth_strategies,
            'moderation_recommendations': moderation_recs,
            'community_milestones': self._generate_milestones(development_stage),
            'best_practices': self._get_best_practices()
        }

    def _analyze_discord(
        self,
        discord_data: Dict[str, Any],
        stage: str
    ) -> Dict[str, Any]:
        """Analyze Discord community health"""
        members = discord_data.get('members', 0)
        daily_active = discord_data.get('daily_active', 0)
        messages_per_day = discord_data.get('messages_per_day', 0)
        channels = discord_data.get('channels', 0)
        roles = discord_data.get('roles', 0)

        benchmarks = self.STAGE_BENCHMARKS.get(stage, self.STAGE_BENCHMARKS['announced'])
        discord_benchmarks = benchmarks['discord']

        # Calculate engagement rate
        engagement_rate = (daily_active / members * 100) if members > 0 else 0

        # Calculate component scores
        size_score = min(100, (members / discord_benchmarks['members']) * 100)
        engagement_score = min(100, (engagement_rate / 10) * 100)  # 10% is excellent
        activity_score = min(100, (messages_per_day / discord_benchmarks['messages_per_day']) * 100)

        # Overall Discord score
        discord_score = (size_score + engagement_score + activity_score) / 3

        # Health status
        if discord_score >= 80:
            status = 'Excellent'
        elif discord_score >= 60:
            status = 'Good'
        elif discord_score >= 40:
            status = 'Fair'
        else:
            status = 'Poor'

        return {
            'score': round(discord_score, 1),
            'status': status,
            'metrics': {
                'members': members,
                'daily_active': daily_active,
                'messages_per_day': messages_per_day,
                'engagement_rate': round(engagement_rate, 2),
                'channels': channels,
                'roles': roles
            },
            'benchmarks': discord_benchmarks,
            'gaps': {
                'members': discord_benchmarks['members'] - members,
                'daily_active': discord_benchmarks['daily_active'] - daily_active,
                'messages_per_day': discord_benchmarks['messages_per_day'] - messages_per_day
            },
            'strengths': self._identify_discord_strengths(discord_data, discord_benchmarks),
            'weaknesses': self._identify_discord_weaknesses(discord_data, discord_benchmarks)
        }

    def _analyze_reddit(
        self,
        reddit_data: Dict[str, Any],
        stage: str
    ) -> Dict[str, Any]:
        """Analyze Reddit community health"""
        subscribers = reddit_data.get('subscribers', 0)
        daily_posts = reddit_data.get('daily_posts', 0)
        comments_per_post = reddit_data.get('comments_per_post', 0)
        upvote_ratio = reddit_data.get('upvote_ratio', 0)

        benchmarks = self.STAGE_BENCHMARKS.get(stage, self.STAGE_BENCHMARKS['announced'])
        reddit_benchmarks = benchmarks['reddit']

        # Calculate component scores
        size_score = min(100, (subscribers / reddit_benchmarks['subscribers']) * 100)
        activity_score = min(100, (daily_posts / reddit_benchmarks['daily_posts']) * 100)
        engagement_score = min(100, (comments_per_post / reddit_benchmarks['comments_per_post']) * 100)
        sentiment_score = upvote_ratio * 100 if upvote_ratio > 0 else 50

        # Overall Reddit score
        reddit_score = (size_score + activity_score + engagement_score + sentiment_score) / 4

        # Health status
        if reddit_score >= 80:
            status = 'Excellent'
        elif reddit_score >= 60:
            status = 'Good'
        elif reddit_score >= 40:
            status = 'Fair'
        else:
            status = 'Poor'

        return {
            'score': round(reddit_score, 1),
            'status': status,
            'metrics': {
                'subscribers': subscribers,
                'daily_posts': daily_posts,
                'comments_per_post': comments_per_post,
                'upvote_ratio': upvote_ratio
            },
            'benchmarks': reddit_benchmarks,
            'gaps': {
                'subscribers': reddit_benchmarks['subscribers'] - subscribers,
                'daily_posts': reddit_benchmarks['daily_posts'] - daily_posts,
                'comments_per_post': reddit_benchmarks['comments_per_post'] - comments_per_post
            },
            'strengths': self._identify_reddit_strengths(reddit_data, reddit_benchmarks),
            'weaknesses': self._identify_reddit_weaknesses(reddit_data, reddit_benchmarks)
        }

    def _identify_discord_strengths(
        self,
        discord_data: Dict[str, Any],
        benchmarks: Dict[str, Any]
    ) -> List[str]:
        """Identify Discord community strengths"""
        strengths = []

        members = discord_data.get('members', 0)
        daily_active = discord_data.get('daily_active', 0)
        messages_per_day = discord_data.get('messages_per_day', 0)

        if members >= benchmarks['members'] * 1.5:
            strengths.append(f"Strong member count ({members:,} members, 150% of benchmark)")

        engagement_rate = (daily_active / members * 100) if members > 0 else 0
        if engagement_rate >= 15:
            strengths.append(f"Excellent engagement rate ({engagement_rate:.1f}% daily active)")

        if messages_per_day >= benchmarks['messages_per_day'] * 1.2:
            strengths.append(f"High activity level ({messages_per_day:,} messages/day)")

        if not strengths:
            strengths.append("Community shows potential for growth")

        return strengths

    def _identify_discord_weaknesses(
        self,
        discord_data: Dict[str, Any],
        benchmarks: Dict[str, Any]
    ) -> List[str]:
        """Identify Discord community weaknesses"""
        weaknesses = []

        members = discord_data.get('members', 0)
        daily_active = discord_data.get('daily_active', 0)
        messages_per_day = discord_data.get('messages_per_day', 0)

        if members < benchmarks['members']:
            gap = benchmarks['members'] - members
            weaknesses.append(f"Member count below benchmark (need +{gap:,} members)")

        engagement_rate = (daily_active / members * 100) if members > 0 else 0
        if engagement_rate < 5:
            weaknesses.append(f"Low engagement rate ({engagement_rate:.1f}% daily active, target 10%+)")

        if messages_per_day < benchmarks['messages_per_day']:
            gap = benchmarks['messages_per_day'] - messages_per_day
            weaknesses.append(f"Low activity (need +{gap:,} messages/day)")

        if not weaknesses:
            weaknesses.append("No critical weaknesses detected")

        return weaknesses

    def _identify_reddit_strengths(
        self,
        reddit_data: Dict[str, Any],
        benchmarks: Dict[str, Any]
    ) -> List[str]:
        """Identify Reddit community strengths"""
        strengths = []

        subscribers = reddit_data.get('subscribers', 0)
        comments_per_post = reddit_data.get('comments_per_post', 0)
        upvote_ratio = reddit_data.get('upvote_ratio', 0)

        if subscribers >= benchmarks['subscribers'] * 1.5:
            strengths.append(f"Strong subscriber base ({subscribers:,}, 150% of benchmark)")

        if comments_per_post >= benchmarks['comments_per_post'] * 1.2:
            strengths.append(f"High engagement ({comments_per_post:.1f} comments/post)")

        if upvote_ratio >= 0.90:
            strengths.append(f"Positive community sentiment ({upvote_ratio*100:.0f}% upvote ratio)")

        if not strengths:
            strengths.append("Community is building momentum")

        return strengths

    def _identify_reddit_weaknesses(
        self,
        reddit_data: Dict[str, Any],
        benchmarks: Dict[str, Any]
    ) -> List[str]:
        """Identify Reddit community weaknesses"""
        weaknesses = []

        subscribers = reddit_data.get('subscribers', 0)
        daily_posts = reddit_data.get('daily_posts', 0)
        comments_per_post = reddit_data.get('comments_per_post', 0)

        if subscribers < benchmarks['subscribers']:
            gap = benchmarks['subscribers'] - subscribers
            weaknesses.append(f"Subscriber count below benchmark (need +{gap:,} subscribers)")

        if daily_posts < benchmarks['daily_posts']:
            weaknesses.append(f"Low posting frequency (need {benchmarks['daily_posts']} posts/day)")

        if comments_per_post < benchmarks['comments_per_post']:
            weaknesses.append(f"Low discussion engagement ({comments_per_post:.1f} comments/post)")

        if not weaknesses:
            weaknesses.append("No critical weaknesses detected")

        return weaknesses

    def _calculate_overall_health(
        self,
        discord_analysis: Dict[str, Any],
        reddit_analysis: Dict[str, Any]
    ) -> int:
        """Calculate overall community health score"""
        discord_score = discord_analysis.get('score', 0)
        reddit_score = reddit_analysis.get('score', 0)

        # Weight Discord more heavily (70%) as it's more important for indie games
        overall = (discord_score * 0.70) + (reddit_score * 0.30)

        return round(overall, 1)

    def _get_health_tier(self, score: float) -> str:
        """Get health tier classification"""
        if score >= 80:
            return 'Thriving'
        elif score >= 60:
            return 'Healthy'
        elif score >= 40:
            return 'Growing'
        else:
            return 'Needs Attention'

    def _generate_growth_strategies(
        self,
        discord_analysis: Dict[str, Any],
        reddit_analysis: Dict[str, Any],
        stage: str,
        game_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate community growth strategies"""
        strategies = []

        discord_score = discord_analysis.get('score', 0)
        reddit_score = reddit_analysis.get('score', 0)

        # Discord growth strategies
        if discord_score < 60:
            strategies.append({
                'platform': 'Discord',
                'priority': 'HIGH',
                'strategy': 'Build Initial Community',
                'tactics': [
                    'Add Discord link to Steam page, Twitter bio, YouTube descriptions',
                    'Create welcoming #welcome and #rules channels',
                    'Run Discord-exclusive giveaways (game keys, merch)',
                    'Host weekly dev Q&A sessions',
                    'Create role system for testers, supporters, content creators'
                ],
                'expected_impact': '+200-500 members in 30 days',
                'time_required': '2-3 hours/week'
            })

            strategies.append({
                'platform': 'Discord',
                'priority': 'HIGH',
                'strategy': 'Boost Engagement Rate',
                'tactics': [
                    'Daily discussion prompts in #general ("What\'s your favorite build?")',
                    'Screenshot/art sharing channel with emoji reactions',
                    'Bug reporting channel (makes users feel involved)',
                    'Meme channel (organic community bonding)',
                    'Voice chat events (playtesting, game nights)'
                ],
                'expected_impact': '+5-10% engagement rate',
                'time_required': '30 min/day'
            })

        # Reddit growth strategies
        if reddit_score < 60:
            strategies.append({
                'platform': 'Reddit',
                'priority': 'MEDIUM',
                'strategy': 'Establish Subreddit Presence',
                'tactics': [
                    'Create r/YourGame subreddit early (claim the name)',
                    'Post weekly dev blogs with behind-the-scenes content',
                    'Cross-post to relevant subreddits (r/indiegaming, r/roguelikes, etc.)',
                    'Run "Wishlist Wednesday" weekly threads',
                    'Respond to ALL comments within 24h (shows you care)'
                ],
                'expected_impact': '+100-300 subscribers in 30 days',
                'time_required': '1 hour/week'
            })

            strategies.append({
                'platform': 'Reddit',
                'priority': 'MEDIUM',
                'strategy': 'Drive Discussion Engagement',
                'tactics': [
                    'Ask open-ended questions in posts ("What features do you want?")',
                    'Create polls (build vs patch notes preferences)',
                    'Share GIFs/videos (higher engagement than images)',
                    'Highlight community suggestions you implemented',
                    'Run AMA (Ask Me Anything) sessions'
                ],
                'expected_impact': '+5-8 comments per post',
                'time_required': '30 min/week'
            })

        # Cross-platform strategies
        strategies.append({
            'platform': 'Cross-Platform',
            'priority': 'HIGH',
            'strategy': 'Community Event Calendar',
            'tactics': [
                'Weekly: Dev update (alternating Discord/Reddit)',
                'Bi-weekly: Screenshot Saturday (#screenshotsaturday)',
                'Monthly: Community playtest sessions',
                'Quarterly: Major announcement livestream',
                'Pre-launch: Discord nitro giveaway for most active members'
            ],
            'expected_impact': '+25% overall community engagement',
            'time_required': '3-4 hours/week'
        })

        return strategies[:5]  # Top 5 strategies

    def _generate_moderation_recommendations(
        self,
        discord_analysis: Dict[str, Any],
        reddit_analysis: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate moderation recommendations"""
        recommendations = []

        # Discord moderation
        recommendations.append({
            'platform': 'Discord',
            'category': 'Moderation Setup',
            'recommendation': 'Implement tiered moderation system',
            'implementation': 'Admin (you) → Moderators (2-3 trusted) → Helper (5-8 active members)',
            'rationale': 'Scales moderation as community grows, prevents burnout'
        })

        recommendations.append({
            'platform': 'Discord',
            'category': 'Automation',
            'recommendation': 'Use moderation bots',
            'implementation': 'MEE6 or Dyno for auto-moderation (spam, links, caps)',
            'rationale': 'Reduces manual moderation workload by 70%'
        })

        # Reddit moderation
        recommendations.append({
            'platform': 'Reddit',
            'category': 'Moderation Setup',
            'recommendation': 'Configure AutoModerator',
            'implementation': 'Filter spam, auto-flair posts, welcome new members',
            'rationale': 'Maintains quality with minimal manual effort'
        })

        recommendations.append({
            'platform': 'Reddit',
            'category': 'Community Guidelines',
            'recommendation': 'Post clear community rules',
            'implementation': 'Pin rules post, create wiki page with examples',
            'rationale': 'Reduces toxic behavior by 40-60%'
        })

        # Cross-platform
        recommendations.append({
            'platform': 'Both',
            'category': 'Response Strategy',
            'recommendation': 'Develop crisis response plan',
            'implementation': 'Template responses for bugs, delays, negative reviews',
            'rationale': 'Maintains trust during difficult situations'
        })

        return recommendations

    def _generate_milestones(self, stage: str) -> List[Dict[str, Any]]:
        """Generate community growth milestones"""
        milestones = [
            {'members': 100, 'achievement': 'First 100 members', 'celebration': 'Thank you post, role badge'},
            {'members': 500, 'achievement': 'Growing community', 'celebration': 'Community poll on next feature'},
            {'members': 1000, 'achievement': '1K milestone', 'celebration': 'Discord server boost giveaway'},
            {'members': 5000, 'achievement': 'Thriving community', 'celebration': 'Exclusive in-game item for members'},
            {'members': 10000, 'achievement': '10K members!', 'celebration': 'Major announcement livestream event'}
        ]

        return milestones

    def _get_best_practices(self) -> List[str]:
        """Get community management best practices"""
        return [
            "**Be authentic** - Share real development struggles and wins, not just marketing",
            "**Respond quickly** - <24h response time builds trust and engagement",
            "**Celebrate community** - Highlight fan art, bug reports, suggestions",
            "**Be consistent** - Regular updates matter more than frequency",
            "**Don't over-moderate** - Light touch unless spam/toxicity appears",
            "**Give members ownership** - Let them contribute (testing, feedback, content)",
            "**Create insider feel** - Exclusive previews, early access, behind-the-scenes",
            "**Listen more than you talk** - Community feedback is goldmine for features",
            "**Avoid negativity** - Don't argue with critics, acknowledge and move forward",
            "**Plan for scale** - Set up moderation systems before you need them"
        ]
