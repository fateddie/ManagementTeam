# 🚀 Project Setup Guide

**Version:** 2.0 - Production Grade
**Last Updated:** 2025-10-17

This guide provides a comprehensive, reusable setup system for Python projects with professional development tools and best practices.

---

## ✨ Features

This setup provides:

- ✅ **Python Virtual Environment** - Isolated dependencies
- ✅ **Centralized Configuration** - Type-safe environment management
- ✅ **Code Formatting** - Black & Ruff automatic formatting
- ✅ **Pre-commit Hooks** - Auto-format on every commit
- ✅ **Testing Framework** - pytest with coverage
- ✅ **CI/CD Pipeline** - GitHub Actions with quality checks
- ✅ **Documentation** - EditorConfig for consistency

---

## 🎯 Quick Start (This Project)

```bash
# Run the comprehensive setup script
./setup/setup_project_complete.sh

# Activate virtual environment
source venv/bin/activate

# Edit your API keys
nano config/.env

# Validate configuration
python -m config.env_manager

# Run tests
pytest

# Check code quality
ruff check .
black --check .
```

---

## 📋 For New Projects

To use this setup system for a new project:

### 1. Copy Setup Files

```bash
# Copy to your new project directory
cp -r setup/ /path/to/new-project/
cp pyproject.toml /path/to/new-project/
cp pytest.ini /path/to/new-project/
cp .editorconfig /path/to/new-project/
cp .pre-commit-config.yaml /path/to/new-project/
cp requirements-dev.txt /path/to/new-project/
cp config/env_manager.py /path/to/new-project/config/
cp config/.env.example /path/to/new-project/config/
cp .gitignore /path/to/new-project/
```

### 2. Run Setup

```bash
cd /path/to/new-project
./setup/setup_project_complete.sh
```

### 3. Configure Environment

```bash
# Edit config/.env with your API keys
nano config/.env

# Test configuration
python -m config.env_manager
```

### 4. Start Coding!

```bash
# Write your code
# Pre-commit hooks will auto-format on commit
git add .
git commit -m "feat: initial setup"
```

---

## 🛠️ Tools Installed

### Code Quality

| Tool | Purpose | Command |
|------|---------|---------|
| **Black** | Code formatter (opinionated) | `black .` |
| **Ruff** | Fast linter (replaces flake8, isort, etc.) | `ruff check .` |
| **Pre-commit** | Git hooks for auto-formatting | `pre-commit run --all-files` |

### Testing

| Tool | Purpose | Command |
|------|---------|---------|
| **pytest** | Testing framework | `pytest` |
| **pytest-cov** | Coverage reporting | `pytest --cov` |
| **pytest-asyncio** | Async test support | (automatic) |

### Development

| Tool | Purpose | Command |
|------|---------|---------|
| **IPython** | Enhanced Python shell | `ipython` |
| **MyPy** | Type checking (optional) | `mypy .` |

---

## 📚 Configuration Files

### `config/env_manager.py`

Centralized environment variable management with type safety.

**Usage:**
```python
from config.env_manager import get_config

config = get_config()
api_key = config.openai_api_key  # Type-safe access
```

**Benefits:**
- ✅ Single source of truth for all config
- ✅ Type-safe access (no typos)
- ✅ Automatic validation with helpful errors
- ✅ Default values for optional settings
- ✅ Easy to test (just pass Config object)

### `pyproject.toml`

Configuration for Black, Ruff, pytest, and coverage.

**Key Settings:**
- Line length: 100 characters
- Python version: 3.11+
- Comprehensive linting rules
- Test coverage tracking

### `.pre-commit-config.yaml`

Automated checks that run before every commit.

**Enabled Checks:**
- Trailing whitespace removal
- End of file fixes
- YAML/JSON syntax validation
- Ruff linting + formatting
- Security checks (Bandit)
- Large file detection

**Install:**
```bash
pre-commit install
```

**Run Manually:**
```bash
pre-commit run --all-files
```

### `.editorconfig`

Ensures consistent code style across all editors/IDEs.

**Settings:**
- UTF-8 encoding
- LF line endings
- Trailing whitespace trimming
- Python: 4 spaces
- YAML/JSON: 2 spaces

### `pytest.ini`

Testing configuration with coverage tracking.

**Features:**
- Test discovery in `tests/` directory
- Coverage for `agents/`, `core/`, `src/`
- HTML coverage reports in `htmlcov/`
- Custom markers: `@pytest.mark.slow`, `@pytest.mark.integration`

---

## 🎨 Code Quality Workflow

### Before Committing

```bash
# Format code
black .

# Fix linting issues
ruff check --fix .

# Run tests
pytest

# Or let pre-commit do it all
git commit -m "feat: new feature"  # Pre-commit hooks run automatically
```

### Manual Quality Check

```bash
# Full quality check
black --check .        # Check formatting
ruff check .           # Check linting
pytest --cov           # Run tests with coverage
mypy .                 # Type checking (optional)
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_example.py

# Run tests with specific marker
pytest -m "not slow"

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

### Test Structure

```
tests/
├── test_agents.py       # Agent tests
├── test_config.py       # Configuration tests
├── test_integration.py  # Integration tests (marked @pytest.mark.integration)
└── conftest.py          # Shared fixtures
```

### Writing Tests

```python
import pytest
from config.env_manager import Config

def test_config_validation():
    """Test that config validates required fields."""
    config = Config(
        project_name="test",
        environment="development",
        debug=True,
        management_team_root="/tmp"
    )
    errors = config.validate()
    assert len(errors) == 0

@pytest.mark.slow
def test_api_call():
    """Slow test that calls external API."""
    # Test implementation
    pass
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions

**File:** `.github/workflows/management_team.yml`

**Jobs:**
1. **build-and-test** - Full pipeline with validation
2. **code-quality** - Black, Ruff, pytest, coverage
3. **documentation-check** - Verify docs exist

**Triggers:**
- Push to `main` or `dev`
- Pull requests to `main`
- Manual trigger (workflow_dispatch)

**Secrets Required:**
```
OPENAI_API_KEY
PERPLEXITY_API_KEY
```

---

## 📖 Environment Variables

### Required Variables

```bash
PROJECT_NAME=MyProject
ENVIRONMENT=development  # development, staging, production
MANAGEMENT_TEAM_ROOT=/path/to/project
```

### Optional API Keys

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
```

### Feature Flags

```bash
ENABLE_CACHING=true
ENABLE_LOGGING=true
ENABLE_PERSISTENT_MEMORY=true
```

See `config/.env.example` for complete list.

---

## 🐛 Troubleshooting

### Virtual Environment Issues

```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Pre-commit Hook Failures

```bash
# Update hooks
pre-commit autoupdate

# Run manually to see errors
pre-commit run --all-files

# Skip hooks temporarily (not recommended)
git commit --no-verify
```

### Import Errors

```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH=/path/to/project:$PYTHONPATH

# Or add to config/.env
echo "PYTHONPATH=/path/to/project" >> config/.env
```

### Configuration Errors

```bash
# Validate environment
python -m config.env_manager

# Check if .env exists
ls -la config/.env

# Copy from example if missing
cp config/.env.example config/.env
```

---

## 🎓 Best Practices

### 1. Always Use Virtual Environment

```bash
# Activate before any Python work
source venv/bin/activate

# Verify you're in venv
which python  # Should show venv path
```

### 2. Commit Often, Push Regularly

```bash
# Pre-commit hooks ensure quality
git add .
git commit -m "feat: descriptive message"
git push
```

### 3. Write Tests for New Features

```python
# tests/test_new_feature.py
def test_new_feature():
    """Test description."""
    # Test implementation
    pass
```

### 4. Use Type Hints

```python
def process_data(data: dict) -> list[str]:
    """Process data and return results."""
    return []
```

### 5. Keep Config Centralized

```python
# ❌ Bad - scattered os.getenv()
import os
api_key = os.getenv("OPENAI_API_KEY")

# ✅ Good - centralized config
from config.env_manager import get_config
config = get_config()
api_key = config.openai_api_key
```

---

## 📦 Dependencies

### Production

See `requirements.txt` for full list.

### Development

See `requirements-dev.txt` for full list including:
- black
- ruff
- pytest, pytest-cov, pytest-asyncio
- pre-commit
- mypy
- ipython

---

## 🔗 Resources

- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [EditorConfig](https://editorconfig.org/)

---

## 📝 License

This setup system is free to use for all your projects.

---

**Maintained By:** Robert Freyne
**Version:** 2.0
**Last Updated:** 2025-10-17
