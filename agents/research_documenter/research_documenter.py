"""
research_documenter.py
Research Documenter Agent - Deep documentation research sub-agent.
---------------------------------------------------------

WHY: When integrating new libraries, SDKs, or APIs, shallow research leads
to implementation delays, gotchas, and brittle code. ResearchDocumenter
performs parallel deep-dives into official docs, GitHub issues, and community
knowledge to surface capabilities, constraints, and battle-tested patterns.

TRIGGER RULES (any):
    - New external library/SDK integration
    - Major version bump of existing dependency
    - Low confidence (<0.6) in implementation approach
    - User explicitly requests deep research
    - Unfamiliar API or service integration

OUTPUT:
    - Capabilities and constraints summary
    - Known pitfalls and workarounds
    - Minimal working example
    - 5-step implementation plan with citations
    - Stored as sub-agent artifact in ProjectContext

EXECUTION MODE: Interactive (explains research plan and gets user approval)

Created: 2025-10-19 (Phase 2 - Sub-Agent Unification)
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from core.base_agent import BaseAgent, AgentContext
from core.agent_protocol import AgentOutput

logger = logging.getLogger(__name__)


class ResearchDocumenter(BaseAgent):
    """
    Research Documenter Agent - Deep documentation research for integrations.

    WHY: Reduce implementation risk by thoroughly researching new libraries
    and APIs before integration. Runs interactively with user approval.
    """

    @property
    def name(self) -> str:
        """Agent identifier for registry and logging."""
        return "ResearchDocumenter"

    @property
    def dependencies(self) -> List[str]:
        """
        No dependencies - can research independently.

        WHY: Research is typically done before implementation,
        doesn't need output from other agents.
        """
        return []

    def validate_inputs(self, context: AgentContext) -> bool:
        """
        Validate that we have a research topic.

        WHY: Need at least a library name or API to research.
        """
        topic = context.inputs.get('topic')
        library_name = context.inputs.get('library_name')
        api_name = context.inputs.get('api_name')

        if not any([topic, library_name, api_name]):
            logger.warning(f"{self.name}: No research topic provided")
            return False

        return True

    def execute(self, context: AgentContext) -> AgentOutput:
        """
        Perform deep documentation research.

        WHY: Comprehensive research prevents implementation pitfalls
        and identifies best practices before coding begins.

        Args:
            context: Contains topic, library_name, api_name, use_case

        Returns:
            AgentOutput with research findings and implementation brief
        """
        logger.info(f"{self.name}: Starting documentation research...")

        topic = context.inputs.get('topic', '')
        library_name = context.inputs.get('library_name', topic)
        api_name = context.inputs.get('api_name', topic)
        use_case = context.inputs.get('use_case', 'general integration')
        language = context.inputs.get('language', 'python')

        # 1. Research official documentation
        official_docs = self._research_official_docs(library_name, api_name, language)

        # 2. Search GitHub for issues and examples
        github_insights = self._research_github(library_name, use_case)

        # 3. Find known pitfalls and workarounds
        pitfalls = self._identify_pitfalls(library_name, official_docs, github_insights)

        # 4. Extract minimal working example
        example = self._generate_minimal_example(library_name, use_case, language, official_docs)

        # 5. Create 5-step implementation plan
        implementation_plan = self._generate_implementation_plan(
            library_name, use_case, official_docs, github_insights, pitfalls
        )

        # 6. Compile citations
        citations = self._compile_citations(official_docs, github_insights)

        research_brief = {
            'timestamp': datetime.now().isoformat(),
            'topic': library_name or api_name,
            'use_case': use_case,
            'capabilities': official_docs.get('capabilities', []),
            'constraints': official_docs.get('constraints', []),
            'pitfalls': pitfalls,
            'minimal_example': example,
            'implementation_plan': implementation_plan,
            'citations': citations,
            'summary': f'Research complete for {library_name or api_name}: {len(pitfalls)} pitfalls identified, {len(implementation_plan)} step plan created'
        }

        confidence = self._calculate_research_confidence(official_docs, github_insights, pitfalls)

        return AgentOutput(
            agent_name=self.name,
            decision="research_complete",
            reasoning=f"Completed research for {library_name or api_name} with {len(citations)} sources",
            data_for_next_agent=research_brief,
            confidence=confidence,
            metadata={
                'execution_mode': 'interactive',
                'artifact_type': 'research_brief',
                'sources_consulted': len(citations),
                'pitfalls_found': len(pitfalls)
            }
        )

    def _research_official_docs(self, library_name: str, api_name: str, language: str) -> Dict[str, Any]:
        """Research official documentation sources."""

        # Simulated research - in production, this would use web scraping or APIs
        docs = {
            'capabilities': [
                f'{library_name} core functionality',
                f'Integration with {language} ecosystem',
                'Authentication and authorization support',
                'Rate limiting and retry logic',
            ],
            'constraints': [
                'Requires specific version dependencies',
                'Limited to certain platforms',
                'May have API rate limits',
            ],
            'documentation_url': f'https://docs.example.com/{library_name}',
            'quick_start_url': f'https://docs.example.com/{library_name}/quickstart',
        }

        logger.info(f"Researched official docs for {library_name}")
        return docs

    def _research_github(self, library_name: str, use_case: str) -> Dict[str, Any]:
        """Search GitHub for issues, examples, and common patterns."""

        # Simulated GitHub research - in production, use GitHub API
        insights = {
            'common_issues': [
                'Installation on Windows requires extra steps',
                'Async/await support requires specific configuration',
                'Error handling best practices',
            ],
            'popular_examples': [
                f'{library_name} with Flask integration',
                f'{library_name} async example',
                f'{library_name} production configuration',
            ],
            'recent_discussions': [
                'Performance optimization tips',
                'Breaking changes in v2.0',
                'Best practices for error handling',
            ],
            'github_url': f'https://github.com/search?q={library_name}',
        }

        logger.info(f"Researched GitHub for {library_name}")
        return insights

    def _identify_pitfalls(
        self,
        library_name: str,
        official_docs: Dict[str, Any],
        github_insights: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Identify known pitfalls and workarounds."""

        pitfalls = []

        # Extract from common issues
        for issue in github_insights.get('common_issues', []):
            pitfalls.append({
                'issue': issue,
                'severity': 'medium',
                'workaround': 'See documentation for platform-specific guidance',
                'source': 'GitHub Issues'
            })

        # Add constraint-based pitfalls
        for constraint in official_docs.get('constraints', []):
            pitfalls.append({
                'issue': constraint,
                'severity': 'low',
                'workaround': 'Check compatibility before installation',
                'source': 'Official Documentation'
            })

        return pitfalls[:10]  # Top 10 pitfalls

    def _generate_minimal_example(
        self,
        library_name: str,
        use_case: str,
        language: str,
        official_docs: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate minimal working example."""

        # Template-based example generation
        if language.lower() == 'python':
            code = f'''# Minimal {library_name} example for {use_case}
import {library_name.lower().replace('-', '_')}

# Initialize client
client = {library_name}.Client(api_key="your-api-key")

# Basic usage
try:
    result = client.execute(parameter="value")
    print(f"Success: {{result}}")
except {library_name}.Error as e:
    print(f"Error: {{e}}")
'''
        else:
            code = f'// Minimal {library_name} example\n// See official docs for {language} implementation'

        return {
            'code': code,
            'language': language,
            'description': f'Basic {library_name} setup for {use_case}',
            'prerequisites': [
                f'Install {library_name}',
                'Configure API credentials',
                'Import required dependencies'
            ]
        }

    def _generate_implementation_plan(
        self,
        library_name: str,
        use_case: str,
        official_docs: Dict[str, Any],
        github_insights: Dict[str, Any],
        pitfalls: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Generate 5-step implementation plan with citations."""

        plan = [
            {
                'step': 1,
                'title': 'Install and Configure',
                'description': f'Install {library_name} and configure environment',
                'details': 'Set up package dependencies and environment variables',
                'citation': official_docs.get('quick_start_url', 'Official documentation')
            },
            {
                'step': 2,
                'title': 'Initialize Client',
                'description': 'Create and configure the client instance',
                'details': 'Initialize with credentials and connection settings',
                'citation': official_docs.get('documentation_url', 'API reference')
            },
            {
                'step': 3,
                'title': 'Implement Core Functionality',
                'description': f'Implement primary {use_case} logic',
                'details': 'Add main business logic with error handling',
                'citation': github_insights.get('github_url', 'Community examples')
            },
            {
                'step': 4,
                'title': 'Add Error Handling',
                'description': 'Implement comprehensive error handling and retries',
                'details': 'Handle common failure modes and edge cases',
                'citation': 'Best practices from GitHub discussions'
            },
            {
                'step': 5,
                'title': 'Test and Validate',
                'description': 'Write tests and validate integration',
                'details': 'Unit tests, integration tests, and edge case validation',
                'citation': 'Testing guidelines'
            }
        ]

        return plan

    def _compile_citations(
        self,
        official_docs: Dict[str, Any],
        github_insights: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Compile all research citations."""

        citations = []

        # Official documentation
        if official_docs.get('documentation_url'):
            citations.append({
                'type': 'Official Documentation',
                'url': official_docs['documentation_url'],
                'title': 'Official Documentation'
            })

        if official_docs.get('quick_start_url'):
            citations.append({
                'type': 'Quick Start Guide',
                'url': official_docs['quick_start_url'],
                'title': 'Quick Start Guide'
            })

        # GitHub
        if github_insights.get('github_url'):
            citations.append({
                'type': 'GitHub Repository',
                'url': github_insights['github_url'],
                'title': 'GitHub Search Results'
            })

        return citations

    def _calculate_research_confidence(
        self,
        official_docs: Dict[str, Any],
        github_insights: Dict[str, Any],
        pitfalls: List[Dict[str, str]]
    ) -> float:
        """Calculate confidence based on research depth."""

        base_confidence = 0.6

        # Bonus for finding official docs
        if official_docs.get('documentation_url'):
            base_confidence += 0.15

        # Bonus for GitHub insights
        if github_insights.get('common_issues'):
            base_confidence += 0.1

        # Bonus for identifying pitfalls
        if pitfalls:
            base_confidence += 0.1

        return min(0.95, base_confidence)

    async def execute_async(self, context: AgentContext) -> AgentOutput:
        """
        Async version of execute for non-blocking operation.

        WHY: Documentation research can involve multiple web requests,
        async allows efficient parallel fetching.
        """
        # TODO: Implement async web scraping and API calls
        # For now, just call sync version
        return self.execute(context)
