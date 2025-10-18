# Social Media Trending Intelligence - Quick Start Guide

**Ready in 5 minutes!** 🚀

---

## 🎯 What You'll Build

A system that automatically:
- ✅ Discovers trending topics on YouTube, Reddit, X (Twitter)
- ✅ Extracts customer pain points from social discussions
- ✅ Predicts viral content engagement
- ✅ Generates product opportunities from market signals

---

## ⚡ Quick Start (3 Steps)

### **Step 1: Install Dependencies**

```bash
# From ManagementTeam directory
pip install -r requirements.txt
```

**What gets installed:**
- YouTube Data API client
- Hugging Face transformers (TwHIN-BERT, RoBERTa, BART)
- BERTopic for topic modeling
- All ML dependencies

### **Step 2: Test with Mock Data (No API Keys!)**

```bash
# Test full system with mock data
python agents/trend_research_agent/trend_research_agent.py
```

**Expected Output:**
```
🔍 TrendResearchAgent - Starting Trend Research
📊 Phase 1: Data Collection
  📺 YouTube: ✅ Collected 10 videos (mock)
  🔴 Reddit: ✅ Collected 10 posts (mock)
  🐦 X: ✅ Collected 10 tweets (mock)

🔥 Phase 2: Viral Pattern Analysis
  ✅ Average virality score: 65.5/100

💬 Phase 3: Pain Point Extraction
  ✅ Pain points found in 6 items (60%)
  ✅ Average severity: 6.2/10

🔬 Phase 4: Topic Discovery
  ✅ Discovered 4 topics

💡 Phase 5: Generating Recommendations
  ✅ 3 recommendations generated

✅ TrendResearchAgent - Research Complete
```

### **Step 3: Add Real API Keys (Optional)**

**Get Free API Keys:**

| Platform | Get Key | Free Tier |
|----------|---------|-----------|
| **YouTube** | [Get Key](https://console.cloud.google.com/) | 10,000 units/day |
| **Reddit** | [Get Key](https://www.reddit.com/prefs/apps) | Unlimited |
| **X (Twitter)** | [Get Key](https://developer.twitter.com/) | 1,500 tweets/month |

**Add to `.env`:**
```bash
# Copy template
cp .env.example .env

# Edit .env (add your keys)
YOUTUBE_API_KEY=your_youtube_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id  # Already added in Phase 2
REDDIT_CLIENT_SECRET=your_reddit_secret
X_BEARER_TOKEN=your_x_bearer_token
```

**Test with Real Data:**
```bash
python agents/trend_research_agent/trend_research_agent.py
```

---

## 📖 Usage Examples

### **Example 1: Standalone Pain Point Research**

```python
from src.ml.pain_point_extractor import PainPointExtractor

extractor = PainPointExtractor()

# Analyze customer feedback
texts = [
    "This app is so slow! Crashes every time.",
    "The UI is confusing, can't find settings.",
    "I wish it had dark mode. Would be perfect."
]

# Extract pain points
results = extractor.batch_extract(texts)
aggregated = extractor.aggregate_pain_points(results)

# Results
print(f"Pain point rate: {aggregated['pain_point_percentage']}%")
print(f"Top keywords: {[kw for kw, _ in aggregated['top_pain_keywords'][:5]]}")
# Output: pain_point_percentage=100%, keywords=['slow', 'crash', 'confusing', 'wish', ...]
```

### **Example 2: Predict Content Virality**

```python
from src.ml.virality_analyzer import ViralityAnalyzer

analyzer = ViralityAnalyzer()

# Compare content variants
variants = [
    "New feature: Dark mode",
    "🌙 Dark mode is live! Check it out now 😎 #DarkMode",
    "Just shipped dark mode. Feedback?"
]

comparison = analyzer.compare_variants(variants, platform="twitter")

print(f"Best: {comparison['best_variant']['text']}")
print(f"Score: {comparison['best_variant']['score']}/100")
# Output: Best="🌙 Dark mode is live...", Score=78/100
```

### **Example 3: Discover Trending Topics**

```python
from src.ml.topic_clustering import TopicClusterer

clusterer = TopicClusterer()

# Documents from social media
posts = [
    "Slow performance issues with app",
    "App crashes frequently, very buggy",
    "Love the new dark mode feature!",
    "UI is confusing, hard to navigate",
    "Performance problems, freezes often",
    # ... more posts
]

# Discover topics
result = clusterer.discover_topics(posts, min_topic_size=2)

print(f"Discovered {result['num_topics']} topics:")
for topic in result['topics']:
    print(f"  - {topic['label']}: {', '.join(topic['keywords'][:5])}")
# Output:
#   - performance_issues: slow, crash, freeze, lag, bug
#   - user_experience: UI, confusing, navigate, design, interface
```

### **Example 4: Full Trend Research**

```python
from agents.trend_research_agent.trend_research_agent import TrendResearchAgent
from core.base_agent import AgentContext

# Create context
context = AgentContext(
    session_id="research_001",
    inputs={
        "research_query": "productivity app for developers",
        "platforms": ["youtube", "reddit", "twitter"],
        "max_results": 50
    }
)

# Run research
agent = TrendResearchAgent()
result = agent.execute(context)

# Access findings
data = result.data_for_next_agent

print(f"Topics: {data['topics']['num_topics']}")
print(f"Pain points: {data['pain_points']['pain_point_percentage']}%")
print(f"Virality: {data['viral_analysis']['average_virality_score']}/100")
print(f"Recommendations: {len(data['recommendations'])}")

# Top recommendation
if data['recommendations']:
    top_rec = data['recommendations'][0]
    print(f"\nTop opportunity: {top_rec['title']}")
    print(f"Description: {top_rec['description']}")
```

---

## 🔧 Customization

### **Change Platforms**

Edit `config/trend_research_config.yaml`:
```yaml
data_collection:
  default_platforms:
    - youtube
    - reddit
    # - twitter  # Disable Twitter
```

### **Adjust Thresholds**

```yaml
thresholds:
  virality:
    high: 85  # Stricter (default: 80)

  pain_severity:
    critical: 8.5  # Stricter (default: 9.0)
```

### **Custom Topics**

```yaml
custom_topics:
  product_related:
    - "my custom topic"
    - "another topic"
```

---

## 🚀 Integration with Management Team

### **Activate in Orchestrator**

1. Edit `agents/orchestrator/agent_registry.yaml`:
```yaml
- name: TrendResearchAgent
  active: true  # Change from false
  stage: 0.5
```

2. Run orchestrator:
```bash
python agents/orchestrator/orchestrator.py
```

3. TrendResearchAgent runs first, passes data to downstream agents

### **Access Results in Other Agents**

```python
# In StrategyAgent, VerticalAgent, etc.
def execute(self, context: AgentContext) -> AgentOutput:
    # Get trend research data
    trend_data = context.get_agent_data("TrendResearchAgent")

    if trend_data:
        topics = trend_data.get("topics", {})
        pain_points = trend_data.get("pain_points", {})

        # Use in strategy decisions
        print(f"Trending topics: {topics['num_topics']}")
```

---

## 💡 Pro Tips

### **1. Start with Mock Data**

Test everything without API keys first. All modules work with mock data.

### **2. Use Individual Modules**

Don't run the full agent if you only need one component:
```python
# Just pain point extraction
from src.ml.pain_point_extractor import PainPointExtractor
extractor = PainPointExtractor()

# Just virality prediction
from src.ml.virality_analyzer import ViralityAnalyzer
analyzer = ViralityAnalyzer()
```

### **3. Optimize for Speed**

Enable GPU in config:
```yaml
ai_models:
  twhin_bert:
    device: "cuda"  # 5-10x faster
```

### **4. Manage API Quotas**

- Cache results
- Use `max_results` wisely
- Test with mock data first

---

## 📊 Output Files

After running TrendResearchAgent, find reports in:
```
outputs/trend_research/
├── research_20251017_143022.json  # Full data
└── research_20251017_143022.md    # Summary
```

**JSON Output:**
```json
{
  "research_query": "productivity app",
  "data_collected": {...},
  "viral_analysis": {...},
  "pain_points": {
    "top_pain_keywords": [
      ["slow", 12],
      ["crash", 8],
      ["confusing", 6]
    ],
    "average_severity": 6.5
  },
  "topics": {...},
  "recommendations": [...]
}
```

---

## 🐛 Common Issues

### **"Module not found: transformers"**
```bash
pip install transformers torch
```

### **"YouTube API quota exceeded"**
- Wait 24 hours OR
- Reduce `max_results` OR
- Use mock mode

### **"Out of memory"**
```yaml
# Reduce batch size in config
ai_models:
  twhin_bert:
    batch_size: 16  # Default: 32
```

### **"No pain points detected"**
- Check if text contains pain keywords
- Increase dataset size (need 10+ items)
- Lower severity threshold

---

## 🎓 Next Steps

1. **Read Full Documentation:** `docs/system/TREND_RESEARCH_SYSTEM.md`
2. **Customize Config:** `config/trend_research_config.yaml`
3. **Integrate with Workflow:** Add to orchestrator
4. **Build Custom Tools:** Use modules in your own apps

---

## 🆘 Need Help?

- **Documentation:** `docs/system/TREND_RESEARCH_SYSTEM.md`
- **API Setup:** `docs/setup/API_KEYS_SETUP_GUIDE.md`
- **Config Reference:** `config/trend_research_config.yaml`

---

**Happy Trending! 🚀**

Last Updated: 2025-10-17
Version: 1.0
