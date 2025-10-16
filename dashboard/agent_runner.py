"""
agent_runner.py
Agent execution wrapper for dashboard monitoring

This module provides subprocess management for running agents,
capturing their output, and tracking execution metadata.
"""

import subprocess
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from config import PROJECT_ROOT, DASHBOARD_RUNS_DIR, AGENTS


@dataclass
class AgentExecution:
    """Represents a single agent execution."""
    agent_name: str
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    status: str = "running"  # running, completed, failed, stopped
    exit_code: Optional[int] = None
    stdout_lines: List[str] = None
    stderr_lines: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.stdout_lines is None:
            self.stdout_lines = []
        if self.stderr_lines is None:
            self.stderr_lines = []
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return asdict(self)


class AgentRunner:
    """Manages agent execution as subprocesses."""

    def __init__(self):
        self.root = PROJECT_ROOT
        self.runs_dir = DASHBOARD_RUNS_DIR
        self.active_processes: Dict[str, subprocess.Popen] = {}
        self.executions: Dict[str, AgentExecution] = {}
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def start_agent(self, agent_name: str, args: List[str] = None) -> Dict[str, Any]:
        """
        Start an agent as a subprocess.

        Args:
            agent_name: Name of the agent to run
            args: Optional command-line arguments

        Returns:
            Dict with execution info
        """
        # Find agent config
        agent_config = next((a for a in AGENTS if a["name"] == agent_name), None)
        if not agent_config:
            return {"error": f"Agent {agent_name} not found"}

        # Check if already running
        if agent_name in self.active_processes:
            proc = self.active_processes[agent_name]
            if proc.poll() is None:
                return {"error": f"Agent {agent_name} is already running"}

        # Build command
        agent_path = self.root / agent_config["path"]
        if not agent_path.exists():
            return {"error": f"Agent file not found: {agent_path}"}

        cmd = ["python", str(agent_path)]
        if args:
            cmd.extend(args)

        # Create execution record
        execution = AgentExecution(
            agent_name=agent_name,
            session_id=self.session_id,
            start_time=datetime.now().isoformat(),
            metadata={"command": " ".join(cmd)}
        )

        try:
            # Start process
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=str(self.root)
            )

            self.active_processes[agent_name] = proc
            self.executions[agent_name] = execution

            # Start output capture thread
            threading.Thread(
                target=self._capture_output,
                args=(agent_name, proc),
                daemon=True
            ).start()

            # Save execution metadata
            self._save_execution(agent_name)

            return {
                "success": True,
                "agent_name": agent_name,
                "pid": proc.pid,
                "session_id": self.session_id,
                "start_time": execution.start_time
            }

        except Exception as e:
            execution.status = "failed"
            execution.end_time = datetime.now().isoformat()
            execution.metadata["error"] = str(e)
            self._save_execution(agent_name)

            return {"error": str(e)}

    def stop_agent(self, agent_name: str) -> Dict[str, Any]:
        """
        Stop a running agent.

        Args:
            agent_name: Name of the agent to stop

        Returns:
            Dict with status
        """
        if agent_name not in self.active_processes:
            return {"error": f"Agent {agent_name} is not running"}

        proc = self.active_processes[agent_name]

        try:
            proc.terminate()
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

        # Update execution record
        if agent_name in self.executions:
            execution = self.executions[agent_name]
            execution.status = "stopped"
            execution.end_time = datetime.now().isoformat()
            execution.exit_code = proc.returncode
            self._save_execution(agent_name)

        del self.active_processes[agent_name]

        return {"success": True, "agent_name": agent_name, "stopped": True}

    def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """
        Get current status of an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Dict with status info
        """
        is_running = False
        pid = None

        if agent_name in self.active_processes:
            proc = self.active_processes[agent_name]
            if proc.poll() is None:
                is_running = True
                pid = proc.pid
            else:
                # Process finished, update execution
                if agent_name in self.executions:
                    execution = self.executions[agent_name]
                    execution.status = "completed" if proc.returncode == 0 else "failed"
                    execution.end_time = datetime.now().isoformat()
                    execution.exit_code = proc.returncode
                    self._save_execution(agent_name)

                del self.active_processes[agent_name]

        execution_info = {}
        if agent_name in self.executions:
            execution_info = self.executions[agent_name].to_dict()

        return {
            "agent_name": agent_name,
            "is_running": is_running,
            "pid": pid,
            **execution_info
        }

    def get_all_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents."""
        return [self.get_agent_status(agent["name"]) for agent in AGENTS]

    def get_logs(self, agent_name: str, lines: int = 100) -> Dict[str, Any]:
        """
        Get recent log lines for an agent.

        Args:
            agent_name: Name of the agent
            lines: Number of lines to return (default 100)

        Returns:
            Dict with stdout and stderr
        """
        if agent_name not in self.executions:
            return {"error": f"No execution found for {agent_name}"}

        execution = self.executions[agent_name]

        return {
            "agent_name": agent_name,
            "stdout": execution.stdout_lines[-lines:],
            "stderr": execution.stderr_lines[-lines:],
            "total_stdout": len(execution.stdout_lines),
            "total_stderr": len(execution.stderr_lines)
        }

    def _capture_output(self, agent_name: str, proc: subprocess.Popen):
        """Capture stdout/stderr from process (runs in thread)."""
        execution = self.executions[agent_name]

        # Capture stdout
        for line in proc.stdout:
            execution.stdout_lines.append(line.rstrip())

        # Capture stderr
        for line in proc.stderr:
            execution.stderr_lines.append(line.rstrip())

        # Wait for process to complete
        proc.wait()

        # Update execution record
        execution.status = "completed" if proc.returncode == 0 else "failed"
        execution.end_time = datetime.now().isoformat()
        execution.exit_code = proc.returncode

        self._save_execution(agent_name)

    def _save_execution(self, agent_name: str):
        """Save execution metadata to disk."""
        if agent_name not in self.executions:
            return

        execution = self.executions[agent_name]

        # Create session directory
        session_dir = self.runs_dir / self.session_id
        session_dir.mkdir(exist_ok=True, parents=True)

        # Save execution JSON
        execution_file = session_dir / f"{agent_name}.json"
        execution_file.write_text(
            json.dumps(execution.to_dict(), indent=2),
            encoding='utf-8'
        )


# Global singleton
_runner = None


def get_runner() -> AgentRunner:
    """Get or create the global agent runner instance."""
    global _runner
    if _runner is None:
        _runner = AgentRunner()
    return _runner
