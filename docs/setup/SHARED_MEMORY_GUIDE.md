# Shared Long-Term Memory Guide
## ManagementTeam + AskSharon.ai Integration

**Status:** Active
**Last Updated:** 2025-11-12

---

## 🎯 Overview

ManagementTeam uses **Supabase pgvector** for persistent memory that's shared with AskSharon.ai. This enables:

- ✅ **Agent memory** - Store project decisions with semantic search
- ✅ **Cross-system intelligence** - Business projects inform personal tasks
- ✅ **Unified timeline** - See how personal work supports business goals

### Why Shared Memory?

When strategy agent approves a project → AskSharon can automatically suggest personal tasks to work on it.

**Example:**
```
ManagementTeam: "AI_Receptionist approved by strategy_agent"
     ↓
AskSharon: "Would you like to create tasks for AI_Receptionist?"
     ↓
Tasks: "Build MVP", "Research competitors", "Draft marketing"
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────┐
│     Supabase PostgreSQL (Shared)         │
│  https://coxnsvusaxfniqivhlar.supabase.co│
│                                           │
│  Tables:                                  │
│  ├─ long_term_memory (semantic search)   │
│  ├─ project_decisions (ManagementTeam)   │
│  ├─ user_tasks (AskSharon)               │
│  └─ memory_links (cross-references)      │
└──────────────────────────────────────────┘
         ↑                    ↑
         │                    │
   ManagementTeam      AskSharon.ai
   (stores projects)   (stores tasks)
```

### Data Isolation

- **Write:** Each system can only write to its own records
- **Read:** Both can read each other (for context)
- **Security:** Row-level security policies enforce isolation

---

## 🔌 Python API

### Store Project Decision

```python
from memory.supabase_memory import store_project_decision

# Store agent decision
memory_id = store_project_decision(
    project_name="AI_Receptionist",
    decision="approved",          # 'approved', 'rejected', 'on_hold', 'completed'
    agent_name="strategy_agent",
    notes="High market demand, strong ROI potential",
    metadata={"industry": "healthcare", "market_fit": "high"}
)
```

### Search for Related Projects

```python
from memory.supabase_memory import recall_related_projects

# Semantic search
results = recall_related_projects(
    query="dental clinic automation",
    limit=5,
    min_similarity=0.7
)

for r in results:
    print(f"{r['similarity']:.2f} - {r['metadata']['project']}")
    print(f"   Decision: {r['metadata']['decision']}")
```

### Check Project Status

```python
from memory.supabase_memory import get_project_status

status = get_project_status("AI_Receptionist")
if status:
    print(f"Decision: {status['decision']}")
    print(f"Agent: {status['agent_name']}")
    print(f"Date: {status['created_at']}")
```

### Get All Active Projects

```python
from memory.supabase_memory import get_all_active_projects

projects = get_all_active_projects()
for p in projects:
    print(f"{p['project_name']}: {p['decision']} ({p['agent_name']})")
```

### Get Memory Stats

```python
from memory.supabase_memory import get_memory_stats

stats = get_memory_stats()
print(f"Total memories: {stats['total_memories']}")
print(f"Active projects: {stats['active_projects']}")
```

---

## 🖥️ CLI Commands

Test and use the memory system from command line:

```bash
# Test connection
python memory/supabase_memory.py test

# Store a project decision
python memory/supabase_memory.py store \
  --project "AI_Receptionist" \
  --decision approved \
  --agent strategy_agent \
  --notes "Strong market fit confirmed"

# Search for projects
python memory/supabase_memory.py search \
  --query "healthcare AI solutions"

# Check project status
python memory/supabase_memory.py status \
  --project "AI_Receptionist"

# Get statistics
python memory/supabase_memory.py stats
```

---

## 🚀 Setup Instructions

### 1. Run SQL Setup (One Time)

```bash
# Copy SQL to clipboard
cat docs/sql/setup_shared_memory.sql | pbcopy

# Go to Supabase SQL Editor:
# https://supabase.com/dashboard/project/coxnsvusaxfniqivhlar/sql

# Paste and run (takes ~5 seconds)
```

### 2. Install Dependencies

```bash
cd ManagementTeam
source venv/bin/activate
pip install supabase openai
```

### 3. Configure Credentials

Add to `config/.env`:

```bash
# Supabase Shared Memory
SUPABASE_URL=https://coxnsvusaxfniqivhlar.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNveG5zdnVzYXhmbmlxaXZobGFyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTA3NzU4MCwiZXhwIjoyMDc0NjUzNTgwfQ.qyAMlwd171_YtNVoKevXpqLBTB5pBcwFQ6f-giAGBWo
ENABLE_SUPABASE_MEMORY=true
```

**Note:** Use `SUPABASE_SERVICE_ROLE_KEY` (admin access) for ManagementTeam.

### 4. Test Connection

```bash
python memory/supabase_memory.py test
```

Expected output:
```
✅ Supabase connected
✅ Generated 1536-dimensional embedding
✅ All tests passed!
```

---

## 🔄 Migrate Existing JSON Memories

If you have existing agent memories in `/memory/*.json`:

```bash
# Dry run (preview)
python scripts/migrate_to_supabase.py --dry-run

# Create backup + migrate
python scripts/migrate_to_supabase.py --backup

# Migrate specific agent only
python scripts/migrate_to_supabase.py --agent strategy_agent
```

**What happens:**
- Reads all JSON files in `/memory/`
- Uploads project_history to Supabase
- Original JSON files preserved as backup
- Skips duplicates automatically

---

## 📊 Monitoring

### View in Supabase Dashboard

https://supabase.com/dashboard/project/coxnsvusaxfniqivhlar/editor

**Tables to check:**
- `long_term_memory` - All semantic memories
- `project_decisions` - ManagementTeam projects
- `recent_project_activity` - View showing active projects
- `task_summary_by_project` - Tasks grouped by project

### SQL Queries

```sql
-- See ManagementTeam projects
SELECT * FROM project_decisions
ORDER BY created_at DESC;

-- See linked AskSharon tasks
SELECT
    pd.project_name,
    pd.decision,
    COUNT(ut.id) as task_count
FROM project_decisions pd
LEFT JOIN user_tasks ut ON ut.project_reference = pd.project_name
WHERE pd.decision = 'approved'
GROUP BY pd.project_name, pd.decision;

-- Semantic search (requires embedding)
SELECT * FROM search_memory(
    '[0.1, 0.2, ...]'::vector(1536),
    0.7,
    5,
    'management_team',
    'project_decision'
);
```

---

## 💰 Cost

**Free tier (current usage):**
- Supabase: $0/month (500MB limit, using <1%)
- OpenAI embeddings: ~$0.01/month (1,000 decisions)

**Total: ~$0/month** ✅

---

## 🔗 Cross-System Features

### View AskSharon Tasks for Your Projects

```python
from memory.supabase_memory import _get_supabase_client

supabase = _get_supabase_client()

# Get tasks for a project
tasks = supabase.table("user_tasks")\
    .select("*")\
    .eq("project_reference", "AI_Receptionist")\
    .execute()

for task in tasks.data:
    status = "✅" if task['completed'] else "⏳"
    print(f"{status} {task['title']} (U:{task['urgency']} I:{task['importance']})")
```

### Link ManagementTeam Project → AskSharon Task

```python
from memory.supabase_memory import link_to_asksharon_task

# Create explicit link
link_to_asksharon_task(
    project_name="AI_Receptionist",
    task_id=123,
    relationship="implements"
)
```

---

## 🛠️ Integration Examples

### In Strategy Agent

```python
from memory.supabase_memory import store_project_decision

class StrategyAgent:
    def approve_project(self, project_name: str, analysis: dict):
        # Store decision
        memory_id = store_project_decision(
            project_name=project_name,
            decision="approved",
            agent_name="strategy_agent",
            notes=analysis['rationale'],
            metadata={
                "market_fit": analysis['market_fit'],
                "roi_potential": analysis['roi']
            }
        )

        print(f"✅ Project approved and stored (Memory ID: {memory_id})")
        print(f"💡 AskSharon will now see this project in morning check-in")
```

### In Financial Agent

```python
from memory.supabase_memory import store_project_decision, get_project_status

class FinancialAgent:
    def check_budget_approval(self, project_name: str) -> bool:
        # Check if strategy agent already approved
        status = get_project_status(project_name)

        if status and status['decision'] == 'approved':
            print(f"✅ {project_name} already approved by {status['agent_name']}")

            # Add financial approval
            store_project_decision(
                project_name=project_name,
                decision="approved",
                agent_name="financial_agent",
                notes="Budget allocated, funding approved"
            )
            return True

        return False
```

---

## ⚠️ Troubleshooting

### "Extension vector does not exist"

**Solution:** Re-run SQL setup from Step 1.

### "Permission denied for table..."

**Cause:** Wrong Supabase key

**Solution:** Ensure using `SUPABASE_SERVICE_ROLE_KEY` (not ANON_KEY)

### Slow searches

**Solution:**
```sql
REINDEX INDEX long_term_memory_embedding_idx;
```

### "Module not found: supabase"

**Solution:**
```bash
pip install supabase openai
```

---

## 📚 Full Documentation

### ManagementTeam Documentation
- **This guide:** `/ManagementTeam/docs/setup/SHARED_MEMORY_GUIDE.md` (you are here)
- **Architecture:** `/ManagementTeam/docs/ARCHITECTURE.md` - Memory architecture section
- **README:** `/ManagementTeam/README.md` - Shared memory overview

### AskSharon.ai Documentation
For complete details including database schema, row-level security, and use cases:
- **Integration Guide:** `/asksharon_ai_blueprint/docs/MEMORY_INTEGRATION.md` - Complete technical guide
- **Quick Start:** `/asksharon_ai_blueprint/docs/MEMORY_QUICKSTART.md` - 10-minute setup
- **AskSharon Core:** `/asksharon_ai_blueprint/assistant/core/supabase_memory.py` - Python API

---

## 🎯 Next Steps

1. **Test the connection:** `python memory/supabase_memory.py test`
2. **Store a test project:** `python memory/supabase_memory.py store --project Test --decision approved`
3. **Search it:** `python memory/supabase_memory.py search --query "test project"`
4. **Migrate existing data:** `python scripts/migrate_to_supabase.py --dry-run`
5. **View progress reports:** See activity across both systems (AskSharon feature)

---

## 📊 Progress Reports

**NEW:** Track your activity across ManagementTeam + AskSharon!

AskSharon.ai includes a progress report system that shows:
- ManagementTeam projects worked on
- AskSharon tasks created/completed
- Connections between projects and tasks
- Timeline of activity

**Commands (run from AskSharon directory):**
```bash
cd /Users/robertfreyne/Documents/ClaudeCode/asksharon_ai_blueprint

# Yesterday's activity
python scripts/progress_report.py yesterday

# Weekly progress
python scripts/progress_report.py week

# Since last login
python scripts/progress_report.py last-session
```

**Documentation:** `/asksharon_ai_blueprint/docs/PROGRESS_REPORTS.md`

---

**Questions?** See full docs at `/asksharon_ai_blueprint/docs/MEMORY_INTEGRATION.md`
