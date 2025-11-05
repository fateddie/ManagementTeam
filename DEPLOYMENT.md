# Streamlit Cloud Deployment Guide

## Prerequisites
- GitHub account
- Streamlit Community Cloud account (free) - [Sign up here](https://share.streamlit.io/)
- API keys for the services you want to use

## Step 1: Access Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Authorize Streamlit to access your GitHub repositories

## Step 2: Deploy Your App

1. Click "New app" button
2. Select your repository: `fateddie/PersonalAssistant`
3. Branch: `main`
4. Main file path: `streamlit_app/app.py`
5. Click "Deploy!"

## Step 3: Configure Environment Variables (Secrets)

After deployment starts, configure your secrets:

1. Click "Settings" → "Secrets" in your Streamlit Cloud dashboard
2. Add the following secrets in TOML format:

```toml
# Required API Keys
OPENAI_API_KEY = "your_openai_api_key_here"
PERPLEXITY_API_KEY = "your_perplexity_api_key_here"

# Optional: Reddit API (if using social media features)
REDDIT_CLIENT_ID = "your_reddit_client_id"
REDDIT_CLIENT_SECRET = "your_reddit_client_secret"
REDDIT_USER_AGENT = "VES Market Research Bot v1.0"

# Optional: X/Twitter API (if using social media features)
X_BEARER_TOKEN = "your_x_bearer_token"
```

3. Click "Save"
4. Your app will automatically reboot with the new secrets

## Step 4: Access Your Deployed App

Your app will be available at:
`https://[your-app-name].streamlit.app`

The URL will be shown in your Streamlit Cloud dashboard.

## Required API Keys

### OpenAI API Key
- Get from: [platform.openai.com](https://platform.openai.com/api-keys)
- Used for: AI-powered idea refinement and scoring

### Perplexity API Key
- Get from: [docs.perplexity.ai](https://docs.perplexity.ai/)
- Used for: Research and market analysis

### Optional: Reddit API (Phase 2)
- Get from: [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
- Create app (type: script)
- Used for: Social media monitoring

### Optional: X/Twitter API (Phase 2)
- Get from: [developer.twitter.com](https://developer.twitter.com/)
- Use Bearer Token (OAuth 2.0)
- Used for: Social media trending analysis

## Troubleshooting

### App won't start
- Check logs in Streamlit Cloud dashboard
- Verify all required environment variables are set
- Check that `requirements.txt` includes all dependencies

### Missing dependencies
- Streamlit Cloud automatically installs from `requirements.txt`
- If you need system packages, create a `packages.txt` file

### App is slow
- Free tier has resource limits
- Consider upgrading to paid tier for better performance
- Optimize your code to reduce API calls

## Local Development

To run locally before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the app
streamlit run streamlit_app/app.py
```

## Updates

To update your deployed app:
1. Push changes to your GitHub repository
2. Streamlit Cloud will automatically redeploy
3. Check the dashboard for deployment status

## Support

- Streamlit Docs: [docs.streamlit.io](https://docs.streamlit.io/)
- Community Forum: [discuss.streamlit.io](https://discuss.streamlit.io/)
