# 🧠 Strategic Planner Agent

**Management-Layer Agent: Decides WHAT to Build Next**

---

## 🎯 Purpose

The Strategic Planner Agent sits between the Vertical Agent and the Planning Agent:

```
Vertical Agent → Strategic Planner → Planning Agent → Full Project
(Scores ideas)  (Decides which)    (Scaffolds it)
```

**Role:** Makes the final decision on which business vertical to pursue and orchestrates the tactical planning phase.

---

## 🚀 Quick Start

### **Typical Workflow:**

```bash
# 1. Evaluate business ideas
python scripts/run_vertical_agent.py inputs/ideas.json

# 2. Strategic decision (with approval)
python scripts/run_strategic_planner.py

# 3. Review generated project
ls projects/ai-receptionist-for-hair-salons/
```

### **Example Output:**

```
🧠 STRATEGIC PLANNER DECISION
======================================================================

📂 Vertical: AI Receptionist for Hair Salons
📈 RICE Score: 84.0

Suggested action:
- Project Title: ai-receptionist-for-hair-salons
- Description: Build: AI Receptionist for Hair Salons

💡 Reasoning: Moderate opportunity (score: 84.0). Proceed with MVP approach.

======================================================================
💡 Would you like to send this to the Planning Department?
======================================================================

👉 Approve? (Y/N):
```

---

## ⚙️ Features

### **1. Human-in-the-Loop Approval**
- ✅ Shows strategic proposal
- ✅ Displays score and reasoning
- ✅ Lists alternatives considered
- ✅ Waits for Y/N approval
- ✅ Skippable with `--non-interactive`

### **2. Intelligent Decision Making**
- ✅ Score thresholds (>100 = strong, >50 = moderate, <50 = hold)
- ✅ Reasoning generation
- ✅ Alternative comparison
- ✅ Risk assessment

### **3. Automatic Planning Invocation**
- ✅ Triggers Planning Agent on approval
- ✅ Passes project name and description
- ✅ Creates complete project structure
- ✅ Logs decision trail

### **4. Decision Logging**
- ✅ Saves to `outputs/strategic_decision.yaml`
- ✅ Creates decision log in `logs/strategic_decisions/`
- ✅ Timestamped records
- ✅ Full audit trail

---

## 📁 File Structure

```
agents/strategic_planner/
├── __init__.py
├── strategic_planner.py      # Main agent
└── README.md                  # This file

scripts/
└── run_strategic_planner.py  # CLI wrapper

outputs/
└── strategic_decision.yaml   # Decision output

logs/strategic_decisions/
└── project-name_timestamp.txt  # Decision logs
```

---

## 🎮 Usage

### **Interactive Mode (Default)**

```bash
python scripts/run_strategic_planner.py
```

You'll be prompted:
```
💡 Would you like to send this to the Planning Department?
👉 Approve? (Y/N):
```

### **Auto-Approve (Non-Interactive)**

```bash
python scripts/run_strategic_planner.py --non-interactive
```

Skips approval prompt and proceeds automatically.

### **Custom Paths**

```bash
python scripts/run_strategic_planner.py \
  --recommendation outputs/my_recommendation.md \
  --scores outputs/my_scores.yaml \
  --output outputs/my_decision.yaml
```

### **Programmatic Usage**

```python
from agents.strategic_planner.strategic_planner import StrategicPlannerAgent

# Interactive mode
agent = StrategicPlannerAgent(interactive=True)
result = agent.run()  # Will prompt for approval

# Non-interactive mode
agent = StrategicPlannerAgent(interactive=False)
result = agent.run()  # Auto-proceeds
```

---

## 📊 Decision Logic

### **Score Thresholds:**

| Score Range | Decision | Reasoning |
|-------------|----------|-----------|
| **≥ 100** | PROCEED | Strong opportunity - immediate planning |
| **50-99** | PROCEED | Moderate opportunity - MVP approach |
| **< 50** | HOLD | Below threshold - further validation needed |

### **Confidence Levels:**

| Score | Confidence |
|-------|------------|
| **≥ 100** | 0.8 (High) |
| **50-99** | 0.6 (Moderate) |
| **< 50** | 0.3 (Low) |

---

## 📄 Output Format

### **`outputs/strategic_decision.yaml`**

```yaml
selected_vertical: AI Receptionist for Hair Salons
score: 84.0
proceed: true
reasoning: 'Moderate opportunity (score: 84.0). Proceed with MVP approach.'
decision_date: '2025-10-12T16:52:21.740381'
human_approved: true
vertical_details:
  name: AI Receptionist for Hair Salons
  reach: 7
  impact: 8
  confidence: 6
  effort: 4
alternatives:
  - name: Tyre Fitters Booking Bot
    score: 56.0
```

### **Decision Log (`logs/strategic_decisions/*.txt`)**

```
======================================================================
STRATEGIC DECISION LOG
======================================================================

Project: AI Receptionist for Hair Salons
Score: 84.0
Decision: PROCEED
Date: 2025-10-12T16:52:21.740381

Reasoning:
Moderate opportunity (score: 84.0). Proceed with MVP approach.

Alternatives Considered:
  1. Tyre Fitters Booking Bot (score: 56.0)

======================================================================
Decision logged by Strategic Planner Agent
======================================================================
```

---

## 🔗 Integration with Other Agents

### **Input: Vertical Agent**
- Reads: `outputs/recommendation.md` or `outputs/vertical_scores.yaml`
- Uses: Top recommendation and score

### **Output: Planning Agent**
- Invokes: `scripts/run_planner.py`
- Passes: Project name and description
- Creates: Complete project structure

### **Protocol: AgentOutput**
- Returns: Standardized `AgentOutput`
- Decision: "approve" (proceed) or "conditional" (hold)
- Confidence: Based on score threshold

---

## 🎮 Complete Workflow Example

### **End-to-End: Idea → Project**

```bash
# Step 1: Evaluate business ideas
python scripts/run_vertical_agent.py inputs/ideas.json
# Output: Hair Salons wins (score: 84.0)

# Step 2: Strategic decision
python scripts/run_strategic_planner.py
# Prompt: Would you like to proceed? (Y/N)
# You type: Y

# Step 3: Planning Agent auto-invoked
# Creates: projects/ai-receptionist-for-hair-salons/

# Step 4: Review generated project
cat projects/ai-receptionist-for-hair-salons/planning/project_plan.yaml
```

**Time: 2-3 minutes from idea to scaffolded project!** ⚡

---

## 🧪 Testing

### **Test with Examples:**

```bash
# 1. Run vertical evaluation
python scripts/run_vertical_agent.py inputs/ideas.json

# 2. Run strategic planner (interactive)
python scripts/run_strategic_planner.py
# Type: Y to approve

# 3. Check outputs
cat outputs/strategic_decision.yaml
ls projects/
```

### **Test Non-Interactive:**

```bash
python scripts/run_strategic_planner.py --non-interactive
```

---

## 💡 Human Approval Benefits

### **Why Ask for Approval?**

1. ✅ **Human oversight** - Final check before resource allocation
2. ✅ **Context consideration** - Human can add business context
3. ✅ **Risk management** - Pause if timing isn't right
4. ✅ **Team alignment** - Get stakeholder buy-in
5. ✅ **Flexibility** - Can skip `--non-interactive` for automation

### **When to Use Interactive:**
- Team workshops
- Stakeholder reviews
- High-stakes decisions
- Initial project selection

### **When to Use Non-Interactive:**
- Automated workflows
- CI/CD pipelines
- Batch processing
- Testing

---

## 🔧 Customization

### **Change Score Thresholds:**

Edit `strategic_planner.py`:

```python
def _make_strategic_decision(self, top_vertical, vertical_result):
    score = top_vertical.get('score', 0)
    
    # Custom thresholds
    proceed = score >= 75  # Your custom threshold
    
    if score >= 120:  # Your custom threshold
        reasoning = "Exceptional opportunity..."
```

### **Custom Approval Logic:**

Add business rules, budget checks, resource availability, etc.

---

## 📊 Agent Protocol Integration

Compatible with Phase 9 protocol:

```python
AgentOutput(
    agent_name="StrategicPlannerAgent",
    decision="approve",  # or "conditional"
    reasoning="Moderate opportunity...",
    data_for_next_agent={
        'selected_project': 'ai-receptionist-for-hair-salons',
        'project_score': 84.0,
        'proceed_to_planning': True
    },
    confidence=0.6,
    flags=[]
)
```

---

## 🎯 Key Benefits

- ✅ **Bridges** Vertical Agent and Planning Agent
- ✅ **Human oversight** before resource commitment
- ✅ **Clear proposal** with score and reasoning
- ✅ **Auto-invokes** Planning Agent on approval
- ✅ **Complete audit trail** of decisions
- ✅ **Flexible** - interactive or automated

---

## 🚀 Next Steps

After Strategic Planner approves and creates project:

1. **Review** `projects/your-project/planning/`
2. **Address** gaps in `missing_info.md`
3. **Validate** `project_plan.yaml`
4. **Begin** development using generated structure

---

**Perfect for:**
- Strategic project selection
- Resource allocation decisions
- Team alignment on priorities
- Automated project initialization
- Portfolio management

---

*Strategic Planner Agent v1.0*  
*Management Team AI System - Phase 13*

