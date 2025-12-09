"""
Input Processor - Parse and validate the 4 required inputs
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ClientInputs:
    """Validated client inputs"""
    steam_url: str
    app_id: str
    competitors: List[str]
    intake_form: Dict[str, Any]
    strategy_notes: str


class InputProcessor:
    """Process and validate client inputs"""

    @staticmethod
    def extract_app_id(steam_url: str) -> Optional[str]:
        """
        Extract Steam app ID from URL.

        Examples:
            https://store.steampowered.com/app/12345/Game_Name/ → '12345'
            https://store.steampowered.com/app/570/ → '570'
        """
        pattern = r'/app/(\d+)'
        match = re.search(pattern, steam_url)
        return match.group(1) if match else None

    @staticmethod
    def load_inputs_from_directory(client_dir: Path) -> ClientInputs:
        """
        Load all 4 inputs from a client directory.

        Expected structure:
            client_dir/
                steam_url.txt         - Single line with Steam URL
                competitors.txt       - One competitor per line
                intake_form.json      - JSON with client data
                strategy_notes.txt    - Freeform text notes
        """
        print(f"\n📂 Loading inputs from: {client_dir}")

        # 1. Load Steam URL
        steam_url_file = client_dir / "steam_url.txt"
        if not steam_url_file.exists():
            raise FileNotFoundError(f"Missing: {steam_url_file}")

        steam_url = steam_url_file.read_text().strip()
        app_id = InputProcessor.extract_app_id(steam_url)

        if not app_id:
            raise ValueError(f"Invalid Steam URL: {steam_url}")

        print(f"✅ Steam URL: {steam_url} (App ID: {app_id})")

        # 2. Load Competitors
        competitors_file = client_dir / "competitors.txt"
        if not competitors_file.exists():
            raise FileNotFoundError(f"Missing: {competitors_file}")

        competitors = [
            line.strip()
            for line in competitors_file.read_text().splitlines()
            if line.strip() and not line.strip().startswith('#')
        ]

        if len(competitors) < 3:
            raise ValueError(f"Need at least 3 competitors, got {len(competitors)}")

        print(f"✅ Competitors: {len(competitors)} provided")

        # 3. Load Intake Form
        intake_form_file = client_dir / "intake_form.json"
        if not intake_form_file.exists():
            raise FileNotFoundError(f"Missing: {intake_form_file}")

        try:
            intake_form = json.loads(intake_form_file.read_text())
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in intake_form.json: {e}")

        # Validate required fields
        required_fields = ['client_name', 'game_name', 'launch_date']
        missing = [f for f in required_fields if f not in intake_form]
        if missing:
            raise ValueError(f"Missing required fields in intake_form.json: {missing}")

        print(f"✅ Intake Form: {intake_form['client_name']} - {intake_form['game_name']}")

        # 4. Load Strategy Notes
        strategy_notes_file = client_dir / "strategy_notes.txt"
        if not strategy_notes_file.exists():
            raise FileNotFoundError(f"Missing: {strategy_notes_file}")

        strategy_notes = strategy_notes_file.read_text().strip()

        if not strategy_notes:
            print("⚠️  Warning: Strategy notes are empty")

        print(f"✅ Strategy Notes: {len(strategy_notes)} characters")

        return ClientInputs(
            steam_url=steam_url,
            app_id=app_id,
            competitors=competitors,
            intake_form=intake_form,
            strategy_notes=strategy_notes
        )

    @staticmethod
    def create_example_inputs(output_dir: Path, client_name: str = "example-client"):
        """
        Create example input files for testing/documentation.
        """
        client_dir = output_dir / client_name
        client_dir.mkdir(exist_ok=True)

        # Example Steam URL
        (client_dir / "steam_url.txt").write_text(
            "https://store.steampowered.com/app/1091500/Cyberpunk_2077/"
        )

        # Example Competitors
        (client_dir / "competitors.txt").write_text("""# Top competitors for this game
The Witcher 3: Wild Hunt
Deus Ex: Mankind Divided
Watch Dogs 2
Fallout 4
Borderlands 3
""")

        # Example Intake Form
        intake_form = {
            "client_name": "Example Studio",
            "client_email": "contact@examplestudio.com",
            "game_name": "Awesome RPG",
            "launch_date": "2025-03-15",
            "target_price": 29.99,
            "main_concerns": "Pricing strategy, launch timing, visibility",
            "marketing_budget": "Limited (<$5K)",
            "team_size": 3,
            "development_stage": "Pre-launch",
            "wishlist_count": 2500
        }
        (client_dir / "intake_form.json").write_text(
            json.dumps(intake_form, indent=2)
        )

        # Example Strategy Notes
        (client_dir / "strategy_notes.txt").write_text("""Strategy Call Notes - January 5, 2025

Client Emotional State: Anxious but motivated

Key Concerns:
- Worried the capsule image isn't standing out vs competitors
- Concerned about launching in March (busy season?)
- Not sure if $29.99 is the right price point
- Limited marketing budget

Wishlist Status:
- Currently at 2,500 wishlists
- Growth has slowed in the past month

Client's Target Audience:
- Fans of story-driven RPGs
- Players who enjoyed The Witcher 3 and Cyberpunk 2077
- Target age: 18-35

Additional Context:
- First game from this studio
- Team of 3 working full-time for 2 years
- No publisher, self-funded
- Plan to launch on Steam first, then Epic/GOG later

Priority Overrides:
- Client is most worried about pricing (mentioned 3 times)
- Needs reassurance on launch timing
- Store page optimization is critical (low wishlist velocity)
""")

        print(f"\n✅ Example inputs created at: {client_dir}")
        print("\n📝 Created files:")
        print(f"  - steam_url.txt")
        print(f"  - competitors.txt")
        print(f"  - intake_form.json")
        print(f"  - strategy_notes.txt")


def validate_intake_form(intake_form: Dict[str, Any]) -> List[str]:
    """
    Validate intake form data and return list of warnings.
    """
    warnings = []

    # Check required fields
    required = {
        'client_name': str,
        'game_name': str,
        'launch_date': str,
    }

    for field, field_type in required.items():
        if field not in intake_form:
            warnings.append(f"Missing required field: {field}")
        elif not isinstance(intake_form[field], field_type):
            warnings.append(f"Field '{field}' should be {field_type.__name__}")

    # Check optional but recommended fields
    recommended = ['target_price', 'main_concerns', 'team_size', 'development_stage']
    for field in recommended:
        if field not in intake_form:
            warnings.append(f"Missing recommended field: {field}")

    # Validate launch date format
    if 'launch_date' in intake_form:
        launch_date = intake_form['launch_date']
        if not re.match(r'\d{4}-\d{2}-\d{2}', launch_date):
            warnings.append(f"Launch date should be YYYY-MM-DD format, got: {launch_date}")

    return warnings


if __name__ == "__main__":
    """Test the input processor"""
    from pathlib import Path

    # Create example inputs
    test_dir = Path("inputs")
    InputProcessor.create_example_inputs(test_dir)

    # Load and validate
    try:
        inputs = InputProcessor.load_inputs_from_directory(test_dir / "example-client")
        print("\n✅ All inputs loaded successfully!")
        print(f"\nApp ID: {inputs.app_id}")
        print(f"Competitors: {inputs.competitors}")
        print(f"Client: {inputs.intake_form['client_name']}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
