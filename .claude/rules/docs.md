# Documentation Maintenance Rules for Claude Code

**Purpose:** Ensure documentation integrity and consistency when creating or modifying .md files in the ManagementTeam project.

**Last Updated:** 2026-01-03

---

## 🎯 Core Responsibilities

Claude Code MUST follow these rules when creating, editing, or moving documentation files:

---

## 📝 Rule 1: Check for Broken Links

**When:** Creating new .md files OR editing existing links

**What to do:**
1. Scan the new/edited file for all markdown links: `[text](path.md)`
2. Verify each linked file exists at the specified path
3. Check relative path correctness (e.g., `../setup/GUIDE.md` vs `setup/GUIDE.md`)
4. For internal links to headers: `[text](#section)`, verify the header exists in target file
5. If a broken link is detected, either:
   - Fix the path
   - Create the missing file (if appropriate)
   - Remove the link (if no longer needed)
   - Ask the user for clarification

**Example Check:**
```python
# Pseudo-code for link validation
def validate_links(file_path):
    content = read(file_path)
    links = extract_markdown_links(content)
    for link in links:
        if link.startswith('http'):
            continue  # External link - skip
        target = resolve_relative_path(file_path, link)
        if not file_exists(target):
            warn(f"Broken link in {file_path}: {link}")
```

**Tools to use:**
```bash
# Check for broken links manually
mkdocs build --strict
# This will fail if navigation references missing files
```

---

## 📚 Rule 2: Update mkdocs.yml Navigation

**When:** Creating new TOP-LEVEL documentation files in `docs/` (not subfolders)

**What to do:**
1. Open `mkdocs.yml`
2. Find the appropriate section in the `nav:` block
3. Add a navigation entry for the new file
4. Follow the existing naming pattern (emoji + title)
5. Place the entry in a logical position (alphabetical or by importance)

**Example:**
```yaml
# Before
- 🚀 Getting Started:
  - Quick Start: QUICKSTART.md
  - API Keys Setup: setup/API_KEYS_SETUP_GUIDE.md

# After adding "NEW_GUIDE.md"
- 🚀 Getting Started:
  - Quick Start: QUICKSTART.md
  - New Guide: NEW_GUIDE.md  # ← Added
  - API Keys Setup: setup/API_KEYS_SETUP_GUIDE.md
```

**When NOT to update mkdocs.yml:**
- Editing existing files (no change needed)
- Creating files in subfolders that are already in navigation tree
- Creating temporary/draft files

---

## 🏷️ Rule 3: Validate YAML Frontmatter Consistency

**When:** Creating new .md files

**What to do:**
1. Check if the project uses YAML frontmatter (check 2-3 existing docs)
2. If YES, include frontmatter in new files:
   ```yaml
   ---
   title: Document Title
   description: Brief description
   date: 2026-01-03
   author: Claude Code
   ---
   ```
3. If NO, skip frontmatter (don't add if not used)

**Current state for this project:** NOT using frontmatter (checked README, ARCHITECTURE, PRINCIPLES)

**Action:** Do NOT add frontmatter unless user requests it.

---

## 🆕 Rule 4: Update index.md Dashboard for New Modules

**When:** Creating new MODULES or MAJOR FEATURES (not minor docs)

**What to do:**
1. Open `docs/index.md`
2. Add an entry in the relevant section (e.g., "Modules & Features")
3. Include:
   - Descriptive title
   - Brief one-liner explanation
   - Link to the module's main documentation
4. Update system stats if applicable (e.g., increment "Modules" count)

**Example:**
```markdown
### 🔬 Modules & Advanced Features

**Pain Point Radar System** (NEW):
- [Technical Design](modules/pain_point_radar/TECHNICAL_DESIGN.md)

**My New Module** (NEW):  # ← Added
- [Overview](modules/my_new_module/README.md) - Brief description
```

**When to update index.md:**
- Adding a new module under `docs/modules/`
- Adding a major feature (e.g., new AI agent, integration)
- Adding a new section/category

**When NOT to update:**
- Minor doc updates
- Typo fixes
- Reordering existing content

---

## 🧪 Rule 5: Run Local Build Before Committing

**When:** Making significant documentation changes (new files, navigation updates, major edits)

**What to do:**
1. Run `mkdocs build --strict` locally
2. If build fails, fix errors before committing
3. Common errors:
   - Missing navigation entries
   - Broken internal links
   - Invalid YAML in mkdocs.yml
   - Missing files referenced in navigation

**Command:**
```bash
# Validate documentation build
mkdocs build --strict --verbose

# Test locally with live reload
mkdocs serve
# Opens http://127.0.0.1:8000
```

**If mkdocs not installed:**
```bash
pip install -r requirements-docs.txt
```

**If build fails:**
- Read error message carefully
- Check navigation paths in mkdocs.yml
- Verify all linked files exist
- Fix and re-run

---

## 📸 Rule 6: Update PROJECT_SNAPSHOT.md for Major Changes

**When:** Making significant system changes that affect documentation structure

**What to do:**
1. Open `docs/PROJECT_SNAPSHOT.md`
2. Update the "Documentation" section if:
   - New major documentation category added
   - Documentation structure reorganized
   - New module documentation created
3. Update version/date at top
4. Add entry to change log section (if present)

**Example updates:**
- Adding Pain Point Radar module → Update snapshot
- Fixing typos → Skip snapshot update
- Adding new Getting Started guide → Update snapshot

---

## 🔍 Rule 7: Navigation Path Validation

**When:** Moving or renaming files

**What to do:**
1. Search mkdocs.yml for all references to the old filename
2. Update all navigation entries
3. Search all .md files for links to the old path
4. Update or add redirect note in old location

**Example move:**
```bash
# Moving docs/OLD.md → docs/new_location/NEW.md

# 1. Update mkdocs.yml
nav:
  - Old Doc: OLD.md  # Change to: new_location/NEW.md

# 2. Search for links
grep -r "OLD.md" docs/

# 3. Update all references
# OLD: [Link](OLD.md)
# NEW: [Link](new_location/NEW.md)
```

---

## 📋 Rule 8: Consistency Checks

**When:** Creating or editing documentation

**What to check:**
1. **Heading levels:** Use `#` for title, `##` for sections, `###` for subsections
2. **Emoji usage:** Follow existing emoji conventions (🚀 for Getting Started, 📖 for docs, etc.)
3. **Code blocks:** Always specify language (```python, ```bash, etc.)
4. **Lists:** Use `-` for unordered, `1.` for ordered
5. **Links:** Use relative paths for internal docs, absolute URLs for external
6. **Dates:** Use ISO format (YYYY-MM-DD) or "Last Updated: YYYY-MM-DD"

**Good example:**
```markdown
# System Architecture

**Last Updated:** 2026-01-03

## Overview
Brief overview here.

### Key Components
- Component 1
- Component 2

```python
def example():
    pass
```

[Related Doc](../setup/GUIDE.md)
[External Link](https://example.com)
```

---

## 🚫 What NOT to Do

❌ **Don't** create orphan documentation (files not linked from anywhere)
❌ **Don't** hard-code absolute paths to local files
❌ **Don't** use markdown extensions not enabled in mkdocs.yml
❌ **Don't** commit broken documentation builds
❌ **Don't** duplicate content across multiple files (use links instead)
❌ **Don't** mix documentation styles (stick to existing patterns)

---

## ✅ Checklist: Before Committing Documentation Changes

Use this checklist for significant documentation work:

- [ ] All new .md files added to mkdocs.yml navigation (if top-level)
- [ ] All internal links validated (no 404s)
- [ ] index.md updated (if new module/major feature)
- [ ] PROJECT_SNAPSHOT.md updated (if major change)
- [ ] Local build successful: `mkdocs build --strict`
- [ ] Local preview checked: `mkdocs serve`
- [ ] Frontmatter consistent with project style (if used)
- [ ] Code blocks have language specifiers
- [ ] Emoji usage consistent with existing docs
- [ ] Relative paths used for internal links
- [ ] No orphan files (all docs linked from somewhere)

---

## 🔧 Automated Tools

**Pre-commit check (recommended):**
```bash
# Add to .pre-commit-config.yaml
- repo: local
  hooks:
    - id: mkdocs-build
      name: MkDocs Build Check
      entry: mkdocs build --strict
      language: system
      pass_filenames: false
      files: '(mkdocs\.yml|docs/.*\.md)$'
```

**Link checker:**
```bash
# Install markdown-link-check
npm install -g markdown-link-check

# Check all docs
find docs -name "*.md" -exec markdown-link-check {} \;
```

---

## 📊 Documentation Statistics

**Current stats (as of 2026-01-03):**
- Total .md files: ~120
- Navigation sections: 9 main categories
- Modules documented: 1 (Pain Point Radar)
- Setup guides: 9
- PRDs: 7
- Status reports: 5

**Update these stats when:**
- Adding new documentation files
- Creating new modules
- Reorganizing navigation

---

## 🆘 When Uncertain

If you're uncertain about:
- Where to place a new document → Ask the user
- Whether to update navigation → Err on side of updating (can always remove)
- Link validation failing → Show user the broken link and ask
- Major restructuring → Present plan to user before executing

**Remember:** Documentation is for humans. When in doubt, prioritize clarity and accessibility over strict adherence to rules.

---

**Version:** 1.0
**Maintained by:** Claude Code
**Related:** mkdocs.yml, docs/index.md, docs/PROJECT_SNAPSHOT.md
