---
title: Perplexity AI Integration
author: Rob Freyne
date: 2025-10-11
version: 1.0
status: Complete
---

# 🔍 Perplexity AI Integration for Planning Agent

## Overview

The Planning Agent can now query **Perplexity AI** for real-time research, enabling it to:

- 🔍 Research latest frameworks and best practices
- 📰 Get up-to-date industry news and trends
- 💻 Find code examples and patterns
- 📊 Validate technical decisions with current data
- 🧠 Fill knowledge gaps automatically

---

## Architecture

```
Planning Agent v2
    ↓
Initialize Context (docs/, config/)
    ↓
Identify Knowledge Gaps
    ↓
Query Perplexity AI → [Research Results]
    ↓
Incorporate into Roadmap
    ↓
Generate Enhanced Planning Docs
```

---

## Setup

### 1. Get Perplexity API Key

Visit: https://www.perplexity.ai/settings/api

Create an account and generate an API key.

### 2. Set Environment Variable

```bash
# Add to your .env file
export PERPLEXITY_API_KEY="pplx-xxxxxxxxxxxxx"

# Or set directly
echo 'export PERPLEXITY_API_KEY="your_key"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Verify Installation

```bash
python src/utils/perplexity_connector.py
```

---

## Usage

### Basic Research Query

```python
from src.utils.perplexity_connector import PerplexityConnector

connector = PerplexityConnector()

# Research a topic
result = connector.search(
    query="Best practices for AI agent orchestration",
    focus="research"  # or "news" or "code"
)

print(result['summary'])
print(result['sources'])
```

### Integrated with Planning Agent

```python
from src.agents.planning_agent_with_research import PlanningAgentWithResearch

# Create enhanced agent
agent = PlanningAgentWithResearch()

# Initialize with research enabled
agent.initialize(enable_research=True)

# Generate roadmap with automatic research
result = agent.generate_enhanced_roadmap("My-Project")

# Output: Enhanced roadmap with research citations
print(f"Roadmap: {result['roadmap_path']}")
print(f"Research conducted: {result['research_conducted']} queries")
```

---

## Focus Modes

| Mode | Use Case | Example Query |
|------|----------|---------------|
| **research** | Technical research, frameworks | "Latest AI agent architectures" |
| **news** | Industry trends, updates | "Recent AI regulations 2025" |
| **code** | Code examples, patterns | "Python async agent implementation" |

---

## Features

### 1. **Automatic Knowledge Gap Detection**

The agent scans your docs for:
- `TODO:` markers
- `TBD:` placeholders  
- `Research:` notes
- Question marks in context

Then automatically queries Perplexity!

### 2. **Research Caching**

Results are cached in memory to avoid duplicate API calls.

### 3. **Markdown Formatting**

Research results are auto-formatted for insertion into docs:

```markdown
### 🔍 Research Query: Latest agile frameworks

**Focus:** research
**Timestamp:** 2025-10-11T18:30:00.000Z UTC

[Summary from Perplexity]

**Sources:**
- https://example.com/source1
- https://example.com/source2
```

---

## Files Created

| File | Purpose | Location |
|------|---------|----------|
| `perplexity_connector.py` | Core API connector | `src/utils/` |
| `planning_agent_with_research.py` | Enhanced planner | `src/agents/` |
| `perplexity_integration.md` | This documentation | `docs/system/` |

---

## Example Workflow

### Scenario: Planning a New AI Project

```python
# 1. Create agent
agent = PlanningAgentWithResearch()

# 2. Load context from your docs
agent.initialize(enable_research=True)

# 3. Agent automatically:
#    - Finds "TODO: Research best agent framework"
#    - Queries Perplexity
#    - Gets latest info
#    - Incorporates into roadmap

# 4. Generate enhanced roadmap
result = agent.generate_enhanced_roadmap("AI-Trading-Assistant")

# Output includes:
# - Research insights
# - Cited sources
# - Evidence-based milestones
```

---

## Configuration

### In `planning_agent_context.yaml`:

```yaml
memory:
  type: "vector_store"
  provider: "local"
  embedding_model: "text-embedding-3-large"
  refresh_on_file_change: true
  search_mode: "hybrid"
  max_results: 10

# Add research settings
research:
  enabled: true
  provider: "perplexity"
  max_queries_per_cycle: 5
  cache_results: true
  include_citations: true
```

---

## API Rate Limits

### Perplexity AI Limits:

| Plan | Requests/Day | Cost |
|------|--------------|------|
| **Free** | ~50 | $0 |
| **Standard** | ~1000 | $20/month |
| **Pro** | ~10,000 | $200/month |

**Recommendation:** Start with free tier for testing.

---

## Security Best Practices

### ✅ DO:

- Store API key in `.env` file
- Add `.env` to `.gitignore`
- Use environment variables
- Validate all API responses
- Cache results to minimize calls

### ❌ DON'T:

- Hardcode API keys in code
- Commit credentials to Git
- Share API keys publicly
- Skip error handling

---

## Error Handling

The connector includes comprehensive error handling:

```python
try:
    result = connector.search("query")
except ValueError as e:
    # Missing API key
    logger.error(f"Configuration error: {e}")
except requests.HTTPError as e:
    # API error (rate limit, auth, etc.)
    logger.error(f"API error: {e}")
except Exception as e:
    # Unexpected error
    logger.error(f"Unexpected error: {e}")
```

---

## Testing

### Test the Connector

```bash
# Set your API key
export PERPLEXITY_API_KEY="pplx-xxxxx"

# Run test
python src/utils/perplexity_connector.py
```

### Test Enhanced Planning Agent

```bash
python src/agents/planning_agent_with_research.py
```

---

## Future Enhancements

- [ ] Add more research providers (OpenAI, Anthropic Claude)
- [ ] Implement vector similarity for better caching
- [ ] Auto-prioritize research topics by importance
- [ ] Generate research reports as separate documents
- [ ] Integration with Documentation Agent
- [ ] Real-time research during planning cycle

---

## Integration Points

| Agent | How It Uses Research |
|-------|---------------------|
| **Planning Agent** | Find frameworks, validate timelines |
| **Documentation Agent** | Get technical specs, ERD patterns |
| **Execution Agent** | Find code examples, libraries |
| **Reflection Agent** | Compare against industry best practices |

---

## Example Output

When you run the enhanced agent, you get:

```
outputs/
├── AI-Management-Layer_roadmap_enhanced.md   # With research
├── planning_summary.md                        # Cycle results
└── research_cache.json                        # Cached queries
```

---

## Benefits

### For Planning

- ✅ **Evidence-Based** - Decisions backed by research
- ✅ **Current** - Always uses latest information
- ✅ **Cited** - Includes source links
- ✅ **Automated** - No manual research needed

### For Quality

- ✅ **Reduces Guesswork** - Real data vs assumptions
- ✅ **Validates Approaches** - Compare vs industry
- ✅ **Discovers Gaps** - Finds what's missing
- ✅ **Improves Estimates** - Better timeline accuracy

---

## Cost Estimation

### For Typical Project Planning:

- **Queries per project:** ~5-10
- **Characters per response:** ~2000
- **Daily usage:** 1-2 projects
- **Monthly total:** ~200-400 queries

**Fits in FREE tier!** ✅

---

## Related Documentation

- **Planning Agent Spec:** `docs/system/planner_agent_spec.md`
- **Context Configuration:** `config/planning_agent_context.yaml`
- **Perplexity API Docs:** https://docs.perplexity.ai/

---

**Status:** ✅ Complete and Operational  
**Version:** 1.0  
**Last Updated:** 2025-10-11

