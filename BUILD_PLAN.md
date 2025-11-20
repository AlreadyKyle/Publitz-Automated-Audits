# 🛠️ BUILD PLAN - Systematic Approach to Success

## Problem: No Successful Report Yet

We need a methodical, step-by-step approach to get this working.

---

## Phase 1: Fix Current Error (IMMEDIATE)

### Error: `Client.__init__() got an unexpected keyword argument 'proxies'`

**Root Cause**: Outdated `anthropic==0.18.1` library

**Fix Steps**:

1. **Update Streamlit Cloud Dependencies**:
   - Go to your Streamlit Cloud app dashboard
   - Click "⋮" → "Settings" → "Python version"
   - Make sure it's Python 3.9+

2. **Force Dependency Upgrade**:
   ```bash
   # In requirements.txt (ALREADY UPDATED)
   anthropic>=0.40.0  # Was: anthropic==0.18.1
   ```

3. **Reboot App on Streamlit Cloud**:
   - Click "⋮" → "Reboot app"
   - Wait for rebuild (2-3 minutes)
   - Fresh install will use new version

---

## Phase 2: Test Without API (30 minutes)

### Create Mock/Test Mode

**Goal**: Verify everything works EXCEPT Claude API

**Test Script Created**: `test_components.py`

```bash
# Run locally first
python test_components.py
```

This tests:
- ✅ Steam URL parsing
- ✅ Game data fetching
- ✅ Competitor finding
- ✅ Sales data gathering
- ✅ Session state
- ❌ NO API calls (skip Claude for now)

---

## Phase 3: Test Each Component (1 hour)

### Component 1: Steam URL Parsing
```python
# Test URL: https://store.steampowered.com/app/3183790/Defense_Of_Fort_Burton/
Expected Output: app_id = 3183790
```

### Component 2: Game Data Fetching
```python
# Should return: name, developer, release_date, etc.
Status: Check logs
```

### Component 3: Competitor Finding
```python
# Should return: 3-10 competitors
# NEVER ZERO
Status: Check logs
```

### Component 4: Steam Data
```python
# Should return: sales estimates, reviews
Status: Check logs
```

### Component 5: Claude API
```python
# Last step - only test after above work
Status: Pending
```

---

## Phase 4: Incremental Deployment

### Step 1: Deploy with Test Mode
1. Add `TEST_MODE=true` to Streamlit secrets
2. App runs without Claude API
3. Shows "Test Report" instead
4. Verify all steps work

### Step 2: Enable API Gradually
1. Remove TEST_MODE
2. Add real ANTHROPIC_API_KEY
3. Test one report
4. Monitor logs

### Step 3: Full Production
1. All tests passing
2. Remove debug logging
3. Go live

---

## Phase 5: Debugging Checklist

### If Steam API Fails:
- [ ] Check URL is correct format
- [ ] Try different game
- [ ] Check internet connection
- [ ] SteamSpy might be rate limiting

### If Competitors = 0:
- [ ] Check fallback is triggered
- [ ] Should ALWAYS return 3-5 minimum
- [ ] Check logs for errors

### If Claude API Fails:
- [ ] Verify anthropic>=0.40.0 installed
- [ ] Check API key is valid (console.anthropic.com)
- [ ] Check API key in secrets (no quotes)
- [ ] Try API key in Python directly

### If Streamlit Keeps Rebuilding:
- [ ] Session state fixed (already done)
- [ ] Check for syntax errors in app.py
- [ ] Clear browser cache
- [ ] Hard refresh (Cmd+Shift+R)

---

## Phase 6: Success Criteria

### Before Declaring Success:
- [ ] Can paste Steam URL
- [ ] URL parses correctly
- [ ] Game data fetches
- [ ] Finds 3+ competitors
- [ ] Sales data loads
- [ ] Claude API connects
- [ ] Report generates
- [ ] Download works
- [ ] No infinite loops
- [ ] No crashes

---

## Quick Start Commands

### Local Testing:
```bash
# 1. Upgrade dependencies
pip install --upgrade -r requirements.txt

# 2. Test components
python test_components.py

# 3. Run app
streamlit run app.py

# 4. Test with URL:
# https://store.steampowered.com/app/3183790/Defense_Of_Fort_Burton/
```

### Streamlit Cloud:
```bash
# 1. Commit changes
git add .
git commit -m "Fix anthropic version"
git push

# 2. In Streamlit Cloud dashboard:
# - Click "Reboot app"
# - Wait 2-3 minutes
# - Clear browser cache
# - Hard refresh page

# 3. Check logs for errors
# - Click "Manage app" → "Logs"
```

---

## Error Resolution Matrix

| Error | Cause | Fix |
|-------|-------|-----|
| `proxies` keyword | Old anthropic lib | Update to >=0.40.0 |
| No game found | Invalid URL | Check URL format |
| Zero competitors | API fail | Fallback should trigger |
| Empty report | API key wrong | Verify in console.anthropic.com |
| Infinite loop | Session state | Already fixed |
| Import errors | Missing deps | Check requirements.txt |

---

## Next Steps (RIGHT NOW)

1. **Commit the anthropic version update**
2. **Reboot Streamlit Cloud app**
3. **Wait 3 minutes for rebuild**
4. **Hard refresh browser**
5. **Try again with your test URL**
6. **Check logs if it fails**

---

## Support Contacts

- **Anthropic Status**: https://status.anthropic.com/
- **Streamlit Status**: https://status.streamlit.io/
- **Steam API Status**: https://steamstat.us/

---

**THIS PLAN WILL GET IT WORKING** 🎯

The main issue is the outdated anthropic library. Once that's updated on Streamlit Cloud, it should work.
