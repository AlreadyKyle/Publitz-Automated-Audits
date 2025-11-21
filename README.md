# Publitz Automated Game Audits

AI-powered Steam game audit system. Paste a Steam URL, get a professional audit report.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

That's it! The app will open in your browser.

## How to Use

1. **Get your Anthropic API Key**: [console.anthropic.com](https://console.anthropic.com/)
2. **Paste a Steam Game URL**: Like `https://store.steampowered.com/app/292030/The_Witcher_3_Wild_Hunt/`
3. **Click Generate**: The system will automatically:
   - Detect if the game is Pre-Launch or Post-Launch
   - Find 3-10 competitor games
   - Analyze Steam data
   - Generate a comprehensive audit report with Claude AI
4. **Download**: Get your report as a Markdown file

## Features

✅ **Paste Steam URL** - No need to type game names
✅ **Auto-Detect Launch Status** - Automatically determines Pre-Launch vs Post-Launch
✅ **Always Finds Competitors** - Multi-tier search ensures 3-10 competitors (never zero)
✅ **AI-Powered Reports** - Uses Claude Sonnet 4.5 for professional analysis
✅ **Real Steam Data** - Live data from Steam API and SteamSpy
✅ **One-Click Download** - Export as Markdown

## What You Get

### Pre-Launch Reports Include:
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

### Post-Launch Reports Include:
- Executive Summary
- Market Positioning Analysis
- Sales & Revenue Performance
- Marketing Effectiveness
- Competitor Comparison
- Review & Sentiment Analysis
- Visibility & Discoverability
- Actionable Recommendations
- Pricing Strategy
- Growth Opportunities

## Environment Setup (Optional)

To skip entering API key every time, create a `.env` file:

```bash
ANTHROPIC_API_KEY=your_key_here
```

## Requirements

- Python 3.8+
- Internet connection
- Anthropic API key

## Project Structure

```
Publitz-Automated-Audits/
├── app.py                      # Main Streamlit web app
├── src/
│   ├── ai_generator.py         # Claude AI report generator
│   ├── game_search.py          # Steam URL parser & competitor finder
│   └── steamdb_scraper.py      # Steam data scraper
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## Fixes Applied

✅ **Model Error Fixed**: Updated to `claude-sonnet-4-5-20250929` (was using non-existent model)
✅ **Zero Competitors Fixed**: Guaranteed minimum 3-10 competitors with multi-tier fallback system
✅ **URL-Based Input**: Paste Steam URLs instead of searching by name
✅ **Auto-Detection**: Automatically detects Pre-Launch vs Post-Launch from release date

## Support

Built with Claude AI and Streamlit for Publitz game audits.

---

**Made with ❤️ for game developers**
