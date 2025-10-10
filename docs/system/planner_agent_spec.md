---
title: Planner Agent Specification
author: Rob Freyne
date: 2025-10-10
version: 1.1
status: Updated
---

# 🧩 Planner Agent Specification (Unified Architecture)

## 1. Purpose

The **Planner Agent** is the foundational component of the AI Management Layer within the unified ManagementTeam system. It is responsible for collecting high-level project goals, eliciting missing details, and generating structured planning artifacts such as PRDs, roadmaps, and milestone definitions. It ensures each new project is initialized within the unified directory structure.

---

## 2. Objectives

- Convert natural-language project descriptions into structured YAML and Markdown documentation.
- Identify missing information and prompt the user for clarification.
- Automatically generate the standardized `/projects/<project_name>/` folder structure.
- Create a baseline roadmap with estimated durations and dependencies.
- Handoff outputs to the Documentation Agent for technical detailing.

---

## 3. Inputs

| Input Type          | Description                                                      | Format          |
| :------------------ | :--------------------------------------------------------------- | :-------------- |
| Project Description | Free-form text describing the project's intent, scope, and goals | Text            |
| User Preferences    | Settings for documentation style, naming, and structure          | JSON / YAML     |
| Existing Context    | Related context from Mem0 (previous projects, goals)             | JSON            |
| Templates           | Default PRD and roadmap templates from `/config/`                | Markdown / YAML |

---

## 4. Outputs

| Output                 | Description                                                         | Location                                  |
| :--------------------- | :------------------------------------------------------------------ | :---------------------------------------- |
| `project_plan.yaml`    | Structured definition of objectives, milestones, deliverables, etc. | `/projects/<project_name>/planning/`      |
| `roadmap.md`           | Human-readable roadmap showing sequencing and timelines             | `/projects/<project_name>/planning/`      |
| `folder_structure.json`| Directory schema defining the new project                           | `/config/`                                |
| `missing_info.md`      | List of open questions for the user to clarify                      | `/projects/<project_name>/planning/`      |

---

## 5. Process Flow

1. **Input Gathering**: Parse user's description and identify key entities.
2. **Elicitation Loop**: Ask clarification questions for incomplete data.
3. **Structure Generation**: Create YAML and Markdown outputs following unified standards.
4. **Dependency Mapping**: Link deliverables and milestones.
5. **Folder Initialization**: Build the `/projects/<project_name>/` directory with correct subfolders.
6. **Handoff**: Forward structured files to the Documentation Agent.

---

## 6. Core Components

| Component          | Function                                                 |
| :----------------- | :------------------------------------------------------- |
| Input Parser       | Extracts entities, actions, and constraints from input   |
| Elicitation Engine | Dynamically generates clarification prompts             |
| Template Engine    | Populates YAML and Markdown templates                   |
| Folder Builder     | Creates folder hierarchy under `/projects/`             |
| Memory Connector   | Registers project context with Mem0 memory              |

---

## 7. File Paths (Unified)

```
/ManagementTeam/
├── config/
│   ├── global.yaml
│   ├── templates/
│   │   ├── project_plan.yaml
│   │   ├── roadmap.md
│   │   ├── folder_structure.json
│   │   └── missing_info.md
│
├── src/agents/planner_agent.py
├── src/utils/
│   ├── io_utils.py
│   ├── parser_utils.py
│   ├── template_utils.py
│   ├── validation_utils.py
│   └── elicitation_utils.py
│
└── projects/<project_name>/planning/
    ├── project_plan.yaml
    ├── roadmap.md
    ├── missing_info.md
    └── milestones.json
```

---

## 8. Claude Code Integration

**System Prompt:**

> You are the Planner Agent within the ManagementTeam architecture. Your task is to generate structured documentation and initialize standardized project folders under `/projects/<project_name>/`. Use provided templates from `/config/templates/`. Always validate output and ensure schema compliance.

**Example Prompt:**

> "I want to build an AI agent that manages daily trading reports and sentiment analysis."

**Response:**
- Clarification questions
- `project_plan.yaml` with project objectives
- `roadmap.md` with milestones
- Auto-generated `/projects/trading-assistant/` folder

---

## 9. Integration Points

| Integration          | Description                                           |
| :------------------- | :---------------------------------------------------- |
| Documentation Agent  | Consumes outputs to generate ERDs, DFDs, tech specs   |
| Execution Agent      | Uses generated plans for build orchestration          |
| Memory Agent (Mem0)  | Stores project metadata and relationships             |
| Reflection Agent     | Evaluates plan quality post-execution                 |

---

## 10. Success Criteria

| Metric                           | Target    |
| :------------------------------- | :-------- |
| % of projects scaffolded correctly | ≥ 95 %    |
| YAML validation success rate     | 100 %     |
| Average planning time            | < 3 min   |
| Relevant elicitation coverage    | ≥ 85 %    |
| Integration readiness            | 100 %     |

---

## 11. Future Enhancements

- Introduce AI-based project type classification (auto-template selection)
- Add CLI command for quick project generation (`scripts/run_planner.py`)
- Integrate dashboard updates for new projects
- Expand Mem0 memory schema for project lineage tracking

