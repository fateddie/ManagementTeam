# ✅ New Project Setup Checklist

Use this checklist when starting a new Python project with this setup system.

---

## 📋 Initial Setup

### Step 1: Copy Setup Files

```bash
# Set your new project path
NEW_PROJECT="/path/to/new-project"

# Create directory if needed
mkdir -p $NEW_PROJECT

# Copy core setup files
cp setup/setup_project_complete.sh $NEW_PROJECT/setup/
cp pyproject.toml $NEW_PROJECT/
cp pytest.ini $NEW_PROJECT/
cp .editorconfig $NEW_PROJECT/
cp .pre-commit-config.yaml $NEW_PROJECT/
cp requirements-dev.txt $NEW_PROJECT/

# Copy configuration files
mkdir -p $NEW_PROJECT/config
cp config/env_manager.py $NEW_PROJECT/config/
cp config/.env.example $NEW_PROJECT/config/

# Copy .gitignore
cp .gitignore $NEW_PROJECT/
```

**Checklist:**
- [ ] Copied `setup/setup_project_complete.sh`
- [ ] Copied `pyproject.toml`
- [ ] Copied `pytest.ini`
- [ ] Copied `.editorconfig`
- [ ] Copied `.pre-commit-config.yaml`
- [ ] Copied `requirements-dev.txt`
- [ ] Copied `config/env_manager.py`
- [ ] Copied `config/.env.example`
- [ ] Copied `.gitignore`

---

### Step 2: Customize for Your Project

#### Edit `pyproject.toml`

```toml
[project]
name = "your-project-name"  # ← Change this
version = "0.1.0"           # ← Start at 0.1.0
description = "Your project description"  # ← Change this
authors = [
    {name = "Your Name", email = "your-email@example.com"},  # ← Change this
]
```

**Checklist:**
- [ ] Updated project name
- [ ] Updated project description
- [ ] Updated author information
- [ ] Updated version to 0.1.0

---

#### Create `requirements.txt`

```bash
# Create your requirements.txt with project dependencies
cat > $NEW_PROJECT/requirements.txt <<'EOF'
# Core dependencies
requests
python-dotenv

# Add your project-specific dependencies here
EOF
```

**Checklist:**
- [ ] Created `requirements.txt`
- [ ] Added project-specific dependencies

---

#### Customize `config/.env.example`

```bash
# Edit config/.env.example for your project's needs
# Add your specific API keys and configuration
```

**Checklist:**
- [ ] Updated `.env.example` with project-specific variables
- [ ] Documented all required vs. optional variables

---

### Step 3: Run Setup

```bash
cd $NEW_PROJECT
chmod +x setup/setup_project_complete.sh
./setup/setup_project_complete.sh
```

**Checklist:**
- [ ] Ran setup script successfully
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Pre-commit hooks installed

---

### Step 4: Configure Environment

```bash
# Copy .env.example to .env
cp config/.env.example config/.env

# Edit with your API keys
nano config/.env

# Test configuration
source venv/bin/activate
python -m config.env_manager
```

**Checklist:**
- [ ] Created `config/.env` from example
- [ ] Added required API keys
- [ ] Validated configuration successfully

---

## 🏗️ Project Structure Setup

### Step 5: Create Standard Directories

```bash
mkdir -p src tests docs scripts
mkdir -p logs data outputs
```

**Checklist:**
- [ ] Created `src/` for main code
- [ ] Created `tests/` for test files
- [ ] Created `docs/` for documentation
- [ ] Created `scripts/` for utility scripts
- [ ] Created `logs/`, `data/`, `outputs/` as needed

---

### Step 6: Create Initial Files

#### Create `README.md`

```markdown
# Project Name

Brief description of your project.

## Setup

\`\`\`bash
./setup/setup_project_complete.sh
source venv/bin/activate
\`\`\`

## Usage

\`\`\`bash
python src/main.py
\`\`\`

## Testing

\`\`\`bash
pytest
\`\`\`
```

#### Create `src/__init__.py`

```python
"""Your project name."""

__version__ = "0.1.0"
```

#### Create `tests/conftest.py`

```python
"""Pytest configuration and shared fixtures."""

import pytest

@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    from config.env_manager import Config
    return Config(
        project_name="test",
        environment="development",
        debug=True,
        management_team_root="/tmp"
    )
```

**Checklist:**
- [ ] Created `README.md`
- [ ] Created `src/__init__.py`
- [ ] Created `tests/conftest.py`

---

## 🧪 Testing Setup

### Step 7: Create Sample Tests

#### Create `tests/test_config.py`

```python
"""Test configuration management."""

import pytest
from config.env_manager import get_config, Config


def test_config_loads():
    """Test that config loads without errors."""
    config = get_config()
    assert config.project_name is not None


def test_config_validation():
    """Test config validation."""
    config = Config(
        project_name="test",
        environment="development",
        debug=True,
        management_team_root="/tmp"
    )
    errors = config.validate()
    # Should have warnings but no critical errors
    assert all("required" not in e.lower() for e in errors)
```

#### Run Tests

```bash
pytest
```

**Checklist:**
- [ ] Created sample test file
- [ ] Tests pass successfully
- [ ] Coverage report generated

---

## 🔧 Git Setup

### Step 8: Initialize Git Repository

```bash
cd $NEW_PROJECT

# Initialize git
git init

# Create initial commit
git add .
git commit -m "chore: initial project setup"

# Add remote (if using GitHub/GitLab)
git remote add origin https://github.com/username/repo.git
git push -u origin main
```

**Checklist:**
- [ ] Initialized git repository
- [ ] Created initial commit
- [ ] Added remote repository (if applicable)
- [ ] Pushed to remote

---

### Step 9: GitHub Actions (Optional)

If using GitHub, create `.github/workflows/ci.yml`:

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: black --check .
      - run: ruff check .
      - run: pytest --cov
```

**Checklist:**
- [ ] Created GitHub Actions workflow
- [ ] Added required secrets to GitHub
- [ ] Verified CI/CD runs successfully

---

## 📚 Documentation

### Step 10: Add Essential Documentation

Create these files:

1. **`LICENSE`** - Choose license (MIT, Apache, etc.)
2. **`CONTRIBUTING.md`** - Contribution guidelines
3. **`CHANGELOG.md`** - Track version changes
4. **`.github/PULL_REQUEST_TEMPLATE.md`** - PR template

**Checklist:**
- [ ] Added LICENSE file
- [ ] Created CONTRIBUTING.md
- [ ] Created CHANGELOG.md
- [ ] Added PR template (if using GitHub)

---

## ✅ Final Verification

### Step 11: Verify Everything Works

```bash
# Activate environment
source venv/bin/activate

# Verify configuration
python -m config.env_manager

# Run tests
pytest --cov

# Check code quality
black --check .
ruff check .

# Run pre-commit on all files
pre-commit run --all-files

# Try making a commit
git add .
git commit -m "test: verify setup"  # Pre-commit should run
```

**Checklist:**
- [ ] Configuration loads successfully
- [ ] All tests pass
- [ ] Black formatting passes
- [ ] Ruff linting passes
- [ ] Pre-commit hooks run on commit
- [ ] No errors or warnings

---

## 🎉 Setup Complete!

Your new project is ready with:

✅ Professional development environment
✅ Automated code quality checks
✅ Testing framework with coverage
✅ Type-safe configuration management
✅ CI/CD pipeline (if using GitHub)
✅ Comprehensive documentation

---

## 📋 Quick Reference

### Daily Development Commands

```bash
# Activate environment
source venv/bin/activate

# Format code
black .

# Lint code
ruff check --fix .

# Run tests
pytest --cov

# Commit (pre-commit runs automatically)
git commit -m "feat: your feature"
```

---

## 🔄 For Your Next Project

1. Copy the setup files again from this project
2. Follow this checklist
3. Customize for your new project's needs
4. Start coding with confidence!

---

**Template Version:** 2.0
**Last Updated:** 2025-10-17
