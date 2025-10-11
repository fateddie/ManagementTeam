# CI/CD Setup Guide - Management Team

**Phase 8: Continuous Integration & Version Control Automation**

---

## 🎯 Overview

The Management Team system includes automated CI/CD via GitHub Actions that:

- ✅ Runs validation tests on every push
- ✅ Executes full pipeline on main/dev branches
- ✅ Uploads build artifacts
- ✅ Auto-commits build summaries
- ✅ Checks code quality
- ✅ Verifies documentation

---

## 📁 Files

### GitHub Actions Workflow

```
.github/workflows/management_team.yml
```

### Key Configuration

- **Triggers:** Push to main/dev, PRs to main, manual dispatch
- **Python Version:** 3.11
- **Runners:** ubuntu-latest
- **Artifacts Retention:** 30 days

---

## 🔧 Setup Instructions

### 1. Configure GitHub Secrets

Navigate to: **Repository Settings → Secrets and variables → Actions**

Add the following secrets:

| Secret Name          | Description                     | Required   |
| -------------------- | ------------------------------- | ---------- |
| `OPENAI_API_KEY`     | OpenAI API key for agents       | Optional\* |
| `PERPLEXITY_API_KEY` | Perplexity API key for research | Optional\* |

\*Optional for validation-only runs

### 2. Enable GitHub Actions

1. Go to repository **Actions** tab
2. Click "I understand my workflows, go ahead and enable them"
3. Verify workflow appears in the list

### 3. Test the Workflow

**Option A: Push to dev branch**

```bash
git checkout -b dev
git push origin dev
```

**Option B: Manual trigger**

1. Go to **Actions** tab
2. Select "Management Team CI/CD"
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow"

---

## 🔄 CI/CD Workflow Jobs

### Job 1: build-and-test

**Steps:**

1. ✅ Checkout repository
2. ✅ Set up Python 3.11
3. ✅ Install dependencies
4. ✅ Run validation tests
5. ✅ Show system status
6. ✅ Run full pipeline (non-PR only)
7. ✅ Final validation
8. ✅ Upload artifacts
9. ✅ Generate summary
10. ✅ Auto-commit (main only)

**Triggers:**

- Push to `main` or `dev`
- Pull requests to `main`
- Manual dispatch

### Job 2: code-quality

**Steps:**

1. ✅ Checkout repository
2. ✅ Set up Python
3. ✅ Check syntax
4. ✅ Count lines of code
5. ✅ Generate statistics

### Job 3: documentation-check

**Steps:**

1. ✅ Checkout repository
2. ✅ Verify required docs
3. ✅ Generate documentation summary

---

## 📊 Workflow Behavior

### Pull Requests

- Runs validation tests only
- Does not execute full pipeline
- No auto-commit
- Artifacts uploaded for review

### Dev Branch Pushes

- Runs validation tests
- Executes full pipeline
- Uploads artifacts
- No auto-commit

### Main Branch Pushes

- Runs validation tests
- Executes full pipeline
- Uploads artifacts
- **Auto-commits build summary** (with `[skip ci]`)

---

## 📦 Artifacts

### What Gets Uploaded

```
management-team-artifacts-<run-number>/
├── outputs/
│   ├── *.yaml
│   ├── *.md
│   └── reports/
│       ├── validation_report_*.md
│       ├── build_summary_*.md
│       └── session_audit_*.json
└── logs/
    ├── orchestrator.log
    └── planner_trace.log
```

### Accessing Artifacts

1. Go to **Actions** tab
2. Click on a workflow run
3. Scroll to **Artifacts** section
4. Download `management-team-artifacts-<number>`

**Retention:** 30 days

---

## 🔒 Security & Governance

### API Keys Management

**DO:**

- ✅ Store API keys in GitHub Secrets
- ✅ Never commit keys to repository
- ✅ Use environment variables in workflow

**DON'T:**

- ❌ Hardcode API keys in code
- ❌ Commit `.env` files
- ❌ Share secrets in logs

### File Protection

The CI workflow:

- ✅ Does NOT modify `/config/`
- ✅ Does NOT modify `/docs/` (except auto-summaries)
- ✅ Only writes to `/outputs/` and `/logs/`
- ✅ Respects `.gitignore` rules

### Branch Protection (Recommended)

Set up branch protection for `main`:

1. Go to **Settings → Branches**
2. Add rule for `main`
3. Enable:
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date
   - ✅ Status checks: `build-and-test`, `code-quality`

---

## 🐛 Troubleshooting

### Workflow Fails on Validation

**Cause:** Missing or invalid output files

**Solution:**

```bash
# Run locally first
python cli/manage.py validate

# Check outputs
ls -la outputs/

# Run pipeline
python cli/manage.py run
```

### API Key Errors

**Cause:** Missing GitHub Secrets

**Solution:**

1. Add `OPENAI_API_KEY` and/or `PERPLEXITY_API_KEY` to secrets
2. Or run validation-only (doesn't need API keys)

### Auto-commit Not Working

**Cause:** Insufficient permissions

**Solution:**

- Verify `GITHUB_TOKEN` has write permissions
- Check repository settings → Actions → General
- Enable "Read and write permissions"

### Pipeline Takes Too Long

**Cause:** Full pipeline includes API calls

**Solution:**

- Use `pull_request` event (validation only)
- Or add timeout limits in workflow
- Or mock API calls for CI

---

## 📈 Monitoring

### GitHub Actions Dashboard

View workflow status:

- **Actions** tab shows all runs
- Green ✅ = success
- Red ❌ = failure
- Yellow 🟡 = in progress

### Workflow Summary

Each run includes:

- ✅ Validation results
- ✅ Code statistics
- ✅ Documentation status
- ✅ Build number and commit info

### Notifications

Configure in: **Settings → Notifications**

- Email on workflow failure
- Slack integration available
- GitHub app notifications

---

## 🚀 Advanced Configuration

### Custom Workflow Triggers

Add to `.github/workflows/management_team.yml`:

```yaml
on:
  schedule:
    - cron: "0 2 * * *" # Daily at 2 AM UTC
  workflow_dispatch:
    inputs:
      phase:
        description: "Phase to run (1-6, or blank for all)"
        required: false
```

### Matrix Testing

Test multiple Python versions:

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

### Deployment

Add deployment step:

```yaml
- name: Deploy to production
  if: github.ref == 'refs/heads/main'
  run: |
    # Your deployment script
    ./deploy.sh
```

---

## ✅ Success Checklist

- [ ] GitHub Actions workflow file created
- [ ] API keys added to GitHub Secrets
- [ ] Workflow runs successfully on push
- [ ] Validation tests pass
- [ ] Artifacts uploaded correctly
- [ ] Build summary auto-committed (main)
- [ ] Branch protection enabled (optional)
- [ ] Team notified of CI setup

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Managing Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

**Setup Complete!** 🎉

Your Management Team system now has fully automated CI/CD with:

- Continuous validation
- Automated testing
- Artifact preservation
- Auto-documentation
- Quality control

---

**Last Updated:** Phase 8 Implementation  
**Status:** Production Ready
