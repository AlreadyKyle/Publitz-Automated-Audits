# Publitz Automated Steam Audit Tool

Automated tool for generating comprehensive Steam launch readiness and post-launch performance reports.

## Features

- 🔍 **Auto-Detection**: Automatically detects if a game needs Pre-Launch or Post-Launch report
- 🤖 **AI-Powered**: Uses Claude AI to generate detailed, actionable insights
- 📊 **Data Collection**: Automatically scrapes Steam, SteamDB, and competitor data
- 📄 **Professional Reports**: Generates comprehensive PDF reports matching manual templates
- 🚀 **One-Click Operation**: Just paste a Steam URL and go

## Setup

1. Install Python 3.11+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. Create `.env` file with your API keys:
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Open the Streamlit app in your browser
2. Paste a Steam store page URL
3. Click "Generate Report"
4. Wait for data collection and AI analysis
5. Download the generated PDF report

## Report Types

### Pre-Launch Report
Generated for games that haven't launched yet. Includes:
- Steam compliance audit
- Store page optimization
- Competitive benchmarking
- Regional pricing strategy
- Launch timing analysis

### Post-Launch Report
Generated for launched games. Includes:
- Performance diagnostics
- Sales analysis
- Review sentiment analysis
- Pricing recovery strategy
- 90-day live-ops roadmap

## Architecture

- `app.py` - Streamlit web interface
- `src/steam_scraper.py` - Steam store data collection
- `src/steamdb_scraper.py` - SteamDB competitive data
- `src/ai_generator.py` - Claude AI integration
- `src/report_generator.py` - PDF report generation
- `src/utils.py` - Helper utilities

## License

Internal use only.
