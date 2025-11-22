"""
Screenshot Narrative Flow Analysis

Analyzes how screenshots tell a story and guide players through
understanding the game's features and appeal.
"""

from typing import Dict, Any, List


class ScreenshotFlowAnalyzer:
    """Analyzes screenshot narrative flow and feature coverage"""

    # Screenshot types and their importance
    SCREENSHOT_TYPES = {
        'hero_moment': {
            'description': 'Epic gameplay moment that excites players',
            'importance': 'CRITICAL',
            'position': 'first',
            'examples': ['Boss fight', 'Major ability unlock', 'Dramatic scene']
        },
        'gameplay_core': {
            'description': 'Core gameplay loop demonstration',
            'importance': 'CRITICAL',
            'position': 'early',
            'examples': ['Combat', 'Puzzle-solving', 'Exploration']
        },
        'unique_feature': {
            'description': 'Unique mechanic or selling point',
            'importance': 'HIGH',
            'position': 'middle',
            'examples': ['Deckbuilding UI', 'Procedural generation', 'Crafting system']
        },
        'variety': {
            'description': 'Different environments/enemies/scenarios',
            'importance': 'HIGH',
            'position': 'middle',
            'examples': ['Different biomes', 'Enemy variety', 'Level themes']
        },
        'progression': {
            'description': 'Character/base progression systems',
            'importance': 'MEDIUM',
            'position': 'middle',
            'examples': ['Skill tree', 'Upgrade menu', 'Unlocks screen']
        },
        'atmosphere': {
            'description': 'Mood and art style showcase',
            'importance': 'MEDIUM',
            'position': 'any',
            'examples': ['Beautiful vista', 'Atmospheric scene', 'Art detail']
        },
        'social_proof': {
            'description': 'Multiplayer or community features',
            'importance': 'LOW',
            'position': 'late',
            'examples': ['Co-op gameplay', 'Leaderboard', 'Player creations']
        }
    }

    # Genre-specific screenshot priorities
    GENRE_PRIORITIES = {
        'roguelike': ['gameplay_core', 'unique_feature', 'variety', 'progression'],
        'deckbuilder': ['unique_feature', 'gameplay_core', 'variety', 'progression'],
        'horror': ['atmosphere', 'hero_moment', 'gameplay_core', 'variety'],
        'platformer': ['hero_moment', 'gameplay_core', 'variety', 'atmosphere'],
        'strategy': ['unique_feature', 'gameplay_core', 'variety', 'progression'],
        'rpg': ['hero_moment', 'gameplay_core', 'progression', 'variety'],
        'puzzle': ['gameplay_core', 'unique_feature', 'variety'],
        'multiplayer': ['gameplay_core', 'social_proof', 'variety', 'unique_feature'],
    }

    def __init__(self):
        """Initialize the screenshot flow analyzer"""
        pass

    def analyze_flow(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        screenshot_count: int = 5
    ) -> Dict[str, Any]:
        """
        Analyze screenshot narrative flow and coverage

        Args:
            game_data: Game information
            sales_data: Sales data
            screenshot_count: Number of screenshots (Steam allows up to 5)

        Returns:
            Flow analysis with recommendations
        """
        genres = game_data.get('genres', '').lower()
        tags = game_data.get('tags', '').lower()

        # Identify primary genre
        primary_genre = self._identify_primary_genre(genres, tags)

        # Get genre-specific priorities
        genre_priorities = self.GENRE_PRIORITIES.get(primary_genre, ['gameplay_core', 'unique_feature', 'variety'])

        # Analyze ideal screenshot sequence
        ideal_sequence = self._generate_ideal_sequence(primary_genre, screenshot_count)

        # Calculate flow score
        flow_score = self._calculate_flow_score(screenshot_count, primary_genre)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            screenshot_count, primary_genre, ideal_sequence
        )

        return {
            'flow_score': flow_score,
            'screenshot_count': screenshot_count,
            'max_screenshots': 5,
            'primary_genre': primary_genre,
            'ideal_sequence': ideal_sequence,
            'recommendations': recommendations,
            'best_practices': self._get_best_practices(primary_genre)
        }

    def _identify_primary_genre(self, genres: str, tags: str) -> str:
        """Identify the primary genre from genres and tags"""
        combined = f"{genres} {tags}".lower()

        # Priority order (most specific first)
        genre_priority = [
            'roguelike', 'deckbuilder', 'horror', 'multiplayer',
            'platformer', 'puzzle', 'strategy', 'rpg'
        ]

        for genre in genre_priority:
            if genre in combined:
                return genre

        return 'general'

    def _generate_ideal_sequence(
        self,
        primary_genre: str,
        screenshot_count: int
    ) -> List[Dict[str, Any]]:
        """Generate ideal screenshot sequence for genre"""
        sequence = []

        # Get genre priorities
        priorities = self.GENRE_PRIORITIES.get(primary_genre, ['gameplay_core', 'unique_feature', 'variety'])

        # Build sequence based on screenshot count
        if screenshot_count >= 1:
            # Screenshot 1: ALWAYS hero moment (hook)
            sequence.append({
                'position': 1,
                'type': 'hero_moment',
                'description': self.SCREENSHOT_TYPES['hero_moment']['description'],
                'importance': 'CRITICAL',
                'purpose': 'Hook player interest with exciting moment',
                'examples': self.SCREENSHOT_TYPES['hero_moment']['examples']
            })

        if screenshot_count >= 2:
            # Screenshot 2: Core gameplay
            sequence.append({
                'position': 2,
                'type': 'gameplay_core',
                'description': self.SCREENSHOT_TYPES['gameplay_core']['description'],
                'importance': 'CRITICAL',
                'purpose': 'Show what players actually DO in the game',
                'examples': self.SCREENSHOT_TYPES['gameplay_core']['examples']
            })

        if screenshot_count >= 3:
            # Screenshot 3: Unique feature or selling point
            first_priority = priorities[0] if priorities else 'unique_feature'
            sequence.append({
                'position': 3,
                'type': first_priority,
                'description': self.SCREENSHOT_TYPES.get(first_priority, {}).get('description', 'Key feature'),
                'importance': 'HIGH',
                'purpose': 'Differentiate from competitors with unique mechanic',
                'examples': self.SCREENSHOT_TYPES.get(first_priority, {}).get('examples', ['Unique mechanic'])
            })

        if screenshot_count >= 4:
            # Screenshot 4: Variety or progression
            second_priority = priorities[1] if len(priorities) > 1 else 'variety'
            sequence.append({
                'position': 4,
                'type': second_priority,
                'description': self.SCREENSHOT_TYPES.get(second_priority, {}).get('description', 'Content variety'),
                'importance': 'MEDIUM',
                'purpose': 'Show game has variety and depth',
                'examples': self.SCREENSHOT_TYPES.get(second_priority, {}).get('examples', ['Different content'])
            })

        if screenshot_count >= 5:
            # Screenshot 5: Atmosphere or late-game content
            third_priority = priorities[2] if len(priorities) > 2 else 'atmosphere'
            sequence.append({
                'position': 5,
                'type': third_priority,
                'description': self.SCREENSHOT_TYPES.get(third_priority, {}).get('description', 'Visual appeal'),
                'importance': 'MEDIUM',
                'purpose': 'Reinforce art style and polish',
                'examples': self.SCREENSHOT_TYPES.get(third_priority, {}).get('examples', ['Polished visuals'])
            })

        return sequence

    def _calculate_flow_score(
        self,
        screenshot_count: int,
        primary_genre: str
    ) -> int:
        """Calculate flow score based on screenshot count and optimal sequence"""
        score = 50  # Base score

        # Screenshot count score (40 points max)
        if screenshot_count >= 5:
            score += 40  # Using all 5 screenshots
        elif screenshot_count == 4:
            score += 30
        elif screenshot_count == 3:
            score += 20
        elif screenshot_count == 2:
            score += 10
        else:
            score += 0  # Only 1 screenshot is bad

        # Genre appropriateness (20 points max)
        # In a real implementation, this would analyze actual screenshots
        # For now, assume moderate appropriateness
        score += 10

        # Variety and pacing (20 points max)
        # Assume moderate variety if using 3+ screenshots
        if screenshot_count >= 3:
            score += 15
        elif screenshot_count >= 2:
            score += 8

        # Technical quality (20 points max)
        # Assume moderate quality
        score += 10

        return min(100, max(0, score))

    def _generate_recommendations(
        self,
        screenshot_count: int,
        primary_genre: str,
        ideal_sequence: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate screenshot recommendations"""
        recommendations = []

        # Recommendation 1: Use all 5 screenshots
        if screenshot_count < 5:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Screenshot Count',
                'issue': f'Only using {screenshot_count}/5 available screenshots',
                'recommendation': f'Add {5 - screenshot_count} more screenshot{"s" if 5 - screenshot_count > 1 else ""} to maximize store page appeal',
                'impact': 'More screenshots = higher conversion rate (industry data shows 15-25% CTR boost)',
                'action': 'Capture and upload additional screenshots showing different aspects of the game'
            })

        # Recommendation 2: Follow ideal sequence
        if screenshot_count >= 1:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Narrative Flow',
                'issue': 'Screenshots should tell a story',
                'recommendation': 'Follow the ideal sequence to guide players through understanding your game',
                'impact': 'Clear narrative flow reduces confusion and increases wishlist conversion',
                'action': f'Use this sequence: {" → ".join([s["type"].replace("_", " ").title() for s in ideal_sequence])}'
            })

        # Recommendation 3: Technical quality
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Technical Quality',
            'issue': 'Screenshot quality affects perceived game quality',
            'recommendation': 'Ensure all screenshots are high-resolution, well-lit, and show polished gameplay',
            'impact': 'Low-quality screenshots hurt conversion rate by 10-15%',
            'action': 'Use 1920x1080 or higher, disable debug UI, use best lighting/camera angles'
        })

        # Recommendation 4: UI visibility
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'UI Clarity',
            'issue': 'Players need to understand the gameplay from screenshots',
            'recommendation': 'Show clear UI elements that explain game mechanics',
            'impact': 'Clear UI in screenshots reduces "what do I do?" confusion',
            'action': 'Include at least 2-3 screenshots with visible UI (health, abilities, menus)'
        })

        # Genre-specific recommendations
        genre_specific = self._get_genre_specific_recommendations(primary_genre)
        if genre_specific:
            recommendations.extend(genre_specific)

        return recommendations[:6]  # Top 6 recommendations

    def _get_genre_specific_recommendations(self, genre: str) -> List[Dict[str, Any]]:
        """Get genre-specific screenshot recommendations"""
        genre_recs = {
            'roguelike': [
                {
                    'priority': 'HIGH',
                    'category': 'Roguelike-Specific',
                    'issue': 'Roguelike players want to see run variety',
                    'recommendation': 'Show different builds, items, or run states',
                    'impact': 'Demonstrates replayability, a key roguelike selling point',
                    'action': 'Include screenshots from different runs showing varied gameplay'
                }
            ],
            'deckbuilder': [
                {
                    'priority': 'HIGH',
                    'category': 'Deckbuilder-Specific',
                    'issue': 'Deckbuilder players want to see deck/card variety',
                    'recommendation': 'Dedicate 1-2 screenshots to deck-building UI and card variety',
                    'impact': 'Shows depth of card pool and strategic options',
                    'action': 'Screenshot deck-building screen with diverse cards visible'
                }
            ],
            'horror': [
                {
                    'priority': 'HIGH',
                    'category': 'Horror-Specific',
                    'issue': 'Horror games sell on atmosphere',
                    'recommendation': 'Use dark, moody screenshots with visible threats',
                    'impact': 'Atmospheric screenshots are critical for horror conversion',
                    'action': 'Emphasize lighting, shadows, and unsettling environments'
                }
            ],
            'platformer': [
                {
                    'priority': 'MEDIUM',
                    'category': 'Platformer-Specific',
                    'issue': 'Platformers need to show movement and level design',
                    'recommendation': 'Capture mid-jump or mid-action shots showing platforming challenges',
                    'impact': 'Static screenshots make platformers look boring',
                    'action': 'Use dynamic camera angles showing verticality and movement'
                }
            ],
            'strategy': [
                {
                    'priority': 'HIGH',
                    'category': 'Strategy-Specific',
                    'issue': 'Strategy players want to see strategic depth',
                    'recommendation': 'Show complex decisions, resource management, or tactical situations',
                    'impact': 'Demonstrates game depth and complexity',
                    'action': 'Screenshot decision points with multiple options visible'
                }
            ],
        }

        return genre_recs.get(genre, [])

    def _get_best_practices(self, genre: str) -> List[str]:
        """Get screenshot best practices"""
        practices = [
            "**Use all 5 screenshot slots** - More screenshots = higher conversion rate",
            "**First screenshot is critical** - It's the thumbnail in search results, make it exciting",
            "**Show, don't tell** - Demonstrate gameplay, not static menus",
            "**Variety matters** - Different environments, enemies, abilities keep viewers engaged",
            "**High resolution only** - Minimum 1920x1080, preferably 4K",
            "**Disable debug UI** - Remove FPS counters, debug text, development tools",
            "**Tell a story** - Screenshots should flow from introduction → core gameplay → depth → variety",
            "**Include UI in 2-3 screenshots** - Players need to understand controls and mechanics",
            "**Use max graphics settings** - Unless pixel art, show the game at its best visual quality",
            "**Action over beauty** - Exciting gameplay moment > pretty but static screenshot",
        ]

        # Add genre-specific practices
        genre_practices = {
            'roguelike': "**Show build variety** - Multiple screenshots with different items/abilities demonstrates replayability",
            'deckbuilder': "**Feature your cards** - Dedicate 1-2 screenshots to showing card variety and deck-building",
            'horror': "**Nail the atmosphere** - Dark, moody screenshots with visible (but not overexposed) threats",
            'multiplayer': "**Show player count** - Screenshots with multiple players demonstrate active community",
            'platformer': "**Capture motion** - Mid-jump, mid-ability screenshots show movement feel",
        }

        if genre in genre_practices:
            practices.append(genre_practices[genre])

        return practices

    def generate_screenshot_brief(
        self,
        game_data: Dict[str, Any],
        screenshot_count: int = 5
    ) -> str:
        """Generate a screenshot capture brief for developers"""
        genres = game_data.get('genres', '').lower()
        tags = game_data.get('tags', '').lower()
        primary_genre = self._identify_primary_genre(genres, tags)

        ideal_sequence = self._generate_ideal_sequence(primary_genre, screenshot_count)

        brief = "# Screenshot Capture Brief\n\n"
        brief += f"**Game:** {game_data.get('name', 'Your Game')}\n"
        brief += f"**Genre:** {primary_genre.title()}\n"
        brief += f"**Target:** {screenshot_count} screenshots\n\n"

        brief += "## Ideal Screenshot Sequence\n\n"

        for shot in ideal_sequence:
            brief += f"### Screenshot #{shot['position']}: {shot['type'].replace('_', ' ').title()}\n"
            brief += f"**Purpose:** {shot['purpose']}\n"
            brief += f"**Importance:** {shot['importance']}\n"
            brief += f"**Examples:** {', '.join(shot['examples'])}\n\n"

        brief += "## Technical Requirements\n\n"
        brief += "- Resolution: Minimum 1920x1080 (4K preferred)\n"
        brief += "- Format: PNG or JPG\n"
        brief += "- Aspect ratio: 16:9\n"
        brief += "- Graphics settings: Maximum (unless pixel art)\n"
        brief += "- Remove: Debug UI, FPS counters, watermarks\n\n"

        return brief
