#!/usr/bin/env python3
"""
Test script for subagent system integration.

Tests all 4 agents:
1. ExplorerAgent - File mapping
2. HistorianAgent - Project snapshots
3. CriticAgent - Security review
4. ResearchDocumenter - API research

Usage:
    python scripts/test_subagent_system.py

Expected: All agents execute successfully and create artifacts.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.explorer_agent import ExplorerAgent
from core.historian_agent import HistorianAgent
from core.critic_agent import CriticAgent
from core.research_documenter import ResearchDocumenter
from core.subagent_coordinator import SubAgentCoordinator
from core.subagent_triggers import SubAgentTriggerEngine


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def test_explorer_agent():
    """Test ExplorerAgent file mapping."""
    print_header("TEST 1: ExplorerAgent (File Mapping)")

    agent = ExplorerAgent()

    result = agent.explore({
        'task_description': 'Test file mapping for agent implementations',
        'files_to_modify': [
            'core/explorer_agent.py',
            'core/historian_agent.py',
            'core/critic_agent.py'
        ],
        'search_terms': ['agent', 'subagent']
    })

    assert result['success'], "ExplorerAgent failed"
    assert len(result['file_map']) >= 3, "Should map at least 3 files"
    assert Path(result['artifact_path']).exists(), "Artifact should exist"

    print(f"✅ ExplorerAgent test passed!")
    print(f"   Files mapped: {len(result['file_map'])}")
    print(f"   Artifact: {result['artifact_path']}")
    print(f"   Summary: {result['summary'][:100]}...")

    return result


def test_historian_agent():
    """Test HistorianAgent snapshot creation."""
    print_header("TEST 2: HistorianAgent (Project Snapshots)")

    agent = HistorianAgent()

    result = agent.create_snapshot({
        'session_summary': 'Subagent system implementation complete',
        'modified_files': [
            'core/explorer_agent.py',
            'core/historian_agent.py',
            'core/critic_agent.py',
            'core/research_documenter.py'
        ],
        'modified_loc': 600,
        'milestone_reached': True,
        'rationale': 'Implemented all 4 subagent classes and integrated with coordinator',
        'next_steps': [
            'Test integration with interactive_orchestrator',
            'Verify auto-triggering works correctly',
            'Document in .claude/rules.md'
        ],
        'open_risks': [
            'Agent implementations need real-world testing',
            'ResearchDocumenter currently uses templates (needs WebFetch integration)'
        ]
    })

    assert result['success'], "HistorianAgent failed"
    assert result['project_snapshot_updated'], "PROJECT_SNAPSHOT.md should be updated"
    assert Path(result['snapshot_path']).exists(), "Checkpoint should exist"
    assert Path('PROJECT_SNAPSHOT.md').exists(), "PROJECT_SNAPSHOT.md should exist"

    print(f"✅ HistorianAgent test passed!")
    print(f"   Checkpoint: {result['snapshot_path']}")
    print(f"   Summary: {result['summary']}")

    return result


def test_critic_agent():
    """Test CriticAgent security review."""
    print_header("TEST 3: CriticAgent (Security Review)")

    agent = CriticAgent()

    result = agent.review({
        'change_type': 'security',
        'description': 'Implement JWT authentication for API',
        'files': ['core/auth.py', 'core/middleware.py', 'tests/test_auth.py'],
        'complexity': 'high',
        'confidence': 0.7
    })

    assert result['success'], "CriticAgent failed"
    assert len(result['risks']) > 0, "Should identify risks"
    assert result['recommendation'] in ['proceed', 'revise', 'stop'], "Should make recommendation"

    print(f"✅ CriticAgent test passed!")
    print(f"   Risks identified: {result['risk_count']}")
    print(f"   Recommendation: {result['recommendation'].upper()}")
    print(f"   Rationale: {result['recommendation_rationale']}")

    # Show top 3 risks
    print(f"\n   Top 3 Risks:")
    for risk in result['risks'][:3]:
        print(f"   - {risk['title']} ({risk['severity']})")

    return result


def test_research_documenter():
    """Test ResearchDocumenter API research."""
    print_header("TEST 4: ResearchDocumenter (API Research)")

    agent = ResearchDocumenter()

    result = agent.research({
        'topic': 'stripe',
        'research_focus': 'payment processing and webhooks'
    })

    assert result['success'], "ResearchDocumenter failed"
    assert 'implementation_brief' in result, "Should return implementation brief"
    assert Path(result['artifact_path']).exists(), "Research artifact should exist"

    brief = result['implementation_brief']
    assert len(brief['capabilities']) > 0, "Should list capabilities"
    assert len(brief['constraints']) > 0, "Should list constraints"
    assert len(brief['common_pitfalls']) > 0, "Should list pitfalls"
    assert len(brief['integration_plan']) == 5, "Should have 5-step plan"

    print(f"✅ ResearchDocumenter test passed!")
    print(f"   Topic: {brief['topic']}")
    print(f"   Capabilities: {len(brief['capabilities'])}")
    print(f"   Pitfalls: {len(brief['common_pitfalls'])}")
    print(f"   Artifact: {result['artifact_path']}")

    return result


def test_coordinator_integration():
    """Test SubAgentCoordinator integration."""
    print_header("TEST 5: SubAgentCoordinator (Integration)")

    coordinator = SubAgentCoordinator(
        project_id="test_project",
        session_id="test_session",
        verbose=True
    )

    # Test silent agent (ExplorerAgent)
    print("\n🔍 Testing silent agent execution (ExplorerAgent)...")
    result1 = coordinator.execute_agent(
        agent_name='ExplorerAgent',
        agent_context={
            'task_description': 'Test coordinator integration',
            'files_to_modify': ['core/subagent_coordinator.py']
        }
    )

    assert result1['success'], "Coordinator ExplorerAgent execution failed"
    print(f"   ✓ ExplorerAgent via coordinator: {result1['summary'][:60]}...")

    # Test silent agent (HistorianAgent)
    print("\n📸 Testing silent agent execution (HistorianAgent)...")
    result2 = coordinator.execute_agent(
        agent_name='HistorianAgent',
        agent_context={
            'session_summary': 'Test snapshot via coordinator',
            'modified_loc': 50
        }
    )

    assert result2['success'], "Coordinator HistorianAgent execution failed"
    print(f"   ✓ HistorianAgent via coordinator: {result2['summary'][:60]}...")

    print(f"\n✅ SubAgentCoordinator test passed!")
    print(f"   Agents available: ExplorerAgent, HistorianAgent, CriticAgent, ResearchDocumenter")
    print(f"   Silent agents work: ✓")

    return True


def test_trigger_engine():
    """Test SubAgentTriggerEngine decision logic."""
    print_header("TEST 6: SubAgentTriggerEngine (Auto-Triggering)")

    engine = SubAgentTriggerEngine()

    # Test Explorer triggers
    print("\n🔍 Testing Explorer triggers...")
    context1 = {
        'files_to_modify': ['file1.py', 'file2.py', 'file3.py'],
        'estimated_loc': 200,
        'complexity': 'high'
    }

    decision1 = engine.should_invoke_explorer(context1)
    assert decision1.should_trigger, "Should trigger on 3+ files"
    print(f"   ✓ Explorer trigger: {decision1.reason}")

    # Test Historian triggers
    print("\n📸 Testing Historian triggers...")
    context2 = {
        'modified_loc': 180,
        'at_end_of_block': True
    }

    decision2 = engine.should_invoke_historian(context2)
    assert decision2.should_trigger, "Should trigger on end of block + high LOC"
    print(f"   ✓ Historian trigger: {decision2.reason}")

    # Test Critic triggers
    print("\n🔍 Testing Critic triggers...")
    context3 = {
        'change_type': 'security',
        'security_impact': True,
        'affects_auth': True
    }

    decision3 = engine.should_invoke_critic(context3)
    assert decision3.should_trigger, "Should trigger on auth changes"
    print(f"   ✓ Critic trigger: {decision3.reason}")

    # Test Research triggers
    print("\n📚 Testing Research triggers...")
    context4 = {
        'library_name': 'stripe',
        'confidence': 0.5
    }

    decision4 = engine.should_invoke_research(context4)
    assert decision4.should_trigger, "Should trigger on external library + low confidence"
    print(f"   ✓ Research trigger: {decision4.reason}")

    print(f"\n✅ SubAgentTriggerEngine test passed!")
    print(f"   All trigger conditions work correctly")

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  SUBAGENT SYSTEM INTEGRATION TEST SUITE")
    print("=" * 70)

    results = {}

    try:
        # Test individual agents
        results['explorer'] = test_explorer_agent()
        results['historian'] = test_historian_agent()
        results['critic'] = test_critic_agent()
        results['research'] = test_research_documenter()

        # Test infrastructure
        results['coordinator'] = test_coordinator_integration()
        results['triggers'] = test_trigger_engine()

        # Summary
        print("\n" + "=" * 70)
        print("  TEST SUMMARY")
        print("=" * 70 + "\n")

        print("✅ All tests passed!\n")
        print("Components tested:")
        print("  1. ExplorerAgent - File mapping ✓")
        print("  2. HistorianAgent - Project snapshots ✓")
        print("  3. CriticAgent - Security review ✓")
        print("  4. ResearchDocumenter - API research ✓")
        print("  5. SubAgentCoordinator - Integration ✓")
        print("  6. SubAgentTriggerEngine - Auto-triggers ✓")

        print(f"\nArtifacts created:")
        print(f"  - {Path('.history/explorer').absolute()}")
        print(f"  - {Path('.history/checkpoints').absolute()}")
        print(f"  - {Path('.history/research').absolute()}")
        print(f"  - {Path('PROJECT_SNAPSHOT.md').absolute()}")

        print("\n" + "=" * 70)
        print("  🎉 SUBAGENT SYSTEM IS FULLY OPERATIONAL!")
        print("=" * 70 + "\n")

        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
