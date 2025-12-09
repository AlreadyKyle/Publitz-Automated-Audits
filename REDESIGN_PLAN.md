# Publitz Audit System - Complete Redesign Plan

**Date**: December 9, 2025
**Last Updated**: December 9, 2025 (Vision Integration Added ✅)
**Goal**: Transform complex Streamlit app into a simple, automated document generation system
**Deliverable**: Professional $800-value customer-facing audit report

---

## Executive Summary

**What We're Building**: A streamlined system that takes 4 inputs and automatically generates a comprehensive, beautifully designed Steam game audit report suitable for customer delivery.

**Key Changes**:
- ❌ Remove: Complex UI, multi-tier reports, excessive analysis modules
- ✅ Keep: Core data gathering, Claude AI integration, Steam API connections
- ✅ Add: Simple intake form processing, automated report generation, professional PDF output

---

## Part 1: Input Requirements

### The 4 Required Inputs

1. **Client Steam URL**
   - Example: `https://store.steampowered.com/app/12345/Game_Name/`
   - Used to: Fetch game data automatically

2. **Top 5+ Competitors** (URLs or names)
   - Example:
     ```
     - Hades
     - Dead Cells
     - Binding of Isaac
     - Enter the Gungeon
     - Slay the Spire
     ```
   - Used to: Competitive analysis, pricing benchmarks

3. **Intake Form Data** (JSON/Dict)
   ```json
   {
     "client_name": "Studio Name",
     "client_email": "contact@studio.com",
     "game_name": "My Awesome Game",
     "launch_date": "2025-03-15",
     "target_price": 19.99,
     "main_concerns": "Pricing, visibility, launch timing",
     "marketing_budget": "Limited (<$5K)",
     "team_size": 3,
     "development_stage": "Pre-launch / Post-launch"
   }
   ```

4. **Strategy Call Notes** (Text)
   ```
   - Client is stressed about launch timing
   - Mentioned they're concerned capsule isn't standing out
   - Wishlist count: 2,500
   - Key insight: They're targeting roguelike fans but tags are too generic
   - Emotional state: Anxious but motivated
   ```

---

## Part 2: What To Keep from Current System

### Core Components (Keep & Refactor)

1. **Steam Data Collection** (`src/game_search.py`, `src/steamdb_scraper.py`)
   - ✅ Steam Store API integration
   - ✅ SteamSpy data fetching
   - ✅ Review data collection
   - 🔧 Simplify: Remove multi-tier fallbacks, keep core functionality

2. **AI Analysis** (`src/ai_generator.py`)
   - ✅ Claude API integration
   - ✅ Vision analysis for capsule/screenshots
   - 🔧 Simplify: Single-pass generation, remove multi-model ensemble

3. **Competitor Analysis** (`src/comparable_games_analyzer.py`)
   - ✅ Find similar games
   - ✅ Price comparison
   - 🔧 Simplify: Focus on user-provided competitors only

4. **Regional Pricing** (`src/regional_pricing.py`)
   - ✅ Price recommendations by region
   - ✅ CSV export
   - 🔧 Keep as-is (simple module)

### What To Remove (Bloat)

- ❌ `report_orchestrator.py` (3 tier system - too complex)
- ❌ `revenue_based_scoring.py` (over-engineered)
- ❌ `score_validation.py` (unnecessary)
- ❌ `roi_calculator.py` (complex, not customer-facing)
- ❌ `negative_review_analyzer.py` (deep analysis not needed)
- ❌ `ab_testing.py`, `dashboard_generator.py`, `conversion_funnel.py` (feature creep)
- ❌ Multi-tier report system (Tier 1/2/3)
- ❌ Streamlit UI complexity (keep minimal or CLI)

---

## Part 3: New System Architecture

### Simple Flow Diagram

```
┌─────────────────────┐
│  4 Inputs Provided  │
│  - Steam URL        │
│  - Competitors      │
│  - Intake Form      │
│  - Strategy Notes   │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│  Data Collection    │
│  - Fetch Steam data │
│  - Analyze comps    │
│  - HLTB/Reddit APIs │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│  Claude Generation  │
│  - Single prompt    │
│  - Full report      │
│  - 9 sections       │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│  Export Deliverable │
│  - PDF (primary)    │
│  - Markdown (backup)│
│  - Pricing CSV      │
└─────────────────────┘
```

### File Structure (Simplified)

```
publitz-audits/
├── generate_audit.py           # Main entry point (CLI or minimal UI)
├── config.py                   # API keys, settings
├── requirements.txt            # Minimal dependencies
│
├── src/
│   ├── input_processor.py      # Parse 4 inputs
│   ├── data_collector.py       # Steam/competitor data
│   ├── report_generator.py     # Claude prompt + generation
│   ├── export_pdf.py           # PDF with nice design
│   └── utils.py                # Helpers
│
├── templates/
│   ├── audit_prompt.txt        # Master Claude prompt
│   └── pdf_template.html       # PDF design (HTML → PDF)
│
├── output/                     # Generated reports
│
└── WORKFLOW.md                 # This file
```

---

## Part 4: Report Structure (Based on KB)

### Single Unified Report (35-45 pages)

Following the knowledge base structure but simplified:

1. **Cover Page** (1 page)
   - Game name, client logo, date
   - Launch readiness badge (✅/⚠️/🚨/❌)

2. **Executive Summary** (2-3 pages)
   - Star ratings (Store/Position/Timing)
   - Top 3 priority actions
   - Biggest risk & opportunity

3. **Section 1: Compliance Audit** (3-4 pages)
   - Steam page checklist
   - Critical issues flagged

4. **Section 2: Store Page Optimization** (5-6 pages)
   - Capsule analysis (with Claude Vision)
   - Description rewrite
   - Tag optimization
   - Screenshot strategy

5. **Section 3: Regional Pricing** (3-4 pages)
   - Base price recommendation
   - Regional pricing table
   - CSV attachment

6. **Section 4: Competitive Analysis** (4-5 pages)
   - 5+ competitor breakdown
   - Competitive matrix
   - Differentiation opportunities

7. **Section 5: Launch Timing** (3-4 pages)
   - Launch window analysis
   - Conflicts identified
   - Keep/delay recommendation

8. **Section 6: Implementation Roadmap** (4-5 pages)
   - Week 1: Critical actions
   - Week 2-3: Important optimizations
   - Timeline Gantt chart

9. **Section 7: First-Year Sales Strategy** (3-4 pages)
   - Discount calendar
   - Steam seasonal sales
   - Bundle strategy

10. **Section 8: Multi-Storefront** (3-4 pages)
    - Epic/GOG/Console assessment
    - Effort vs return analysis

11. **Section 9: 90-Day Post-Launch** (3-4 pages)
    - Community management
    - Update cadence
    - DLC decision

12. **Next Steps & Resources** (2 pages)
    - Follow-up actions
    - Links and tools

---

## Part 5: Implementation Plan

### Phase 1: Core Infrastructure (Day 1)

**Goal**: Get basic input → output working

```python
# generate_audit.py (CLI version)

import json
from src.input_processor import process_inputs
from src.data_collector import collect_all_data
from src.report_generator import generate_report
from src.export_pdf import export_to_pdf

def main():
    # Load inputs
    inputs = {
        'steam_url': 'https://store.steampowered.com/app/...',
        'competitors': ['Game A', 'Game B', 'Game C', 'Game D', 'Game E'],
        'intake_form': json.load(open('intake.json')),
        'strategy_notes': open('strategy_notes.txt').read()
    }

    # Collect data
    print("📊 Collecting game data...")
    game_data = collect_all_data(inputs)

    # Generate report with Claude
    print("🤖 Generating audit report...")
    report_markdown = generate_report(game_data, inputs)

    # Export
    print("📄 Exporting PDF...")
    pdf_path = export_to_pdf(report_markdown, game_data['game_name'])

    print(f"✅ Report complete: {pdf_path}")

if __name__ == '__main__':
    main()
```

**Files to Create**:
- `src/input_processor.py` - Validate and parse inputs
- `src/data_collector.py` - Gather Steam/competitor data
- `src/report_generator.py` - Single Claude prompt for full report
- `src/export_pdf.py` - Markdown → Beautiful PDF

### Phase 2: Claude Prompt Engineering (Day 1-2)

**Goal**: Single comprehensive prompt that generates the full 9-section report

**Strategy**:
- Use the KB content as context in system message
- Provide all collected data in structured format
- Request full report in single response
- Use Claude Sonnet 4.5 (supports 200K tokens)

```python
def generate_report(game_data, inputs):
    """
    Generate full audit report in one Claude call.
    """
    # Build comprehensive prompt
    prompt = f"""
    Generate a complete Pre-Launch Steam Audit for:

    GAME DATA:
    {json.dumps(game_data, indent=2)}

    CLIENT INFO:
    {json.dumps(inputs['intake_form'], indent=2)}

    STRATEGY NOTES:
    {inputs['strategy_notes']}

    COMPETITORS ANALYZED:
    {json.dumps(game_data['competitors'], indent=2)}

    Generate a comprehensive report following this structure:
    [Insert full section structure here...]

    Use markdown formatting. Be specific and actionable.
    """

    response = call_claude_api(prompt)
    return response.content
```

### Phase 3: Data Collection (Day 2)

**Refactor existing code to be simpler**:

```python
# src/data_collector.py

def collect_all_data(inputs):
    """
    Collect all necessary data for the audit.
    Returns a single comprehensive dict.
    """
    data = {}

    # 1. Parse Steam URL, fetch game data
    data['game'] = fetch_steam_data(inputs['steam_url'])

    # 2. Fetch competitor data
    data['competitors'] = []
    for comp in inputs['competitors']:
        comp_data = fetch_steam_data(comp)
        comp_data['hltb'] = fetch_howlongtobeat(comp)
        data['competitors'].append(comp_data)

    # 3. External research (free APIs)
    data['reddit_insights'] = fetch_reddit_genre_insights(data['game']['genre'])
    data['launch_window'] = check_steamdb_conflicts(data['game']['launch_date'])
    data['tag_popularity'] = get_tag_follower_counts(data['game']['tags'])

    # 4. Vision analysis (if capsule image available) ✅ IMPLEMENTED!
    if data['game']['capsule_url']:
        data['capsule_analysis'] = analyze_with_vision(data['game']['capsule_url'])
        # Now also analyzes screenshots (up to 3) and banner/background
        # See src/report_generator.py: _analyze_all_visual_assets()

    return data
```

### Phase 4: PDF Export (Day 2-3)

**Goal**: Professional-looking PDF that feels like $800 of value

**Approach**: Use markdown → HTML → PDF pipeline

```python
# src/export_pdf.py

import markdown
from weasyprint import HTML
from jinja2 import Template

def export_to_pdf(markdown_report, game_name):
    """
    Convert markdown report to beautifully formatted PDF.
    """
    # Convert markdown to HTML
    html_body = markdown.markdown(
        markdown_report,
        extensions=['tables', 'fenced_code', 'codehilite']
    )

    # Load template
    template = Template(open('templates/pdf_template.html').read())

    # Render with styling
    full_html = template.render(
        game_name=game_name,
        report_body=html_body,
        generated_date=datetime.now().strftime('%B %d, %Y')
    )

    # Convert to PDF with nice styling
    pdf_path = f'output/{sanitize(game_name)}_audit.pdf'
    HTML(string=full_html).write_pdf(pdf_path)

    return pdf_path
```

**PDF Template** (`templates/pdf_template.html`):
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: 'Helvetica', sans-serif;
            line-height: 1.6;
            color: #333;
        }
        h1 {
            color: #2C3E50;
            border-bottom: 3px solid #3498DB;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495E;
            margin-top: 30px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #3498DB;
            color: white;
        }
        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: bold;
        }
        .badge-green { background: #27AE60; color: white; }
        .badge-yellow { background: #F39C12; color: white; }
        .badge-red { background: #E74C3C; color: white; }
    </style>
</head>
<body>
    <div class="cover">
        <h1>Pre-Launch Steam Audit</h1>
        <h2>{{ game_name }}</h2>
        <p><strong>Generated:</strong> {{ generated_date }}</p>
        <p><strong>Prepared by:</strong> Publitz</p>
    </div>

    <div class="report-body">
        {{ report_body|safe }}
    </div>

    <footer>
        <p><em>This audit was prepared by Publitz using proprietary analysis methods and 20+ years of AAA publishing experience.</em></p>
    </footer>
</body>
</html>
```

### Phase 5: Testing & Refinement (Day 3)

**Test Cases**:
1. Pre-launch indie game (typical customer)
2. Post-launch struggling game
3. Successful game (for comparison)

**Quality Checks**:
- ✅ Report is 35-45 pages
- ✅ All 9 sections present
- ✅ Recommendations are specific (not generic)
- ✅ PDF looks professional
- ✅ Pricing CSV exports correctly
- ✅ Total generation time < 10 minutes

---

## Part 6: Free APIs To Use

### Data Sources (All Free)

1. **Steam Store API**
   - Endpoint: `https://store.steampowered.com/api/appdetails?appids={app_id}`
   - Free, no key needed
   - Returns: Game details, price, description, screenshots

2. **SteamSpy API**
   - Endpoint: `https://steamspy.com/api.php?request=appdetails&appid={app_id}`
   - Free, no key needed
   - Returns: Owner estimates, player counts

3. **HowLongToBeat** (web scraping)
   - URL: `https://howlongtobeat.com/game/{game_name}`
   - Free (use requests + BeautifulSoup)
   - Returns: Playtime estimates

4. **Reddit API** (no auth for public data)
   - Endpoint: `https://www.reddit.com/r/{subreddit}/search.json?q={query}`
   - Free for read-only
   - Returns: Community discussions, genre insights

5. **SteamDB** (web scraping for launch conflicts)
   - URL: `https://steamdb.info/upcoming/`
   - Free (use requests + BeautifulSoup)
   - Returns: Upcoming game releases, conflicts

### Paid API (Required)

1. **Anthropic Claude API**
   - Model: `claude-sonnet-4-5-20250929`
   - Cost: ~$3-5 per report (200K tokens input, 10K output)
   - Critical for: Report generation, vision analysis

---

## Part 7: Minimal Dependencies

```txt
# requirements.txt (stripped down)

# Core
anthropic==0.40.0           # Claude API
python-dotenv==1.0.0        # Config management

# Data fetching
requests==2.31.0            # HTTP requests
beautifulsoup4==4.12.3      # Web scraping (HLTB, SteamDB)
lxml==5.1.0                 # HTML parsing

# PDF generation
markdown==3.5.1             # Markdown → HTML
weasyprint==60.2            # HTML → PDF
Jinja2==3.1.3               # HTML templates

# Optional: Simple UI
streamlit==1.29.0           # Only if keeping web interface
```

**Remove**:
- ❌ fpdf2 (replaced by weasyprint)
- ❌ plotly, matplotlib (no charts needed)
- ❌ pandas (overkill for simple data)
- ❌ Many other unused dependencies

---

## Part 8: Workflow & Best Practices

### Claude.md Workflow File

```markdown
# Publitz Audit Generation Workflow

## Pre-Requisites
- [ ] Anthropic API key set in `.env`
- [ ] Python 3.10+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`

## Generation Process

### Step 1: Prepare Inputs (5 mins)
1. Create `inputs/` folder for the client
2. Save 4 required files:
   - `steam_url.txt` - Game's Steam URL
   - `competitors.txt` - One competitor per line
   - `intake_form.json` - Client intake data
   - `strategy_notes.txt` - Call notes

**Example**:
```
inputs/awesome-game/
├── steam_url.txt
├── competitors.txt
├── intake_form.json
└── strategy_notes.txt
```

### Step 2: Run Generation (8-10 mins)
```bash
python generate_audit.py --client awesome-game
```

**What Happens**:
1. Validates inputs (30s)
2. Collects Steam data (2-3 mins)
3. Fetches competitor data (2-3 mins)
4. External research (Reddit, HLTB, SteamDB) (1-2 mins)
5. Generates report with Claude (2-3 mins)
6. Exports PDF + pricing CSV (30s)

### Step 3: Review & Deliver (5 mins)
1. Open `output/awesome-game/audit.pdf`
2. Quick review:
   - [ ] All 9 sections present
   - [ ] Client name/game name correct
   - [ ] Recommendations are specific
   - [ ] PDF formatting looks good
3. Attach pricing CSV
4. Send to client

**Total Time**: ~20 minutes per audit

## Quality Checks

Before delivery, verify:
- [ ] Report is 35-45 pages
- [ ] Top 3 priorities are clearly highlighted
- [ ] Star ratings (Store/Position/Timing) are present
- [ ] Competitive analysis includes all competitors provided
- [ ] Pricing recommendations are justified
- [ ] Launch timing section addresses conflicts
- [ ] Implementation roadmap has specific tasks
- [ ] No placeholder text ("[FILL IN]", "TODO", etc.)
- [ ] Client logo on cover (if provided)

## Troubleshooting

**Issue**: "Steam API returned 429"
- **Fix**: Wait 60 seconds, retry
- **Prevention**: Add rate limiting

**Issue**: "Claude API timeout"
- **Fix**: Report likely > 200K tokens, split into 2 prompts
- **Prevention**: Reduce competitor count or compress data

**Issue**: "PDF export failed"
- **Fix**: Check weasyprint dependencies: `pip install weasyprint --upgrade`
- **Fallback**: Export markdown only

## Best Practices

1. **Before Starting**:
   - Review strategy notes for client concerns
   - Validate Steam URL is accessible
   - Check competitor names are correct

2. **During Generation**:
   - Monitor console output for API errors
   - Watch for data quality warnings
   - Note any missing data (HLTB not found, etc.)

3. **After Generation**:
   - Skim report for obvious errors
   - Verify star ratings make sense
   - Check that tone matches client's emotional state

4. **Client Communication**:
   - Set expectation: 24-48 hour turnaround
   - Mention follow-up strategy call included
   - Offer to clarify any recommendations

## Testing

Run test generation before client work:
```bash
python generate_audit.py --test
```

This uses a known good test case to verify:
- APIs are accessible
- Claude API key is valid
- PDF export works
- Output quality is acceptable

**Expected**: Full report in ~10 mins, no errors

---

## Emergency Fallbacks

If critical component fails:

1. **No Claude API**:
   - Export data only (JSON/CSV)
   - Manual report writing required
   - Refund customer or delay delivery

2. **Steam API down**:
   - Request client provide SteamSpy data manually
   - Reduced audit (skip sections requiring Steam data)

3. **PDF export broken**:
   - Deliver markdown + instructions to convert
   - Or use Google Docs for quick formatting

```

---

## Part 9: Configuration

### .env File

```env
# API Keys
ANTHROPIC_API_KEY=sk-ant-...

# Optional
OPENAI_API_KEY=  # Not needed in simplified version
GOOGLE_API_KEY=  # Not needed

# Settings
REPORT_LANGUAGE=en
MAX_COMPETITORS=10
CLAUDE_MODEL=claude-sonnet-4-5-20250929
CLAUDE_MAX_TOKENS=10000
CLAUDE_TEMPERATURE=0.7

# Paths
INPUT_DIR=inputs
OUTPUT_DIR=output
TEMPLATE_DIR=templates
```

### config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

    # Claude Settings
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-5-20250929')
    CLAUDE_MAX_TOKENS = int(os.getenv('CLAUDE_MAX_TOKENS', 10000))
    CLAUDE_TEMPERATURE = float(os.getenv('CLAUDE_TEMPERATURE', 0.7))

    # Paths
    INPUT_DIR = os.getenv('INPUT_DIR', 'inputs')
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')
    TEMPLATE_DIR = os.getenv('TEMPLATE_DIR', 'templates')

    # Limits
    MAX_COMPETITORS = int(os.getenv('MAX_COMPETITORS', 10))
    REPORT_TIMEOUT = int(os.getenv('REPORT_TIMEOUT', 600))  # 10 mins

    @classmethod
    def validate(cls):
        """Validate configuration before running"""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set in .env")

        # Create directories if needed
        os.makedirs(cls.INPUT_DIR, exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
```

---

## Part 10: Next Steps

### Immediate Actions (Today)

1. ✅ Create this design document
2. ⏳ Get client approval on design/approach
3. ⏳ Start Phase 1 implementation (core infrastructure)

### This Week

**Day 1**:
- Build `generate_audit.py` CLI
- Create `src/input_processor.py`
- Test input validation

**Day 2**:
- Refactor data collection (`src/data_collector.py`)
- Build Claude prompt (`templates/audit_prompt.txt`)
- Test end-to-end generation (markdown output)

**Day 3**:
- Build PDF export (`src/export_pdf.py`)
- Design PDF template (`templates/pdf_template.html`)
- Run full test cases
- Refine output quality

### Success Criteria

**MVP Complete When**:
- ✅ Takes 4 inputs, generates report
- ✅ Report matches KB structure (9 sections)
- ✅ PDF looks professional
- ✅ Total time < 15 minutes
- ✅ Zero manual intervention needed

**Production Ready When**:
- ✅ All test cases pass
- ✅ Error handling robust
- ✅ Documentation complete
- ✅ Client delivers first paid audit successfully

---

## Part 11: Migration Strategy

### What Happens to Old Code?

**Keep (in `/legacy/` folder)**:
- Current `app.py` and Streamlit UI (backup)
- `report_orchestrator.py` (reference for structure)
- All analysis modules (may cannibalize later)

**Archive**:
- Move to `legacy/` folder
- Keep for reference only
- Don't import into new system

**Delete**:
- Nothing yet (risky to delete before new system works)
- After 2 successful customer deliveries, clean up

---

## Conclusion

This redesign focuses on **simplicity** and **deliverability**:

1. **4 Inputs** → No more complex UI flows
2. **Single Report** → No more tier confusion
3. **Beautiful PDF** → Customer-ready deliverable
4. **Automated** → No manual steps
5. **Fast** → < 15 minutes total

**Estimated Build Time**: 3 days
**Maintenance**: Minimal (few dependencies, simple flow)
**Scalability**: Easy to add more clients (just folders of inputs)

Ready to start implementation? Let's build Phase 1! 🚀
