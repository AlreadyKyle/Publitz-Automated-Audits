# Quick Start Guide

## Prerequisites

- Python 3.11 or higher
- Anthropic API Key ([Get one here](https://console.anthropic.com/))

## Installation

### Option 1: Automated Setup (Recommended)

```bash
./setup.sh
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Configuration

1. Open `.env` file
2. Add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Running the App

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run Streamlit app
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## Usage

1. **Enter Steam URL**: Paste a Steam store page URL (e.g., `https://store.steampowered.com/app/1234567/GameName/`)

2. **Generate Report**: Click "🚀 Generate Report"

3. **Wait for Processing**: The tool will:
   - Scrape Steam store data
   - Gather competitive intel from SteamDB
   - Auto-detect if game is pre-launch or post-launch
   - Generate AI-powered analysis
   - Create professional PDF report

4. **Download Report**: Click "📥 Download PDF Report" to save

## Report Types

### Pre-Launch Report
For games that haven't launched yet. Includes:
- Steam compliance audit
- Store page optimization (capsule, description, tags, screenshots)
- Competitive benchmarking
- Regional pricing strategy
- Launch timing analysis
- Priority action plan

### Post-Launch Report
For launched games. Includes:
- Performance diagnostics
- Sales analysis (if data available)
- Review sentiment analysis
- Pricing recovery strategy
- 90-day live-ops roadmap
- Revenue projections

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Make sure you've created `.env` file and added your API key
- Or enter the API key directly in the sidebar

### "Invalid Steam URL"
- Ensure you're using a full Steam store page URL
- Format: `https://store.steampowered.com/app/[APP_ID]/[GAME_NAME]/`

### Scraping errors
- Some games may have age gates or region restrictions
- The tool handles most cases automatically
- If issues persist, check that the game is publicly visible

### PDF generation issues
- WeasyPrint requires system dependencies
- On Linux: `apt-get install python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info`
- On Mac: `brew install cairo pango gdk-pixbuf libffi`

## Features

- ✅ Automatic pre-launch/post-launch detection
- ✅ Comprehensive Steam data scraping
- ✅ SteamDB competitive intelligence
- ✅ AI-powered analysis using Claude
- ✅ Professional PDF report generation
- ✅ One-click operation
- ✅ Progress tracking
- ✅ Export to PDF and Markdown

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review error messages in the Streamlit interface
3. Contact Kyle Smith for internal support

## Notes

- This tool is for internal use only
- Reports are confidential
- API costs: ~$0.50-$1.50 per report depending on complexity
- Processing time: 1-3 minutes per report
