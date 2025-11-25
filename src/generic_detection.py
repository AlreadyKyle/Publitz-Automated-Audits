"""
Generic Data Detection System

Detects when "personalized" recommendations are actually just generic lists that
apply to every game. Reduces scores and adds warnings when data isn't game-specific.

PROBLEM: Report gives 85/100 for "Community" but lists r/gaming, r/pcgaming -
the same subreddits EVERY game gets. This isn't personalized value.

SOLUTION: Detect generic patterns and penalize scores accordingly.
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# GENERIC PATTERN DEFINITIONS
# ============================================================================

# Generic subreddits that apply to EVERY game
GENERIC_SUBREDDITS = {
    'r/gaming',
    'r/pcgaming',
    'r/indiegaming',
    'r/gamedev',
    'r/games',
    'r/truegaming',
    'r/patientgamers',
    'r/rpg_gamers',
    'r/gamingsuggestions',
    'r/shouldibuythisgame',
    'r/playitforward',
    'r/lowendgaming',
    'r/linux_gaming',
    'r/steam',
    'r/steamdeals'
}

# Generic influencer indicators (phrases that signal non-specific recommendations)
GENERIC_INFLUENCER_INDICATORS = {
    'generic action channels',
    'broad gaming coverage',
    'covers multiple genres',
    'variety gaming content',
    'general gaming channel',
    'popular gaming YouTuber',
    'mainstream gaming coverage',
    'all types of games',
    'general audience',
    'broad appeal'
}

# Generic curator names/patterns
GENERIC_CURATOR_PATTERNS = {
    'Action Aficionado',
    'Shooter Specialists',
    'IndieGameReviewer',
    'Generic Indie Curator',
    'General Gaming Curator',
    'All Games Curator',
    'Popular Indie Games',
    'Must Play Indies',
    'Best Indie Games'
}

# Generic tags that apply to most games
GENERIC_TAGS = {
    'Action',
    'Adventure',
    'Indie',
    'Casual',
    'Singleplayer',
    'Multiplayer',
    'Great Soundtrack',
    'Atmospheric',
    'Story Rich'
}

# Thresholds for each category
THRESHOLDS = {
    'subreddits': {
        'generic_threshold': 0.6,  # >60% generic = not personalized
        'penalty_severe': 40,      # Penalty if >80% generic
        'penalty_moderate': 25,    # Penalty if >60% generic
        'penalty_minor': 10        # Penalty if >40% generic
    },
    'influencers': {
        'min_specific': 3,         # Need 3+ specific influencers
        'penalty_no_specific': 50, # No specific influencers
        'penalty_few_specific': 30 # <3 specific influencers
    },
    'curators': {
        'generic_threshold': 0.7,
        'penalty_severe': 40,
        'penalty_moderate': 20
    },
    'tags': {
        'generic_threshold': 0.5,
        'penalty': 15
    }
}


@dataclass
class DetectionResult:
    """Result of generic data detection"""
    is_generic: bool
    specificity_score: float  # 0-100, higher = more personalized
    reasoning: str
    penalty: int              # Score penalty to apply
    generic_count: int
    total_count: int
    specific_examples: List[str]
    improvements: str


def detect_generic_subreddits(subreddits: List[str]) -> DetectionResult:
    """
    Detect if subreddit list is generic or game-specific.

    Args:
        subreddits: List of subreddit names (with or without 'r/' prefix)

    Returns:
        DetectionResult with detection info and penalty

    Examples:
        >>> result = detect_generic_subreddits(['r/gaming', 'r/pcgaming', 'r/indiegaming'])
        >>> result.is_generic
        True
        >>> result.penalty
        40
    """

    if not subreddits:
        return DetectionResult(
            is_generic=True,
            specificity_score=0,
            reasoning="No subreddits provided",
            penalty=50,
            generic_count=0,
            total_count=0,
            specific_examples=[],
            improvements="Identify subreddits specific to your game's genre, theme, or mechanics"
        )

    # Normalize subreddit names (lowercase, ensure 'r/' prefix)
    normalized = []
    for sub in subreddits:
        sub_clean = sub.strip().lower()
        if not sub_clean.startswith('r/'):
            sub_clean = f'r/{sub_clean}'
        normalized.append(sub_clean)

    # Calculate overlap with generic list
    found_set = set(normalized)
    generic_set = GENERIC_SUBREDDITS
    overlap = found_set & generic_set

    overlap_ratio = len(overlap) / len(found_set) if found_set else 0
    specificity = (1 - overlap_ratio) * 100

    # Determine penalty based on overlap
    thresholds = THRESHOLDS['subreddits']
    if overlap_ratio > 0.8:
        penalty = thresholds['penalty_severe']
        is_generic = True
        level = "severe"
    elif overlap_ratio > 0.6:
        penalty = thresholds['penalty_moderate']
        is_generic = True
        level = "moderate"
    elif overlap_ratio > 0.4:
        penalty = thresholds['penalty_minor']
        is_generic = True
        level = "minor"
    else:
        penalty = 0
        is_generic = False
        level = "good"

    # Identify specific (non-generic) examples
    specific_examples = list(found_set - generic_set)[:3]

    reasoning = f"{overlap_ratio*100:.0f}% of subreddits ({len(overlap)}/{len(found_set)}) are generic gaming communities"

    improvements = _generate_subreddit_improvements(found_set, generic_set, overlap_ratio)

    logger.info(f"Subreddit detection: {len(overlap)}/{len(found_set)} generic ({overlap_ratio*100:.0f}%), "
                f"penalty: {penalty}, specificity: {specificity:.0f}")

    return DetectionResult(
        is_generic=is_generic,
        specificity_score=specificity,
        reasoning=reasoning,
        penalty=penalty,
        generic_count=len(overlap),
        total_count=len(found_set),
        specific_examples=specific_examples,
        improvements=improvements
    )


def detect_generic_influencers(influencer_data: List[Dict[str, str]]) -> DetectionResult:
    """
    Detect if influencer recommendations are generic or game-specific.

    Args:
        influencer_data: List of dicts with 'name' and 'description' keys

    Returns:
        DetectionResult with detection info

    Examples:
        >>> data = [
        ...     {'name': 'GenericGamer', 'description': 'Covers all types of games'},
        ...     {'name': 'ActionFan', 'description': 'Focuses on roguelike shooters'}
        ... ]
        >>> result = detect_generic_influencers(data)
        >>> result.penalty
        30  # Has some specific but not enough
    """

    if not influencer_data:
        return DetectionResult(
            is_generic=True,
            specificity_score=0,
            reasoning="No influencers provided",
            penalty=50,
            generic_count=0,
            total_count=0,
            specific_examples=[],
            improvements="Research influencers who specifically cover your game's genre/niche"
        )

    generic_count = 0
    specific_count = 0
    specific_examples = []

    for influencer in influencer_data:
        desc = influencer.get('description', '').lower()

        # Check if description contains generic indicators
        is_generic_influencer = any(indicator in desc for indicator in GENERIC_INFLUENCER_INDICATORS)

        if is_generic_influencer:
            generic_count += 1
        else:
            specific_count += 1
            if len(specific_examples) < 3:
                specific_examples.append(influencer.get('name', 'Unknown'))

    total = len(influencer_data)
    specificity = (specific_count / total) * 100 if total > 0 else 0

    # Apply penalty based on specific influencers
    thresholds = THRESHOLDS['influencers']
    if specific_count == 0:
        penalty = thresholds['penalty_no_specific']
        is_generic = True
        reasoning = "No game-specific influencers identified - all are generic gaming channels"
    elif specific_count < thresholds['min_specific']:
        penalty = thresholds['penalty_few_specific']
        is_generic = True
        reasoning = f"Only {specific_count} game-specific influencer(s) - need at least {thresholds['min_specific']}"
    else:
        penalty = 0
        is_generic = False
        reasoning = f"{specific_count} game-specific influencers identified"

    improvements = _generate_influencer_improvements(specific_count, thresholds['min_specific'])

    logger.info(f"Influencer detection: {specific_count}/{total} specific, penalty: {penalty}")

    return DetectionResult(
        is_generic=is_generic,
        specificity_score=specificity,
        reasoning=reasoning,
        penalty=penalty,
        generic_count=generic_count,
        total_count=total,
        specific_examples=specific_examples,
        improvements=improvements
    )


def detect_generic_curators(curator_names: List[str]) -> DetectionResult:
    """
    Detect if Steam curator recommendations are generic or game-specific.

    Args:
        curator_names: List of curator names

    Returns:
        DetectionResult with detection info
    """

    if not curator_names:
        return DetectionResult(
            is_generic=True,
            specificity_score=0,
            reasoning="No curators provided",
            penalty=40,
            generic_count=0,
            total_count=0,
            specific_examples=[],
            improvements="Identify curators who focus on your game's specific genre or niche"
        )

    # Check for generic patterns
    generic_count = 0
    for curator in curator_names:
        curator_lower = curator.lower()
        if any(pattern.lower() in curator_lower for pattern in GENERIC_CURATOR_PATTERNS):
            generic_count += 1

    total = len(curator_names)
    overlap_ratio = generic_count / total if total > 0 else 0
    specificity = (1 - overlap_ratio) * 100

    thresholds = THRESHOLDS['curators']
    if overlap_ratio > thresholds['generic_threshold']:
        penalty = thresholds['penalty_severe']
        is_generic = True
    elif overlap_ratio > 0.5:
        penalty = thresholds['penalty_moderate']
        is_generic = True
    else:
        penalty = 0
        is_generic = False

    specific_examples = [name for name in curator_names if not any(
        pattern.lower() in name.lower() for pattern in GENERIC_CURATOR_PATTERNS
    )][:3]

    reasoning = f"{overlap_ratio*100:.0f}% of curators ({generic_count}/{total}) have generic names"
    improvements = "Seek out curators who specialize in your game's specific subgenre or mechanics"

    return DetectionResult(
        is_generic=is_generic,
        specificity_score=specificity,
        reasoning=reasoning,
        penalty=penalty,
        generic_count=generic_count,
        total_count=total,
        specific_examples=specific_examples,
        improvements=improvements
    )


def detect_generic_tags(tags: List[str]) -> DetectionResult:
    """
    Detect if Steam tags are generic or specific.

    Args:
        tags: List of Steam tags

    Returns:
        DetectionResult with detection info
    """

    if not tags:
        return DetectionResult(
            is_generic=True,
            specificity_score=0,
            reasoning="No tags provided",
            penalty=20,
            generic_count=0,
            total_count=0,
            specific_examples=[],
            improvements="Add more specific tags that describe your game's unique mechanics or theme"
        )

    # Normalize tags
    normalized = [tag.strip() for tag in tags]
    found_set = set(normalized)
    generic_set = GENERIC_TAGS

    overlap = found_set & generic_set
    overlap_ratio = len(overlap) / len(found_set) if found_set else 0
    specificity = (1 - overlap_ratio) * 100

    thresholds = THRESHOLDS['tags']
    if overlap_ratio > thresholds['generic_threshold']:
        penalty = thresholds['penalty']
        is_generic = True
    else:
        penalty = 0
        is_generic = False

    specific_examples = list(found_set - generic_set)[:3]

    reasoning = f"{overlap_ratio*100:.0f}% of tags ({len(overlap)}/{len(found_set)}) are generic"
    improvements = "Add niche-specific tags like game mechanics, themes, or subgenres"

    return DetectionResult(
        is_generic=is_generic,
        specificity_score=specificity,
        reasoning=reasoning,
        penalty=penalty,
        generic_count=len(overlap),
        total_count=len(found_set),
        specific_examples=specific_examples,
        improvements=improvements
    )


def adjust_score_for_generic_data(
    section_score: int,
    section_name: str,
    detection_result: DetectionResult
) -> Dict[str, Any]:
    """
    Adjust section score based on generic data detection.

    Args:
        section_score: Original calculated score (0-100)
        section_name: Name of section (e.g., "Community Reach")
        detection_result: Result from detection function

    Returns:
        Dict with adjusted score and explanation

    Examples:
        >>> result = detect_generic_subreddits(['r/gaming', 'r/pcgaming'])
        >>> adjusted = adjust_score_for_generic_data(85, "Community Reach", result)
        >>> adjusted['adjusted_score']
        45  # 85 - 40 penalty
        >>> adjusted['was_adjusted']
        True
    """

    if not detection_result.is_generic:
        # No penalty needed
        return {
            'raw_score': section_score,
            'adjusted_score': section_score,
            'was_adjusted': False,
            'penalty_applied': 0,
            'is_personalized': True,
            'specificity': detection_result.specificity_score,
            'value_label': "✅ Personalized - Game-specific recommendations",
            'warning': None,
            'improvements': None
        }

    # Apply penalty
    adjusted_score = max(section_score - detection_result.penalty, 0)

    warning = _generate_adjustment_warning(
        section_name,
        section_score,
        adjusted_score,
        detection_result
    )

    logger.warning(f"{section_name} score adjusted: {section_score} → {adjusted_score} "
                   f"(generic data penalty: {detection_result.penalty})")

    return {
        'raw_score': section_score,
        'adjusted_score': adjusted_score,
        'was_adjusted': True,
        'penalty_applied': detection_result.penalty,
        'is_personalized': False,
        'specificity': detection_result.specificity_score,
        'value_label': "⚠️  Generic - These recommendations apply to most games",
        'warning': warning,
        'improvements': detection_result.improvements
    }


def _generate_adjustment_warning(
    section_name: str,
    raw_score: int,
    adjusted_score: int,
    detection: DetectionResult
) -> str:
    """Generate warning message for score adjustment"""

    warning = f"""⚠️  {section_name.upper()} SCORE ADJUSTED FOR GENERIC DATA

**Score Change:** {raw_score}/100 → {adjusted_score}/100 (-{detection.penalty} points)

**Why Reduced:**
{detection.reasoning}

This section listed {detection.generic_count}/{detection.total_count} generic recommendations that apply to EVERY game, not specifically to yours.

**The Problem:**
Generic recommendations provide no real value - you could find these yourself in 30 seconds on Google.
Personalized, game-specific recommendations are what you need.

**How To Improve:**
{detection.improvements}
"""

    if detection.specific_examples:
        warning += f"\n**Good Examples Found:**\n"
        for example in detection.specific_examples:
            warning += f"- {example}\n"
        warning += "\nMore recommendations like these would improve your score."

    return warning


def _generate_subreddit_improvements(found: Set[str], generic: Set[str], overlap_ratio: float) -> str:
    """Generate specific improvements for subreddit recommendations"""

    if overlap_ratio > 0.8:
        return """**To Get Game-Specific Subreddits:**

1. **Identify your game's niche:** What makes your game unique?
   - Mechanics: e.g., r/roguelike, r/metroidvania, r/soulslikes
   - Theme: e.g., r/cyberpunk, r/fantasy, r/horror
   - Style: e.g., r/pixelart, r/lowpoly, r/visualnovel

2. **Search for similar games:** Find games like yours, check where they're discussed

3. **Look beyond "gaming":** Check hobby subreddits related to your theme
   - Space game? Try r/space, r/spacesim
   - Historical? Try r/history, r/medievalhistory
   - Music-based? Try r/electronicmusic, r/chiptunes

4. **Check game-specific subs:** Many popular games have their own communities

Generic subreddits like r/gaming get 1000+ posts per day. Your announcement will be buried.
Niche subreddits get 10-20 posts per day. Your announcement will be seen."""

    elif overlap_ratio > 0.5:
        specific = list(found - generic)[:2]
        return f"""**Good Start, But Needs More Specificity:**

You found some good niche subreddits{f": {', '.join(specific)}" if specific else ""}.
Add 3-5 more subreddits that are even MORE specific to your game's unique features.

Example: If your game is a "roguelike deckbuilder with pixel art":
- r/roguelike ✅ (good niche)
- r/pixelart ✅ (good niche)
- r/gaming ❌ (too generic, everyone goes here)"""

    else:
        return "Continue focusing on niche-specific communities over broad gaming subreddits."


def _generate_influencer_improvements(specific_count: int, min_needed: int) -> str:
    """Generate specific improvements for influencer recommendations"""

    if specific_count == 0:
        return """**To Find Game-Specific Influencers:**

1. **Search YouTube/Twitch for your genre:**
   - "[your genre] lets play"
   - "[similar game name] gameplay"
   - "[game mechanic] games"

2. **Look for mid-tier creators (10K-100K subs):**
   - More likely to cover indie games
   - More engaged audiences
   - Actually respond to emails

3. **Check who covered similar games:**
   - Find games like yours on Steam
   - Check their announcement/review threads
   - See which YouTubers/streamers covered them

4. **Avoid mega-channels (1M+ subs):**
   - They rarely cover small indies
   - Expensive or impossible to reach
   - Generic recommendations don't help

**Example:**
Bad: "PewDiePie" (covers everything, won't cover your game)
Good: "RetroMMMO" (covers only roguelike games, perfect fit)"""

    elif specific_count < min_needed:
        return f"""**You found {specific_count} game-specific influencer(s). Need {min_needed}+ for full score.**

Focus on finding influencers who:
- Specialize in your exact subgenre
- Have covered similar games recently
- Have engaged communities (not just subscriber count)
- Actually respond to indie game pitches

Quality > Quantity. 5 perfectly-matched 50K-sub channels beat 20 generic mega-channels."""

    else:
        return "Good work identifying game-specific influencers. Continue this focused approach."


# ============================================================================
# COMPREHENSIVE DETECTION
# ============================================================================

def detect_all_generic_patterns(data: Dict[str, Any]) -> Dict[str, DetectionResult]:
    """
    Run generic detection on all applicable data categories.

    Args:
        data: Dict containing various recommendation data

    Returns:
        Dict mapping category names to DetectionResults

    Example:
        >>> data = {
        ...     'subreddits': ['r/gaming', 'r/pcgaming'],
        ...     'influencers': [...],
        ...     'curators': [...],
        ...     'tags': [...]
        ... }
        >>> results = detect_all_generic_patterns(data)
        >>> results['subreddits'].is_generic
        True
    """

    results = {}

    # Detect subreddits
    if 'subreddits' in data:
        results['subreddits'] = detect_generic_subreddits(data['subreddits'])

    # Detect influencers
    if 'influencers' in data:
        results['influencers'] = detect_generic_influencers(data['influencers'])

    # Detect curators
    if 'curators' in data:
        results['curators'] = detect_generic_curators(data['curators'])

    # Detect tags
    if 'tags' in data:
        results['tags'] = detect_generic_tags(data['tags'])

    return results


# ============================================================================
# TESTING
# ============================================================================

def test_generic_detection():
    """Test generic detection with example data"""

    print("\n" + "="*80)
    print("GENERIC DATA DETECTION TEST")
    print("="*80 + "\n")

    # Test 1: Generic subreddits (like Retrace the Light would get)
    print("TEST 1: Generic Subreddits")
    print("-" * 80)

    subreddits_generic = ['r/gaming', 'r/pcgaming', 'r/gamedev', 'r/rpg_gamers', 'r/indiegaming']
    print(f"Input: {subreddits_generic}")
    print()

    result = detect_generic_subreddits(subreddits_generic)
    print(f"Is Generic: {result.is_generic}")
    print(f"Specificity Score: {result.specificity_score:.0f}/100")
    print(f"Reasoning: {result.reasoning}")
    print(f"Penalty: {result.penalty} points")
    print(f"Generic Count: {result.generic_count}/{result.total_count}")
    print()

    # Apply to score
    raw_score = 85
    adjusted = adjust_score_for_generic_data(raw_score, "Community Reach", result)
    print(f"Score Adjustment:")
    print(f"  Raw Score: {adjusted['raw_score']}/100")
    print(f"  Adjusted Score: {adjusted['adjusted_score']}/100")
    print(f"  Was Adjusted: {adjusted['was_adjusted']}")
    print(f"  Value Label: {adjusted['value_label']}")
    print()

    if adjusted['warning']:
        print("Warning Generated:")
        print(adjusted['warning'])
    print()

    # Test 2: Mix of generic and specific
    print("\nTEST 2: Mixed Subreddits (Some Specific)")
    print("-" * 80)

    subreddits_mixed = ['r/gaming', 'r/metroidvania', 'r/indiedev', 'r/pixelart', 'r/indiegaming']
    print(f"Input: {subreddits_mixed}")
    print()

    result2 = detect_generic_subreddits(subreddits_mixed)
    print(f"Is Generic: {result2.is_generic}")
    print(f"Specificity Score: {result2.specificity_score:.0f}/100")
    print(f"Reasoning: {result2.reasoning}")
    print(f"Penalty: {result2.penalty} points")
    print(f"Specific Examples: {result2.specific_examples}")
    print()

    adjusted2 = adjust_score_for_generic_data(85, "Community Reach", result2)
    print(f"Score: {adjusted2['raw_score']}/100 → {adjusted2['adjusted_score']}/100")
    print(f"Value Label: {adjusted2['value_label']}")
    print()

    # Test 3: Highly specific
    print("\nTEST 3: Specific Subreddits (Good)")
    print("-" * 80)

    subreddits_specific = ['r/metroidvania', 'r/roguelike', 'r/pixelart', 'r/2dgaming', 'r/indiedev']
    print(f"Input: {subreddits_specific}")
    print()

    result3 = detect_generic_subreddits(subreddits_specific)
    print(f"Is Generic: {result3.is_generic}")
    print(f"Specificity Score: {result3.specificity_score:.0f}/100")
    print(f"Reasoning: {result3.reasoning}")
    print(f"Penalty: {result3.penalty} points")
    print()

    adjusted3 = adjust_score_for_generic_data(85, "Community Reach", result3)
    print(f"Score: {adjusted3['raw_score']}/100 → {adjusted3['adjusted_score']}/100")
    print(f"Value Label: {adjusted3['value_label']}")
    print()

    print("="*80)
    print("VERIFICATION")
    print("="*80)
    print(f"✅ Generic subreddits detected: {result.is_generic}")
    print(f"✅ Severe penalty applied: {result.penalty == 40}")
    print(f"✅ Score reduced: 85 → {adjusted['adjusted_score']}")
    print(f"✅ Warning generated: {adjusted['warning'] is not None}")
    print(f"✅ Mixed case penalty lower: {result2.penalty < result.penalty}")
    print(f"✅ Specific case no penalty: {result3.penalty == 0}")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_generic_detection()
