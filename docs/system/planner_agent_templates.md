---
title: Planner Agent Templates
author: Rob Freyne
date: 2025-10-10
version: 1.1
status: Updated
---

# 📘 Planner Agent Templates (Unified Architecture)

This document defines the **baseline templates** used by the Planner Agent for consistent project scaffolding inside the unified **ManagementTeam** system.

---

## 1. project_plan.yaml (Schema Template)

```yaml
# ==============================================
# Project Plan Template (v1.1)
# ==============================================
meta:
  title: <string>
  author: <string>
  date_created: <YYYY-MM-DD>
  version: 1.0
  status: draft | active | archived

project:
  overview:
    summary: <string>
    goals:
      - <goal_1>
      - <goal_2>
    scope:
      include:
        - <item_1>
      exclude:
        - <item_2>
    stakeholders:
      - name: <string>
        role: <string>
        responsibility: <string>

objectives:
  - id: OBJ-001
    description: <string>
    success_metric: <string>
    priority: high | medium | low

milestones:
  - id: M1
    name: <string>
    description: <string>
    start_date: <YYYY-MM-DD>
    end_date: <YYYY-MM-DD>
    duration_days: <int>
    dependencies:
      - <milestone_id>

risks:
  - id: RSK-001
    description: <string>
    impact: high | medium | low
    likelihood: high | medium | low
    mitigation_strategy: <string>

resources:
  people:
    - name: <string>
      role: <string>
      availability: <percentage>
  tools:
    - name: <string>
      purpose: <string>
      license: <type>

success_criteria:
  - metric: <string>
    target: <value>
    method: <string>

notes:
  - <string>
```

**Location:** `/config/templates/project_plan.yaml`

---

## 2. roadmap.md (Markdown Template)

```markdown
# 🗺️ Project Roadmap

**Project:** {{ title }}  
**Version:** {{ version }}  
**Author:** {{ author }}  
**Date:** {{ date_created }}

---

## Overview

{{ summary }}

---

## Major Milestones

| ID  | Milestone | Description   | Duration | Dependencies | Status  |
| --- | --------- | ------------- | -------- | ------------ | ------- |
| M1  | <Name>    | <Description> | 3 days   | —            | Pending |
| M2  | <Name>    | <Description> | 5 days   | M1           | Pending |
| M3  | <Name>    | <Description> | 7 days   | M2           | Pending |

---

## Timeline (Example Gantt Summary)

M1: [#####.....] Week 1
M2: [######....] Week 2
M3: [########..] Week 3

---

## Key Deliverables

- [ ] Define requirements
- [ ] Build prototype
- [ ] Integrate memory layer
- [ ] Conduct review & testing
- [ ] Finalize documentation

---

## Dependencies

- Claude Code environment setup complete
- Cursor workspace initialized
- Access to Mem0 API keys granted

---

## Risks & Mitigations

| Risk                   | Impact | Mitigation                                  |
| ---------------------- | ------ | ------------------------------------------- |
| Vendor lock-in         | High   | Build abstraction layer for memory services |
| Time estimation errors | Medium | Conduct weekly progress reviews             |
| Context overload       | Medium | Implement summarization pipelines           |

---

## Review Schedule

| Review          | Date       | Owner            | Purpose           |
| --------------- | ---------- | ---------------- | ----------------- |
| Kickoff Review  | YYYY-MM-DD | Rob              | Confirm scope     |
| Midpoint Review | YYYY-MM-DD | Planner Agent    | Evaluate progress |
| Final Review    | YYYY-MM-DD | Reflection Agent | Assess outcomes   |
```

**Location:** `/config/templates/roadmap.md`

---

## 3. folder_structure.json (Baseline Template)

```json
{
  "project_root": "<project-name>",
  "structure": {
    "planning": ["project_plan.yaml", "roadmap.md", "milestones.json"],
    "docs": ["PRD.md", "tech_spec.md", "ERD.png", "DFD.png", "progress_log.md"],
    "control": ["Claude.md", "Rules.md", "ProgressLog.md"],
    "environment": ["environment.sh", "requirements.txt", ".env"],
    "memory": ["mem0_adapter.py", "policies.yaml", "neo4j_exporter.py"],
    "root_files": ["README.md"]
  }
}
```

**Location:** `/config/templates/folder_structure.json`

---

## 4. missing_info.md (Prompt Template)

```markdown
# ❓ Missing Information

The Planner Agent identified missing or unclear information. Please provide the following details:

1. [ ] Define the primary stakeholders (names & roles)
2. [ ] Clarify target users or departments for this project
3. [ ] Specify success metrics for each objective
4. [ ] Confirm desired timeline and deadlines
5. [ ] Indicate required integrations (APIs, data sources, etc.)
6. [ ] Highlight known risks or dependencies

Once complete, rerun the Planner Agent to update the project plan.
```

**Location:** `/config/templates/missing_info.md`

---

## 5. Usage Notes

- Templates are stored in `/config/templates/` and read by the Planner Agent at runtime.
- Variables within `{{ ... }}` are dynamically populated by the agent.
- Users can override templates per project in `/projects/<project_name>/planning/templates/`.
- All outputs are version-controlled and time-stamped automatically.

---

## ✅ Integration Summary

| Component               | Purpose                                         | Path                                 |
| ----------------------- | ----------------------------------------------- | ------------------------------------ |
| **Planner Agent**       | Reads templates and generates project structure | `/src/agents/planner_agent.py`       |
| **Documentation Agent** | Consumes generated PRD + roadmap                | `/src/agents/documentation_agent.py` |
| **Mem0 Adapter**        | Logs metadata about generated projects          | `/memory/mem0_adapter.py`            |
| **Scripts**             | Automate testing and execution                  | `/scripts/run_planner.py`            |

---

**Next Step:** Integrate these templates into the Planner Agent's build process and verify output consistency using schema validation under `/tests/test_planner_agent.py`.
