# CLAUDE OPERATIONAL RULES
**Version:** 3.0
**Date:** 2025-10-18
**Maintainer:** Founder (Rob)

---

## 🧠 PURPOSE & PHILOSOPHY

**WHY These Rules Exist:**
These rules define how Claude should interpret, create, or modify files in this repository. They protect code integrity, maintain consistency, ensure traceability, and enforce modern best practices including error handling, async patterns, and tool usage.

**REASONING Behind Our Approach:**
Every technical decision in this project has a "why" - from error handling patterns to async execution to conversational workflows. We prioritize:
- **User Experience First**: Features should feel natural, not technical
- **Graceful Degradation**: System works with reduced features, never crashes
- **Educational Context**: Code and interactions explain "why", not just "what"
- **Iterative Improvement**: Soft validation guides, doesn't block
- **Transparency**: User always knows what's happening and why

**PROJECT ETHOS:**
- **Explain the "WHY"**: Every pattern, every choice has reasoning
- **User-Friendly Errors**: Guide users to solutions, not just report problems
- **Conversational Design**: Natural interactions over rigid interfaces
- **Fail Gracefully**: Optional services degrade without breaking core features
- **Document Reasoning**: Future developers understand why decisions were made

---

## ✅ PERMITTED ACTIONS

**WHY:** Clear permissions prevent accidental breaking changes while enabling productive development.

Claude may:
- Create or update `.py`, `.md`, `.yaml`, `.json` files within approved folders
  - **WHY:** Core development work without structural risk
- Generate documentation under `/docs/system/`
  - **WHY:** Knowledge capture for future developers
- Propose, but not directly implement, structural changes to `/config/` or `/setup/` scripts without approval
  - **WHY:** Configuration changes affect entire system, need review
- Refactor code for clarity or modularity if structure remains unchanged
  - **WHY:** Continuous improvement without breaking dependencies
- Automatically update `/docs/system/file_structure.md` when adding files
  - **WHY:** Keep documentation synchronized with codebase
- Use MCP tools (Playwright, Supabase) when available for enhanced functionality
  - **WHY:** Leverage external integrations when available
- Implement async/await patterns for better performance (Phase 17)
  - **WHY:** Non-blocking I/O improves throughput and user experience
- Use Redis memory system for persistent storage (Phase 16)
  - **WHY:** Cross-session data persistence without database overhead
- Design conversational, natural interactions over rigid forms
  - **WHY:** User experience should feel like talking to Claude, not filling forms

---

## 🚫 RESTRICTED ACTIONS
Claude may **not**:
- Modify or delete any `.env`, `.venv`, or environment credential file
- Alter version history or TDRs without explicit review
- Push commits without a corresponding changelog entry
- Overwrite more than one major subsystem in a single request
- Introduce new dependencies without updating `requirements.txt` **and** `TDR_index.md`
- Use bare `except:` clauses (must catch specific exception types)
- Hardcode API keys, file paths, or credentials (use `config.env_manager` instead)
- Block the event loop with synchronous I/O in async functions

---

## 🛡️ ERROR HANDLING STANDARDS

### Always Use Try/Except for External Services
All external API calls (OpenAI, Perplexity, Redis, Supabase, HTTP requests) **must** be wrapped in try/except blocks.

**Required Pattern:**
```python
try:
    result = external_api_call()
except ConnectionError as e:
    logger.warning(f"⚠️ Service unavailable: {e}")
    print("⚠️ Feature disabled (service not running)")
    return fallback_value
except TimeoutError as e:
    logger.error(f"Request timeout: {e}")
    raise ValueError(f"Service timeout after 30s: {e}")
except ValueError as e:
    logger.error(f"Invalid data: {e}")
    raise  # Re-raise if critical
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

### Graceful Degradation
System must work with reduced features if optional services are unavailable:
- **Redis down?** → Memory features disabled, pipeline continues
- **Perplexity key missing?** → Research skipped, uses fallback data
- **OpenAI rate limit?** → Retry with exponential backoff, then fail gracefully

**Example (Phase 16 Memory):**
```python
def _init_memory(self):
    """Initialize Redis memory (graceful fallback if unavailable)"""
    try:
        memory = ProjectMemory()
        logger.info("✅ Persistent memory connected")
        return memory
    except ConnectionError as e:
        logger.warning(f"⚠️ Redis unavailable: {e}")
        print("⚠️ Memory disabled (start with: ./scripts/start_redis.sh)")
        return None  # System continues without memory
```

### User-Friendly Error Messages
Never show raw stack traces to users. Provide actionable guidance:
```python
# ❌ Bad
raise Exception("Connection failed")

# ✅ Good
raise ConnectionError(
    "Cannot connect to Redis on localhost:6379.\n"
    "Start Redis: ./scripts/start_redis.sh\n"
    "Or disable memory: ENABLE_PERSISTENT_MEMORY=false"
)
```

### Logging Requirements
- **Log all errors** with context (timestamp, agent name, error type)
- **Use structured logging** for easier debugging
- **Include stack traces** only in log files, not user output

---

## 🧰 MCP TOOLS (MODEL CONTEXT PROTOCOL)

### When Available, Prefer MCP Tools

**Playwright MCP** (Browser automation):
```python
# Check availability first
if mcp_playwright_available():
    result = await playwright_mcp.navigate(url)
else:
    logger.info("Playwright MCP not available, using fallback")
```

**Supabase MCP** (Database operations):
```python
# Always gracefully degrade
try:
    data = await supabase_mcp.query("users", filters={"active": True})
except ServiceUnavailableError:
    logger.warning("Supabase MCP unavailable")
    data = load_from_cache()
```

### Tool Configuration
MCP tools configured in Claude Code settings. Check `PROJECT_SETUP_TEMPLATE.md` for integration patterns.

---

## ⚡ ASYNC/AWAIT PATTERNS (Phase 17)

### New Agents Must Support Async
All agents created after Phase 17 **must** implement `execute_async()`:

```python
class MyNewAgent(BaseAgent):
    async def execute_async(self, context: AgentContext) -> AgentOutput:
        """Non-blocking execution with async I/O"""
        # Parallel API calls
        results = await asyncio.gather(
            self._fetch_data_a(),
            self._fetch_data_b(),
            self._fetch_data_c()
        )
        return AgentOutput(...)
```

### Async Best Practices
- **Use `asyncio.gather()` for parallel I/O** (API calls, file reads, database queries)
- **Never block event loop**: Use `await asyncio.sleep(1)` not `time.sleep(1)`
- **Run sync code in thread pool**:
  ```python
  loop = asyncio.get_event_loop()
  result = await loop.run_in_executor(None, sync_function, args)
  ```
- **Handle exceptions in gather()**:
  ```python
  results = await asyncio.gather(*tasks, return_exceptions=True)
  for result in results:
      if isinstance(result, Exception):
          logger.error(f"Task failed: {result}")
  ```

### Backward Compatibility
Agents without `execute_async()` automatically run in thread pool (see `core/base_agent.py:229-231`).

---

## 🧠 PERSISTENT MEMORY SYSTEM (Phase 16)

### Use ProjectMemory for Cross-Session Data

```python
from core.project_memory import ProjectMemory

# Initialize (graceful fallback)
memory = ProjectMemory()  # Raises ConnectionError if Redis unavailable

# Store agent output
memory.store_project(
    project_id="proj_123",
    stage="StrategyAgent",
    data={"goals": [...], "confidence": 0.85},
    ttl_days=30  # Auto-expires after 30 days
)

# Retrieve history
history = memory.get_project_history("proj_123")

# Search by keyword
results = memory.search_projects_with_keyword("trading")

# Publish events (real-time tracking)
memory.publish_event("agent_completed", {
    "agent": "StrategyAgent",
    "confidence": 0.85
})
```

### Memory System Rules
- **30-day TTL**: Data auto-expires to keep memory clean
- **Check availability**: Always handle `ConnectionError` gracefully
- **Event publishing**: Publish lifecycle events (started, completed, failed)
- **Search optimization**: Use keyword search for cross-project queries

---

## 🏗️ BASE AGENT INTERFACE (Phase 1.1)

### All New Agents Inherit from BaseAgent

**Required structure:**
```python
from core.base_agent import BaseAgent, AgentContext, AgentOutput

class MyAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "MyAgent"  # Unique identifier

    @property
    def dependencies(self) -> List[str]:
        return ["StrategyAgent"]  # Runs after StrategyAgent

    def validate_inputs(self, context: AgentContext) -> bool:
        """Optional: Validate before execution"""
        return context.inputs.get("prd_path") is not None

    def execute(self, context: AgentContext) -> AgentOutput:
        """Synchronous execution (required)"""
        # Access upstream agent data
        strategy_data = context.get_agent_data("StrategyAgent")

        return AgentOutput(
            agent_name=self.name,
            decision="approve",
            reasoning="Analysis complete",
            data_for_next_agent={"results": [...]},
            confidence=0.9
        )

    async def execute_async(self, context: AgentContext) -> AgentOutput:
        """Async execution (recommended for Phase 17+)"""
        # Non-blocking I/O operations
        result = await self._async_process()
        return AgentOutput(...)
```

### AgentOutput Protocol
All agents **must** return `AgentOutput` with:
- `agent_name`: String identifier
- `decision`: "approve", "reject", "needs_info"
- `reasoning`: Human-readable explanation
- `data_for_next_agent`: Dict for downstream agents
- `confidence`: Float 0.0-1.0

---

## 📋 ENVIRONMENT MANAGEMENT

### Never Hardcode Paths or Credentials

**❌ Bad:**
```python
api_key = "sk-1234567890abcdef"  # Exposed in code
redis_host = "localhost"  # Not configurable
```

**✅ Good:**
```python
from config.env_manager import get_config

config = get_config()
api_key = config.openai_api_key  # From .env
redis_host = config.redis_host  # Configurable
```

### Config Validation
- **Fail fast**: Validate config at startup
- **Helpful errors**: Tell user exactly what's missing
- **Optional features**: Warn but continue if optional keys missing

**Example:**
```python
config = get_config()
if not config.openai_api_key:
    logger.warning("⚠️ OpenAI key not set (AI features disabled)")
if not config.project_name:
    raise ValueError("PROJECT_NAME is required in .env")
```

### Environment-Specific Configs
Use separate configs per environment:
- `.env.development` - Local development
- `.env.staging` - Staging environment
- `.env.production` - Production (never commit!)

---

## 🧪 TESTING REQUIREMENTS

### All New Agents Need Tests
Create tests in `tests/test_<agent_name>.py`:

```python
import pytest
from core.base_agent import AgentContext, AgentOutput
from agents.my_agent.my_agent import MyAgent

@pytest.fixture
def mock_context():
    return AgentContext(
        session_id="test",
        inputs={"prd_path": "test.md"},
        shared_data={}
    )

def test_agent_execution(mock_context):
    agent = MyAgent()
    result = agent.execute(mock_context)

    assert isinstance(result, AgentOutput)
    assert result.confidence > 0.5
    assert result.decision in ["approve", "reject", "needs_info"]

@pytest.mark.asyncio
async def test_agent_async_execution(mock_context):
    agent = MyAgent()
    result = await agent.execute_async(mock_context)

    assert isinstance(result, AgentOutput)
```

### Testing Standards
- **Mock external services**: No real API calls in tests
- **Use pytest fixtures**: Share test data across tests
- **Async tests**: Use `@pytest.mark.asyncio` decorator
- **Coverage goal**: 80%+ on core logic
- **Fast tests**: All tests should run in <10 seconds

---

## 🚀 CLI INTEGRATION

### Register New Agents

Add to `agents/orchestrator/agent_registry.yaml`:
```yaml
agents:
  - name: MyAgent
    path: agents.my_agent.my_agent:MyAgent
    stage: 5
    active: true
    description: "Does something useful"
```

### CLI Testing
```bash
# Test synchronous execution
python cli/manage.py run

# Test async execution (Phase 17)
python cli/manage.py run --async

# Test specific agent
PHASE_OVERRIDE=5 python agents/orchestrator/orchestrator.py
```

---

## 🔁 INTERACTION RULES
| Action | Required Step |
|--------|----------------|
| Add new module | Create `.py` file + update `file_structure.md` |
| Add new agent | Update `agent_registry.yaml` + implement `BaseAgent` + create tests |
| Update logic | Reference original doc in commit message |
| Add dependency | Modify `requirements.txt` + note in `change_log.md` |
| Major design change | Create TDR under `/docs/system/` |
| Add MCP tool | Update `PROJECT_SETUP_TEMPLATE.md` + add graceful fallback |
| Add API integration | Wrap in try/except + add to `config.env_manager` |

---

## 🧩 CLAUDE BEHAVIOUR MODES
| Mode | Description |
|------|--------------|
| **Planning Mode** | Generate structured plans, PRDs, TDRs with error handling considerations |
| **Build Mode** | Generate modular, testable code with async support and proper error handling |
| **Review Mode** | Audit changes for: error handling, async patterns, test coverage, documentation |

---

## 🧭 PROJECT CONTEXT SUMMARY
Claude operates under:
- **Architecture**: `core/base_agent.py` - BaseAgent interface (Phase 1.1)
- **Orchestration**: `agents/orchestrator/orchestrator.py` - Async/parallel execution (Phase 17)
- **Memory**: `core/project_memory.py` - Redis persistent storage (Phase 16)
- **Config**: `config/env_manager.py` - Centralized environment variables
- **Templates**: `PROJECT_SETUP_TEMPLATE.md` - Universal setup guide
- **Registry**: `agents/orchestrator/agent_registry.yaml` - Agent definitions

All actions must align with these systems and follow error handling standards.

---

## 💬 CONVERSATIONAL WORKFLOW PRINCIPLES

**WHY:** Users should interact with the system naturally, like talking to Claude, not filling rigid forms.

### Always Explain "Why"
Every prompt, question, and step should include context about why it matters:
```python
# ❌ Bad: Rigid form
"Enter target customer:"

# ✅ Good: Conversational with context
"Who is this for? Who would benefit most from this?
I'm thinking this could help: small businesses, large enterprises, or consumers.
Knowing your target customer helps me find the right communities to research."
```

### Soft Validation Over Hard Blocking
Guide users to better answers, never block them:
```python
# ❌ Bad: Hard validation
if len(answer) < 20:
    raise ValueError("Answer too short")

# ✅ Good: Soft validation with guidance
result = validate_field(config, answer)
if result['confidence'] < 0.5:
    print(f"💡 {result['suggestions'][0]}")
    print("Want to add more detail? (y/N):")
# Always allows proceeding
```

### Present Options, Allow Custom
Offer suggestions but never limit to a fixed set:
```python
print("Here are some options (or describe in your own words):")
print("  1) Small businesses")
print("  2) Large enterprises")
print("  3) Consumers")
print()
choice = input("Your choice (number or custom answer): ")
```

### Summarize Before Proceeding
Always show what was collected and get confirmation:
```python
print("📋 Here's what I understand so far:")
print(f"• Your idea: {collected['core_idea']}")
print(f"• Target: {collected['target_customer']}")
print()
print("Does this capture your idea? (y/N):")
```

### Iterative Detail Gathering
Ask follow-up questions to drill down naturally:
```python
if user_selected_business:
    print("What industry are they in?")
    industry = input("→ ")

    print("What's their role? What do they do day-to-day?")
    role = input("→ ")
```

### Research Clarification
Before auto-triggering research, explain the plan and ask for guidance:
```python
print("Based on what you've told me, here's my research plan:")
print("📍 What I'll research: ...")
print("🎯 What I'll find: ...")
print()
print("Is there anything else I should know or consider?")
additional_context = input("→ ")
```

### Auto-Save Everything
Never lose user's work:
```python
def save_field(field_name, value):
    workflow_state.save_field(field_name, value)
    print("💾 Auto-saved")
```

---

## 📖 REFERENCE DOCUMENTATION
- **Setup Guide**: `PROJECT_SETUP_TEMPLATE.md`
- **Async Testing**: `tests/test_async_orchestration.py`
- **Memory System**: `core/project_memory.py`
- **Config Management**: `config/env_manager.py` pattern (see template)
- **Conversational Workflow**: `CONVERSATIONAL_WORKFLOW_GUIDE.md`
- **Workflow Implementation**: `core/interactive_orchestrator.py`

---

## 📜 VERSION HISTORY
| Version | Date | Author | Notes |
|----------|------|---------|-------|
| 1.0 | 2025-10-08 | Founder | Initial rules definition for Claude operation |
| 2.0 | 2025-10-17 | Founder | Added error handling, MCP tools, async patterns (Phase 16-17), BaseAgent standards |
| 3.0 | 2025-10-18 | Founder | Added PURPOSE & PHILOSOPHY, conversational workflow principles, "WHY" explanations throughout |

