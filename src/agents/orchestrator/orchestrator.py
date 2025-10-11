# ==============================================
# orchestrator.py
# Phase 1.5: Management-Team-Ready Orchestrator
# ==============================================
"""
Modular Orchestrator for Management Team System
------------------------------------------------
Coordinates Planning Agent and Research Agent with support
for future plug-ins (Strategy, Technical Architect, Documentation).

🎯 Goal:
Implement a modular Orchestrator that coordinates existing agents
while supporting future plugins without refactoring.

Success Criteria:
✅ Runs end-to-end with current Planning & Research Agents
✅ Handles missing (inactive) agents gracefully
✅ Writes full session summary & log
✅ Code structure allows future agents to plug in without refactor
"""

import importlib
import yaml
import json
import logging
import datetime
import pathlib
from typing import Dict, Any, List, Optional
from jinja2 import Template


class Orchestrator:
    """
    Plugin-based orchestrator that dynamically loads and coordinates agents
    from a YAML registry configuration.
    """
    
    def __init__(self, registry_path: str = "./src/agents/orchestrator/agent_registry.yaml"):
        """
        Initialize the orchestrator.
        
        Args:
            registry_path: Path to agent_registry.yaml file
        """
        self.registry_path = pathlib.Path(registry_path)
        self.log_path = pathlib.Path("./logs/orchestrator.log")
        self.results: Dict[str, Any] = {}
        self.session_id = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.logger = self._init_logger()
        self.registry_config: Dict[str, Any] = {}
        self.agents: List[Any] = []
        
        # Initialize
        self.logger.info(f"🚀 Orchestrator session started: {self.session_id}")
        self._load_registry()
        self._load_agents()
    
    def _init_logger(self) -> logging.Logger:
        """
        Initialize logging system.
        
        Returns:
            Configured logger instance
        """
        # Ensure log directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            filename=self.log_path,
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
            filemode='a'
        )
        
        logger = logging.getLogger("Orchestrator")
        logger.info("=" * 70)
        logger.info(f"New session: {self.session_id}")
        logger.info("=" * 70)
        
        return logger
    
    def _load_registry(self):
        """Load agent registry configuration from YAML."""
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Agent registry not found: {self.registry_path}")
        
        with open(self.registry_path, 'r') as f:
            self.registry_config = yaml.safe_load(f)
        
        total_agents = len(self.registry_config.get('agents', []))
        self.logger.info(f"📋 Registry loaded: {total_agents} agents defined")
        print(f"📋 Registry loaded: {total_agents} agents defined")
    
    def _load_agents(self) -> List[Any]:
        """
        Dynamically load active agents from registry.
        
        Returns:
            List of instantiated agent objects
        """
        agents_config = self.registry_config.get('agents', [])
        
        # Sort by stage number
        agents_config = sorted(agents_config, key=lambda x: x.get('stage', 999))
        
        loaded_agents = []
        
        for agent_def in agents_config:
            name = agent_def['name']
            path = agent_def['path']
            is_active = agent_def.get('active', False)
            stage = agent_def.get('stage', '?')
            
            if not is_active:
                self.logger.info(f"⏭️  Stage {stage}: {name} - inactive (skipping)")
                print(f"⏭️  Stage {stage}: {name} - inactive")
                continue
            
            try:
                # Parse module path and class name
                # Format: "module.path:ClassName"
                module_path, class_name = path.rsplit(':', 1)
                
                # Dynamically import module
                module = importlib.import_module(module_path)
                
                # Get class from module
                agent_class = getattr(module, class_name)
                
                # Instantiate agent
                agent_instance = agent_class()
                loaded_agents.append(agent_instance)
                
                self.logger.info(f"✅ Stage {stage}: {name} - loaded successfully")
                print(f"✅ Stage {stage}: {name} - loaded")
                
            except ModuleNotFoundError as e:
                self.logger.warning(f"⚠️  Stage {stage}: {name} - module not found: {e}")
                print(f"⚠️  Stage {stage}: {name} - not found (will skip)")
                
            except AttributeError as e:
                self.logger.warning(f"⚠️  Stage {stage}: {name} - class not found: {e}")
                print(f"⚠️  Stage {stage}: {name} - class not found")
                
            except Exception as e:
                self.logger.error(f"❌ Stage {stage}: {name} - load error: {e}")
                print(f"❌ Stage {stage}: {name} - error: {e}")
        
        self.agents = loaded_agents
        self.logger.info(f"📦 Total agents loaded: {len(self.agents)}")
        print(f"\n📦 Active agents: {len(self.agents)}/{len(agents_config)}\n")
        
        return loaded_agents
    
    def run_cycle(self) -> Dict[str, Any]:
        """
        Execute orchestration cycle through all active agents.
        
        Returns:
            Dictionary containing results from all agents
        """
        self.log_event("🔄 Orchestration cycle start")
        print("=" * 70)
        print("🔄 STARTING ORCHESTRATION CYCLE")
        print("=" * 70 + "\n")
        
        for agent in self.agents:
            name = agent.__class__.__name__
            
            self.log_event(f"▶️  Starting {name}")
            print(f"▶️  {name}...")
            
            try:
                # Try different execution methods based on agent type
                if hasattr(agent, 'run_cycle'):
                    result = agent.run_cycle()
                elif hasattr(agent, 'run'):
                    result = agent.run()
                elif hasattr(agent, 'search'):
                    # Research agent - provide default query
                    topic = "best practices for AI project management and orchestration"
                    result = agent.search(topic, focus="research")
                elif hasattr(agent, 'execute'):
                    result = agent.execute()
                else:
                    raise NotImplementedError(f"{name} has no recognized execution method")
                
                self.results[name] = result
                self.log_event(f"✅ {name} complete")
                print(f"   ✅ Complete\n")
                
            except NotImplementedError as e:
                self.log_event(f"⏭️  {name} skipped — {e}")
                print(f"   ⏭️  Skipped: {e}\n")
                self.results[name] = {"status": "skipped", "reason": str(e)}
                
            except Exception as e:
                self.log_event(f"❌ {name} failed: {e}")
                print(f"   ❌ Failed: {e}\n")
                self.results[name] = {"status": "error", "error": str(e)}
                
                # Check if we should stop on error
                orchestration_config = self.registry_config.get('orchestration', {})
                if orchestration_config.get('stop_on_error', False):
                    self.logger.error("🛑 Stopping orchestration due to error")
                    raise
        
        # Write session summary
        self._write_summary()
        self.log_event("✅ Orchestration cycle complete")
        
        print("=" * 70)
        print("✅ ORCHESTRATION CYCLE COMPLETE")
        print("=" * 70 + "\n")
        
        return self.results
    
    def _write_summary(self):
        """Generate session summary using Jinja2 template."""
        summary_path = pathlib.Path(f"./outputs/orchestrator_session_{self.session_id}.md")
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load template
        template_path = pathlib.Path(__file__).parent / "templates" / "session_summary_template.md"
        
        if template_path.exists():
            with open(template_path, 'r') as f:
                template_content = f.read()
            template = Template(template_content)
        else:
            # Fallback to basic template
            self.logger.warning(f"⚠️  Template not found: {template_path}, using fallback")
            template = Template(self._get_fallback_template())
        
        # Prepare data for template
        agents_data = []
        for agent_name, result in self.results.items():
            if isinstance(result, dict):
                status = result.get('status', 'success')
                if status == 'skipped':
                    status_icon = '⏭️  Skipped'
                    message = result.get('reason', 'Not implemented')
                elif status == 'error':
                    status_icon = '❌ Error'
                    message = result.get('error', 'Unknown error')
                else:
                    status_icon = '✅ Success'
                    message = f"{len(result)} result fields"
            else:
                status_icon = '✅ Success'
                message = 'Completed'
            
            agents_data.append({
                'name': agent_name,
                'status': status_icon,
                'message': message
            })
        
        # Calculate metrics
        successful_count = sum(1 for r in self.results.values() 
                              if isinstance(r, dict) and r.get('status') not in ['error', 'skipped'])
        skipped_count = sum(1 for r in self.results.values() 
                           if isinstance(r, dict) and r.get('status') == 'skipped')
        error_count = sum(1 for r in self.results.values() 
                         if isinstance(r, dict) and r.get('status') == 'error')
        
        # Generate combined results summary
        combined_results = self._generate_combined_results()
        
        # Render template
        rendered = template.render(
            session_id=self.session_id,
            timestamp=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            phase="1.5 - Management-Team-Ready",
            total_agents=len(self.agents),
            agents=agents_data,
            combined_results=combined_results,
            outputs=[],  # Can be populated later
            duration="N/A",  # Can calculate if tracking start time
            successful_count=successful_count,
            skipped_count=skipped_count,
            error_count=error_count,
            orchestrator_version="2.1",
            log_path=str(self.log_path),
            registry_path=str(self.registry_path)
        )
        
        # Write summary
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
        
        self.log_event(f"📄 Summary written: {summary_path}")
        print(f"📄 Summary written: {summary_path}")
        
        return summary_path
    
    def _generate_combined_results(self) -> str:
        """Generate combined results text from all agents."""
        lines = []
        
        for agent_name, result in self.results.items():
            if isinstance(result, dict) and result.get('status') not in ['error', 'skipped']:
                lines.append(f"**{agent_name}:**")
                
                # Show summary if available
                if 'summary' in result:
                    summary_text = result['summary'][:500]
                    lines.append(f"{summary_text}...\n")
                else:
                    lines.append(f"Completed successfully\n")
        
        return '\n'.join(lines) if lines else "No results to display"
    
    def _get_fallback_template(self) -> str:
        """Fallback template if Jinja2 template not found."""
        return """# Session Summary — {{session_id}}

**Generated:** {{timestamp}}

## Agent Results
{% for agent in agents %}
- {{agent.name}}: {{agent.status}}
{% endfor %}

**Log:** {{log_path}}
"""
    
    def log_event(self, message: str):
        """
        Log an event with timestamp.
        
        Args:
            message: Event description
        """
        self.logger.info(message)
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get orchestration results.
        
        Returns:
            Dictionary of results from all agents
        """
        return self.results
    
    def get_active_agents(self) -> List[str]:
        """
        Get list of active agent names.
        
        Returns:
            List of active agent class names
        """
        return [agent.__class__.__name__ for agent in self.agents]


# ==============================================
# Main Execution
# ==============================================
if __name__ == "__main__":
    """
    Test the orchestrator with current active agents.
    """
    print("\n" + "=" * 70)
    print("🎭 ORCHESTRATOR v2.1 - PHASE 1.5")
    print("Management-Team-Ready with Plugin Architecture")
    print("=" * 70)
    print("\nFeatures:")
    print("  • YAML-based agent registry")
    print("  • Dynamic agent loading")
    print("  • Graceful degradation (inactive agents skipped)")
    print("  • Comprehensive logging")
    print("  • Automatic session summaries")
    print("  • Future-proof plugin architecture")
    print("\n" + "=" * 70 + "\n")
    
    try:
        # Create and run orchestrator
        orchestrator = Orchestrator()
        
        print(f"🎯 Active Agents: {', '.join(orchestrator.get_active_agents())}\n")
        
        # Run orchestration cycle
        results = orchestrator.run_cycle()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 SESSION SUMMARY")
        print("=" * 70)
        
        successful = sum(1 for r in results.values() 
                        if isinstance(r, dict) and r.get('status') != 'error' and r.get('status') != 'skipped')
        skipped = sum(1 for r in results.values() 
                     if isinstance(r, dict) and r.get('status') == 'skipped')
        errors = sum(1 for r in results.values() 
                    if isinstance(r, dict) and r.get('status') == 'error')
        
        print(f"\n✅ Successful: {successful}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"❌ Errors: {errors}")
        print(f"\n📁 Check outputs/ for detailed summary")
        print(f"📁 Check logs/orchestrator.log for audit trail")
        print("\n" + "=" * 70 + "\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Ensure agent_registry.yaml exists at:")
        print(f"   {pathlib.Path('./src/agents/orchestrator/agent_registry.yaml').absolute()}\n")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
