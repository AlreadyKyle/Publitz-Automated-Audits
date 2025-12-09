# Production Workflow: Publitz Automated Audits

**Version**: 1.0
**Last Updated**: December 9, 2025

---

## Overview

This document outlines the complete production workflow for generating and delivering Steam game audit reports using the Publitz Automated Audit system.

**What You Get**:
- 35-45 page professional audit report (PDF)
- Regional pricing CSV (50+ countries, Steam-compatible)
- Complete package ready for client delivery
- Generation time: 8-10 minutes
- Cost per report: $5-8

---

## Prerequisites

### System Requirements

**Software**:
- Python 3.8+
- Git (for version control)
- Internet connection (for API calls)

**API Keys**:
- Anthropic API key (Claude AI)
- Free tier is sufficient for moderate usage

**Dependencies Installed**:
```bash
pip install -r requirements.txt
```

### Initial Setup (One Time)

1. **Clone Repository**:
```bash
git clone <repository-url>
cd Publitz-Automated-Audits
```

2. **Create Environment File**:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

3. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

4. **Verify Setup**:
```bash
python generate_audit.py --help
```

---

## Standard Workflow

### Step 1: Client Intake

**Collect from Client**:
1. Steam store page URL
2. List of 5-10 competitor games
3. Completed intake form (use template)
4. Strategy call notes

**Intake Form Template** (`intake_form.json`):
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

### Step 2: Create Client Folder

**Option A: Use Template**
```bash
python generate_audit.py --create-example client-name

# This creates:
# inputs/client-name/
# ├── steam_url.txt
# ├── competitors.txt
# ├── intake_form.json
# └── strategy_notes.txt
```

**Option B: Manual Creation**
```bash
mkdir -p inputs/client-name
# Create the 4 required files (see templates below)
```

### Step 3: Fill in Client Data

**File 1: `steam_url.txt`**
```
https://store.steampowered.com/app/12345/Game_Name/
```

**File 2: `competitors.txt`**
```
# One competitor per line (names or URLs)
Hades
Dead Cells
https://store.steampowered.com/app/588650/Dead_Cells/
The Binding of Isaac: Rebirth
Enter the Gungeon
Slay the Spire
```

**File 3: `intake_form.json`**
- Copy template above
- Fill with client's actual data
- Validate JSON syntax (use jsonlint.com if needed)

**File 4: `strategy_notes.txt`**
```
Strategy Call Notes - December 9, 2025

Client Emotional State: [Anxious/Confident/Burned out/etc.]

Key Concerns:
- [Specific concern 1]
- [Specific concern 2]
- [Specific concern 3]

Additional Context:
- [Team dynamics, budget constraints, timeline pressure, etc.]
- [Any unique circumstances affecting the launch]
- [Previous experience with launches (first-time vs veteran)]

Target Audience:
- [Age range, interests, favorite games]

Marketing Plan:
- [Current marketing activities]
- [Social media presence]
- [Influencer outreach plans]
```

### Step 4: Generate Audit

**Run Generation**:
```bash
python generate_audit.py --client client-name
```

**What Happens**:
1. **Phase 1** (5-10 seconds):
   - Validates all 4 input files
   - Extracts Steam App ID
   - Checks for required fields

2. **Phase 2** (2-3 minutes):
   - Fetches game data from Steam API
   - Analyzes competitor data
   - Collects external research (Reddit, HLTB, etc.)
   - Processes client context

3. **Phase 2.5** (30-60 seconds):
   - Downloads visual assets (capsule, screenshots, banner)
   - Analyzes with Claude Vision
   - Provides specific design critique

4. **Phase 3** (2-3 minutes):
   - Builds comprehensive prompt
   - Calls Claude AI
   - Generates 35-45 page markdown report
   - Saves to `output/client-name/`

5. **Phase 4** (15-30 seconds):
   - Converts markdown to PDF
   - Applies professional styling
   - Generates pricing CSV
   - Creates complete deliverable package

**Expected Output**:
```
output/client-name/
├── client-name_audit_20251209.md     # Markdown (backup)
├── client-name_audit_20251209.pdf    # PDF (deliverable) ⭐
└── client-name_pricing_20251209.csv  # Pricing CSV ⭐
```

### Step 5: Quality Review

**Review Checklist**:
- [ ] PDF opens and renders correctly
- [ ] All 9 sections present and complete
- [ ] Star ratings make sense (Store/Position/Timing)
- [ ] Overall tier appropriate (Launch Ready/Viable/High Risk/Not Ready)
- [ ] Recommendations are specific, not generic
- [ ] Vision analysis incorporated into Section 2
- [ ] Competitor data accurate in Section 4
- [ ] Pricing CSV has all major markets
- [ ] Client name spelled correctly throughout
- [ ] Game name correct
- [ ] No placeholder text remaining

**Spot Checks**:
1. Open PDF → Check cover page branding
2. Scroll to Section 2 → Verify vision analysis present
3. Check Section 4 → Verify competitor data
4. Open CSV in Excel → Spot-check pricing calculations
5. Read Executive Summary → Verify tone matches client

**Quality Standards**:
- ✅ Specific measurements ("increase logo to 120px")
- ✅ Time estimates ("2-4 hours")
- ✅ Impact ratings (percentage improvements)
- ❌ Generic advice ("improve your capsule")
- ❌ Dollar projections ("worth $5K in revenue")

### Step 6: Deliver to Client

**Delivery Package**:
```
📦 Audit Package for [Client Name]

📄 Files Included:
1. [Game Name]_audit_[date].pdf
   → 35-45 page comprehensive audit report
   → Professional formatting, ready to print/view

2. [Game Name]_pricing_[date].csv
   → Regional pricing for 50+ countries
   → Ready to upload to Steam Partner portal

📊 What's Inside the Audit:
- Executive Summary with star ratings
- Store page optimization recommendations
- Regional pricing strategy
- Competitive analysis
- Launch timing assessment
- Implementation roadmap
- First-year sales strategy
- Post-launch management plan

💰 Value: $800 professional audit

🚀 Next Steps:
1. Review the audit report
2. Prioritize top 3 recommendations
3. Use pricing CSV for Steam upload
4. Schedule follow-up call to discuss
```

**Delivery Methods**:
- Email attachment (files <5MB total)
- Google Drive/Dropbox shared link
- Client portal upload (if available)

**Follow-up**:
- Schedule call within 3-5 business days
- Answer questions about recommendations
- Provide implementation support as needed
- Check in 2 weeks before launch

---

## Advanced Workflows

### Multiple Clients in Parallel

**Batch Processing**:
```bash
# Generate for multiple clients
for client in client1 client2 client3; do
    echo "Generating audit for $client..."
    python generate_audit.py --client $client
    echo "---"
done
```

**Note**: Each audit takes ~8-10 minutes. Plan accordingly.

### Re-generating After Updates

**If Client Updates Data**:
```bash
# Edit inputs/client-name/* files
# Re-run generation
python generate_audit.py --client client-name

# New files will have updated timestamp
# Previous versions remain (date-stamped)
```

### Emergency Quick Review

**If You Need Fast Turnaround**:
1. Use `--test` to verify system working: `python generate_audit.py --test`
2. Create client folder with minimal data
3. Generate audit (may have warnings for missing data)
4. Manually fill gaps in report if critical
5. Deliver with caveats noted

---

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not set"

**Solution**:
```bash
# Check .env file exists
ls -la .env

# Check key is set
grep ANTHROPIC_API_KEY .env

# If missing, add it:
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env
```

### Issue: "No module named 'anthropic'"

**Solution**:
```bash
pip install -r requirements.txt
```

### Issue: Vision analysis fails

**Possible Causes**:
- Steam image URLs unreachable
- Claude API error
- Rate limiting

**Resolution**:
- System continues without vision analysis
- Report still generates (uses text-based analysis)
- Check console for specific error

### Issue: PDF rendering fails

**Possible Causes**:
- WeasyPrint not installed
- System font missing
- Markdown formatting issue

**Resolution**:
1. Check WeasyPrint installed: `pip show weasyprint`
2. Markdown report still available as backup
3. Can manually convert markdown to PDF if needed

### Issue: Report quality seems low

**Check**:
- Input data quality (garbage in = garbage out)
- Steam API returned valid data
- Competitor list has similar games
- Strategy notes provide context

**Improve**:
- Add more detailed strategy notes
- Choose more relevant competitors
- Ensure intake form is complete
- Provide specific client concerns

### Issue: Generation takes too long (>15 minutes)

**Possible Causes**:
- Slow internet connection
- Claude API slow/congested
- Too many competitors (>10)

**Solutions**:
- Check internet speed
- Try during off-peak hours
- Reduce competitors to top 5-7
- Check Claude API status page

---

## Best Practices

### Data Collection

**Do**:
- ✅ Collect complete intake form
- ✅ Take detailed strategy call notes
- ✅ Choose relevant competitors (same genre, similar scope)
- ✅ Verify Steam URL is correct before generation
- ✅ Note client's emotional state and priorities

**Don't**:
- ❌ Use placeholder data ("TBD", "Unknown")
- ❌ Choose random/unrelated competitors
- ❌ Skip strategy notes (critical for tone calibration)
- ❌ Generate without reviewing inputs first

### Quality Control

**Before Delivery**:
1. Open PDF and scroll through entire document
2. Verify client name appears correctly
3. Check star ratings make logical sense
4. Read at least Executive Summary + Section 2
5. Spot-check competitor data accuracy
6. Test pricing CSV opens in Excel

**After Delivery**:
1. Save a copy for records
2. Note any client feedback received
3. Track implementation of recommendations
4. Monitor launch results

### Cost Management

**API Costs**:
- ~$5-8 per audit (Claude API)
- Monitor usage in Anthropic dashboard
- Set up billing alerts if doing high volume
- Budget approximately $10 per audit to be safe

**Optimizations**:
- Vision analysis caches results (saves cost on re-runs)
- Markdown always generated first (can review before PDF)
- Can skip PDF if just need quick review

---

## Maintenance

### Weekly

- [ ] Check API key balance/usage
- [ ] Review any failed generations
- [ ] Update competitor databases if needed

### Monthly

- [ ] Review 2-3 generated reports for quality
- [ ] Check for Steam API changes
- [ ] Update pricing multipliers if currencies shift significantly
- [ ] Archive old output files (>90 days)

### Quarterly

- [ ] Review and update knowledge base if methodology changes
- [ ] Test with newly released games
- [ ] Update documentation
- [ ] Review cost per audit trends

### As Needed

- [ ] Update dependencies: `pip install --upgrade -r requirements.txt`
- [ ] Update Claude model if new version available
- [ ] Add new regions to pricing CSV if Steam adds support
- [ ] Customize templates (PDF styling, cover page)

---

## Customization

### Branding

**Change Company Name/Logo**:
1. Edit `templates/pdf_template.html`
2. Update `<h1>PUBLITZ</h1>` to your company name
3. Update tagline
4. Add logo image if desired

**Change Color Scheme**:
1. Edit `templates/pdf_styles.css`
2. Find `#667eea` (primary purple)
3. Replace with your brand color
4. Find `#764ba2` (secondary purple)
5. Replace with your secondary color

### Pricing Tiers

**Adjust Regional Pricing**:
1. Edit `src/pricing_csv.py`
2. Modify `PRICING_TIERS` dictionary
3. Adjust tier assignments in `TIER_ASSIGNMENTS`

**Add New Regions**:
1. Edit `STEAM_REGIONS` in `src/pricing_csv.py`
2. Add: `'COUNTRY_CODE': ('CURRENCY', multiplier, 'Country Name')`

---

## Support & Resources

### Documentation

- **README_NEW_SYSTEM.md** - System overview
- **claude.md** - Project context and goals
- **REDESIGN_PLAN.md** - Complete architecture
- **PHASE1_COMPLETE.md** - Phase 1 details
- **PHASE2_COMPLETE.md** - Phase 2 + Vision
- **PHASE3_COMPLETE.md** - Phase 3 PDF/CSV
- **TEST_PLAN.md** - Testing procedures
- **This file** - Production workflow

### Getting Help

**Common Issues**: See Troubleshooting section above

**System Status**:
- Claude API: https://status.anthropic.com
- Steam API: Generally stable (no status page)

**Questions**:
- Check documentation first
- Review error messages carefully
- Check git commit history for recent changes

---

## Appendix: Quick Reference

### Command Cheat Sheet

```bash
# Create new client template
python generate_audit.py --create-example client-name

# Generate test audit
python generate_audit.py --test

# Generate production audit
python generate_audit.py --client client-name

# Check configuration
python config.py

# Validate inputs without generating
# (Not yet implemented - future feature)
```

### File Structure Reference

```
Publitz-Automated-Audits/
├── generate_audit.py          # Main CLI ⭐
├── config.py                  # Configuration
├── .env                       # API keys (YOU CREATE THIS)
├── requirements.txt           # Dependencies
│
├── inputs/                    # Client data ⭐
│   └── client-name/
│       ├── steam_url.txt
│       ├── competitors.txt
│       ├── intake_form.json
│       └── strategy_notes.txt
│
├── output/                    # Generated reports ⭐
│   └── client-name/
│       ├── *_audit_*.md       # Markdown
│       ├── *_audit_*.pdf      # PDF deliverable
│       └── *_pricing_*.csv    # Pricing CSV
│
├── src/                       # Core modules
│   ├── input_processor.py
│   ├── simple_data_collector.py
│   ├── report_generator.py
│   ├── export_pdf.py
│   └── pricing_csv.py
│
├── templates/                 # PDF templates
│   ├── pdf_template.html
│   └── pdf_styles.css
│
└── docs/                      # Documentation
    ├── README_NEW_SYSTEM.md
    ├── claude.md
    ├── WORKFLOW.md           # This file
    └── TEST_PLAN.md
```

---

**Workflow Version**: 1.0
**Last Updated**: December 9, 2025
**Next Review**: Monthly or as system evolves
