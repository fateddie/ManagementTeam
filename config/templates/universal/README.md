# Universal Project Template

**Version:** 1.0
**Purpose:** Standardized starter pack for new projects with built-in best practices

This directory contains universal templates for starting new projects with:
- ✅ Centralized credential management
- ✅ Transparent system principles
- ✅ AI assistant guidelines
- ✅ Security best practices
- ✅ Validation scripts

---

## 📦 What's Included

### Core Files

| File | Purpose |
|------|---------|
| `env_manager_template.py` | Centralized credential management pattern |
| `.env.example` | Environment variables template |
| `.gitignore` | Security-focused git ignore rules |
| `PRINCIPLES.md` | System design principles (transparency, auditability) |
| `CLAUDE.md` | AI assistant implementation guidelines |
| `validate_env.py` | Environment validation script |
| `README.md` | This file |

---

## 🚀 Quick Start - New Project

### Option 1: Automated Setup (Recommended)

```bash
# From ManagementTeam root
./scripts/create_new_project.sh my-new-project
```

This creates a new project with all templates automatically configured.

### Option 2: Manual Setup

```bash
# 1. Create project structure
mkdir -p my-project/{config,docs,src,tests,scripts}

# 2. Copy universal templates
cp config/templates/universal/env_manager_template.py my-project/config/env_manager.py
cp config/templates/universal/.env.example my-project/config/.env.example
cp config/templates/universal/.gitignore my-project/.gitignore
cp config/templates/universal/PRINCIPLES.md my-project/docs/
cp config/templates/universal/CLAUDE.md my-project/docs/
cp config/templates/universal/validate_env.py my-project/scripts/

# 3. Customize env_manager.py
# Edit my-project/config/env_manager.py:
#   - Update Config dataclass with your project-specific credentials
#   - Update get_config() to load your credentials
#   - Update validate() with your validation logic

# 4. Create .env file
cd my-project
cp config/.env.example config/.env
nano config/.env  # Add your credentials

# 5. Validate setup
python scripts/validate_env.py

# 6. Initialize git
git init
git add .
git commit -m "Initial commit from universal template"
```

---

## 🔧 Customization Guide

### 1. Customize `env_manager.py`

Edit the `Config` dataclass to match your project's needs:

```python
@dataclass
class Config:
    # Keep universal fields
    project_name: str
    environment: str
    debug: bool
    project_root: str

    # ADD your project-specific credentials
    stripe_api_key: Optional[str] = None
    sendgrid_api_key: Optional[str] = None
    custom_api_key: Optional[str] = None

    # REMOVE credentials you don't need
    # (e.g., comment out supabase if using Firebase)
```

Update `get_config()` to load your credentials:

```python
def get_config() -> Config:
    config = Config(
        # ... existing fields ...

        # ADD your credentials
        stripe_api_key=os.getenv("STRIPE_API_KEY"),
        sendgrid_api_key=os.getenv("SENDGRID_API_KEY"),
    )
    return config
```

### 2. Customize `.env.example`

Add your project-specific environment variables:

```bash
# Add to config/.env.example:

# Stripe Payment Processing
STRIPE_API_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here

# SendGrid Email
SENDGRID_API_KEY=SG.your_key_here
```

### 3. Customize `validate_env.py`

Update validation checks for your project:

```python
# Add your API keys to validation
api_keys = [
    ("OpenAI", config.openai_api_key),
    ("Stripe", config.stripe_api_key),
    ("SendGrid", config.sendgrid_api_key),
]
```

### 4. Review `PRINCIPLES.md` and `CLAUDE.md`

These files are already universal and follow best practices:
- `PRINCIPLES.md` - System design principles (transparency, human-in-loop, auditability)
- `CLAUDE.md` - AI assistant implementation guidelines

**No changes needed** unless you have project-specific rules to add.

---

## 📋 Template Philosophy

### Why Centralized Credentials?

**Problem:**
```python
# ❌ BAD - Scattered throughout codebase
import os
api_key = os.getenv("API_KEY")  # Repeated 50 times
```

**Solution:**
```python
# ✅ GOOD - Single source of truth
from config.env_manager import get_config
config = get_config()
api_key = config.api_key  # Type-safe, validated, one place
```

**Benefits:**
- ✅ Single location for all credentials
- ✅ Type-safe access (autocomplete in IDE)
- ✅ Automatic validation on startup
- ✅ Easy to mock for testing
- ✅ Fail fast with helpful errors

### Why PRINCIPLES.md and CLAUDE.md?

**Purpose:** Ensure consistent system behavior across all projects

**PRINCIPLES.md** defines:
- Transparency (every insight traces to source data)
- Human-in-the-loop (no automated decisions)
- Auditability (full audit trails)
- Configurability (no hard-coded values)

**CLAUDE.md** teaches AI assistants:
- How to implement transparent systems
- Code patterns to follow
- Anti-patterns to avoid
- Testing requirements

**Result:** Every project built with these principles has:
- Verifiable insights
- User control over decisions
- Reproducible results
- Consistent code quality

---

## 🔒 Security Best Practices

### What's Protected

| Protected | How |
|-----------|-----|
| API Keys | `config/.env` in `.gitignore` |
| Credentials | Never hardcoded in code |
| Secrets | `.key`, `.pem` files ignored |
| Test Data | Validation on startup |

### Security Checklist

- [x] `.env` files ignored by git
- [x] Credentials loaded via env_manager
- [x] No hardcoded secrets in code
- [x] Validation on startup
- [x] Type-safe access patterns
- [x] Optional credentials handled gracefully

---

## 🎯 Use Cases

### Use Case 1: AI Research Tool

**Credentials needed:**
- OpenAI API
- Anthropic API
- Perplexity API

**Customization:**
1. Copy `env_manager_template.py` → `config/env_manager.py`
2. Keep AI API key fields, remove database/backend fields
3. Update `.env.example` with just AI keys
4. Done!

### Use Case 2: Full-Stack Web App

**Credentials needed:**
- Supabase (backend)
- Stripe (payments)
- SendGrid (email)

**Customization:**
1. Copy `env_manager_template.py` → `config/env_manager.py`
2. Keep Supabase fields, add Stripe and SendGrid
3. Remove AI API keys (or keep if using AI features)
4. Update `.env.example` with all services
5. Done!

### Use Case 3: Data Pipeline

**Credentials needed:**
- Database (PostgreSQL)
- Redis (caching)
- AWS S3 (storage)

**Customization:**
1. Copy `env_manager_template.py` → `config/env_manager.py`
2. Keep database and Redis fields
3. Add AWS credentials to Config dataclass
4. Update `.env.example` with AWS keys
5. Done!

---

## 📚 Additional Resources

- **Full Setup Guide:** `/docs/setup/PROJECT_SETUP_TEMPLATE.md`
- **API Keys Guide:** `/docs/setup/API_KEYS_SETUP_GUIDE.md`
- **System Principles:** `/docs/PRINCIPLES.md`
- **Claude Guidelines:** `/docs/CLAUDE.md`

---

## 🤝 Contributing

Found an improvement to the universal templates?

1. Update the template files in `config/templates/universal/`
2. Test with a new project
3. Document changes in this README
4. Commit with descriptive message

---

## 📝 Version History

- **v1.0** (2025-01-06): Initial universal template system
  - Centralized credential management
  - Security best practices
  - System principles documentation
  - AI assistant guidelines

---

**Remember:** These templates are **starting points**. Customize them for your project's specific needs while maintaining the core principles of transparency, security, and maintainability.
