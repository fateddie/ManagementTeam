# Cursor AI Rules for AI Management Layer System

## Project Context
This is the **AI Management Layer System** - a modular AI agent framework that plans, documents, and coordinates AI projects from ideation to execution.

## Core Principles
1. **Modularity First** - All agents are independent, interchangeable modules
2. **Documentation Driven** - Every component must be documented before implementation
3. **Memory Persistence** - All decisions and context must be stored for continuity
4. **Human-in-Loop** - Critical decisions require human approval
5. **Scalability** - Design for growth from day one

## File Structure Rules
- All agents go in `/src/agents/`
- All utilities go in `/src/utils/`
- All configs go in `/config/`
- All documentation goes in `/docs/system/`
- Each scaffolded project goes in `/projects/`

## Coding Standards
- **Language**: Python 3.8+
- **Style**: PEP 8 compliant
- **Type Hints**: Required for all functions
- **Docstrings**: Required for all classes and functions (Google style)
- **Error Handling**: Comprehensive try-except blocks with logging
- **Testing**: Unit tests required for all new functionality

## Agent Development Rules
1. Each agent must inherit from a base `Agent` class (when created)
2. Each agent must implement:
   - `execute()` method
   - `validate_input()` method
   - `log_action()` method
3. Each agent must use the centralized memory system
4. Each agent must write to structured logs

## Documentation Requirements
- Every new agent needs a specification document in `/docs/system/`
- Every significant change requires a TDR (Technical Decision Record)
- Every project phase requires a progress update

### **⚠️ CRITICAL: Documentation Alignment Rule**
**Before any Git commit, ensure ALL documentation is updated and aligned:**

1. **Update Version Numbers**
   - README.md (version, date, phase count)
   - FINAL_SYSTEM_STATUS.md (agent count, phase list)
   - QUICK_START.md (new features, commands)
   
2. **Update Agent Lists**
   - README.md (agent count and names)
   - FINAL_SYSTEM_STATUS.md (agent table)
   - PROJECT_INDEX.md (if new docs added)
   - agents/orchestrator/agent_registry.yaml (new agents)
   
3. **Create Phase Summary**
   - outputs/PHASE_X_SUMMARY.md for new phases
   - Include: objectives, deliverables, tests, success criteria
   
4. **Update Navigation**
   - PROJECT_INDEX.md (add new docs)
   - QUICK_START.md (add new commands)
   - DOCUMENTATION_STATUS.md (audit status)

**✅ Checklist Before Commit:**
- [ ] All agent counts updated (6 → 7 → 8, etc.)
- [ ] All phase counts updated (9 → 11 → 13, etc.)
- [ ] All version numbers incremented
- [ ] All dates updated to current
- [ ] New features added to QUICK_START.md
- [ ] New agents added to README.md
- [ ] Navigation updated in PROJECT_INDEX.md
- [ ] Phase summary created (if new phase)

**Why This Matters:**
- Prevents documentation drift
- Ensures all docs tell the same story
- Makes onboarding easier
- Maintains professional quality
- Avoids confusion for users

## Memory System Rules
- Use Mem0 for phase 1 (first 6 months)
- Design all memory interfaces to be database-agnostic
- Plan for Neo4j migration in phase 2
- Never hard-code memory storage logic in agents

## Deployment Considerations
- All code must work on Vercel (if web components)
- All code must be cloud-agnostic
- Environment variables for all secrets
- Rate limiting on all exposed endpoints

## Testing Requirements
- Unit tests in `/tests/`
- Integration tests for agent workflows
- Mock external API calls
- Minimum 80% code coverage target

## Security Requirements
- No hardcoded credentials
- Input validation on all user inputs
- Sanitize all file paths
- Rate limiting on API endpoints
- Audit logging for all critical operations

