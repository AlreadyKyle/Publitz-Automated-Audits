# Strategic Audit: Data Source Analysis & Solutions

**Date:** November 20, 2025
**Problem:** Streamlit Cloud IPs are completely blocked by Steam and SteamSpy APIs
**Goal:** Get accurate, recent Steam game data for audit reports

---

## Current Situation

### Confirmed Blocks
Testing shows **complete IP-based blocking** from Streamlit Cloud infrastructure:
- ❌ SteamSpy API: `Access denied`
- ❌ Steam Store API: `Access denied`
- ❌ Steam Review API: `Access denied`
- ❌ Steam Store Pages (HTML): `Access denied`

This is infrastructure-level blocking, not fixable with User-Agent headers or cookies.

---

## Data Requirements Analysis

### Critical Data Points Needed:
1. **Reviews** (count, positive/negative, score) - ESSENTIAL
2. **Ownership estimates** (min/max range) - ESSENTIAL
3. **Price** - ESSENTIAL
4. **Game metadata** (name, dev, publisher, tags, genres) - ESSENTIAL
5. **Revenue estimates** - DERIVED (can calculate from #1-3)
6. **Playtime stats** (median/average) - NICE TO HAVE
7. **Concurrent players** - NICE TO HAVE

### Current Data Flow:
```
User Input (Steam URL)
  → Extract app_id
  → Try Alternative Source (Steam store scraping) → BLOCKED
  → Try SteamSpy API → BLOCKED
  → Fallback to placeholder data → ⚠️ INACCURATE
```

---

## Alternative Data Sources Research

### 1. **RAWG API** 🟡 Partial Solution
**URL:** https://rawg.io/apidocs
**Free Tier:** 20,000 requests/month
**Registration:** Required (free API key)

**Pros:**
- ✅ Free with decent limits
- ✅ Has Steam playtime data
- ✅ Has Metacritic ratings, genres, tags
- ✅ Has release dates, descriptions
- ✅ 350,000+ games in database

**Cons:**
- ❌ **NO ownership data**
- ❌ **NO review count data**
- ❌ **NO revenue data**
- ⚠️ Only aggregated ratings, not Steam-specific scores

**Verdict:** Can supplement metadata but **cannot replace SteamSpy** for core metrics.

---

### 2. **IGDB API** 🟡 Partial Solution
**URL:** https://www.igdb.com/api
**Free Tier:** Unknown limits
**Registration:** Required

**Pros:**
- ✅ Comprehensive game database
- ✅ Has Steam integration
- ✅ Has ratings and metadata

**Cons:**
- ❌ **NO ownership data**
- ❌ **NO review count data**
- ❌ Requires API key setup

**Verdict:** Similar to RAWG - good for metadata, not for sales/ownership data.

---

### 3. **Steam Web API (Official)** 🔴 Not Viable
**URL:** https://steamcommunity.com/dev
**Free Tier:** Free with Steam account
**Registration:** Required (API key)

**Pros:**
- ✅ Official Steam data
- ✅ Has appdetails endpoint for game info
- ✅ Free to use

**Cons:**
- ❌ **NO ownership/sales data** (only available to game developers for their own games)
- ❌ **NO revenue data**
- ⚠️ Likely ALSO blocked on Streamlit Cloud

**Verdict:** Not a solution for ownership estimates.

---

### 4. **Proxy Services** 🟢 Technical Solution
**Services:** ScraperAPI, ScrapingBee, Bright Data
**Cost:** $50-200/month for reasonable limits

**Pros:**
- ✅ Bypasses IP blocks reliably
- ✅ Handles CAPTCHAs automatically
- ✅ Rotates IPs to avoid detection
- ✅ Would work with existing code

**Cons:**
- ❌ **Costs money** (~$50-100/month minimum)
- ❌ Adds latency (routing through proxy)
- ❌ May violate Steam's Terms of Service

**Verdict:** Would work but adds cost and complexity.

---

### 5. **SteamDB** 🔴 Not Accessible
**URL:** https://steamdb.info/
**Has Data:** Yes, comprehensive Steam stats

**Pros:**
- ✅ Has all the data we need
- ✅ Updated in real-time

**Cons:**
- ❌ **No public API** for programmatic access
- ❌ Would require scraping (likely blocked too)

**Verdict:** Not feasible without API.

---

### 6. **Kaggle/Static Datasets** 🟡 Outdated Backup
**Availability:** Free Steam datasets on Kaggle

**Pros:**
- ✅ Free to download
- ✅ No API limits
- ✅ Large coverage

**Cons:**
- ❌ **Static/outdated** (not real-time)
- ❌ Would need manual updates
- ❌ Not suitable for live audit reports

**Verdict:** Only useful as last-resort fallback.

---

## Recommended Solutions

### 🥇 **OPTION A: User-Provided Steam API Key** (BEST)

**Implementation:**
1. Add optional field for Steam Web API key in UI
2. If provided, use official Steam API for game metadata
3. Still need SteamSpy for ownership (blocked)
4. Fall back to improved estimation algorithms

**Pros:**
- ✅ Free for users
- ✅ Official data source
- ✅ No rate limits (user's key)
- ✅ Easy to implement

**Cons:**
- ⚠️ Still doesn't solve ownership/review count issue
- ⚠️ Users need to register for API key (friction)
- ⚠️ Steam API might also be IP-blocked on Streamlit Cloud

**Effort:** 2-3 hours
**Cost:** $0

---

### 🥈 **OPTION B: Hybrid Multi-Source Approach** (RECOMMENDED)

**Implementation:**
```python
def get_game_data(app_id):
    # Priority 1: Try Steam store scraping (if not blocked)
    try:
        data = scrape_steam_store_page(app_id)
        if data['reviews_total'] > 0:
            return data
    except: pass

    # Priority 2: Try Steam Web API (if user provided key)
    if user_has_api_key:
        try:
            metadata = get_steam_api_data(app_id, user_key)
            # Estimate ownership from Metacritic/RAWG data
            ownership = estimate_from_ratings(metadata)
            return merge(metadata, ownership)
        except: pass

    # Priority 3: Try RAWG API for metadata
    try:
        rawg_data = get_rawg_data(game_name)
        # Estimate ownership from playtime/ratings
        ownership = estimate_from_rawg(rawg_data)
        return rawg_data + ownership
    except: pass

    # Priority 4: Improved fallback with better estimates
    return intelligent_fallback(app_id, game_name)
```

**Key Innovation: Smart Ownership Estimation**
```python
def estimate_owners_from_alternatives(data):
    """
    Use multiple signals to estimate ownership:
    - Metacritic score + review count correlation
    - RAWG ratings + playtime data
    - Genre/tag benchmarks
    - Release date (time decay factor)
    """
    # Industry ratios:
    # - High-rated indie: 50K-500K typical
    # - AAA with 90+ Metacritic: 1M-10M typical
    # - F2P with high playtime: 10M+ possible

    base_estimate = calculate_from_ratings_and_genre(data)
    adjusted = apply_confidence_intervals(base_estimate, data['signals'])
    return {
        'owners_min': adjusted * 0.5,
        'owners_max': adjusted * 2.0,
        'owners_avg': adjusted,
        'confidence': 'estimated',
        'method': 'multi-signal_analysis'
    }
```

**Pros:**
- ✅ Multiple fallbacks increase success rate
- ✅ Combines best of each source
- ✅ Transparent about estimation methods
- ✅ Still provides value even when primary sources fail

**Cons:**
- ⚠️ More complex code
- ⚠️ Estimates may be less accurate
- ⚠️ Requires multiple API keys (RAWG, Steam)

**Effort:** 8-12 hours
**Cost:** $0 (free API tiers)

---

### 🥉 **OPTION C: Proxy Service Integration** (WORKS BUT COSTS)

**Implementation:**
1. Sign up for ScraperAPI or ScrapingBee
2. Route all Steam requests through proxy
3. Use existing code with minimal changes

**Example:**
```python
import requests

SCRAPER_API_KEY = os.getenv('SCRAPER_API_KEY')

def get_via_proxy(url):
    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
    return requests.get(proxy_url).text
```

**Pros:**
- ✅ **Would definitely work**
- ✅ Minimal code changes
- ✅ Handles all blocking automatically
- ✅ Reliable and fast

**Cons:**
- ❌ **Costs $50-200/month**
- ❌ Adds dependency on third-party service
- ❌ May violate Steam ToS (risky)

**Effort:** 2-4 hours
**Cost:** $50-200/month ongoing

---

### 🔧 **OPTION D: Deploy Own Proxy on Different Cloud** (TECHNICAL)

**Implementation:**
1. Deploy simple proxy server on AWS/GCP/DigitalOcean
2. Route Steam requests through own proxy
3. Different IP range = not blocked

**Architecture:**
```
Streamlit Cloud App
  ↓ (HTTPS request)
Your Proxy Server (AWS/GCP)
  ↓ (appears as different IP)
Steam/SteamSpy APIs
  ↓ (returns data)
```

**Pros:**
- ✅ Full control over proxy
- ✅ Relatively cheap ($5-10/month)
- ✅ Would definitely work
- ✅ Can optimize for this use case

**Cons:**
- ❌ Requires DevOps setup
- ❌ Need to maintain server
- ❌ Some ongoing cost
- ❌ May still violate Steam ToS

**Effort:** 6-8 hours (setup + maintenance)
**Cost:** $5-10/month

---

## Immediate Action Plan

### 🚀 **Phase 1: Quick Wins (2-4 hours)**

1. **Improve Fallback Estimates**
   - Use game name to look up on RAWG (metadata)
   - Apply genre-based benchmarks for ownership estimates
   - Use Metacritic scores as quality signal
   - Make estimation method transparent in report

2. **Add Better Error Messages**
   - Show exact error (IP blocked, timeout, etc.)
   - Suggest user actions (try different game, wait, etc.)
   - Add link to explanation of data sources

3. **Test Different Endpoints**
   - Try steamcommunity.com instead of store.steampowered.com
   - Try different SteamSpy endpoints
   - Document which ones work

**Result:** App works with better estimates, users understand limitations

---

### 🎯 **Phase 2: Multi-Source Integration (1-2 days)**

1. **Integrate RAWG API**
   - Add RAWG API key to environment
   - Fetch metadata from RAWG as backup
   - Use playtime data for engagement estimates

2. **Add Steam Web API Support (Optional)**
   - Allow users to provide their own Steam API key
   - Fetch official metadata when available
   - Fall back gracefully if not provided

3. **Smart Ownership Estimation Algorithm**
   - Build model based on genre, ratings, playtime
   - Use multiple signals for confidence intervals
   - Clearly label as "estimated" vs "reported"

**Result:** Higher success rate, better data quality, transparent methodology

---

### 💡 **Phase 3: Premium Features (Optional)**

1. **Proxy Integration (Paid)**
   - Add ScraperAPI for users who want 100% accurate data
   - Make it optional upgrade ($10/month per user?)
   - Market as "Premium Accurate Mode"

2. **Cached Data Layer**
   - Cache successful API calls in database
   - Serve cached data when APIs are blocked
   - Update cache when possible
   - Show data freshness in report

**Result:** Path to monetization, better UX for serious users

---

## Recommended Path Forward

### 🎯 **MY RECOMMENDATION: Start with Phase 1 + Phase 2**

**Week 1: Improve Current System**
1. ✅ Better fallback estimation algorithm (4 hours)
2. ✅ Integrate RAWG API for metadata (3 hours)
3. ✅ Improve error handling and messaging (2 hours)
4. ✅ Add data source transparency to reports (1 hour)

**Week 2: Test and Optimize**
1. Test with 20-30 different games
2. Fine-tune estimation algorithms
3. Document accuracy vs. real data
4. Gather user feedback

**Week 3: Optional Enhancements**
1. Add Steam API key support
2. Consider proxy service for premium tier
3. Build cache layer if needed

---

## Success Metrics

**Current State:**
- ❌ 0% success rate fetching real data
- ⚠️ 100% fallback rate (inaccurate estimates)
- ❌ Poor user experience (hanging, wrong data)

**After Phase 1:**
- 🎯 0% API success (still blocked)
- ✅ 100% fallback rate BUT better estimates
- ✅ Clear communication about data sources
- ✅ Fast failure instead of hanging

**After Phase 2:**
- 🎯 30-50% partial data from RAWG
- ✅ Intelligent estimates for ownership
- ✅ Multi-source verification
- ✅ Confidence scores for each data point

**After Phase 3 (Optional):**
- 🎯 90%+ success with proxy service
- ✅ Near-perfect accuracy
- ✅ Premium tier monetization
- ✅ Cached data for speed

---

## Technical Implementation Notes

### RAWG API Integration
```python
# Add to requirements.txt
# (nothing needed - just requests)

# Add to environment variables
RAWG_API_KEY=<get from https://rawg.io/apidocs>

# Usage example
def get_rawg_data(game_name):
    url = "https://api.rawg.io/api/games"
    params = {
        'key': os.getenv('RAWG_API_KEY'),
        'search': game_name,
        'page_size': 1
    }
    response = requests.get(url, params=params)
    return response.json()['results'][0] if response.ok else None
```

### Smart Estimation Algorithm
```python
def estimate_ownership_intelligent(game_data):
    """
    Multi-signal ownership estimation

    Signals used:
    1. Metacritic score (quality indicator)
    2. Genre (benchmark ranges)
    3. Release year (decay factor)
    4. Playtime stats (engagement proxy)
    5. Rating count on RAWG (popularity proxy)
    """
    # Genre benchmarks (median ownership by genre)
    GENRE_BENCHMARKS = {
        'action': 200000,
        'indie': 50000,
        'rpg': 150000,
        'strategy': 80000,
        'mmo': 1000000,
        'casual': 100000,
    }

    # Start with genre baseline
    genre = game_data.get('genre', 'indie').lower()
    base_estimate = GENRE_BENCHMARKS.get(genre, 100000)

    # Adjust for quality (Metacritic score)
    metacritic = game_data.get('metacritic', 75)
    if metacritic >= 90:
        base_estimate *= 3.0  # Exceptional games sell 3x
    elif metacritic >= 85:
        base_estimate *= 2.0
    elif metacritic >= 80:
        base_estimate *= 1.5
    elif metacritic < 70:
        base_estimate *= 0.5

    # Adjust for age (newer games have lower cumulative sales)
    release_year = game_data.get('released', '2020')[:4]
    years_old = 2025 - int(release_year)
    age_factor = min(1.0 + (years_old * 0.2), 2.5)  # Cap at 2.5x
    base_estimate *= age_factor

    # Adjust for engagement (high playtime = dedicated players)
    playtime = game_data.get('playtime', 0)
    if playtime > 50:
        base_estimate *= 1.3  # High engagement games

    # Adjust for RAWG ratings count (popularity signal)
    ratings_count = game_data.get('ratings_count', 0)
    if ratings_count > 10000:
        base_estimate *= 2.0
    elif ratings_count > 5000:
        base_estimate *= 1.5

    # Create confidence range
    return {
        'owners_min': int(base_estimate * 0.4),
        'owners_max': int(base_estimate * 2.5),
        'owners_avg': int(base_estimate),
        'confidence': 'medium',
        'method': 'multi_signal_estimation',
        'signals_used': ['genre', 'metacritic', 'age', 'playtime', 'ratings']
    }
```

---

## Conclusion

**The harsh reality:** Streamlit Cloud IPs are completely blocked by Steam. No amount of header manipulation will fix this.

**The pragmatic solution:** Build a robust multi-source system with intelligent estimation algorithms and transparent data sourcing.

**The path forward:**
1. ✅ Implement Phase 1 (improved fallbacks) → 10 hours
2. ✅ Implement Phase 2 (RAWG integration + smart estimates) → 16 hours
3. 🤔 Consider Phase 3 (proxy service) → if users demand perfect accuracy

**Expected outcome:** Reports that work 100% of the time with clear indication of data quality and methodology.

