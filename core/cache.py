"""
cache.py
Phase 11 — Performance Optimization Cache
---------------------------------------------------------
Simple file-based cache keyed by (agent_name, inputs_hash).
Uses YAML storage with TTL (time-to-live) expiration.

Purpose:
    - Cache agent outputs to avoid redundant execution
    - Hash-based input change detection
    - TTL-based automatic expiration
    - Lightweight and dependency-free
"""

import yaml
import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class Cache:
    """
    Simple file-based cache with TTL support for agent outputs.
    """
    
    def __init__(self, root: str = "./.cache", ttl_hours: int = 24):
        """
        Initialize cache.
        
        Args:
            root: Cache directory path
            ttl_hours: Time-to-live in hours
        """
        self.root = Path(root)
        self.root.mkdir(exist_ok=True, parents=True)
        self.ttl = ttl_hours * 3600  # Convert to seconds
    
    @staticmethod
    def _hash_file(path: Path) -> str:
        """
        Compute SHA256 hash of a file.
        
        Args:
            path: File path
            
        Returns:
            Hex digest of file hash
        """
        h = hashlib.sha256()
        try:
            h.update(path.name.encode())
            if path.exists():
                h.update(path.read_bytes())
        except Exception:
            pass
        return h.hexdigest()
    
    @classmethod
    def hash_inputs(cls, inputs: List[str]) -> str:
        """
        Compute combined hash of multiple input files/patterns.
        
        Args:
            inputs: List of file paths (supports wildcards)
            
        Returns:
            Combined hash of all inputs
        """
        h = hashlib.sha256()
        
        # Expand wildcards
        expanded = []
        for p in inputs:
            if "*" in p:
                # Expand glob pattern
                matches = list(Path().glob(p))
                expanded.extend([str(x) for x in matches])
            else:
                expanded.append(p)
        
        # Hash all files
        for p in sorted(set(expanded)):
            h.update(p.encode())
            path = Path(p)
            if path.exists() and path.is_file():
                try:
                    h.update(path.read_bytes())
                except Exception:
                    pass
        
        return h.hexdigest()
    
    def _path_for(self, agent_name: str, key: str) -> Path:
        """Get cache file path for agent and key."""
        return self.root / f"{agent_name}_{key}.yaml"
    
    def get(self, agent_name: str, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached data if valid.
        
        Args:
            agent_name: Name of the agent
            key: Cache key (usually inputs hash)
            
        Returns:
            Cached data if valid, None otherwise
        """
        p = self._path_for(agent_name, key)
        
        if not p.exists():
            return None
        
        try:
            blob = yaml.safe_load(p.read_text(encoding='utf-8')) or {}
            
            # Check TTL
            timestamp = float(blob.get("ts", 0))
            age = time.time() - timestamp
            
            if age > self.ttl:
                # Expired
                return None
            
            return blob.get("data")
            
        except Exception:
            return None
    
    def set(self, agent_name: str, key: str, data: Dict[str, Any]):
        """
        Store data in cache.
        
        Args:
            agent_name: Name of the agent
            key: Cache key (usually inputs hash)
            data: Data to cache
        """
        p = self._path_for(agent_name, key)
        
        blob = {
            "ts": time.time(),
            "data": data,
            "agent": agent_name,
            "key": key
        }
        
        try:
            content = yaml.safe_dump(blob, sort_keys=False, default_flow_style=False)
            p.write_text(content, encoding='utf-8')
        except Exception as e:
            print(f"⚠️  Cache write failed for {agent_name}: {e}")
    
    def clear(self, agent_name: Optional[str] = None):
        """
        Clear cache for specific agent or all agents.
        
        Args:
            agent_name: Agent to clear cache for, or None for all
        """
        if agent_name:
            pattern = f"{agent_name}_*.yaml"
        else:
            pattern = "*.yaml"
        
        count = 0
        for cache_file in self.root.glob(pattern):
            try:
                cache_file.unlink()
                count += 1
            except Exception:
                pass
        
        return count
    
    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total = 0
        expired = 0
        valid = 0
        
        for cache_file in self.root.glob("*.yaml"):
            total += 1
            try:
                blob = yaml.safe_load(cache_file.read_text(encoding='utf-8'))
                timestamp = float(blob.get("ts", 0))
                age = time.time() - timestamp
                
                if age > self.ttl:
                    expired += 1
                else:
                    valid += 1
            except Exception:
                expired += 1
        
        return {
            "total": total,
            "valid": valid,
            "expired": expired,
            "ttl_hours": self.ttl / 3600
        }


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("💾 CACHE SYSTEM - PHASE 11")
    print("=" * 70 + "\n")
    
    cache = Cache(ttl_hours=1)
    
    # Test hash inputs
    inputs = ["README.md", "config/*.yaml"]
    input_hash = Cache.hash_inputs(inputs)
    print(f"Input hash: {input_hash[:16]}...")
    
    # Test cache operations
    test_data = {"result": "success", "value": 42}
    
    cache.set("TestAgent", input_hash, test_data)
    print("✅ Data cached")
    
    retrieved = cache.get("TestAgent", input_hash)
    print(f"✅ Retrieved: {retrieved}")
    
    # Stats
    stats = cache.stats()
    print(f"\n📊 Cache Stats:")
    print(f"   Total: {stats['total']}")
    print(f"   Valid: {stats['valid']}")
    print(f"   Expired: {stats['expired']}")
    
    print("\n" + "=" * 70)
    print("✅ CACHE TEST COMPLETE")
    print("=" * 70)

