# Social Media Trending Intelligence System

**Version:** 1.0
**Status:** Production Ready
**Integration:** Management Team Ecosystem
**Created:** 2025-10-17

---

## 🎯 Purpose

The Social Media Trending Intelligence System discovers trending topics, viral content patterns, and customer pain points across social media platforms. It provides actionable insights for:

- **Product Discovery:** Identify customer problems and unmet needs
- **Market Validation:** Validate demand through social signals
- **Content Strategy:** Understand what content resonates
- **Competitive Intelligence:** Track market trends and conversations

---

## 🏗️ System Architecture

### **Modular Design**

The system is built following the Management Team's modular architecture principles:

```
Social Media Trending Intelligence System
│
├── Connectors Layer (Reusable Utilities)
│   ├── YouTubeConnector
│   ├── RedditConnector (Enhanced)
│   ├── XConnector (Enhanced)
│   └── LinkedInConnector (Future)
│
├── AI Analysis Layer (Portable ML Modules)
│   ├── TwHINPredictor (Engagement Prediction)
│   ├── ViralityAnalyzer (Multi-Model Virality)
│   ├── PainPointExtractor (NER + Sentiment)
│   └── TopicClusterer (BERTopic)
│
└── Agent Layer (BaseAgent Integration)
    └── TrendResearchAgent (Orchestrates all components)
```

### **Key Principles**

✅ **Modularity:** Each component works standalone OR within Management Team
✅ **Reusability:** All modules usable across different applications
✅ **BaseAgent Pattern:** Follows Management Team agent standards
✅ **YAML-Driven:** Behavior configured via YAML files
✅ **Zero-Config:** Works out-of-box with mock data, real APIs optional

---

## 📦 Components

### **1. Data Connectors**

#### **YouTubeConnector** (`src/integrations/youtube_connector.py`)

**Purpose:** Fetch trending videos and analyze viral patterns

**Features:**
- Get trending videos by region/category
- Search videos by keyword
- Analyze viral patterns (tags, titles, engagement)
- Track quota usage (10,000 units/day free)

**API:** YouTube Data API v3
**Quota Costs:** Search (100), Video Details (1)

**Example:**
```python
from src.integrations.youtube_connector import YouTubeConnector

youtube = YouTubeConnector()
trending = youtube.get_trending_videos(region_code="US", max_results=50)
patterns = youtube.analyze_viral_patterns(trending['videos'])
```

#### **RedditConnector** (Enhanced)

Already exists in Phase 2. Collects pain points from subreddit discussions.

#### **XConnector** (Enhanced)

Already exists in Phase 2. Analyzes tweets for sentiment and engagement.

---

### **2. AI Analysis Modules**

#### **TwHINPredictor** (`src/ml/twhin_predictor.py`)

**Purpose:** Predict social media engagement using Twitter's TwHIN-BERT

**Model:** `Twitter/twhin-bert-base` (110M parameters)
**Training Data:** 7 billion tweets with social engagement signals
**Use Case:** Engagement prediction, virality scoring

**Features:**
- Predict engagement score (0-100)
- Estimate likes/shares/comments multipliers
- Content feature analysis (hashtags, emojis, length)
- Compare content variants

**Example:**
```python
from src.ml.twhin_predictor import TwHINPredictor

predictor = TwHINPredictor()
result = predictor.predict_engagement(
    "Check out our new app! 🚀 #productivity"
)
# Output: engagement_score=75, engagement_level="high"
```

#### **ViralityAnalyzer** (`src/ml/virality_analyzer.py`)

**Purpose:** Multi-model virality prediction combining sentiment, engagement, topics

**Models Used:**
- `cardiffnlp/twitter-roberta-base-sentiment` (Sentiment)
- `Twitter/twhin-bert-base` (Engagement)
- `facebook/bart-large-mnli` (Zero-shot topics)

**Platform Weights:**
- Twitter: sentiment(25%) + engagement(50%) + topic(25%)
- Reddit: sentiment(35%) + engagement(30%) + topic(35%)
- YouTube: sentiment(20%) + engagement(40%) + topic(40%)

**Example:**
```python
from src.ml.virality_analyzer import ViralityAnalyzer

analyzer = ViralityAnalyzer()
result = analyzer.analyze_virality(
    text="New feature launch! 🔥",
    platform="twitter",
    context={"follower_count": 5000}
)
# Output: virality_score=82, probability_viral=87%
```

#### **PainPointExtractor** (`src/ml/pain_point_extractor.py`)

**Purpose:** Extract customer pain points, frustrations, and problems

**Models:**
- `dslim/bert-base-NER` (Entity extraction)
- `cardiffnlp/twitter-roberta-base-sentiment` (Frustration detection)
- `facebook/bart-large-mnli` (Problem categorization)

**Categories:**
- Performance issue
- Usability problem
- Missing feature
- Pricing concern
- Reliability issue
- Integration problem
- Documentation issue

**Example:**
```python
from src.ml.pain_point_extractor import PainPointExtractor

extractor = PainPointExtractor()
result = extractor.extract_pain_points(
    "This app is so slow! Crashes every time I export data."
)
# Output: severity=8.5/10, category="reliability issue"
```

#### **TopicClusterer** (`src/ml/topic_clustering.py`)

**Purpose:** Discover trending topics using BERTopic zero-shot modeling

**Model:** BERTopic + `all-MiniLM-L6-v2` embeddings
**Approach:** Zero-shot (no training data needed)

**Features:**
- Auto-discover topics in text corpus
- Track trending topics over time
- Hierarchical topic clustering
- Custom topic labels

**Example:**
```python
from src.ml.topic_clustering import TopicClusterer

clusterer = TopicClusterer()
result = clusterer.discover_topics(posts, min_topic_size=10)
# Output: 5 topics discovered with keywords
```

---

### **3. TrendResearchAgent** (BaseAgent)

#### **Overview**

**Location:** `agents/trend_research_agent/trend_research_agent.py`
**Inherits:** `BaseAgent`
**Dependencies:** None (runs first, early research stage)
**Stage:** 0.5 (before StrategyAgent)

**Purpose:**
Orchestrates all connectors and AI models to provide comprehensive trending intelligence.

#### **Execution Flow**

```
1. Data Collection
   ├── YouTube: Trending videos
   ├── Reddit: Pain point discussions
   └── X (Twitter): Sentiment & engagement

2. Viral Analysis
   └── Analyze content virality across platforms

3. Pain Point Extraction
   └── Extract and categorize customer problems

4. Topic Discovery
   └── Discover trending topics with BERTopic

5. Generate Recommendations
   └── Actionable insights based on findings
```

#### **Inputs**

Required in `context.inputs`:
```python
{
    "research_query": "productivity app for developers",
    "platforms": ["youtube", "reddit", "twitter"],
    "max_results": 50,
    "config_path": "config/trend_research_config.yaml"  # Optional
}
```

#### **Outputs**

Returns `AgentOutput` with:
```python
{
    "research_query": str,
    "data_collected": {
        "total_items": int,
        "by_platform": dict
    },
    "viral_analysis": {
        "average_virality_score": float,
        "high_viral_count": int,
        "viral_patterns": dict
    },
    "pain_points": {
        "pain_point_percentage": float,
        "average_severity": float,
        "top_pain_keywords": list
    },
    "topics": {
        "num_topics": int,
        "topics": list
    },
    "recommendations": list
}
```

#### **Using TrendResearchAgent**

**Standalone:**
```python
from agents.trend_research_agent.trend_research_agent import TrendResearchAgent
from core.base_agent import AgentContext

context = AgentContext(
    session_id="test_123",
    inputs={
        "research_query": "AI productivity tools",
        "platforms": ["youtube", "reddit"],
        "max_results": 30
    }
)

agent = TrendResearchAgent()
result = agent.execute(context)

print(f"Confidence: {result.confidence}")
print(f"Recommendations: {len(result.data_for_next_agent['recommendations'])}")
```

**In Management Team Orchestrator:**
1. Edit `agents/orchestrator/agent_registry.yaml`
2. Set `TrendResearchAgent` to `active: true`
3. Run orchestrator:
   ```bash
   python agents/orchestrator/orchestrator.py
   ```

---

## 🚀 Setup & Installation

### **1. Install Dependencies**

```bash
# Install all required packages
pip install -r requirements.txt
```

**New Dependencies Added:**
- `google-api-python-client` - YouTube Data API
- `transformers` - Hugging Face models
- `torch` - PyTorch backend
- `sentence-transformers` - Embeddings
- `bertopic` - Topic modeling
- `umap-learn` - Dimensionality reduction
- `hdbscan` - Clustering

### **2. Configure API Keys**

**Create `.env` file:**
```bash
cp .env.example .env
```

**Add credentials:**
```bash
# YouTube
YOUTUBE_API_KEY=your_youtube_api_key_here

# Reddit (already configured in Phase 2)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret

# X (Twitter) (already configured in Phase 2)
X_BEARER_TOKEN=your_x_bearer_token
```

**Get API Keys:**

| Platform | URL | Free Tier |
|----------|-----|-----------|
| **YouTube** | https://console.cloud.google.com/ | 10,000 units/day |
| **Reddit** | https://www.reddit.com/prefs/apps | Yes |
| **X (Twitter)** | https://developer.twitter.com/ | 1,500 tweets/month |

### **3. Test Installation**

```bash
# Test YouTube connector
python src/integrations/youtube_connector.py

# Test AI models
python src/ml/twhin_predictor.py
python src/ml/virality_analyzer.py
python src/ml/pain_point_extractor.py
python src/ml/topic_clustering.py

# Test full agent
python agents/trend_research_agent/trend_research_agent.py
```

---

## 📊 Usage Examples

### **Example 1: Research Trending Topics**

```python
from agents.trend_research_agent.trend_research_agent import TrendResearchAgent
from core.base_agent import AgentContext

context = AgentContext(
    session_id="research_001",
    inputs={
        "research_query": "SaaS productivity tools",
        "platforms": ["youtube", "reddit", "twitter"],
        "max_results": 100
    }
)

agent = TrendResearchAgent()
result = agent.execute(context)

# Access findings
data = result.data_for_next_agent
print(f"Topics discovered: {data['topics']['num_topics']}")
print(f"Pain points: {data['pain_points']['pain_point_percentage']}%")
print(f"Recommendations: {len(data['recommendations'])}")
```

### **Example 2: Standalone Viral Analysis**

```python
from src.ml.virality_analyzer import ViralityAnalyzer

analyzer = ViralityAnalyzer()

# Compare content variants
variants = [
    "New feature: Dark mode",
    "🌙 Dark mode is live! Switch now 😎 #DarkMode",
    "Just shipped dark mode. Feedback welcome!"
]

comparison = analyzer.compare_variants(variants, platform="twitter")

print(f"Best variant: {comparison['best_variant']['text']}")
print(f"Score: {comparison['best_variant']['score']}/100")
```

### **Example 3: Extract Pain Points from Reddit**

```python
from src.integrations.reddit_connector import RedditConnector
from src.ml.pain_point_extractor import PainPointExtractor

# Collect data
reddit = RedditConnector()
posts = reddit.search_pain_points(
    "productivity app problems",
    subreddits=["productivity"],
    limit=50
)

# Extract pain points
extractor = PainPointExtractor()
texts = [post['title'] + " " + post['selftext'] for post in posts['posts']]
results = extractor.batch_extract(texts)

# Aggregate
aggregated = extractor.aggregate_pain_points(results)
print(f"Pain point rate: {aggregated['pain_point_percentage']}%")
print(f"Top pain keywords: {[kw for kw, _ in aggregated['top_pain_keywords'][:5]]}")
```

---

## 🔧 Configuration

### **Config File**

Location: `config/trend_research_config.yaml`

**Key Sections:**
- `data_collection`: Platform settings, rate limits
- `ai_models`: Model selection and parameters
- `thresholds`: Virality, pain severity thresholds
- `reporting`: Output formats and paths
- `custom_topics`: Zero-shot classification topics

**Example Customization:**
```yaml
data_collection:
  max_results_per_platform:
    youtube: 100
    reddit: 200
    twitter: 150

ai_models:
  twhin_bert:
    batch_size: 64
    device: "cuda"  # Use GPU

thresholds:
  virality:
    high: 85  # Stricter threshold
```

---

## 📈 Performance & Optimization

### **Resource Usage**

| Component | RAM | GPU | Speed |
|-----------|-----|-----|-------|
| **YouTubeConnector** | Low | None | Fast (API) |
| **TwHIN-BERT** | 2GB | Optional | Medium |
| **Virality Analyzer** | 3GB | Optional | Medium |
| **Pain Point Extractor** | 2GB | Optional | Medium |
| **BERTopic** | 1.5GB | Optional | Slow (first run) |

### **Optimization Tips**

1. **Use GPU:** Set `device: "cuda"` in config for 5-10x speedup
2. **Batch Processing:** Process in batches of 50-100 items
3. **Caching:** Enable caching to avoid re-processing
4. **Mock Mode:** Use mock data for testing without API calls
5. **Parallel Collection:** Enable `use_parallel_collection: true`

### **API Quota Management**

- **YouTube:** 10,000 units/day (search=100 units, video=1 unit)
- **Reddit:** 60 requests/minute
- **X:** 1,500 tweets/month (free tier)

**Strategy:** Cache results, use mock mode for development, batch requests.

---

## 🧪 Testing

### **Unit Tests**

Each module has built-in tests:
```bash
# Test individual modules
python src/integrations/youtube_connector.py
python src/ml/twhin_predictor.py
python src/ml/virality_analyzer.py
python src/ml/pain_point_extractor.py
python src/ml/topic_clustering.py
```

### **Integration Test**

Full agent test:
```bash
python agents/trend_research_agent/trend_research_agent.py
```

### **Mock Mode**

All components work without API keys using mock data:
```python
# No API keys needed - uses mock data
youtube = YouTubeConnector()  # Works without YOUTUBE_API_KEY
predictor = TwHINPredictor()  # Works without transformers installed
```

---

## 🔌 Integration with Management Team

### **Agent Registry**

**File:** `agents/orchestrator/agent_registry.yaml`

```yaml
- name: TrendResearchAgent
  path: "agents.trend_research_agent.trend_research_agent:TrendResearchAgent"
  active: false  # Set to true to enable
  stage: 0.5  # Runs early (before strategy)
```

### **Data Flow**

```
TrendResearchAgent (Stage 0.5)
    ↓
StrategyAgent (Stage 1) ← Receives trending topics
    ↓
VerticalAgent (Stage 1.5) ← Receives pain points for scoring
    ↓
Technical Architect (Stage 2)
    ↓
... rest of pipeline
```

### **Passing Data to Other Agents**

```python
# TrendResearchAgent output available to downstream agents
context.shared_data["TrendResearchAgent"] = AgentOutput(
    data_for_next_agent={
        "trending_topics": [...],
        "pain_points": [...],
        "viral_patterns": {...}
    }
)

# StrategyAgent can access it
strategy_data = context.get_agent_data("TrendResearchAgent")
trending_topics = strategy_data.get("trending_topics", [])
```

---

## 📝 Best Practices

### **1. Modular Usage**

✅ **DO:** Use modules independently for specific tasks
```python
# Use just pain point extraction
from src.ml.pain_point_extractor import PainPointExtractor
extractor = PainPointExtractor()
```

❌ **DON'T:** Run full agent when you only need one component

### **2. API Keys**

✅ **DO:** Store in `.env` file (gitignored)
❌ **DON'T:** Hardcode in scripts or commit to git

### **3. Quota Management**

✅ **DO:** Use caching, mock mode for testing
❌ **DON'T:** Repeatedly fetch same data

### **4. Error Handling**

All modules gracefully fall back to mock data when:
- API keys missing
- Models not installed
- Rate limits exceeded

---

## 🐛 Troubleshooting

### **Issue:** "Module not found: transformers"
**Solution:** `pip install transformers torch`

### **Issue:** "YouTube API quota exceeded"
**Solution:** Wait 24 hours or reduce `max_results`

### **Issue:** "Out of memory"
**Solution:** Reduce `batch_size` in config or use `device: "cpu"`

### **Issue:** "No pain points detected"
**Solution:** Check if text contains pain keywords, increase dataset size

---

## 📚 Related Documentation

- **BaseAgent Pattern:** `docs/system/base_agent.md`
- **Agent Registry:** `docs/system/orchestrator_README.md`
- **Evidence Collector:** Phase 2 documentation
- **API Setup:** `docs/setup/API_KEYS_SETUP_GUIDE.md`

---

## 🎓 Learn More

### **Models**

- TwHIN-BERT: https://arxiv.org/abs/2209.07562
- BERTopic: https://arxiv.org/abs/2203.05794
- RoBERTa Sentiment: https://github.com/cardiffnlp/tweeteval

### **APIs**

- YouTube Data API: https://developers.google.com/youtube/v3
- Reddit API: https://www.reddit.com/dev/api
- X (Twitter) API: https://developer.twitter.com

---

**Version:** 1.0
**Last Updated:** 2025-10-17
**Maintainer:** Management Team System
**Status:** ✅ Production Ready
