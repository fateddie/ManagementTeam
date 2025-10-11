---
title: Phase 2 - Agent Collaboration Architecture
author: Rob Freyne
date: 2025-10-11
version: 1.0
status: Design Phase
---

# 🤝 Phase 2: Agent Collaboration Architecture

## Overview

Phase 2 establishes a **multi-agent collaboration system** where specialized agents work together to provide comprehensive project planning and analysis.

---

## 🔀 Agent Collaboration Flow

```
User Input
    ↓
┌───────────────────────────────────────┐
│  Strategy Agent                       │  ← Business alignment, priorities
│  Technical Architect Agent            │  ← Technical feasibility, architecture
└───────────────────────────────────────┘
                ↓
┌───────────────────────────────────────┐
│  Planning Agent  ↔  Research Agent    │  ← Milestones, validation
└───────────────────────────────────────┘
                ↓
┌───────────────────────────────────────┐
│  Documentation Agent                  │  ← ERDs, DFDs, specs
└───────────────────────────────────────┘
                ↓
           Final Output
```

---

## 🎯 Agent Roles & Responsibilities

### 1️⃣ **Strategy Agent** (Management Layer)

**Purpose:** Business-level decision making and prioritization

**Inputs:**
- User requirements
- Business objectives
- Resource constraints

**Outputs:**
- Strategic recommendations
- Priority rankings
- Business alignment score

**Interfaces With:**
- User (direct input)
- Planning Agent (provides business context)

---

### 2️⃣ **Technical Architect Agent** (Management Layer)

**Purpose:** Technical feasibility and architecture design

**Inputs:**
- User requirements
- Technology constraints
- System requirements

**Outputs:**
- Architecture recommendations
- Technology stack suggestions
- Technical feasibility assessment

**Interfaces With:**
- User (direct input)
- Planning Agent (provides technical constraints)

---

### 3️⃣ **Planning Agent** (Coordination Layer)

**Purpose:** Convert inputs into structured plans and milestones

**Inputs:**
- Strategy Agent recommendations
- Technical Architect constraints
- User project description
- Research Agent validation

**Outputs:**
- `project_plan.yaml`
- `roadmap.md`
- `milestones.json`

**Interfaces With:**
- Strategy Agent (receives business context)
- Technical Architect (receives technical constraints)
- Research Agent (bidirectional - sends queries, receives research)
- Documentation Agent (passes plan for detailed docs)

---

### 4️⃣ **Research Agent** (Validation Layer)

**Purpose:** External validation and current best practices

**Inputs:**
- Research queries from Planning Agent
- Topics needing validation

**Outputs:**
- Research summaries
- Cited sources
- Best practice recommendations

**Interfaces With:**
- Planning Agent (bidirectional collaboration)
- Perplexity AI (external API)

**Current Implementation:**
- ✅ `src/utils/perplexity_connector.py`
- ✅ Working and tested

---

### 5️⃣ **Documentation Agent** (Output Layer)

**Purpose:** Generate comprehensive technical documentation

**Inputs:**
- Completed project plan
- Architecture from Technical Architect
- Milestones from Planning Agent

**Outputs:**
- ERD.png (Entity Relationship Diagram)
- DFD.png (Data Flow Diagram)
- tech_spec.md (Technical specifications)
- API documentation

**Interfaces With:**
- Planning Agent (receives completed plan)

---

## 🔄 Interaction Patterns

### Pattern 1: Sequential (Top-Down)

```
User → Strategy → Technical Architect → Planning → Documentation
```

**Use Case:** New project from scratch

**Flow:**
1. User describes project
2. Strategy Agent evaluates business value
3. Technical Architect assesses feasibility
4. Planning Agent creates roadmap
5. Documentation Agent generates specs

---

### Pattern 2: Collaborative (Bidirectional)

```
Planning Agent ↔ Research Agent
```

**Use Case:** Continuous validation during planning

**Flow:**
1. Planning Agent identifies knowledge gap
2. Research Agent queries Perplexity
3. Returns validated information
4. Planning Agent incorporates into plan

---

### Pattern 3: Parallel Consultation

```
      User Input
         ↓
    ┌────┴────┐
    ↓         ↓
Strategy  Technical Arch
    ↓         ↓
    └────┬────┘
         ↓
    Planning Agent
```

**Use Case:** Get both perspectives simultaneously

**Flow:**
1. User input goes to both agents
2. Strategy provides business view
3. Technical provides tech view
4. Planning Agent synthesizes both

---

## 📋 Data Flow Protocol

### Message Format (Agent-to-Agent)

```python
{
    "from_agent": "strategy_agent",
    "to_agent": "planning_agent",
    "timestamp": "2025-10-11T18:00:00Z",
    "message_type": "recommendation",
    "payload": {
        "priority": "high",
        "business_value": 8.5,
        "recommendations": ["..."]
    }
}
```

### Storage Location

```
/memory/agent_messages/
├── strategy_to_planning_20251011.json
├── technical_to_planning_20251011.json
└── planning_to_research_20251011.json
```

---

## 🎯 Phase 2 Implementation Plan

### Milestone 1: Agent Base Class (3 days)

Create common interface all agents inherit from:

```python
# src/agents/base_agent.py
class BaseAgent:
    def __init__(self, agent_name):
        self.name = agent_name
        self.context = None
        
    def receive_message(self, message: dict):
        """Receive message from another agent"""
        
    def send_message(self, to_agent: str, payload: dict):
        """Send message to another agent"""
        
    def execute(self, task: dict):
        """Execute agent-specific task"""
```

### Milestone 2: Strategy Agent (5 days)

Implement business decision logic:

```python
# src/agents/strategy_agent.py
class StrategyAgent(BaseAgent):
    def evaluate_business_value(self, project_desc):
        # Returns priority score, recommendations
        
    def assess_roi(self, project_plan):
        # Returns ROI estimate
```

### Milestone 3: Technical Architect Agent (5 days)

Implement technical feasibility assessment:

```python
# src/agents/technical_architect_agent.py  
class TechnicalArchitectAgent(BaseAgent):
    def assess_feasibility(self, requirements):
        # Returns feasibility score
        
    def recommend_architecture(self, project_type):
        # Returns tech stack
```

### Milestone 4: Agent Communication System (4 days)

Implement message passing between agents:

```python
# src/utils/agent_messenger.py
class AgentMessenger:
    def route_message(self, message: dict):
        # Routes to correct agent
        
    def broadcast(self, message: dict, agents: list):
        # Send to multiple agents
```

### Milestone 5: Integration Testing (3 days)

Test all agents working together

**Total: 20 days for Phase 2**

---

## 🔧 Configuration

### New Config File Needed:

```yaml
# config/agent_collaboration.yaml
agents:
  strategy:
    enabled: true
    priority: 1
    timeout_seconds: 30
    
  technical_architect:
    enabled: true
    priority: 1
    timeout_seconds: 30
    
  planning:
    enabled: true
    priority: 2
    uses_research: true
    
  research:
    enabled: true
    provider: "perplexity"
    
  documentation:
    enabled: false  # Phase 3
    
collaboration:
  mode: "sequential"  # or "parallel"
  require_consensus: false
  timeout_seconds: 300
```

---

## ✅ Success Criteria for Phase 2

- [ ] BaseAgent class created and tested
- [ ] Strategy Agent operational
- [ ] Technical Architect Agent operational
- [ ] Agents can communicate via messages
- [ ] Planning Agent integrated with both
- [ ] Full workflow tested end-to-end
- [ ] Phase 2 summary generated

---

## 📊 Current Status

**Phase 1:** ✅ Complete  
**Phase 2:** 📋 Designed, ready to implement  
**Dependencies:** None (Phase 1 complete)  
**Blockers:** None  

**User Approval Required:** Please review this architecture and approve Phase 2 start.

---

**Version:** 1.0  
**Status:** Design Complete  
**Next:** Awaiting approval for implementation

