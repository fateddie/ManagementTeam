"""
prd_parser.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRD Parser & Validator

Extracts structured information from PRD markdown files and
validates completeness before project creation.

Location: src/utils/prd_parser.py

Purpose:
    - Parse PRD markdown into structured data
    - Validate PRD completeness
    - Extract agents, tech stack, requirements
    - Provide quality checks before planning

Phase: 17 - PRD-Driven Planning Enhancement
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class PRDParser:
    """
    Parse and validate PRD markdown documents.
    """
    
    def __init__(self, prd_path: str):
        """
        Initialize PRD parser.
        
        Args:
            prd_path: Path to PRD markdown file
        """
        self.prd_path = Path(prd_path)
        self.content = ""
        self.parsed_data = {}
        
        if self.prd_path.exists():
            self.content = self.prd_path.read_text()
        else:
            raise FileNotFoundError(f"PRD not found: {prd_path}")
    
    def parse(self) -> Dict:
        """
        Parse PRD into structured data.
        
        Returns:
            Dict with extracted sections
        """
        self.parsed_data = {
            'metadata': self._extract_metadata(),
            'overview': self._extract_overview(),
            'features': self._extract_features(),
            'agents': self._extract_agents(),
            'tech_stack': self._extract_tech_stack(),
            'success_criteria': self._extract_success_criteria(),
            'next_steps': self._extract_next_steps(),
            'open_decisions': self._extract_open_decisions(),
        }
        
        return self.parsed_data
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate PRD completeness.
        
        Returns:
            (is_valid, list of issues)
        """
        issues = []
        
        # Parse if not already done
        if not self.parsed_data:
            self.parse()
        
        # Check required sections
        required_sections = [
            'overview',
            'features',
            'tech_stack',
            'success_criteria'
        ]
        
        for section in required_sections:
            if not self.parsed_data.get(section):
                issues.append(f"❌ Missing required section: {section}")
        
        # Check metadata
        metadata = self.parsed_data.get('metadata', {})
        if not metadata.get('project_name'):
            issues.append("❌ Missing project name in metadata")
        
        # Check overview
        overview = self.parsed_data.get('overview', {})
        if not overview.get('goal'):
            issues.append("⚠️  No clear goal defined in overview")
        
        # Check agents (if applicable)
        agents = self.parsed_data.get('agents', [])
        if len(agents) == 0:
            issues.append("ℹ️  No agents defined (may be intentional)")
        
        # Check tech stack
        tech_stack = self.parsed_data.get('tech_stack', {})
        if len(tech_stack) == 0:
            issues.append("⚠️  No tech stack specified")
        
        # Check success criteria
        criteria = self.parsed_data.get('success_criteria', [])
        if len(criteria) == 0:
            issues.append("⚠️  No success criteria defined")
        
        is_valid = len([i for i in issues if i.startswith("❌")]) == 0
        
        return is_valid, issues
    
    def _extract_metadata(self) -> Dict:
        """Extract project metadata from header."""
        metadata = {}
        
        # Extract project name from title
        title_match = re.search(r'^#\s+[🧾📋]*\s*(?:PRD\s*[–-]\s*)?(.+?)$', self.content, re.MULTILINE)
        if title_match:
            metadata['project_name'] = title_match.group(1).strip()
        
        # Extract owner
        owner_match = re.search(r'\*\*Owner:\*\*\s*(.+?)(?:\n|$)', self.content)
        if owner_match:
            metadata['owner'] = owner_match.group(1).strip()
        
        # Extract version
        version_match = re.search(r'\*\*Version:\*\*\s*(.+?)(?:\n|$)', self.content)
        if version_match:
            metadata['version'] = version_match.group(1).strip()
        
        # Extract dates
        created_match = re.search(r'\*\*Created:\*\*\s*(.+?)(?:\n|$)', self.content)
        if created_match:
            metadata['created'] = created_match.group(1).strip()
        
        return metadata
    
    def _extract_overview(self) -> Dict:
        """Extract overview section."""
        overview = {}
        
        # Find Overview section
        overview_match = re.search(
            r'##\s+[0-9]*[️⃣]*\s*Overview\s*\n(.*?)(?=\n##|\Z)',
            self.content,
            re.DOTALL | re.IGNORECASE
        )
        
        if overview_match:
            overview_text = overview_match.group(1)
            
            # Extract goal
            goal_match = re.search(r'\*\*Goal:\*\*\s*\n?(.+?)(?=\n\*\*|\n\n|\Z)', overview_text, re.DOTALL)
            if goal_match:
                overview['goal'] = goal_match.group(1).strip()
            
            # Extract key outcomes
            outcomes_match = re.search(r'\*\*Key Outcomes:\*\*\s*\n(.*?)(?=\n\*\*|\n##|\Z)', overview_text, re.DOTALL)
            if outcomes_match:
                outcomes_text = outcomes_match.group(1)
                outcomes = re.findall(r'[-•]\s*(.+?)(?=\n[-•]|\Z)', outcomes_text, re.DOTALL)
                overview['key_outcomes'] = [o.strip() for o in outcomes if o.strip()]
        
        return overview
    
    def _extract_features(self) -> List[Dict]:
        """Extract features and capabilities."""
        features = []
        
        # Find Features section
        features_match = re.search(
            r'##\s+[0-9]*[️⃣]*\s*Features?\s*(?:&|and)?\s*Capabilities?\s*\n(.*?)(?=\n##|\Z)',
            self.content,
            re.DOTALL | re.IGNORECASE
        )
        
        if features_match:
            features_text = features_match.group(1)
            
            # Extract from table format
            table_rows = re.findall(r'\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|', features_text)
            for name, description in table_rows:
                if name.lower() not in ['feature', 'capability']:  # Skip header
                    features.append({
                        'name': name.strip(),
                        'description': description.strip()
                    })
            
            # Also try bullet point format
            if not features:
                bullets = re.findall(r'[-•]\s*\*\*(.+?)\*\*:?\s*(.+?)(?=\n[-•]|\Z)', features_text, re.DOTALL)
                for name, description in bullets:
                    features.append({
                        'name': name.strip(),
                        'description': description.strip()
                    })
        
        return features
    
    def _extract_agents(self) -> List[Dict]:
        """Extract agent definitions (if multi-agent system)."""
        agents = []
        
        # Find Agent section
        agent_match = re.search(
            r'##\s+[0-9]*[️⃣]*\s*Agent\s+Role\s+Definitions?\s*\n(.*?)(?=\n##|\Z)',
            self.content,
            re.DOTALL | re.IGNORECASE
        )
        
        if agent_match:
            agent_text = agent_match.group(1)
            
            # Extract from table format
            table_rows = re.findall(r'\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|', agent_text)
            for agent, specialization, notes in table_rows:
                if agent.lower() not in ['agent', 'name']:  # Skip header
                    agents.append({
                        'name': agent.strip(),
                        'specialization': specialization.strip(),
                        'notes': notes.strip()
                    })
        
        return agents
    
    def _extract_tech_stack(self) -> Dict:
        """Extract technology stack."""
        tech_stack = {}
        
        # Find Tech Stack section
        tech_match = re.search(
            r'##\s+[0-9]*[️⃣]*\s*Technical?\s+Stack\s*\n(.*?)(?=\n##|\Z)',
            self.content,
            re.DOTALL | re.IGNORECASE
        )
        
        if tech_match:
            tech_text = tech_match.group(1)
            
            # Extract from table format
            table_rows = re.findall(r'\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|', tech_text)
            for layer, stack in table_rows:
                if layer.lower() not in ['layer', 'component']:  # Skip header
                    tech_stack[layer.strip()] = stack.strip()
        
        return tech_stack
    
    def _extract_success_criteria(self) -> List[Dict]:
        """Extract success criteria and metrics."""
        criteria = []
        
        # Find Success Criteria section
        success_match = re.search(
            r'##\s+[0-9]*[️⃣]*\s*Success\s+Criteria\s*\n(.*?)(?=\n##|\Z)',
            self.content,
            re.DOTALL | re.IGNORECASE
        )
        
        if success_match:
            success_text = success_match.group(1)
            
            # Extract from table format
            table_rows = re.findall(r'\|\s*([✅❌]?)\s*(.+?)\s*\|\s*(.+?)\s*\|', success_text)
            for status, metric, target in table_rows:
                if metric.lower() not in ['metric', 'criteria']:  # Skip header
                    criteria.append({
                        'status': status.strip() or '⏳',
                        'metric': metric.strip(),
                        'target': target.strip()
                    })
        
        return criteria
    
    def _extract_next_steps(self) -> List[str]:
        """Extract next steps/execution plan."""
        steps = []
        
        # Find Next Steps section
        steps_match = re.search(
            r'##\s+[0-9]*[️⃣]*\s*Next\s+Steps\s*(?:\(Execution Plan\))?\s*\n(.*?)(?=\n##|\Z)',
            self.content,
            re.DOTALL | re.IGNORECASE
        )
        
        if steps_match:
            steps_text = steps_match.group(1)
            
            # Extract numbered or bulleted list
            step_items = re.findall(r'[0-9]+\.\s*([✅🔜⏳❌]?)\s*(.+?)(?=\n[0-9]+\.|\Z)', steps_text, re.DOTALL)
            for status, step in step_items:
                steps.append({
                    'status': status.strip() or '⏳',
                    'description': step.strip()
                })
        
        return steps
    
    def _extract_open_decisions(self) -> List[Dict]:
        """Extract open decisions/questions."""
        decisions = []
        
        # Find Open Decisions section
        decisions_match = re.search(
            r'##\s+[0-9]*[️⃣]*\s*Open\s+Decisions?\s*\n(.*?)(?=\n##|\Z)',
            self.content,
            re.DOTALL | re.IGNORECASE
        )
        
        if decisions_match:
            decisions_text = decisions_match.group(1)
            
            # Extract from table format
            table_rows = re.findall(r'\|\s*(.+?)\s*\|\s*(.+?)\s*\|', decisions_text)
            for question, owner in table_rows:
                if question.lower() not in ['question', 'decision']:  # Skip header
                    decisions.append({
                        'question': question.strip(),
                        'owner': owner.strip()
                    })
        
        return decisions
    
    def generate_report(self) -> str:
        """
        Generate a validation report.
        
        Returns:
            Formatted report string
        """
        if not self.parsed_data:
            self.parse()
        
        is_valid, issues = self.validate()
        
        report = []
        report.append("\n" + "="*70)
        report.append("📋 PRD ANALYSIS REPORT")
        report.append("="*70 + "\n")
        
        # Metadata
        metadata = self.parsed_data.get('metadata', {})
        report.append(f"**Project:** {metadata.get('project_name', 'Unknown')}")
        report.append(f"**Owner:** {metadata.get('owner', 'Unknown')}")
        report.append(f"**Version:** {metadata.get('version', 'Unknown')}")
        report.append("")
        
        # Validation Status
        status = "✅ VALID" if is_valid else "⚠️  NEEDS ATTENTION"
        report.append(f"**Status:** {status}\n")
        
        if issues:
            report.append("**Issues Found:**")
            for issue in issues:
                report.append(f"  {issue}")
            report.append("")
        
        # Overview
        overview = self.parsed_data.get('overview', {})
        if overview.get('goal'):
            report.append("**Goal:**")
            report.append(f"  {overview['goal']}\n")
        
        # Agents
        agents = self.parsed_data.get('agents', [])
        if agents:
            report.append(f"**Agents Defined:** {len(agents)}")
            for agent in agents:
                report.append(f"  • {agent['name']}: {agent['specialization']}")
            report.append("")
        
        # Tech Stack
        tech_stack = self.parsed_data.get('tech_stack', {})
        if tech_stack:
            report.append(f"**Tech Stack:** {len(tech_stack)} layers")
            for layer, stack in tech_stack.items():
                report.append(f"  • {layer}: {stack}")
            report.append("")
        
        # Success Criteria
        criteria = self.parsed_data.get('success_criteria', [])
        if criteria:
            report.append(f"**Success Criteria:** {len(criteria)} defined")
            for criterion in criteria[:3]:  # Show first 3
                report.append(f"  {criterion['status']} {criterion['metric']}")
            report.append("")
        
        report.append("="*70)
        report.append(f"{'✅ Ready for Planning Agent' if is_valid else '⚠️  Review and fix issues before proceeding'}")
        report.append("="*70 + "\n")
        
        return "\n".join(report)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI Testing
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python prd_parser.py <path_to_prd.md>")
        sys.exit(1)
    
    prd_path = sys.argv[1]
    
    try:
        parser = PRDParser(prd_path)
        data = parser.parse()
        
        # Print report
        print(parser.generate_report())
        
        # Print detailed structure (optional)
        print("\n📊 DETAILED STRUCTURE:\n")
        import json
        print(json.dumps(data, indent=2))
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


