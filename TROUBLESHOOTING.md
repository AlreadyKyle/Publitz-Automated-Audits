# Troubleshooting Guide

Quick solutions to common problems.

---

## GitHub Desktop Issues

### "Fetch origin" doesn't do anything

**Cause:** You're already up to date.

**Solution:**
1. Check "History" tab - do you see recent commits?
2. Make sure "Current Branch" says "main"
3. If you see recent commits, you already have the updates

---

### I'm on the wrong branch (not "main")

**Cause:** Accidentally switched or GitHub Desktop switched automatically.

**Solution:**
1. Click "Current Branch" dropdown (top center)
2. Search for "main"
3. Click "main" to switch
4. If you see "Stash" or "Discard" popup → Click "Discard"

**See:** [GITHUB_DESKTOP_GUIDE.md](GITHUB_DESKTOP_GUIDE.md) for detailed branch switching guide

---

### "Pull origin" doesn't appear after "Fetch origin"

**Cause:** You're already up to date with the remote.

**Solution:**
- This is normal
- Check "History" tab to see if new commits are there
- If commits are there, you're good
- If no new commits, then there are no updates available

---

### GitHub Desktop shows "Push origin" instead of "Pull origin"

**Cause:** You have local commits that aren't on GitHub yet.

**Solution:**
1. Click "Push origin" to sync your changes
2. Then click "Fetch origin" again
3. If "Pull origin" appears, click it

---

## Python / Installation Issues

### "Command not found: python3"

**Cause:** Python not installed or not in PATH.

**Solution:**
1. Install Python from [python.org](https://www.python.org/downloads/)
2. Download the macOS installer
3. Run it and follow the wizard
4. Close Terminal and open a new one
5. Try again

---

### "No module named 'anthropic'" or other import errors

**Cause:** Virtual environment not activated or dependencies not installed.

**Solution:**
```bash
cd ~/Documents/GitHub/Publitz-Automated-Audits
source venv/bin/activate  # You should see (venv) appear in your prompt
pip install -r requirements.txt
```

---

### "Permission denied" errors

**Cause:** File permissions issue.

**Solution:**
```bash
chmod +x *.command
```

---

## API / Network Issues

### "ProxyError" or "Connection refused"

**Cause:** Network blocking or VPN issues.

**Solution:**
1. Make sure you're running on your Mac (not in Claude Code web)
2. Disable VPN if you have one
3. Run the network diagnostic:
   ```bash
   python test_network.py
   ```
4. See [DEBUG_MAC_NETWORK.md](DEBUG_MAC_NETWORK.md) for detailed network debugging

---

### "API rate limit exceeded"

**Cause:** Made too many requests to an API in a short time.

**Solution:**
- Wait 5-10 minutes
- Try again
- The system uses caching to avoid this (24-hour cache)

---

### "Invalid API key" errors

**Cause:** Missing or incorrect API keys in `.env` file.

**Solution:**
1. Check `.env` file exists in project root
2. Make sure it has:
   ```
   ANTHROPIC_API_KEY="sk-ant-..."
   RAWG_API_KEY="..."
   ```
3. No spaces around the `=` sign
4. Keys in quotes
5. See `.env.example` for reference

---

## Report Generation Issues

### "Report generation failed: could not convert string to float"

**Cause:** Data format issue (should be fixed in latest version).

**Solution:**
1. Make sure you're on latest code
2. In GitHub Desktop: Fetch → Pull
3. Run test again
4. If still failing, send me the full error message

---

### Generated report has placeholder text

**Cause:** AI generation failed, system fell back to placeholder.

**Solution:**
1. Check API key is valid in `.env`
2. Check internet connection
3. Look at the error message above "Falling back to placeholder"
4. Send me the error message

---

### PDF generation fails but markdown works

**Cause:** PDF rendering library issue.

**Solution:**
1. The markdown report still has all the content
2. You can manually convert .md to .pdf using:
   - [CloudConvert](https://cloudconvert.com/md-to-pdf)
   - [Pandoc](https://pandoc.org/) (requires installation)
3. Or send me the error and I'll fix the PDF generator

---

## Data Collection Issues

### "Steam API 404 error"

**Cause:** Using deprecated Steam endpoint (should be fixed).

**Solution:**
1. Make sure you're on latest code
2. Fetch/Pull in GitHub Desktop
3. The system should now use Steam Store scraping instead

---

### "No data found for game"

**Cause:** Game too new, region-locked, or invalid Steam URL.

**Solution:**
1. Verify Steam URL is correct
2. Make sure game is publicly available (not beta/unreleased)
3. Try using the game's App ID directly in `steam_url.txt`:
   ```
   https://store.steampowered.com/app/APP_ID/Game_Name/
   ```

---

### Competitor games showing "Unknown" data

**Cause:** Using game names instead of URLs, or game search failing.

**Solution:**
- **Use Steam URLs for competitors instead of names**
- Edit `inputs/your-client/competitors.txt`:
  ```
  https://store.steampowered.com/app/292030/The_Witcher_3/
  https://store.steampowered.com/app/460930/Tom_Clancys_Ghost_Recon_Wildlands/
  ```

---

## Test Failures

### Test runs but creates placeholder report

**Causes:**
1. API key issue
2. Network blocking
3. Data collection failure

**Solution:**
1. Check terminal output for specific errors
2. Look for lines starting with "ERROR" or "❌"
3. Address the specific error using this guide
4. If unclear, copy the full terminal output and send it to me

---

### Test hangs or takes forever

**Cause:** Network timeout or API slowness.

**Solution:**
1. Wait 15 minutes (test normally takes 10-12 min)
2. If still hanging, press Ctrl+C to cancel
3. Check internet connection
4. Try again

---

## Quick Diagnostics

### Run All System Checks

```bash
cd ~/Documents/GitHub/Publitz-Automated-Audits
source venv/bin/activate

# Check Python
python --version

# Check dependencies
pip list | grep anthropic
pip list | grep requests

# Check API connectivity
python test_network.py

# Check if .env exists
cat .env
```

---

## When To Ask For Help

**Ask me if:**
- You've tried the solutions here and they don't work
- You see an error not listed in this guide
- Something worked before but suddenly stopped
- You're unsure what an error means

**Include in your message:**
- Full error message / terminal output
- What you were trying to do
- What you've tried already
- Screenshot if relevant

---

## Emergency Recovery

### Nuclear Option: Fresh Start

If everything is broken and nothing works:

```bash
# 1. Backup your .env file
cp .env .env.backup

# 2. Delete virtual environment
rm -rf venv

# 3. Get latest code in GitHub Desktop
#    Make sure you're on "main" branch
#    Click Fetch → Pull

# 4. Recreate virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Restore .env
cp .env.backup .env

# 6. Test
python generate_audit.py --test
```

---

*Last Updated: December 9, 2025*
