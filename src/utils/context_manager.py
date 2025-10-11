# ==============================================
# file: /ManagementTeam/src/utils/context_manager.py
# ==============================================
"""
Context Manager for Planning Agent
-----------------------------------
Automatically discovers, prioritizes, and merges contextual files
according to planning_agent_context.yaml rules.

This module implements intelligent context gathering so the Planner Agent
can ground its reasoning in existing project documentation.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List
import yaml
import json
from datetime import datetime


def discover_files(
    paths: List[str], 
    extensions: List[str], 
    recursive: bool = True
) -> List[Path]:
    """
    Discover all relevant files in specified paths.
    
    Args:
        paths: List of directory paths to search
        extensions: List of file extensions to include (e.g., [".md", ".yaml"])
        recursive: Whether to search subdirectories
        
    Returns:
        List of Path objects for discovered files
    """
    discovered: List[Path] = []
    
    for path_str in paths:
        path = Path(path_str)
        if not path.exists():
            continue
            
        if recursive:
            for ext in extensions:
                discovered.extend(path.rglob(f"*{ext}"))
        else:
            for ext in extensions:
                discovered.extend(path.glob(f"*{ext}"))
    
    return discovered


def load_yaml(filepath: str | Path) -> Dict[str, Any]:
    """
    Safely load YAML configuration file.
    
    Args:
        filepath: Path to YAML file
        
    Returns:
        Dictionary containing YAML data
    """
    path = Path(filepath)
    if not path.exists():
        return {}
    
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def parse_and_merge(files: List[Path], rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse files according to rules and merge into unified context.
    
    Args:
        files: List of file paths to parse
        rules: Configuration rules from planning_agent_context.yaml
        
    Returns:
        Merged context data dictionary
    """
    parsing_rules = rules.get('parsing', {})
    fusion_rules = rules.get('fusion', {})
    priority_hierarchy = rules.get('priority_hierarchy', [])
    
    # Sort files by priority
    prioritized_files = sort_by_priority(files, priority_hierarchy)
    
    context_data: Dict[str, Any] = {
        'files': {},
        'sections': {},
        'metadata': {
            'parsed_at': datetime.now().isoformat(),
            'total_files': len(files),
            'parsing_rules': parsing_rules,
        }
    }
    
    for file_path in prioritized_files:
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Parse based on file type
            if file_path.suffix in ['.yaml', '.yml']:
                parsed = yaml.safe_load(content)
            elif file_path.suffix == '.json':
                parsed = json.loads(content)
            else:
                parsed = {'content': content, 'type': 'text'}
            
            # Extract sections if enabled
            if parsing_rules.get('extract_sections', True):
                sections = extract_sections(content, file_path.suffix)
                context_data['sections'][file_path.name] = sections
            
            # Store parsed content
            context_data['files'][str(file_path)] = {
                'content': parsed,
                'priority': get_priority_score(file_path.name, priority_hierarchy),
                'size': len(content),
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            
        except Exception as e:
            context_data['files'][str(file_path)] = {'error': str(e)}
    
    return context_data


def sort_by_priority(files: List[Path], priority_hierarchy: List[str]) -> List[Path]:
    """
    Sort files by their priority in the hierarchy.
    
    Args:
        files: List of file paths
        priority_hierarchy: Ordered list of high-priority filenames
        
    Returns:
        Sorted list of files (highest priority first)
    """
    def get_priority_score(filepath: Path) -> int:
        """Lower score = higher priority"""
        filename = filepath.name
        for i, priority_name in enumerate(priority_hierarchy):
            if priority_name in filename:
                return i
        return len(priority_hierarchy)  # Default lowest priority
    
    return sorted(files, key=get_priority_score)


def get_priority_score(filename: str, priority_hierarchy: List[str]) -> int:
    """
    Calculate priority score for a file (lower = higher priority).
    
    Args:
        filename: Name of the file
        priority_hierarchy: Ordered list of filenames
        
    Returns:
        Priority score (0 = highest)
    """
    for i, priority_name in enumerate(priority_hierarchy):
        if priority_name in filename:
            return i
    return len(priority_hierarchy)


def extract_sections(content: str, file_type: str) -> Dict[str, str]:
    """
    Extract major sections from markdown or text files.
    
    Args:
        content: File content
        file_type: File extension (.md, .txt, etc.)
        
    Returns:
        Dictionary mapping section names to content
    """
    sections: Dict[str, str] = {}
    
    if file_type not in ['.md', '.txt']:
        return sections
    
    # Simple section detection for markdown (## headers)
    current_section = 'preamble'
    current_content: List[str] = []
    
    for line in content.split('\n'):
        if line.startswith('## '):
            # Save previous section
            if current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            # Start new section
            current_section = line.replace('## ', '').strip()
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections


def summarize_context(context_data: Dict[str, Any]) -> str:
    """
    Generate a concise summary of the context for quick reference.
    
    Args:
        context_data: Full context dictionary
        
    Returns:
        Markdown-formatted summary string
    """
    summary_lines = [
        "# 📋 Context Summary",
        "",
        f"**Generated:** {context_data['metadata']['parsed_at']}  ",
        f"**Total Files:** {context_data['metadata']['total_files']}  ",
        "",
        "## 📁 Files Loaded",
        ""
    ]
    
    # List files by priority
    sorted_files = sorted(
        context_data['files'].items(),
        key=lambda x: x[1].get('priority', 999)
    )
    
    for filepath, file_info in sorted_files[:10]:  # Top 10
        filename = Path(filepath).name
        priority = file_info.get('priority', '?')
        size = file_info.get('size', 0)
        summary_lines.append(f"- **{filename}** (Priority: {priority}, Size: {size:,} bytes)")
    
    summary_lines.extend([
        "",
        "## 🎯 Key Sections Detected",
        ""
    ])
    
    # List important sections
    for filename, sections in list(context_data.get('sections', {}).items())[:5]:
        summary_lines.append(f"### {filename}")
        for section_name in list(sections.keys())[:3]:
            summary_lines.append(f"  - {section_name}")
        summary_lines.append("")
    
    return '\n'.join(summary_lines)


def initialize_context() -> Dict[str, Any]:
    """
    Main entry point: Initialize context for Planning Agent.
    
    This function:
    1. Discovers files automatically
    2. Loads & parses according to planning_agent_context.yaml
    3. Merges and summarizes
    4. Caches into memory (stub for now)
    5. Generates internal summary
    
    Returns:
        Dictionary containing all context data
    """
    # 1. Discover files automatically
    files = discover_files(
        paths=["./docs", "./config", "./context"],
        extensions=[".md", ".yaml", ".yml", ".json", ".txt"],
        recursive=True
    )
    
    # 2. Load & parse according to planning_agent_context.yaml
    rules = load_yaml("./config/planning_agent_context.yaml")
    
    # 3. Merge and summarize
    context_data = parse_and_merge(files, rules)
    
    # 4. Cache into memory / vector DB (stub for now)
    # TODO: Implement memory.store(context_data) when memory system is ready
    
    # 5. Generate internal summary for quick access
    context_summary = summarize_context(context_data)
    context_data['summary'] = context_summary
    
    return context_data


# ==============================================
# Testing & Demo
# ==============================================
if __name__ == "__main__":
    """Test the context manager"""
    print("🧪 Testing Context Manager...")
    print("=" * 60)
    
    context = initialize_context()
    
    print(f"\n✅ Discovered {context['metadata']['total_files']} files")
    print(f"✅ Extracted {len(context['sections'])} file sections")
    print(f"✅ Context parsed at: {context['metadata']['parsed_at']}")
    
    print("\n" + "=" * 60)
    print("📋 CONTEXT SUMMARY:")
    print("=" * 60)
    print(context['summary'])

