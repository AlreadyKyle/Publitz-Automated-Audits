# API Integration Test Plan

**Date**: December 9, 2025
**Version**: 1.0
**Purpose**: Validate new API integrations (SteamSpy, RAWG, YouTube, Enhanced Steam)

---

## Test Overview

**New Features Being Tested**:
1. SteamSpy integration - Owner estimates and player data
2. RAWG integration - Metacritic scores and ratings
3. YouTube integration - Video counts and buzz metrics
4. Enhanced Steam Web API - Richer game data
5. Final research refinements in system prompt

**Expected Outcomes**:
- All APIs fetch data successfully
- Data formats correctly in report prompts
- Graceful handling of API failures
- Report quality improves with new data
- No regressions in existing functionality

---

## Test Categories

### 1. Unit Tests - API Clients

#### Test 1.1: SteamSpy Client
```bash
# Test with known Steam game (Hades - 1145360)
python -c "
from src.api_clients import SteamSpyClient
client = SteamSpyClient()
data = client.get_game_data('1145360')
print('Found:', data.get('found'))
print('Owners:', data.get('owners'))
print('Playtime:', data.get('average_playtime'))
"
```

**Expected**:
- `found: True`
- Owner range (e.g., "1,000,000 .. 2,000,000")
- Average playtime > 0

#### Test 1.2: RAWG Client
```bash
# Test with known game (Hades)
python -c "
from src.api_clients import RAWGClient
from config import Config
client = RAWGClient(Config.RAWG_API_KEY)
data = client.search_game('Hades')
print('Found:', data.get('found') if data else False)
print('Metacritic:', data.get('metacritic') if data else 'N/A')
print('Rating:', data.get('rating') if data else 'N/A')
"
```

**Expected**:
- `found: True`
- Metacritic score (93 for Hades)
- RAWG rating (~4.5/5.0)

#### Test 1.3: YouTube Client
```bash
# Test with known game
python -c "
from src.api_clients import YouTubeClient
from config import Config
client = YouTubeClient(Config.YOUTUBE_API_KEY)
data = client.search_game_videos('Hades game', max_results=10)
print('Found:', data.get('found'))
print('Videos:', data.get('video_count'))
print('Views:', data.get('total_views'))
"
```

**Expected**:
- `found: True`
- Video count > 0
- Total views > 0

#### Test 1.4: Enhanced Steam Client
```bash
# Test with known game
python -c "
from src.api_clients import EnhancedSteamClient
from config import Config
client = EnhancedSteamClient(Config.STEAM_WEB_API_KEY)
players = client.get_player_count('1145360')
reviews = client.get_review_details('1145360')
print('Current players:', players)
print('Reviews found:', reviews.get('found'))
print('Positive:', reviews.get('positive_percentage'))
"
```

**Expected**:
- Player count >= 0 (may be 0 if game not running)
- Reviews found: True
- Positive percentage ~90%+ for Hades

---

### 2. Integration Tests - Data Collector

#### Test 2.1: Main Game Data Collection
```bash
# Test enhanced data collection
python -c "
from src.simple_data_collector import SimpleDataCollector
collector = SimpleDataCollector()
game_data = collector._fetch_game_data(
    'https://store.steampowered.com/app/1145360/Hades/',
    '1145360'
)
print('Game:', game_data.get('name'))
print('SteamSpy found:', game_data.get('steamspy', {}).get('found'))
print('RAWG found:', game_data.get('rawg', {}).get('found'))
print('YouTube found:', game_data.get('youtube', {}).get('found'))
"
```

**Expected**:
- Game name: "Hades"
- SteamSpy found: True
- RAWG found: True
- YouTube found: True

#### Test 2.2: Competitor Data Collection
```bash
# Test competitor enrichment
python -c "
from src.simple_data_collector import SimpleDataCollector
collector = SimpleDataCollector()
competitors = collector._fetch_competitors(['Dead Cells'])
if competitors:
    comp = competitors[0]
    print('Competitor:', comp.get('name'))
    print('SteamSpy:', comp.get('steamspy', {}).get('found'))
    print('RAWG:', comp.get('rawg', {}).get('found'))
"
```

**Expected**:
- Competitor: "Dead Cells"
- SteamSpy: True
- RAWG: True

---

### 3. End-to-End Test - Full Audit Generation

#### Test 3.1: Generate Test Audit with New APIs
```bash
# Run full audit generation
python generate_audit.py --test
```

**Expected Flow**:
1. ✅ Phase 1: Input validation
2. ✅ Phase 2: Data collection with new APIs
   - SteamSpy data fetched
   - RAWG data fetched
   - YouTube data fetched
3. ✅ Phase 3: Report generation with enhanced data
4. ✅ Phase 4: PDF and CSV export

**Expected Output Files**:
```
output/test-client/
├── test-client_audit_YYYYMMDD.md
├── test-client_audit_YYYYMMDD.pdf
└── test-client_pricing_YYYYMMDD.csv
```

**Quality Checks**:
- [ ] Markdown contains "SteamSpy Data (Owner Estimates)"
- [ ] Markdown contains "Quality Benchmarks (RAWG/Metacritic)"
- [ ] Markdown contains "YouTube Presence (Community Buzz)"
- [ ] Markdown contains "Competitive Analysis Standards" (new research)
- [ ] Markdown contains "Steam Next Fest Strategy" (new research)
- [ ] Competitor section shows Metacritic scores
- [ ] Competitor section shows owner estimates
- [ ] PDF renders correctly
- [ ] Pricing CSV has PPP warnings

#### Test 3.2: Generate Audit with Real Steam Game
```bash
# Create test for Hades
python generate_audit.py --create-example hades-test
# Edit inputs/hades-test/steam_url.txt to: https://store.steampowered.com/app/1145360/Hades/
echo "https://store.steampowered.com/app/1145360/Hades/" > inputs/hades-test/steam_url.txt
# Edit competitors to similar games
cat > inputs/hades-test/competitors.txt << 'EOF'
Dead Cells
The Binding of Isaac: Rebirth
Enter the Gungeon
Slay the Spire
EOF

# Generate audit
python generate_audit.py --client hades-test
```

**Expected**:
- High-quality data (Hades is well-known)
- Metacritic: 93
- Owner estimates: 1M-2M range
- YouTube: 1000s of videos
- All competitor data enriched

---

### 4. Error Handling Tests

#### Test 4.1: API Failures
```bash
# Test with invalid API keys (temporarily modify config)
# Should gracefully skip APIs and continue
```

**Expected**:
- ⚠️ Warnings shown for failed APIs
- System continues without crashing
- Report still generates with available data

#### Test 4.2: Game Not Found in External APIs
```bash
# Test with very new/obscure game
# Some APIs may not have data
```

**Expected**:
- "Data not available" messages
- No crashes
- Report still generates

#### Test 4.3: Rate Limiting
```bash
# Test with 10+ competitors
# May hit rate limits on YouTube API
```

**Expected**:
- Graceful handling of rate limits
- Appropriate delays between requests
- No crashes

---

### 5. Data Quality Tests

#### Test 5.1: SteamSpy Data Accuracy
```bash
# Manual verification
# Compare SteamSpy owner estimates with known data
```

**Check**:
- Owner ranges are reasonable
- Playtime data makes sense
- Review counts match Steam

#### Test 5.2: RAWG/Metacritic Accuracy
```bash
# Manual verification
# Compare Metacritic scores with actual scores
```

**Check**:
- Metacritic scores match official scores
- Ratings are in correct range (0-100)
- Game names match correctly

#### Test 5.3: YouTube Buzz Metrics
```bash
# Manual verification
# Spot-check video counts
```

**Check**:
- Video counts are plausible
- View counts are reasonable
- Top videos make sense

---

### 6. Performance Tests

#### Test 6.1: Generation Time
```bash
# Measure total generation time
time python generate_audit.py --test
```

**Target**: < 10 minutes total
**Expected Breakdown**:
- Phase 1: < 10s
- Phase 2: ~3-4 minutes (with new APIs)
- Phase 3: ~2-3 minutes
- Phase 4: < 30s

**Acceptable**: Up to 12 minutes (new APIs add ~1-2 min)

#### Test 6.2: API Cost
```bash
# Check Anthropic API dashboard after test
```

**Expected Cost**:
- Claude report: $3-5
- Claude vision: $2-3
- RAWG: Free
- YouTube: Free (within quota)
- SteamSpy: Free
- Steam Web API: Free
- **Total**: $5-8 per report (same as before)

---

### 7. Report Quality Tests

#### Test 7.1: New Data Sections Present
```bash
# Check generated markdown
grep -A 5 "SteamSpy Data" output/test-client/*.md
grep -A 5 "Quality Benchmarks" output/test-client/*.md
grep -A 5 "YouTube Presence" output/test-client/*.md
```

**Expected**:
- All three sections present
- Data formatted correctly
- No "Data not available" for well-known games

#### Test 7.2: Competitive Analysis Enhanced
```bash
# Check competitor sections
grep -A 10 "Competitor 1:" output/test-client/*.md
```

**Expected**:
- Metacritic scores shown
- Owner estimates shown
- Richer competitive context

#### Test 7.3: New Research Refinements Applied
```bash
# Check for new methodologies
grep "Unit Calculation" output/test-client/*.md
grep "Steam Next Fest" output/test-client/*.md
grep "10-20 competitors" output/test-client/*.md
```

**Expected**:
- Unit calculation formula present
- Next Fest emphasized as pinnacle event
- Competitive analysis standards mentioned

---

## Test Execution Log

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| 1.1 | SteamSpy Client | ⏳ | |
| 1.2 | RAWG Client | ⏳ | |
| 1.3 | YouTube Client | ⏳ | |
| 1.4 | Enhanced Steam Client | ⏳ | |
| 2.1 | Main Game Data Collection | ⏳ | |
| 2.2 | Competitor Data Collection | ⏳ | |
| 3.1 | Full Audit Generation (Test) | ⏳ | |
| 3.2 | Full Audit Generation (Hades) | ⏳ | |
| 4.1 | API Failures | ⏳ | |
| 4.2 | Game Not Found | ⏳ | |
| 4.3 | Rate Limiting | ⏳ | |
| 5.1 | SteamSpy Accuracy | ⏳ | |
| 5.2 | RAWG Accuracy | ⏳ | |
| 5.3 | YouTube Accuracy | ⏳ | |
| 6.1 | Generation Time | ⏳ | |
| 6.2 | API Cost | ⏳ | |
| 7.1 | New Data Sections | ⏳ | |
| 7.2 | Competitive Analysis | ⏳ | |
| 7.3 | Research Refinements | ⏳ | |

---

## Success Criteria

**Must Pass**:
- ✅ All API clients fetch data without crashing
- ✅ Data formats correctly in reports
- ✅ Full audit generates successfully
- ✅ No regressions in existing functionality
- ✅ Generation time < 12 minutes
- ✅ API cost < $10 per report

**Quality Goals**:
- ✅ New data sections enhance report value
- ✅ Competitive analysis more comprehensive
- ✅ Research refinements improve actionability
- ✅ Client receives $1,500+ value (up from $1,000)

---

## Bug Tracking

| Bug ID | Description | Severity | Status | Fix |
|--------|-------------|----------|--------|-----|
| | | | | |

---

## Test Execution Notes

_Add notes here as tests are run_

---

**Test Plan Version**: 1.0
**Last Updated**: December 9, 2025
**Next Review**: After first test run
