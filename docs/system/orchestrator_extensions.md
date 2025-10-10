# ORCHESTRATOR EXTENSIONS GUIDE
**Version:** 1.0  
**Owner:** Founder (Rob)  
**Date:** 2025-10-08  

---

## 🎯 PURPOSE
This guide provides step-by-step instructions for extending the orchestrator with monitoring, notifications, and advanced features according to the project roadmap.

---

## 📡 SLACK INTEGRATION

### Phase 1: Webhook Notifications (Basic Alerts)

**Goal:** Send real-time notifications when agents complete decisions.

#### Step 1: Setup Slack Webhook
1. Go to your Slack workspace
2. Create a new app at https://api.slack.com/apps
3. Enable "Incoming Webhooks"
4. Create a webhook URL for your target channel
5. Copy the webhook URL (looks like: `https://hooks.slack.com/services/...`)

#### Step 2: Update Environment Variables
```bash
# Edit config/.env
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

#### Step 3: Modify orchestrator.py

Add imports at the top:
```python
from slack_sdk.webhook import WebhookClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv("config/.env")
```

Add to the `Orchestrator.__init__()` method:
```python
def __init__(self, project_name: str):
    self.project_name = project_name
    self.session_log = os.path.join(
        BASE_LOG_DIR, f"{datetime.date.today()}_{project_name}.jsonl"
    )
    
    # Initialize Slack webhook (Phase 1)
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    self.slack_webhook = WebhookClient(webhook_url) if webhook_url else None
```

Add notification method:
```python
def _notify_slack(self, agent: str, result: dict):
    """Send Slack notification for agent completion."""
    if not self.slack_webhook:
        return
    
    message = (
        f"✅ *{agent.replace('_', ' ').title()}* completed\n"
        f"📋 Project: *{self.project_name}*\n"
        f"🎯 Decision: `{result['decision']}`\n"
        f"📊 Score: `{result['score']}`\n"
        f"💡 {result['reasoning'][:100]}..."
    )
    
    try:
        self.slack_webhook.send(text=message)
    except Exception as e:
        print(f"⚠️  Slack notification failed: {e}")
```

Call in the main loop (after step 2):
```python
# 2️⃣ Run agent logic (placeholder)
result = self._simulate_agent_run(agent, memory)
self._log({"event": "agent_result", "agent": agent, "result": result})
print(f"✅ {agent} completed with decision: {result['decision']} (score {result['score']})")

# 📡 Notify Slack (Phase 1)
self._notify_slack(agent, result)
```

#### Step 4: Test
```bash
source .venv/bin/activate
python scripts/orchestrator.py
```

Check your Slack channel for notifications!

---

### Phase 2: Interactive Approvals (Two-Way Communication)

**Goal:** Allow Founder to approve/reject decisions directly from Slack.

#### Requirements
- Slack Bot Token (with `chat:write`, `commands`, `interactive-messages` scopes)
- FastAPI server to handle Slack events
- Database to track pending approvals

#### Implementation (Future)
```python
# Will be implemented in v1.2
# - Add approval buttons to Slack messages
# - Create webhook endpoint to receive button clicks
# - Pause orchestrator until approval received
# - Update agent memory with approval status
```

---

### Phase 3: Daily Summaries & KPI Alerts

**Goal:** Automated daily/weekly reports sent to Slack.

#### Implementation (Future)
```python
# Scheduled job (cron or similar)
# - Aggregate all projects from past 24 hours
# - Calculate success metrics (ROI, speed, alignment)
# - Generate summary report
# - Send to Slack with charts/graphs
```

---

## 📊 DASHBOARD INTEGRATION

### Phase 1: Read-Only Dashboard (FastAPI + React)

**Goal:** Visual interface to view agent activity, logs, and memory.

#### Backend Setup (FastAPI)
```python
# File: dashboards/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI(title="Management Team Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/agents")
def list_agents():
    """List all agent memory files."""
    memory_dir = "memory"
    agents = []
    for file in os.listdir(memory_dir):
        if file.endswith('.json'):
            with open(f"{memory_dir}/{file}") as f:
                agents.append(json.load(f))
    return {"agents": agents}

@app.get("/api/logs/{project}")
def get_project_logs(project: str):
    """Retrieve logs for a specific project."""
    logs = []
    log_dir = "logs"
    for file in os.listdir(log_dir):
        if project.lower() in file.lower():
            with open(f"{log_dir}/{file}") as f:
                for line in f:
                    logs.append(json.loads(line))
    return {"logs": logs}

@app.get("/api/projects")
def list_projects():
    """List all unique projects across agent memories."""
    projects = set()
    memory_dir = "memory"
    for file in os.listdir(memory_dir):
        if file.endswith('.json'):
            with open(f"{memory_dir}/{file}") as f:
                data = json.load(f)
                for record in data.get('project_history', []):
                    projects.add(record['project'])
    return {"projects": sorted(list(projects))}
```

Run dashboard:
```bash
cd dashboards/api
uvicorn main:app --reload --port 8000
```

---

## 🧠 VECTOR MEMORY INTEGRATION

### Phase 1: ChromaDB for Semantic Search

**Goal:** Enable agents to find similar past decisions using semantic search.

#### Setup
Already included in dependencies (chromadb installed).

#### Create Vector Memory Wrapper
```python
# File: src/utils/vector_memory.py
from chromadb import Client
from chromadb.config import Settings

class VectorMemory:
    def __init__(self):
        self.client = Client(Settings(
            persist_directory="memory/vector",
            anonymized_telemetry=False
        ))
        self.collection = self.client.get_or_create_collection("decisions")
    
    def store(self, project: str, agent: str, decision: str, metadata: dict):
        """Store a decision with vector embedding."""
        self.collection.add(
            documents=[decision],
            metadatas=[{
                "project": project,
                "agent": agent,
                **metadata
            }],
            ids=[f"{project}_{agent}_{metadata.get('date')}"]
        )
    
    def search(self, query: str, n_results: int = 3):
        """Find similar past decisions."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
```

#### Integrate with Orchestrator
```python
# In orchestrator.py
from src.utils.vector_memory import VectorMemory

class Orchestrator:
    def __init__(self, project_name: str):
        # ... existing code ...
        self.vector_memory = VectorMemory()
    
    def run(self):
        for agent in AGENT_ORDER:
            # ... existing code ...
            
            # Store in vector memory for semantic search
            self.vector_memory.store(
                project=self.project_name,
                agent=agent,
                decision=result['reasoning'],
                metadata={
                    "score": result['score'],
                    "date": datetime.date.today().isoformat()
                }
            )
```

---

## 📈 LEARNING FEEDBACK LOOP

### Auto-Adjust Decision Weights

**Goal:** Data Agent automatically updates decision criteria weights based on outcomes.

#### Implementation (Future - v2.0)
```python
# File: src/agents/data_agent.py
class DataAgent:
    def analyze_outcomes(self):
        """Compare expected vs actual results and adjust weights."""
        
        # Load all project outcomes
        outcomes = self._load_outcomes()
        
        # Calculate correlation between decision scores and actual ROI
        for criterion in ['data_strength', 'roi_potential', 'speed_to_value']:
            correlation = self._calculate_correlation(outcomes, criterion)
            
            # Adjust weight based on predictive power
            if correlation > 0.8:
                self._increase_weight(criterion, factor=1.1)
            elif correlation < 0.3:
                self._decrease_weight(criterion, factor=0.9)
        
        # Update management_team_rules.yaml
        self._save_updated_weights()
        
        # Log change in change_log.md
        self._record_learning("Adjusted decision weights based on outcome analysis")
```

---

## 🔄 YAML CONFIG LOADING

### Dynamic Workflow from system_context.yaml

**Goal:** Load agent order and dependencies from YAML instead of hardcoding.

#### Implementation
```python
# Add to orchestrator.py
import yaml

def load_workflow_config():
    """Load workflow configuration from YAML."""
    with open('docs/system/system_context.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    return {
        'agent_order': config.get('workflow_order', []),
        'dependencies': config.get('dependencies', {})
    }

class Orchestrator:
    def __init__(self, project_name: str):
        # ... existing code ...
        
        # Load dynamic config
        self.config = load_workflow_config()
        self.agent_order = [
            agent.lower().replace(' ', '_') 
            for agent in self.config['agent_order']
        ]
```

---

## 🎬 PARALLEL AGENT EXECUTION

### For Independent Agents

**Goal:** Run agents in parallel when they don't depend on each other's output.

#### Implementation (Future - v2.1)
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class Orchestrator:
    async def run_parallel(self):
        """Execute independent agents in parallel."""
        
        # Identify independent agents from system_context.yaml
        parallel_groups = self._identify_parallel_groups()
        
        for group in parallel_groups:
            # Run group in parallel
            with ThreadPoolExecutor(max_workers=len(group)) as executor:
                futures = [
                    executor.submit(self._run_agent, agent)
                    for agent in group
                ]
                results = [f.result() for f in futures]
            
            # Log aggregated results
            self._log_group_results(group, results)
```

---

## 🧪 TESTING EXTENSIONS

### Test Slack Integration
```bash
# Set webhook URL
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."

# Run orchestrator
python scripts/orchestrator.py

# Check Slack channel for notifications
```

### Test Dashboard API
```bash
# Start API server
cd dashboards/api
uvicorn main:app --reload

# Test endpoints
curl http://localhost:8000/api/agents
curl http://localhost:8000/api/projects
curl http://localhost:8000/api/logs/AI_Receptionist
```

### Test Vector Memory
```python
from src.utils.vector_memory import VectorMemory

vm = VectorMemory()
vm.store("Test", "strategy_agent", "AI project for small business", {"score": 4.2})
results = vm.search("automation for SMB")
print(results)
```

---

## 📋 EXTENSION ROADMAP

| Extension | Priority | Complexity | Target Version |
|-----------|----------|------------|----------------|
| Slack Phase 1 (Webhooks) | 🔥 High | Low | v1.1 |
| YAML Config Loading | 🔥 High | Low | v1.1 |
| Dashboard Read-Only | Medium | Medium | v1.2 |
| Vector Memory | Medium | Medium | v1.3 |
| Slack Phase 2 (Approvals) | Medium | High | v1.4 |
| Learning Feedback Loop | Low | High | v2.0 |
| Parallel Execution | Low | High | v2.1 |

---

## 📚 RELATED FILES

- `orchestrator.py` - Main orchestration script
- `orchestrator_README.md` - Basic usage documentation
- `project_progress_plan.md` - Development roadmap
- `system_context.yaml` - Workflow configuration
- `management_team_rules.yaml` - Decision criteria

---

**Next Immediate Step:**  
Implement Slack Phase 1 (Webhook notifications) as outlined above.

---

**Version:** 1.0  
**Last Updated:** 2025-10-08  
**Status:** Ready for implementation

