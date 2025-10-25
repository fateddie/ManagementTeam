# Market Validation Engine (MVE)
## Purpose
A modular, reusable system for validating any product or application idea by collecting, analyzing, and scoring real-world market signals.

---

## 🧭 Overview
The MVE transforms **raw human conversation** (Reddit, X/Twitter, Quora, reviews, etc.) and **search intent data** (Google Trends, YouTube, Keyword Planner) into structured insight:

> **Idea → Keywords → Data → Insights → Copy → Validation Score**

---

## ⚙️ Core Modules

| Module | Name | Responsibility | Input | Output | Reusable? |
|---------|------|----------------|--------|----------|-----------|
| **01** | `keyword_generator.py` | Generate problem-driven keywords from a seed idea | idea prompt | `keywords.json` | ✅ |
| **02** | `data_collector.py` | Gather real posts + search data (Reddit, X, Trends) | `keywords.json`, `config.json` | `social_posts.csv` | ✅ |
| **03** | `data_validator.py` | Clean, deduplicate, visualize | `social_posts.csv` | `validation_report.md` + charts | ✅ |
| **04** | `message_miner.py` | Cluster recurring phrases & sentiment themes | `social_posts.csv` | `copy_intelligence_report.md` | ✅ |
| **05** | `copy_generator.py` | Convert mined language into ads, headlines, or landing-page copy | mined clusters | `generated_copy.md` | ✅ |
| **06** | `dashboard.py` | Human-in-the-loop review & rating | generated copy | `rated_copy.csv` | ✅ |
| **07** | `market_insights.py` | Overlay competitor + trend analysis | upstream outputs | `market_summary.md` | ✅ |

---

## 🧱 Directory Structure
```
/market_validation_engine
│
├── modules/
│   ├── 01_keyword_generator.md
│   ├── 02_data_collector.md
│   ├── 03_data_validator.md
│   ├── 04_message_miner.md
│   ├── 05_copy_generator.md
│   ├── 06_dashboard.md
│   └── 07_market_insights.md
│
├── data/
│   ├── keywords.json
│   ├── social_posts.csv
│   ├── copy_intelligence_report.md
│   ├── generated_copy.md
│   ├── rated_copy.csv
│   └── charts/
│
├── config.json
├── requirements.txt
├── .env
└── README.md
```

---

## 🧩 Configuration (`config.json`)
```json
{
  "project_name": "AI_Call_Receptionist",
  "region": "UK",
  "channels": ["reddit", "twitter", "google_trends"],
  "min_text_length": 40,
  "sentiment_mode": "vader",
  "max_records_per_keyword": 150
}
```

---

## 🧠 Data Flow

```
Seed Idea ─▶ 01_keyword_generator ─▶ 02_data_collector
       └────────────────────────────▶ 03_data_validator
                                     └▶ 04_message_miner
                                        └▶ 05_copy_generator
                                           └▶ 06_dashboard
                                              └▶ 07_market_insights
```

Each step saves its own artifact in `/data`, enabling independent reruns or swaps of modules.

---

## 🧰 Shared Utilities
- `logger.py` – timestamped logging across all modules  
- `utils.py` – text cleaning, sentiment analysis, deduplication  
- `common.py` – shared config + argument parser  

---

## 📊 Validation Criteria

| Metric | Description | Target Threshold |
|---------|--------------|------------------|
| **Volume** | ≥100 unique posts across channels | ✅ |
| **Relevance** | ≥70% posts contextually aligned with topic | ✅ |
| **Sentiment Spread** | At least one strong negative and one positive cluster (indicates emotional salience) | ✅ |
| **Keyword Coverage** | ≥80% keywords return >3 records | ✅ |
| **Signal Strength** | Avg compound sentiment magnitude ≥0.25 | ✅ |

---

## 🧠 Scoring Framework
Each idea gets a **Validation Score (0–100)**:

| Weight | Component | Formula |
|---------|------------|---------|
| 30% | **Pain Signal** | % of negative posts mentioning frustration |
| 25% | **Solution Intent** | % of posts seeking recommendations |
| 20% | **Trend Momentum** | Avg Google Trends growth rate |
| 15% | **Competitive Gap** | % of posts complaining about existing solutions |
| 10% | **Emotional Richness** | Avg sentiment variance |

A score ≥70 → Proceed to prototype.  
50–69 → Re-position or niche down.  
<50 → Not worth pursuing now.

---

## 🧭 Example Workflow (AI Receptionist)

```bash
# 1️⃣ Generate keywords
python modules/01_keyword_generator.py "AI call receptionist for SMEs"

# 2️⃣ Collect data
python modules/02_data_collector.py --config config.json

# 3️⃣ Validate & visualize
python modules/03_data_validator.py

# 4️⃣ Mine phrases → generate copy
python modules/04_message_miner.py
python modules/05_copy_generator.py

# 5️⃣ Review & rate in dashboard
streamlit run modules/06_dashboard.py

# 6️⃣ Generate market insight summary
python modules/07_market_insights.py
```

Outputs:  
- `social_posts.csv` (raw)  
- `validation_report.md` (summary)  
- `copy_intelligence_report.md` (themes)  
- `generated_copy.md` (ad copy)  
- `rated_copy.csv` (human review)  
- `market_summary.md` (decision artifact)

---

## 🚀 Future Extensions
| Feature | Description |
|----------|--------------|
| **Agent Orchestrator** | Automate sequential runs and scoring |
| **Database Memory (Neo4j)** | Track idea history & relationships |
| **LLM Embedding Search** | Replace TF-IDF with semantic clustering |
| **Competitor Intelligence Agent** | Pull competitor pricing, reviews, positioning |
| **Validation Dashboard (Streamlit)** | Unified view of all module outputs |
| **Voice/Video Sentiment Integration** | Future social channels (YouTube/TikTok comments) |

---

## 🧾 Success Criteria
- Re-usable across domains with only keyword/region swap.  
- Modular independence — any component can be upgraded without breaking others.  
- Produces tangible validation artifacts:
  - CSVs, Markdown reports, and visual charts.  
- Supports rapid iteration: *Idea → Market Validation Report in under 60 minutes.*

---

**Version 1.0 — Designed for Claude Code (for Rob)**
