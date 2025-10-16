---
title: "PRD-03 — Agent Roles & Prompts"
version: "1.0"
owner: "Rob"
date: "2025-10-16"
project: "Variant Exploration System"
status: "Planned"
description: >
  Defines the agent architecture and prompt specifications for human‑in‑loop
  operation of the Variant Exploration System (VES). Each agent controls one
  domain of the SOP process and interacts with templates and schemas created
  in PRD‑01 and PRD‑02.
---

# 📘 PRD‑03 — Agent Roles & Prompts

## 1️⃣ Objective
Design a modular multi‑agent framework where each agent handles a clear
functional domain—Planning, Market Intelligence, Finance, Risk, and
Documentation—while the **Orchestrator** coordinates their workflow through
elicitation prompts and approval gates.

Agents guide the human decision‑maker through the SOP process, ensuring every
artifact is completed correctly and justified with reasoning.

---

## 2️⃣ Scope

### Included
- Five core domain agents + one orchestrator supervisor.
- Each agent defined by:  
  • purpose and responsibilities  
  • input/output files  
  • default prompts and interaction pattern  
- Directory path: `/agents/` (one markdown file per agent).

### Excluded
- Model orchestration code (PRD‑04).  
- Automated API data collectors (future extension).  
- Non‑core support agents (e.g., summarization, trend discovery).

---

## 3️⃣ Agent Overview

| Agent | Primary Role | Key Interactions | Output |
|--------|---------------|------------------|--------|
| **Planner Agent** | Guides SOP flow, ensures correct gating and milestone tracking. | Orchestrator, all templates. | phase approvals, state logs |
| **Market Intelligence Agent** | Conducts evidence gathering and competitive analysis. | research_plan.md, pains_tagged.json, market_competition.md | summarized findings, source logs |
| **Finance Agent** | Calculates ROI, LTV:CAC, payback. | unit_economics.json, gtm_options.md | economics tables, sensitivity notes |
| **Risk Agent** | Identifies operational and compliance risks. | risk_register.json, feasibility_risk.md | risk register entries |
| **Documentation Agent** | Assembles reports and maintains audit trail. | report_ADSR.md, decision_log.json | finalized docs + citations |
| **Orchestrator (Supervisor)** | Coordinates all agents and gates. | All above agents | workflow state, consolidated outputs |

---

## 4️⃣ Prompt & Interaction Patterns

### 4.1 Planner Agent (`planner_agent.md`)
**Purpose:** Manage SOP phase progression and confirmations.

**Prompt Example:**
```
You are the Planner Agent. Your job is to guide the user through each SOP
phase step‑by‑step. For each phase:
1. Display the objective.
2. Ask clarifying questions.
3. Confirm before saving.
Use concise language and record every decision in /logs/audit_trail.json.
```

**Inputs:** SOP index, state_schema.json  
**Outputs:** phase confirmation log, next‑step instructions

---

### 4.2 Market Intelligence Agent (`market_agent.md`)
**Purpose:** Help gather and interpret market and customer evidence.

**Prompt Example:**
```
You are the Market Intelligence Agent.
Use research_plan.md as your reference.
Guide the user to extract pain points, segment frequency, and competitor data.
For each data point, record:
  - What was found (quote or metric)
  - Where (URL or platform)
  - Why it matters commercially
```
**Outputs:** pains_tagged.json, pain_scores.json, market_competition.md

---

### 4.3 Finance Agent (`finance_agent.md`)
**Purpose:** Quantify financial viability.

**Prompt Example:**
```
You are the Finance Agent.
Your task is to calculate basic unit economics using the data in
unit_economics.json. Ask for:
  - Expected price point
  - CAC assumptions
  - LTV estimate
  - Payback months
  - Confidence level
Explain the reasoning behind each assumption.
```
**Outputs:** unit_economics.json, sensitivity notes

---

### 4.4 Risk Agent (`risk_agent.md`)
**Purpose:** Capture compliance, operational, and execution risks.

**Prompt Example:**
```
You are the Risk Agent.
Identify risks from feasibility_risk.md and external context.
For each risk:
  - Describe it
  - Rate impact (Low/Med/High)
  - Rate probability (Low/Med/High)
  - Suggest mitigation
Always explain why this risk matters.
```
**Outputs:** risk_register.json

---

### 4.5 Documentation Agent (`doc_agent.md`)
**Purpose:** Ensure every artifact is properly documented and cited.

**Prompt Example:**
```
You are the Documentation Agent.
Assemble the final report_ADSR.md by combining inputs from all agents.
Ensure every metric has a citation (URL + date + method).
Generate the decision_log.json and maintain /logs/audit_trail.json.
```
**Outputs:** report_ADSR.md, decision_log.json, audit trail

---

### 4.6 Orchestrator (Supervisor)
**Purpose:** Coordinate agent execution and enforce gate logic.

**Prompt Example:**
```
You are the Orchestrator.
Read current phase from state_schema.json.
Activate the relevant agent, await completion, then request user confirmation
before proceeding to the next phase.
No phase may advance without explicit user approval.
```
**Outputs:** updated state_schema.json, consolidated logs

---

## 5️⃣ Acceptance Criteria

| ID | Requirement | Verification |
|----|--------------|--------------|
| AR-1 | Each agent has its own markdown definition file | Directory listing |
| AR-2 | Prompts clearly specify purpose, steps, and outputs | Manual review |
| AR-3 | Agent outputs match schema + template fields | Cross‑check |
| AR-4 | Planner agent enforces confirmation gates | Functional test |
| AR-5 | Documentation agent maintains full audit trail | Log inspection |

---

## 6️⃣ Dependencies

| Dependency | Type | Relation |
|-------------|------|----------|
| PRD‑01 Schema Layer | Upstream | Provides structured field definitions |
| PRD‑02 Templates | Upstream | Provides artifact placeholders |
| PRD‑04 Orchestrator | Downstream | Consumes agent prompts to run workflow |

---

## 7️⃣ Milestones

| Step | Deliverable | ETA | Owner |
|------|--------------|-----|-------|
| M1 | Draft markdown prompt files for each agent | Day 1 | Dev Agent |
| M2 | Cross‑check consistency with schema & templates | Day 2 | Rob |
| M3 | Commit and tag `agents-v1.0` | Day 2 | Planner Agent |

---

## 8️⃣ Success Metrics
- 100 % agent coverage of SOP responsibilities.  
- Prompts fully align with templates and schema fields.  
- Agents generate consistent, auditable outputs.  

---

## 9️⃣ Risks & Mitigations

| Risk | Impact | Mitigation |
|-------|---------|------------|
| Prompt drift or inconsistency | High | Centralize all prompts in `/agents/` directory |
| Overlap in agent responsibilities | Medium | Keep single source of truth in Orchestrator |
| Missing audit documentation | Low | Documentation agent verifies logs each cycle |

---

## ✅ Approval

| Role | Name | Date | Signature |
|------|------|------|------------|
| Product Owner | Rob | 2025‑10‑16 | — |
| Technical Reviewer | TBD | — | — |
