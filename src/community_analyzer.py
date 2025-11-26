#!/usr/bin/env python3
"""
Community Analyzer - Analyzes community reach with generic detection

This module provides game-specific community recommendations and detects
when recommendations are generic vs. personalized.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

try:
    from src.generic_detection import (
        detect_generic_subreddits,
        detect_generic_influencers,
        detect_generic_curators,
        adjust_score_for_generic_data
    )
except ImportError:
    import sys
    sys.path.insert(0, '/home/user/Publitz-Automated-Audits')
    from src.generic_detection import (
        detect_generic_subreddits,
        detect_generic_influencers,
        detect_generic_curators,
        adjust_score_for_generic_data
    )


@dataclass
class CommunityAnalysis:
    """Results from community reach analysis"""
    subreddit_score: int
    influencer_score: int
    curator_score: int
    overall_score: int
    subreddit_recommendations: List[str]
    influencer_recommendations: List[str]
    curator_recommendations: List[str]
    warnings: List[str]
    value_labels: Dict[str, str]
    improvements: List[str]


def analyze_community_reach(
    game_data: Dict[str, Any],
    subreddit_list: Optional[List[str]] = None,
    influencer_list: Optional[List[str]] = None,
    curator_list: Optional[List[str]] = None
) -> CommunityAnalysis:
    """
    Analyze community reach and detect generic vs. personalized recommendations.

    Args:
        game_data: Game data including genres, tags, etc.
        subreddit_list: Optional list of recommended subreddits
        influencer_list: Optional list of recommended influencers
        curator_list: Optional list of recommended curators

    Returns:
        CommunityAnalysis with scores, recommendations, and warnings
    """
    warnings = []
    value_labels = {}
    improvements = []

    # Generate or validate subreddit recommendations
    if subreddit_list is None:
        subreddit_list = _generate_subreddit_recommendations(game_data)

    # Detect generic subreddits and adjust score
    subreddit_detection = detect_generic_subreddits(subreddit_list)
    subreddit_adjustment = adjust_score_for_generic_data(
        section_score=85,  # Base score for having recommendations
        section_name="Community Reach (Subreddits)",
        detection_result=subreddit_detection
    )

    subreddit_score = subreddit_adjustment['adjusted_score']
    if subreddit_adjustment['was_adjusted']:
        warnings.append(subreddit_adjustment['warning'])
    value_labels['subreddits'] = subreddit_adjustment['value_label']
    if subreddit_adjustment.get('improvements'):
        improvements.append(subreddit_adjustment['improvements'])

    # Generate or validate influencer recommendations
    if influencer_list is None:
        influencer_list = _generate_influencer_recommendations(game_data)

    # Convert influencer list to expected format (list of dicts with name/description)
    influencer_dicts = []
    for inf in influencer_list:
        if isinstance(inf, dict):
            influencer_dicts.append(inf)
        else:
            # String format - use as both name and description
            influencer_dicts.append({'name': inf, 'description': inf})

    # Detect generic influencers and adjust score
    influencer_detection = detect_generic_influencers(influencer_dicts)
    influencer_adjustment = adjust_score_for_generic_data(
        section_score=80,  # Base score for having influencer recommendations
        section_name="Influencer Reach",
        detection_result=influencer_detection
    )

    influencer_score = influencer_adjustment['adjusted_score']
    if influencer_adjustment['was_adjusted']:
        warnings.append(influencer_adjustment['warning'])
    value_labels['influencers'] = influencer_adjustment['value_label']
    if influencer_adjustment.get('improvements'):
        improvements.append(influencer_adjustment['improvements'])

    # Generate or validate curator recommendations
    if curator_list is None:
        curator_list = _generate_curator_recommendations(game_data)

    # Convert curator list to expected format (list of strings with curator names)
    if curator_list and isinstance(curator_list[0], dict):
        curator_names = [c.get('name', str(c)) for c in curator_list]
    else:
        curator_names = curator_list

    # Detect generic curators and adjust score
    curator_detection = detect_generic_curators(curator_names)
    curator_adjustment = adjust_score_for_generic_data(
        section_score=75,  # Base score for having curator recommendations
        section_name="Steam Curator Reach",
        detection_result=curator_detection
    )

    curator_score = curator_adjustment['adjusted_score']
    if curator_adjustment['was_adjusted']:
        warnings.append(curator_adjustment['warning'])
    value_labels['curators'] = curator_adjustment['value_label']
    if curator_adjustment.get('improvements'):
        improvements.append(curator_adjustment['improvements'])

    # Calculate overall community score (weighted average)
    overall_score = int(
        (subreddit_score * 0.4) +      # Subreddits: 40% weight
        (influencer_score * 0.4) +      # Influencers: 40% weight
        (curator_score * 0.2)           # Curators: 20% weight
    )

    return CommunityAnalysis(
        subreddit_score=subreddit_score,
        influencer_score=influencer_score,
        curator_score=curator_score,
        overall_score=overall_score,
        subreddit_recommendations=subreddit_list,
        influencer_recommendations=influencer_list,
        curator_recommendations=curator_list,
        warnings=warnings,
        value_labels=value_labels,
        improvements=improvements
    )


def _generate_subreddit_recommendations(game_data: Dict[str, Any]) -> List[str]:
    """
    Generate game-specific subreddit recommendations based on genres and tags.

    This is a smart recommendation system that suggests niche subreddits
    instead of generic ones.
    """
    subreddits = []
    genres = game_data.get('genres', [])
    tags = game_data.get('tags', [])

    # Map genres to specific subreddits
    genre_mapping = {
        'Roguelike': ['r/roguelikes', 'r/roguelikedev'],
        'Metroidvania': ['r/metroidvania'],
        'RPG': ['r/rpg_gamers', 'r/JRPG', 'r/CRPG'],
        'Strategy': ['r/strategyGames', 'r/4Xgaming'],
        'Puzzle': ['r/puzzles', 'r/puzzlegames'],
        'Horror': ['r/HorrorGaming', 'r/horror'],
        'Simulation': ['r/SimulationGaming', 'r/tycoon'],
        'Adventure': ['r/adventuregames'],
        'Visual Novel': ['r/visualnovels'],
        'Card Game': ['r/digitaltcg', 'r/cardgames'],
        'Rhythm': ['r/rhythmgames'],
        'Sports': ['r/sportsgames'],
        'Racing': ['r/simracing']
    }

    # Add genre-specific subreddits
    for genre in genres:
        if genre in genre_mapping:
            subreddits.extend(genre_mapping[genre])

    # Add art style subreddits
    if 'Pixel Graphics' in tags or 'Retro' in tags:
        subreddits.append('r/pixelart')
    if 'Low-Poly' in tags or 'Minimalist' in tags:
        subreddits.append('r/lowpoly')
    if 'Anime' in tags:
        subreddits.append('r/visualnovels')

    # Add development-related if indie
    if 'Indie' in genres:
        subreddits.extend(['r/indiedev', 'r/IndieDev'])

    # If we have no specific recommendations, return generic ones
    # (This will be flagged by the detector)
    if not subreddits:
        return ['r/gaming', 'r/pcgaming', 'r/indiegaming']

    # Remove duplicates
    return list(set(subreddits))[:10]


def _generate_influencer_recommendations(game_data: Dict[str, Any]) -> List[str]:
    """
    Generate influencer recommendations based on game genre.

    Returns specific influencer names/channels when possible.
    """
    genres = game_data.get('genres', [])

    # Genre-specific influencers (these are EXAMPLES - real implementation would use actual data)
    influencers = []

    if 'Roguelike' in genres or 'Roguelite' in genres:
        influencers.extend([
            'NorthernLion (roguelike specialist, 1M+ subs)',
            'Wanderbots (indie roguelike reviews)',
            'Retromation (roguelike coverage)'
        ])

    if 'Metroidvania' in genres:
        influencers.extend([
            'Skill Up (Metroidvania reviews)',
            'Mortismal Gaming (comprehensive RPG/Metroidvania reviews)'
        ])

    if 'Horror' in genres:
        influencers.extend([
            'ManlyBadassHero (horror indie specialist)',
            'Gab Smolders (horror gaming)'
        ])

    if 'Strategy' in genres or '4X' in genres:
        influencers.extend([
            'Quill18 (4X and strategy specialist)',
            'PotatoMcWhiskey (Civ and strategy games)'
        ])

    # If no specific influencers, return generic descriptions
    # (This will be flagged by detector)
    if not influencers:
        return [
            'General gaming channels',
            'Indie game reviewers',
            'Genre-appropriate streamers'
        ]

    return influencers[:10]


def _generate_curator_recommendations(game_data: Dict[str, Any]) -> List[str]:
    """
    Generate Steam curator recommendations based on game type.
    """
    genres = game_data.get('genres', [])
    curators = []

    # Genre-specific curators
    if 'Indie' in genres:
        curators.extend([
            'Indie Game Enthusiast',
            'Following Indies'
        ])

    if 'Roguelike' in genres:
        curators.append('Roguelike Recommendation Committee')

    if 'Horror' in genres:
        curators.append('Horror Games Curator')

    if 'Strategy' in genres:
        curators.append('Strategy Gamers')

    # If no specific curators, return generic ones
    # (This will be flagged)
    if not curators:
        return [
            'Steam Curators',
            'PC Gaming Curators',
            'Game Recommendation Lists'
        ]

    return curators[:10]


def generate_community_report(analysis: CommunityAnalysis, game_name: str) -> str:
    """
    Generate markdown report for community reach analysis.

    Args:
        analysis: CommunityAnalysis results
        game_name: Name of the game

    Returns:
        Markdown formatted report
    """
    md = f"## Community Reach Analysis for {game_name}\n\n"

    # Overall score
    md += f"**Overall Community Score**: {analysis.overall_score}/100\n\n"

    # Subreddit section
    md += "### Subreddit Recommendations\n\n"
    md += f"**Score**: {analysis.subreddit_score}/100\n"
    md += f"**Quality**: {analysis.value_labels.get('subreddits', 'Unknown')}\n\n"

    if analysis.subreddit_recommendations:
        md += "**Recommended Subreddits**:\n"
        for sub in analysis.subreddit_recommendations:
            md += f"- {sub}\n"
        md += "\n"

    # Influencer section
    md += "### Influencer Recommendations\n\n"
    md += f"**Score**: {analysis.influencer_score}/100\n"
    md += f"**Quality**: {analysis.value_labels.get('influencers', 'Unknown')}\n\n"

    if analysis.influencer_recommendations:
        md += "**Recommended Influencers**:\n"
        for inf in analysis.influencer_recommendations:
            md += f"- {inf}\n"
        md += "\n"

    # Curator section
    md += "### Steam Curator Recommendations\n\n"
    md += f"**Score**: {analysis.curator_score}/100\n"
    md += f"**Quality**: {analysis.value_labels.get('curators', 'Unknown')}\n\n"

    if analysis.curator_recommendations:
        md += "**Recommended Curators**:\n"
        for cur in analysis.curator_recommendations:
            md += f"- {cur}\n"
        md += "\n"

    # Warnings section
    if analysis.warnings:
        md += "---\n\n"
        md += "### ⚠️ Data Quality Warnings\n\n"
        for warning in analysis.warnings:
            md += warning + "\n\n"

    # Improvements section
    if analysis.improvements:
        md += "---\n\n"
        md += "### 💡 How to Improve\n\n"
        for improvement in analysis.improvements:
            md += improvement + "\n\n"

    return md


# Test the system
if __name__ == "__main__":
    print("="*80)
    print("COMMUNITY ANALYZER TEST")
    print("="*80 + "\n")

    # Test 1: Generic recommendations (should be flagged)
    print("TEST 1: Generic Subreddit List\n")
    game_data_generic = {
        'name': 'Generic Game',
        'genres': ['Indie', 'Action'],
        'tags': []
    }

    generic_subreddits = ['r/gaming', 'r/pcgaming', 'r/indiegaming', 'r/gamedev']

    analysis1 = analyze_community_reach(
        game_data_generic,
        subreddit_list=generic_subreddits
    )

    print(f"Overall Score: {analysis1.overall_score}/100")
    print(f"Subreddit Score: {analysis1.subreddit_score}/100")
    print(f"Warnings: {len(analysis1.warnings)}")
    if analysis1.warnings:
        print("\nWarning Preview:")
        print(analysis1.warnings[0][:200] + "...")

    # Test 2: Specific recommendations (should pass)
    print("\n" + "="*80)
    print("TEST 2: Specific Subreddit List\n")

    game_data_specific = {
        'name': 'Roguelike Metroidvania',
        'genres': ['Roguelike', 'Metroidvania'],
        'tags': ['Pixel Graphics']
    }

    # Auto-generate specific recommendations
    analysis2 = analyze_community_reach(game_data_specific)

    print(f"Overall Score: {analysis2.overall_score}/100")
    print(f"Subreddit Score: {analysis2.subreddit_score}/100")
    print(f"Generated Subreddits: {analysis2.subreddit_recommendations}")
    print(f"Warnings: {len(analysis2.warnings)}")

    # Generate full report
    print("\n" + "="*80)
    print("FULL REPORT EXAMPLE\n")
    report = generate_community_report(analysis2, game_data_specific['name'])
    print(report[:500] + "...")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
