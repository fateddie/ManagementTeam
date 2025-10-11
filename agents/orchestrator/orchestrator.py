"""
orchestrator.py
Phase 1.5 – Management-Team-Ready Orchestrator
"""

import importlib
import yaml
import json
import logging
from datetime import datetime
from pathlib import Path


class Orchestrator:
    """
    Plugin-based orchestrator that coordinates agents from YAML registry.
    
    Success Criteria:
    ✅ Executes Planning and Research Agents
    ✅ Skips missing/inactive agents gracefully
    ✅ Generates session summary and logs
    ✅ Supports future agent plugins without refactor
    """
    
    def __init__(self, registry_path="./agents/orchestrator/agent_registry.yaml"):
        """Initialize orchestrator with agent registry."""
        self.registry_path = registry_path
        self.log_path = "./logs/orchestrator.log"
        self.results = {}
        self.session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.logger = self._init_logger()
        self.agents = self._load_agents()

    def _init_logger(self):
        """Setup logging to file."""
        Path("logs").mkdir(exist_ok=True)
        logging.basicConfig(
            filename=self.log_path,
            level=logging.INFO,
            format="%(asctime)s | %(message)s"
        )
        logger = logging.getLogger("orchestrator")
        logger.info(f"Session start {self.session_id}")
        return logger

    def _load_agents(self):
        """Load active agents from registry."""
        with open(self.registry_path, "r") as f:
            registry = yaml.safe_load(f)
        
        agents = []
        for a in sorted(registry["agents"], key=lambda x: x["stage"]):
            if not a.get("active", False):
                self.logger.info(f"{a['name']} SKIPPED (inactive)")
                continue
            
            try:
                module_path, class_name = a["path"].split(":")
                module = importlib.import_module(module_path)
                cls = getattr(module, class_name)
                agents.append(cls())
                self.logger.info(f"{a['name']} loaded")
            except Exception as e:
                self.logger.error(f"Failed to load {a['name']}: {e}")
        
        return agents

    def run_cycle(self):
        """Execute all active agents in sequence."""
        self.logger.info("Cycle start")
        print(f"🔄 Starting orchestration cycle...\n")
        
        for agent in self.agents:
            name = agent.__class__.__name__
            self.logger.info(f"Running {name}")
            print(f"▶️  {name}...")
            
            try:
                # Try different execution methods based on agent type
                if hasattr(agent, 'run_cycle'):
                    result = agent.run_cycle()
                elif hasattr(agent, 'run'):
                    result = agent.run()
                elif hasattr(agent, 'search'):
                    # Research agent - provide a query
                    topic = "best practices for AI agent orchestration and project management"
                    result = agent.search(topic, focus="research")
                elif hasattr(agent, 'execute'):
                    result = agent.execute()
                else:
                    raise NotImplementedError(f"No recognized execution method")
                
                self.results[name] = result
                self.logger.info(f"{name} completed")
                print(f"   ✅ Complete\n")
                
            except NotImplementedError as e:
                self.logger.info(f"{name} SKIPPED – {e}")
                print(f"   ⏭️  Skipped: {e}\n")
                self.results[name] = {"status": "skipped", "reason": str(e)}
                
            except Exception as e:
                self.results[name] = {"error": str(e)}
                self.logger.error(f"{name} failed: {e}")
                print(f"   ❌ Failed: {e}\n")
        
        self._write_summary()
        self.logger.info("Cycle complete")

    def _write_summary(self):
        """Generate session summary from template."""
        Path("outputs").mkdir(exist_ok=True)
        
        template_path = Path("./agents/orchestrator/templates/session_summary_template.md")
        
        if template_path.exists():
            template = template_path.read_text()
        else:
            template = "# Session {{session_id}}\n\n{{combined_results}}\n"
        
        # Build agent table
        table_lines = []
        for name, v in self.results.items():
            status = 'OK' if 'error' not in str(v) else 'FAIL'
            error_msg = v.get('error', '–') if isinstance(v, dict) else '–'
            table_lines.append(f"| {name} | {status} | {error_msg} |")
        
        agent_table = "\n".join(table_lines)
        combined = json.dumps(self.results, indent=2)
        
        # Simple template replacement
        filled = template.replace("{{session_id}}", self.session_id) \
                        .replace("{{combined_results}}", combined) \
                        .replace("{{log_path}}", self.log_path) \
                        .replace("{% for agent in agents %}", "") \
                        .replace("{% endfor %}", "") \
                        .replace("{{agent_table}}", agent_table)
        
        # Remove any remaining template syntax
        import re
        filled = re.sub(r'\{\{[^}]+\}\}', '', filled)
        filled = re.sub(r'\{%[^%]+%\}', '', filled)
        
        out_path = Path(f"./outputs/session_summary_{self.session_id}.md")
        out_path.write_text(filled)
        
        self.logger.info(f"Summary written to {out_path}")
        print(f"✅ Summary saved: {out_path}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎭 ORCHESTRATOR v2.1 - PHASE 1.5")
    print("Management-Team-Ready with Plugin Architecture")
    print("=" * 70 + "\n")
    
    o = Orchestrator()
    o.run_cycle()
    
    print("\n" + "=" * 70)
    print("✅ PHASE 1.5 COMPLETE")
    print("=" * 70 + "\n")

