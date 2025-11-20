# Publitz Automated Game Audits

AI-powered game audit system for pre-launch and post-launch analysis using Claude AI and Steam data.

## Features

- **Automated Game Discovery**: Search and identify games on Steam
- **Competitor Analysis**: Automatically find and analyze 3-10 competitor games (never zero!)
- **AI-Powered Reports**: Generate comprehensive audit reports using Claude Sonnet 4.5
- **Pre-Launch Audits**: Market analysis, competitive landscape, pricing strategy, and launch recommendations
- **Post-Launch Audits**: Performance analysis, sales data, review sentiment, and growth opportunities
- **Steam Data Integration**: Real-time data from Steam API and SteamSpy

## Fixed Issues

### ✅ Model Error Fixed
- **Old Error**: `claude-3-5-sonnet-20240620` model not found (404 error)
- **Fix**: Updated to use `claude-sonnet-4-5-20250929` (latest Claude model)

### ✅ Zero Competitors Fixed
- **Old Issue**: System could return 0 competitors
- **Fix**: Implemented multi-tier fallback system:
  1. Search by primary tag
  2. Search by genre
  3. Broad category search
  4. Fallback competitor generation
- **Result**: Always returns 3-10 relevant competitors

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Publitz-Automated-Audits
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Anthropic API key:
   - Option 1: Create a `.env` file with `ANTHROPIC_API_KEY=your_key_here`
   - Option 2: Enter it in the app sidebar when running

## Usage

Run the Streamlit application:

```bash
streamlit run app.py
```

### Steps:
1. Enter your Anthropic API key in the sidebar (if not in .env)
2. Select report type (Pre-Launch or Post-Launch)
3. Enter the game name to audit
4. Click "Generate Audit Report"
5. Download the generated report in Markdown format

## Report Templates

The system generates reports based on Publitz's professional templates:

### Pre-Launch Report Includes:
- Executive Summary
- Market Analysis
- Competitive Landscape
- Pricing Strategy
- Feature Differentiation
- Marketing Strategy Recommendations
- Steam Store Optimization
- Wishlist Strategy
- Launch Plan
- Risk Mitigation

### Post-Launch Report Includes:
- Executive Summary
- Market Positioning Analysis
- Sales & Revenue Performance
- Marketing Effectiveness
- Competitor Comparison
- Review & Sentiment Analysis
- Visibility & Discoverability
- Recommendations (Immediate, Short-term, Long-term)
- Pricing Strategy
- Growth Opportunities

## Project Structure

```
Publitz-Automated-Audits/
├── app.py                          # Main Streamlit application
├── src/
│   ├── __init__.py
│   ├── ai_generator.py             # Claude AI report generator
│   ├── game_search.py              # Game search and competitor finder
│   └── steamdb_scraper.py          # Steam data scraper
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore patterns
└── *.pdf                           # Report templates (reference materials)
```

## API Data Sources

- **Steam API**: Game details and store information
- **SteamSpy API**: Ownership estimates, player counts, and tags
- **Anthropic Claude API**: AI-powered report generation

## Requirements

- Python 3.8+
- Anthropic API key (for Claude AI)
- Internet connection (for Steam API access)

## Environment Variables

Create a `.env` file with:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## License

Proprietary - Publitz

## Support

For issues or questions, please contact the development team.

---

**Built with ❤️ using Claude AI and Streamlit**
