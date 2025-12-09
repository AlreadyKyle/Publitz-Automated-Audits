# API Setup & Testing Guide

This guide will help you set up and test all external APIs used in the Publitz Automated Audits tool.

## Required APIs for Full Functionality

### 1. **Anthropic Claude** ⭐ REQUIRED
- **Purpose**: AI-powered report generation and analysis
- **Cost**: Pay-as-you-go (~$0.50-1.50 per audit with Claude Sonnet)
- **Get your key**: https://console.anthropic.com/
- **Environment variable**: `ANTHROPIC_API_KEY`

### 2. **Twitch (Helix API)** 🎮 REQUIRED FOR STREAMING DATA
- **Purpose**: Real-time streaming viewership and influencer discovery
- **Cost**: FREE
- **Setup**:
  1. Go to https://dev.twitch.tv/console/apps
  2. Click "Register Your Application"
  3. Name: "Publitz Audits" (or anything)
  4. OAuth Redirect URLs: `http://localhost`
  5. Category: "Application Integration"
  6. Click "Create"
  7. Copy your **Client ID**
  8. Click "New Secret" and copy your **Client Secret**
- **Environment variables**:
  - `TWITCH_CLIENT_ID`
  - `TWITCH_CLIENT_SECRET`

### 3. **YouTube Data API v3** 📺 REQUIRED FOR INFLUENCER OUTREACH
- **Purpose**: Find YouTube creators for outreach
- **Cost**: FREE (10,000 units/day = ~100 searches)
- **Setup**:
  1. Go to https://console.cloud.google.com/
  2. Create a new project or select existing
  3. Enable "YouTube Data API v3"
  4. Go to "Credentials" → "Create Credentials" → "API Key"
  5. Copy your API key
  6. (Optional) Restrict key to YouTube Data API v3
- **Environment variable**: `YOUTUBE_API_KEY`

### 4. **RAWG** 🎯 RECOMMENDED FOR GAME METADATA
- **Purpose**: Community ratings, Metacritic scores, engagement metrics
- **Cost**: FREE (20,000 requests/month)
- **Get your key**: https://rawg.io/apidocs
- **Environment variable**: `RAWG_API_KEY`

### 5. **IGDB (Twitch-owned)** 🎯 RECOMMENDED FOR CRITIC SCORES
- **Purpose**: Critic ratings, user ratings, community signals
- **Cost**: FREE for non-commercial use
- **Setup**:
  1. Go to https://api-docs.igdb.com/#account-creation
  2. Register for a Twitch developer account
  3. Create an application (same as Twitch setup above if not done)
  4. Use the same Client ID and Secret as Twitch
- **Environment variables**:
  - `IGDB_CLIENT_ID` (same as Twitch)
  - `IGDB_CLIENT_SECRET` (same as Twitch)

### 6. **OpenAI GPT-4** (Optional)
- **Purpose**: Multi-model ensemble for higher quality reports
- **Cost**: Pay-as-you-go (~$0.30-0.60 per audit)
- **Get your key**: https://platform.openai.com/api-keys
- **Environment variable**: `OPENAI_API_KEY`

### 7. **Google Gemini** (Optional)
- **Purpose**: Multi-model ensemble for higher quality reports
- **Cost**: FREE tier available
- **Get your key**: https://makersuite.google.com/app/apikey
- **Environment variable**: `GOOGLE_API_KEY`

---

## Quick Setup

### Step 1: Copy .env.example to .env
```bash
cp .env.example .env
```

### Step 2: Edit .env and add your API keys
```bash
nano .env  # or use any text editor
```

### Step 3: Add your keys to .env
```env
# REQUIRED
ANTHROPIC_API_KEY=sk-ant-api03-xxxx...

# REQUIRED FOR STREAMING DATA
TWITCH_CLIENT_ID=xxxxxxxxxxxx
TWITCH_CLIENT_SECRET=xxxxxxxxxxxx

# REQUIRED FOR INFLUENCER OUTREACH
YOUTUBE_API_KEY=AIzaSyXXXXXXXXXX

# RECOMMENDED (both use same Twitch credentials)
IGDB_CLIENT_ID=xxxxxxxxxxxx
IGDB_CLIENT_SECRET=xxxxxxxxxxxx
RAWG_API_KEY=xxxxxxxxxxxx

# OPTIONAL
OPENAI_API_KEY=sk-xxxx...
GOOGLE_API_KEY=AIzaSyXXXXXXXXXX
```

---

## Testing Your APIs

### Test All APIs at Once
```bash
python scripts/test_apis.py
```

### Test Individual APIs

#### Test Twitch API
```python
from src.twitch_collector import TwitchCollector

twitch = TwitchCollector()
data = twitch.analyze_game_viewership("Hades")
print(f"Current viewers: {data.get('current_viewers', 0)}")
print(f"Data source: {data.get('data_source')}")
# Should show 'twitch_api' if working, 'fallback' if not
```

#### Test YouTube API
```python
from src.youtube_api import get_youtube_outreach_analysis

result = get_youtube_outreach_analysis("Hades", ["Roguelike"])
print(f"Channels found: {len(result.get('channels', []))}")
print(f"Total reach: {result.get('total_reach', 0):,}")
```

#### Test RAWG API
```python
from src.rawg_api import RAWGApi

rawg = RAWGApi()
data = rawg.search_game("Hades")
if data:
    print(f"RAWG Rating: {data.get('rating', 0)}/5")
    print(f"Ratings Count: {data.get('ratings_count', 0):,}")
    print(f"Metacritic: {data.get('metacritic', 'N/A')}")
else:
    print("RAWG API key not configured or game not found")
```

#### Test IGDB API
```python
from src.igdb_api import IGDBApi

igdb = IGDBApi()
data = igdb.search_game("Hades")
if data:
    print(f"IGDB Rating: {data.get('rating', 0)}/5")
    print(f"Critic Score: {data.get('aggregated_rating', 0)}/100")
    print(f"Followers: {data.get('follows', 0):,}")
else:
    print("IGDB API key not configured or game not found")
```

#### Test Claude API
```python
from src.ai_generator import AIGenerator
import os

api_key = os.getenv('ANTHROPIC_API_KEY')
ai = AIGenerator(api_key)

# Simple test
result = ai.client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say 'API works!'"}]
)
print(result.content[0].text)
# Should print "API works!" or similar
```

---

## Troubleshooting

### "Twitch API credentials not configured"
- Check that both `TWITCH_CLIENT_ID` and `TWITCH_CLIENT_SECRET` are set in .env
- Verify the .env file is in the project root directory
- Restart the Streamlit app after adding credentials

### "RAWG_API_KEY not set"
- Get a free API key from https://rawg.io/apidocs
- Add to .env: `RAWG_API_KEY=your_key_here`

### "IGDB access token failed"
- IGDB uses Twitch OAuth, so check your Twitch credentials
- Make sure `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET` match your Twitch app

### "YouTube quota exceeded"
- Free tier: 10,000 units/day
- Each search costs ~100 units = ~100 searches/day
- Wait 24 hours for quota to reset
- Or: Enable billing in Google Cloud for higher limits

### "Anthropic API authentication error"
- Verify your API key starts with `sk-ant-`
- Check your API key is active at https://console.anthropic.com/
- Ensure you have credits in your account

---

## What Happens Without Each API?

| API | Impact if Missing |
|-----|-------------------|
| **Anthropic** | ❌ App won't work - required for report generation |
| **Twitch** | ⚠️ Uses fallback data - limited streamer recommendations |
| **YouTube** | ⚠️ Uses fallback data - generic creator suggestions |
| **RAWG** | ℹ️ Missing community ratings and Metacritic scores |
| **IGDB** | ℹ️ Missing critic scores and community signals |
| **OpenAI** | ℹ️ No multi-model ensemble (Claude-only is fine) |
| **Gemini** | ℹ️ No multi-model ensemble (Claude-only is fine) |

---

## Cost Estimates (per 100 audits)

| API | Cost | Notes |
|-----|------|-------|
| **Claude** | $50-150 | Main cost driver |
| **Twitch** | $0 | FREE |
| **YouTube** | $0 | FREE (within quota) |
| **RAWG** | $0 | FREE tier sufficient |
| **IGDB** | $0 | FREE |
| **OpenAI** | $30-60 | Optional |
| **Gemini** | $0-10 | Optional |
| **Total** | ~$50-210 | For 100 audits sold at $99 = ~$9,900 revenue |

**Profit margin**: ~95-98% (excluding Claude costs: 85-90%)

---

## Best Practices

1. **Always set Anthropic API key** - Required for core functionality
2. **Set Twitch + YouTube keys** - Critical for professional reports
3. **Set RAWG + IGDB keys** - Adds significant value for $99 price point
4. **Don't commit .env to git** - Already in .gitignore
5. **Use Streamlit Secrets for deployment**:
   ```toml
   # In Streamlit Cloud: Settings > Secrets
   ANTHROPIC_API_KEY = "sk-ant-xxx"
   TWITCH_CLIENT_ID = "xxx"
   TWITCH_CLIENT_SECRET = "xxx"
   YOUTUBE_API_KEY = "xxx"
   RAWG_API_KEY = "xxx"
   IGDB_CLIENT_ID = "xxx"
   IGDB_CLIENT_SECRET = "xxx"
   ```

---

## Support

If you encounter issues:
1. Check this guide first
2. Verify all environment variables are set correctly
3. Test individual APIs using the code snippets above
4. Check API provider status pages:
   - Anthropic: https://status.anthropic.com/
   - Twitch: https://devstatus.twitch.tv/
   - Google (YouTube): https://status.cloud.google.com/

---

**Remember**: For a professional $99 audit, having all APIs configured provides the most comprehensive and valuable reports for your customers!
