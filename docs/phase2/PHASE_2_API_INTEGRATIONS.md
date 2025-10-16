# Phase 2: API Integrations & ML Predictions

**Status:** ✅ Complete
**Date:** 2025-10-16
**Version:** 4.0.0

---

## Overview

Phase 2 adds powerful automated evidence collection and ML-based predictions to the Variant Exploration System. This significantly reduces manual research time and improves decision quality.

---

## 🎯 Features Implemented

### 1. Reddit API Integration ✅
**File:** `src/integrations/reddit_connector.py`

**Capabilities:**
- Search subreddits for pain points and discussions
- Sentiment analysis of posts and comments
- Pain point extraction and ranking
- Competitor mention tracking
- Trending topics analysis

**Usage:**
```python
from src.integrations.reddit_connector import RedditConnector

reddit = RedditConnector()
results = reddit.search_pain_points(
    "productivity app",
    subreddits=["productivity", "smallbusiness"],
    time_filter="month",
    limit=100
)
```

**Output:**
- Total posts analyzed
- Pain points with frequency and sentiment
- Top discussions with links
- Sentiment distribution

---

### 2. Google Trends Integration ✅
**File:** `src/integrations/google_trends_connector.py`

**Capabilities:**
- Track search interest over time
- Compare multiple keywords
- Geographic interest analysis
- Related queries and topics
- Trend direction detection (rising/declining/stable)

**Usage:**
```python
from src.integrations.google_trends_connector import GoogleTrendsConnector

trends = GoogleTrendsConnector()
results = trends.analyze_interest("productivity app", timeframe="today 12-m")
comparison = trends.compare_keywords(["productivity app", "task manager", "todo list"])
```

**Output:**
- Interest over time with statistics
- Related and rising queries
- Regional interest breakdown
- Market size indicators

---

### 3. X (Twitter) Integration ✅
**File:** `src/integrations/x_connector.py`

**Capabilities:**
- Search tweets related to topics
- Sentiment analysis of social signals
- Influencer identification
- Engagement metrics tracking
- Competitor mention analysis

**Usage:**
```python
from src.integrations.x_connector import XConnector

x_api = XConnector()
results = x_api.search_sentiment("productivity app", limit=100)
```

**Output:**
- Total tweets with sentiment analysis
- Top influential tweets
- Social proof indicators
- Engagement metrics

---

### 4. Unified Evidence Collector ✅
**File:** `src/integrations/evidence_collector.py`

**Capabilities:**
- Parallel data collection from all sources
- Unified evidence scoring (0-100)
- Cross-platform sentiment aggregation
- Automated insight generation
- Evidence report generation (JSON + Markdown)

**Usage:**
```python
from src.integrations.evidence_collector import EvidenceCollector

collector = EvidenceCollector()
evidence = collector.collect_all_evidence(
    idea="productivity app for developers",
    keywords=["task management", "code tracking"],
    subreddits=["programming", "productivity"]
)

# Save report
collector.save_evidence_report(evidence, "outputs/evidence/my_idea.json")
```

**Output:**
- Evidence score (0-100)
- Multi-source insights
- GO/NO-GO recommendation
- Detailed JSON + Markdown reports

---

### 5. ML-Based Scoring Predictor ✅
**File:** `src/ml/scoring_predictor.py`

**Capabilities:**
- Multi-factor success prediction
- Historical pattern recognition
- Feature importance analysis
- Confidence scoring
- Continuous learning from outcomes

**Usage:**
```python
from src.ml.scoring_predictor import ScoringPredictor

predictor = ScoringPredictor()
prediction = predictor.predict_success(idea_data)

print(f"Success Probability: {prediction['success_probability']}%")
print(f"Predicted Score: {prediction['predicted_score']}")
print(f"Recommendation: {prediction['recommendation']}")
```

**Features Used:**
- Evidence scores (Reddit, Trends, X)
- RICE/ICE scores
- Pain point metrics
- Unit economics (LTV:CAC, payback)
- Risk assessment
- Competitive landscape

---

## 📊 Evidence Score Calculation

The Evidence Collector generates a comprehensive score (0-100) based on:

| Source | Weight | Criteria |
|--------|--------|----------|
| **Reddit** | 40% | Post volume (25%) + Pain points (15%) |
| **Google Trends** | 30% | Average search interest |
| **X (Twitter)** | 30% | Tweet volume (20%) + Sentiment (10%) |

**Score Interpretation:**
- **80-100**: Strong market validation
- **60-79**: Good validation, proceed with confidence
- **40-59**: Moderate validation, additional research recommended
- **20-39**: Weak validation, significant risk
- **0-19**: Very weak validation, reconsider idea

---

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**New dependencies:**
- `praw` - Reddit API
- `pytrends` - Google Trends API
- `tweepy` - X (Twitter) API
- `textblob` - Sentiment analysis
- `scikit-learn` - ML predictions
- `joblib` - Model persistence

### 2. Configure API Credentials

Create `config/api_config.json` from the example:

```bash
cp config/api_config.example.json config/api_config.json
```

Edit `config/api_config.json` with your credentials:

```json
{
  "reddit": {
    "client_id": "YOUR_REDDIT_CLIENT_ID",
    "client_secret": "YOUR_REDDIT_CLIENT_SECRET",
    "user_agent": "VES Market Research Bot v1.0"
  },
  "x": {
    "bearer_token": "YOUR_X_BEARER_TOKEN"
  }
}
```

**Or use environment variables:**

```bash
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_secret"
export X_BEARER_TOKEN="your_bearer_token"
```

### 3. Get API Credentials

#### Reddit API
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script" type
4. Copy Client ID and Secret

#### X (Twitter) API
1. Go to https://developer.twitter.com/
2. Create a project and app
3. Generate Bearer Token (OAuth 2.0)
4. Copy the bearer token

#### Google Trends
- No API key required! Uses `pytrends` library

---

## 💡 Usage Examples

### Example 1: Complete Evidence Collection

```python
from src.integrations.evidence_collector import EvidenceCollector

# Initialize
collector = EvidenceCollector(config_path="config/api_config.json")

# Collect evidence
evidence = collector.collect_all_evidence(
    idea="AI-powered email assistant",
    keywords=["email management", "inbox zero"],
    subreddits=["productivity", "Entrepreneur"],
    parallel=True  # Fast parallel collection
)

# Results
print(f"Evidence Score: {evidence['evidence_score']}/100")
print(f"Recommendation: {evidence['unified_insights']['recommendation']}")

# Save reports
collector.save_evidence_report(evidence, "outputs/evidence/email_assistant.json")
```

### Example 2: ML Prediction

```python
from src.ml.scoring_predictor import ScoringPredictor

# Initialize predictor
predictor = ScoringPredictor()

# Prepare idea data (from evidence + other sources)
idea_data = {
    "evidence": evidence,
    "scores": {"rice_total": 75, "ice_score": 8.5},
    "economics": {"ltv_cac_ratio": 5.0, "payback_months": 6},
    "risks": {"high": 2, "medium": 5, "total": 12}
}

# Predict
prediction = predictor.predict_success(idea_data)

print(f"Success Probability: {prediction['success_probability']}%")
print(f"Confidence: {prediction['confidence']}")
print(f"Recommendation: {prediction['recommendation']}")

# Feature importance
for feature in prediction['feature_importance'][:5]:
    print(f"  {feature['feature']}: {feature['importance']}")
```

### Example 3: Individual Connectors

```python
# Reddit only
from src.integrations.reddit_connector import RedditConnector
reddit = RedditConnector()
pain_points = reddit.search_pain_points("productivity app")

# Google Trends only
from src.integrations.google_trends_connector import GoogleTrendsConnector
trends = GoogleTrendsConnector()
interest = trends.analyze_interest("productivity app")

# X only
from src.integrations.x_connector import XConnector
x_api = XConnector()
sentiment = x_api.search_sentiment("productivity app")
```

---

## 🧪 Testing

### Mock Mode (No API Keys)
All connectors work in mock mode without API keys:

```python
# Will use mock data automatically
reddit = RedditConnector()  # No config needed
results = reddit.search_pain_points("test query")
# Returns mock data with note
```

### With API Keys
Provide configuration for real data:

```python
reddit = RedditConnector(config_path="config/api_config.json")
results = reddit.search_pain_points("real query")
# Returns real Reddit data
```

---

## 📈 Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Reddit search (100 posts) | ~30-60s | Rate limited by Reddit |
| Google Trends analysis | ~5-10s | Fast, no rate limits |
| X search (100 tweets) | ~10-20s | Depends on API tier |
| **Parallel collection** | ~40-70s | All 3 sources simultaneously |
| ML prediction | ~0.1s | Very fast once trained |

**Optimization:**
- Use `parallel=True` for evidence collection
- Cache results for repeat queries
- Adjust `limit` parameter for faster testing

---

## 🎓 ML Model Training

The ML model can learn from historical data:

```python
from src.ml.scoring_predictor import ScoringPredictor

predictor = ScoringPredictor()

# Historical data with outcomes
training_data = [
    {
        "evidence": {...},
        "scores": {...},
        "outcome": {"success": True, "final_score": 85}
    },
    # ... more examples
]

# Train model
predictor.train_model(training_data)
# Model auto-saved to data/ml_models/
```

**Model improves over time** as more outcomes are recorded!

---

## 🔒 Privacy & Rate Limits

### Reddit
- Rate limit: ~60 requests/minute
- Respect subreddit rules
- Use descriptive user agent

### Google Trends
- No authentication required
- Rate limits are generous
- Data is aggregated/anonymized

### X (Twitter)
- Free tier: 1,500 tweets/month
- Basic tier: 10,000 tweets/month
- Respect user privacy

**Best Practice:** Use mock mode for development, real APIs for production.

---

## 📊 Output Examples

### Evidence Report (Markdown)

```markdown
# Evidence Collection Report

**Idea:** AI-powered email assistant
**Evidence Score:** 78/100

## Overall Assessment
**Recommendation:** ✅ STRONG GO - Clear market demand with validated pain points

### Market Validation
- Reddit: 64 posts, 18 pain points
- Google Trends: Rising interest (avg: 72/100)
- X: 89 tweets, positive sentiment

## Pain Points
1. "email overload" - 12 mentions
2. "inbox management" - 8 mentions
3. "time consuming" - 6 mentions
```

### ML Prediction Output

```json
{
  "success_probability": 76.5,
  "predicted_score": 74.2,
  "confidence": 0.82,
  "recommendation": "✅ GO - Model shows positive indicators",
  "feature_importance": [
    {"feature": "evidence_score", "importance": 0.245},
    {"feature": "trends_direction", "importance": 0.189},
    {"feature": "reddit_pain_points", "importance": 0.156}
  ]
}
```

---

## 🚀 Next Steps

1. **Set up API credentials** (see Setup section)
2. **Run example collection** to verify setup
3. **Integrate into orchestrator** for automated evidence gathering
4. **Collect outcomes** to train ML model
5. **Monitor and improve** based on prediction accuracy

---

## 📚 API Documentation

- [Reddit API (PRAW)](https://praw.readthedocs.io/)
- [Google Trends (pytrends)](https://pypi.org/project/pytrends/)
- [X API (Tweepy)](https://docs.tweepy.org/)
- [TextBlob (Sentiment)](https://textblob.readthedocs.io/)
- [scikit-learn](https://scikit-learn.org/)

---

**Phase 2 Complete! 🎉**

The system now has powerful automated research and predictive capabilities, significantly reducing manual work while improving decision quality.
