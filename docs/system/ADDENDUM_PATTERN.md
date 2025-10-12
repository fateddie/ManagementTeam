# 📝 PRD Addendum Pattern Documentation

**Version:** 1.0  
**Date:** 2025-10-11  
**Purpose:** Enable machine-readable extensions to human-readable PRDs

---

## Overview

The **PRD Addendum Pattern** separates human-readable project requirements from machine-parsable structured data. This allows:

1. **Human-Optimized PRDs** - Natural language, tables, diagrams remain in `.md` files
2. **Machine-Readable Extensions** - Milestones, risks, modules, phases in `.yaml` addendum files
3. **Automatic Merging** - Strategy Agent auto-detects and merges addendum data

---

## File Naming Convention

For a PRD file named `{name}.md`, the addendum must be named `{name}_addendum.yaml`.

**Examples:**
- `trading_strategy_prd.md` → `trading_strategy_prd_addendum.yaml`
- `project_requirements.md` → `project_requirements_addendum.yaml`
- `PRD.md` → `PRD_addendum.yaml`

---

## Addendum YAML Structure

```yaml
# ==========================================================
# Claude Parsing Addendum
# Project: [Your Project Name]
# Author: [Your Name]
# Date: YYYY-MM-DD
# Purpose: Machine-readable extensions to PRD
# ==========================================================

milestones:
  - id: M1
    name: "Milestone Name"
    description: "What this milestone achieves"
    duration_days: 14

risks:
  - id: R1
    description: "Risk description"
    mitigation: "How to mitigate this risk"

modules:
  - name: ModuleName
    purpose: "What this module does"
    inputs: [input1, input2]
    outputs: [output1, output2]

phases:
  - id: P1
    name: "Phase Name"
    duration_weeks: 6
    deliverables: [deliverable1, deliverable2]
```

---

## How It Works

### 1. Strategy Agent Auto-Detection

When initialized, Strategy Agent checks for addendum:

```python
# In __init__:
potential_addendum = self.prd_path.parent / (self.prd_path.stem + "_addendum.yaml")
self.addendum_path = potential_addendum if potential_addendum.exists() else None
```

### 2. Automatic Merging

After parsing PRD, Strategy Agent merges addendum:

```python
# In run():
strategy_data = self._generate_fallback(prd_text)  # or _generate_with_llm()

if self.addendum_path and self.addendum_path.exists():
    strategy_data = self._merge_addendum(strategy_data)
```

### 3. Merge Rules

- **Milestones**: Addendum **overrides** PRD-extracted milestones
- **Risks**: Addendum **overrides** PRD-extracted risks
- **Phases**: Addendum **adds** new field (not in standard strategy schema)
- **Modules**: Stored as `recommended_modules` for Technical Architect Agent

---

## Agent Consumption

### Strategy Agent
- Reads PRD markdown
- Extracts goals, constraints, priorities from PRD
- Merges milestones, risks, phases from addendum
- Outputs: `strategy_plan.yaml`

### Technical Architect Agent
- Reads `strategy_plan.yaml`
- Checks for `recommended_modules` field
- If present: Uses addendum modules
- If absent: Falls back to generic modules
- Outputs: `technical_design.yaml`

### Planning Agent
- Reads `strategy_plan.yaml` with merged data
- Uses milestones for dependency mapping
- Uses phases for roadmap generation
- Outputs: `project_plan.yaml`, `roadmap.md`, `dependency_map.yaml`

### Documentation Agent
- Reads `project_plan.yaml` (includes merged data)
- Formats phases, risks, milestones into PRD.md
- Outputs: `prd.md`, `tech_spec.md`, `final_summary.md`

---

## Benefits

### ✅ Version Control Friendly
- PRD remains stable (fewer conflicts)
- Addendum can be updated independently
- Clean separation of concerns

### ✅ Domain-Specific Extensions
- Trading project? Add confluence scoring modules
- Web app? Add authentication, API gateway modules
- Data pipeline? Add ETL, transformation modules

### ✅ No Agent Code Changes Required
- Strategy Agent automatically detects addendum
- Works with or without addendum file
- Backward compatible with existing PRDs

### ✅ Human + Machine Collaboration
- Humans write intuitive PRD markdown
- Machines consume structured addendum
- Best of both worlds

---

## Example: Trading Strategy Project

### File Structure
```
projects/swing-fx-trading-assistant/docs/
├── trading_strategy_prd.md          # Human-readable requirements
└── trading_strategy_prd_addendum.yaml  # Machine-readable extensions
```

### PRD (trading_strategy_prd.md)
```markdown
# Trading Strategy Reference System

## Goals
- Encode trading philosophy into standardized layers
- Enable Claude to generate trading plans
- Ensure consistency across documentation

## Dependencies
- Interactive Brokers API
- TradingView API/Pine Scripts
- COT/Sentiment Feeds
```

### Addendum (trading_strategy_prd_addendum.yaml)
```yaml
milestones:
  - id: M1
    name: "Interactive Brokers Integration"
    description: "Integrate Interactive Brokers API for trade and exposure data."
    duration_days: 14

modules:
  - name: MethodologyEngine
    purpose: "Bias formation using multi-timeframe analysis (Monthly→Weekly→Daily→4H)."
    inputs: [price_data, cot_data, sentiment_feeds]
    outputs: [directional_bias, market_narrative]
```

### Output (strategy_plan.yaml)
```yaml
project:
  name: Trading Strategy Reference System  # From PRD YAML frontmatter
goals:
  - Encode trading philosophy...  # From PRD markdown
milestones:
  - id: M1  # From addendum (overrides)
    name: "Interactive Brokers Integration"
recommended_modules:
  - name: MethodologyEngine  # From addendum → passed to Technical Architect
```

---

## Migration Guide

### For Existing Projects

1. **Create addendum file**:
   ```bash
   touch projects/{your-project}/docs/{prd-name}_addendum.yaml
   ```

2. **Copy template**:
   ```yaml
   milestones: []
   risks: []
   modules: []
   phases: []
   ```

3. **Populate with project-specific data**

4. **Re-run orchestrator**:
   ```bash
   PYTHONPATH=. python agents/orchestrator/orchestrator.py
   ```

5. **Verify outputs**:
   - Check `outputs/strategy_plan.yaml` for merged milestones/risks
   - Check `outputs/technical_design.yaml` for recommended modules

### For New Projects

1. Write PRD markdown with natural language
2. Create addendum with structured data
3. Run orchestrator - addendum merges automatically

---

## Troubleshooting

### Issue: Addendum Not Detected
**Symptom**: Milestones/risks still empty in output

**Check naming**:
```bash
# PRD file
ls projects/your-project/docs/*.md

# Expected addendum name
# If PRD is "foo_bar.md", addendum must be "foo_bar_addendum.yaml"
```

**Fix**:
```bash
mv projects/your-project/docs/wrong_name.yaml \
   projects/your-project/docs/correct_name_addendum.yaml
```

### Issue: Modules Not Appearing in Technical Design
**Check**: `outputs/strategy_plan.yaml` has `recommended_modules` field

**If missing**: Addendum wasn't merged (check naming)

**If present but not used**: Technical Architect may have error - check logs

---

## Advanced: Custom Addendum Fields

You can add custom fields to addendum:

```yaml
# Standard fields
milestones: [...]
risks: [...]

# Custom fields
compliance_requirements:
  - GDPR data retention
  - SOC2 audit trail

performance_targets:
  latency_p99: 100ms
  throughput: 10000 rps
```

Access in Strategy Agent:
```python
if 'compliance_requirements' in addendum:
    strategy_data['compliance'] = addendum['compliance_requirements']
```

---

## References

- **Strategy Agent**: `agents/strategy_agent/strategy_agent.py`
- **Technical Architect**: `agents/technical_architect/architect_agent.py`
- **Example Addendum**: `projects/swing-fx-trading-assistant/docs/trading_strategy_prd_addendum.yaml`

---

**Generated by:** Rob Freyne + Claude Code  
**Last Updated:** 2025-10-11
