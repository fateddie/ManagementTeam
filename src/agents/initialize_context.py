"""
initialize_context.py
---------------------------------------------------------
Automatic context loader for the Planning Agent.
Reads /docs, /config, /context folders and merges their
contents according to planning_agent_context.yaml.
---------------------------------------------------------
"""

import os
import yaml
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any


# Optional: swap in a real embedding or vector store later.
# For now we use a simple in-memory store.
class SimpleMemory:
    """Simple in-memory storage for context data."""
    
    def __init__(self):
        self.data = {}
    
    def store(self, key: str, value: Any):
        self.data[key] = value
    
    def get(self, key: str):
        return self.data.get(key)
    
    def __len__(self):
        return len(self.data)


# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------

def discover_files(paths: List[str], extensions: List[str]) -> List[Path]:
    """Recursively find files in given paths with matching extensions."""
    found = []
    for p in paths:
        if not os.path.exists(p):
            continue
        for root, _, files in os.walk(p):
            for f in files:
                if any(f.endswith(ext) for ext in extensions):
                    found.append(Path(root) / f)
    return found


def compute_hash_for_files(files: List[Path]) -> str:
    """Compute SHA256 hash of all file contents for change detection."""
    sha = hashlib.sha256()
    for f in sorted(files):
        sha.update(f.name.encode())
        try:
            with open(f, "rb") as fh:
                sha.update(fh.read())
        except Exception:
            continue
    return sha.hexdigest()


def load_yaml(path: str) -> Dict:
    """Load YAML configuration file."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def read_file_content(path: Path) -> str:
    """Read file content safely."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def summarize_context(text: str, max_chars: int = 2000) -> str:
    """Simple summarizer placeholder. Replace with LLM summary later."""
    lines = text.splitlines()
    short = [l for l in lines if len(l.strip()) > 0][:100]
    summary = "\n".join(short)
    if len(summary) > max_chars:
        summary = summary[:max_chars] + "\n...[truncated]..."
    return summary


# ---------------------------------------------------------
# Main initialization function
# ---------------------------------------------------------

def initialize_context(config_path: str = "./config/planning_agent_context.yaml") -> Dict[str, Any]:
    """
    Reads all defined context sources and returns structured context data.
    
    This function:
    1. Discovers files automatically
    2. Loads & parses according to planning_agent_context.yaml
    3. Merges and summarizes
    4. Caches into memory
    5. Generates internal summary for quick access
    
    Args:
        config_path: Path to the context configuration file
        
    Returns:
        Dictionary containing context data and memory instance
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Missing context config: {config_path}")

    config = load_yaml(config_path)

    # 1. Discover candidate files
    paths = [src["path"] for src in config.get("file_sources", [])]
    exts = []
    for src in config.get("file_sources", []):
        exts.extend(src.get("include_extensions", []))
    files = discover_files(paths, exts)

    if not files:
        raise FileNotFoundError("No context files found in configured directories.")

    # 2. Compute hash for caching and change detection
    context_hash = compute_hash_for_files(files)

    # 3. Load file contents
    merged_content = ""
    file_map = {}
    for f in files:
        text = read_file_content(f)
        merged_content += f"\n\n# {f.name}\n{text}\n"
        file_map[f.name] = text

    # 4. Basic summarization
    summary = summarize_context(merged_content)

    # 5. Validate PRD presence if required
    if config.get("validation", {}).get("require_prd", True):
        prd_found = any("PRD.md" in str(f) for f in files)
        if not prd_found:
            raise ValueError("PRD.md not found — planning aborted per validation rules.")

    # 6. Store in memory
    memory = SimpleMemory()
    memory.store("context_full", merged_content)
    memory.store("context_summary", summary)
    memory.store("context_hash", context_hash)
    memory.store("context_files", [str(f) for f in files])

    # 7. Construct final context object
    context = {
        "config": config,
        "files": file_map,
        "summary": summary,
        "hash": context_hash,
        "memory": memory,
    }

    return context


# ---------------------------------------------------------
# Example direct invocation
# ---------------------------------------------------------
if __name__ == "__main__":
    """Test the context manager"""
    print("🧪 Testing Context Initialization...")
    print("=" * 60)
    
    ctx = initialize_context()
    
    print(f"\n✅ Context initialized successfully.")
    print(f"✅ Loaded {len(ctx['files'])} files.")
    print(f"✅ Context hash: {ctx['hash'][:16]}...")
    print("\n" + "=" * 60)
    print("📋 CONTEXT SUMMARY:")
    print("=" * 60)
    print(ctx["summary"])

