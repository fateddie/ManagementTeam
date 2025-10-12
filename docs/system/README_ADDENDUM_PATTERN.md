# Quick Start: PRD Addendum Pattern

## What It Solves
Human-readable PRDs (markdown) + Machine-readable extensions (YAML) = Best of both worlds

## Usage

### 1. Create Addendum File
For PRD: `my_project_prd.md`  
Create: `my_project_prd_addendum.yaml`

### 2. Add Structured Data
```yaml
milestones:
  - id: M1
    name: "API Integration"
    description: "Connect to external API"
    duration_days: 14

risks:
  - id: R1
    description: "API rate limits"
    mitigation: "Implement caching layer"

modules:
  - name: DataProcessor
    purpose: "Process incoming data"
    inputs: [raw_data]
    outputs: [processed_data]
```

### 3. Run Workflow
```bash
PYTHONPATH=. python agents/orchestrator/orchestrator.py
```

### 4. Verify Outputs
- `outputs/strategy_plan.yaml` - Contains merged milestones + risks
- `outputs/technical_design.yaml` - Uses recommended modules
- `outputs/prd.md` - Formatted documentation with all data

## Key Files
- Full Documentation: `docs/system/ADDENDUM_PATTERN.md`
- Example Addendum: `projects/swing-fx-trading-assistant/docs/trading_strategy_prd_addendum.yaml`
- Strategy Agent Code: `agents/strategy_agent/strategy_agent.py:281-314`
