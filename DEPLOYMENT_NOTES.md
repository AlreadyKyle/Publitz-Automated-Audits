# Deployment Notes for Streamlit Cloud

## Current Status

All features are deployed and functional with the following notes:

## Known Issues

### PDF Generation

**Issue**: PDF generation may fail with "ModuleNotFoundError: No module named 'fpdf'"

**Cause**: The fpdf2 library (listed in requirements.txt) may not install correctly on Streamlit Cloud in some cases.

**Solutions**:

1. **Verify requirements.txt includes**: `fpdf2>=2.7.0`
2. **Streamlit Cloud Rebuild**: Try redeploying the app to trigger a fresh pip install
3. **Alternative**: Users can download the Markdown version as a workaround

**Graceful Degradation**:
- The app now detects when fpdf2 is unavailable
- Shows clear warning message to users
- Markdown download remains fully functional
- No app crashes

**Error Handling Added** (app.py lines 694-745):
- Pre-flight check for fpdf2 availability
- Clear user messaging when PDF generation unavailable
- Detailed error logging for debugging
- Fallback to Markdown download with user guidance

## Deployment Checklist

Before deploying to Streamlit Cloud:

- [ ] Verify all API keys are in Streamlit Secrets:
  - `ANTHROPIC_API_KEY`
  - `TWITCH_CLIENT_ID`
  - `TWITCH_CLIENT_SECRET`
  - `YOUTUBE_API_KEY`
  - `RAWG_API_KEY`
  - `OPENAI_API_KEY` (optional - for multi-model ensemble)
  - `GOOGLE_API_KEY` (optional - for multi-model ensemble)

- [ ] Verify requirements.txt is up to date:
  ```
  streamlit>=1.31.0
  anthropic>=0.40.0
  requests>=2.31.0
  fpdf2>=2.7.0
  markdown>=3.5.0
  python-dotenv>=1.0.0
  python-dateutil>=2.8.2
  beautifulsoup4>=4.12.0
  lxml>=4.9.0
  pytrends>=4.9.0
  howlongtobeatpy>=1.0.0
  openai>=1.0.0  # optional
  google-generativeai>=0.3.0  # optional
  ```

- [ ] Verify branch is correct:
  - Main: `claude/fix-report-generation-01SnDXjDxLko8gYKCbpEKJ4d`

- [ ] Test PDF generation after deployment:
  - Generate a test report
  - Attempt PDF download
  - If fails, check logs for fpdf2 import errors
  - Verify Markdown download works as fallback

## Recent Fixes Applied

### Session 2025-11-23

1. **LaTeX Rendering** - Fixed currency symbols breaking in Streamlit markdown
2. **Revenue Estimation** - Narrowed ranges from 3.0x to 1.44x spread
3. **Twitch Cache** - Fixed CacheManager signature bugs
4. **Competitor Data** - Fixed normalized genre/tag handling
5. **Review Velocity** - Added validation to prevent impossible values
6. **Reddit Data** - Added estimated subscriber fallbacks
7. **Community/Influencer Sections** - Added specific requirements for real API data
8. **Pricing Recommendations** - Added definitive guidance format
9. **PDF Error Handling** - Added graceful degradation when fpdf2 unavailable

## Performance Notes

- Report generation takes 4-5 minutes (expected due to multi-pass AI system)
- Phase 2 data collection adds 30-60 seconds (Twitch/YouTube/Reddit APIs)
- PDF generation adds 5-10 seconds (if available)

## Support Contacts

If PDF generation consistently fails after rebuild:
1. Check Streamlit Cloud logs for pip install errors
2. Verify Python version compatibility (fpdf2 requires Python 3.7+)
3. Consider adding system package dependencies if needed (unlikely for fpdf2)
