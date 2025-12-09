# How to Get Updates & Test

**When I tell you "I've pushed updates" or "pull the latest code", follow these steps EXACTLY.**

---

## The Complete Update & Test Workflow

### Part 1: Get Updates (GitHub Desktop)

1. **Open GitHub Desktop**

2. **CHECK YOUR BRANCH FIRST**
   - Look at "Current Branch" dropdown (top center)
   - It MUST say "main"
   - If it says anything else: Click dropdown → Select "main"

3. **Fetch Updates**
   - Click "Fetch origin" button (top right)
   - Wait 1-2 seconds

4. **Pull If Needed**
   - If button changes to "Pull origin" → Click it
   - If button stays as "Fetch origin" → You're already up to date

5. **Verify Updates**
   - Click "History" tab
   - Check the top commit (most recent)
   - Look for commit message matching what I told you (e.g., "Fix price parsing error")

---

### Part 2: Run Test (Terminal)

1. **Open Terminal**

2. **Navigate to Project**
   ```bash
   cd ~/Documents/GitHub/Publitz-Automated-Audits
   ```

3. **Activate Virtual Environment**
   ```bash
   source venv/bin/activate
   ```
   You should see `(venv)` appear at the start of your prompt.

4. **Run Test**
   ```bash
   python generate_audit.py --test
   ```

5. **Wait 10-12 Minutes**
   - System will show progress
   - Don't close Terminal while it's running

6. **Check Results**
   - ✅ **Success:** You'll see "🎉 Complete audit package ready for delivery!"
   - ❌ **Failure:** You'll see error messages - copy them and send to me

---

## Expected Test Output

### ✅ Successful Test Looks Like:

```
================================================================================
  ___  _   _ ___ _    ___ _____ _____   _   _   _ ___ ___ _____  ___
================================================================================

✅ Configuration validated successfully
🧪 Setting up test client...
...
[1/4] Fetching main game data...
✅ Loaded: Cyberpunk 2077
...
✅ Data collection completed
...
✅ PDF export complete
✅ Pricing CSV generated

================================================================================
✅ AUDIT GENERATION COMPLETE
================================================================================

⏱️  Total time: 13.9 seconds (0.2 minutes)
🎉 Complete audit package ready for delivery!
```

### ❌ Failed Test Looks Like:

```
❌ Report generation failed: [some error message]
   Falling back to placeholder report
```

**If you see this, send me the error message.**

---

## Common Issues During Update & Test

### Issue: "Fetch origin" doesn't do anything

**Solution:** You're already up to date. Check History tab - if you see recent commits from today, you have the updates.

---

### Issue: "I'm on the wrong branch"

**Solution:**
1. Click "Current Branch" dropdown
2. Select "main"
3. If popup appears asking about stash/discard → Click "Discard"

---

### Issue: Test shows errors about API keys

**Solution:**
1. Check `.env` file has your `ANTHROPIC_API_KEY`
2. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

### Issue: Test creates placeholder report instead of real report

**Solution:**
1. Look for error message above "Falling back to placeholder"
2. Copy the full error
3. Send it to me
4. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Quick Reference: The 10-Step Update & Test

```
1. Open GitHub Desktop
2. Check "Current Branch" = "main"
3. Click "Fetch origin"
4. Click "Pull origin" if it appears
5. Open Terminal
6. cd ~/Documents/GitHub/Publitz-Automated-Audits
7. source venv/bin/activate
8. python generate_audit.py --test
9. Wait 10-12 minutes
10. Check for success message
```

---

## After Successful Test

### View Your Generated Files:

```bash
# Open output folder in Finder
open output/test-client
```

You'll see:
- `test-client_audit_YYYYMMDD.pdf` - The full report
- `test-client_pricing_YYYYMMDD.csv` - Pricing data for Steam
- `test-client_audit_YYYYMMDD.md` - Markdown version

### Next Steps:
- ✅ System is working
- ✅ You can now generate real client reports
- ✅ See [CUSTOMER_SETUP.md](CUSTOMER_SETUP.md) for daily usage

---

## Detailed Guides

- **GitHub Desktop confused?** → [GITHUB_DESKTOP_GUIDE.md](GITHUB_DESKTOP_GUIDE.md)
- **Errors during test?** → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Network issues?** → [DEBUG_MAC_NETWORK.md](DEBUG_MAC_NETWORK.md)
- **General setup** → [CUSTOMER_SETUP.md](CUSTOMER_SETUP.md)

---

*Last Updated: December 9, 2025*
