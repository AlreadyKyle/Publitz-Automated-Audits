"""
Mock Game Data - Realistic examples for testing and demos

Since Steam/SteamSpy APIs are blocked, this provides realistic
game data across all performance tiers for testing the system.
"""

from typing import Dict, Any, List


# Tier 4: Exceptional Performance (85-100 score)
HADES_II = {
    'app_id': '1145350',
    'name': 'Hades II',
    'price': 29.99,
    'review_score': 96.5,  # % positive
    'review_count': 50285,
    'owners': 3350000,
    'revenue': 38500000,
    'genres': ['Action', 'Roguelike', 'Indie'],
    'release_date': '2024-05-06',
    'review_velocity_trend': 'stable',
    'developer': 'Supergiant Games',
    'tags': ['Roguelike', 'Action', 'Indie', 'Early Access', 'Greek Mythology']
}

STARDEW_VALLEY = {
    'app_id': '413150',
    'name': 'Stardew Valley',
    'price': 14.99,
    'review_score': 98.2,
    'review_count': 587000,
    'owners': 20000000,
    'revenue': 85000000,
    'genres': ['Simulation', 'RPG', 'Indie'],
    'release_date': '2016-02-26',
    'review_velocity_trend': 'increasing',
    'developer': 'ConcernedApe',
    'tags': ['Farming Sim', 'Indie', 'Pixel Graphics', 'Relaxing', 'Multiplayer']
}

# Tier 3: Solid Performance (66-80 score)
INDIE_SUCCESS = {
    'app_id': '888888',
    'name': 'Example Indie Success',
    'price': 19.99,
    'review_score': 82.0,
    'review_count': 3500,
    'owners': 85000,
    'revenue': 520000,
    'genres': ['Adventure', 'Puzzle', 'Indie'],
    'release_date': '2023-03-15',
    'review_velocity_trend': 'increasing',
    'developer': 'Small Studio Games',
    'tags': ['Puzzle', 'Adventure', 'Indie', 'Atmospheric', 'Story Rich']
}

STRATEGY_GAME = {
    'app_id': '777777',
    'name': 'Tactical Commander',
    'price': 24.99,
    'review_score': 75.5,
    'review_count': 1850,
    'owners': 42000,
    'revenue': 380000,
    'genres': ['Strategy', 'Simulation'],
    'release_date': '2023-09-20',
    'review_velocity_trend': 'stable',
    'developer': 'Strategy Masters',
    'tags': ['Strategy', 'Turn-Based', 'Tactical', 'Singleplayer', 'Difficult']
}

# Tier 2: Struggling Performance (41-65 score)
STRUGGLING_GAME = {
    'app_id': '666666',
    'name': 'Troubled Launch',
    'price': 29.99,
    'review_score': 58.0,
    'review_count': 850,
    'owners': 15000,
    'revenue': 125000,
    'genres': ['Action', 'Adventure'],
    'release_date': '2024-01-10',
    'review_velocity_trend': 'declining',
    'developer': 'Ambitious Devs',
    'tags': ['Action', 'Adventure', 'Third Person', 'Exploration', 'Open World']
}

MIXED_REVIEWS = {
    'app_id': '555555',
    'name': 'Divisive Mechanics',
    'price': 19.99,
    'review_score': 64.0,
    'review_count': 1200,
    'owners': 28000,
    'revenue': 185000,
    'genres': ['RPG', 'Action'],
    'release_date': '2023-11-05',
    'review_velocity_trend': 'stable',
    'developer': 'Experimental Studios',
    'tags': ['RPG', 'Action', 'Roguelite', 'Procedural Generation', 'Permadeath']
}

# Tier 1: Crisis Performance (0-40 score)
CRISIS_GAME = {
    'app_id': '444444',
    'name': 'Failed Experiment',
    'price': 24.99,
    'review_score': 35.0,
    'review_count': 450,
    'owners': 8500,
    'revenue': 45000,
    'genres': ['Action', 'Indie'],
    'release_date': '2023-08-15',
    'review_velocity_trend': 'declining',
    'developer': 'Struggling Studio',
    'tags': ['Action', 'Survival', 'Horror', 'Early Access', 'Multiplayer']
}

BROKEN_LAUNCH = {
    'app_id': '333333',
    'name': 'Technical Disaster',
    'price': 39.99,
    'review_score': 22.0,
    'review_count': 1850,
    'owners': 32000,
    'revenue': 280000,
    'genres': ['Action', 'Multiplayer'],
    'release_date': '2024-02-14',
    'review_velocity_trend': 'declining',
    'developer': 'Rushed Release Inc',
    'tags': ['Action', 'FPS', 'Multiplayer', 'Early Access', 'Online Co-Op']
}

# Early Access / Special Cases
EARLY_ACCESS = {
    'app_id': '222222',
    'name': 'Promising Early Access',
    'price': 19.99,
    'review_score': 78.0,
    'review_count': 2400,
    'owners': 55000,
    'revenue': 385000,
    'genres': ['Simulation', 'Strategy'],
    'release_date': '2024-04-01',
    'review_velocity_trend': 'increasing',
    'developer': 'Patient Developers',
    'tags': ['Early Access', 'Simulation', 'City Builder', 'Sandbox', 'Management']
}

FREE_TO_PLAY = {
    'app_id': '111111',
    'name': 'Free Multiplayer Game',
    'price': 0.00,
    'review_score': 71.0,
    'review_count': 125000,
    'owners': 5500000,
    'revenue': 2800000,  # From DLC/IAP
    'genres': ['Action', 'Free to Play'],
    'release_date': '2022-06-15',
    'review_velocity_trend': 'stable',
    'developer': 'F2P Studios',
    'tags': ['Free to Play', 'Multiplayer', 'Action', 'Team-Based', 'Competitive']
}


# Organized by tier for easy access
MOCK_GAMES_BY_TIER = {
    'exceptional': [HADES_II, STARDEW_VALLEY],
    'solid': [INDIE_SUCCESS, STRATEGY_GAME, EARLY_ACCESS],
    'struggling': [STRUGGLING_GAME, MIXED_REVIEWS],
    'crisis': [CRISIS_GAME, BROKEN_LAUNCH],
    'special': [FREE_TO_PLAY]
}

# All games in a list
ALL_MOCK_GAMES = [
    HADES_II,
    STARDEW_VALLEY,
    INDIE_SUCCESS,
    STRATEGY_GAME,
    STRUGGLING_GAME,
    MIXED_REVIEWS,
    CRISIS_GAME,
    BROKEN_LAUNCH,
    EARLY_ACCESS,
    FREE_TO_PLAY
]

# Games by name for easy lookup
MOCK_GAMES_BY_NAME = {
    'hades_ii': HADES_II,
    'stardew_valley': STARDEW_VALLEY,
    'indie_success': INDIE_SUCCESS,
    'strategy_game': STRATEGY_GAME,
    'struggling_game': STRUGGLING_GAME,
    'mixed_reviews': MIXED_REVIEWS,
    'crisis_game': CRISIS_GAME,
    'broken_launch': BROKEN_LAUNCH,
    'early_access': EARLY_ACCESS,
    'free_to_play': FREE_TO_PLAY
}


def get_mock_game(identifier: str = 'hades_ii') -> Dict[str, Any]:
    """
    Get a mock game by name.

    Args:
        identifier: Game identifier (e.g., 'hades_ii', 'struggling_game')

    Returns:
        Game data dictionary
    """
    return MOCK_GAMES_BY_NAME.get(identifier.lower(), HADES_II)


def get_games_by_tier(tier: str) -> List[Dict[str, Any]]:
    """
    Get all mock games in a specific tier.

    Args:
        tier: One of 'exceptional', 'solid', 'struggling', 'crisis', 'special'

    Returns:
        List of game data dictionaries
    """
    return MOCK_GAMES_BY_TIER.get(tier.lower(), [])


def list_available_games() -> List[str]:
    """Get list of available mock game identifiers."""
    return list(MOCK_GAMES_BY_NAME.keys())


def print_game_summary(game: Dict[str, Any]) -> None:
    """Print a summary of a game's data."""
    print(f"\n{'='*60}")
    print(f"Game: {game['name']}")
    print(f"{'='*60}")
    print(f"App ID: {game['app_id']}")
    print(f"Price: ${game['price']:.2f}")
    print(f"Review Score: {game['review_score']:.1f}% ({game['review_count']:,} reviews)")
    print(f"Owners: {game['owners']:,}")
    print(f"Revenue: ${game['revenue']:,}")
    print(f"Genres: {', '.join(game['genres'])}")
    print(f"Release: {game['release_date']}")
    print(f"Trend: {game['review_velocity_trend']}")
    print(f"Developer: {game['developer']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("AVAILABLE MOCK GAMES")
    print("="*60 + "\n")

    for tier, games in MOCK_GAMES_BY_TIER.items():
        print(f"\n{tier.upper()} TIER:")
        for game in games:
            print(f"  - {game['name']} ({game['review_score']:.1f}% reviews)")

    print("\n" + "="*60)
    print("EXAMPLE: Hades II")
    print("="*60)
    print_game_summary(HADES_II)

    print("\n" + "="*60)
    print("USAGE EXAMPLES")
    print("="*60)
    print("""
# Get a specific game
from src.mock_game_data import get_mock_game
game = get_mock_game('hades_ii')

# Get all games in a tier
from src.mock_game_data import get_games_by_tier
struggling = get_games_by_tier('struggling')

# List all available games
from src.mock_game_data import list_available_games
games = list_available_games()

# Generate report with mock data
from src.report_orchestrator import ReportOrchestrator
orchestrator = ReportOrchestrator(hourly_rate=50.0)
reports = orchestrator.generate_complete_report(game)
    """)
