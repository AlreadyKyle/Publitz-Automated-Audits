"""
Tag Insights & Impression Estimates

Provides specific tag recommendations with estimated traffic impact.
Identifies high-value tags to add and low-value tags to remove.
"""

from typing import Dict, Any, List, Tuple


class TagInsightsAnalyzer:
    """Analyzes tags and provides impression estimates"""

    # Tag traffic tiers (estimated daily impressions)
    TAG_TRAFFIC = {
        # Mega tags (1M+ daily impressions)
        'indie': {'traffic': 1200000, 'tier': 'mega', 'specificity': 'low'},
        'action': {'traffic': 1000000, 'tier': 'mega', 'specificity': 'low'},
        'rpg': {'traffic': 900000, 'tier': 'mega', 'specificity': 'medium'},
        'strategy': {'traffic': 850000, 'tier': 'mega', 'specificity': 'medium'},
        'adventure': {'traffic': 800000, 'tier': 'mega', 'specificity': 'low'},
        'simulation': {'traffic': 750000, 'tier': 'mega', 'specificity': 'medium'},

        # Major tags (100K-1M)
        'roguelike': {'traffic': 350000, 'tier': 'major', 'specificity': 'high'},
        'roguelite': {'traffic': 300000, 'tier': 'major', 'specificity': 'high'},
        'pixel art': {'traffic': 280000, 'tier': 'major', 'specificity': 'medium'},
        '2d': {'traffic': 250000, 'tier': 'major', 'specificity': 'low'},
        'singleplayer': {'traffic': 400000, 'tier': 'major', 'specificity': 'low'},
        'multiplayer': {'traffic': 380000, 'tier': 'major', 'specificity': 'low'},
        'horror': {'traffic': 220000, 'tier': 'major', 'specificity': 'high'},
        'deckbuilder': {'traffic': 180000, 'tier': 'major', 'specificity': 'high'},
        'card game': {'traffic': 160000, 'tier': 'major', 'specificity': 'high'},
        'turn-based': {'traffic': 140000, 'tier': 'major', 'specificity': 'medium'},
        'platformer': {'traffic': 130000, 'tier': 'major', 'specificity': 'medium'},
        'puzzle': {'traffic': 120000, 'tier': 'major', 'specificity': 'medium'},

        # Medium tags (10K-100K)
        'detective': {'traffic': 45000, 'tier': 'medium', 'specificity': 'high'},
        'mystery': {'traffic': 48000, 'tier': 'medium', 'specificity': 'high'},
        'visual novel': {'traffic': 95000, 'tier': 'medium', 'specificity': 'high'},
        'dating sim': {'traffic': 75000, 'tier': 'medium', 'specificity': 'high'},
        'dungeon crawler': {'traffic': 80000, 'tier': 'medium', 'specificity': 'high'},
        'procedural generation': {'traffic': 85000, 'tier': 'medium', 'specificity': 'high'},
        'story rich': {'traffic': 92000, 'tier': 'medium', 'specificity': 'medium'},
        'atmospheric': {'traffic': 65000, 'tier': 'medium', 'specificity': 'medium'},
        'crafting': {'traffic': 70000, 'tier': 'medium', 'specificity': 'medium'},
        'survival': {'traffic': 88000, 'tier': 'medium', 'specificity': 'medium'},
        '3d': {'traffic': 90000, 'tier': 'medium', 'specificity': 'low'},
        'first-person': {'traffic': 75000, 'tier': 'medium', 'specificity': 'low'},
        'third-person': {'traffic': 68000, 'tier': 'medium', 'specificity': 'low'},

        # Niche tags (1K-10K)
        'colony sim': {'traffic': 35000, 'tier': 'niche', 'specificity': 'high'},
        'city builder': {'traffic': 42000, 'tier': 'niche', 'specificity': 'high'},
        'tower defense': {'traffic': 38000, 'tier': 'niche', 'specificity': 'high'},
        'metroidvania': {'traffic': 55000, 'tier': 'niche', 'specificity': 'high'},
        'souls-like': {'traffic': 48000, 'tier': 'niche', 'specificity': 'high'},
        'bullet hell': {'traffic': 28000, 'tier': 'niche', 'specificity': 'high'},
        'management': {'traffic': 40000, 'tier': 'niche', 'specificity': 'medium'},
        'sandbox': {'traffic': 45000, 'tier': 'niche', 'specificity': 'medium'},
        'noir': {'traffic': 15000, 'tier': 'niche', 'specificity': 'high'},
        'investigation': {'traffic': 18000, 'tier': 'niche', 'specificity': 'high'},
    }

    def __init__(self):
        """Initialize the tag insights analyzer"""
        pass

    def analyze_tags(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze current tags and provide improvement recommendations

        Args:
            game_data: Game information with tags and genres
            sales_data: Sales data for engagement metrics

        Returns:
            Tag analysis with recommendations and impression estimates
        """
        # Extract current tags
        current_tags = self._extract_tags(game_data)

        # Analyze current tags
        current_analysis = self._analyze_current_tags(current_tags, sales_data)

        # Suggest tags to add
        suggested_additions = self._suggest_tag_additions(game_data, current_tags)

        # Identify tags to remove/replace
        suggested_removals = self._suggest_tag_removals(current_tags, current_analysis)

        # Calculate total impression impact
        impression_impact = self._calculate_impression_impact(
            current_analysis, suggested_additions, suggested_removals
        )

        return {
            'current_tags': current_tags,
            'tag_count': len(current_tags),
            'current_analysis': current_analysis,
            'suggested_additions': suggested_additions,
            'suggested_removals': suggested_removals,
            'impression_impact': impression_impact,
            'optimization_score': self._calculate_optimization_score(
                len(current_tags), current_analysis, suggested_additions
            )
        }

    def _extract_tags(self, game_data: Dict[str, Any]) -> List[str]:
        """Extract normalized tags from game data"""
        tags_str = game_data.get('tags', '')
        genres_str = game_data.get('genres', '')

        all_tags_str = f"{tags_str}, {genres_str}"
        tags = [t.strip().lower() for t in all_tags_str.split(',') if t.strip()]

        return list(set(tags))  # Remove duplicates

    def _analyze_current_tags(
        self,
        current_tags: List[str],
        sales_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze each current tag"""
        analysis = []

        for tag in current_tags:
            tag_data = self.TAG_TRAFFIC.get(tag)

            if tag_data:
                # Estimate your visibility in this tag (based on engagement)
                reviews_total = sales_data.get('reviews_total', 0)

                # More reviews = higher visibility in tag pages
                if reviews_total > 1000:
                    visibility_percent = 0.006  # 0.6% of tag traffic
                elif reviews_total > 500:
                    visibility_percent = 0.004  # 0.4%
                elif reviews_total > 100:
                    visibility_percent = 0.002  # 0.2%
                else:
                    visibility_percent = 0.001  # 0.1%

                daily_impressions = int(tag_data['traffic'] * visibility_percent)

                analysis.append({
                    'tag': tag,
                    'tier': tag_data['tier'],
                    'specificity': tag_data['specificity'],
                    'total_daily_traffic': tag_data['traffic'],
                    'your_daily_impressions': daily_impressions,
                    'your_visibility_percent': round(visibility_percent * 100, 3),
                    'status': 'optimal' if tag_data['specificity'] == 'high' else 'good' if tag_data['specificity'] == 'medium' else 'too_broad'
                })
            else:
                # Unknown tag (might be very niche or misspelled)
                analysis.append({
                    'tag': tag,
                    'tier': 'unknown',
                    'specificity': 'unknown',
                    'total_daily_traffic': 0,
                    'your_daily_impressions': 0,
                    'your_visibility_percent': 0,
                    'status': 'unknown'
                })

        return sorted(analysis, key=lambda x: x['your_daily_impressions'], reverse=True)

    def _suggest_tag_additions(
        self,
        game_data: Dict[str, Any],
        current_tags: List[str]
    ) -> List[Dict[str, Any]]:
        """Suggest high-value tags to add"""
        genres = game_data.get('genres', '').lower()
        tags = game_data.get('tags', '').lower()
        combined = f"{genres} {tags}"

        suggestions = []

        # Genre-specific recommendations
        recommendations = {
            'roguelike': ['roguelike', 'roguelite', 'procedural generation', 'dungeon crawler', 'turn-based'],
            'deckbuilder': ['deckbuilder', 'card game', 'roguelike', 'strategy', 'turn-based'],
            'horror': ['horror', 'atmospheric', 'first-person', 'survival', 'story rich'],
            'detective': ['detective', 'mystery', 'investigation', 'noir', 'story rich'],
            'strategy': ['strategy', 'turn-based', 'management', 'simulation'],
            'rpg': ['rpg', 'story rich', 'character customization', 'turn-based'],
            'platformer': ['platformer', '2d', 'pixel art', 'metroidvania'],
            'puzzle': ['puzzle', 'casual', 'singleplayer', '2d'],
        }

        # Find matching genre recommendations
        for genre_key, rec_tags in recommendations.items():
            if genre_key in combined:
                for rec_tag in rec_tags:
                    if rec_tag not in current_tags and rec_tag in self.TAG_TRAFFIC:
                        tag_data = self.TAG_TRAFFIC[rec_tag]

                        # Estimate impact if added (assume 0.2% visibility for new tag)
                        estimated_impressions = int(tag_data['traffic'] * 0.002)

                        suggestions.append({
                            'tag': rec_tag,
                            'reason': f"High-traffic {tag_data['tier']} tag for {genre_key} games",
                            'tier': tag_data['tier'],
                            'specificity': tag_data['specificity'],
                            'estimated_additional_impressions_daily': estimated_impressions,
                            'estimated_additional_impressions_monthly': estimated_impressions * 30,
                            'priority': 'HIGH' if tag_data['tier'] in ['major', 'mega'] and tag_data['specificity'] == 'high' else 'MEDIUM'
                        })

        # Always recommend singleplayer or multiplayer if not present
        if 'singleplayer' not in current_tags and 'multiplayer' not in current_tags:
            tag = 'singleplayer'  # Assume singleplayer by default
            tag_data = self.TAG_TRAFFIC[tag]
            estimated_impressions = int(tag_data['traffic'] * 0.002)

            suggestions.append({
                'tag': tag,
                'reason': "Essential player count tag",
                'tier': tag_data['tier'],
                'specificity': tag_data['specificity'],
                'estimated_additional_impressions_daily': estimated_impressions,
                'estimated_additional_impressions_monthly': estimated_impressions * 30,
                'priority': 'HIGH'
            })

        # Always recommend art style tag if not present
        art_tags = ['pixel art', '2d', '3d', 'hand-drawn', 'low-poly']
        has_art_tag = any(tag in current_tags for tag in art_tags)

        if not has_art_tag and 'pixel' in combined:
            tag = 'pixel art'
            tag_data = self.TAG_TRAFFIC[tag]
            estimated_impressions = int(tag_data['traffic'] * 0.002)

            suggestions.append({
                'tag': tag,
                'reason': "Popular art style tag",
                'tier': tag_data['tier'],
                'specificity': tag_data['specificity'],
                'estimated_additional_impressions_daily': estimated_impressions,
                'estimated_additional_impressions_monthly': estimated_impressions * 30,
                'priority': 'MEDIUM'
            })

        # Sort by estimated impact
        suggestions.sort(key=lambda x: x['estimated_additional_impressions_daily'], reverse=True)

        return suggestions[:8]  # Top 8 suggestions

    def _suggest_tag_removals(
        self,
        current_tags: List[str],
        current_analysis: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Suggest tags to remove (too broad or underperforming)"""
        removals = []

        for tag_analysis in current_analysis:
            tag = tag_analysis['tag']
            status = tag_analysis['status']

            # Remove if too broad (mega tier + low specificity)
            if status == 'too_broad':
                removals.append({
                    'tag': tag,
                    'reason': f"Too broad ({tag_analysis['tier']} tier) - low visibility (%{tag_analysis['your_visibility_percent']:.3f})",
                    'current_impressions': tag_analysis['your_daily_impressions'],
                    'replacement_suggestion': self._get_replacement_suggestion(tag)
                })

            # Remove if unknown tag
            elif status == 'unknown':
                removals.append({
                    'tag': tag,
                    'reason': "Unknown tag - not in Steam's main tag database",
                    'current_impressions': 0,
                    'replacement_suggestion': "Check spelling or use a more common tag"
                })

        return removals

    def _get_replacement_suggestion(self, broad_tag: str) -> str:
        """Get specific replacement for a broad tag"""
        replacements = {
            'adventure': 'Choose more specific: Mystery, Detective, Platformer, etc.',
            'action': 'Choose more specific: Bullet Hell, Hack and Slash, etc.',
            'indie': 'Keep if using <15 tags, otherwise use more specific genre',
            '2d': 'Combine with art style: Pixel Art, Hand-Drawn, etc.',
            '3d': 'Combine with perspective: First-Person, Third-Person, etc.',
        }

        return replacements.get(broad_tag, "Use a more specific genre or mechanic tag")

    def _calculate_impression_impact(
        self,
        current_analysis: List[Dict[str, Any]],
        suggested_additions: List[Dict[str, Any]],
        suggested_removals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate total impression impact of optimization"""

        # Current total
        current_daily = sum(tag['your_daily_impressions'] for tag in current_analysis)

        # Additions
        additions_daily = sum(tag['estimated_additional_impressions_daily'] for tag in suggested_additions)

        # Removals (lost impressions)
        removals_daily = sum(tag['current_impressions'] for tag in suggested_removals)

        # Net impact
        net_daily = additions_daily - removals_daily
        net_monthly = net_daily * 30

        return {
            'current_daily_impressions': current_daily,
            'current_monthly_impressions': current_daily * 30,
            'additional_from_new_tags': additions_daily,
            'lost_from_removals': removals_daily,
            'net_daily_change': net_daily,
            'net_monthly_change': net_monthly,
            'optimized_daily_impressions': current_daily + net_daily,
            'optimized_monthly_impressions': (current_daily + net_daily) * 30,
            'percent_improvement': round((net_daily / current_daily * 100) if current_daily > 0 else 0, 1)
        }

    def _calculate_optimization_score(
        self,
        tag_count: int,
        current_analysis: List[Dict[str, Any]],
        suggested_additions: List[Dict[str, Any]]
    ) -> int:
        """Calculate tag optimization score (0-100)"""

        score = 50  # Base score

        # Tag count (optimal is 15-20)
        if 15 <= tag_count <= 20:
            score += 20
        elif 10 <= tag_count < 15:
            score += 10
        elif tag_count > 20:
            score -= 5

        # High-specificity tags
        high_spec_count = sum(1 for tag in current_analysis if tag.get('specificity') == 'high')
        score += min(20, high_spec_count * 3)

        # If has suggestions, means room for improvement
        if suggested_additions:
            score -= min(15, len(suggested_additions) * 2)

        return max(0, min(100, score))
