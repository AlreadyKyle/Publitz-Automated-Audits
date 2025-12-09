# GitHub Desktop Guide for Non-Coders

**Purpose:** Get updates from me (Claude) when I fix bugs or add features.

**Rule #1:** YOU ALWAYS WORK ON THE `main` BRANCH - NEVER SWITCH TO OTHER BRANCHES

---

## Understanding GitHub Desktop Layout

```
┌─────────────────────────────────────────────────────────┐
│  Current Repository    Current Branch         Fetch     │
│  [dropdown]           [main ▼]              [origin]    │
├─────────────────────────────────────────────────────────┤
│  [Changes] [History]                                    │
│                                                          │
│  Changes Tab: Shows files you've modified locally       │
│  History Tab: Shows all commits (updates) over time     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## How to Get Updates (Step-by-Step)

### Step 1: Check Your Current Branch

**Look at the top center of GitHub Desktop.**

You should see: **"Current Branch: main"**

✅ **If it says "main"** → Continue to Step 2

❌ **If it says anything else** (like "claude/design-customer-docs-..."):
1. Click the "Current Branch" dropdown
2. Type "main" in the search
3. Click "main" to switch to it
4. Wait 1-2 seconds for the switch to complete

---

### Step 2: Fetch Updates from GitHub

**Click the "Fetch origin" button** (top right)

**What happens:**
- Button will spin briefly
- One of three things will happen:

#### Option A: Nothing Changes
This means you're already up to date. No new updates available.

#### Option B: Button Changes to "Pull origin"
This means there ARE new updates!
1. **Click "Pull origin"**
2. Wait for it to complete (1-5 seconds)
3. ✅ Done! You now have the latest code

#### Option C: Button Changes to "Push origin"
This means YOU have local commits that aren't on GitHub yet.
1. **Click "Push origin"** to sync your changes
2. Then click "Fetch origin" again
3. If "Pull origin" appears, click it

---

### Step 3: Verify You Got the Updates

1. Click the **"History"** tab (top left)
2. Look at the top commit (most recent)
3. Check the date/time - should be recent
4. You should see commit messages like:
   - "Fix price parsing error"
   - "Remove deprecated Steam API"
   - etc.

---

## Common Scenarios & Solutions

### Scenario 1: "Fetch origin doesn't do anything"

**Problem:** You're already up to date, or you're on the wrong branch.

**Solution:**
1. Check "Current Branch" - make sure it says "main"
2. Click "History" tab - check if recent commits are there
3. If the latest commit is from today, you already have the updates

---

### Scenario 2: "I see 'Stash' or 'Discard' popup"

**Problem:** You switched branches while having unsaved changes.

**Solution:**
1. **Click "Discard"** - Your changes on the other branch aren't needed
2. Continue with getting updates

---

### Scenario 3: "I see 'Pull X commits from origin'"

**Problem:** Your local branch is behind the remote.

**Solution:**
1. Make sure you're on "main" branch
2. **Click "Pull origin"**
3. Done

---

### Scenario 4: "I see 'Push X commits to origin'"

**Problem:** You have local commits that aren't on GitHub yet.

**Solution:**
1. **Click "Push origin"** to sync them
2. Then fetch again

---

## The ONLY Workflow You Need

### When I Tell You "I've Pushed Updates":

```
1. Open GitHub Desktop
2. Check "Current Branch" → Should be "main"
3. Click "Fetch origin"
4. If "Pull origin" appears → Click it
5. Check "History" tab → See new commits
6. Open Terminal → Run test
```

That's it. Every single time.

---

## Visual Reference

### What "Fetch origin" Looks Like:
```
┌──────────────────┐
│  ↻ Fetch origin  │  ← This button
└──────────────────┘
```

### What "Pull origin" Looks Like:
```
┌──────────────────┐
│  ↓ Pull origin   │  ← Click this when it appears
└──────────────────┘
```

### What "Current Branch" Looks Like:
```
┌────────────────────────┐
│  Current Branch        │
│  main            ▼     │  ← Should always say "main"
└────────────────────────┘
```

---

## FAQ

### Q: Why do I have to check the branch every time?
**A:** Because sometimes GitHub Desktop switches branches automatically or you accidentally switched. Checking takes 1 second and prevents hours of confusion.

### Q: What if I'm on a branch that starts with "claude/"?
**A:** Switch back to "main" immediately. You should NEVER be on a claude/ branch. Those are my work branches.

### Q: What if "Fetch origin" never shows "Pull origin"?
**A:** You're already up to date. Check the History tab to confirm. If you don't see recent commits, let me know.

### Q: Can I just use Terminal for git commands?
**A:** No. Use GitHub Desktop. It's visual and clearer for non-coders. Terminal git commands require knowing what you're doing.

---

## Troubleshooting

### GitHub Desktop shows weird errors
1. Close GitHub Desktop
2. Open it again
3. Try fetch/pull again

### Still confused?
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or ask me directly.

---

*Last Updated: December 9, 2025*
