# Customer Setup Guide - Mac Only

**IMPORTANT**: This system must run on your Mac. It won't work in the Claude Code web interface due to network restrictions.

---

## First Time Setup (5 minutes)

### Step 1: Get Latest Code

1. Open **GitHub Desktop**
2. Click **"Fetch origin"** (top-right button)
3. If it says "Pull origin" appears, click that too
4. Make sure you're on the **main** branch

### Step 2: Install Dependencies

1. Open **Terminal** (Applications → Utilities → Terminal)
2. Navigate to your project:
   ```bash
   cd ~/path/to/Publitz-Automated-Audits
   ```
3. Create virtual environment:
   ```bash
   python3 -m venv venv
   ```
4. Activate it:
   ```bash
   source venv/bin/activate
   ```
5. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

### Step 3: Test It

Still in Terminal with venv activated:

```bash
python3 generate_audit.py --test
```

**This should take 10-12 minutes and generate:**
- `output/test-client/test-client_audit_YYYYMMDD.pdf`
- `output/test-client/test-client_pricing_YYYYMMDD.csv`

---

## Daily Usage

### Quick Start (With Terminal)

1. Open Terminal
2. Navigate to project:
   ```bash
   cd ~/path/to/Publitz-Automated-Audits
   ```
3. Activate venv:
   ```bash
   source venv/bin/activate
   ```
4. Run test:
   ```bash
   python3 generate_audit.py --test
   ```

### Generate Client Report

1. Create client folder:
   ```bash
   python3 generate_audit.py --create-example client-name
   ```
2. Open the folder and edit the 4 files:
   - `steam_url.txt`
   - `competitors.txt`
   - `intake_form.json`
   - `strategy_notes.txt`
3. Generate report:
   ```bash
   python3 generate_audit.py --client client-name
   ```
4. Find outputs in `output/client-name/`

---

## Using the .command Files (Double-Click)

### First Time Only:

1. Right-click `SETUP.command` → **Open With** → **Terminal**
2. If you see a security warning, go to **System Settings → Privacy & Security** and click "Open Anyway"
3. After first time, you can just double-click

### Running Tests:

Just double-click `RUN_TEST.command`

### Creating Clients:

Just double-click `CREATE_CLIENT.command`

---

## Troubleshooting

### "Command not found: python3"

Install Python from [python.org](https://www.python.org/downloads/)

### "Permission denied" on .command files

```bash
chmod +x *.command
```

### Getting Updates from GitHub

In GitHub Desktop:
1. Click "Fetch origin"
2. If "Pull origin" appears, click it
3. That's it!

---

## What Fixed in Latest Version

✅ Removed broken Steam Web API
✅ Removed YouTube API (not needed)
✅ Fixed all type conversion errors
✅ Simplified to only working APIs: RAWG + SteamSpy + Steam scraping

---

## Need Help?

1. Make sure you're running on your Mac (not in Claude Code web)
2. Make sure you pulled latest from GitHub Desktop
3. Make sure venv is activated (`source venv/bin/activate`)
4. Check that `.env` has your `ANTHROPIC_API_KEY`

---

*Last Updated: December 9, 2025*
