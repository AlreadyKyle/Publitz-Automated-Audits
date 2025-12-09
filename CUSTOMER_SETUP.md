# Customer Setup Guide - Mac Only

**IMPORTANT**: This system must run on your Mac. It won't work in Claude Code due to network restrictions.

**YOU ALWAYS WORK ON THE `main` BRANCH - NEVER SWITCH BRANCHES**

---

## First Time Setup (5 minutes)

### Step 1: Get the Code

1. Open **GitHub Desktop**
2. **Make sure you're on the `main` branch** (see "Current Branch" dropdown - it should say "main")
3. Click **"Fetch origin"** button at top
4. If **"Pull origin"** appears, click it

### Step 2: Install Dependencies

1. Open **Terminal** (Applications → Utilities → Terminal)
2. Copy/paste these commands one at a time:

```bash
cd ~/Documents/GitHub/Publitz-Automated-Audits
```

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

### Step 3: Test It

```bash
python generate_audit.py --test
```

**This takes 10-12 minutes and creates:**
- `output/test-client/test-client_audit_YYYYMMDD.pdf`
- `output/test-client/test-client_pricing_YYYYMMDD.csv`

**If you see errors**, check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Getting Updates (When I Push Fixes)

**CRITICAL: You must ALWAYS be on the `main` branch**

### In GitHub Desktop:

1. **Check Current Branch** - Top dropdown should say "main"
   - If it says something else, click it and select "main"
2. **Click "Fetch origin"** (top button)
3. **If "Pull origin" appears**, click it
4. **Check History tab** to see if new commits appeared

### Then Test:

```bash
cd ~/Documents/GitHub/Publitz-Automated-Audits
source venv/bin/activate
python generate_audit.py --test
```

**For detailed GitHub Desktop instructions, see: [GITHUB_DESKTOP_GUIDE.md](GITHUB_DESKTOP_GUIDE.md)**

---

## Daily Usage

### Run Test Audit

```bash
cd ~/Documents/GitHub/Publitz-Automated-Audits
source venv/bin/activate
python generate_audit.py --test
```

### Generate Client Report

1. Create client folder:
```bash
python generate_audit.py --create-example client-name
```

2. Edit the 4 files in `inputs/client-name/`:
   - `steam_url.txt` - Game's Steam URL
   - `competitors.txt` - Competitor game names or URLs
   - `intake_form.json` - Client details
   - `strategy_notes.txt` - Your strategic notes

3. Generate report:
```bash
python generate_audit.py --client client-name
```

4. Find outputs in `output/client-name/`

---

## Quick Troubleshooting

### "Command not found: python3"
Install Python from [python.org](https://www.python.org/downloads/)

### API Errors / Network Issues
See [DEBUG_MAC_NETWORK.md](DEBUG_MAC_NETWORK.md)

### GitHub Desktop Confusion
See [GITHUB_DESKTOP_GUIDE.md](GITHUB_DESKTOP_GUIDE.md)

### All Other Issues
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## What's Fixed in Latest Version

✅ Fixed price parsing errors (CDN$, EUR$, etc.)
✅ Removed broken Steam GetAppList API
✅ Fixed all type conversion errors
✅ Simplified API stack: RAWG + SteamSpy + Steam scraping

---

## System Requirements

- Mac (Intel or Apple Silicon)
- Python 3.8 or higher
- Internet connection
- API Keys in `.env`:
  - `ANTHROPIC_API_KEY` (required)
  - `RAWG_API_KEY` (optional, for Metacritic scores)

---

*Last Updated: December 9, 2025*
