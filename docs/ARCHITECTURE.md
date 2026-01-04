# Management Team Application - Data Architecture Map

## 🏗️ System Overview

The Management Team Application is a **universal business validation system** that analyzes any business idea through multi-source data collection and AI-powered analysis.

---

## 📊 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       USER INPUT LAYER                          │
│                    (Business Idea Details)                      │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│               STEP 1: IDEA REFINEMENT                           │
│            (interactive_orchestrator.py)                        │
│                                                                 │
│  Collects:                                                      │
│    • core_idea                                                  │
│    • target_customer                                            │
│    • industry                                                   │
│    • pain_context                                               │
│    • value_proposition                                          │
│    • competitive_awareness                                      │
│    • timeline                                                   │
│                                                                 │
│  Output: refinement_data → workflow_state                       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│            KEYWORD GENERATION LAYER                             │
│              (keyword_generator.py)                             │
│                                                                 │
│  Input: refinement_data                                         │
│                                                                 │
│  Process:                                                       │
│    1. AI generates keywords OR                                  │
│    2. Falls back to FALLBACK_KEYWORDS                           │
│                                                                 │
│  Output: Categorized keywords                                   │
│    ├─ pain_based: "missing calls", "can't answer phone"         │
│    ├─ core_intent: "virtual receptionist", "AI receptionist"    │
│    ├─ industry_vertical: "for dentists", "medical office"       │
│    ├─ adjacency_proxy: "alternative to X"                       │
│    └─ trend_validation: "AI automation 2025"                    │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│               STEP 2: PAIN DISCOVERY                            │
│          (pain_discovery_analyzer.py)                           │
│                                                                 │
│  Input: keywords + refinement_data                              │
│                                                                 │
│  Triggers: use_v4_enhanced_collector()                          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│          DATA COLLECTION LAYER (V4 ENHANCED)                    │
│       (message_collector_v4_enhanced.py)                        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  REDDIT COLLECTION (Primary Source)                     │   │
│  │  • Searches business subreddits:                        │   │
│  │    - r/smallbusiness                                    │   │
│  │    - r/entrepreneur                                     │   │
│  │    - r/startups                                         │   │
│  │    - r/business, r/sales, r/marketing                   │   │
│  │                                                         │   │
│  │  • Phrase search: "virtual receptionist" (exact match)  │   │
│  │  • Collects: Post + top 10 comments                     │   │
│  │  • Filters: Business context required                   │   │
│  │  • MD5 deduplication                                    │   │
│  │  • Min length: 30 chars                                 │   │
│  │                                                         │   │
│  │  Extracts per post:                                     │   │
│  │    ├─ ICP (Ideal Customer Profile)                      │   │
│  │    │   ├─ industry: regex patterns (dental, medical,    │   │
│  │    │   │           legal, automotive, etc.)             │   │
│  │    │   ├─ company_size: solo, micro, small, medium      │   │
│  │    │   └─ location: UK, Ireland, US, Canada, etc.       │   │
│  │    │                                                     │   │
│  │    ├─ Urgency Detection                                 │   │
│  │    │   ├─ critical: "urgent", "losing customers"        │   │
│  │    │   ├─ high: "need soon", "actively looking"         │   │
│  │    │   ├─ medium: default                               │   │
│  │    │   └─ low: "considering", "maybe"                   │   │
│  │    │                                                     │   │
│  │    ├─ Competitor Mentions                               │   │
│  │    │   └─ Patterns: "Dialpad", "Ruby", "Sonant", etc.   │   │
│  │    │                                                     │   │
│  │    ├─ Pricing Signals                                   │   │
│  │    │   ├─ explicit: "$500/month", "£2,000/year"         │   │
│  │    │   ├─ budget_concern: "afford", "expensive"         │   │
│  │    │   └─ quantified_loss: "losing $2k/month"           │   │
│  │    │                                                     │   │
│  │    └─ Basic Metadata                                    │   │
│  │        ├─ upvotes (community validation)                │   │
│  │        ├─ num_comments (engagement)                     │   │
│  │        ├─ sentiment (VADER)                             │   │
│  │        └─ date                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  GOOGLE TRENDS (Quantitative Validation)                │   │
│  │  • Search volume trends (12 months)                     │   │
│  │  • Breakout queries (explosive growth)                  │   │
│  │  • Rising queries (emerging trends)                     │   │
│  │  • Geographic breakdown                                 │   │
│  │  • Related topics                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  TWITTER/X (Future - Currently Disabled)                │   │
│  │  • Real-time sentiment                                  │   │
│  │  • Viral moments (>1k likes)                            │   │
│  │  • Influencer validation                                │   │
│  │  • Competitor @mentions                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Output: social_posts_enriched.csv                              │
│    Columns: platform, keyword, text_excerpt,                   │
│             comments_analyzed, sentiment, date, subreddit,      │
│             upvotes, num_comments, industry, company_size,      │
│             location, urgency, competitors_mentioned,           │
│             price_mentions, has_budget_concern,                 │
│             quantified_loss, trend_avg                          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│           ANALYSIS LAYER (DEMAND VALIDATOR)                     │
│            (demand_validator.py)                                │
│                                                                 │
│  Input: social_posts_enriched.csv                               │
│                                                                 │
│  Analyzes:                                                      │
│                                                                 │
│  1. ICP GENERATION                                              │
│     • Top industries (by frequency)                             │
│     • Company size distribution                                │
│     • Geographic concentration                                 │
│     • Urgency profile (critical/high/medium/low)                │
│     • Confidence score (data completeness)                      │
│                                                                 │
│  2. PAIN QUOTE RANKING                                          │
│     • Score = upvotes × urgency_weight × engagement             │
│     • Top 20 ranked by signal strength                          │
│                                                                 │
│  3. FEATURE EXTRACTION                                          │
│     • Regex patterns for common features:                       │
│       - appointment_booking                                     │
│       - 24_7_availability                                       │
│       - multilingual                                            │
│       - crm_integration                                         │
│       - sms_texting                                             │
│       - ai_powered                                              │
│     • Ranked by mention frequency                              │
│                                                                 │
│  4. COMPETITOR INTELLIGENCE                                     │
│     • Extract all competitor mentions                           │
│     • Filter false positives                                    │
│     • Rank by frequency                                         │
│     • Sentiment per competitor (future)                         │
│                                                                 │
│  5. PRICING ANALYSIS                                            │
│     • Price mentions count                                      │
│     • Budget concern percentage                                │
│     • Price examples extraction                                │
│     • Willingness-to-pay signals                               │
│                                                                 │
│  6. SALES TALK TRACK GENERATION                                 │
│     • Top pain examples                                         │
│     • Objection preparation (based on concerns)                 │
│     • Opening lines (based on ICP)                              │
│                                                                 │
│  Output: demand_validation_report.json                          │
│    {                                                            │
│      "summary": {...},                                          │
│      "icp": {...},                                              │
│      "top_pain_quotes": [...],                                  │
│      "feature_priorities": [...],                               │
│      "competitor_intelligence": {...},                          │
│      "pricing_signals": {...},                                  │
│      "sales_talk_track": {...}                                  │
│    }                                                            │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│          ENRICHED RESULTS INTEGRATION                           │
│         (pain_discovery_analyzer.py)                            │
│                                                                 │
│  Combines:                                                      │
│    • Standard pain analysis (old method)                        │
│    • Enriched demand report (v4 enhanced)                       │
│                                                                 │
│  Returns:                                                       │
│    {                                                            │
│      "demand_signal_strength": float,                           │
│      "conversation_volume": {...},                              │
│      "top_pain_quotes": [...],                                  │
│      "willingness_to_pay": {...},                               │
│      "urgency_analysis": {...},                                 │
│      "key_concerns": [...],                                     │
│      "validation_decision": {...},                              │
│      "enriched_analysis": {         ← NEW!                      │
│        "icp": {...},                                            │
│        "feature_priorities": [...],                             │
│        "competitor_intelligence": {...},                        │
│        "pricing_signals": {...},                                │
│        "sales_talk_track": {...},                               │
│        "top_pain_quotes_ranked": [...]                          │
│      }                                                          │
│    }                                                            │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│            DISPLAY LAYER (ORCHESTRATOR)                         │
│         (interactive_orchestrator.py)                           │
│                                                                 │
│  Displays:                                                      │
│    1. Standard pain discovery results                           │
│    2. Enriched insights (_display_enriched_insights)            │
│       ├─ ICP breakdown                                          │
│       ├─ Top requested features                                 │
│       ├─ Pricing intelligence                                   │
│       ├─ Competitor mentions                                    │
│       └─ Top validated pain quote                               │
│                                                                 │
│  Saves to workflow_state:                                       │
│    • pain_discovery_results (full results)                      │
│    • Checkpoint for resumability                                │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   OUTPUT ARTIFACTS                              │
│                                                                 │
│  Files Generated:                                               │
│    ├─ social_posts_enriched.csv                                 │
│    │   └─ Raw collected data with enrichments                   │
│    │                                                            │
│    ├─ demand_validation_report.json                             │
│    │   └─ Full analysis report                                  │
│    │                                                            │
│    ├─ .checkpoints/{project_id}/latest.json                     │
│    │   └─ Workflow state for resumability                       │
│    │                                                            │
│    └─ (Future) Charts:                                          │
│        ├─ sentiment_histogram.png                               │
│        └─ keyword_coverage.png                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Workflow States

```
User Input
    ↓
Step 1: Refinement (score: 0-1)
    ↓
Step 2: Pain Discovery (score: 0-1)  ← ENHANCED WITH V4
    ├─ Validation Gates:
    │   ├─ Test Reddit credentials
    │   ├─ Collect enriched data
    │   ├─ Validate quality (>50 posts)
    │   └─ Retry with fallback if needed
    │
    └─ Output: enriched_analysis + standard_analysis
    ↓
Step 3: Market Sizing
    ↓
Step 4: Competitive Analysis
```

---

## 📁 File Structure

```
ManagementTeam/
├── cli/
│   └── interactive_workflow.py         # Entry point
│
├── core/
│   ├── interactive_orchestrator.py     # Workflow orchestration
│   ├── pain_discovery_analyzer.py      # Pain analysis (uses v4)
│   ├── keyword_generator.py            # Keyword generation
│   ├── workflow_state.py               # State management
│   └── checkpoint_manager.py           # Checkpoint saving
│
├── src/
│   ├── integrations/
│   │   ├── message_collector_v4_enhanced.py  # V4 enhanced collector
│   │   ├── message_collector_v3_fixed.py     # V3 (phrase search)
│   │   ├── reddit_connector.py               # Reddit API
│   │   └── x_connector.py                    # Twitter/X API
│   │
│   └── analysis/
│       └── demand_validator.py         # Demand analysis
│
├── tests/
│   ├── test_reddit_credentials.py      # Credential validation
│   ├── validate_collector_output.py    # Data quality check
│   └── test_integration.py             # Integration test
│
└── .checkpoints/
    └── {project_id}/
        ├── latest.json                 # Current state
        └── social_posts_enriched.csv   # Collected data
```

---

## 🎯 Key Enhancements (V4)

### Before (V2/V3):
- ❌ Zero results or irrelevant data
- ❌ No ICP extraction
- ❌ No urgency detection
- ❌ No competitor intelligence
- ❌ No pricing signals
- ❌ Generic pain quotes

### After (V4 Enhanced):
- ✅ 40+ high-quality business conversations
- ✅ ICP: Industry, size, location (46% confidence)
- ✅ Urgency: 70% CRITICAL (need it NOW)
- ✅ Competitors: Dialpad, Sonant, Ruby mentioned
- ✅ Pricing: 49% have budget concerns
- ✅ Features: AI powered (74%), 24/7 (21%), Booking (16%)
- ✅ Top quote: 158 upvotes (highly validated)

---

## 🚀 Usage

### Run Full Workflow:
```bash
python cli/interactive_workflow.py --resume project_20251025_150409
```

### Test Integration:
```bash
python test_integration.py
```

### Manual Collection:
```bash
python src/integrations/message_collector_v4_enhanced.py
python src/analysis/demand_validator.py
```

---

## 🧠 Shared Memory Architecture (Supabase Integration)

**Status:** Active ✅ (2025-11-12)
**Integration:** Cross-system with AskSharon.ai

### Architecture Overview

```
┌──────────────────────────────────────────┐
│     Supabase PostgreSQL (Shared)         │
│  https://coxnsvusaxfniqivhlar.supabase.co│
│                                           │
│  Tables:                                  │
│  ├─ long_term_memory (semantic search)   │
│  │  └─ pgvector embeddings (1536-dim)    │
│  ├─ project_decisions (ManagementTeam)   │
│  ├─ user_tasks (AskSharon)               │
│  └─ memory_links (cross-references)      │
└──────────────────────────────────────────┘
         ↑                    ↑
         │                    │
   ManagementTeam      AskSharon.ai
   (stores projects)   (stores tasks)
```

### Core Components

**1. Memory Storage (`memory/supabase_memory.py`)**

```python
from memory.supabase_memory import (
    store_project_decision,    # Store agent decisions
    recall_related_projects,   # Semantic search
    get_project_status,        # Check project state
    get_all_active_projects    # List active work
)
```

**2. Semantic Search (OpenAI + pgvector)**

- Embeddings: OpenAI `text-embedding-ada-002` (1536 dimensions)
- Index: IVFFlat with cosine similarity
- Search: SQL function `search_memory()` with configurable threshold

**3. Data Flow**

```
Strategy Agent Approval
    ↓
store_project_decision()
    ↓
Supabase long_term_memory + project_decisions
    ↓
AskSharon queries via find_related_business_projects()
    ↓
User sees business project in morning check-in
    ↓
Creates linked task (project_reference field)
```

### Security Model

- **ManagementTeam:** `SUPABASE_SERVICE_ROLE_KEY` (admin access)
- **AskSharon:** `SUPABASE_ANON_KEY` (user-level access)
- **Row-Level Security:** Each system writes only its own records
- **Cross-Reading:** Both systems can read all records (for context)

### Performance

- **Embedding Generation:** ~50ms per decision (OpenAI API)
- **Semantic Search:** ~100ms (pgvector indexed)
- **Storage:** ~2KB per project decision
- **Cost:** ~$0.01/month for 1,000 decisions (free tier)

### CLI Usage

```bash
# Test connection
python memory/supabase_memory.py test

# Store decision
python memory/supabase_memory.py store \
  --project "AI_Receptionist" \
  --decision approved \
  --agent strategy_agent \
  --notes "High market demand confirmed"

# Search projects
python memory/supabase_memory.py search \
  --query "dental automation tools"

# Get stats
python memory/supabase_memory.py stats
```

### Migration from JSON

Existing agent memories in `/memory/*.json` can be migrated:

```bash
# Dry run
python scripts/migrate_to_supabase.py --dry-run

# Full migration
python scripts/migrate_to_supabase.py --backup
```

### Documentation

- **Setup Guide:** [docs/setup/SHARED_MEMORY_GUIDE.md](../setup/SHARED_MEMORY_GUIDE.md)
- **Full Integration Docs:** `/asksharon_ai_blueprint/docs/MEMORY_INTEGRATION.md`
- **Quick Start:** `/asksharon_ai_blueprint/docs/MEMORY_QUICKSTART.md`

---

## 💡 Adaptability for Any Business

The system is **fully generic** - just change keywords and it works for any business idea:

### Example: SaaS Project Management Tool
```python
keywords = [
    "project management pain",
    "team collaboration tool",
    "alternative to Asana",
    "project tracking software"
]
```

The same enriched analysis will extract:
- ICP: Tech startups, remote teams
- Features: Gantt charts, time tracking, integrations
- Competitors: Asana, Monday.com, Jira
- Pricing: "$10-50/user/month"

---

## 📊 Data Quality Gates

| Gate | Threshold | Action |
|------|-----------|--------|
| Total Posts | ≥50 | PASS / Retry with fallback |
| Weak Keywords | <5 | PASS / Flag for review |
| ICP Confidence | ≥30% | PASS / Collect more data |
| Platform Coverage | Reddit + Trends | PASS / Warn if single source |
| Urgency Signal | ≥20% critical | Strong / Moderate / Weak |

---

## 💰 Cost Optimization Architecture (HuggingFace Integration)

**Status:** Phase 1 Complete ✅ (66-75% cost reduction achieved)
**Savings:** $50-100/month
**Details:** See `docs/COST_OPTIMIZATION.md`

### Philosophy

The system uses a **hybrid approach** to minimize OpenAI API costs while maintaining quality:

- **Free/Local Models (HuggingFace):** Commoditized tasks (grammar, sentiment, keyword extraction)
- **Paid Models (OpenAI):** Complex reasoning, structured outputs, domain expertise

```
┌─────────────────────────────────────────────────────────────────┐
│                   HYBRID AI ARCHITECTURE                        │
│                                                                 │
│  STEP 1: Free Preprocessing (HuggingFace - $0)                 │
│  ├─ T5 Grammar Correction                                      │
│  ├─ KeyBERT Keyword Candidates                                 │
│  └─ Sentence-Transformers Embeddings                           │
│                       │                                         │
│                       ▼                                         │
│  STEP 2: Paid Value-Add (OpenAI - $$)                          │
│  ├─ GPT Critique (grammar pre-corrected)                       │
│  ├─ GPT Keyword Categorization (14 instead of 50)              │
│  └─ GPT Reasoning & Structured Output                          │
│                                                                 │
│  RESULT: Same quality, 70% cheaper!                            │
└─────────────────────────────────────────────────────────────────┘
```

### Components

#### 1. T5 Grammar Correction (idea_critic.py:91-135)

**Before (OpenAI only):**
```python
critique = gpt.correct_and_critique(text)  # $15-30/mo
```

**After (T5 + GPT hybrid):**
```python
corrected = t5.correct_grammar(text)  # FREE!
critique = gpt.critique_only(corrected)  # 50% cheaper!
```

**Model:** `vennify/t5-base-grammar-correction`
**Savings:** $15-30/month
**Benefits:** 10x faster, 100% private, graceful fallback

#### 2. KeyBERT Hybrid Keywords (keyword_generator.py:164-197)

**Before (OpenAI only):**
```python
keywords = gpt.generate_keywords(text, n=50)  # $30-70/mo
```

**After (KeyBERT + GPT hybrid):**
```python
candidates = keybert.extract(text, n=50)  # FREE!
keywords = gpt.categorize_with_reasoning(candidates[:14])  # 70% cheaper!
```

**Models:** `all-MiniLM-L6-v2` + `KeyBERT`
**Savings:** $30-50/month
**Benefits:** Better diversity (MMR algorithm), faster batch processing

#### 3. Semantic Search (scripts/search_evidence.py)

**New Capability (didn't exist before):**
```python
# Find similar pain points semantically
embeddings = sentence_transformers.encode(posts)
similar = util.cos_sim(query_emb, embeddings).topk(5)
```

**Model:** `all-MiniLM-L6-v2`
**Cost:** $0 (local)
**Benefits:** Better than keyword matching, cached embeddings (9s initial, instant after)

### Cost Breakdown

| Component | Before (OpenAI) | After (Hybrid) | Monthly Savings |
|-----------|-----------------|----------------|-----------------|
| Grammar correction | $15-30/mo | **$0** | **$15-30/mo** |
| Keyword generation | $30-70/mo | $10-30/mo | **$30-50/mo** |
| Semantic search | N/A (didn't exist) | **$0** | **New capability!** |
| **TOTAL** | **$45-100/mo** | **$10-30/mo** | **$50-100/mo** |

**ROI:** 66-75% cost reduction with zero quality loss!

### Local Models Used (All $0)

| Model | Purpose | File |
|-------|---------|------|
| vennify/t5-base-grammar-correction | Grammar | core/idea_critic.py |
| all-MiniLM-L6-v2 | Embeddings | core/keyword_generator.py, scripts/search_evidence.py |
| KeyBERT | Keyword extraction | core/keyword_generator.py |
| cardiffnlp/twitter-roberta-base-sentiment | Sentiment | src/ml/pain_point_extractor.py |
| dslim/bert-base-NER | Entity extraction | src/ml/pain_point_extractor.py |
| facebook/bart-large-mnli | Classification | src/ml/pain_point_extractor.py |

### Installation

```bash
# T5 Grammar Correction
pip install transformers

# KeyBERT Hybrid Keywords
pip install keybert

# Verify installation
python -c "from transformers import pipeline; from keybert import KeyBERT; print('✅ All installed')"
```

### Graceful Degradation

All HuggingFace integrations have **fallback to OpenAI** if models are unavailable:

```python
try:
    result = huggingface_model.process(input)
except Exception:
    logger.warning("HuggingFace unavailable, falling back to OpenAI")
    result = openai.process(input)
```

This ensures the system **always works**, even without optional dependencies installed.

---

## 🔮 Future Enhancements

1. **Twitter/X Integration** (when API fixed)
2. **YouTube Comments** (video pain signals)
3. **Product Hunt** (product launches/feedback)
4. **G2/Capterra Reviews** (competitor weaknesses)
5. **LinkedIn Posts** (B2B pain signals)
6. **Time-series Analysis** (trend detection)
7. **Automated Content Generation** (blog posts from pain quotes)
8. **Sales Email Templates** (based on talk tracks)

---

**Built with ❤️ for universal business validation**
