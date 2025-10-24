#!/usr/bin/env python3
"""
Test script for Phase 2 Sub-Agent implementations.

Validates that all sub-agents (ExplorerAgent, HistorianAgent, CriticAgent,
ResearchDocumenter) can be instantiated and executed successfully.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.base_agent import AgentContext
from agents.explorer.explorer import ExplorerAgent
from agents.historian.historian import HistorianAgent
from agents.critic.critic import CriticAgent
from agents.research_documenter.research_documenter import ResearchDocumenter


def test_explorer_agent():
    """Test ExplorerAgent instantiation and execution."""
    print("\n" + "="*70)
    print("🔍 Testing ExplorerAgent")
    print("="*70)

    try:
        agent = ExplorerAgent()
        print(f"✅ Agent created: {agent.name}")
        print(f"   Dependencies: {agent.dependencies}")

        # Test with minimal context
        context = AgentContext(
            session_id="test_session",
            inputs={
                'task_description': 'Find agent classes in the codebase',
                'target_directory': '.',
                'file_patterns': ['*.py']
            }
        )

        result = agent.execute(context)
        print(f"✅ Execution completed")
        print(f"   Decision: {result.decision}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Summary: {result.data_for_next_agent.get('summary', 'N/A')}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_historian_agent():
    """Test HistorianAgent instantiation and execution."""
    print("\n" + "="*70)
    print("📚 Testing HistorianAgent")
    print("="*70)

    try:
        agent = HistorianAgent()
        print(f"✅ Agent created: {agent.name}")
        print(f"   Dependencies: {agent.dependencies}")

        # Test with minimal context
        context = AgentContext(
            session_id="test_session",
            inputs={
                'project_id': 'test_project',
                'session_id': 'test_session',
                'project_root': '.',
                'rationale': 'Testing Phase 2 sub-agent implementation'
            }
        )

        result = agent.execute(context)
        print(f"✅ Execution completed")
        print(f"   Decision: {result.decision}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Files changed: {len(result.data_for_next_agent.get('files_changed', []))}")
        print(f"   Risks identified: {len(result.data_for_next_agent.get('open_risks', []))}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_critic_agent():
    """Test CriticAgent instantiation and execution."""
    print("\n" + "="*70)
    print("🔎 Testing CriticAgent")
    print("="*70)

    try:
        agent = CriticAgent()
        print(f"✅ Agent created: {agent.name}")
        print(f"   Dependencies: {agent.dependencies}")

        # Test with sample code review
        context = AgentContext(
            session_id="test_session",
            inputs={
                'plan': 'Implement user authentication with password hashing',
                'code_diff': '''
                def authenticate(username, password):
                    query = f"SELECT * FROM users WHERE username='{username}'"
                    result = db.execute(query)
                    return result
                ''',
                'change_type': 'security'
            }
        )

        result = agent.execute(context)
        print(f"✅ Execution completed")
        print(f"   Decision: {result.decision}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Risks found: {len(result.data_for_next_agent.get('risks', []))}")
        print(f"   Recommendation: {result.data_for_next_agent.get('overall_recommendation', 'N/A')}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_research_documenter():
    """Test ResearchDocumenter instantiation and execution."""
    print("\n" + "="*70)
    print("📖 Testing ResearchDocumenter")
    print("="*70)

    try:
        agent = ResearchDocumenter()
        print(f"✅ Agent created: {agent.name}")
        print(f"   Dependencies: {agent.dependencies}")

        # Test with sample research request
        context = AgentContext(
            session_id="test_session",
            inputs={
                'topic': 'FastAPI',
                'library_name': 'fastapi',
                'use_case': 'REST API development',
                'language': 'python'
            }
        )

        result = agent.execute(context)
        print(f"✅ Execution completed")
        print(f"   Decision: {result.decision}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Pitfalls found: {len(result.data_for_next_agent.get('pitfalls', []))}")
        print(f"   Plan steps: {len(result.data_for_next_agent.get('implementation_plan', []))}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all sub-agent tests."""
    print("\n" + "="*70)
    print("🧪 PHASE 2 SUB-AGENT TESTS")
    print("="*70)

    results = {
        'ExplorerAgent': test_explorer_agent(),
        'HistorianAgent': test_historian_agent(),
        'CriticAgent': test_critic_agent(),
        'ResearchDocumenter': test_research_documenter(),
    }

    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for agent_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{agent_name:25} {status}")

    print("\n" + "-"*70)
    print(f"Total: {passed}/{total} tests passed")
    print("="*70 + "\n")

    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
