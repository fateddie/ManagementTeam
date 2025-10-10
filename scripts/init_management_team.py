"""
AI MANAGEMENT TEAM INITIALIZER
v1.0  |  Author: Rob / Strategy Agent

Purpose:
    Quickly spin up a new management-team instance for Claude Code projects.
    Creates /docs/system structure and seeds all governance + agent files.

Usage:
    python init_management_team.py "ProjectName"
"""

import os
from datetime import date
import textwrap

# ---------------- CONFIG ---------------- #
BASE_DIR = "docs/system"
FILES = [
    "management_team_charter_v1.0.md",
    "management_team_rules.yaml",
    "agent_definitions.yaml",
    "system_context.yaml",
    "README_management_team.md",
    "change_log.md",
]
# ---------------------------------------- #


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def write_file(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")


def seed_charter(project_name):
    return f"""# MANAGEMENT TEAM CHARTER v1.0
**Project:** {project_name}
**Date:** {date.today()}

> Rapidly deliver innovative, data-driven AI solutions that transform businesses,
> save them money, and free them to focus on core operations.

See README_management_team.md for usage.
"""


def seed_readme(project_name):
    return textwrap.dedent(f"""
    # AI MANAGEMENT TEAM – README
    **Project:** {project_name}  
    **Created:** {date.today()}

    This directory defines the management framework for **{project_name}**.
    Load these files into Claude Code context before development begins.

    Folder structure:
    ```
    /docs/system/
      ├── management_team_charter_v1.0.md
      ├── management_team_rules.yaml
      ├── agent_definitions.yaml
      ├── system_context.yaml
      ├── README_management_team.md
      └── change_log.md
    ```
    """)


def seed_change_log(project_name):
    return f"""# CHANGE LOG – {project_name}
## {date.today()}
Initial scaffold created for project **{project_name}** using init_management_team.py
"""


def main():
    import sys
    project_name = sys.argv[1] if len(sys.argv) > 1 else "New_Project"

    ensure_dir(BASE_DIR)
    print(f"📁 Creating {BASE_DIR}/ for project: {project_name}")

    # basic charter, readme, changelog
    write_file(os.path.join(BASE_DIR, "management_team_charter_v1.0.md"),
               seed_charter(project_name))
    write_file(os.path.join(BASE_DIR, "README_management_team.md"),
               seed_readme(project_name))
    write_file(os.path.join(BASE_DIR, "change_log.md"),
               seed_change_log(project_name))

    # placeholders for other yaml/md files
    placeholders = {
        "management_team_rules.yaml": "# TODO: insert shared decision rules\n",
        "agent_definitions.yaml": "# TODO: insert agent definitions\n",
        "system_context.yaml": "# TODO: insert system workflow\n"
    }

    for file, content in placeholders.items():
        write_file(os.path.join(BASE_DIR, file), content)

    print("✅ Management-team scaffold initialized successfully.")
    print(f"→ Located in: {BASE_DIR}/")


if __name__ == "__main__":
    main()

