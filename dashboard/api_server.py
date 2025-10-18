"""
api_server.py
FastAPI backend for agent monitoring dashboard

Provides REST API endpoints for:
- Agent control (start/stop)
- Status monitoring
- Log access
- File operations
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pathlib import Path
import uvicorn

from agent_runner import get_runner
from file_manager import FileManager
from config import API_HOST, API_PORT, AGENTS, OUTPUTS_DIR, DATA_DIR, PROJECT_ROOT

# Initialize FastAPI app
app = FastAPI(
    title="Agent Monitoring API",
    description="REST API for monitoring and controlling AI agents",
    version="1.0.0"
)

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
runner = get_runner()
file_manager = FileManager()


# Request/Response models
class StartAgentRequest(BaseModel):
    args: Optional[List[str]] = None


class WriteFileRequest(BaseModel):
    content: str


# ============================================================================
# Agent Endpoints
# ============================================================================

@app.get("/")
def root():
    """API root endpoint."""
    return {
        "name": "Agent Monitoring API",
        "version": "1.0.0",
        "endpoints": {
            "agents": "/api/agents",
            "status": "/api/agents/status",
            "logs": "/api/agents/{agent_name}/logs",
            "files": "/api/files/tree"
        }
    }


@app.get("/api/agents")
def list_agents():
    """List all available agents."""
    return {"agents": AGENTS}


@app.get("/api/agents/status")
def get_all_agent_status():
    """Get status of all agents."""
    return {"status": runner.get_all_status()}


@app.get("/api/agents/{agent_name}/status")
def get_agent_status(agent_name: str):
    """Get status of a specific agent."""
    status = runner.get_agent_status(agent_name)
    return status


@app.post("/api/agents/{agent_name}/start")
def start_agent(agent_name: str, request: StartAgentRequest = None):
    """Start an agent."""
    args = request.args if request else None
    result = runner.start_agent(agent_name, args)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@app.post("/api/agents/{agent_name}/stop")
def stop_agent(agent_name: str):
    """Stop a running agent."""
    result = runner.stop_agent(agent_name)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@app.get("/api/agents/{agent_name}/logs")
def get_agent_logs(agent_name: str, lines: int = 100):
    """Get recent log lines for an agent."""
    result = runner.get_logs(agent_name, lines)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


# ============================================================================
# File Endpoints
# ============================================================================

@app.get("/api/files/tree")
def get_file_tree():
    """Get file tree for monitored directories."""
    return {"tree": file_manager.get_file_tree()}


@app.get("/api/files/recent")
def get_recent_files(limit: int = 10):
    """Get recently modified files."""
    return {"files": file_manager.get_recent_files(limit)}


@app.get("/api/files/content")
def read_file(path: str):
    """
    Read file contents.

    Query param:
        path: Relative path from project root
    """
    result = file_manager.read_file(path)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@app.put("/api/files/content")
def write_file(path: str, request: WriteFileRequest):
    """
    Write file contents.

    Query param:
        path: Relative path from project root

    Body:
        content: New file content
    """
    result = file_manager.write_file(path, request.content)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Write failed"))

    return result


@app.delete("/api/files/content")
def delete_file(path: str):
    """
    Delete a file.

    Query param:
        path: Relative path from project root
    """
    result = file_manager.delete_file(path)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Delete failed"))

    return result


# ============================================================================
# Health & Info
# ============================================================================

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "agent-monitoring-api"}


@app.get("/api/info")
def get_system_info():
    """Get system information."""
    from config import PROJECT_ROOT, OUTPUTS_DIR, RESULTS_DIR, DATA_DIR

    return {
        "project_root": str(PROJECT_ROOT),
        "outputs_dir": str(OUTPUTS_DIR),
        "results_dir": str(RESULTS_DIR),
        "data_dir": str(DATA_DIR),
        "total_agents": len(AGENTS),
        "api_version": "1.0.0"
    }


# ============================================================================
# Workflow & Agent Attribution Endpoints
# ============================================================================

@app.get("/api/workflow/status")
def get_workflow_status():
    """
    Get workflow status showing which stages are complete.

    Returns workflow progress based on agent outputs in directories.
    Helps visualize the idea-to-project pipeline progress.
    """
    try:
        workflow_stages = _analyze_workflow_status()
        return {"workflow": workflow_stages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze workflow: {str(e)}")


@app.get("/api/files/by-agent")
def get_files_by_agent():
    """
    Get files grouped by the agent that produced them.

    Analyzes file paths and names to determine which agent created each file.
    Enables agent-centric view of outputs.
    """
    try:
        agent_files = {
            "RefinementAgent": [],
            "IterativeWorkshopAgent": [],
            "VerticalAgent": [],
            "StrategyAgent": [],
            "TechnicalArchitectAgent": [],
            "PlanningAgent": [],
            "DocumentationAgent": [],
            "ReportingAgent": [],
            "TrendResearchAgent": [],
            "Unknown": []
        }

        # Scan outputs directory
        for file_path in OUTPUTS_DIR.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                agent = _identify_agent_from_file(file_path)
                file_info = {
                    "name": file_path.name,
                    "path": str(file_path.relative_to(PROJECT_ROOT)),
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime,
                    "extension": file_path.suffix
                }
                agent_files[agent].append(file_info)

        # Scan data directory
        for file_path in DATA_DIR.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                agent = _identify_agent_from_file(file_path)
                file_info = {
                    "name": file_path.name,
                    "path": str(file_path.relative_to(PROJECT_ROOT)),
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime,
                    "extension": file_path.suffix
                }
                agent_files[agent].append(file_info)

        # Sort each agent's files by modification time (newest first)
        for agent in agent_files:
            agent_files[agent].sort(key=lambda x: x['modified'], reverse=True)

        return {"agents": agent_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to group files by agent: {str(e)}")


def _identify_agent_from_file(file_path: Path) -> str:
    """
    Identify which agent created a file based on path and filename.

    Uses pattern matching on file paths and names.
    Returns agent name or "Unknown" if can't determine.
    """
    path_str = str(file_path).lower()
    filename = file_path.name.lower()

    # Refinement agent patterns
    if 'refined' in filename or 'refinement' in path_str:
        return "RefinementAgent"

    # Workshop agent patterns
    if 'workshop' in filename or 'workshop' in path_str:
        return "IterativeWorkshopAgent"
    if 'pain_discovery' in filename or 'market_sizing' in filename or 'competitive_landscape' in filename:
        return "IterativeWorkshopAgent"

    # Vertical agent patterns
    if 'vertical' in filename or 'vertical' in path_str:
        return "VerticalAgent"

    # Strategy agent patterns
    if 'strategy' in filename or 'goals' in filename:
        return "StrategyAgent"

    # Technical architect patterns
    if 'architecture' in filename or 'technical' in filename or 'tech_stack' in filename:
        return "TechnicalArchitectAgent"

    # Planning agent patterns
    if 'plan' in filename or 'planning' in path_str:
        return "PlanningAgent"

    # Documentation agent patterns
    if 'documentation' in filename or 'docs' in path_str or filename.endswith('.md'):
        return "DocumentationAgent"

    # Reporting agent patterns
    if 'report' in filename or 'summary' in filename:
        return "ReportingAgent"

    # Trend research patterns
    if 'trend' in filename or 'social' in filename or 'reddit' in filename or 'twitter' in filename:
        return "TrendResearchAgent"

    return "Unknown"


def _analyze_workflow_status() -> List[Dict[str, Any]]:
    """
    Analyze workflow progress by checking for agent outputs.

    Returns list of workflow stages with completion status.
    """
    stages = [
        {
            "stage": 0.5,
            "name": "Trend Research",
            "agent": "TrendResearchAgent",
            "description": "Social media trending & pain point discovery",
            "complete": False,
            "outputs": []
        },
        {
            "stage": 1,
            "name": "Idea Refinement",
            "agent": "RefinementAgent",
            "description": "Clarify and refine initial idea",
            "complete": False,
            "outputs": []
        },
        {
            "stage": 1.5,
            "name": "Workshop Analysis",
            "agent": "IterativeWorkshopAgent",
            "description": "3-round stress testing (Pain/Market/Competition)",
            "complete": False,
            "outputs": []
        },
        {
            "stage": 2,
            "name": "Vertical Strategy",
            "agent": "VerticalAgent",
            "description": "Define target verticals and positioning",
            "complete": False,
            "outputs": []
        },
        {
            "stage": 3,
            "name": "Strategy Development",
            "agent": "StrategyAgent",
            "description": "Business strategy and goals",
            "complete": False,
            "outputs": []
        },
        {
            "stage": 4,
            "name": "Technical Architecture",
            "agent": "TechnicalArchitectAgent",
            "description": "System design and tech stack",
            "complete": False,
            "outputs": []
        },
        {
            "stage": 5,
            "name": "Implementation Planning",
            "agent": "PlanningAgent",
            "description": "Development plan and milestones",
            "complete": False,
            "outputs": []
        },
        {
            "stage": 6,
            "name": "Documentation",
            "agent": "DocumentationAgent",
            "description": "Technical documentation",
            "complete": False,
            "outputs": []
        },
        {
            "stage": 7,
            "name": "Reporting",
            "agent": "ReportingAgent",
            "description": "Final reports and summaries",
            "complete": False,
            "outputs": []
        }
    ]

    # Check for outputs in each stage
    for stage in stages:
        agent_name = stage["agent"]

        # Search for files created by this agent
        for file_path in OUTPUTS_DIR.rglob('*'):
            if file_path.is_file():
                if _identify_agent_from_file(file_path) == agent_name:
                    stage["outputs"].append(str(file_path.relative_to(PROJECT_ROOT)))
                    stage["complete"] = True

        for file_path in DATA_DIR.rglob('*'):
            if file_path.is_file():
                if _identify_agent_from_file(file_path) == agent_name:
                    stage["outputs"].append(str(file_path.relative_to(PROJECT_ROOT)))
                    stage["complete"] = True

    return stages


# ============================================================================
# Project Context Endpoints
# ============================================================================

# Initialize context tracker (optional - graceful failure)
try:
    from core.project_context import ProjectContext
    context_tracker = ProjectContext()
except Exception as e:
    context_tracker = None
    print(f"⚠️  Project context unavailable: {e}")


@app.get("/api/context/projects")
def list_context_projects(status: Optional[str] = None):
    """
    List all projects, optionally filtered by status.

    Query params:
        status: Optional filter (planning, active, paused, completed, cancelled)
    """
    if not context_tracker:
        raise HTTPException(status_code=503, detail="Context tracking unavailable")

    try:
        projects = context_tracker.list_projects(status=status)
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list projects: {str(e)}")


@app.post("/api/context/projects")
def create_context_project(
    name: str,
    description: str = "",
    deadline: Optional[str] = None,
    priority: str = "medium",
    tags: Optional[List[str]] = None
):
    """
    Create a new project.

    Body:
        name: Project name (required)
        description: Project description
        deadline: Target date (YYYY-MM-DD format)
        priority: Priority level (low, medium, high, urgent)
        tags: List of tags
    """
    if not context_tracker:
        raise HTTPException(status_code=503, detail="Context tracking unavailable")

    try:
        from datetime import datetime
        deadline_dt = datetime.fromisoformat(deadline) if deadline else None

        project_id = context_tracker.create_project(
            name=name,
            description=description,
            deadline=deadline_dt,
            priority=priority,
            tags=tags
        )

        if project_id:
            return {"success": True, "project_id": project_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to create project")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")


@app.get("/api/context/projects/{project_id}")
def get_context_project(project_id: str):
    """Get project details and summary."""
    if not context_tracker:
        raise HTTPException(status_code=503, detail="Context tracking unavailable")

    try:
        summary = context_tracker.get_project_summary(project_id)
        if not summary:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")


@app.put("/api/context/projects/{project_id}/status")
def update_context_project_status(
    project_id: str,
    status: str,
    progress_percent: Optional[int] = None
):
    """
    Update project status.

    Body:
        status: New status (planning, active, paused, completed, cancelled)
        progress_percent: Optional progress (0-100)
    """
    if not context_tracker:
        raise HTTPException(status_code=503, detail="Context tracking unavailable")

    try:
        success = context_tracker.update_project_status(
            project_id=project_id,
            status=status,
            progress_percent=progress_percent
        )

        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to update status")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")


@app.get("/api/context/projects/{project_id}/timeline")
def get_context_timeline(project_id: str, days: int = 7, limit: int = 50):
    """
    Get recent activity timeline.

    Query params:
        days: Number of days to look back (default: 7)
        limit: Maximum activities to return (default: 50)
    """
    if not context_tracker:
        raise HTTPException(status_code=503, detail="Context tracking unavailable")

    try:
        activity = context_tracker.get_recent_activity(
            project_id=project_id,
            days=days,
            limit=limit
        )
        return {"activity": activity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get timeline: {str(e)}")


@app.get("/api/context/projects/{project_id}/deadline")
def check_context_deadline(project_id: str):
    """Check deadline status and progress."""
    if not context_tracker:
        raise HTTPException(status_code=503, detail="Context tracking unavailable")

    try:
        status = context_tracker.check_deadline_status(project_id)
        return {
            "project_id": status.project_id,
            "target_date": str(status.target_date) if status.target_date else None,
            "days_remaining": status.days_remaining,
            "is_overdue": status.is_overdue,
            "status": status.status,
            "progress_percent": status.progress_percent
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check deadline: {str(e)}")


@app.post("/api/context/projects/{project_id}/milestones")
def add_context_milestone(
    project_id: str,
    name: str,
    target_date: Optional[str] = None,
    order: int = 0,
    description: str = ""
):
    """
    Add a milestone to a project.

    Body:
        name: Milestone name (required)
        target_date: Target date (YYYY-MM-DD)
        order: Display order
        description: Milestone description
    """
    if not context_tracker:
        raise HTTPException(status_code=503, detail="Context tracking unavailable")

    try:
        from datetime import datetime
        target_dt = datetime.strptime(target_date, '%Y-%m-%d').date() if target_date else None

        milestone_id = context_tracker.add_milestone(
            project_id=project_id,
            name=name,
            target_date=target_dt,
            order=order,
            description=description
        )

        if milestone_id:
            return {"success": True, "milestone_id": milestone_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to add milestone")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add milestone: {str(e)}")


@app.get("/api/context/projects/{project_id}/milestones")
def get_context_milestones(project_id: str):
    """Get all milestones for a project."""
    if not context_tracker:
        raise HTTPException(status_code=503, detail="Context tracking unavailable")

    try:
        milestones = context_tracker.get_milestones(project_id)
        return {"milestones": milestones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get milestones: {str(e)}")


@app.post("/api/context/projects/{project_id}/actions")
def add_context_action(
    project_id: str,
    title: str,
    priority: str = "medium",
    due_date: Optional[str] = None,
    description: str = "",
    milestone_id: Optional[int] = None
):
    """
    Add an action point/task.

    Body:
        title: Action title (required)
        priority: Priority (low, medium, high, urgent)
        due_date: Due date (YYYY-MM-DD)
        description: Action description
        milestone_id: Optional associated milestone
    """
    if not context_tracker:
        raise HTTPException(status_code=503, detail="Context tracking unavailable")

    try:
        from datetime import datetime
        due_dt = datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None

        action_id = context_tracker.add_action_point(
            project_id=project_id,
            title=title,
            priority=priority,
            due_date=due_dt,
            description=description,
            milestone_id=milestone_id
        )

        if action_id:
            return {"success": True, "action_id": action_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to add action")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add action: {str(e)}")


@app.get("/api/context/projects/{project_id}/actions")
def get_context_actions(
    project_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None
):
    """
    Get action points for a project.

    Query params:
        status: Filter by status (todo, in_progress, done, blocked, cancelled)
        priority: Filter by priority (low, medium, high, urgent)
    """
    if not context_tracker:
        raise HTTPException(status_code=503, detail="Context tracking unavailable")

    try:
        actions = context_tracker.get_action_points(
            project_id=project_id,
            status=status,
            priority=priority
        )
        return {"actions": actions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get actions: {str(e)}")


@app.put("/api/context/actions/{action_id}/status")
def update_context_action_status(
    action_id: int,
    status: str,
    actual_hours: Optional[float] = None
):
    """
    Update action status.

    Body:
        status: New status (todo, in_progress, done, blocked, cancelled)
        actual_hours: Optional time spent
    """
    if not context_tracker:
        raise HTTPException(status_code=503, detail="Context tracking unavailable")

    try:
        success = context_tracker.update_action_status(
            action_id=action_id,
            status=status,
            actual_hours=actual_hours
        )

        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to update action")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update action: {str(e)}")


@app.get("/api/context/projects/{project_id}/decisions")
def get_context_decisions(project_id: str):
    """Get all decisions for a project."""
    if not context_tracker:
        raise HTTPException(status_code=503, detail="Context tracking unavailable")

    try:
        decisions = context_tracker.get_decisions(project_id)
        return {"decisions": decisions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get decisions: {str(e)}")


@app.post("/api/context/projects/{project_id}/notes")
def add_context_note(
    project_id: str,
    note_type: str,
    title: str,
    content: str,
    action_id: Optional[int] = None,
    milestone_id: Optional[int] = None
):
    """
    Add a note (issue, success, idea, learning).

    Body:
        note_type: Type (issue, success, idea, learning, general) (required)
        title: Note title (required)
        content: Note content (required)
        action_id: Optional related action
        milestone_id: Optional related milestone
    """
    if not context_tracker:
        raise HTTPException(status_code=503, detail="Context tracking unavailable")

    try:
        success = context_tracker.add_note(
            project_id=project_id,
            note_type=note_type,
            title=title,
            content=content,
            action_id=action_id,
            milestone_id=milestone_id
        )

        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to add note")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add note: {str(e)}")


@app.get("/api/context/projects/{project_id}/notes")
def get_context_notes(
    project_id: str,
    note_type: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Get notes for a project.

    Query params:
        note_type: Filter by type (issue, success, idea, learning, general)
        status: Filter by status (open, in_progress, resolved, wont_fix)
    """
    if not context_tracker:
        raise HTTPException(status_code=503, detail="Context tracking unavailable")

    try:
        notes = context_tracker.get_notes(
            project_id=project_id,
            note_type=note_type,
            status=status
        )
        return {"notes": notes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notes: {str(e)}")


# ============================================================================
# Main
# ============================================================================

def main():
    """Run the API server."""
    print(f"\n🚀 Starting Agent Monitoring API...")
    print(f"📍 API: http://{API_HOST}:{API_PORT}")
    print(f"📖 Docs: http://{API_HOST}:{API_PORT}/docs")
    print(f"🔧 Monitoring {len(AGENTS)} agents\n")

    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()
