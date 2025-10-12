# 🎯 Vertical Agent - Business Opportunity Evaluator

**Purpose:** Evaluates and scores business vertical ideas to recommend the best next project to pursue.

---

## 🚀 Quick Start

### Run with Example Data

```bash
python scripts/run_vertical.py
```

### Run with Custom YAML

```bash
# Edit inputs/verticals.yaml with your ideas
python agents/vertical_agent/vertical_agent.py
```

### Use in Code

```python
from agents.vertical_agent.vertical_agent import run_vertical_agent

ideas = [
    {"name": "Golf Courses", "reach": 6, "impact": 7, "confidence": 8, "effort": 4},
    {"name": "Car Garages", "reach": 7, "impact": 8, "confidence": 7, "effort": 3},
]

result = run_vertical_agent(ideas)
print(result['summary'])
```

---

## 📊 RICE Scoring Framework

**RICE = (Reach × Impact × Confidence) / Effort**

| Factor | Range | Description |
|--------|-------|-------------|
| **Reach** | 1-10 | Market size / number of potential customers |
| **Impact** | 1-10 | Value created / improvement magnitude |
| **Confidence** | 1-10 | Certainty in estimates / proven model |
| **Effort** | 1-10 | Implementation complexity (higher = harder) |

### Scoring Guidance

**Reach (Market Size):**
- 1-3: Niche market (< 10K potential customers)
- 4-6: Medium market (10K-100K customers)
- 7-10: Large market (> 100K customers)

**Impact (Value Creation):**
- 1-3: Minor improvement
- 4-6: Moderate value
- 7-10: Major transformation

**Confidence (Certainty):**
- 1-3: Low confidence / high uncertainty
- 4-6: Moderate confidence
- 7-10: High confidence / proven model

**Effort (Implementation):**
- 1-3: Simple / quick to build
- 4-6: Moderate complexity
- 7-10: Complex / resource intensive

---

## 📁 File Structure

```
agents/vertical_agent/
├── __init__.py              # Package initialization
├── vertical_agent.py        # Main agent logic
└── README.md               # This file

src/utils/
└── scoring_utils.py        # RICE/ICE scoring functions

scripts/
└── run_vertical.py         # CLI runner script

inputs/
└── verticals.yaml          # Business vertical ideas (YAML)

outputs/
└── vertical_scores.yaml    # Scored results (auto-generated)
```

---

## 🎮 Usage Examples

### Example 1: Quick Evaluation

```python
from agents.vertical_agent.vertical_agent import run_vertical_agent

ideas = [
    {"name": "Pet Grooming", "reach": 4, "impact": 6, "confidence": 9, "effort": 2},
    {"name": "Dental Practices", "reach": 7, "impact": 8, "confidence": 8, "effort": 4},
]

result = run_vertical_agent(ideas)

print(result['summary'])
# Output: 🏆 Recommend pursuing: Pet Grooming (score: 108.0)

print(result['top_choice'])
# {'name': 'Pet Grooming', 'reach': 4, 'impact': 6, 'confidence': 9, 'effort': 2, 'score': 108.0}
```

### Example 2: Class-Based (Orchestrator Integration)

```python
from agents.vertical_agent.vertical_agent import VerticalAgent

agent = VerticalAgent(
    verticals_path="./inputs/verticals.yaml",
    output_path="./outputs/vertical_scores.yaml",
    framework="RICE"
)

result = agent.run()
# Loads from YAML, scores, saves, returns AgentOutput
```

### Example 3: Custom YAML Input

Create `inputs/verticals.yaml`:

```yaml
verticals:
  - name: "Your Business Idea"
    reach: 7
    impact: 8
    confidence: 6
    effort: 4
    description: "What it does..."
    
  - name: "Another Idea"
    reach: 5
    impact: 9
    confidence: 8
    effort: 3
    description: "Alternative option..."
```

Then run:

```bash
python agents/vertical_agent/vertical_agent.py
```

---

## 🔗 Orchestrator Integration

Add to `agents/orchestrator/agent_registry.yaml`:

```yaml
agents:
  - name: VerticalAgent
    path: "agents.vertical_agent.vertical_agent:VerticalAgent"
    active: true
    stage: 0.5  # Runs before Strategy Agent
```

The agent will:
1. Load verticals from `inputs/verticals.yaml`
2. Score using RICE framework
3. Output recommendation via `AgentOutput` protocol
4. Pass top vertical to Strategy Agent

---

## 📈 Output Format

### Returned Dict

```python
{
    "top_choice": {
        "name": "Hair Salons",
        "reach": 5,
        "impact": 6,
        "confidence": 9,
        "effort": 2,
        "score": 135.0,
        "framework": "RICE"
    },
    "alternatives": [...],  # Top 3 alternatives
    "all_ranked": [...],    # Full list, sorted
    "summary": "🏆 Recommend pursuing: Hair Salons (score: 135.0)"
}
```

### Saved YAML (`outputs/vertical_scores.yaml`)

```yaml
top_choice:
  name: Hair Salons
  reach: 5
  impact: 6
  confidence: 9
  effort: 2
  score: 135.0
  
all_ranked:
  - name: Hair Salons
    score: 135.0
    ...
  - name: Car Garages
    score: 130.67
    ...
```

---

## 🧪 Testing

```bash
# Run with example data
python scripts/run_vertical.py

# Run with YAML input
python agents/vertical_agent/vertical_agent.py

# Run via orchestrator
python cli/manage.py run
```

---

## 💡 Next Steps

1. **Customize Verticals:** Edit `inputs/verticals.yaml` with your business ideas
2. **Adjust Scores:** Fine-tune reach, impact, confidence, effort values
3. **Feed to Strategy Agent:** Use top recommendation as input for detailed planning
4. **Integrate with Orchestrator:** Add to agent registry for automated workflow

---

## 📊 Example Output

```
======================================================================
🎯 VERTICAL AGENT - Business Opportunity Evaluation
======================================================================

🏆 RECOMMENDATION: Hair Salons (score: 135.0)

📊 FULL RANKING:
   🥇 1. Hair Salons          Score:   135.00
   🥈 2. Car Garages          Score:   130.67
   🥉 3. Fitness Studios      Score:   112.00
      4. Golf Courses         Score:    84.00
      5. Restaurants          Score:    67.20

✅ Evaluation Complete!
```

---

## 🎯 Key Features

✅ Simple RICE scoring framework  
✅ YAML input support  
✅ Function-based or class-based usage  
✅ Orchestrator integration ready  
✅ AgentOutput protocol compatible  
✅ Caching support  
✅ Beautiful CLI output  
✅ Saves results to YAML  

---

**Created:** Phase 12 - Vertical Agent Enhancement  
**Author:** Management Team AI System  
**Status:** ✅ Complete & Tested

