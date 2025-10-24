# ManagementTeam - Python Setup Guide

**Project:** ManagementTeam (Multi-Agent System)  
**Version:** 1.0  
**Last Updated:** October 19, 2025

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.11+ ([Download](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **Git** for version control
- **Redis** (optional - for caching/memory)

### Setup Steps

1. **Clone the repository** (if not already done)
   ```bash
   cd ~/Documents/ClaudeCode/ManagementTeam
   ```

2. **Run the automated setup script**
   ```bash
   ./setup/setup_project_complete.sh
   ```
   
   This script will:
   - ✅ Create Python virtual environment
   - ✅ Install all dependencies
   - ✅ Set up Black + Ruff formatters
   - ✅ Configure pre-commit hooks
   - ✅ Validate environment variables

3. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

4. **Configure environment variables**
   ```bash
   cp config/.env.example config/.env
   # Edit config/.env with your actual API keys
   ```

5. **Validate configuration**
   ```bash
   python -m config.env_manager
   ```

6. **Run tests**
   ```bash
   pytest tests/
   ```

---

## 🎯 Tech Stack

This project uses the following technologies:

### Backend
- **Python 3.11+** - Modern Python with type hints
- **FastAPI** (if API) - Fast, async web framework
- **Pydantic** - Data validation
- **Redis** - Caching and memory storage

### AI/ML
- **OpenAI API** - GPT models for agents
- **Anthropic API** - Claude models
- **Perplexity API** - Research capabilities

### Data & Storage
- **PostgreSQL** - Primary database (if used)
- **Supabase** - Backend as a service (if used)

### Development Tools
- **Black** - Code formatting
- **Ruff** - Fast linting
- **pytest** - Testing framework
- **pre-commit** - Git hooks for quality
- **mypy** - Type checking (optional)

---

## 📋 Python Coding Standards

### Code Formatting

**Black Configuration:**
```toml
[tool.black]
line-length = 100
target-version = ['py311']
```

**Run Black:**
```bash
black .
```

**Ruff Configuration:**
```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W", "C90", "B", "UP"]
ignore = ["E501"]
```

**Run Ruff:**
```bash
ruff check .
ruff check --fix .  # Auto-fix issues
```

### Naming Conventions

| Item | Convention | Example |
|------|------------|---------|
| Modules | snake_case | `strategy_agent.py` |
| Classes | PascalCase | `StrategyAgent` |
| Functions | snake_case | `process_task()` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRIES` |
| Private | _leading_underscore | `_internal_method()` |

### File Structure

```
ManagementTeam/
├── agents/              # AI agent modules
│   ├── strategy_agent/
│   ├── research_agent/
│   └── coding_agent/
├── core/                # Core system modules
│   ├── base_agent.py
│   ├── workflow_state.py
│   └── cache.py
├── config/              # Configuration
│   ├── env_manager.py
│   ├── .env
│   └── .env.example
├── tests/               # Test files
│   ├── test_agents.py
│   └── conftest.py
├── docs/                # Documentation
├── scripts/             # Utility scripts
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Development dependencies
└── pyproject.toml       # Project configuration
```

---

## 🛠️ Development Workflow

### Daily Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run your code
python your_script.py

# Format code
black .

# Lint code
ruff check .

# Run tests
pytest tests/
```

### Before Committing

```bash
# Pre-commit runs automatically, but you can run manually:
pre-commit run --all-files

# Or run individual checks:
black --check .
ruff check .
pytest tests/
```

### Adding Dependencies

```bash
# Add to requirements.txt
echo "new-package>=1.0.0" >> requirements.txt

# Install
pip install -r requirements.txt

# Or install directly
pip install new-package
pip freeze > requirements.txt  # Update requirements
```

---

## 🔐 Environment Variables

### Required Variables

Create `config/.env` with these values:

```bash
# Project Settings
PROJECT_NAME=ManagementTeam
ENVIRONMENT=development
DEBUG=true

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...

# Database (if used)
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# Redis (for caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Supabase (if used)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

### Validation

The `config/env_manager.py` automatically validates all required variables:

```python
from config.env_manager import get_config

config = get_config()
print(f"Project: {config.project_name}")
print(f"Environment: {config.environment}")
```

---

## 📦 Key Python Patterns

### Module Pattern
```python
"""
Module: strategy_agent.py
Purpose: [description]
Location: /agents/strategy_agent/
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


class StrategyInput(BaseModel):
    """Input model for strategy generation."""
    goal: str
    constraints: Optional[List[str]] = None


class StrategyAgent:
    """
    Strategy Agent
    
    Purpose: Generate strategic plans based on goals
    
    Methods:
        generate_strategy: Create strategic plan
        evaluate_options: Assess different approaches
    """
    
    def __init__(self, config):
        self.config = config
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AI client (private method)."""
        pass
    
    def generate_strategy(self, input_data: StrategyInput) -> Dict:
        """
        Generate strategic plan.
        
        Args:
            input_data: Strategy input with goals and constraints
            
        Returns:
            Dictionary with strategy details
            
        Raises:
            ValueError: If input is invalid
        """
        try:
            # Implementation
            return {"strategy": "..."}
        except Exception as error:
            print(f"[ERROR] Strategy generation failed: {error}")
            raise
```

### Error Handling Pattern
```python
import logging

logger = logging.getLogger(__name__)


def process_task(task_id: str) -> Dict:
    """
    Process a task with comprehensive error handling.
    
    Args:
        task_id: Unique task identifier
        
    Returns:
        Processing results
    """
    logger.info(f"[process_task] Starting: {task_id}")
    
    try:
        # Validate input
        if not task_id:
            raise ValueError("task_id is required")
        
        # Process
        result = _perform_processing(task_id)
        
        logger.info(f"[process_task] Complete: {task_id}")
        return {"success": True, "data": result}
        
    except ValueError as error:
        logger.error(f"[process_task] Validation error: {error}")
        return {"success": False, "error": str(error)}
        
    except Exception as error:
        logger.exception(f"[process_task] Unexpected error: {error}")
        return {"success": False, "error": "Processing failed"}
```

### Configuration Pattern
```python
# Use centralized config
from config.env_manager import get_config

class MyAgent:
    def __init__(self):
        config = get_config()
        
        if not config.openai_api_key:
            raise ValueError("OpenAI API key required")
        
        self.api_key = config.openai_api_key
        self.debug = config.debug
```

---

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_agents.py

# Specific test
pytest tests/test_agents.py::test_strategy_agent

# With coverage
pytest --cov=. --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Test Structure

```python
# tests/test_agents.py
import pytest
from agents.strategy_agent import StrategyAgent


@pytest.fixture
def strategy_agent():
    """Fixture for strategy agent."""
    return StrategyAgent(test_config)


def test_strategy_generation(strategy_agent):
    """Test strategy generation."""
    result = strategy_agent.generate_strategy({"goal": "test"})
    assert result["success"] is True
    assert "strategy" in result


def test_invalid_input(strategy_agent):
    """Test error handling with invalid input."""
    with pytest.raises(ValueError):
        strategy_agent.generate_strategy({})
```

---

## 🐍 Python Best Practices

### Type Hints

```python
from typing import Dict, List, Optional, Union


def process_data(
    items: List[str],
    options: Optional[Dict[str, any]] = None
) -> Union[Dict, None]:
    """Always use type hints for clarity."""
    pass
```

### Docstrings

```python
def calculate_score(data: Dict) -> float:
    """
    Calculate weighted score from input data.
    
    Args:
        data: Dictionary with 'reach', 'impact', 'confidence', 'effort'
        
    Returns:
        Weighted score between 0-100
        
    Raises:
        ValueError: If required keys missing
        
    Example:
        >>> calculate_score({'reach': 8, 'impact': 7, 'confidence': 0.9})
        75.5
    """
    pass
```

### Error Messages

```python
# ✅ GOOD: Descriptive error messages
if not data.get("title"):
    raise ValueError(
        "Title is required. Received data: "
        f"{list(data.keys())}"
    )

# ❌ BAD: Vague errors
if not data.get("title"):
    raise ValueError("Invalid input")
```

---

## 🔍 Code Quality Checklist

Before committing code, verify:

- [ ] Code formatted with Black (`black .`)
- [ ] No linting errors (`ruff check .`)
- [ ] All tests pass (`pytest`)
- [ ] Type hints added to public functions
- [ ] Docstrings present for classes and public methods
- [ ] Error handling implemented
- [ ] Logging added for important operations
- [ ] No hardcoded credentials
- [ ] Configuration uses `env_manager`
- [ ] New dependencies added to `requirements.txt`

---

## 🚢 Deployment

### Building for Production

```bash
# Install production dependencies only
pip install -r requirements.txt

# Run with production settings
export ENVIRONMENT=production
export DEBUG=false
python main.py
```

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run
CMD ["python", "main.py"]
```

---

## 🔧 Troubleshooting

### "Module not found" errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Import errors

```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Environment variable issues

```bash
# Validate configuration
python -m config.env_manager

# Check .env file exists
ls -la config/.env
```

---

## 📚 Additional Resources

### Python Documentation
- [Python 3.11 Docs](https://docs.python.org/3.11/)
- [Type Hints Guide](https://docs.python.org/3/library/typing.html)
- [Pydantic](https://docs.pydantic.dev/)

### Tools
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)
- [pre-commit](https://pre-commit.com/)

### Project Documentation
- `docs/RULES_DATABASE.md` - Universal coding standards
- `docs/IMPLEMENTATION_GUIDE.md` - Setup guide
- `docs/setup/PROJECT_SETUP_TEMPLATE.md` - Universal patterns

---

## ✅ Setup Checklist

Use this checklist to verify your setup:

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] config/.env configured with API keys
- [ ] Black and Ruff installed
- [ ] Pre-commit hooks installed
- [ ] Tests run successfully
- [ ] Configuration validated
- [ ] All imports work correctly

---

**Last Updated:** October 19, 2025  
**Maintainer:** Robert Freyne  
**Status:** ✅ Production Ready

---

**Remember:** Follow the universal rules in `RULES_DATABASE.md` for consistent, high-quality Python code that works seamlessly with AI assistants!

