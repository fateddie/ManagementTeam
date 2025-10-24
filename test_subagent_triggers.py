#!/usr/bin/env python3
"""
Test script for Phase 4 Auto-Triggering System.

Tests SubAgentTriggerEngine decision logic and configuration loading.

WHAT THIS TESTS:
1. Configuration loading from YAML
2. Trigger rule evaluation for each agent
3. Threshold-based triggers
4. Confidence-based triggers
5. Pattern/keyword triggers
6. Metrics tracking
7. Enable/disable functionality

Created: 2025-10-19 (Phase 4 - Sub-Agent Unification)
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.subagent_triggers import SubAgentTriggerEngine, TriggerDecision


def test_explorer_triggers():
    """Test ExplorerAgent trigger conditions."""
    print("\n" + "="*70)
    print("🔍 Test 1: ExplorerAgent Triggers")
    print("="*70)

    try:
        engine = SubAgentTriggerEngine()

        # Test 1: File threshold trigger
        context = {
            'files_to_modify': ['file1.py', 'file2.py', 'file3.py'],
            'estimated_loc': 100
        }
        decision = engine.should_invoke_explorer(context)
        assert decision.should_trigger, "Should trigger on file threshold"
        print(f"✅ File threshold trigger: {decision.reason}")

        # Test 2: LOC threshold trigger
        context = {
            'files_to_modify': [],
            'estimated_loc': 200
        }
        decision = engine.should_invoke_explorer(context)
        assert decision.should_trigger, "Should trigger on LOC threshold"
        print(f"✅ LOC threshold trigger: {decision.reason}")

        # Test 3: High complexity trigger
        context = {
            'files_to_modify': [],
            'estimated_loc': 50,
            'complexity': 'high'
        }
        decision = engine.should_invoke_explorer(context)
        assert decision.should_trigger, "Should trigger on high complexity"
        print(f"✅ Complexity trigger: {decision.reason}")

        # Test 4: No trigger
        context = {
            'files_to_modify': [],
            'estimated_loc': 10,
            'complexity': 'low'
        }
        decision = engine.should_invoke_explorer(context)
        assert not decision.should_trigger, "Should not trigger"
        print(f"✅ No trigger: {decision.reason}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_historian_triggers():
    """Test HistorianAgent trigger conditions."""
    print("\n" + "="*70)
    print("📚 Test 2: HistorianAgent Triggers")
    print("="*70)

    try:
        engine = SubAgentTriggerEngine()

        # Test 1: End of block
        context = {
            'at_end_of_block': True
        }
        decision = engine.should_invoke_historian(context)
        assert decision.should_trigger, "Should trigger at end of block"
        print(f"✅ End of block trigger: {decision.reason}")

        # Test 2: PRD changed
        context = {
            'prd_changed': True
        }
        decision = engine.should_invoke_historian(context)
        assert decision.should_trigger, "Should trigger on PRD change"
        print(f"✅ PRD change trigger: {decision.reason}")

        # Test 3: LOC threshold
        context = {
            'modified_loc': 200
        }
        decision = engine.should_invoke_historian(context)
        assert decision.should_trigger, "Should trigger on LOC threshold"
        print(f"✅ LOC threshold trigger: {decision.reason}")

        # Test 4: Milestone
        context = {
            'milestone_reached': True
        }
        decision = engine.should_invoke_historian(context)
        assert decision.should_trigger, "Should trigger on milestone"
        print(f"✅ Milestone trigger: {decision.reason}")

        # Test 5: No trigger
        context = {
            'modified_loc': 10
        }
        decision = engine.should_invoke_historian(context)
        assert not decision.should_trigger, "Should not trigger"
        print(f"✅ No trigger: {decision.reason}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_critic_triggers():
    """Test CriticAgent trigger conditions."""
    print("\n" + "="*70)
    print("🔎 Test 3: CriticAgent Triggers")
    print("="*70)

    try:
        engine = SubAgentTriggerEngine()

        # Test 1: Security impact
        context = {
            'security_impact': True
        }
        decision = engine.should_invoke_critic(context)
        assert decision.should_trigger, "Should trigger on security impact"
        print(f"✅ Security trigger: {decision.reason}")

        # Test 2: Authentication changes
        context = {
            'affects_auth': True
        }
        decision = engine.should_invoke_critic(context)
        assert decision.should_trigger, "Should trigger on auth changes"
        print(f"✅ Auth trigger: {decision.reason}")

        # Test 3: Payment changes
        context = {
            'affects_payments': True
        }
        decision = engine.should_invoke_critic(context)
        assert decision.should_trigger, "Should trigger on payment changes"
        print(f"✅ Payment trigger: {decision.reason}")

        # Test 4: High complexity
        context = {
            'complexity': 'high'
        }
        decision = engine.should_invoke_critic(context)
        assert decision.should_trigger, "Should trigger on high complexity"
        print(f"✅ Complexity trigger: {decision.reason}")

        # Test 5: Low confidence
        context = {
            'confidence': 0.5
        }
        decision = engine.should_invoke_critic(context)
        assert decision.should_trigger, "Should trigger on low confidence"
        print(f"✅ Low confidence trigger: {decision.reason}")

        # Test 6: No trigger
        context = {
            'confidence': 0.9,
            'complexity': 'low'
        }
        decision = engine.should_invoke_critic(context)
        assert not decision.should_trigger, "Should not trigger"
        print(f"✅ No trigger: {decision.reason}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_research_triggers():
    """Test ResearchDocumenter trigger conditions."""
    print("\n" + "="*70)
    print("📖 Test 4: ResearchDocumenter Triggers")
    print("="*70)

    try:
        engine = SubAgentTriggerEngine()

        # Test 1: External library
        context = {
            'library_name': 'fastapi'
        }
        decision = engine.should_invoke_research(context)
        assert decision.should_trigger, "Should trigger on external library"
        print(f"✅ External library trigger: {decision.reason}")

        # Test 2: External API
        context = {
            'api_name': 'stripe'
        }
        decision = engine.should_invoke_research(context)
        assert decision.should_trigger, "Should trigger on external API"
        print(f"✅ External API trigger: {decision.reason}")

        # Test 3: Major version bump
        context = {
            'major_version_bump': True
        }
        decision = engine.should_invoke_research(context)
        assert decision.should_trigger, "Should trigger on version bump"
        print(f"✅ Version bump trigger: {decision.reason}")

        # Test 4: Low confidence
        context = {
            'confidence': 0.5
        }
        decision = engine.should_invoke_research(context)
        assert decision.should_trigger, "Should trigger on low confidence"
        print(f"✅ Low confidence trigger: {decision.reason}")

        # Test 5: Unfamiliar tech
        context = {
            'unfamiliar_tech': True
        }
        decision = engine.should_invoke_research(context)
        assert decision.should_trigger, "Should trigger on unfamiliar tech"
        print(f"✅ Unfamiliar tech trigger: {decision.reason}")

        # Test 6: No trigger
        context = {
            'confidence': 0.9
        }
        decision = engine.should_invoke_research(context)
        assert not decision.should_trigger, "Should not trigger"
        print(f"✅ No trigger: {decision.reason}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_evaluate_all_triggers():
    """Test evaluating all triggers at once."""
    print("\n" + "="*70)
    print("🎯 Test 5: Evaluate All Triggers")
    print("="*70)

    try:
        engine = SubAgentTriggerEngine()

        # Complex context that triggers multiple agents
        context = {
            # Explorer
            'files_to_modify': ['file1.py', 'file2.py', 'file3.py'],

            # Historian
            'at_end_of_block': True,

            # Critic
            'security_impact': True,

            # Research
            'library_name': 'oauth'
        }

        decisions = engine.evaluate_all_triggers(context)
        triggered = [name for name, dec in decisions.items() if dec.should_trigger]

        print(f"✅ Found {len(triggered)} triggered agents:")
        for agent_name in triggered:
            print(f"   • {agent_name}: {decisions[agent_name].reason}")

        assert len(triggered) >= 2, "Should trigger multiple agents"

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_triggered_agents():
    """Test getting list of triggered agent names."""
    print("\n" + "="*70)
    print("📋 Test 6: Get Triggered Agents List")
    print("="*70)

    try:
        engine = SubAgentTriggerEngine()

        context = {
            'files_to_modify': ['file1.py', 'file2.py', 'file3.py'],
            'library_name': 'fastapi',
            'affects_auth': True
        }

        triggered = engine.get_triggered_agents(context)

        print(f"✅ Triggered agents: {', '.join(triggered)}")
        assert len(triggered) > 0, "Should have triggered agents"
        assert 'ExplorerAgent' in triggered, "Explorer should be triggered"

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_metrics_tracking():
    """Test trigger metrics tracking."""
    print("\n" + "="*70)
    print("📊 Test 7: Metrics Tracking")
    print("="*70)

    try:
        engine = SubAgentTriggerEngine()

        # Trigger some agents
        contexts = [
            {'files_to_modify': ['a.py', 'b.py', 'c.py']},
            {'library_name': 'fastapi'},
            {'affects_auth': True},
        ]

        for ctx in contexts:
            engine.evaluate_all_triggers(ctx)

        metrics = engine.get_trigger_metrics()

        print(f"✅ Total triggers: {metrics['total_triggers']}")
        print(f"✅ By agent:")
        for agent, stats in metrics.get('by_agent', {}).items():
            print(f"   • {agent}: {stats['count']} times (avg confidence: {stats['avg_confidence']:.0%})")

        assert metrics['total_triggers'] > 0, "Should have recorded triggers"

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enable_disable():
    """Test enabling/disabling auto-triggering."""
    print("\n" + "="*70)
    print("🔧 Test 8: Enable/Disable Functionality")
    print("="*70)

    try:
        engine = SubAgentTriggerEngine()

        context = {
            'files_to_modify': ['file1.py', 'file2.py', 'file3.py']
        }

        # Should trigger when enabled
        decision = engine.should_invoke_explorer(context)
        assert decision.should_trigger, "Should trigger when enabled"
        print("✅ Triggers when enabled")

        # Disable
        engine.disable()
        decision = engine.should_invoke_explorer(context)
        assert not decision.should_trigger, "Should not trigger when disabled"
        print("✅ Doesn't trigger when disabled")

        # Re-enable
        engine.enable()
        decision = engine.should_invoke_explorer(context)
        assert decision.should_trigger, "Should trigger after re-enabling"
        print("✅ Triggers after re-enabling")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_loading():
    """Test configuration loading."""
    print("\n" + "="*70)
    print("⚙️  Test 9: Configuration Loading")
    print("="*70)

    try:
        engine = SubAgentTriggerEngine()

        # Check config loaded
        assert engine.config is not None, "Config should be loaded"
        assert 'triggers' in engine.config, "Config should have triggers"
        assert 'defaults' in engine.config, "Config should have defaults"

        print("✅ Configuration loaded successfully")
        print(f"✅ Trigger sections: {list(engine.config['triggers'].keys())}")
        print(f"✅ Defaults: {list(engine.config['defaults'].keys())}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all trigger engine tests."""
    print("\n" + "="*70)
    print("🧪 PHASE 4 AUTO-TRIGGERING TESTS")
    print("="*70)
    print("\nTesting intelligent sub-agent invocation logic...")

    results = {
        'Explorer Triggers': test_explorer_triggers(),
        'Historian Triggers': test_historian_triggers(),
        'Critic Triggers': test_critic_triggers(),
        'Research Triggers': test_research_triggers(),
        'Evaluate All Triggers': test_evaluate_all_triggers(),
        'Get Triggered Agents': test_get_triggered_agents(),
        'Metrics Tracking': test_metrics_tracking(),
        'Enable/Disable': test_enable_disable(),
        'Config Loading': test_config_loading(),
    }

    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{test_name:30} {status}")

    print("\n" + "-"*70)
    print(f"Total: {passed}/{total} tests passed")
    print("="*70 + "\n")

    if passed == total:
        print("✅ All trigger tests passed!")
        print("\nAuto-triggering system is ready for production:")
        print("  - Intelligent agent invocation based on context")
        print("  - Configurable thresholds and rules")
        print("  - Full logging and metrics")
        print("  - Easy enable/disable")
        print()

    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
