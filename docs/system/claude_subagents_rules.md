# Claude Code — Subagent Orchestration Rules (Cursor-Specific)

> **⚠️ NOTE:** This document contains the original Cursor-specific sub-agent rules. For **Claude Code** usage, see the comprehensive sub-agent system documentation in `.claude/rules.md` (v4.0) which includes the fully-implemented Phase 1-5 system with ExplorerAgent, HistorianAgent, CriticAgent, and ResearchDocumenter.
>
> **This file is kept for:**
> - Reference for Cursor-based workflows
> - Historical context on original design
> - Alternative implementation approaches
>
> **For current Claude Code usage:** See `.claude/rules.md` → Section "🤖 SUB-AGENT SYSTEM"

---

## Original Goal (Cursor Context)

Enable Claude Code to **automatically decide** when to invoke helpful subagents during project creation and task execution in Cursor—**without** Rob manually choosing. Keep it simple; prefer reuse of existing tools and data. No over‑engineering.

---

## 0) Operating Principles (read first)
- **Simplicity first:** prefer the smallest working solution; avoid new infra unless necessary.
- **Autonomy with guardrails:** you (Claude) decide *when* to use subagents based on the rules below.
- **Re‑use existing context:** detect and leverage any current DBs, docs, READMEs, and prior decision notes.
- **Document decisions briefly:** when a subagent is invoked, write a one‑line reason to `/.history/decisions.log`.
- **Stop when unclear:** if confidence < 0.6 or prerequisites missing, ask a single clarifying question, then proceed.

---

## 1) Core Subagents (and when to use them)

### A. Explorer
**Purpose:** locate relevant code/files quickly to minimize main‑agent context load.  
**Trigger rules (any):**
- Task involves refactor, bugfix, or feature affecting **>2 files** or **>150 LOC**.
- Filename/path unknown; need to map module/class/function definitions.
- Repo unfamiliar or recently changed (>100 modified LOC since last checkpoint).

**Actions:**
1. Build a *targeted* file map (only relevant paths).
2. Return a compact findings summary: paths, symbols, 1–2 line notes per item.
3. Store to `/.history/explorer/{timestamp}.md` and reference it in the main plan.

---

### B. Research Documenter
**Purpose:** deep, parallelized doc research for **large integrations**.  
**Trigger rules (any):**
- Adding/majorly upgrading a library, SDK, or external API.
- New auth, rate‑limits, webhooks, streaming, or concurrency model.
- “Unknown unknowns” admitted by the model (confidence < 0.6).

**Actions:**
1. Run **parallel** targeted queries (official docs first; then issues/examples).
2. Produce a short **Implementation Brief** with: capabilities, constraints, minimal example, pitfalls, and a 5‑step integration plan.
3. Save to `/.history/research/{lib-or-topic}-{timestamp}.md`; cite sources.
4. Extract a 10‑line **Checklist** for the Planner to consume.

---

### C. Historian
**Purpose:** lightweight, LLM‑readable project memory (snapshots > Git diffs).  
**Trigger rules (any):**
- End of a focused work block **or** >150 modified LOC **or** after PRD/architecture updates.
- Before major refactor or dependency changes.

**Actions:**
1. Snapshot key files (paths only + 10‑line summaries per file), rationale, open risks.
2. Write to `/.history/checkpoints/{timestamp}.md` with **What/Why/Next**.
3. Update `/PROJECT_SNAPSHOT.md` (rolling, ≤ 200 lines).

---

## 2) Optional Management‑Layer Subagents (use sparingly)

- **Planner** — turns high‑level goals into concrete steps. Trigger: new feature/epic or messy request. Output: milestone list; dependencies; acceptance criteria.  
- **Critic** — adversarial review of a plan or PR before execution. Trigger: risky changes, security-impacting diffs, or integration with money/credentials. Output: 10‑point risk list + fixes.  
- **Alignment** — checks plan against Rob’s preferences (sequential, modular, documented). Trigger: plan generated. Output: amended plan or short deltas.  
- **Negotiator** — reconcile conflicting constraints (time vs. quality). Trigger: explicit conflicts. Output: 2–3 trade‑off options + recommendation.

> Default posture: **don’t** invoke these unless a trigger is clearly met or complexity is high.

---

## 3) Auto‑Go/No‑Go Heuristics

**Go (auto‑invoke subagents) if:**  
- Integration or change spans multiple modules/files **and** unknown library/API involved.  
- There’s evidence of drift (docs outdated, failing tests, ambiguous ownership).  
- Upcoming work is “one‑way door” (hard to undo).

**No‑Go (proceed directly) if:**  
- Single‑file change, small and reversible.  
- You already have up‑to‑date local examples/tests for the exact change.  
- You can complete safely with <30 lines and no external dependency changes.

---

## 4) Minimal Orchestration Protocol

1. **Triage:** classify request → {tiny | standard | complex}.  
2. **Decide:** apply triggers → pick subagents (0–2 max).  
3. **Execute:** each subagent writes a concise artifact into `/.history/...`.  
4. **Plan:** combine artifacts → produce a short execution plan (≤ 25 lines).  
5. **Act:** ship the change.  
6. **Checkpoint:** Historian snapshot if thresholds met.  
7. **Log:** append a one‑liner to `/.history/decisions.log` (who/why/where).

> Keep artifacts short, linkable, and LLM‑readable. Prefer bullets over prose.

---

## 5) Lightweight Config (YAML)

Create `/config/subagents.yml` (or similar). Claude should create if missing.

```yaml
defaults:
  max_parallel_research: 4
  historian_snapshot_loc_threshold: 150
  ask_before_overwrite: true
  doc_domains_priority: ["official", "github", "trusted-blogs"]

triggers:
  explorer:
    files_threshold: 2
    loc_threshold: 150
  research_documenter:
    require_for_external_api: true
    require_for_major_version_bump: true
  historian:
    on_end_of_block: true
    on_prd_change: true

preferences:
  planning_style: "sequential-modular"
  documentation_level: "brief-but-consistent"
  tone: "blunt, data-driven, minimal"
```

Claude should **read and honor** this config when deciding to invoke subagents.

---

## 6) Prompts Claude Should Use Internally (short forms)

**Explorer prompt (internal):**  
“Map only the files/symbols needed for `<task>`. Output paths + symbol names + 1‑line notes. Keep under 200 lines total.”

**Research Documenter prompt (internal):**  
“Parallel-scan official docs/issues for `<lib/API>`. Produce capabilities, constraints, minimal example, pitfalls, and a 5‑step plan with citations. ≤ 120 lines.”

**Historian prompt (internal):**  
“Snapshot what changed and why. Summarize key files (paths + 10‑line notes), decisions, and next steps. Update PROJECT_SNAPSHOT.md.”

**Critic prompt (internal, optional):**  
“Adversarial review of plan/diff. List top 10 risks, likely failure modes, and fixes. ≤ 80 lines.”

---

## 7) File Conventions (Claude should create/maintain)

```
/.history/
  decisions.log                # one-line entries: [timestamp] [agent] [why] [link]
  explorer/*.md                # targeted code maps for tasks
  research/*.md                # integration briefs with citations
  checkpoints/*.md             # historian snapshots

/PROJECT_SNAPSHOT.md           # rolling 200-line snapshot for LLM recall
/.cursor/subagents.yml         # lightweight config (above)
```

---

## 8) Safety & Cost Guardrails
- Cap parallel web queries at `max_parallel_research`.  
- Prefer official docs; avoid low‑quality sources.  
- If tokens > 12k planned for a single reasoning pass, **summarize** and continue.  
- Red‑flag secrets in snapshots; never print .env values.

---

## 9) Success Criteria (how you judge yourself)
- Fewer “where is X?” lookups in main prompts (Explorer doing its job).  
- Integrations ship with fewer regressions (Research Documenter paying off).  
- Project continuity improves across days (Historian snapshots consulted).  
- Total artifact volume stays lean (signal > noise).

---

## 10) Kickoff Instruction to Claude (paste into first message)
> Load `/.cursor/subagents.yml` if present. If not, create it with sensible defaults.  
> Create the `/.history/` structure.  
> From now on, **apply these rules automatically** when creating projects or executing complex tasks.  
> Document each subagent invocation with a one‑liner in `/.history/decisions.log` and a short artifact.  
> Keep everything minimal and LLM‑readable.
