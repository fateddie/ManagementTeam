# ⚡ Quick Reference Card

**AI Management Team - Development Commands**

---

## 🚀 Setup (One-Time)

```bash
# Complete project setup
./setup/setup_project_complete.sh

# Activate environment
source venv/bin/activate

# Install dev tools
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install
```

---

## 🛠️ Daily Development

```bash
# Activate environment (do this first!)
source venv/bin/activate

# Validate configuration
python -m config.env_manager
```

---

## 🎨 Code Quality

```bash
# Format code (auto-fix)
black .

# Lint code
ruff check .

# Lint with auto-fix
ruff check --fix .

# Run all quality checks
pre-commit run --all-files
```

---
1
## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test
pytest tests/test_example.py

# Run fast tests only
pytest -m "not slow"

# Generate HTML coverage report
pytest --cov --cov-report=html
open htmlcov/index.html
```

---

## 🔧 Configuration

```bash
# Test config manager
python -m config.env_manager

# Validate environment
python scripts/validate_environment.py

# Edit API keys
nano config/.env
```

---

## 📦 Dependencies

```bash
# Install production deps
pip install -r requirements.txt

# Install dev deps
pip install -r requirements-dev.txt

# Add new dependency
pip install package-name
pip freeze > requirements.txt

# Update all dependencies
pip install --upgrade -r requirements.txt
```

---

## 🌳 Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Stage changes
git add .

# Commit (pre-commit runs automatically)
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/my-feature
```

---

## 🐛 Troubleshooting

```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Update pre-commit hooks
pre-commit autoupdate

# Clear pytest cache
rm -rf .pytest_cache

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
```

---

## 📊 Project Management

```bash
# Validate system
python cli/manage.py validate

# List agents
python cli/manage.py list

# Run full pipeline
python cli/manage.py run

# Show status
python cli/manage.py status
```

---

## 🔍 Useful Checks

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check file structure
tree -L 2 -I 'venv|__pycache__|*.pyc'

# Check git status
git status

# Check which Python is active
which python
```

---

## 📝 Commit Message Format

```
<type>(<scope>): <subject>

Examples:
feat(agents): add new research agent
fix(config): resolve env loading issue
docs: update setup guide
test: add integration tests
refactor(core): simplify base agent
chore: update dependencies
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `chore`: Maintenance

---

## 🎯 Quick Commands Cheat Sheet

| Task | Command |
|------|---------|
| Activate venv | `source venv/bin/activate` |
| Format code | `black .` |
| Lint code | `ruff check .` |
| Run tests | `pytest` |
| Test coverage | `pytest --cov` |
| Run pre-commit | `pre-commit run --all-files` |
| Validate config | `python -m config.env_manager` |
| Install deps | `pip install -r requirements.txt` |

---

## 🚨 Before Every Commit

```bash
# 1. Run quality checks
black .
ruff check --fix .

# 2. Run tests
pytest

# 3. Commit (hooks run automatically)
git add .
git commit -m "feat: your message"
```

---

## 🆘 Get Help

- Setup issues: `./setup/setup_project_complete.sh`
- Config issues: `python -m config.env_manager`
- Environment issues: `python scripts/validate_environment.py`
- Full guide: See `SETUP_GUIDE.md`
- Template reference: See `PROJECT_SETUP_TEMPLATE.md`

---

**Version:** 2.0 | **Last Updated:** 2025-10-17
