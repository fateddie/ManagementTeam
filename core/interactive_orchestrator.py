"""
Interactive Orchestrator - Conversational gated workflow for idea validation.

Conducts natural conversation to refine ideas, gather requirements, and guide
users through research phases with educational context and soft validation.
"""

import sys
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

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
from core.subagent_triggers import SubAgentTriggerEngine  # Phase 4
from core.ai_conversation_handler import AIConversationHandler  # AI Conversations
from core.idea_critic import IdeaCritic  # AI Critique & Grammar Correction
from core.keyword_generator import KeywordGenerator  # Enhanced Pain Discovery
from core.pain_discovery_analyzer import PainDiscoveryAnalyzer  # Enhanced Pain Discovery
from core.competitive_analyzer import CompetitiveAnalyzer  # Enhanced Competitive Analysis


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
        # Track if this is a new project (before super().__init__ assigns ID)
        is_new_project = (project_id is None)

        super().__init__(project_id=project_id)

        self.mode = mode
        self.auto_save = auto_save

        # Prompt for project name if new project
        project_name = None
        if is_new_project:
            print("\n🆕 Starting new idea workflow\n")
            name_input = input("What would you like to call this project?\n(Leave blank for auto-name): ").strip()
            if name_input:
                project_name = name_input
                print(f"\n✅ Project: \"{project_name}\"")
                print(f"   ID: {self.project_id}\n")

        # Ensure project exists in database (fixes FOREIGN KEY constraint errors)
        if self.context_tracker and is_new_project:
            # New project - create it in database with specific ID
            try:
                existing_project = self.context_tracker.get_project(self.project_id)
                if not existing_project:
                    # Use project_name if provided, otherwise use default
                    db_name = project_name or f"Idea Validation - {self.session_id}"
                    created_id = self.context_tracker.create_project(
                        name=db_name,
                        description="Interactive workflow project",
                        priority="medium",
                        project_id=self.project_id  # Use the ID orchestrator assigned
                    )
                    if created_id:
                        logger.info(f"✅ Created project in database: {created_id}")
                    else:
                        logger.warning(f"Failed to create project {self.project_id}")
            except Exception as e:
                logger.warning(f"Could not create project in database: {e}")

        self.workflow_state = WorkflowState(
            project_id=self.project_id,
            session_id=self.session_id,
            auto_save=auto_save,
            project_name=project_name
        )

        # Initialize SubAgentCoordinator
        self.subagent_coordinator = SubAgentCoordinator(
            project_id=self.project_id,
            session_id=self.session_id,
            verbose=True
        )

        # Phase 4: Initialize TriggerEngine for auto-invocation
        self.trigger_engine = SubAgentTriggerEngine(enabled=True)

        # AI Conversations: Initialize AI handler with graceful fallback
        self.ai_handler = AIConversationHandler()
        self.use_ai = self.ai_handler.is_available()
        if self.use_ai:
            logger.info("✅ AI-powered conversations enabled")
        else:
            logger.info("ℹ️  Using script-based conversations (AI unavailable)")

        # AI Critique: Initialize idea critic
        self.idea_critic = IdeaCritic()
        if self.idea_critic.is_available():
            logger.info("✅ AI-powered critique enabled")
        else:
            logger.info("ℹ️  Using basic critique (AI unavailable)")

        # Enhanced Pain Discovery: Initialize keyword generator and analyzer
        self.keyword_generator = KeywordGenerator()
        self.pain_analyzer = PainDiscoveryAnalyzer()
        if self.keyword_generator.is_available():
            logger.info("✅ Enhanced pain discovery enabled")
            print("✅ AI keyword generation enabled")
        else:
            logger.warning("⚠️ AI keyword generation unavailable - will use fallback")
            print("⚠️ AI keyword generation unavailable - will use fallback keywords")

        # Enhanced Competitive Analysis: Initialize competitive analyzer
        self.competitive_analyzer = CompetitiveAnalyzer()
        if self.competitive_analyzer.is_available():
            logger.info("✅ Enhanced competitive analysis enabled")

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

            # Phase 4: Check for auto-trigger conditions after step completion
            self._check_and_invoke_subagents(step_name, collected, completion)

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
            # Handle optional fields with clearer context
            if field_config.get('optional'):
                # Show conversation starters if available
                starters = field_config.get('conversation_starters', [])
                if starters:
                    for starter in starters:
                        print(f"\n💡 {starter}")

                choice = input(f"\n{field_config['prompt']}\n(Press Enter to skip): ").strip()
                if not choice:
                    continue
                collected[field_name] = choice
                self.workflow_state.save_field(field_name, choice)
            else:
                # Ask the question conversationally for required fields
                value = self._ask_conversational(field_name, field_config, collected)
                collected[field_name] = value
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
        Ask a question conversationally - routes to AI or script-based.

        Returns:
            User's answer
        """
        # Try AI-powered conversation first (if available)
        if self.use_ai:
            try:
                return self._ask_conversational_ai(field_name, field_config, context)
            except Exception as e:
                logger.warning(f"AI conversation failed, falling back: {e}")
                # Fall through to script-based

        # Fallback: Script-based conversation
        return self._ask_conversational_scripted(field_name, field_config, context)

    def _ask_conversational_ai(self, field_name: str, field_config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        AI-powered conversational question asking.

        Uses OpenAI to:
        - Detect meta-responses
        - Generate contextual follow-ups
        - Provide intelligent suggestions
        """
        # Get question
        starters = field_config.get('conversation_starters', [])
        prompt = field_config.get('prompt')
        question = starters[0] if starters else prompt

        print(f"\n{question}")

        # Get user input
        user_answer = input("→ ").strip()

        # AI analyzes response
        analysis = self.ai_handler.analyze_response(
            question=question,
            user_answer=user_answer,
            field_name=field_name,
            context=context
        )

        # Handle meta-response (user asking for help vs answering)
        if analysis.get('is_meta_response', False):
            print(f"\n{analysis.get('acknowledgment', 'I understand.')}")
            print("\nLet's start with the basics. What problem are you trying to solve?")
            user_answer = input("→ ").strip()

            # Re-analyze the actual answer
            analysis = self.ai_handler.analyze_response(
                question="What problem are you trying to solve?",
                user_answer=user_answer,
                field_name=field_name,
                context=context
            )

        # If quality is low, offer intelligent follow-up
        quality_score = analysis.get('quality_score', 50)
        if quality_score < 70:
            suggested_followup = analysis.get('suggested_follow_up', '')
            if suggested_followup:
                print(f"\n💡 {suggested_followup}")
                refine = input("Want to add more detail? (y/N): ").strip().lower()
                if refine == 'y':
                    additional = input("→ ").strip()
                    user_answer = f"{user_answer} {additional}"

        # Warn about contradictions
        coherence = analysis.get('coherence_check', {})
        if coherence.get('contradictions'):
            print(f"\n⚠️ I noticed: {coherence['contradictions'][0]}")
            print("Would you like to clarify?")

        return user_answer

    def _ask_conversational_scripted(self, field_name: str, field_config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Script-based conversational question asking (fallback).

        Original implementation - uses pre-defined prompts and simple validation.
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
        Show summary of collected data with AI critique, then get approval to proceed.

        NEW: Includes spelling/grammar correction and critique (strengths/weaknesses/suggestions)

        Returns:
            True if approved, False if user wants to pause/refine
        """
        # Get AI critique if available
        critique = None
        if self.idea_critic.is_available():
            print("\n🤔 Analyzing your idea...")
            try:
                critique = self.idea_critic.critique_idea(
                    collected_data=collected,
                    quality_score=completion['score']
                )
            except Exception as e:
                logger.error(f"Critique failed: {e}")

        # Show critique if available
        if critique:
            critique_display = self.idea_critic.format_critique_display(critique)
            print(critique_display)
        else:
            # Fallback: Show basic summary
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
        print("  2) Skip this step (not recommended)")
        print("  3) Save & exit")
        print()

        choice = input("Choice [1-3]: ").strip()

        if choice == '1':
            return True
        elif choice == '2':
            confirm = input("\n⚠️  Skip this step? Data may be incomplete. Confirm (y/N): ").strip().lower()
            return confirm == 'y'
        elif choice == '3':
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
            # Route to enhanced analyzers for Step 2 and Step 4
            if step_name == 'step_2_pain_discovery' and self.keyword_generator.is_available():
                # Enhanced Pain Discovery
                keywords = collected.get('research_keywords', [])
                geography = collected.get('research_geography', 'Ireland/UK')

                if keywords:
                    self._execute_enhanced_pain_discovery(keywords, collected, geography)
                    print(f"\n✅ Enhanced pain discovery complete!\n")
                else:
                    print("\n⚠️  No keywords available - skipping enhanced analysis")

            elif step_name == 'step_4_competitive_landscape' and self.competitive_analyzer.is_available():
                # Enhanced Competitive Analysis
                geography = collected.get('research_geography', 'Ireland/UK')
                self._execute_enhanced_competitive_analysis(collected, geography)
                print(f"\n✅ Enhanced competitive analysis complete!\n")

            else:
                # Fallback to original agent-based research
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
                    'phase_1': 'TrendResearchAgent',  # Pain Discovery (fallback)
                    'phase_2': 'StrategyAgent',        # Market Sizing
                    'phase_3': 'StrategyAgent'         # Competitive Analysis (fallback)
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
        """Explain what Pain Discovery research will do, with keyword generation."""
        target = collected.get('target_customer', 'your target customers')
        core_idea = collected.get('core_idea', 'this problem')

        print("📍 **What I'll research:**")
        print(f"   • Reddit discussions where {target} talk about {core_idea}")
        print(f"   • X/Twitter conversations about this pain point")
        print(f"   • Google Trends data and search patterns")
        print()
        print("🎯 **What I'll find:**")
        print("   • Real pain points in their own words")
        print("   • How frequently this problem comes up")
        print("   • Willingness-to-pay signals (pricing discussions)")
        print("   • Urgency indicators (how badly people need this)")
        print("   • Top complaints and concerns")

        # Generate and edit keywords if generator available
        if self.keyword_generator.is_available():
            geography = collected.get('geography', 'Ireland/UK')
            keywords = self._generate_and_edit_keywords(collected, geography)
            collected['research_keywords'] = keywords  # Save for later use
            collected['research_geography'] = geography
        else:
            print("\n⚠️  AI keyword generation unavailable - will use manual keywords")

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

    def _generate_and_edit_keywords(
        self,
        collected: Dict[str, Any],
        geography: str = "Ireland/UK"
    ) -> List[str]:
        """
        Generate keywords with AI and allow user to edit.

        Returns:
            Final list of keywords to use for research
        """
        print("\n🤖 Generating research keywords based on your idea...")

        # Generate keywords
        keyword_data = self.keyword_generator.generate_keywords(
            refinement_data=collected,
            geography=geography
        )

        # Display generated keywords
        display_text = self.keyword_generator.format_for_display(keyword_data)
        print(display_text)

        # User options
        print(f"\n{'─'*70}")
        print("What would you like to do?")
        print("  1) Use all suggested keywords")
        print("  2) Add more keywords")
        print("  3) Remove some keywords")
        print("  4) Start over with manual keywords")
        print()

        choice = input("Choice [1-4]: ").strip()

        # Extract all keywords into flat list
        all_keywords = []
        keywords_by_category = keyword_data.get('keywords_by_category', {})
        for category, keyword_list in keywords_by_category.items():
            for kw_obj in keyword_list:
                all_keywords.append(kw_obj.get('keyword', ''))

        if choice == '1':
            # Use all
            final_keywords = all_keywords
            print(f"\n✅ Using all {len(final_keywords)} keywords")

        elif choice == '2':
            # Add more
            final_keywords = all_keywords.copy()
            print("\nEnter additional keywords (one per line, press Enter twice when done):")
            while True:
                kw = input("→ ").strip()
                if not kw:
                    break
                final_keywords.append(kw)
                print(f"  ✓ Added: {kw}")

            print(f"\n✅ Using {len(final_keywords)} keywords total")

        elif choice == '3':
            # Remove some
            print("\n📋 Current keywords:")
            for i, kw in enumerate(all_keywords, 1):
                print(f"  {i}. {kw}")

            print("\nEnter numbers to remove (comma-separated, e.g., '2,5,7'):")
            to_remove = input("→ ").strip()

            if to_remove:
                try:
                    indices = [int(x.strip()) - 1 for x in to_remove.split(',')]
                    final_keywords = [kw for i, kw in enumerate(all_keywords) if i not in indices]
                    print(f"\n✅ Removed {len(indices)} keywords, {len(final_keywords)} remaining")
                except (ValueError, IndexError):
                    print("\n⚠️  Invalid input, using all keywords")
                    final_keywords = all_keywords
            else:
                final_keywords = all_keywords

        else:
            # Manual entry
            print("\nEnter your keywords (one per line, press Enter twice when done):")
            final_keywords = []
            while True:
                kw = input("→ ").strip()
                if not kw:
                    break
                final_keywords.append(kw)
                print(f"  ✓ Added: {kw}")

        return final_keywords

    def _display_enriched_insights(self, enriched: Dict[str, Any]):
        """
        Display enriched insights with FULL TRANSPARENCY.

        Shows:
        - Source post IDs for verification
        - Confidence levels
        - Example quotes
        - Commands to view source data
        """
        print("\n" + "="*80)
        print("📊 ENRICHED INSIGHTS - ICP, Features, Competitors, Pricing")
        print("="*80)

        # ICP
        icp = enriched.get("icp", {})
        if icp:
            print(f"\n🎯 IDEAL CUSTOMER PROFILE (Overall Confidence: {icp.get('confidence', 0)}%)")

            top_industries = icp.get("top_industries", [])[:3]
            if top_industries:
                print("\n✨ Top Industries:")
                for i, ind in enumerate(top_industries, 1):
                    conf_badge = self._get_confidence_badge(ind.get('confidence', 'unknown'))
                    print(f"\n   {i}. {ind['industry'].title()}: {ind['count']} posts ({ind['percentage']}%) {conf_badge}")
                    print(f"      Avg Urgency: {ind.get('avg_urgency', 'unknown').upper()}")

                    # Show source IDs
                    source_ids = ind.get('source_posts', [])
                    if source_ids:
                        print(f"      Source Posts: {source_ids[:5]}{'...' if len(source_ids) > 5 else ''}")

                    # Show example quote
                    examples = ind.get('example_quotes', [])
                    if examples:
                        print(f"      Example: \"{examples[0][:100]}...\"")

            company_sizes = icp.get("top_company_sizes", [])
            if company_sizes:
                print("\n🏢 Company Sizes:")
                for size in company_sizes:
                    conf_badge = self._get_confidence_badge(size.get('confidence', 'unknown'))
                    print(f"   • {size['size'].title()}: {size['count']} posts ({size['percentage']}%) {conf_badge}")

            urgency = icp.get("urgency_profile", {})
            if urgency:
                print("\n⚡ Urgency Profile:")
                for urg, data in sorted(urgency.items(), key=lambda x: x[1]['count'], reverse=True)[:3]:
                    print(f"   • {urg.upper()}: {data['count']} posts ({data['percentage']}%)")

        # Feature Priorities
        features = enriched.get("feature_priorities", [])[:5]
        if features:
            print(f"\n🔧 TOP REQUESTED FEATURES:")
            for i, feat in enumerate(features, 1):
                conf_badge = self._get_confidence_badge(feat.get('confidence', 'unknown'))
                print(f"\n   {i}. {feat['feature']}: {feat['mentions']} mentions ({feat['percentage']}%) {conf_badge}")

                # Show source IDs
                source_ids = feat.get('source_posts', [])
                if source_ids:
                    print(f"      Source Posts: {source_ids[:5]}{'...' if len(source_ids) > 5 else ''}")

                # Show example quote
                examples = feat.get('example_quotes', [])
                if examples and len(examples) > 0:
                    print(f"      Example: \"{examples[0][:100]}...\"")

        # Pricing
        pricing = enriched.get("pricing_signals", {})
        if pricing:
            print(f"\n💰 PRICING INTELLIGENCE:")
            print(f"   • Budget concerns: {pricing.get('budget_concern_percentage', 0)}% of posts")
            if pricing.get("price_examples"):
                print(f"   • Price examples: {', '.join(pricing['price_examples'][:3])}")

        # Competitors
        competitors = enriched.get("competitor_intelligence", {})
        if competitors and competitors.get("top_competitors"):
            print(f"\n⚔️  TOP COMPETITORS MENTIONED:")
            for comp in competitors['top_competitors'][:5]:
                print(f"   • {comp['name']}: {comp['mentions']} mentions")

        # Top Pain Quote
        top_quotes = enriched.get("top_pain_quotes_ranked", [])
        if top_quotes:
            print(f"\n🔥 TOP VALIDATED PAIN QUOTE:")
            top = top_quotes[0]
            print(f"   [{top['subreddit']}] {top['upvotes']} upvotes | {top['urgency'].upper()} urgency")
            print(f"   Industry: {top.get('industry', 'Unknown')}")
            print(f"   \"{top['text'][:200]}...\"")

        print("\n" + "="*80)
        print("📂 DATA ACCESS:")
        print("   • Full data: social_posts_enriched.csv")
        print("   • JSON report: demand_validation_report.json")
        print("   • Evidence report: python -c \"from src.analysis.demand_validator import DemandValidator; DemandValidator().export_evidence_report()\"")
        print("="*80)

    def _get_confidence_badge(self, confidence: str) -> str:
        """Get visual badge for confidence level."""
        badges = {
            "high": "🟢 HIGH",
            "medium": "🟡 MEDIUM",
            "low": "🟠 LOW",
            "insufficient": "🔴 INSUFFICIENT"
        }
        return badges.get(confidence.lower(), "⚪ UNKNOWN")

    def _execute_enhanced_pain_discovery(
        self,
        keywords: List[str],
        collected: Dict[str, Any],
        geography: str
    ):
        """
        Execute enhanced pain discovery with rich analysis and validation gates.

        Args:
            keywords: Research keywords
            collected: Refinement data
            geography: Geographic focus
        """
        print(f"\n🔍 Starting pain discovery research...")
        print(f"   Keywords: {len(keywords)}")
        print(f"   Geography: {geography}")
        print(f"\n{'─'*70}\n")

        # VALIDATION GATE 1: Test Reddit credentials
        print("📋 Step 1: Testing Reddit API credentials...")
        try:
            import subprocess
            result = subprocess.run(
                ["python", "tests/test_reddit_credentials.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                print("⚠️  Reddit credentials test failed.")
                print("   Data collection will continue but may have limited results.")
                print(f"   Error: {result.stdout}")
        except Exception as e:
            print(f"⚠️  Could not test credentials: {e}")
            print("   Continuing anyway...")

        print()

        try:
            # Run pain discovery analysis (uses V2 collector by default)
            print("📊 Step 2: Collecting social media data...")
            analysis_results = self.pain_analyzer.analyze_pain_discovery(
                keywords=keywords,
                refinement_data=collected,
                geography=geography,
                use_v2=True  # Use improved v2 collector
            )

            # VALIDATION GATE 2: Validate collection results
            print("\n📋 Step 3: Validating data quality...")
            try:
                from tests.validate_collector_output import validate_collector_output
                validation_results = validate_collector_output("social_posts.csv")

                # Check quality gates
                total_posts = validation_results.get('total_posts', 0)
                weak_keywords = len(validation_results.get('weak_keywords', []))
                success = validation_results.get('success', False)

                if not success or total_posts < 50:
                    print(f"\n⚠️  WARNING: Data collection below threshold")
                    print(f"   Total posts: {total_posts} (target: 100+)")
                    print(f"   Weak keywords: {weak_keywords}")

                    retry = input("\nRetry with fallback keywords? (y/N): ").strip().lower()
                    if retry == 'y':
                        print("\n🔄 Retrying with proven fallback keywords...")
                        # Use fallback keywords from keyword generator
                        from core.keyword_generator import KeywordGenerator
                        fallback_keywords = KeywordGenerator.FALLBACK_KEYWORDS

                        analysis_results = self.pain_analyzer.analyze_pain_discovery(
                            keywords=fallback_keywords,
                            refinement_data=collected,
                            geography=geography,
                            use_v2=True
                        )

                        # Re-validate
                        validation_results = validate_collector_output("social_posts.csv")
                        print(f"\n✅ Retry complete: {validation_results.get('total_posts', 0)} posts collected")

            except Exception as e:
                print(f"⚠️  Validation check failed: {e}")
                print("   Continuing with collected data...")

            print()

            # Display results
            display_text = self.pain_analyzer.format_for_display(analysis_results)
            print(display_text)

            # Display enriched insights if available
            if 'enriched_analysis' in analysis_results:
                self._display_enriched_insights(analysis_results['enriched_analysis'])

            # Save results to workflow state
            self.workflow_state.save_field('pain_discovery_results', analysis_results)

            # Record as artifact if context tracker available
            if self.context_tracker:
                try:
                    self.context_tracker.record_note(
                        self.project_id,
                        note_type="pain_discovery",
                        content=f"Pain Discovery Analysis Complete",
                        metadata=analysis_results
                    )
                except Exception as e:
                    logger.warning(f"Could not record pain discovery artifact: {e}")

        except Exception as e:
            logger.error(f"Pain discovery analysis failed: {e}", exc_info=True)
            print(f"\n❌ Research failed: {e}")
            print("Continuing without enhanced analysis...")

    def _execute_enhanced_competitive_analysis(
        self,
        collected: Dict[str, Any],
        geography: str
    ):
        """
        Execute enhanced competitive analysis.

        Args:
            collected: Refinement data (includes known_competitors if provided)
            geography: Geographic focus
        """
        print(f"\n⚔️  Starting competitive analysis...")
        print(f"   Geography: {geography}")
        print(f"\n{'─'*70}\n")

        try:
            # Extract known competitors if provided
            known_competitors = collected.get('known_competitors', '')
            competitor_list = None
            if known_competitors:
                # Parse comma-separated list
                competitor_list = [c.strip() for c in known_competitors.split(',') if c.strip()]

            # Run competitive analysis
            analysis_results = self.competitive_analyzer.analyze_competitors(
                refinement_data=collected,
                known_competitors=competitor_list,
                geography=geography
            )

            # Display results
            display_text = self.competitive_analyzer.format_for_display(analysis_results)
            print(display_text)

            # Save results to workflow state
            self.workflow_state.save_field('competitive_analysis_results', analysis_results)

            # Record as artifact if context tracker available
            if self.context_tracker:
                try:
                    self.context_tracker.record_note(
                        self.project_id,
                        note_type="competitive_analysis",
                        content=f"Competitive Analysis Complete",
                        metadata=analysis_results
                    )
                except Exception as e:
                    logger.warning(f"Could not record competitive analysis artifact: {e}")

        except Exception as e:
            logger.error(f"Competitive analysis failed: {e}", exc_info=True)
            print(f"\n❌ Analysis failed: {e}")
            print("Continuing without enhanced analysis...")

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

    def _check_and_invoke_subagents(self, step_name: str, collected: Dict[str, Any], completion: Dict[str, Any]):
        """
        Phase 4: Check trigger conditions and auto-invoke sub-agents.

        Args:
            step_name: Current workflow step
            collected: Collected requirements
            completion: Step completion data

        WHY: Proactively assist without blocking flow
        """
        # Build context for trigger evaluation
        trigger_context = {
            # General context
            'step_name': step_name,
            'completion_score': completion.get('score', 0.8),
            'confidence': completion.get('score', 0.8),

            # Explorer triggers
            'files_to_modify': [],  # Would be populated in real workflow
            'estimated_loc': len(str(collected)) // 5,  # Rough estimate
            'complexity': 'medium',

            # Historian triggers
            'at_end_of_block': False,  # Set True at natural breakpoints
            'prd_changed': False,
            'milestone_reached': step_name == 'step_4_competitive_landscape',  # Last step
            'modified_loc': 0,

            # Critic triggers
            'change_type': 'workflow_step',
            'security_impact': False,
            'affects_auth': False,
            'affects_payments': False,

            # Research triggers
            'library_name': None,
            'api_name': None,
            'unfamiliar_tech': False
        }

        # Evaluate triggers
        triggered_agents = self.trigger_engine.get_triggered_agents(trigger_context)

        if not triggered_agents:
            return  # No triggers

        # Show which agents were triggered
        print(f"\n{'─'*60}")
        print("🤖 Auto-Trigger: Sub-agents detected helpful opportunities")
        print(f"{'─'*60}\n")

        for agent_name in triggered_agents:
            decision = self.trigger_engine.evaluate_all_triggers(trigger_context)[agent_name]

            # Log the decision
            print(f"✓ {agent_name}: {decision.reason}")

        # Invoke triggered agents based on mode
        for agent_name in triggered_agents:
            # Silent agents run automatically
            if agent_name in self.subagent_coordinator.SILENT_AGENTS:
                print(f"\n🔄 Running {agent_name} silently...")
                try:
                    self.subagent_coordinator.execute_agent(agent_name, trigger_context)
                except Exception as e:
                    print(f"⚠️ {agent_name} execution failed: {e}")

            # Interactive agents require approval
            elif agent_name in self.subagent_coordinator.INTERACTIVE_AGENTS:
                decision = self.trigger_engine.evaluate_all_triggers(trigger_context)[agent_name]
                print(f"\n💡 Suggestion: Run {agent_name}")
                print(f"   Reason: {decision.reason}")
                print(f"   Confidence: {decision.confidence:.0%}")

                choice = input(f"\nRun {agent_name}? (y/N): ").strip().lower()
                if choice == 'y':
                    print(f"🚀 Executing {agent_name}...")
                    try:
                        self.subagent_coordinator.execute_agent(agent_name, trigger_context)
                    except Exception as e:
                        print(f"⚠️ {agent_name} execution failed: {e}")
                else:
                    print(f"✓ Skipped {agent_name}")

        print()  # Spacing

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
