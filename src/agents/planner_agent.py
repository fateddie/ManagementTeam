# ==============================================
# file: /ManagementTeam/src/agents/planner_agent.py
# ==============================================
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from src.utils.io_utils import ensure_dir, write_text, read_text
from src.utils.parser_utils import extract_entities, identify_gaps
from src.utils.elicitation_utils import questions_markdown
from src.utils.template_utils import fill_template
from src.utils.validation_utils import validate_yaml_structure
from src.utils.log_utils import logger

TEMPLATES_DIR = Path("/Users/robertfreyne/Documents/ClaudeCode/ManagementTeam/config/templates")
PROJECTS_DIR = Path("/Users/robertfreyne/Documents/ClaudeCode/ManagementTeam/projects")


def run(project_name: str, description: str, author: str = "Rob Freyne", interactive: bool = False) -> Dict[str, Any]:
    """
    Orchestrates the planning workflow for a new project with real-time oversight and logging.
    
    Args:
        project_name: Name of the project (used for folder structure)
        description: Free-text description of the project
        author: Project author/owner
        interactive: Enable interactive review mode with pause points
        
    Returns:
        Dictionary containing project root, generated files, and gaps
    """
    logger.info(f"🚀 Initializing Planner Agent for project: {project_name}")
    project_root = PROJECTS_DIR / project_name
    planning_dir = project_root / "planning"
    ensure_dir(planning_dir)

    # STEP 1: Parse description
    logger.info("🔍 STEP 1: Parsing user description.")
    entities = extract_entities(description, defaults={"title": project_name, "author": author})
    logger.info(f"✓ Entities extracted: {list(entities.keys())}")

    if interactive:
        _pause_for_review("Entities parsed", entities)

    # STEP 2: Identify missing data
    logger.info("🔍 STEP 2: Identifying missing or incomplete data.")
    gaps = identify_gaps(entities)
    missing_md = questions_markdown(gaps)
    write_text(planning_dir / "missing_info.md", missing_md)
    if gaps:
        logger.warning(f"⚠️  Missing info written ({len(gaps)} gaps detected).")
    else:
        logger.info("✓ No gaps detected.")

    if interactive and gaps:
        _pause_for_review("Detected data gaps", gaps)

    # STEP 3: Load templates
    logger.info("🔍 STEP 3: Loading templates.")
    plan_tpl = read_text(TEMPLATES_DIR / "project_plan.yaml")
    roadmap_tpl = read_text(TEMPLATES_DIR / "roadmap.md")
    folder_json = json.loads(read_text(TEMPLATES_DIR / "folder_structure.json"))
    logger.info("✓ Templates loaded successfully.")

    # STEP 4: Prepare data
    logger.info("🔍 STEP 4: Preparing template data.")
    data_dict = {
        "title": entities.get("title", project_name),
        "author": entities.get("author", author),
        "date_created": datetime.now().strftime("%Y-%m-%d"),
        "version": "1.0",
        "summary": entities.get("summary", description.strip()[:280]),
        "milestones": entities.get("milestones", []),
    }
    logger.info(f"✓ Data prepared with {len(data_dict['milestones'])} milestones")

    # STEP 5: Generate project_plan.yaml
    logger.info("🔍 STEP 5: Generating project_plan.yaml.")
    plan_filled = fill_template(plan_tpl, data_dict)
    validate_yaml_structure(plan_filled, required_top_keys=["meta", "project"])
    write_text(planning_dir / "project_plan.yaml", plan_filled)
    logger.info("✓ project_plan.yaml created and validated successfully.")

    if interactive:
        _pause_for_review("Generated project_plan.yaml", plan_filled[:500] + "...")

    # STEP 6: Generate roadmap.md
    logger.info("🔍 STEP 6: Generating roadmap.md.")
    roadmap_filled = fill_template(roadmap_tpl, data_dict)
    write_text(planning_dir / "roadmap.md", roadmap_filled)
    logger.info("✓ roadmap.md created successfully.")

    if interactive:
        _pause_for_review("Generated roadmap.md", roadmap_filled[:500] + "...")

    # STEP 7: Create folder structure
    logger.info("🔍 STEP 7: Creating project folder structure.")
    create_scaffold(project_root, folder_json)
    logger.info("✓ Project structure scaffolded.")

    # STEP 8: Generate reflection report
    logger.info("🔍 STEP 8: Generating reflection report.")
    reflection_path = planning_dir / "reflection_report.md"
    reflection = _generate_reflection(gaps, entities, planning_dir)
    write_text(reflection_path, reflection)
    logger.info("✓ Reflection report generated.")

    # STEP 9: Write summary
    logger.info("🔍 STEP 9: Writing summary report.")
    summary = {
        "project_root": str(project_root),
        "generated": [
            str(planning_dir / "project_plan.yaml"),
            str(planning_dir / "roadmap.md"),
            str(planning_dir / "missing_info.md"),
            str(reflection_path),
        ],
        "gaps": gaps,
    }
    write_text(planning_dir / "summary_report.json", json.dumps(summary, indent=2))
    logger.info("✓ Summary report written.")
    logger.info(f"✅ Planner Agent completed successfully for project: {project_name}")

    return summary


def create_scaffold(project_root: Path, folder_json: Dict[str, Any]) -> None:
    """
    Create the project folder structure based on folder_structure.json.
    
    Args:
        project_root: Root directory for the project
        folder_json: JSON structure defining folders and files
    """
    ensure_dir(project_root)
    structure = folder_json.get("structure", {})
    folders_created = 0
    files_created = 0
    
    for folder, files in structure.items():
        folder_path = project_root / folder
        ensure_dir(folder_path)
        folders_created += 1
        
        if isinstance(files, list):
            for fname in files:
                fpath = folder_path / fname
                if not fpath.exists():
                    write_text(fpath, "")
                    files_created += 1
                    logger.debug(f"Created stub file: {fpath.relative_to(project_root)}")
        elif isinstance(files, dict):
            # Handle nested structures (like data: {raw: [], processed: []})
            for subfolder in files:
                ensure_dir(folder_path / subfolder)
                folders_created += 1
    
    logger.info(f"✓ Created {folders_created} directories and {files_created} stub files")


def _pause_for_review(step_name: str, data: Any) -> None:
    """
    Pause execution for human review in interactive mode.
    
    Args:
        step_name: Name of the current step
        data: Data to display for review
    """
    print("\n🟡 [PlannerAgent Oversight] Review Point:")
    print(f"Step: {step_name}")
    print(f"Data Preview:\n{data}\n")
    user_input = input("Proceed? (Y/n/edit): ").strip().lower()
    
    if user_input == "n":
        logger.warning(f"❌ Execution aborted by user at step: {step_name}")
        raise SystemExit(0)
    elif user_input == "edit":
        logger.info(f"✏️  User requested edit at step: {step_name}")
        print("Open the relevant file manually, then press Enter to continue...")
        input()
    else:
        logger.info(f"✓ User approved step: {step_name}")


def _generate_reflection(gaps: Dict[str, Any], entities: Dict[str, Any], planning_dir: Path) -> str:
    """
    Generate a reflection report analyzing the planning process.
    
    Args:
        gaps: Dictionary of detected information gaps
        entities: Extracted entities from description
        planning_dir: Directory where planning files are stored
        
    Returns:
        Markdown-formatted reflection report
    """
    reflection = [
        "# 🧩 Planner Agent Reflection Report",
        "",
        f"**Run Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**Project:** {entities.get('title', 'Unnamed')}  ",
        f"**Author:** {entities.get('author', 'Unknown')}  ",
        "",
        "---",
        "",
        "## 📊 Summary",
        "",
        f"- **Detected Gaps:** {len(gaps)}",
        f"- **Entities Parsed:** {', '.join(list(entities.keys()))}",
        f"- **Milestones Identified:** {len(entities.get('milestones', []))}",
        "",
        "---",
        "",
        "## ⚠️ Information Gaps",
        "",
    ]
    
    if gaps:
        for key, reason in gaps.items():
            reflection.append(f"- **{key}**: {reason}")
    else:
        reflection.append("✅ No information gaps detected. Project description was comprehensive.")
    
    reflection.extend([
        "",
        "---",
        "",
        "## 💡 Suggested Improvements",
        "",
        "### For Future Projects:",
        "- Add more structured milestone input in user prompts",
        "- Consider refining YAML templates with objective definitions",
        "- Include stakeholder identification in initial description",
        "- Specify success criteria and KPIs upfront",
        "",
        "### For This Project:",
        "- Review `missing_info.md` and provide missing details",
        "- Validate generated `project_plan.yaml` against requirements",
        "- Customize roadmap timeline based on team capacity",
        "",
        "---",
        "",
        "## 📁 Generated Artifacts",
        "",
        f"- `{planning_dir.name}/project_plan.yaml` - Structured project plan",
        f"- `{planning_dir.name}/roadmap.md` - Timeline and milestones",
        f"- `{planning_dir.name}/missing_info.md` - Information gaps",
        f"- `{planning_dir.name}/summary_report.json` - Machine-readable summary",
        "",
        "---",
        "",
        "**Generated by:** Planner Agent v1.1  ",
        "**Template Version:** 1.1  ",
    ])
    
    return "\n".join(reflection)


if __name__ == "__main__":
    # Simple manual test entrypoint
    demo = run(
        project_name="management-layer-demo",
        description=(
            "Build an AI Management Layer that plans, documents, and coordinates agent projects. "
            "Integrate Claude/Cursor and a Mem0 memory layer with a future Neo4j export."
        ),
        author="Rob Freyne",
        interactive=False,
    )
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    print(json.dumps(demo, indent=2))
