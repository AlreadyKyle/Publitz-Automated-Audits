"""
Manual Game Data Entry System

Since Steam/SteamSpy APIs are blocked, this allows users to manually
provide game data for report generation.
"""

from typing import Dict, Any, Optional, List
import json
import os


def validate_game_data(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate that game data has all required fields.

    Args:
        data: Game data dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Required fields
    required_fields = {
        'app_id': str,
        'name': str,
        'price': (int, float),
        'review_score': (int, float),
        'review_count': int,
        'owners': int,
        'revenue': int,
        'genres': list,
        'release_date': str
    }

    for field, expected_type in required_fields.items():
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(data[field], expected_type):
            errors.append(f"Field '{field}' should be {expected_type}, got {type(data[field])}")

    # Validation rules
    if 'review_score' in data:
        if not 0 <= data['review_score'] <= 100:
            errors.append("review_score must be between 0 and 100")

    if 'price' in data:
        if data['price'] < 0:
            errors.append("price cannot be negative")

    if 'review_count' in data:
        if data['review_count'] < 0:
            errors.append("review_count cannot be negative")

    if 'owners' in data:
        if data['owners'] < 0:
            errors.append("owners cannot be negative")

    if 'revenue' in data:
        if data['revenue'] < 0:
            errors.append("revenue cannot be negative")

    return len(errors) == 0, errors


def prompt_for_game_data_interactive() -> Dict[str, Any]:
    """
    Interactive prompt for manual game data entry.

    Returns:
        Game data dictionary
    """
    print("\n" + "="*60)
    print("MANUAL GAME DATA ENTRY")
    print("="*60)
    print("\nPlease provide the following information about your game.")
    print("You can find this data on your Steam dashboard or the Steam store page.\n")

    game_data = {}

    # App ID
    while True:
        app_id = input("Steam App ID (e.g., 1145350): ").strip()
        if app_id:
            game_data['app_id'] = app_id
            break
        print("⚠️  App ID is required")

    # Name
    while True:
        name = input("Game Name: ").strip()
        if name:
            game_data['name'] = name
            break
        print("⚠️  Game name is required")

    # Price
    while True:
        try:
            price = input("Price in USD (e.g., 29.99, or 0 for free): ").strip()
            price_val = float(price)
            if price_val >= 0:
                game_data['price'] = price_val
                break
            print("⚠️  Price cannot be negative")
        except ValueError:
            print("⚠️  Please enter a valid number")

    # Review Score
    while True:
        try:
            review_score = input("Review Score % (0-100, e.g., 85.5): ").strip()
            score_val = float(review_score)
            if 0 <= score_val <= 100:
                game_data['review_score'] = score_val
                break
            print("⚠️  Review score must be between 0 and 100")
        except ValueError:
            print("⚠️  Please enter a valid number")

    # Review Count
    while True:
        try:
            review_count = input("Total Review Count (e.g., 5000): ").strip()
            count_val = int(review_count)
            if count_val >= 0:
                game_data['review_count'] = count_val
                break
            print("⚠️  Review count cannot be negative")
        except ValueError:
            print("⚠️  Please enter a valid integer")

    # Owners
    while True:
        try:
            owners = input("Estimated Owners (e.g., 100000): ").strip()
            owners_val = int(owners)
            if owners_val >= 0:
                game_data['owners'] = owners_val
                break
            print("⚠️  Owners cannot be negative")
        except ValueError:
            print("⚠️  Please enter a valid integer")

    # Revenue
    while True:
        try:
            revenue = input("Estimated Revenue in USD (e.g., 500000): ").strip()
            revenue_val = int(revenue)
            if revenue_val >= 0:
                game_data['revenue'] = revenue_val
                break
            print("⚠️  Revenue cannot be negative")
        except ValueError:
            print("⚠️  Please enter a valid integer")

    # Genres
    genres_input = input("Genres (comma-separated, e.g., Action, RPG, Indie): ").strip()
    game_data['genres'] = [g.strip() for g in genres_input.split(',') if g.strip()]

    # Release Date
    release_date = input("Release Date (YYYY-MM-DD, e.g., 2024-01-15): ").strip()
    game_data['release_date'] = release_date if release_date else "Unknown"

    # Optional fields
    print("\n--- Optional Fields (press Enter to skip) ---")

    developer = input("Developer: ").strip()
    if developer:
        game_data['developer'] = developer

    tags_input = input("Tags (comma-separated): ").strip()
    if tags_input:
        game_data['tags'] = [t.strip() for t in tags_input.split(',') if t.strip()]

    velocity = input("Review Velocity Trend (increasing/stable/declining): ").strip().lower()
    game_data['review_velocity_trend'] = velocity if velocity in ['increasing', 'stable', 'declining'] else 'stable'

    # Validate
    is_valid, errors = validate_game_data(game_data)

    if not is_valid:
        print("\n⚠️  Validation errors:")
        for error in errors:
            print(f"   - {error}")
        print("\nPlease fix these errors and try again.")
        return None

    print("\n✅ Game data collected successfully!")
    return game_data


def create_game_data_dict(
    app_id: str,
    name: str,
    price: float,
    review_score: float,
    review_count: int,
    owners: int,
    revenue: int,
    genres: List[str],
    release_date: str,
    developer: Optional[str] = None,
    tags: Optional[List[str]] = None,
    review_velocity_trend: str = 'stable'
) -> Dict[str, Any]:
    """
    Create a validated game data dictionary programmatically.

    Args:
        app_id: Steam App ID
        name: Game name
        price: Price in USD
        review_score: Review score percentage (0-100)
        review_count: Total number of reviews
        owners: Estimated number of owners
        revenue: Estimated revenue in USD
        genres: List of genre strings
        release_date: Release date (YYYY-MM-DD format)
        developer: Developer name (optional)
        tags: List of tag strings (optional)
        review_velocity_trend: One of 'increasing', 'stable', 'declining'

    Returns:
        Validated game data dictionary

    Raises:
        ValueError: If validation fails
    """
    game_data = {
        'app_id': str(app_id),
        'name': name,
        'price': float(price),
        'review_score': float(review_score),
        'review_count': int(review_count),
        'owners': int(owners),
        'revenue': int(revenue),
        'genres': genres,
        'release_date': release_date,
        'review_velocity_trend': review_velocity_trend
    }

    if developer:
        game_data['developer'] = developer
    if tags:
        game_data['tags'] = tags

    is_valid, errors = validate_game_data(game_data)

    if not is_valid:
        raise ValueError(f"Validation errors: {', '.join(errors)}")

    return game_data


def save_game_data_to_file(game_data: Dict[str, Any], filename: Optional[str] = None) -> str:
    """
    Save game data to a JSON file.

    Args:
        game_data: Game data dictionary
        filename: Output filename (optional, auto-generated if not provided)

    Returns:
        Path to saved file
    """
    if filename is None:
        # Auto-generate filename from game name
        safe_name = game_data['name'].lower().replace(' ', '_').replace("'", "")
        filename = f"game_data_{safe_name}.json"

    filepath = os.path.join('game_data', filename)

    # Create directory if it doesn't exist
    os.makedirs('game_data', exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump(game_data, f, indent=2)

    return filepath


def load_game_data_from_file(filepath: str) -> Dict[str, Any]:
    """
    Load game data from a JSON file.

    Args:
        filepath: Path to JSON file

    Returns:
        Game data dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If data is invalid
    """
    with open(filepath, 'r') as f:
        game_data = json.load(f)

    is_valid, errors = validate_game_data(game_data)

    if not is_valid:
        raise ValueError(f"Invalid game data in file: {', '.join(errors)}")

    return game_data


def print_game_data_summary(game_data: Dict[str, Any]) -> None:
    """Print a summary of the entered game data."""
    print("\n" + "="*60)
    print("GAME DATA SUMMARY")
    print("="*60)
    print(f"App ID: {game_data['app_id']}")
    print(f"Name: {game_data['name']}")
    print(f"Price: ${game_data['price']:.2f}")
    print(f"Review Score: {game_data['review_score']:.1f}%")
    print(f"Review Count: {game_data['review_count']:,}")
    print(f"Owners: {game_data['owners']:,}")
    print(f"Revenue: ${game_data['revenue']:,}")
    print(f"Genres: {', '.join(game_data['genres'])}")
    print(f"Release Date: {game_data['release_date']}")
    print(f"Review Trend: {game_data.get('review_velocity_trend', 'stable')}")
    if 'developer' in game_data:
        print(f"Developer: {game_data['developer']}")
    print("="*60 + "\n")


def quick_entry_from_steam_data(
    steam_url_or_appid: str,
    review_score: float,
    review_count: int,
    owners: int
) -> Dict[str, Any]:
    """
    Quick entry method - minimal input required.

    Users provide just the critical data that's hard to estimate.
    The system will prompt for or estimate the rest.

    Args:
        steam_url_or_appid: Steam URL or App ID
        review_score: Review score % (0-100)
        review_count: Total reviews
        owners: Estimated owners

    Returns:
        Game data dictionary with estimates for other fields
    """
    # Extract app ID from URL if needed
    if 'steampowered.com' in steam_url_or_appid:
        import re
        match = re.search(r'/app/(\d+)', steam_url_or_appid)
        if match:
            app_id = match.group(1)
        else:
            raise ValueError("Could not extract App ID from URL")
    else:
        app_id = steam_url_or_appid

    print(f"\nQuick Entry Mode for App ID: {app_id}")
    print("Please provide just the essential information:\n")

    name = input("Game Name: ").strip()
    if not name:
        raise ValueError("Game name is required")

    price_str = input("Price ($): ").strip()
    price = float(price_str) if price_str else 19.99

    # Estimate revenue (simple model: owners * price * 0.7 average discount)
    estimated_revenue = int(owners * price * 0.7)

    genres_str = input("Main Genre (e.g., Action, RPG): ").strip()
    genres = [genres_str] if genres_str else ['Indie']

    release_str = input("Release Date (YYYY-MM-DD, or press Enter to skip): ").strip()
    release_date = release_str if release_str else "2024-01-01"

    game_data = create_game_data_dict(
        app_id=app_id,
        name=name,
        price=price,
        review_score=review_score,
        review_count=review_count,
        owners=owners,
        revenue=estimated_revenue,
        genres=genres,
        release_date=release_date,
        review_velocity_trend='stable'
    )

    print(f"\n✅ Quick entry complete! Estimated revenue: ${estimated_revenue:,}")
    return game_data


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MANUAL DATA ENTRY EXAMPLES")
    print("="*60)

    print("\n1. Interactive Entry (Full Prompts)")
    print("-" * 60)
    print("from src.manual_data_entry import prompt_for_game_data_interactive")
    print("game = prompt_for_game_data_interactive()")
    print()

    print("\n2. Programmatic Entry (Direct Function Call)")
    print("-" * 60)
    print("""from src.manual_data_entry import create_game_data_dict

game = create_game_data_dict(
    app_id='1145350',
    name='My Game',
    price=29.99,
    review_score=85.0,
    review_count=5000,
    owners=100000,
    revenue=1500000,
    genres=['Action', 'RPG'],
    release_date='2024-01-15'
)""")

    print("\n3. Quick Entry (Minimal Input)")
    print("-" * 60)
    print("""from src.manual_data_entry import quick_entry_from_steam_data

game = quick_entry_from_steam_data(
    steam_url_or_appid='1145350',
    review_score=85.0,
    review_count=5000,
    owners=100000
)""")

    print("\n4. Generate Report")
    print("-" * 60)
    print("""from src.report_orchestrator import ReportOrchestrator

orchestrator = ReportOrchestrator(hourly_rate=50.0)
reports = orchestrator.generate_complete_report(game)

print(reports['tier_1_executive'])  # 2-3 page brief
print(reports['tier_2_strategic'])  # 8-12 page overview
print(reports['tier_3_deepdive'])   # 30-40 page analysis
""")
