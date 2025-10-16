# Orchestrator Script — Technical Documentation

The facilitator agent uses this logic to run the SOP interactively.

---

## State Flow

```
1. KICK-OFF
   ↓
   Load: kick_off.txt
   Save: idea_intake.json
   
2. VARIANT GENERATION
   ↓
   Load: variant_generation.txt
   User selects variant(s)
   
3. PHASE LOOP (1-12)
   ↓
   For each phase:
     - Load: phase_template.txt
     - Display phase instructions
     - Collect user input
     - Save to appropriate file
     - Gate decision (Confirm/Revise/Park)
     - Log to audit_trail.json
     - Update state_schema.json
   
4. COMPARISON (Phase 13)
   ↓
   Load: comparison_prompt.txt
   Generate comparison matrix
   Save: reports/comparison_matrix.md
   
5. HYBRIDIZATION / DECISION
   ↓
   User chooses: Advance / Combine / Park
   Log final decision
   Return to SOP
```

---

## Behaviour Rules

### **1. Never Auto-Advance Without Confirmation**

The orchestrator **must wait** for user approval before moving to the next phase.

**Gate Options:**
- **Confirm (C):** Proceed to next phase
- **Revise (R):** Re-do current phase with new inputs  
- **Park (P):** Pause variant, save state, exit gracefully

### **2. Persist State in `state_schema.json`**

After every phase, save:
```json
{
  "variant_name": "variant_1",
  "phase": 6,
  "status": "in_progress",
  "last_updated": "2025-10-16T10:30:00Z"
}
```

This enables:
- Resuming parked variants
- Tracking progress across sessions
- Audit trail of all actions

### **3. Log Every Decision to `audit_trail.json`**

Every approval, revision, or park decision gets logged:
```json
[
  {
    "variant": "variant_1",
    "phase": 6,
    "decision": "Approved",
    "timestamp": "2025-10-16T09:15:00Z",
    "notes": "Pain scores validated with 45 data points"
  }
]
```

### **4. Validate Outputs**

Before moving to next phase, check:
- Required files exist
- JSON files are valid JSON
- YAML files are valid YAML
- All metrics have sources (where applicable)

---

## Example CLI Usage

### **Start New Variant:**
```bash
python orchestrator.py --variant variant_1
```

### **Resume Parked Variant:**
```bash
python orchestrator.py --variant variant_1
# Will resume at last saved phase
```

### **Compare All Variants:**
```bash
python orchestrator.py --compare
```

### **Custom Variant Name:**
```bash
python orchestrator.py --variant email_for_freelancers
```

---

## Phase-to-File Mapping

| Phase | Phase Name | Output File |
|-------|------------|-------------|
| 0 | Intake & Ownership | `idea_intake.json` |
| 1 | Hypothesis & Scope | `scope.yaml` |
| 2 | Research Plan | `research_plan.md` |
| 3 | Evidence Collection | `/data/raw/variant_X/` |
| 4 | Cleaning & Chain-of-Custody | `/data/clean/variant_X/` |
| 5 | Pain Extraction & Tagging | `pains_tagged.json` |
| 6 | Pain Quantification | `pain_scores.json` |
| 7 | Market & Competition | `market_competition.md` |
| 8 | Unit Economics | `unit_economics.json` |
| 9 | Feasibility & Risk | `feasibility_risk.md` |
| 10 | GTM Options & Prioritisation | `gtm_options.md` |
| 11 | Synthesis (ADSR Report) | `report_ADSR.md` |
| 12 | Decision & Logging | `decision_log.json` |
| 13 | Cross-Variant Comparison | `/reports/comparison_matrix.md` |

---

## Error Handling

### **Missing Prompt File:**
```python
def load_prompt(prompt_name):
    prompt_path = f"agent/prompts/{prompt_name}.txt"
    if not os.path.exists(prompt_path):
        return f"[Prompt {prompt_name} not found - using generic]"
    return open(prompt_path).read()
```

### **Invalid JSON Input:**
```python
try:
    data = json.loads(user_input)
    save_json(output_path, data)
except json.JSONDecodeError:
    # Save as wrapped object
    save_json(output_path, {
        "phase": phase_num,
        "raw_input": user_input,
        "timestamp": timestamp()
    })
```

### **Parked Variant Resume:**
```python
state = load_json(STATE_FILE, default_state)
if state.get("status") == "parked":
    print(f"Resuming from Phase {state['phase']}")
```

---

## Extension Points

### **1. Integrate Workshop Agent for Phase 3**

```python
# In orchestrator.py, Phase 3:
if phase_num == 3:
    print("📊 Gathering market data using Workshop Agent...")
    from agents.workshop_agent.workshop_agent import IterativeWorkshopAgent
    workshop = IterativeWorkshopAgent()
    market_data = workshop._gather_market_data(variant_idea)
    save_json(f"data/raw/{variant}/market_data.json", market_data)
```

### **2. Add Streamlit UI**

```python
# streamlit_variant_explorer.py
import streamlit as st
from orchestrator import run_orchestrator

st.title("Variant Exploration System")
variant_name = st.text_input("Variant Name:")
if st.button("Start"):
    run_orchestrator(variant_name)
```

### **3. Add Email Notifications**

```python
def notify_on_completion(variant, phase):
    if phase == 13:
        send_email(f"Variant {variant} completed!")
```

### **4. Add Database Storage**

```python
# Instead of JSON files:
def save_phase_output(variant, phase, data):
    db.execute(
        "INSERT INTO phase_outputs (variant, phase, data) VALUES (?, ?, ?)",
        (variant, phase, json.dumps(data))
    )
```

---

## Performance Considerations

### **Large Variants:**
- Phase 3 (Evidence Collection) can take 5-10 minutes if using Perplexity
- Consider showing progress indicator:
  ```python
  for i, query in enumerate(queries):
      print(f"Query {i+1}/{len(queries)}: {query[:50]}...")
  ```

### **Many Variants:**
- Comparison matrix can get large with 5+ variants
- Consider pagination or filtering:
  ```python
  if len(variants) > 3:
      print("Showing top 3 ranked variants...")
  ```

---

## Testing

### **Unit Tests:**
```python
def test_phase_file_mapping():
    assert PHASE_FILES[0] == "idea_intake.json"
    assert PHASE_FILES[6] == "pain_scores.json"
```

### **Integration Tests:**
```python
def test_full_workflow():
    # Run complete workflow with test inputs
    run_orchestrator("test_variant_1")
    assert os.path.exists("projects/test_variant_1/decision_log.json")
```

---

## Governance & Audit

### **All decisions are logged:**
```json
[
  {"variant": "v1", "phase": 3, "decision": "Approved", "timestamp": "..."},
  {"variant": "v1", "phase": 6, "decision": "Revised", "timestamp": "..."},
  {"variant": "v2", "phase": 9, "decision": "Parked", "timestamp": "..."}
]
```

### **Chain of custody for all data:**
- Raw data: `/data/raw/`
- Cleaned data: `/data/clean/`
- Processed data: `/data/processed/`
- Logs: `/logs/cleaning_log.txt`, `/logs/scoring_log.json`

### **Traceability:**
Every metric must include:
- Source URL or identifier
- Date accessed
- Method of collection
- Confidence level

---

## Future Enhancements

1. **AI-Assisted Input:**
   - Pre-fill phases using Workshop Agent
   - User reviews and confirms/edits
   
2. **Collaborative Mode:**
   - Multiple team members can contribute to phases
   - Version control for phase outputs
   
3. **Template Library:**
   - Industry-specific templates (SaaS, marketplace, etc.)
   - Pre-loaded research questions
   
4. **Auto-Comparison:**
   - Automatically rank variants by success criteria
   - Highlight best performer in each metric

---

**This documentation covers the technical implementation of the orchestrator.**

For user-facing instructions, see `QUICKSTART.md`.

