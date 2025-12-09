# Publitz Automated Audits - Complete User Guide

**The ONLY guide you need to read** ✨

---

## What This System Does

Generates professional $1,500 Steam game audit reports in 10 minutes:
- 4 simple input files → 35-45 page PDF report + pricing CSV
- Owner estimates, Metacritic scores, YouTube buzz metrics
- Research-backed recommendations
- Customer-ready deliverable

**Cost**: $5-8 per report (Claude API only, all other APIs free)

---

## 🚀 Quick Start (First Time - Mac Users)

### Step 1: Pull Latest Changes (GitHub Desktop)

1. Open **GitHub Desktop**
2. Click **"Fetch origin"** (top button)
3. If you see a branch called `claude/final-docs-merge...`:
   - Click **"Current Branch"** dropdown
   - Select the `claude/final-docs-merge...` branch
   - Click **"Branch"** menu → **"Merge into Current Branch..."**
   - Select **"main"** and click **"Merge"**
   - Click **"Push origin"** button
   - Delete the old branch: **Branch** menu → **Delete**
4. Make sure you're on the **"main"** branch

### Step 2: Setup (One Time Only)

**Double-click this file**: `SETUP.command`

This will:
- Create a virtual environment
- Install all dependencies
- Take 2-3 minutes

### Step 3: Run Test

**Double-click this file**: `RUN_TEST.command`

This will:
- Generate a test report for the game "Hades"
- Take about 10 minutes
- Open the output folder when done

✅ **If you see a PDF and CSV file, you're ready to go!**

---

## 📊 How to Generate Client Audits (Mac Users)

### Step 1: Create Client Folder

**Double-click**: `CREATE_CLIENT.command`

- Enter client name (lowercase, no spaces)
- Example: `awesome-studio`
- The folder will open automatically

### Step 2: Fill in the 4 Files

The client folder has 4 files to edit (just double-click to open):

1. **steam_url.txt** - Paste the Steam store URL
2. **competitors.txt** - List 5-10 competitor games
3. **intake_form.json** - Fill in client info
4. **strategy_notes.txt** - Paste your call notes

### Step 3: Generate Report

**Double-click**: `GENERATE_AUDIT.command`

- Enter the client name
- Wait 10 minutes
- Output folder opens automatically

### Step 4: Deliver to Client

Send these 2 files:
- `client-name_audit_YYYYMMDD.pdf`
- `client-name_pricing_YYYYMMDD.csv`

**Done!** 🎉

---

## 🖥️ Terminal Users (Advanced)

### 2. Verify API Key is Set

Your `.env` file is already configured:

```bash
cat .env
```

Should show:
```
ANTHROPIC_API_KEY="sk-ant-api03-..." ✅
RAWG_API_KEY="..." ✅
YOUTUBE_API_KEY="..." ✅
STEAM_WEB_API_KEY="..." ✅
```

### 3. Run Test

```bash
python generate_audit.py --test
```

**Expected output** (9-12 minutes):
```
📊 DATA COLLECTION PHASE
[1/4] Fetching main game data...
  - Fetching SteamSpy data... ✅
  - Fetching RAWG data (Metacritic)... ✅ (Metacritic: 93)
  - Fetching YouTube data... ✅ (250 videos, 5,000,000 views)
✅ Loaded: Hades

[2/4] Fetching 5 competitors...
  [1/5] Dead Cells...
    ✅ Loaded with enhanced data
...

✅ DATA COLLECTION COMPLETE

🤖 REPORT GENERATION PHASE
✅ Report generation complete (2-3 minutes)

📄 PDF EXPORT
✅ PDF export complete: test-client_audit_20251209.pdf

💰 PRICING CSV
✅ Pricing CSV generated: test-client_pricing_20251209.csv

✅ COMPLETE!
```

**Check output**:
```bash
ls -lh output/test-client/
```

You should see:
- `test-client_audit_YYYYMMDD.pdf` (300-500 KB)
- `test-client_pricing_YYYYMMDD.csv` (5-10 KB)

---

## How to Generate Audits

### Step 1: Create Client Folder

```bash
python generate_audit.py --create-example client-name
```

This creates:
```
inputs/client-name/
├── steam_url.txt
├── competitors.txt
├── intake_form.json
└── strategy_notes.txt
```

### Step 2: Fill in the 4 Files

#### File 1: `steam_url.txt`
```
https://store.steampowered.com/app/12345/Game_Name/
```

#### File 2: `competitors.txt`
```
# One per line (names or URLs)
Hades
Dead Cells
https://store.steampowered.com/app/588650/Dead_Cells/
The Binding of Isaac: Rebirth
Enter the Gungeon
```

#### File 3: `intake_form.json`
```json
{
  "client_name": "Studio Name",
  "client_email": "contact@studio.com",
  "game_name": "Game Title",
  "launch_date": "2025-06-15",
  "target_price": 19.99,
  "main_concerns": "Pricing, visibility, launch timing",
  "marketing_budget": "Limited (<$5K)",
  "team_size": 3,
  "development_stage": "Pre-launch",
  "wishlist_count": 2500
}
```

#### File 4: `strategy_notes.txt`
```
Strategy Call Notes - [Date]

Client Emotional State: [Anxious/Confident/Burned out/etc.]

Key Concerns:
- [Specific concern 1]
- [Specific concern 2]

Additional Context:
- [Team dynamics, budget, timeline, etc.]

Target Audience:
- [Age range, interests, favorite games]
```

### Step 3: Generate Report

```bash
python generate_audit.py --client client-name
```

**Generation time**: 9-12 minutes
**Output location**: `output/client-name/`

### Step 4: Deliver to Client

**Files to send**:
1. `client-name_audit_YYYYMMDD.pdf` - The full report
2. `client-name_pricing_YYYYMMDD.csv` - Regional pricing (upload to Steam)

**That's it!** No other steps needed.

---

## What You Get in Reports

### New Enhanced Features (Added Dec 2025)

#### 1. Owner Estimates (SteamSpy)
```markdown
**SteamSpy Data:**
- Owner Range: 1,000,000 .. 2,000,000
- Players (Total): 1,500,000
- Average Playtime: 22h 15m
```

#### 2. Metacritic Scores (RAWG)
```markdown
**Quality Benchmarks:**
- Metacritic Score: 93/100
- RAWG Rating: 4.6/5.0
```

#### 3. YouTube Buzz Metrics
```markdown
**YouTube Presence:**
- Video Count: 1,250 videos
- Total Views: 25,000,000
- Buzz Level: 🟢 HIGH
```

#### 4. Enhanced Competitive Analysis
- 10-20 competitors with full data
- Owner estimates for each
- Metacritic scores
- Market tier classification

#### 5. Research-Backed Recommendations
- Unit calculation formulas
- Steam Next Fest strategy
- Content timing precision
- PPP pricing audit (flags 20-56% overpricing)

---

## Troubleshooting

### "No module named 'anthropic'"
```bash
pip install -r requirements.txt
```

### "ANTHROPIC_API_KEY not set"
Check `.env` file exists and has your key:
```bash
cat .env | grep ANTHROPIC_API_KEY
```

### PDF Not Generating
```bash
# Install PDF dependencies
pip install weasyprint
```

### Generation Takes Too Long (>15 min)
- **Normal**: 9-12 minutes with new APIs
- **Slow internet**: May add 2-3 minutes
- **Too many competitors**: Limit to 5-10 in competitors.txt

### API Data Not Showing

**Check APIs are working**:
```bash
python3 -c "
from src.api_clients import SteamSpyClient
client = SteamSpyClient()
data = client.get_game_data('1145360')  # Hades
print('SteamSpy found:', data.get('found'))
"
```

**Normal cases where APIs return no data**:
- SteamSpy: Game not released yet
- RAWG: Game not in database
- YouTube: No videos found (indicates marketing gap!)

---

## Tips & Best Practices

### For Best Report Quality

**DO**:
- ✅ Take detailed strategy call notes
- ✅ Choose relevant competitors (same genre/scope)
- ✅ Complete all intake form fields
- ✅ Note client's emotional state

**DON'T**:
- ❌ Use placeholder data ("TBD", "Unknown")
- ❌ Choose random/unrelated competitors
- ❌ Skip strategy notes (critical for tone)

### Choosing Competitors

**Good**: Same genre, similar price point, similar scope
```
# For roguelike deckbuilder at $19.99
Slay the Spire
Monster Train
Inscryption
```

**Bad**: Different genres, wrong scope
```
# Don't do this
The Witcher 3 (AAA, different genre)
Minecraft (different scope)
```

### Pricing Strategy

The system generates a CSV with:
- 50+ countries
- Regional pricing tiers
- **PPP audit warnings** (flags overpricing)

**⚠️ Important**: If you see PPP warnings, manually reduce prices in those regions for better conversion.

---

## API Quotas & Costs

### Daily Limits

- **YouTube**: 200 audits/day (10K units quota)
- **RAWG**: 5,000 audits/month (20K requests)
- **SteamSpy**: Unlimited
- **Steam Web API**: Unlimited

### Cost Per Audit

- **Claude AI**: $5-8
- **All other APIs**: $0 (free tier)
- **Total**: $5-8 per report

**Budget**: ~$10/audit to be safe

---

## Advanced Usage

### Test with Real Game (Hades)

```bash
# Create test
python generate_audit.py --create-example hades-test

# Set Steam URL
echo "https://store.steampowered.com/app/1145360/Hades/" > inputs/hades-test/steam_url.txt

# Set competitors
cat > inputs/hades-test/competitors.txt << 'EOF'
Dead Cells
The Binding of Isaac: Rebirth
Enter the Gungeon
Slay the Spire
Hollow Knight
EOF

# Generate
python generate_audit.py --client hades-test
```

**Expected data quality**:
- SteamSpy: 1M-2M owners ✅
- Metacritic: 93/100 ✅
- YouTube: 1,000+ videos ✅

### Batch Processing

```bash
# Generate for multiple clients
for client in client1 client2 client3; do
    python generate_audit.py --client $client
done
```

**Note**: Each takes ~10 minutes, plan accordingly.

---

## System Requirements

### Minimum
- Python 3.8+
- 2 GB RAM
- Internet connection
- Anthropic API key

### Recommended
- Python 3.10+
- 4 GB RAM
- Fast internet
- All API keys configured

---

## Getting Help

### Check Documentation
- **This file** - Everything you need to know ✨
- `ENHANCEMENTS.md` - What features exist
- `claude.md` - Project context (for development)

### Common Issues

**"Generation failed"**:
1. Check .env has ANTHROPIC_API_KEY
2. Verify all 4 input files exist
3. Check Steam URL is valid
4. Look at error message for specifics

**"PDF looks wrong"**:
1. Open markdown file (backup)
2. Check if data collected correctly
3. Verify templates exist in `templates/`

**"Pricing CSV empty"**:
- This shouldn't happen - check console for errors

---

## File Structure (For Reference)

```
Publitz-Automated-Audits/
├── generate_audit.py          # Main CLI ⭐ RUN THIS
├── .env                        # API keys (YOU created this)
│
├── inputs/                     # Client data ⭐
│   └── client-name/
│       ├── steam_url.txt       # 1. Steam URL
│       ├── competitors.txt     # 2. Competitor list
│       ├── intake_form.json    # 3. Client info
│       └── strategy_notes.txt  # 4. Call notes
│
├── output/                     # Generated reports ⭐
│   └── client-name/
│       ├── *_audit_*.pdf       # DELIVERABLE 1
│       └── *_pricing_*.csv     # DELIVERABLE 2
│
├── src/                        # Code (don't modify)
├── templates/                  # PDF templates
└── docs/                       # Additional docs
```

---

## Maintenance

### Weekly
- [ ] Check Anthropic API usage/costs
- [ ] Review generated reports for quality

### Monthly
- [ ] Update dependencies: `pip install --upgrade -r requirements.txt`
- [ ] Archive old output files (>90 days)
- [ ] Check API quota usage (YouTube, RAWG)

### As Needed
- [ ] Update API keys if changed
- [ ] Customize PDF templates (templates/pdf_template.html)
- [ ] Adjust pricing tiers (src/pricing_csv.py)

---

## Summary

### To Generate an Audit:

1. **Create**: `python generate_audit.py --create-example client-name`
2. **Fill**: Edit 4 files in `inputs/client-name/`
3. **Generate**: `python generate_audit.py --client client-name`
4. **Deliver**: Send PDF + CSV from `output/client-name/`

**Time**: 10 minutes to generate
**Cost**: $5-8 per report
**Value**: $1,500 professional audit

---

## That's It!

You now know everything you need to generate professional Steam game audit reports.

**Questions?** Re-read the relevant section above - everything is covered.

**Ready to start?** Run: `python generate_audit.py --test`

---

*Last Updated: December 9, 2025*
*System Version: 2.0 (Enhanced with APIs)*
