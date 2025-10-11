"""
test_perf.py
Phase 11 — Performance & Parallelism Tests
---------------------------------------------------------
Unit tests for caching, lazy execution, and performance optimization.
"""

import sys
import time
import yaml
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from core.cache import Cache


class TestCache:
    """Test cache functionality."""
    
    def test_basic_cache_operations(self):
        """Test basic cache set/get operations."""
        cache = Cache(root="./.cache_test", ttl_hours=1)
        
        # Set data
        test_data = {"result": "success", "count": 42}
        cache.set("TestAgent", "test_key", test_data)
        
        # Get data
        retrieved = cache.get("TestAgent", "test_key")
        
        assert retrieved is not None
        assert retrieved["result"] == "success"
        assert retrieved["count"] == 42
        
        # Cleanup
        cache.clear()
    
    def test_cache_expiration(self):
        """Test TTL expiration."""
        cache = Cache(root="./.cache_test", ttl_hours=0.0001)  # Very short TTL
        
        # Set data
        cache.set("TestAgent", "expire_key", {"data": "test"})
        
        # Wait for expiration
        time.sleep(1)
        
        # Should be expired
        retrieved = cache.get("TestAgent", "expire_key")
        assert retrieved is None
        
        # Cleanup
        cache.clear()
    
    def test_hash_inputs(self):
        """Test input hashing."""
        # Hash same inputs multiple times
        inputs = ["README.md"]
        
        hash1 = Cache.hash_inputs(inputs)
        hash2 = Cache.hash_inputs(inputs)
        
        assert hash1 == hash2  # Should be deterministic
        assert len(hash1) == 64  # SHA256 hex digest
    
    def test_cache_miss(self):
        """Test cache miss for non-existent key."""
        cache = Cache(root="./.cache_test")
        
        retrieved = cache.get("NonExistent", "missing_key")
        assert retrieved is None
    
    def test_cache_stats(self):
        """Test cache statistics."""
        cache = Cache(root="./.cache_test", ttl_hours=1)
        
        # Add some cached data
        cache.set("Agent1", "key1", {"data": 1})
        cache.set("Agent2", "key2", {"data": 2})
        
        stats = cache.stats()
        
        assert stats["total"] >= 2
        assert stats["valid"] >= 2
        assert stats["ttl_hours"] == 1
        
        # Cleanup
        cache.clear()
    
    def test_clear_specific_agent(self):
        """Test clearing cache for specific agent."""
        cache = Cache(root="./.cache_test")
        
        # Cache data for multiple agents
        cache.set("Agent1", "key1", {"data": 1})
        cache.set("Agent2", "key2", {"data": 2})
        
        # Clear only Agent1
        cleared = cache.clear("Agent1")
        
        assert cleared >= 1
        assert cache.get("Agent1", "key1") is None
        assert cache.get("Agent2", "key2") is not None
        
        # Cleanup
        cache.clear()
    
    def test_glob_pattern_inputs(self):
        """Test hashing with glob patterns."""
        inputs = ["config/*.yaml", "README.md"]
        
        hash_result = Cache.hash_inputs(inputs)
        
        assert hash_result is not None
        assert len(hash_result) == 64


class TestLazyExecution:
    """Test lazy execution scenarios."""
    
    def test_unchanged_inputs_detected(self):
        """Test that unchanged inputs produce same hash."""
        cache = Cache(root="./.cache_test")
        
        inputs = ["README.md"]
        hash1 = Cache.hash_inputs(inputs)
        
        # Sleep briefly
        time.sleep(0.1)
        
        # Hash again
        hash2 = Cache.hash_inputs(inputs)
        
        # Should be identical
        assert hash1 == hash2
        
        cache.clear()
    
    def test_cache_reuse(self):
        """Test that cached results can be reused."""
        cache = Cache(root="./.cache_test", ttl_hours=1)
        
        agent_name = "PlanningAgent"
        inputs = ["README.md"]
        input_hash = Cache.hash_inputs(inputs)
        
        # First run - cache miss
        cached = cache.get(agent_name, input_hash)
        assert cached is None
        
        # Execute and cache
        result = {"plan": "generated", "milestones": 3}
        cache.set(agent_name, input_hash, result)
        
        # Second run - cache hit
        cached = cache.get(agent_name, input_hash)
        assert cached is not None
        assert cached["plan"] == "generated"
        assert cached["milestones"] == 3
        
        # Cleanup
        cache.clear()


class TestPerformancePolicy:
    """Test performance policy loading and parsing."""
    
    def test_load_perf_policy(self):
        """Test loading performance policy file."""
        policy_path = PROJECT_ROOT / "config" / "perf_policy.yaml"
        
        if not policy_path.exists():
            print(f"   ⚠️  SKIP: {policy_path} not found")
            return
        
        with open(policy_path, 'r') as f:
            policy = yaml.safe_load(f)
        
        assert "parallel_groups" in policy
        assert "cache" in policy
        assert "lazy" in policy
        assert policy["cache"]["enabled"] == True
    
    def test_parallel_groups_valid(self):
        """Test that parallel groups are valid."""
        policy_path = PROJECT_ROOT / "config" / "perf_policy.yaml"
        
        if not policy_path.exists():
            print(f"   ⚠️  SKIP: {policy_path} not found")
            return
        
        with open(policy_path, 'r') as f:
            policy = yaml.safe_load(f)
        
        parallel_groups = policy.get("parallel_groups", [])
        
        # Each group should be a list
        for group in parallel_groups:
            assert isinstance(group, list)
            assert len(group) >= 1


# ==============================================
# Test Runner
# ==============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 PERFORMANCE & CACHE TESTS - PHASE 11")
    print("=" * 70 + "\n")
    
    test_cache = TestCache()
    test_lazy = TestLazyExecution()
    test_policy = TestPerformancePolicy()
    
    tests_run = 0
    tests_passed = 0
    
    test_classes = [
        ("Cache", test_cache, [
            "test_basic_cache_operations",
            "test_cache_expiration",
            "test_hash_inputs",
            "test_cache_miss",
            "test_cache_stats",
            "test_clear_specific_agent",
            "test_glob_pattern_inputs"
        ]),
        ("Lazy Execution", test_lazy, [
            "test_unchanged_inputs_detected",
            "test_cache_reuse"
        ]),
        ("Performance Policy", test_policy, [
            "test_load_perf_policy",
            "test_parallel_groups_valid"
        ])
    ]
    
    for class_name, test_instance, test_methods in test_classes:
        print(f"\n📋 Testing {class_name}:")
        for method_name in test_methods:
            tests_run += 1
            try:
                method = getattr(test_instance, method_name)
                method()
                print(f"   ✅ {method_name}")
                tests_passed += 1
            except Exception as e:
                print(f"   ❌ {method_name}: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 TEST RESULTS: {tests_passed}/{tests_run} passed")
    print("=" * 70 + "\n")
    
    if tests_passed == tests_run:
        print("🎉 ALL PERFORMANCE TESTS PASSED!\n")
        sys.exit(0)
    else:
        print(f"⚠️  {tests_run - tests_passed} test(s) failed\n")
        sys.exit(1)

