---
title: Environment Setup Guide
author: Rob Freyne
date: 2025-10-11
version: 1.0
status: Active
---

# 🔧 Environment Setup Guide

## Central Configuration Philosophy

**ALL** environment variables, API keys, and secrets are stored in **ONE** central location:

```
/config/.env
```

**Why?**

- ✅ Single source of truth
- ✅ Easier to manage
- ✅ Consistent across all agents
- ✅ Secure (file is gitignored)
- ✅ Easy to backup/restore

---

## 📁 File Locations

| File                  | Purpose                    | Git Tracked             |
| --------------------- | -------------------------- | ----------------------- |
| `config/.env`         | **ACTUAL** secrets & keys  | ❌ NO (gitignored)      |
| `config/.env.example` | Template with placeholders | ✅ YES (safe to commit) |

---

## 🚀 Quick Setup

### Step 1: Copy Template

```bash
cd /Users/robertfreyne/Documents/ClaudeCode/ManagementTeam
cp config/.env.example config/.env
```

### Step 2: Edit with Your Keys

```bash
# Open in your editor
nano config/.env
# OR
code config/.env
# OR
open -a TextEdit config/.env
```

### Step 3: Add Your API Keys

```bash
# Replace the placeholder values:
PERPLEXITY_API_KEY=pplx-your-actual-key-here
MEM0_API_KEY=your-mem0-key-here
# etc...
```

### Step 4: Verify

```bash
source activate.sh
# Should see: "✅ Environment variables loaded"
```

---

## 🔑 Required API Keys

### For Planning Agent with Research

| Service           | Required? | Where to Get                           | Cost                |
| ----------------- | --------- | -------------------------------------- | ------------------- |
| **Perplexity AI** | Optional  | https://www.perplexity.ai/settings/api | Free tier available |
| **OpenAI**        | Optional  | https://platform.openai.com/api-keys   | Pay-as-you-go       |

### For Memory System (Phase 2)

| Service   | Required? | Where to Get      | Cost                |
| --------- | --------- | ----------------- | ------------------- |
| **Mem0**  | Phase 2   | https://mem0.ai   | Free tier available |
| **Neo4j** | Phase 2   | https://neo4j.com | Free tier available |

### For Notifications (Phase 2)

| Service   | Required? | Where to Get               | Cost |
| --------- | --------- | -------------------------- | ---- |
| **Slack** | Phase 2   | https://api.slack.com/apps | Free |

---

## 🔒 Security Best Practices

### ✅ DO:

1. **Keep .env file local** - Never commit to Git
2. **Use .env.example** - Commit template only
3. **Rotate keys regularly** - Change every 90 days
4. **Use read-only keys** - When possible
5. **Validate on load** - Check keys are set

### ❌ DON'T:

1. **Hardcode keys in code** - Always use env vars
2. **Share .env file** - Each developer has their own
3. **Email keys** - Use secure password managers
4. **Commit credentials** - Double-check before pushing
5. **Use production keys in dev** - Separate keys per environment

---

## 📦 How It Works

### 1. Shell Scripts Load It

```bash
# activate.sh and claude/environment.sh both load config/.env
if [ -f "config/.env" ]; then
    export $(grep -v '^#' config/.env | xargs)
fi
```

### 2. Python Code Uses config_loader

```python
# Every Python file that needs env vars:
from src.utils.config_loader import load_env, get_env

# Automatically loads config/.env
load_env()

# Get variables
api_key = get_env("PERPLEXITY_API_KEY", required=True)
```

### 3. All Agents Reference Central File

```python
# src/utils/perplexity_connector.py
from src.utils.config_loader import get_env
api_key = get_env("PERPLEXITY_API_KEY")

# src/agents/memory_agent.py (future)
from src.utils.config_loader import get_env
mem0_key = get_env("MEM0_API_KEY")

# All use the same config/.env file!
```

---

## 🧪 Testing Environment Setup

### Verify .env is Loaded

```bash
python -c "from src.utils.config_loader import print_env_status; print_env_status()"
```

**Output:**

```
======================================================================
🔑 ENVIRONMENT VARIABLES STATUS
======================================================================
✅ PERPLEXITY_API_KEY      : Set
❌ MEM0_API_KEY            : Not set
❌ OPENAI_API_KEY          : Not set
✅ PROJECT_NAME            : Set
✅ ENVIRONMENT             : Set
======================================================================
📁 Config file: /path/to/config/.env
📋 Example file: /path/to/config/.env.example
======================================================================
```

---

## 🔧 Troubleshooting

### "PERPLEXITY_API_KEY not found"

**Solution:**

```bash
# 1. Check if .env exists
ls -la config/.env

# 2. If not, copy from example
cp config/.env.example config/.env

# 3. Edit and add your key
nano config/.env

# 4. Reload environment
source activate.sh
```

### "Environment variables not loading"

**Solution:**

```bash
# Make sure you SOURCE (not just run) activate.sh
source activate.sh   # ✅ Correct
./activate.sh        # ❌ Won't work for env vars
```

### "Keys not working in Python"

**Solution:**

```python
# Always import config_loader first
from src.utils.config_loader import load_env
load_env()  # Call this early in your script

# Then use get_env
from src.utils.config_loader import get_env
key = get_env("YOUR_KEY", required=True)
```

---

## 📋 Environment Variables Reference

### Current Variables

```bash
# API Keys
PERPLEXITY_API_KEY=pplx-xxxxx    # For research queries
MEM0_API_KEY=mem0-xxxxx          # For memory system (Phase 2)
OPENAI_API_KEY=sk-xxxxx          # For embeddings (optional)
NEO4J_PASSWORD=xxxxx             # For graph DB (Phase 2)

# Project Settings
PROJECT_NAME=AI_Management_Team
ENVIRONMENT=development           # development | staging | production
PYTHONPATH=/path/to/ManagementTeam

# System Paths
MANAGEMENT_TEAM_ROOT=/path/to/ManagementTeam
LOGS_DIR=/path/to/ManagementTeam/logs
CONFIG_DIR=/path/to/ManagementTeam/config

# Feature Flags
ENABLE_PERPLEXITY_RESEARCH=true
ENABLE_MEM0_MEMORY=false
ENABLE_SLACK_NOTIFICATIONS=false
ENABLE_NEO4J=false

# Security
ENABLE_API_RATE_LIMITING=true
MAX_API_CALLS_PER_MINUTE=60
```

---

## 🎯 Integration Points

### Files That Load config/.env

| File                                         | How               | Purpose              |
| -------------------------------------------- | ----------------- | -------------------- |
| `activate.sh`                                | Shell export      | Quick startup        |
| `claude/environment.sh`                      | Shell export      | Full setup           |
| `src/utils/config_loader.py`                 | Python dotenv     | Central loader       |
| `src/utils/perplexity_connector.py`          | Via config_loader | API access           |
| `src/agents/planning_agent_with_research.py` | Via config_loader | Research integration |

**ALL agents and utilities use the same source!** ✅

---

## 📊 Migration from Old Setup

If you had env vars elsewhere, consolidate them:

```bash
# OLD (scattered)
export PERPLEXITY_API_KEY=xxx    # in ~/.zshrc
export MEM0_API_KEY=yyy          # in terminal
export PROJECT_NAME=zzz          # in another script

# NEW (centralized) ✅
# All in config/.env
```

---

## ✅ Verification Checklist

- [ ] `config/.env` exists
- [ ] `.env` is in `.gitignore`
- [ ] All API keys are set (no "your-" placeholders)
- [ ] `source activate.sh` shows "Environment variables loaded"
- [ ] `python -c "from src.utils.config_loader import print_env_status; print_env_status()"` shows keys as ✅

---

**Version:** 1.0  
**Last Updated:** 2025-10-11  
**Status:** ✅ Active
