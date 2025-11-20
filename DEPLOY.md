# Deploying to Streamlit Cloud

This guide will help you deploy the Publitz Steam Audit Tool to Streamlit Cloud so you can access it from anywhere via a web URL.

## Prerequisites

1. A GitHub account
2. This repository pushed to GitHub
3. An Anthropic API key ([get one here](https://console.anthropic.com/))

## Deployment Steps

### 1. Push to GitHub (if not already done)

```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 2. Sign Up for Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Click "Sign in with GitHub"
3. Authorize Streamlit to access your GitHub account

### 3. Deploy Your App

1. Click "New app" button
2. Fill in the deployment form:
   - **Repository**: Select `YourUsername/Publitz-Automated-Audits`
   - **Branch**: `main` (or your branch name)
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom URL (e.g., `publitz-steam-audit`)

3. Click "Advanced settings" (optional but recommended)
   - Set Python version: `3.11`

4. Click "Deploy"

### 4. Configure Secrets (API Key)

Instead of hardcoding your API key, you can set it as a secret:

1. After deployment, go to your app's settings
2. Click on "Secrets" in the sidebar
3. Add your secrets in TOML format:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

4. Click "Save"
5. Your app will automatically restart

### 5. Access Your App

Once deployed, you'll get a URL like:
```
https://your-app-name.streamlit.app
```

Share this URL with anyone who needs to use the tool!

## Using the App

### For Users Without API Key in Secrets

1. Open the app URL
2. In the sidebar, enter your Anthropic API key
3. Paste a Steam store URL in the main input
4. Click "Generate Report"
5. Wait for the analysis (1-3 minutes)
6. Download the PDF report

### For Users With API Key in Secrets

The API key will be pre-filled from the secrets, so users just need to:

1. Open the app URL
2. Paste a Steam store URL
3. Click "Generate Report"
4. Download the PDF report

## Troubleshooting

### App Won't Start

**Issue**: Dependencies failing to install

**Solution**: Check the logs in Streamlit Cloud dashboard:
- Look for errors related to `playwright` or `weasyprint`
- These require system packages defined in `packages.txt`
- Streamlit Cloud should automatically install these

### Playwright Browser Not Found

**Issue**: "Executable doesn't exist" error for Chromium

**Solution**: The `.streamlit/setup.sh` script should handle this automatically. If not:
- Check Streamlit Cloud logs
- Verify `setup.sh` is executable
- Contact Streamlit support if issue persists

### PDF Generation Fails

**Issue**: WeasyPrint can't generate PDFs

**Solution**:
- Ensure all packages in `packages.txt` are installed
- Check that Cairo and Pango libraries are available
- Review app logs for specific missing dependencies

### Rate Limits

**Issue**: "Rate limit exceeded" errors

**Solution**:
- Anthropic API has rate limits
- Add delays between requests if processing multiple games
- Upgrade your Anthropic API plan if needed

## App Features

The deployed app includes:

- ✅ **API Key Input**: Enter your key in the sidebar (or use secrets)
- ✅ **Steam URL Input**: Paste any Steam store page URL
- ✅ **Auto-Detection**: Automatically detects pre-launch vs post-launch
- ✅ **Progress Tracking**: Real-time progress bar and status updates
- ✅ **Report Preview**: View the report in-browser before downloading
- ✅ **PDF Download**: Download professional PDF reports
- ✅ **Markdown Export**: Also export as markdown
- ✅ **Clean UI**: Professional, easy-to-use interface

## Updating the App

To update your deployed app:

1. Make changes to your code locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update features"
   git push origin main
   ```
3. Streamlit Cloud will automatically detect changes and redeploy

## Managing the App

From the Streamlit Cloud dashboard you can:

- ⚙️ **Settings**: Configure Python version, secrets, etc.
- 📊 **Analytics**: View app usage statistics
- 📝 **Logs**: Debug issues and monitor performance
- ⏸️ **Pause/Resume**: Stop the app when not in use
- 🗑️ **Delete**: Remove the app completely

## Cost Considerations

- **Streamlit Cloud**: Free tier includes 1 app with unlimited viewers
- **Anthropic API**: Pay per token used
  - Pre-launch report: ~$0.50-1.00 per report
  - Post-launch report: ~$0.50-1.00 per report
  - Depends on game complexity and data amount

## Security Best Practices

1. **Never commit API keys** to the repository
2. **Use Streamlit Secrets** for production API keys
3. **Review .gitignore** to ensure `.env` is excluded
4. **Monitor API usage** to detect unauthorized use
5. **Rotate keys periodically** if shared publicly

## Support

- **Streamlit Cloud Docs**: [docs.streamlit.io](https://docs.streamlit.io/streamlit-community-cloud)
- **Streamlit Forum**: [discuss.streamlit.io](https://discuss.streamlit.io/)
- **Anthropic Docs**: [docs.anthropic.com](https://docs.anthropic.com/)

## Example Deployment URL

After deployment, your app will be accessible at:
```
https://publitz-steam-audit.streamlit.app
```

Share this URL with your team or clients!

---

**Note**: The first cold start may take 2-3 minutes as Streamlit Cloud installs dependencies and Playwright browsers. Subsequent runs will be much faster.
