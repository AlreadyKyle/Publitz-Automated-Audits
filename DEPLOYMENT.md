# 🚀 Deployment Guide - Streamlit Community Cloud

## Quick Start (3 Steps)

### Step 1: Get Your Anthropic API Key
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Create an API key
4. Copy it (starts with `sk-ant-...`)

### Step 2: Deploy to Streamlit Cloud
1. Visit https://share.streamlit.io/
2. Sign in with GitHub
3. Click **"New app"**
4. Fill in:
   - **Repository**: `AlreadyKyle/Publitz-Automated-Audits`
   - **Branch**: `claude/fix-audit-report-error-01MdYQ7RM7Yam7FK5eaoVwHB` (or `main` after merge)
   - **Main file path**: `app.py`
5. Click **"Advanced settings"**
6. In **Secrets**, paste:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-actual-key-here"
   ```
7. Click **"Deploy!"**

### Step 3: Test Your App
1. Wait 2-3 minutes for deployment
2. App will be live at: `https://your-app-name.streamlit.app`
3. Paste this test URL: `https://store.steampowered.com/app/292030/The_Witcher_3_Wild_Hunt/`
4. Click "Generate Audit Report"
5. Download and verify the report

---

## Local Testing (Before Deployment)

### Mac/Linux
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# 3. Run app
streamlit run app.py
```

### Windows
```cmd
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key
set ANTHROPIC_API_KEY=sk-ant-your-key-here

# 3. Run app
streamlit run app.py
```

---

## Environment Variables

You can skip entering the API key every time by setting it as an environment variable.

### Option 1: .env file (Local Only)
Create `.env` file in project root:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Option 2: System Environment Variable

**Mac/Linux** - Add to `~/.bashrc` or `~/.zshrc`:
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**Windows** - System Properties > Environment Variables:
```
Variable: ANTHROPIC_API_KEY
Value: sk-ant-your-key-here
```

### Option 3: Streamlit Secrets (Cloud)
In Streamlit Cloud dashboard > Secrets:
```toml
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

---

## Deployment Settings

### Recommended Streamlit Cloud Settings
- **Python version**: 3.9+
- **Resources**: Default (sufficient)
- **Wake-up time**: Instant (keep app active)

### Custom Domain (Optional)
1. In Streamlit Cloud, go to Settings
2. Click "Custom domain"
3. Add your domain: `audits.yourdomain.com`
4. Follow DNS instructions

---

## Updating Your Deployed App

### Method 1: Push to GitHub (Automatic)
```bash
# Make changes
git add .
git commit -m "Update feature"
git push

# Streamlit Cloud auto-deploys in ~30 seconds
```

### Method 2: Manual Redeploy
1. Go to https://share.streamlit.io/
2. Find your app
3. Click "⋮" > "Reboot app"

---

## Monitoring & Logs

### View Logs
1. Go to https://share.streamlit.io/
2. Click on your app
3. Click "Manage app" > "Logs"
4. See real-time errors and print statements

### Monitor Usage
- View in Streamlit Cloud dashboard
- Track API calls in Anthropic console
- Check error rates

---

## Troubleshooting

### App Won't Start
- Check logs for import errors
- Verify `requirements.txt` is correct
- Ensure `app.py` is in root directory

### "Invalid API Key" Error
- Check secrets are saved correctly
- Verify key format: `sk-ant-...`
- Test key at https://console.anthropic.com/

### Slow Performance
- Normal: 15-30 seconds per report
- Steam API can be slow sometimes
- App uses rate limiting (0.2s delays)

### No Competitors Found
- App has built-in fallback competitors ✅
- Should never return zero (guaranteed 3-5 minimum)

---

## Production Checklist

Before going live:
- [ ] Test locally first
- [ ] API key added to secrets
- [ ] Test all features work
- [ ] Test error handling
- [ ] Verify downloads work
- [ ] Check on mobile
- [ ] Review generated reports
- [ ] Monitor logs for errors
- [ ] Set up custom domain (optional)
- [ ] Share with beta testers

---

## Support & Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **Anthropic API Docs**: https://docs.anthropic.com/
- **Steam API Docs**: https://steamcommunity.com/dev
- **GitHub Issues**: https://github.com/AlreadyKyle/Publitz-Automated-Audits/issues

---

**Ready to deploy!** 🎉

Your app is production-ready with all bugs fixed and features working.
