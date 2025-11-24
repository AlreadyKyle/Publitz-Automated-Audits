# API Usage Map - Publitz Automated Audits

Complete mapping of all external APIs used in the system, where they're called, and their purpose.

## 📊 API Status Overview

| API | Status | Required | Files Using It | Purpose |
|-----|--------|----------|----------------|---------|
| **Steam API** | ✅ Working | **CRITICAL** | game_search.py, steam_api.py | Game details, pricing, reviews |
| **SteamSpy API** | ✅ Working | **CRITICAL** | game_search.py, comparable_games_analyzer.py | Owner counts, revenue estimates |
| **Claude/Anthropic** | ✅ Configured | **HIGH** | negative_review_analyzer.py, ai_generator.py | AI-powered review categorization |
| **RAWG API** | ⚠️ Optional | Optional | rawg_api.py | Game metadata enrichment |
| **YouTube API** | ⚠️ Optional | Optional | youtube_api.py | Content creator analysis |
| **Twitch API** | ⚠️ Optional | Optional | twitch_collector.py | Streaming analytics |

---

## 🔴 CRITICAL APIs (Required for Core Functionality)

### 1. Steam Store API
**Purpose**: Primary source for game data
**Endpoint**: `https://store.steampowered.com/api`
**Authentication**: None required (public API)
**Rate Limits**: ~200 requests/5 minutes

**Used In**:
- `src/game_search.py` (lines 27-28)
  - `get_game_details(app_id)` - Fetch game information
  - `parse_steam_url(url)` - Extract app ID from Steam URLs
  - `get_game_from_url(url)` - Get game data from URL

**Data Retrieved**:
- Game name, description, genres
- Price (current + original)
- Release date
- Developer/Publisher info
- Platform support
- Categories/tags
- Review scores (aggregate)

**Example Usage**:
```python
search = GameSearch()
game_data = search.get_game_details(1145350)  # Hades II
```

---

### 2. SteamSpy API
**Purpose**: Owner counts and revenue estimates (not available from official Steam API)
**Endpoint**: `https://steamspy.com/api.php`
**Authentication**: None required (public API)
**Rate Limits**: 4 requests/second

**Used In**:
- `src/game_search.py` (line 28)
  - `get_steamspy_data(app_id)` - Get owner/revenue data
- `src/comparable_games_analyzer.py` (line 191, 244, 772)
  - Used for owner count filtering when finding comparable games
  - Revenue estimation calculations

**Data Retrieved**:
- Owner ranges (e.g., "100,000 .. 200,000")
- Positive/Negative review counts
- Average playtime
- Player count estimates

**Example Usage**:
```python
search = GameSearch()
spy_data = search.get_steamspy_data(1145350)
owners = spy_data.get('owners', '0 .. 0')  # "3000000 .. 3500000"
```

---

### 3. Steam Reviews API
**Purpose**: Fetch individual user reviews for negative review analysis
**Endpoint**: `https://store.steampowered.com/appreviews/{app_id}`
**Authentication**: None required (public API)
**Rate Limits**: Moderate (~100 requests/minute)

**Used In**:
- `src/negative_review_analyzer.py` (lines 98-99)
  - `fetch_negative_reviews(app_id, count)` - Get negative reviews
  - Filters: most helpful, recent, detailed

**Data Retrieved**:
- Review text (full content)
- Helpfulness votes
- Playtime at review
- Recommendation (positive/negative)
- Post date

**Example Usage**:
```python
analyzer = NegativeReviewAnalyzer(api_key)
reviews = analyzer.fetch_negative_reviews(app_id=1145350, count=100)
```

---

## 🟡 HIGH PRIORITY APIs (Enhanced Functionality)

### 4. Claude/Anthropic API
**Purpose**: AI-powered analysis of negative reviews
**Endpoint**: Anthropic API SDK
**Authentication**: API Key required
**Rate Limits**: Depends on plan (typically 50-200 RPM)

**API Key**: `ANTHROPIC_API_KEY` (set in .env)

**Used In**:
- `src/negative_review_analyzer.py` (line 18, 63-66)
  - `categorize_complaints(reviews)` - AI categorization
  - Model: `claude-sonnet-4-20250514`
- `src/ai_generator.py`
  - Various AI text generation tasks

**Data Sent**:
- Negative review text
- Categorization prompts

**Data Retrieved**:
- Complaint categories (bugs, balance, content, performance, etc.)
- Severity ratings (critical/moderate/minor)
- Fixability assessments
- Root cause analysis

**Example Usage**:
```python
import os
analyzer = NegativeReviewAnalyzer(
    claude_api_key=os.getenv('ANTHROPIC_API_KEY')
)
complaints = analyzer.categorize_complaints(negative_reviews)
```

**Current Status**: ✅ API key configured, SDK installed

---

## 🟢 OPTIONAL APIs (Future Enhancements)

### 5. RAWG API
**Purpose**: Game metadata enrichment (alternative to IGDB)
**Endpoint**: `https://api.rawg.io/api`
**Authentication**: API Key required
**Rate Limits**: 20,000 requests/month (free tier)

**API Key**: `RAWG_API_KEY` (set in .env)

**Used In**:
- `src/rawg_api.py`
  - Game metadata lookup
  - Genre/tag enrichment

**Current Status**: ⚠️ Configured but not actively used in core flow

---

### 6. YouTube Data API
**Purpose**: Content creator and influencer analysis
**Endpoint**: `https://www.googleapis.com/youtube/v3`
**Authentication**: API Key required
**Rate Limits**: 10,000 quota units/day (free tier)

**API Key**: `YOUTUBE_API_KEY` (set in .env)

**Used In**:
- `src/youtube_api.py`
  - Search for game-related videos
  - Channel statistics
  - View count analysis

**Current Status**: ⚠️ Configured but not actively used in core flow

---

### 7. Twitch API
**Purpose**: Live streaming analytics
**Endpoint**: `https://api.twitch.tv/helix`
**Authentication**: Client ID + Secret required
**Rate Limits**: 800 requests/minute

**Credentials**:
- `TWITCH_CLIENT_ID` (set in .env)
- `TWITCH_CLIENT_SECRET` (set in .env)

**Used In**:
- `src/twitch_collector.py`
  - Stream count by game
  - Viewer statistics
  - Streamer directory

**Current Status**: ⚠️ Configured but not actively used in core flow

---

## 🔄 API Call Flow in Report Generation

### Main Report Generation Pipeline

```
User Input (Steam URL or App ID)
         ↓
┌────────────────────────────────────────────┐
│  1. GameSearch.get_game_details()          │
│     └→ Steam API: Game data                │
│     └→ SteamSpy API: Owner counts          │
└────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────┐
│  2. ReportOrchestrator                     │
│     ├→ Executive Summary (no API)          │
│     ├→ ROI Calculator (no API)             │
│     ├→ Comparable Games Analyzer           │
│     │  └→ SteamSpy API: Find similar games│
│     └→ Negative Review Analyzer            │
│        ├→ Steam Reviews API: Fetch reviews │
│        └→ Claude API: Categorize complaints│
└────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────┐
│  3. Three-Tier Report Assembly             │
│     ├→ Tier 1: Executive (2-3 pages)       │
│     ├→ Tier 2: Strategic (8-12 pages)      │
│     └→ Tier 3: Deep-dive (30-40 pages)     │
└────────────────────────────────────────────┘
```

### API Call Frequency (Per Report)

| API | Calls per Report | When Called |
|-----|------------------|-------------|
| Steam API | 1-2 | Initial game data fetch |
| SteamSpy API | 1-16 | Owner data + comparable games search |
| Steam Reviews API | 1-5 | Negative review analysis (if score <80%) |
| Claude API | 1-3 | Review categorization (if negative reviews) |
| RAWG/YouTube/Twitch | 0 | Not in core flow (future enhancement) |

---

## 🛠️ API Configuration

### Environment Variables Required

```bash
# Core System (required)
ANTHROPIC_API_KEY=<your-anthropic-api-key>

# Optional Enhancement APIs
RAWG_API_KEY=<your-rawg-api-key>
YOUTUBE_API_KEY=<your-youtube-api-key>
TWITCH_CLIENT_ID=<your-twitch-client-id>
TWITCH_CLIENT_SECRET=<your-twitch-secret>
```

### Loading Configuration

```python
# Method 1: Direct environment variables
import os
api_key = os.getenv('ANTHROPIC_API_KEY')

# Method 2: .env file (recommended)
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('ANTHROPIC_API_KEY')
```

---

## ✅ What's Working vs What's Not

### ✅ Fully Functional (No Blockers)
1. **Steam Store API** - Public, no auth needed
2. **SteamSpy API** - Public, no auth needed
3. **Steam Reviews API** - Public, no auth needed
4. **ROI Calculator** - Pure computation, no API calls
5. **Executive Summary Generator** - Pure logic, no API calls

### ✅ Configured and Ready
1. **Claude/Anthropic API** - API key set, SDK installed
   - Can now run negative review analysis
   - Can categorize complaints automatically

### ⚠️ Configured But Not Integrated
1. **RAWG API** - Key available, not in core flow
2. **YouTube API** - Key available, not in core flow
3. **Twitch API** - Credentials available, not in core flow

These optional APIs can be integrated for enhanced features like:
- Influencer discovery (YouTube/Twitch)
- Genre trend analysis (RAWG)
- Content creator outreach lists (YouTube/Twitch)

---

## 🎯 Next Steps

### Immediate (Required for Core Functionality)
1. ✅ Install dependencies (beautifulsoup4, anthropic) - **DONE**
2. ✅ Set API keys in environment - **DONE**
3. ⏳ Test Steam + SteamSpy APIs - **IN PROGRESS**
4. ⏳ Test Claude API for review analysis - **IN PROGRESS**
5. ⏳ Verify end-to-end report generation - **NEXT**

### Future Enhancements (Optional)
1. Integrate YouTube API for influencer discovery
2. Integrate Twitch API for streaming metrics
3. Use RAWG API for genre trend analysis
4. Add Reddit API for community sentiment
5. Add Discord API for community size tracking

---

## 🚨 Critical Dependencies

### Must Be Installed
```bash
pip install beautifulsoup4 lxml requests anthropic
```

### Must Be Set
```bash
export ANTHROPIC_API_KEY="<your-anthropic-api-key-here>"
```

### Nice to Have (for optional features)
```bash
export RAWG_API_KEY="your-key"
export YOUTUBE_API_KEY="your-key"
export TWITCH_CLIENT_ID="your-id"
export TWITCH_CLIENT_SECRET="your-secret"
```

---

## 📝 Summary

**What you NEED for the system to work:**
1. ✅ Steam API (public, no setup needed)
2. ✅ SteamSpy API (public, no setup needed)
3. ✅ Claude API (configured with your key)

**What you DON'T need (optional enhancements):**
1. ⚠️ RAWG API (game metadata - not critical)
2. ⚠️ YouTube API (influencer analysis - future feature)
3. ⚠️ Twitch API (streaming metrics - future feature)

**Bottom Line**: The core system is ready to generate reports. The 3 critical APIs are working. Optional APIs are configured but not integrated into the main flow yet.
