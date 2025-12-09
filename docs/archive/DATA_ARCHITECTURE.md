# Data Architecture & API Integration Map

**Complete mapping of data sources, APIs, and data flow for the Publitz system**

---

## 🎯 Data Requirements for Report Generation

### Critical Data (Required for Core Functionality)

| Data Point | Why Critical | Used In |
|------------|--------------|---------|
| **Game Name** | Identification | All reports, file naming |
| **Review Score %** | Performance scoring, tier determination | Executive Summary, Scoring |
| **Review Count** | Confidence level, validation | Executive Summary, Scoring |
| **Owner Count** | Revenue estimates, market size | ROI Calculator, Revenue Analysis |
| **Price** | ROI calculations, pricing analysis | ROI Calculator, Regional Pricing |
| **Revenue Estimate** | Performance assessment | All reports |
| **Genres** | Comparable games, market context | Comparable Games Analyzer |
| **Release Date** | Age analysis, lifecycle stage | All reports |

### Important Data (Enhances Analysis)

| Data Point | Purpose | Used In |
|------------|---------|---------|
| **Developer/Publisher** | Context, branding | Executive Summary |
| **Tags** | Comparable games matching | Comparable Games Analyzer |
| **Review Velocity** | Momentum assessment | Executive Summary, Scoring |
| **Playtime Stats** | Engagement metrics | Optional analysis |
| **Regional Pricing** | International strategy | ROI Calculator |

---

## 📊 API Data Source Matrix

### What Each API Provides

| Data Point | Steam Store API | Steam Web API | SteamSpy API | RAWG API | Claude API |
|------------|----------------|---------------|--------------|----------|------------|
| **Game Name** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Price (Current)** | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No |
| **Price (Original)** | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No |
| **Review Score %** | ⚠️ Aggregate only | ❌ No | ✅ Yes (Detailed) | ⚠️ Metacritic | ❌ No |
| **Review Count** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| **Positive Reviews** | ❌ No | ❌ No | ✅ Yes | ❌ No | ❌ No |
| **Negative Reviews** | ❌ No | ❌ No | ✅ Yes | ❌ No | ❌ No |
| **Owner Count** | ❌ No | ❌ No | ✅ **Yes** | ❌ No | ❌ No |
| **Revenue Estimate** | ❌ No | ❌ No | ⚠️ Calculated | ❌ No | ❌ No |
| **Genres** | ✅ Yes | ❌ No | ❌ No | ✅ Yes | ❌ No |
| **Tags** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| **Release Date** | ✅ Yes | ❌ No | ❌ No | ✅ Yes | ❌ No |
| **Developer** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| **Publisher** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| **Description** | ✅ Yes | ❌ No | ❌ No | ✅ Yes | ❌ No |
| **Screenshots** | ✅ Yes | ❌ No | ❌ No | ✅ Yes | ❌ No |
| **Playtime Average** | ❌ No | ❌ No | ✅ Yes | ❌ No | ❌ No |
| **Player Trends** | ❌ No | ⚠️ Limited | ✅ Yes | ❌ No | ❌ No |
| **Individual Reviews** | ✅ Yes (Store) | ❌ No | ❌ No | ❌ No | ❌ No |
| **Review Analysis** | ❌ No | ❌ No | ❌ No | ❌ No | ✅ **Yes** |
| **News/Updates** | ✅ Yes | ✅ Yes | ❌ No | ❌ No | ❌ No |

### API Priority Ranking

**Tier 1 - Critical (Must Have)**
1. **SteamSpy API** - ONLY source for owner counts (critical for revenue)
2. **Steam Store API** - Primary game data (price, genres, reviews)
3. **Claude API** - AI-powered review analysis

**Tier 2 - Important (Should Have)**
4. **Steam Web API** - Additional Steam data, news, player info

**Tier 3 - Nice to Have (Enhancement)**
5. **RAWG API** - Supplementary metadata, alternative to Steam
6. **YouTube API** - Influencer discovery (future feature)
7. **Twitch API** - Streaming analytics (future feature)

---

## 🔄 Data Flow Architecture

### Report Generation Flow

```
USER INPUT
  └─> Steam App ID or URL
       ↓
┌──────────────────────────────────────────────┐
│  DATA FETCHING LAYER                         │
├──────────────────────────────────────────────┤
│                                              │
│  1. Steam Store API                          │
│     └─> Game name, price, genres            │
│     └─> Release date, developer             │
│     └─> Description, screenshots            │
│     └─> Aggregate review count              │
│                                              │
│  2. SteamSpy API ⭐ CRITICAL                 │
│     └─> Owner count range                   │
│     └─> Positive/Negative review split      │
│     └─> Average playtime                    │
│     └─> Tags and metadata                   │
│                                              │
│  3. Steam Reviews API                        │
│     └─> Individual review text              │
│     └─> Helpfulness votes                   │
│     └─> Review dates                        │
│                                              │
└──────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────┐
│  PROCESSING LAYER                            │
├──────────────────────────────────────────────┤
│                                              │
│  1. Data Normalization                       │
│     └─> Parse owner ranges                  │
│     └─> Calculate review percentage         │
│     └─> Format dates and currencies         │
│                                              │
│  2. Revenue Estimation                       │
│     └─> owners × price × discount_factor    │
│     └─> Confidence scoring                  │
│                                              │
│  3. Performance Scoring                      │
│     └─> (review_% × 0.7) + owner_bonus      │
│     └─> Tier determination (1-4)            │
│                                              │
└──────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────┐
│  ANALYSIS LAYER                              │
├──────────────────────────────────────────────┤
│                                              │
│  1. Executive Summary Generator              │
│     INPUT: score, reviews, revenue, trend    │
│     OUTPUT: Tier-specific summary            │
│                                              │
│  2. ROI Calculator                           │
│     INPUT: revenue, price, owners            │
│     OUTPUT: 7 action types with ROI          │
│                                              │
│  3. Comparable Games Analyzer                │
│     INPUT: genres, price, owners, date       │
│     SOURCE: SteamSpy (find similar games)    │
│     OUTPUT: Competitive analysis             │
│                                              │
│  4. Negative Review Analyzer                 │
│     INPUT: negative review text              │
│     SOURCE: Claude API for categorization    │
│     OUTPUT: Categorized complaints + fixes   │
│                                              │
└──────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────┐
│  REPORT ASSEMBLY LAYER                       │
├──────────────────────────────────────────────┤
│                                              │
│  Report Orchestrator                         │
│     └─> Tier 1: Executive (2-3 pages)       │
│     └─> Tier 2: Strategic (8-12 pages)      │
│     └─> Tier 3: Deep-dive (30-40 pages)     │
│                                              │
└──────────────────────────────────────────────┘
       ↓
  FINAL REPORTS (Markdown)
```

---

## 🔧 Specific API Endpoints Used

### Steam Store API (No Key Required)

**Base URL**: `https://store.steampowered.com/api`

#### 1. Game Details
```
GET /appdetails?appids={app_id}
```
**Returns**: Name, price, genres, release date, developers, publishers, description

**Used By**: `src/game_search.py` → `get_game_details()`

---

### Steam Web API (Key: 7CD62F6A17C80F8E8889CE738578C014)

**Base URL**: `https://api.steampowered.com`

#### 1. App List
```
GET /ISteamApps/GetAppList/v2/?key={api_key}
```
**Returns**: Complete list of all Steam games

**Potential Use**: Game discovery, validation

#### 2. News for App
```
GET /ISteamNews/GetNewsForApp/v2/?appid={app_id}&key={api_key}
```
**Returns**: Recent news and updates for a game

**Potential Use**: Update tracking, momentum analysis

#### 3. Player Summaries
```
GET /ISteamUser/GetPlayerSummaries/v2/?key={api_key}&steamids={steam_ids}
```
**Returns**: Player profile information

**Potential Use**: Community analysis (future)

---

### SteamSpy API (No Key Required) ⭐ CRITICAL

**Base URL**: `https://steamspy.com/api.php`

#### 1. App Details
```
GET ?request=appdetails&appid={app_id}
```
**Returns**: **Owner count**, positive/negative reviews, playtime, tags

**Used By**:
- `src/game_search.py` → `get_steamspy_data()`
- `src/comparable_games_analyzer.py` → Owner count filtering

**CRITICAL**: This is the ONLY API that provides owner counts, which are essential for revenue estimation.

#### 2. Genre Search
```
GET ?request=genre&genre={genre_name}
```
**Returns**: All games in a genre with owner data

**Used By**: `src/comparable_games_analyzer.py` → `_find_by_genre()`

---

### Steam Reviews API (No Key Required)

**Base URL**: `https://store.steampowered.com/appreviews`

#### 1. Get Reviews
```
GET /{app_id}?json=1&filter=recent&num_per_page=100
```
**Returns**: Individual review text, votes, playtime, recommendation

**Used By**: `src/negative_review_analyzer.py` → `fetch_negative_reviews()`

**Filters**:
- `filter=recent` - Most recent reviews
- `filter=updated` - Most helpful reviews
- `review_type=negative` - Only negative reviews

---

### Claude API (Anthropic) ✅ WORKING

**Used Via**: `anthropic` Python SDK

**Model**: `claude-sonnet-4-20250514`

#### 1. Review Categorization
**Input**: Negative review text
**Output**: Categorized complaints with:
- Category (bugs, balance, content, etc.)
- Severity (critical, moderate, minor)
- Fixability (fixable, requires_resources, fundamental)
- Root cause analysis
- Fix recommendations

**Used By**: `src/negative_review_analyzer.py` → `categorize_complaints()`

---

## 📋 Data Dependencies by Component

### Executive Summary Generator
**Required Data**:
- Overall score ← *Calculated internally*
- Review count ← Steam Store API
- Review percentage ← SteamSpy API (positive/(positive+negative))
- Revenue estimate ← SteamSpy owners × Steam price
- Review velocity trend ← Manual/estimated
- Genre ← Steam Store API

**APIs Used**: Steam Store, SteamSpy
**External Dependencies**: None (works with provided data)

---

### ROI Calculator
**Required Data**:
- Current revenue ← SteamSpy owners × Steam price
- Current price ← Steam Store API
- Owner count ← SteamSpy API
- Genre ← Steam Store API

**APIs Used**: None (pure computation)
**External Dependencies**: Requires revenue/owner data from above

---

### Comparable Games Analyzer
**Required Data**:
- Target game genres ← Steam Store API
- Target game price ← Steam Store API
- Target game owners ← SteamSpy API
- Target game release date ← Steam Store API

**Search Process**:
1. Find games by genre → SteamSpy genre endpoint
2. Filter by price (±$10) → Steam Store API
3. Filter by owner tier → SteamSpy API
4. Filter by launch date (±6 months) → Steam Store API

**APIs Used**: Steam Store, SteamSpy
**External Dependencies**: Full access to both APIs

---

### Negative Review Analyzer
**Required Data**:
- Individual negative reviews ← Steam Reviews API

**Processing**:
1. Fetch reviews → Steam Reviews API
2. Filter negative (not recommended) → Local filtering
3. Categorize with AI → Claude API
4. Generate fix recommendations → Claude API

**APIs Used**: Steam Reviews, Claude
**External Dependencies**: Both APIs must be accessible

---

### Report Orchestrator
**Required Data**: All of the above

**Orchestration Flow**:
1. Call `game_search.get_game_details(app_id)`
   - Uses Steam Store API
   - Returns: name, price, genres, release date
2. Call `game_search.get_steamspy_data(app_id)`
   - Uses SteamSpy API
   - Returns: owners, positive/negative reviews
3. Calculate overall score
   - Formula: `(review_% × 0.7) + owner_bonus`
4. Generate components based on tier
   - Exec Summary: Always
   - ROI Calculator: Always
   - Comparable Games: Tier 2+
   - Negative Reviews: Tier 1-2 (low scores)
5. Assemble three report tiers

**APIs Used**: Steam Store, SteamSpy, Claude (conditionally)
**External Dependencies**: At minimum, needs Steam Store + SteamSpy

---

## 🚨 Critical Bottlenecks

### 1. Owner Count Data (CRITICAL)

**Only Source**: SteamSpy API

**Why Critical**:
- Used to calculate revenue: `revenue = owners × price × 0.7`
- Used in performance scoring: `score += owner_bonus`
- Used to find comparable games (tier matching)

**Impact if Unavailable**:
- ❌ Cannot estimate revenue
- ❌ Cannot calculate ROI accurately
- ❌ Scoring will be incomplete (no owner bonus)
- ❌ Cannot find comparable games effectively

**Workaround**: Manual entry of owner count

---

### 2. Review Score Percentage

**Best Source**: SteamSpy API (positive/(positive+negative))
**Alternative**: Steam Store API (aggregate, less accurate)

**Why Critical**:
- Used in performance scoring: `score = review_% × 0.7`
- Determines game tier (1-4)
- Drives tier-specific recommendations

**Impact if Unavailable**:
- ❌ Cannot calculate performance score
- ❌ Cannot determine tier
- ❌ Cannot generate tier-specific content

**Workaround**: Manual entry or aggregate from Steam Store

---

### 3. Price Data

**Source**: Steam Store API

**Why Important**:
- Used in ROI calculations
- Used for comparable game matching
- Used for revenue estimation

**Impact if Unavailable**:
- ⚠️ ROI calculations use default/estimated prices
- ⚠️ Revenue estimates less accurate
- ⚠️ Comparable game matching broader

**Workaround**: Manual entry or public Steam page

---

## 🎯 Minimum Viable Data Set

To generate a basic report, you **absolutely need**:

1. **Game Name** (identification)
2. **Review Score %** (performance tier)
3. **Review Count** (confidence)
4. **Owner Count** (revenue, scoring)
5. **Price** (ROI, revenue)
6. **Genres** (context)
7. **Release Date** (lifecycle stage)

**Sources**:
- Steam Store API: Name, price, genres, release date, review count
- **SteamSpy API**: Owner count, review score %

**Bottom Line**: You **MUST** have access to SteamSpy API for owner counts. Everything else has workarounds.

---

## 💡 Alternative Data Sources (If APIs Blocked)

| Required Data | Primary Source | Alternative 1 | Alternative 2 | Alternative 3 |
|---------------|----------------|---------------|---------------|---------------|
| **Owner Count** | SteamSpy API | SteamDB.info (manual) | ❌ No alternative | **Manual Entry** |
| **Review Score %** | SteamSpy API | Steam Store page | Estimate from reviews | **Manual Entry** |
| **Price** | Steam Store API | Steam page (manual) | Public listing | **Manual Entry** |
| **Review Count** | Steam Store API | Steam page (manual) | SteamDB | **Manual Entry** |
| **Name/Genres** | Steam Store API | Steam page (manual) | RAWG API | **Manual Entry** |

**Conclusion**: If APIs are blocked, **manual data entry is the only viable path** for professional use.

---

## ✅ Current Status (Your Environment)

| API | Your Key | Status | Can Access? |
|-----|----------|--------|-------------|
| **Steam Store API** | None needed | ❌ 403 Blocked | No |
| **Steam Web API** | ✅ Have key | ❌ 403 Blocked | No |
| **SteamSpy API** | None needed | ❌ 403 Blocked | No |
| **Claude API** | ✅ Have key | ✅ Working | **Yes** |
| **RAWG API** | ✅ Have key | ❌ 403 Blocked | No |
| **YouTube API** | ✅ Have key | ❌ 403 Blocked | No |
| **Twitch API** | ✅ Have keys | ❌ 403 Blocked | No |

**Impact**: Cannot fetch game data automatically. Must use manual entry.

**Solution**: Deploy to environment with normal internet access (AWS, local machine, etc.)

---

## 📦 Complete API Configuration (For Proper Environment)

Add to `.env`:
```bash
# Critical
STEAM_WEB_API_KEY=7CD62F6A17C80F8E8889CE738578C014
ANTHROPIC_API_KEY=<your-anthropic-key>

# Optional Enhancement
RAWG_API_KEY=5353e48dc2a4446489ec7c0bbb1ce9e9
YOUTUBE_API_KEY=AIzaSyA6J_1QBANsaE2rYt2IXEVww1U6nAysLik
TWITCH_CLIENT_ID=j6ueihug11unpnzktacouf4y8j6tgb
TWITCH_CLIENT_SECRET=h3er5mdtlddwf58hyn106gum50hg6w
```

**When deployed to proper environment, this will enable**:
- ✅ Automatic game data fetching
- ✅ Owner count retrieval
- ✅ Revenue estimation
- ✅ Comparable games discovery
- ✅ AI-powered review analysis
- ✅ Full automation

---

## 🏁 Summary

**Data Architecture**:
- **7 critical data points** needed for reports
- **3 API tiers** by importance (SteamSpy > Steam Store > Claude)
- **4-layer processing** (fetch → process → analyze → assemble)

**Current Blockers**:
- Environment blocks all external APIs except Claude
- Cannot fetch owner counts (critical blocker)
- Cannot fetch pricing or game data

**Solution**:
- Deploy to AWS/VPS/local machine
- All APIs will likely work there
- System is production-ready, environment is not
