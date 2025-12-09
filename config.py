"""
Configuration management for Publitz Audit System.
Loads settings from .env file and validates configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # API Keys (simplified - only what we actually use)
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    RAWG_API_KEY = os.getenv('RAWG_API_KEY', '5353e48dc2a4446489ec7c0bbb1ce9e9')

    # NOTE: YouTube and Steam Web API removed - they were unreliable/deprecated
    # Primary data source is Steam URL scraping + SteamSpy (both free, no keys)

    # Claude Settings
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-5-20250929')
    CLAUDE_MAX_TOKENS = int(os.getenv('CLAUDE_MAX_TOKENS', 15000))
    CLAUDE_TEMPERATURE = float(os.getenv('CLAUDE_TEMPERATURE', 0.7))

    # Paths
    PROJECT_ROOT = Path(__file__).parent
    INPUT_DIR = PROJECT_ROOT / os.getenv('INPUT_DIR', 'inputs')
    OUTPUT_DIR = PROJECT_ROOT / os.getenv('OUTPUT_DIR', 'output')
    TEMPLATE_DIR = PROJECT_ROOT / os.getenv('TEMPLATE_DIR', 'templates')

    # Limits
    MAX_COMPETITORS = int(os.getenv('MAX_COMPETITORS', 10))
    REPORT_TIMEOUT = int(os.getenv('REPORT_TIMEOUT', 600))  # 10 minutes

    # Steam API
    STEAM_API_BASE = "https://store.steampowered.com/api"
    STEAMSPY_API_BASE = "https://steamspy.com/api.php"

    @classmethod
    def validate(cls):
        """Validate configuration before running"""
        errors = []

        if not cls.ANTHROPIC_API_KEY:
            errors.append("❌ ANTHROPIC_API_KEY not set in .env file")

        if errors:
            raise ValueError("\n".join(errors))

        # Create directories if needed
        cls.INPUT_DIR.mkdir(exist_ok=True)
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.TEMPLATE_DIR.mkdir(exist_ok=True)

        print("✅ Configuration validated successfully")

    @classmethod
    def get_client_input_dir(cls, client_name: str) -> Path:
        """Get input directory for a specific client"""
        client_dir = cls.INPUT_DIR / client_name
        client_dir.mkdir(exist_ok=True)
        return client_dir

    @classmethod
    def get_client_output_dir(cls, client_name: str) -> Path:
        """Get output directory for a specific client"""
        client_dir = cls.OUTPUT_DIR / client_name
        client_dir.mkdir(exist_ok=True)
        return client_dir


if __name__ == "__main__":
    # Test configuration
    try:
        Config.validate()
        print("\n📁 Paths:")
        print(f"  Input: {Config.INPUT_DIR}")
        print(f"  Output: {Config.OUTPUT_DIR}")
        print(f"  Templates: {Config.TEMPLATE_DIR}")
        print("\n⚙️  Settings:")
        print(f"  Claude Model: {Config.CLAUDE_MODEL}")
        print(f"  Max Tokens: {Config.CLAUDE_MAX_TOKENS}")
        print(f"  Max Competitors: {Config.MAX_COMPETITORS}")
    except ValueError as e:
        print(f"\n{e}")
        print("\n💡 Create a .env file with ANTHROPIC_API_KEY=your_key_here")
