# Claude Context: Publitz Automated Audits

**Last Updated**: December 9, 2025
**Current Phase**: Phase 2 Complete (with Vision) ✅ | Phase 3 Next

---

## 🎯 Project Goal

**Transform complex Steam audit tool into a simple, automated report generation system.**

**Input**: 4 simple text files from client
**Output**: Professional 35-45 page PDF audit report worth $800

**Key Principle**: Focus on deliverable quality, not interface complexity.

---

## 📋 Current Status

### ✅ Completed
- **Phase 1**: Core infrastructure (input processing, data collection, CLI)
- **Phase 2**: Claude AI report generation with comprehensive 9-section reports
- **Phase 2.5**: Claude Vision integration for visual asset analysis (capsule, screenshots, banner)

### 🚧 In Progress
- Documentation updates for Vision integration
- Testing Vision integration with real Steam games

### ⏳ Next
- **Phase 3**: PDF export with professional design
- Final production workflow documentation

---

## 🏗️ Architecture

### The 4-Input System

All client data comes from a folder: `inputs/<client-name>/`

1. **steam_url.txt** - Single line with Steam store URL
   ```
   https://store.steampowered.com/app/12345/Game_Name/
   ```

2. **competitors.txt** - List of competitor games (5-10)
   ```
   Hades
   Dead Cells
   The Binding of Isaac
   ```

3. **intake_form.json** - Client metadata
   ```json
   {
     "client_name": "Awesome Studio",
     "game_name": "My Game",
     "launch_date": "2025-03-15",
     "target_price": 19.99,
     "team_size": 3,
     "main_concerns": "Pricing, visibility, timing"
   }
   ```

4. **strategy_notes.txt** - Free-form strategy call notes
   ```
   Strategy Call Notes - Jan 5, 2025

   Client Emotional State: Anxious but motivated

   Key Concerns:
   - Worried about capsule visibility
   - Price uncertainty
   - Limited marketing budget
   ```

### Data Flow

```
4 Input Files
    ↓
Input Validation (config.py, input_processor.py)
    ↓
Data Collection (simple_data_collector.py)
    ├─ Steam API: Game data
    ├─ SteamSpy: Owner estimates
    ├─ Competitor analysis
    └─ External research (Reddit, HLTB, SteamDB)
    ↓
Vision Analysis (report_generator.py - NEW!)
    ├─ Capsule image analysis
    ├─ Screenshot analysis (3 screenshots)
    └─ Banner/background analysis
    ↓
Report Generation (report_generator.py)
    ├─ Claude Sonnet 4.5 with 200K context
    ├─ Expert system prompt (20+ years experience)
    ├─ Vision analysis integrated into Section 2
    └─ 9-section comprehensive report
    ↓
Markdown Output (~35-45 pages)
    ↓
PDF Export (Phase 3 - TODO)
    └─ Beautiful formatted PDF with branding
```

---

## 📁 File Structure

### Core Files
```
generate_audit.py          # Main CLI - THIS IS WHAT USERS RUN
config.py                  # Configuration & validation
.env                       # API keys (ANTHROPIC_API_KEY)
```

### Source Modules
```
src/
├── input_processor.py         # Parse & validate 4 inputs
├── simple_data_collector.py   # Fetch Steam/competitor data
└── report_generator.py        # Claude AI + Vision (700+ lines)
```

### Documentation (Critical)
```
claude.md                      # THIS FILE - Project context
REDESIGN_PLAN.md              # Complete architecture (800+ lines)
PHASE1_COMPLETE.md            # Phase 1 summary
PHASE2_COMPLETE.md            # Phase 2 + Vision integration
README_NEW_SYSTEM.md          # User guide
```

### Data Directories
```
inputs/<client-name>/          # Client input files
output/<client-name>/          # Generated reports
```

---

## 🎨 The Report Structure

### 9 Comprehensive Sections

1. **Cover Page** - Game name, client, readiness badge
2. **Executive Summary** - Star ratings, top 3 actions, key insights
3. **Compliance Audit** - Steam page checklist
4. **Store Page Optimization** - Capsule, description, tags, screenshots (USES VISION!)
5. **Regional Pricing Strategy** - Price analysis & tables
6. **Competitive Analysis** - Detailed competitor breakdown
7. **Launch Timing Analysis** - Window assessment & conflicts
8. **Implementation Roadmap** - Week-by-week action plan
9. **First-Year Sales Strategy** - Discount calendar & bundle strategy

### Star Rating System

- ⭐ **Store Quality** (1-5): Technical + visual + content
- ⭐ **Competitive Position** (1-5): Price + differentiation + market fit
- ⭐ **Launch Timing** (1-5): Window + calendar + prep time

**Overall Tiers**:
- ✅ LAUNCH READY: Mostly 4-5 stars
- ⚠️ LAUNCH VIABLE: Mix of 3-5 stars
- 🚨 HIGH RISK: Multiple 2-3 stars
- ❌ NOT READY: Any 1-star

---

## 🔍 Claude Vision Integration (NEW!)

### What It Analyzes

1. **Capsule/Header Image**:
   - Readability at thumbnail size (460x215px)
   - Logo sizing (120px+ recommended)
   - Contrast and visibility
   - Visual hierarchy
   - Genre appropriateness

2. **Screenshots** (up to 3):
   - UI clarity and readability
   - Visual quality / production value
   - Gameplay communication
   - Action/interest level
   - Technical issues

3. **Banner/Background**:
   - Visual impact
   - Branding consistency
   - Text readability
   - Composition

### How It Works

```python
# In report_generator.py:

1. _fetch_image_as_base64(url)
   - Downloads image from Steam CDN
   - Converts to base64 data URI

2. _analyze_visual_asset(url, type, context)
   - Calls Claude Vision API
   - Asset-specific analysis prompts
   - Returns detailed critique

3. _analyze_all_visual_assets(data, inputs)
   - Orchestrates all vision analysis
   - Caches results
   - Returns structured analysis dict

4. In generate_full_report():
   - Calls vision analysis BEFORE building prompt
   - Integrates results into prompt
   - Claude uses vision feedback in Section 2
```

### Benefits

- **Specific measurements**: "Logo is 60px, needs 120px" not "make logo bigger"
- **Professional critique**: Worth $200-300 standalone
- **Catches thumbnail issues**: What humans miss at small size
- **Genre-aware**: Compares to successful games in genre

### Cost Impact

- Adds ~$2-3 per report (4-5 images analyzed)
- Adds ~30-60 seconds to generation time
- **Total cost**: ~$5-8 per report (still <1% of $800 value)

---

## 💻 How to Use (Production Workflow)

### For Each New Client

#### 1. Create Client Folder
```bash
python generate_audit.py --create-example client-name
```

This creates: `inputs/client-name/` with template files.

#### 2. Fill in Client Data

Edit the 4 files in `inputs/client-name/`:
- `steam_url.txt` - Get from client
- `competitors.txt` - Client provides or you research
- `intake_form.json` - From intake form
- `strategy_notes.txt` - Notes from strategy call

#### 3. Generate Report
```bash
python generate_audit.py --client client-name
```

**Wait 5-8 minutes**. The system will:
1. ✅ Validate inputs
2. ✅ Collect Steam data
3. ✅ Analyze competitors
4. ✅ Run external research
5. ✅ Analyze visuals with Claude Vision (NEW!)
6. ✅ Generate 35-45 page report with Claude AI
7. ✅ Save markdown to `output/client-name/`

#### 4. Review & Deliver (Phase 3 - Coming Soon)
```bash
# Will generate PDF automatically
ls output/client-name/
# → client-name_audit_20251209.pdf
```

---

## 🛠️ Development Best Practices

### When Working on This Project

1. **Always Read Documentation First**
   - `REDESIGN_PLAN.md` - Complete architecture & design decisions
   - `PHASE1_COMPLETE.md` & `PHASE2_COMPLETE.md` - What's built
   - This file (`claude.md`) - Current context

2. **Maintain Simplicity**
   - Core principle: 4 inputs → PDF report
   - Don't over-engineer
   - If feature doesn't improve deliverable, skip it

3. **Focus on Report Quality**
   - Specific recommendations (measurements, steps, time estimates)
   - No generic advice ("improve capsule" ❌ → "increase logo to 120px" ✅)
   - Vision analysis should enhance, not replace, expert analysis

4. **Test with Real Data**
   - Use actual Steam games
   - Check API responses
   - Validate vision analysis quality

5. **Document Everything**
   - Update PHASE docs when completing phases
   - Keep this file current
   - Explain design decisions

### Git Workflow

```bash
# Current branch
git branch
# → claude/design-customer-docs-013AU6obijhzjV9JkhWxqose

# Before committing
git status
git diff

# Commit with clear messages
git add .
git commit -m "Add Claude Vision integration for visual asset analysis"

# Push to feature branch
git push -u origin claude/design-customer-docs-013AU6obijhzjV9JkhWxqose
```

---

## ✅ TODO List

### Completed ✅
- [x] Phase 1: Core infrastructure
- [x] Phase 2: Claude AI report generation
- [x] Claude Vision integration
- [x] Documentation for Phases 1 & 2
- [x] Vision analysis integrated into prompts

### In Progress 🚧
- [ ] Update all documentation with Vision details
- [ ] Test Vision integration with real Steam games
- [ ] Verify vision analysis quality

### Next Up ⏳
- [ ] **Phase 3: PDF Export**
  - Create `src/export_pdf.py`
  - Create `templates/pdf_template.html`
  - Markdown → HTML → PDF pipeline
  - Professional styling & branding
  - Generate pricing CSV

- [ ] **Final Documentation**
  - Create `WORKFLOW.md` with production workflow
  - Update `README_NEW_SYSTEM.md` with Phase 3
  - Add usage examples

- [ ] **Testing & Polish**
  - End-to-end test with real clients
  - Performance optimization
  - Error handling improvements

---

## 🎓 Knowledge Base Reference

### Report Methodology (Embedded in System Prompt)

The system prompt in `report_generator.py` embeds:
- 20+ years AAA publishing experience (EA, Disney, Web3)
- Steam algorithm & visibility mechanics
- Competitive positioning strategy
- Visual design expertise (NEW with Vision)
- Conservative approach (under-promise, over-deliver)
- Tone calibration (match client emotional state)

### Key Quality Standards

**Specificity**:
- ❌ "Improve your capsule"
- ✅ "Increase logo from 60px to 120px, move to left-third"

**Recommendation Format**:
- **What**: Specific task
- **Why**: Impact/stakes
- **How**: Exact numbered steps
- **Time**: Realistic estimate (hours)
- **Impact**: Expected improvement (%, not $)

**No Revenue Projections**:
- ❌ "$10K-15K revenue impact"
- ✅ "Could improve conversion by 15-20%"

---

## 🔧 Technical Details

### APIs Used

**Claude AI**:
- Model: `claude-sonnet-4-5-20250929`
- Context: 200K tokens
- Temperature: 0.7
- Max output: 15,000 tokens

**Claude Vision**:
- Same model with vision capability
- Max tokens per image: 1,000
- Supports: JPEG, PNG, GIF, WebP

**Steam Store API**:
- Endpoint: `https://store.steampowered.com/api/appdetails`
- Free, no auth required
- Returns: Game details, price, screenshots, reviews

**SteamSpy API**:
- Endpoint: `https://steamspy.com/api.php`
- Free, no auth required
- Returns: Owner estimates, playtime data

### Configuration

```bash
# .env file (required)
ANTHROPIC_API_KEY=sk-ant-your-key-here
CLAUDE_MODEL=claude-sonnet-4-5-20250929
CLAUDE_MAX_TOKENS=15000
CLAUDE_TEMPERATURE=0.7

# Optional
INPUT_DIR=inputs
OUTPUT_DIR=output
TEMPLATE_DIR=templates
```

---

## 🚀 Performance Targets

- **Generation Time**: < 10 minutes total ✅
- **Report Length**: 35-45 pages ✅
- **Cost per Report**: < $10 ✅
- **Report Value**: $800 worth of analysis ✅

**Current Performance**:
- Input validation: ~5 seconds
- Data collection: ~2-3 minutes
- Vision analysis: ~30-60 seconds
- Report generation: ~2-3 minutes
- **Total**: 5-8 minutes

---

## 💡 Design Decisions & Rationale

### Why CLI instead of Web UI?
- Faster to build
- Easier to automate
- No hosting/deployment complexity
- Focus on deliverable, not interface

### Why Single Report instead of 3 Tiers?
- Simpler for clients to understand
- Easier to maintain
- All clients get full value
- No confusion about what they're getting

### Why Claude Sonnet 4.5?
- 200K context window (fits entire audit)
- Best balance of quality/cost/speed
- Vision capability built-in
- Excellent instruction following

### Why Vision Integration?
- Capsule analysis is critical for Steam success
- Human reviewers miss issues at thumbnail size
- Specific, measurable feedback (60px → 120px)
- Worth $200-300 standalone
- Small cost increase (~$2-3) for huge value

### Why Markdown First, PDF Later?
- Easier to review/edit
- Git-friendly
- Phase 3 will add beautiful PDF
- Clients can still read markdown

---

## 📞 Common Issues & Solutions

### "ANTHROPIC_API_KEY not set"
```bash
# Create .env file in project root
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env
```

### "No module named 'anthropic'"
```bash
pip install -r requirements.txt
```

### Vision analysis failing
- Check image URLs are accessible
- Verify images are valid formats (JPEG/PNG/GIF/WebP)
- Check Claude API has vision access
- Review error messages in console

### Report generation slow
- Normal: 5-8 minutes total
- Vision adds: 30-60 seconds
- If > 10 minutes: Check API connectivity

---

## 🎯 Success Criteria

### Phase 2 Success (Achieved ✅)
- ✅ Generates comprehensive 9-section reports
- ✅ Uses Claude Sonnet 4.5 effectively
- ✅ Vision analysis integrated
- ✅ Specific, actionable recommendations
- ✅ Star ratings and tier system working
- ✅ < 10 minutes generation time
- ✅ < $10 per report cost

### Phase 3 Success (Target)
- Beautiful PDF output
- Professional branding (client + Publitz)
- Pricing CSV export
- Print-optimized layout
- Customer-ready deliverable

### Production Ready Criteria
- Full end-to-end generation working
- PDF export functional
- Documentation complete
- Tested with 5+ real clients
- Error handling robust
- Performance consistent

---

## 📚 Further Reading

- **REDESIGN_PLAN.md**: Complete 800+ line design document
- **PHASE1_COMPLETE.md**: Phase 1 implementation details
- **PHASE2_COMPLETE.md**: Phase 2 + Vision integration details
- **README_NEW_SYSTEM.md**: User-facing documentation
- **src/report_generator.py**: Code implementation (~700 lines)

---

## 🔄 Session Continuity

### If Starting New Session

1. **Read this file first** (`claude.md`)
2. **Check current status** in TODO list above
3. **Review recent commits**: `git log --oneline -10`
4. **Read relevant PHASE docs** for context
5. **Continue from last TODO item**

### Key Context Points
- We simplified from complex multi-tier system
- 4 inputs → PDF report is core principle
- Claude Vision integration is NEW (just added)
- Phase 3 (PDF export) is next priority
- All design decisions documented in REDESIGN_PLAN.md

---

**Last Updated**: December 9, 2025
**Maintainer**: Project Lead
**Claude Model**: Sonnet 4.5
