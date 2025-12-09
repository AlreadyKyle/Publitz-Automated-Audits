# Publitz Automated Audits

**Generate professional $1,500 Steam game audit reports in 10 minutes.**

4 simple input files → 35-45 page PDF report + pricing CSV

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run test
python generate_audit.py --test

# 3. Check output
ls output/test-client/
```

That's it! You'll see a professional PDF report and pricing CSV.

---

## For Complete Instructions

**📖 Read: [`USER_GUIDE.md`](USER_GUIDE.md)** ← Everything you need is here

This guide covers:
- ✅ How to generate audits (3 steps)
- ✅ How to fill in the 4 input files
- ✅ What you get in reports
- ✅ Troubleshooting
- ✅ Tips & best practices

---

## What's Included

### Report Features ($1,500 value)
- **Owner Estimates** (SteamSpy) - Quantified market sizing
- **Metacritic Scores** (RAWG) - Quality benchmarks
- **YouTube Buzz** (YouTube API) - Community interest metrics
- **Competitive Analysis** - 10-20 competitors with full data
- **PPP Pricing Audit** - Flags 20-56% overpricing in regions
- **Vision Analysis** (Claude Vision) - Capsule, screenshots, banner critique
- **Research-Backed Recommendations** - Launch velocity, Next Fest strategy, timing

### Deliverables
1. **PDF Report** (35-45 pages) - Professional branded audit
2. **Pricing CSV** (50+ countries) - Steam-compatible regional pricing

### Cost
- **Claude API**: $5-8/report
- **Other APIs**: Free (SteamSpy, RAWG, YouTube, Steam Web API)
- **Total**: $5-8/report

---

## System Requirements

- Python 3.8+
- Anthropic API key
- Internet connection

---

## Project Structure

```
Publitz-Automated-Audits/
├── README.md                  ← You are here
├── USER_GUIDE.md              ← Read this for everything
├── generate_audit.py          ← Run this to generate audits
├── .env                       ← Your API keys
│
├── inputs/                    ← Client data (4 files each)
│   └── client-name/
│       ├── steam_url.txt
│       ├── competitors.txt
│       ├── intake_form.json
│       └── strategy_notes.txt
│
├── output/                    ← Generated reports
│   └── client-name/
│       ├── *_audit_*.pdf      ← DELIVERABLE 1
│       └── *_pricing_*.csv    ← DELIVERABLE 2
│
├── src/                       ← Source code
├── templates/                 ← PDF templates
└── docs/                      ← Additional documentation
```

---

## Documentation

- **[`USER_GUIDE.md`](USER_GUIDE.md)** - **START HERE** - Complete user guide
- **[`ENHANCEMENTS.md`](ENHANCEMENTS.md)** - Feature list and enhancements
- **[`claude.md`](claude.md)** - Project context (for developers/Claude)
- **[`docs/WORKFLOW.md`](docs/WORKFLOW.md)** - Production workflow details
- **[`docs/TEST_PLAN.md`](docs/TEST_PLAN.md)** - Testing procedures

---

## Getting Help

**Everything you need is in [`USER_GUIDE.md`](USER_GUIDE.md)**

Common issues:
- API key not set → Check `.env` file
- No PDF generated → `pip install weasyprint`
- Takes too long → Normal for 9-12 minutes

---

## Version

**Current**: 2.0 (Enhanced with External APIs)
**Last Updated**: December 9, 2025
**Status**: Production Ready ✅

---

## Quick Reference

### Generate Test Audit
```bash
python generate_audit.py --test
```

### Generate Real Audit
```bash
# 1. Create client folder
python generate_audit.py --create-example client-name

# 2. Edit inputs/client-name/* files

# 3. Generate
python generate_audit.py --client client-name
```

### Check Output
```bash
ls output/client-name/
```

---

**For complete instructions, see [`USER_GUIDE.md`](USER_GUIDE.md)** 📖
