"""
Interactive Orchestrator - Conversational gated workflow for idea validation.

Conducts natural conversation to refine ideas, gather requirements, and guide
users through research phases with educational context and soft validation.
"""

import sys
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

# Import base orchestrator
sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.orchestrator.orchestrator import Orchestrator

# Import workflow components
from core.workflow_gates import (
    WORKFLOW_STEPS,
    get_step_order,
    get_step_config,
    validate_field,
    calculate_step_completion,
    format_confidence_bar
)
from core.workflow_state import WorkflowState
from core.subagent_coordinator import SubAgentCoordinator


class InteractiveOrchestrator(Orchestrator):
    """
    Extends base Orchestrator with conversational gated workflow.

    Two modes:
    1. Guided Mode: Natural conversation with options and follow-ups
    2. Expert Mode: Quick input of all fields at once
    """

    def __init__(self, project_id: str = None, mode: str = "guided", auto_save: bool = True):
        """
        Initialize interactive orchestrator.

        Args:
            project_id: Existing project ID to resume, or None for new
            mode: "guided" or "expert"
            auto_save: Enable auto-save after each field
        """
        super().__init__(project_id=project_id)

        self.mode = mode
        self.auto_save = auto_save
        self.workflow_state = WorkflowState(
            project_id=self.project_id,
            session_id=self.session_id,
            auto_save=auto_save
        )

        # Initialize SubAgentCoordinator
        self.subagent_coordinator = SubAgentCoordinator(
            project_id=self.project_id,
            session_id=self.session_id,
            verbose=True
        )

        print(f"\n{'='*60}")
        print(f"🚀 Interactive Workflow - {mode.upper()} MODE")
        print(f"{'='*60}\n")

    def run_workflow(self):
        """
        Main entry point for conversational workflow.

        Returns to command line between steps for user control.
        """
        # Welcome message
        self._print_welcome()

        # Get workflow steps
        steps = get_step_order()

        # Process each step
        for step_name in steps:
            step_config = get_step_config(step_name)

            # Skip if already completed (unless user wants to redo)
            if self.workflow_state.is_step_completed(step_name):
                print(f"\n✅ {step_config['name']} already completed")
                choice = input("Redo this step? (y/N): ").strip().lower()
                if choice != 'y':
                    continue

            # Mark step as started
            self.workflow_state.start_step(step_name)

            # Show education
            self._show_education(step_config)

            # Collect requirements based on mode
            if self.mode == "guided":
                collected = self._collect_requirements_guided(step_config)
            else:
                collected = self._collect_requirements_expert(step_config)

            # Calculate completion
            completion = calculate_step_completion(step_config, collected)

            # Show summary and get approval
            approved = self._show_summary_and_approve(step_config, collected, completion)

            if not approved:
                print("\n⏸️  Paused. Run again to continue from here.")
                return

            # Complete step
            summary = self._format_summary(step_config, collected)
            self.workflow_state.complete_step(step_name, completion['score'], summary)

            # Auto-trigger research if configured
            if step_config.get('auto_trigger'):
                self._run_research_phase(step_name, collected)

        # All steps complete!
        print("\n🎉 Workflow Complete!")
        self._print_final_summary()

    def _print_welcome(self):
        """Print welcome message."""
        print("Hey! I'm here to help you explore and validate your idea.")
        print("\nWe'll have a conversation to understand:")
        print("  • What you're building")
        print("  • Who it's for")
        print("  • Why it matters")
        print("\nThen I'll research real pain points, market size, and competition.")
        print("\nLet's get started!\n")

    def _show_education(self, step_config: Dict[str, Any]):
        """Show educational context for a step."""
        print(f"\n{'─'*60}")
        print(f"📍 {step_config['name']}")
        print(f"{'─'*60}")
        print(step_config['education'])
        print()

    def _collect_requirements_guided(self, step_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Guided mode: Conversational Q&A with options and follow-ups.

        Returns:
            Dictionary of collected field values
        """
        requirements = step_config.get('requirements', {})
        collected = {}

        for field_name, field_config in requirements.items():
            # Skip optional fields if user doesn't want them
            if field_config.get('optional'):
                choice = input(f"\n{field_config['prompt']} (optional, press Enter to skip): ").strip()
                if not choice:
                    continue

            # Ask the question conversationally
            value = self._ask_conversational(field_name, field_config, collected)
            collected[field_name] = value

            # Save field immediately (auto-save)
            self.workflow_state.save_field(field_name, value)

            # Ask follow-up questions if needed
            follow_ups = field_config.get('follow_ups', {})
            for followup_name, followup_config in follow_ups.items():
                # Check if this follow-up should trigger
                if self._should_trigger_followup(followup_config, value, collected):
                    followup_value = self._ask_conversational(followup_name, followup_config, collected)
                    collected[followup_name] = followup_value
                    self.workflow_state.save_field(followup_name, followup_value)

        return collected

    def _ask_conversational(self, field_name: str, field_config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Ask a question conversationally with optional suggestions.

        Returns:
            User's answer
        """
        # Use conversation starters if available
        starters = field_config.get('conversation_starters', [])
        prompt = field_config.get('prompt')

        if starters:
            # Pick a random starter (or first one for consistency)
            print(f"\n{starters[0]}")
        else:
            print(f"\n{prompt}")

        # Show options if available
        options = field_config.get('options', [])
        if options:
            print("\nHere are some options (or describe in your own words):")
            for i, option in enumerate(options, 1):
                print(f"  {i}) {option}")
            print()

        # Get user input
        if options:
            response = input("Your choice (number or custom answer): ").strip()

            # Check if they chose a number
            if response.isdigit():
                idx = int(response) - 1
                if 0 <= idx < len(options):
                    value = options[idx]
                    print(f"✓ {value}")
                else:
                    value = response
            else:
                value = response
        else:
            value = input("→ ").strip()

        # Validate and provide gentle suggestions
        validation = validate_field(field_config, value, context)

        if validation['suggestions']:
            print(f"\n💡 {validation['suggestions'][0]}")
            refine = input("Want to add more detail? (y/N): ").strip().lower()
            if refine == 'y':
                additional = input("→ ").strip()
                value = f"{value} {additional}"

        return value

    def _should_trigger_followup(self, followup_config: Dict[str, Any], value: str, context: Dict[str, Any]) -> bool:
        """Determine if a follow-up question should be asked."""
        triggers = followup_config.get('triggers', [])

        if 'always' in triggers:
            return True

        # Add more trigger logic as needed
        if 'selected_business' in triggers:
            business_keywords = ['business', 'company', 'enterprise', 'small', 'mid', 'large']
            return any(kw in value.lower() for kw in business_keywords)

        if 'has_role' in triggers:
            return 'specific_role' in context or 'role' in value.lower()

        if 'has_deadline' in triggers:
            deadline_keywords = ['month', 'quarter', 'year', 'soon', 'asap']
            return any(kw in value.lower() for kw in deadline_keywords)

        return False

    def _collect_requirements_expert(self, step_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expert mode: Fast input of all fields at once.

        Returns:
            Dictionary of collected field values
        """
        requirements = step_config.get('requirements', {})
        collected = {}

        print("\n🚀 Expert Mode: Fill all fields")
        print("─" * 40)

        for field_name, field_config in requirements.items():
            if field_config.get('optional'):
                print(f"\n{field_config['prompt']} (optional)")
            else:
                print(f"\n{field_config['prompt']} *")

            value = input("→ ").strip()

            if value or not field_config.get('optional'):
                collected[field_name] = value

        # Save all at once
        self.workflow_state.save_requirements(collected)

        return collected

    def _show_summary_and_approve(self, step_config: Dict[str, Any], collected: Dict[str, Any], completion: Dict[str, Any]) -> bool:
        """
        Show summary of collected data and get approval to proceed.

        Returns:
            True if approved, False if user wants to pause/refine
        """
        print(f"\n{'='*60}")
        print("📋 SUMMARY")
        print(f"{'='*60}\n")

        # Show collected data
        for field_name, value in collected.items():
            print(f"• {field_name.replace('_', ' ').title()}: {value}")

        # Show confidence
        confidence_bar = format_confidence_bar(completion['score'])
        print(f"\n{confidence_bar} {completion['score']*100:.0f}% Confidence")

        # Show warnings or encouragement
        if completion['warnings']:
            for warning in completion['warnings']:
                print(warning)
        if completion['encouragement']:
            print(completion['encouragement'])

        # Get approval
        print(f"\n{'─'*60}")
        print("What would you like to do?")
        print("  1) Continue - looks good!")
        print("  2) Refine - I want to add more detail")
        print("  3) Skip this step (not recommended)")
        print("  4) Save & exit")
        print()

        choice = input("Choice [1-4]: ").strip()

        if choice == '1':
            return True
        elif choice == '2':
            # TODO: Allow refinement
            print("\n(Refinement not yet implemented - continuing)")
            return True
        elif choice == '3':
            confirm = input("\n⚠️  Skip this step? Data may be incomplete. Confirm (y/N): ").strip().lower()
            return confirm == 'y'
        elif choice == '4':
            return False
        else:
            return True

    def _format_summary(self, step_config: Dict[str, Any], collected: Dict[str, Any]) -> str:
        """Format collected data as summary string."""
        summary_lines = []
        for field_name, value in collected.items():
            summary_lines.append(f"{field_name}: {value}")
        return "; ".join(summary_lines)

    def _run_research_phase(self, step_name: str, collected: Dict[str, Any]):
        """
        Auto-trigger research agents for this step with context gathering and clarification.

        Args:
            step_name: Current step
            collected: Collected requirements
        """
        print(f"\n{'='*60}")
        print("🔍 RESEARCH PHASE")
        print(f"{'='*60}\n")

        # Map steps to agent phases and descriptions
        phase_map = {
            'step_2_pain_discovery': {
                'phase': 'phase_1',
                'name': 'Pain Discovery',
                'description': 'Search for real conversations about this problem'
            },
            'step_3_market_sizing': {
                'phase': 'phase_2',
                'name': 'Market Sizing',
                'description': 'Research market size, growth, and trends'
            },
            'step_4_competitive_landscape': {
                'phase': 'phase_3',
                'name': 'Competitive Analysis',
                'description': 'Find competitors and alternative solutions'
            }
        }

        phase_config = phase_map.get(step_name)
        if not phase_config:
            return

        # Build initial research plan
        query = self._build_research_query(collected)

        # Show research plan
        print(f"📋 **{phase_config['name']}**")
        print(f"   {phase_config['description']}\n")

        print("Based on what you've told me, here's my research plan:\n")

        # Explain what will be researched
        if step_name == 'step_2_pain_discovery':
            self._explain_pain_discovery_plan(collected)
        elif step_name == 'step_3_market_sizing':
            self._explain_market_sizing_plan(collected)
        elif step_name == 'step_4_competitive_landscape':
            self._explain_competitive_plan(collected)

        print(f"\n{'─'*60}")

        # Ask for additional context/commentary
        print("\n💬 Before I start researching...")
        print("\nIs there anything else I should know or consider?")
        print("(Examples: specific competitors, markets to avoid, keywords to use, etc.)")
        print()

        additional_context = input("Additional context (or press Enter to continue): ").strip()

        if additional_context:
            collected['additional_context'] = additional_context
            self.workflow_state.save_field('additional_context', additional_context)
            print("\n✓ Got it! I'll keep that in mind.")

        # Confirm research plan
        print(f"\n{'─'*60}")
        print("\nReady to start research?")
        print("  1) Yes, start researching")
        print("  2) Let me adjust the plan")
        print("  3) Skip research for now")
        print()

        choice = input("Choice [1-3]: ").strip()

        if choice == '2':
            print("\n📝 What would you like to adjust?")
            adjustments = input("→ ").strip()
            if adjustments:
                collected['research_adjustments'] = adjustments
                self.workflow_state.save_field('research_adjustments', adjustments)
                print("\n✓ I'll incorporate your feedback into the research.")

        elif choice == '3':
            print("\n⏸️  Research skipped. You can run it later with:")
            print(f"   python cli/manage.py run --project {self.project_id}")
            return

        # Final confirmation with clarified intent
        print(f"\n{'='*60}")
        print("🚀 STARTING RESEARCH")
        print(f"{'='*60}\n")

        self._summarize_research_intent(step_name, collected)

        print("\nThis will take a few minutes. I'll search for real data and come back with insights.\n")

        try:
            # Execute research using appropriate agents
            phase = phase_config['phase']

            # Create AgentContext with collected requirements
            from core.base_agent import AgentContext
            from core.cache import Cache

            research_context = AgentContext(
                session_id=self.session_id,
                inputs={
                    'research_query': query,
                    'collected_requirements': collected,
                    'step_name': step_name,
                    'project_id': self.project_id
                },
                cache=Cache(),
                shared_data={}
            )

            # Map phases to appropriate agents
            agent_map = {
                'phase_1': 'TrendResearchAgent',  # Pain Discovery
                'phase_2': 'StrategyAgent',        # Market Sizing
                'phase_3': 'StrategyAgent'         # Competitive Analysis
            }

            agent_name = agent_map.get(phase)

            if agent_name:
                # Load and execute the agent
                print(f"🔬 Executing {agent_name}...\n")

                # Import and instantiate the agent
                if agent_name == 'TrendResearchAgent':
                    from agents.trend_research_agent.trend_research_agent import TrendResearchAgent
                    agent = TrendResearchAgent()
                    # Add required inputs for TrendResearchAgent
                    research_context.inputs['platforms'] = ['reddit', 'youtube', 'twitter']
                elif agent_name == 'StrategyAgent':
                    from agents.strategy_agent.strategy_agent import StrategyAgent
                    agent = StrategyAgent()

                # Execute the agent
                if agent.validate_inputs(research_context):
                    result = agent.execute(research_context)

                    # Display results
                    print(f"\n{'='*60}")
                    print("📊 RESEARCH RESULTS")
                    print(f"{'='*60}\n")

                    if hasattr(result, 'summary'):
                        print(result.summary)

                    # Store results in workflow state
                    self.workflow_state.save_field(f'{step_name}_research_results', str(result))

                    print(f"\n✅ Research complete! Results saved.\n")

                    # Optional: Run CriticAgent for adversarial review
                    self._offer_critic_review(step_name, result, collected)
                else:
                    print(f"⚠️  Skipping research - agent validation failed")
            else:
                print(f"⚠️  No agent mapped for {phase}")

        except Exception as e:
            print(f"⚠️  Research failed: {e}")
            print("You can continue manually or retry later.")
            import traceback
            traceback.print_exc()

    def _explain_pain_discovery_plan(self, collected: Dict[str, Any]):
        """Explain what Pain Discovery research will do."""
        target = collected.get('target_customer', 'your target customers')
        core_idea = collected.get('core_idea', 'this problem')

        print("📍 **What I'll research:**")
        print(f"   • Reddit discussions where {target} talk about {core_idea}")
        print(f"   • X/Twitter conversations about this pain point")
        print(f"   • YouTube videos/comments from affected users")
        print()
        print("🎯 **What I'll find:**")
        print("   • Real pain points in their own words")
        print("   • How frequently this problem comes up")
        print("   • Current workarounds they're using")
        print("   • Emotional intensity (frustration level)")

    def _explain_market_sizing_plan(self, collected: Dict[str, Any]):
        """Explain what Market Sizing research will do."""
        target = collected.get('target_customer', 'your target market')
        geography = collected.get('geography', 'relevant markets')

        print("📍 **What I'll research:**")
        print(f"   • Total addressable market for {target}")
        print(f"   • Market growth trends and projections")
        print(f"   • Geographic breakdown ({geography})")
        print()
        print("🎯 **What I'll find:**")
        print("   • Market size estimates (TAM/SAM/SOM)")
        print("   • Year-over-year growth rates")
        print("   • Market maturity and saturation")
        print("   • Emerging trends and opportunities")

    def _explain_competitive_plan(self, collected: Dict[str, Any]):
        """Explain what Competitive Analysis research will do."""
        known_competitors = collected.get('known_competitors', '')
        value_prop = collected.get('value_proposition', 'your solution')

        print("📍 **What I'll research:**")
        if known_competitors:
            print(f"   • Deep dive on: {known_competitors}")
        print(f"   • Direct competitors offering similar solutions")
        print(f"   • Indirect competitors and alternative approaches")
        print(f"   • How {value_prop} compares")
        print()
        print("🎯 **What I'll find:**")
        print("   • Key players and market leaders")
        print("   • Their pricing, features, and positioning")
        print("   • Gaps in the market (white space)")
        print("   • Competitive advantages you can leverage")

    def _summarize_research_intent(self, step_name: str, collected: Dict[str, Any]):
        """Summarize what research will accomplish."""
        print("📊 **Research Summary:**")
        print()

        if step_name == 'step_2_pain_discovery':
            print("I'll search for real people discussing this problem to validate:")
            print("  ✓ The problem is real and widespread")
            print("  ✓ People care enough to complain about it")
            print("  ✓ Current solutions aren't working well")

        elif step_name == 'step_3_market_sizing':
            print("I'll research market data to understand:")
            print("  ✓ How big is the opportunity")
            print("  ✓ Is the market growing or shrinking")
            print("  ✓ What's the revenue potential")

        elif step_name == 'step_4_competitive_landscape':
            print("I'll analyze competitors to identify:")
            print("  ✓ Who you're competing against")
            print("  ✓ What they're doing well (and poorly)")
            print("  ✓ Where you can differentiate")

        if collected.get('additional_context'):
            print(f"\n💡 **Your guidance:** {collected['additional_context']}")

        if collected.get('research_adjustments'):
            print(f"\n📝 **Adjustments:** {collected['research_adjustments']}")

    def _build_research_query(self, collected: Dict[str, Any]) -> str:
        """Build research query from collected requirements."""
        parts = []

        if 'core_idea' in collected:
            parts.append(collected['core_idea'])
        if 'target_customer' in collected:
            parts.append(f"for {collected['target_customer']}")
        if 'value_proposition' in collected:
            parts.append(f"- {collected['value_proposition']}")

        return " ".join(parts)

    def _offer_critic_review(self, step_name: str, research_result: Any, collected: Dict[str, Any]):
        """
        Offer optional CriticAgent review of research results.

        Uses SubAgentCoordinator to run CriticAgent in interactive mode.
        """
        print(f"{'─'*60}")
        print("\n💭 Would you like an adversarial review of these research findings?")
        print("   The Critic Agent will identify potential risks, gaps, and blind spots.")
        print()

        choice = input("Run Critic Agent? (y/N): ").strip().lower()

        if choice == 'y':
            # Prepare context for CriticAgent
            critic_context = {
                'topic': step_name,
                'research_results': str(research_result),
                'collected_requirements': collected,
                'project_id': self.project_id
            }

            # Use SubAgentCoordinator to execute CriticAgent
            critic_result = self.subagent_coordinator.execute_agent(
                agent_name='CriticAgent',
                agent_context=critic_context,
                agent_callable=None  # Will use placeholder until CriticAgent is implemented
            )

            # Store critic results if successful
            if critic_result.get('success'):
                self.workflow_state.save_field(f'{step_name}_critic_review', str(critic_result))
        else:
            print("✓ Skipping critic review\n")

    def _print_final_summary(self):
        """Print final workflow summary."""
        summary = self.workflow_state.export_summary()

        print(f"\n{'='*60}")
        print("🎯 WORKFLOW COMPLETE")
        print(f"{'='*60}\n")

        print(f"Project ID: {self.project_id}")
        print(f"Started: {summary['started']}")
        print(f"Completed Steps: {summary['progress']['completed']}/{summary['progress']['total_steps']}")
        print(f"\nAll data saved! You can:")
        print("  • View results in the dashboard")
        print("  • Run full pipeline: python cli/manage.py run")
        print("  • Continue research: python cli/interactive_workflow.py --resume")
        print()


def main():
    """Test interactive orchestrator."""
    orchestrator = InteractiveOrchestrator(mode="guided", auto_save=True)
    orchestrator.run_workflow()


if __name__ == "__main__":
    main()
