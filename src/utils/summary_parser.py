"""
summary_parser.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary Parser Utility

Cleanly extracts data from Vertical Agent summary files.
Supports multiple formats (Jinja2 template, custom markdown, YAML).

Location: src/utils/summary_parser.py

Purpose:
    Decouples parsing logic from agent code, making testing and
    reuse easier across multiple agents (Strategic Planner, Risk, etc.)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any


def parse_vertical_summary(path: str) -> Dict[str, Any]:
    """
    Extract key metadata from a vertical summary file.
    
    Automatically detects format (YAML, Jinja2 markdown, custom markdown).
    
    Args:
        path: Path to summary file (.md or .yaml)
        
    Returns:
        Dict with keys:
        - top: Dict with top vertical details
        - title: Top vertical name (alias for backward compat)
        - score: RICE/ICE score
        - rationale: Why it won
        - ranked: List of all ranked verticals
        - framework: Scoring framework used
        
    Example:
        summary = parse_vertical_summary("outputs/recommendation.md")
        print(summary['top']['name'])  # → "Hair Salons"
        print(summary['score'])         # → 135.0
    """
    path_obj = Path(path)
    
    if not path_obj.exists():
        raise FileNotFoundError(f"Summary file not found: {path}")
    
    # Detect format by extension
    if path_obj.suffix in ['.yaml', '.yml']:
        return _parse_yaml_summary(path_obj)
    else:
        # Try markdown parsing
        return _parse_markdown_summary(path_obj)


def _parse_yaml_summary(path: Path) -> Dict[str, Any]:
    """
    Parse YAML summary file from Vertical Agent.
    
    Args:
        path: Path to YAML file
        
    Returns:
        Normalized summary dict
    """
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Handle both formats: evaluation_date wrapper or direct
    if 'recommendation' in data:
        # Format from vertical_scores.yaml
        recommendation = data['recommendation']
        top = recommendation.get('top_choice', {}) or recommendation.get('recommended_vertical', {})
        all_ranked = recommendation.get('all_scores', []) or data.get('all_verticals', [])
    else:
        # Direct format
        top = data.get('top_choice', {})
        all_ranked = data.get('all_ranked', []) or data.get('all_verticals', [])
    
    # Normalize top
    if isinstance(top, str):
        # Just a name, need to find it in ranked
        top_name = top
        top = next((v for v in all_ranked if v.get('name') == top_name), {'name': top_name})
    
    return {
        'top': top,
        'title': top.get('name', ''),
        'score': top.get('score', 0),
        'rationale': f"{top.get('name', '')} selected based on RICE scoring",
        'ranked': all_ranked,
        'framework': data.get('framework', 'RICE'),
        'plan': f"Build: {top.get('name', '')}",
    }


def _parse_markdown_summary(path: Path) -> Dict[str, Any]:
    """
    Parse markdown summary file.
    
    Supports both our Jinja2 template format and custom formats.
    
    Args:
        path: Path to markdown file
        
    Returns:
        Normalized summary dict
    """
    content = path.read_text()
    
    # Try our Jinja2 template format first
    result = _parse_jinja2_format(content)
    if result:
        return result
    
    # Try custom format
    result = _parse_custom_format(content)
    if result:
        return result
    
    # Fallback - basic extraction
    return _parse_generic_format(content)


def _parse_jinja2_format(content: str) -> Optional[Dict[str, Any]]:
    """
    Parse our Jinja2 template format.
    
    Looks for:
    ## 🏆 Top Recommendation
    **Name**
    - **Score**: `84.0`
    """
    # Find top recommendation section
    top_section = re.search(
        r'## 🏆 Top Recommendation\s*\*\*(.+?)\*\*',
        content,
        re.MULTILINE | re.DOTALL
    )
    
    if not top_section:
        return None
    
    top_name = top_section.group(1).strip()
    
    # Extract score
    score_match = re.search(r'\*\*Score\*\*:\s*`?(\d+\.?\d*)`?', content)
    score = float(score_match.group(1)) if score_match else 0
    
    # Extract details from table
    reach = _extract_field(content, 'Reach')
    impact = _extract_field(content, 'Impact')
    confidence = _extract_field(content, 'Confidence')
    effort = _extract_field(content, 'Effort')
    
    # Parse ranking table
    ranked = _parse_ranking_table(content)
    
    # Extract framework
    framework_match = re.search(r'\*\*Framework[^:]*:\s*(\w+)', content, re.IGNORECASE)
    framework = framework_match.group(1) if framework_match else 'RICE'
    
    return {
        'top': {
            'name': top_name,
            'score': score,
            'reach': reach,
            'impact': impact,
            'confidence': confidence,
            'effort': effort
        },
        'title': top_name,
        'score': score,
        'rationale': f"{top_name} recommended based on {framework} scoring",
        'ranked': ranked,
        'framework': framework,
        'plan': f"Build: {top_name}"
    }


def _parse_custom_format(content: str) -> Optional[Dict[str, Any]]:
    """
    Parse custom format with specific markers.
    
    Looks for:
    🏆 Winner: Name
    📊 Final Score: 123
    🧠 Why it won: Reason
    🛠️ Plan: Description
    """
    title_match = re.search(r'🏆\s*Winner:\s*(.+?)$', content, re.MULTILINE)
    score_match = re.search(r'📊\s*Final Score:\s*(\d+\.?\d*)', content, re.MULTILINE)
    rationale_match = re.search(r'🧠\s*Why it won:\s*(.+?)(?=\n🛠️|\n##|\Z)', content, re.MULTILINE | re.DOTALL)
    plan_match = re.search(r'🛠️\s*Plan:\s*(.+?)(?=\n##|\Z)', content, re.MULTILINE | re.DOTALL)
    
    if not title_match:
        return None
    
    return {
        'top': {
            'name': title_match.group(1).strip(),
            'score': float(score_match.group(1)) if score_match else 0
        },
        'title': title_match.group(1).strip(),
        'score': float(score_match.group(1)) if score_match else 0,
        'rationale': rationale_match.group(1).strip() if rationale_match else '',
        'plan': plan_match.group(1).strip() if plan_match else '',
        'ranked': [],
        'framework': 'RICE'
    }


def _parse_generic_format(content: str) -> Dict[str, Any]:
    """
    Fallback parser for generic markdown.
    
    Tries to extract anything that looks like a name and score.
    """
    # Look for any score pattern
    score_patterns = [
        r'score[:\s]+(\d+\.?\d*)',
        r'RICE[:\s]+(\d+\.?\d*)',
        r'ICE[:\s]+(\d+\.?\d*)',
    ]
    
    score = 0
    for pattern in score_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            score = float(match.group(1))
            break
    
    # Look for top/winner/recommendation
    name_patterns = [
        r'Top\s+(?:Recommendation|Choice|Project)[:\s]+\*\*(.+?)\*\*',
        r'Recommended[:\s]+(.+?)(?:\n|$)',
        r'Winner[:\s]+(.+?)(?:\n|$)',
    ]
    
    name = 'Unknown'
    for pattern in name_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            break
    
    return {
        'top': {'name': name, 'score': score},
        'title': name,
        'score': score,
        'rationale': 'Extracted from summary',
        'ranked': [],
        'framework': 'RICE',
        'plan': f"Build: {name}"
    }


def _extract_field(content: str, field_name: str) -> int:
    """
    Extract a numbered field from markdown content.
    
    Looks for patterns like:
    - **Reach**: 7/10
    - Reach: 7
    """
    patterns = [
        rf'\*\*{field_name}\*\*:\s*(\d+)',
        rf'{field_name}:\s*(\d+)',
        rf'{field_name}\s*=\s*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    return 0


def _parse_ranking_table(content: str) -> List[Dict]:
    """
    Parse ranking table from markdown.
    
    Looks for table like:
    | Rank | Idea | Score | Reach | Impact | Confidence | Effort |
    |------|------|-------|-------|--------|------------|--------|
    | 🥇 1 | Name | 135.0 | 5 | 6 | 9 | 2 |
    """
    ranked = []
    
    # Find table section
    table_match = re.search(
        r'\|\s*Rank\s*\|.*?\n\|[-\s|]+\n((?:\|.*?\n)+)',
        content,
        re.MULTILINE
    )
    
    if not table_match:
        return ranked
    
    table_rows = table_match.group(1).strip().split('\n')
    
    for row in table_rows:
        # Parse row: | 🥇 1 | Name | 135.0 | 5 | 6 | 9 | 2 |
        cells = [c.strip() for c in row.split('|') if c.strip()]
        
        if len(cells) >= 3:
            try:
                # Remove medal emoji and rank number from first cell
                rank_cell = cells[0]
                name = cells[1]
                score = float(cells[2])
                
                vertical = {
                    'name': name,
                    'score': score
                }
                
                # Add optional fields if present
                if len(cells) >= 7:
                    vertical.update({
                        'reach': int(cells[3]),
                        'impact': int(cells[4]),
                        'confidence': int(cells[5]),
                        'effort': int(cells[6])
                    })
                
                ranked.append(vertical)
            except (ValueError, IndexError):
                continue
    
    return ranked


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helper Functions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def extract_top_vertical(summary_path: str) -> Dict[str, Any]:
    """
    Quick extraction of just the top vertical.
    
    Args:
        summary_path: Path to summary file
        
    Returns:
        Dict with top vertical details
    """
    summary = parse_vertical_summary(summary_path)
    return summary['top']


def extract_score(summary_path: str) -> float:
    """
    Quick extraction of just the score.
    
    Args:
        summary_path: Path to summary file
        
    Returns:
        Score as float
    """
    summary = parse_vertical_summary(summary_path)
    return summary['score']


def extract_all_ranked(summary_path: str) -> List[Dict]:
    """
    Extract full ranking list.
    
    Args:
        summary_path: Path to summary file
        
    Returns:
        List of all verticals with scores
    """
    summary = parse_vertical_summary(summary_path)
    return summary['ranked']


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Testing & Validation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def validate_summary(summary_path: str) -> bool:
    """
    Validate that a summary file can be parsed successfully.
    
    Args:
        summary_path: Path to summary file
        
    Returns:
        True if valid, False otherwise
    """
    try:
        summary = parse_vertical_summary(summary_path)
        
        # Check required fields
        required = ['top', 'title', 'score']
        for field in required:
            if field not in summary or not summary[field]:
                return False
        
        # Check top has name
        if 'name' not in summary['top']:
            return False
        
        return True
        
    except Exception:
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI Test
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Test the parser with actual files."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python src/utils/summary_parser.py <path_to_summary>")
        print("\nTrying default path: outputs/recommendation.md")
        path = "outputs/recommendation.md"
    else:
        path = sys.argv[1]
    
    print(f"\n📖 Parsing: {path}\n")
    
    try:
        summary = parse_vertical_summary(path)
        
        print("✅ Parse successful!\n")
        print("="*60)
        print("EXTRACTED DATA")
        print("="*60 + "\n")
        
        print(f"Top Vertical: {summary['title']}")
        print(f"Score: {summary['score']}")
        print(f"Framework: {summary['framework']}")
        
        if summary['top']:
            print(f"\nTop Details:")
            for key, value in summary['top'].items():
                print(f"  {key}: {value}")
        
        if summary['ranked']:
            print(f"\nRanked List ({len(summary['ranked'])} items):")
            for i, item in enumerate(summary['ranked'][:5], 1):
                print(f"  {i}. {item['name']} - {item['score']}")
        
        print("\n" + "="*60)
        print("✅ Validation:", "PASS" if validate_summary(path) else "FAIL")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Parse failed: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

