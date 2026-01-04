# API Keys Setup Guide - Environment Variables

**Status:** Ready to use
**Method:** Environment Variables (.env file)
**Security:** ✅ Secure (not committed to git)

---

## 🎯 Quick Start

### Option 1: Interactive Setup (Recommended)

```bash
./setup_api_keys.sh
```

Follow the prompts to enter your credentials.

### Option 2: Manual Setup

```bash
# Copy template from config directory (single source of truth)
cp config/.env.example config/.env

# Edit with your credentials
nano config/.env  # or vim, code, etc.
```

**Note:** All credentials are now managed in `config/.env` through the centralized `env_manager.py` system.

---

## 📋 Getting API Credentials

### 1. Reddit API (Required for Reddit connector)

**Steps:**
1. Go to: https://www.reddit.com/prefs/apps
2. Click **"Create App"** or **"Create Another App"**
3. Fill in:
   - **Name**: `VES Market Research Bot`
   - **App type**: Select **"script"**
   - **Description**: `Market research for idea validation`
   - **About URL**: (leave blank)
   - **Redirect URI**: `http://localhost:8080`
4. Click **"Create app"**
5. Copy these values:
   - **Client ID**: The string under "personal use script"
     - Example: `abc123XYZ_defGHI`
   - **Secret**: Next to the word "secret"
     - Example: `1234567890abcdefghijklmnop`

**Add to config/.env:**
```bash
REDDIT_CLIENT_ID=abc123XYZ_defGHI
REDDIT_CLIENT_SECRET=1234567890abcdefghijklmnop
REDDIT_USER_AGENT=VES Market Research Bot v1.0
```

---

### 2. X (Twitter) API (Required for X connector)

**Steps:**
1. Go to: https://developer.twitter.com/
2. Sign up for **Developer Account** (free tier available)
3. Create a **Project** and **App**
4. Go to **"Keys and Tokens"** tab
5. Generate **Bearer Token** (OAuth 2.0)
   - This is the easiest option!
6. Copy the Bearer Token
   - Example: `AAAAAAAAAAAAAAAAAAAAAMLheAAAAAAA0%2BuSeid...`

**Add to config/.env:**
```bash
X_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAMLheAAAAAAA0%2BuSeid...
```

**X API Tiers:**
- **Free**: 1,500 tweets/month (good for testing)
- **Basic**: $100/month, 10,000 tweets/month
- **Pro**: $5,000/month, 1M tweets/month

**Note:** Free tier is sufficient for validation!

---

### 3. Google Trends (No Setup Required!)

✅ **No API key needed!**

Google Trends works automatically via the `pytrends` library.

---

## 🔧 Configuration Methods

### Method 1: Centralized .env File (Recommended)

**Create config/.env:**
```bash
cp config/.env.example config/.env
```

**Edit config/.env:**
```bash
REDDIT_CLIENT_ID=your_actual_client_id
REDDIT_CLIENT_SECRET=your_actual_secret
REDDIT_USER_AGENT=VES Market Research Bot v1.0
X_BEARER_TOKEN=your_actual_bearer_token
YOUTUBE_API_KEY=your_actual_youtube_key
```

**The code loads it automatically!** (via centralized `config/env_manager.py`)

---

### Method 2: Export in Shell

```bash
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_secret"
export X_BEARER_TOKEN="your_bearer_token"

# Run your script
python test_phase2.py
```

---

### Method 3: Python Script (Using Centralized Config)

```python
from config.env_manager import get_config

# Load configuration (validates credentials automatically)
config = get_config()

# Access credentials via type-safe properties
print(f"Reddit configured: {bool(config.reddit_client_id)}")
print(f"X configured: {bool(config.x_bearer_token)}")
print(f"YouTube configured: {bool(config.youtube_api_key)}")

# Now run your code - connectors will use env_manager automatically
from src.integrations.evidence_collector import EvidenceCollector
collector = EvidenceCollector()
```

---

## ✅ Verify Setup

### Test Individual Connectors

**Reddit:**
```bash
python -c "
import os
from src.integrations.reddit_connector import RedditConnector
reddit = RedditConnector()
print('✅ Reddit configured!' if reddit.reddit else '❌ Not configured')
"
```

**X (Twitter):**
```bash
python -c "
import os
from src.integrations.x_connector import XConnector
x = XConnector()
print('✅ X configured!' if x.client else '❌ Not configured')
"
```

**Google Trends:**
```bash
python -c "
from src.integrations.google_trends_connector import GoogleTrendsConnector
trends = GoogleTrendsConnector()
print('✅ Google Trends configured!' if trends.pytrends else '❌ Not configured')
"
```

### Full Integration Test

```bash
python test_phase2.py
```

**Expected Output (with real keys):**
```
✅ Reddit connector: 50+ posts
✅ Google Trends connector: Average interest > 0
✅ X connector: 100+ tweets
✅ Evidence Score: 60-80/100 (real data)
```

---

## 🔒 Security Best Practices

### ✅ DO:
- ✅ Use `.env` file (not committed to git)
- ✅ Use environment variables
- ✅ Keep credentials private
- ✅ Rotate keys periodically
- ✅ Use read-only API permissions

### ❌ DON'T:
- ❌ Commit `config/.env` to git (it's in `.gitignore`)
- ❌ Share credentials in public repos
- ❌ Hardcode keys in code
- ❌ Use production keys in development
- ❌ Bypass `env_manager.py` - always use centralized config system

---

## 🐛 Troubleshooting

### "Reddit API not configured"
**Solution:**
```bash
# Check if config/.env exists
ls -la config/.env

# Test env_manager
python config/env_manager.py

# Check if variables are set
echo $REDDIT_CLIENT_ID

# If using shell, load config/.env manually
export $(cat config/.env | xargs)
```

### "X API rate limited"
**Solution:**
- Free tier: 1,500 tweets/month
- Wait for rate limit reset
- Reduce `limit` parameter in search

### "Google Trends 429 error"
**Solution:**
- Too many requests
- Wait a few minutes
- Use longer `timeframe` (reduces requests)

### "Module not found"
**Solution:**
```bash
pip install python-dotenv
```

---

## 📊 Rate Limits

| Service | Free Tier | Limit | Reset |
|---------|-----------|-------|-------|
| **Reddit** | Yes | 60 req/min | Per minute |
| **X (Twitter)** | Yes | 1,500 tweets/month | Monthly |
| **Google Trends** | Yes | ~100 req/hour | Hourly |

**Tips:**
- Use `parallel=True` for faster collection
- Cache results to avoid repeated API calls
- Adjust `limit` parameter for testing

---

## 📖 Examples

### Example 1: Full Evidence Collection

```python
# Credentials loaded automatically via env_manager.py
from src.integrations.evidence_collector import EvidenceCollector

collector = EvidenceCollector()
evidence = collector.collect_all_evidence(
    idea="AI-powered email assistant",
    keywords=["email management", "inbox zero"],
    subreddits=["productivity", "Entrepreneur"],
    parallel=True
)

print(f"Evidence Score: {evidence['evidence_score']}/100")
print(f"Recommendation: {evidence['unified_insights']['recommendation']}")
```

### Example 2: Reddit Only

```python
# Credentials loaded automatically via env_manager.py
from src.integrations.reddit_connector import RedditConnector

reddit = RedditConnector()
results = reddit.search_pain_points(
    "productivity app problems",
    subreddits=["productivity"],
    limit=50
)

for pain in results['pain_points'][:5]:
    print(f"- {pain['keyword']}: {pain['frequency']} mentions")
```

### Example 3: Google Trends Only

```python
from src.integrations.google_trends_connector import GoogleTrendsConnector

trends = GoogleTrendsConnector()
results = trends.analyze_interest("productivity app", timeframe="today 12-m")

print(f"Average Interest: {results['interest_over_time']['summary']['avg']}")
print(f"Trend: {results['interest_over_time']['summary']['trend']}")
```

---

## 🎯 Next Steps

1. ✅ Get API credentials (Reddit, X, YouTube)
2. ✅ Create `config/.env` file from template
3. ✅ Add credentials to `config/.env`
4. ✅ Test configuration: `python config/env_manager.py`
5. ✅ Run `python test_phase2.py`
6. ✅ Start collecting real evidence!

---

## 📚 Centralized Credential Management

**All credentials are now managed through `config/env_manager.py`:**

- ✅ **Single source of truth:** `config/.env`
- ✅ **Type-safe access:** Python dataclass with validation
- ✅ **Automatic loading:** No manual `load_dotenv()` needed
- ✅ **Graceful fallback:** Works without optional API keys
- ✅ **Easy testing:** `python config/env_manager.py` shows status

**Benefits:**
- No scattered `os.getenv()` calls throughout codebase
- Validation on startup (fail fast with helpful errors)
- Consistent credential management across all integrations
- Easy to add new credentials (single file to update)

---

## 📚 Additional Resources

- [Reddit API Documentation](https://www.reddit.com/dev/api)
- [X API Documentation](https://developer.twitter.com/en/docs)
- [pytrends Documentation](https://pypi.org/project/pytrends/)
- [python-dotenv Documentation](https://pypi.org/project/python-dotenv/)

---

**Need Help?** Check the troubleshooting section or review the example scripts.
