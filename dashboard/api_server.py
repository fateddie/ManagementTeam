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
import uvicorn

from agent_runner import get_runner
from file_manager import FileManager
from config import API_HOST, API_PORT, AGENTS

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
