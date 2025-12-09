# API Configuration - Final Setup

**Last Updated**: 2025-11-24
**System**: Publitz Automated Game Audits

---

## Overview

This document lists all APIs used by the system, their requirements, costs, and configuration.

---

## ✅ CRITICAL APIs (Required for Core Functionality)

### 1. Steam Store API

**Purpose**: Basic game information (name, price, description, genres, release date)
**Cost**: **FREE**
**API Key Required**: No
**Rate Limit**: ~200 requests per 5 minutes
**Documentation**: https://wiki.teamfortress.com/wiki/User:RJackson/StorefrontAPI

**Endpoints Used**:
```
GET https://store.steampowered.com/api/appdetails?appids={appid}
```

**Configuration**: None needed - works out of the box

---

### 2. SteamSpy API

**Purpose**: **Owner counts** (ONLY reliable source for this critical data)
**Cost**: **FREE**
**API Key Required**: No
**Rate Limit**: 1 request per minute for bulk endpoints, faster for individual apps
**Documentation**: https://steamspy.com/api.php

**Endpoints Used**:
```
GET https://steamspy.com/api.php?request=appdetails&appid={appid}
GET https://steamspy.com/api.php?request=genre&genre={genre}
GET https://steamspy.com/api.php?request=tag&tag={tag}
```

**Configuration**: None needed - works out of the box

**CRITICAL NOTE**: This is the ONLY public API that provides owner count estimates. Without this, revenue calculations are impossible.

---

### 3. Steam Reviews API

**Purpose**: Individual reviews for sentiment analysis and complaint categorization
**Cost**: **FREE**
**API Key Required**: No
**Rate Limit**: Standard Steam API limits
**Documentation**: Part of Steam Store API

**Endpoints Used**:
```
GET https://store.steampowered.com/appreviews/{appid}?json=1&filter=recent&num_per_page=100
GET https://store.steampowered.com/appreviews/{appid}?json=1&filter=all&review_type=negative
```

**Configuration**: None needed - works out of the box

---

## ⭐ RECOMMENDED APIs (Highly Valuable)

### 4. Steam Web API

**Purpose**: Additional official endpoints (app lists, player stats, news)
**Cost**: **FREE**
**API Key Required**: **YES** (free to obtain)
**Rate Limit**: 100,000 requests/day
**Get Key**: https://steamcommunity.com/dev/apikey

**Current Key**: `7CD62F6A17C80F8E8889CE738578C014`

**Endpoints Used**:
```
GET https://api.steampowered.com/ISteamApps/GetAppList/v2/?key={key}
GET https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid={appid}&key={key}
GET https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}
```

**Configuration**:
```bash
# In .env file
STEAM_WEB_API_KEY=7CD62F6A17C80F8E8889CE738578C014
```

---

### 5. Anthropic/Claude API

**Purpose**: AI-powered review categorization and sentiment analysis
**Cost**: **PAID** (~$0.015 per 1K input tokens, ~$0.075 per 1K output tokens)
**API Key Required**: **YES**
**Rate Limit**: Depends on plan (starter: 50 requests/minute)
**Get Key**: https://console.anthropic.com/

**Current Key**: Set in environment variables

**Model Used**: `claude-sonnet-4-20250514`

**What It Does**:
- Categorizes negative reviews into actionable complaint types
- Assesses salvageability for struggling games
- Provides intelligent insights beyond simple keyword matching

**Configuration**:
```bash
# In .env file
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

**Cost Estimate**: ~$0.05-0.15 per report (analyzing 100 reviews)

**NOTE**: This is your **competitive differentiator**. Basic sentiment analysis can be done with free tools, but Claude provides human-quality categorization.

---

## 🔧 OPTIONAL APIs (Supplementary Data)

### 6. SteamCharts

**Purpose**: Historical player count data
**Cost**: **FREE**
**API Key Required**: No (web scraping)
**Rate Limit**: Be respectful (1 request per 2-3 seconds)
**Website**: https://steamcharts.com/

**Access Method**: Web scraping with BeautifulSoup

**Configuration**:
```python
import requests
from bs4 import BeautifulSoup

url = f"https://steamcharts.com/app/{appid}"
response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})
```

**Use Case**: Trend analysis, showing if player count is growing/declining

---

## ❌ REMOVED APIs (Not Needed for Steam Analysis)

### RAWG API
- **Removed**: Not essential for Steam-specific analysis
- **Alternative**: Steam Store API provides sufficient game metadata

### YouTube API
- **Removed**: Not essential for core audit functionality
- **Alternative**: Manual YouTube searches if needed for marketing analysis

### Twitch API
- **Removed**: Not essential for core audit functionality
- **Alternative**: Manual Twitch searches if needed for visibility analysis

---

## Environment Variables Setup

Create/update your `.env` file:

```bash
# ============================================================================
# CRITICAL APIs
# ============================================================================
# (None - Steam Store, SteamSpy, and Steam Reviews require no keys)

# ============================================================================
# RECOMMENDED APIs
# ============================================================================

# Steam Web API (FREE - get from https://steamcommunity.com/dev/apikey)
STEAM_WEB_API_KEY=your_steam_web_api_key_here

# Anthropic Claude API (PAID - your competitive differentiator)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# ============================================================================
# OPTIONAL APIs (Removed from core system)
# ============================================================================
# RAWG_API_KEY=your_rawg_key_here  # Not needed for core functionality
# YOUTUBE_API_KEY=your_youtube_key_here  # Not needed for core functionality
# TWITCH_CLIENT_ID=your_twitch_client_id_here  # Not needed for core functionality
# TWITCH_CLIENT_SECRET=your_twitch_secret_here  # Not needed for core functionality
```

---

## Testing Your Configuration

### Quick Health Check

```bash
python diagnostics/api_health_check.py
```

This will:
1. Test all critical APIs
2. Test recommended APIs
3. Test optional APIs
4. Generate a detailed report showing what's working
5. Save results to `diagnostics/api_health_report.txt`

**Expected Output**:
```
✓ Steam Store API - PASS (234ms)
✓ Steam Web API - PASS (156ms)
✓ SteamSpy API - PASS (891ms)
✓ Steam Reviews API - PASS (445ms)
✓ Anthropic/Claude API - PASS (1234ms)
✓ SteamCharts - PASS (678ms)

SYSTEM READY - All critical APIs operational
```

---

## Cost Analysis

### Per Report Costs

| API | Cost per Report | Notes |
|-----|-----------------|-------|
| Steam Store API | $0.00 | Free, unlimited |
| SteamSpy API | $0.00 | Free, unlimited |
| Steam Reviews API | $0.00 | Free, unlimited |
| Steam Web API | $0.00 | Free (100K/day limit) |
| Claude API | $0.05-0.15 | ~100 reviews analyzed |
| **TOTAL** | **$0.05-0.15** | **Very affordable** |

### Monthly Costs (100 reports)

- **100 reports/month**: $5-15/month in Claude API costs
- All Steam APIs: $0
- **Total**: $5-15/month

**ROI**: If you charge $50-200 per audit report, your API costs are 0.25-7.5% of revenue.

---

## Rate Limiting Best Practices

### Steam Store API
```python
import time
time.sleep(1.5)  # 1.5 seconds between requests
```

### SteamSpy API
```python
import time
time.sleep(1.0)  # 1 second between requests
```

### SteamCharts (Scraping)
```python
import time
time.sleep(2.0)  # 2 seconds between requests (be respectful)
```

### Claude API
- No explicit delays needed (has generous rate limits)
- Batch requests where possible to reduce costs

---

## Troubleshooting

### "403 Forbidden" Errors

**Cause**: Network/firewall blocking outbound HTTP requests

**Solutions**:
1. Run from a different environment (AWS, local machine, VPS)
2. Check firewall settings
3. Try from home network instead of corporate network

### "SteamSpy returns empty data"

**Cause**: SteamSpy has rate limits or temporary outages

**Solutions**:
1. Add retry logic with exponential backoff
2. Cache results to reduce requests
3. Wait 1-2 minutes between failed requests

### "Claude API too expensive"

**Solutions**:
1. Reduce review count (analyze top 50 instead of 100)
2. Use Claude Haiku model (cheaper) for simple categorization
3. Cache complaint categories for similar games
4. Only use Claude for tier 2/3 reports, not tier 1

---

## Final Configuration Checklist

- [ ] `.env` file created with Steam Web API key
- [ ] `.env` file has Anthropic API key
- [ ] Run `python diagnostics/api_health_check.py` - all critical APIs pass
- [ ] Test report generation with `python demo_report_generation.py`
- [ ] Verify no API costs are in client reports (only in your diagnostic logs)
- [ ] Set up monitoring to run health check daily

---

## Support & Documentation

- **Steam API Docs**: https://steamcommunity.com/dev
- **SteamSpy Docs**: https://steamspy.com/about
- **Anthropic Docs**: https://docs.anthropic.com/
- **Your Diagnostics**: `diagnostics/api_health_check.py`
- **Your Tests**: `test_api_verification.py`

---

## Conclusion

**You need 2 API keys total:**
1. Steam Web API key (free) - already have: `7CD62F6A17C80F8E8889CE738578C014`
2. Anthropic API key (paid) - already configured

**Total monthly cost**: $5-15 for Claude API (if generating 100 reports)

**Everything else is FREE and requires NO keys.**

This is an extremely cost-effective setup for a professional audit service.
