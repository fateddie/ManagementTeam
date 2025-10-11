"""
reporting_agent.py
Phase 6 – Reporting & Testing Automation
---------------------------------------------------------
Generates build summaries, validation reports, and archives old sessions.

Purpose:
    Self-auditing and quality control agent that:
    - Collects audit information from all outputs
    - Validates YAML and markdown files
    - Generates comprehensive reports
    - Archives old sessions automatically

Outputs:
    - reports/session_audit_<timestamp>.json
    - reports/validation_report_<timestamp>.md
    - reports/build_summary_<timestamp>.md
"""

import os
import yaml
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List


class ReportingAgent:
    """
    Reporting and validation agent for quality control and audit trail.
    """
    
    def __init__(
        self,
        outputs_dir: str = "./outputs/",
        logs_dir: str = "./logs/",
        archive_days: int = 7
    ):
        """
        Initialize Reporting Agent.
        
        Args:
            outputs_dir: Directory containing agent outputs
            logs_dir: Directory containing logs
            archive_days: Archive files older than this many days
        """
        self.outputs = Path(outputs_dir)
        self.logs = Path(logs_dir)
        self.archive_days = archive_days
        self.session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.report_dir = self.outputs / "reports"
        self.report_dir.mkdir(exist_ok=True, parents=True)

    def run(self) -> Dict[str, Any]:
        """
        Main execution - audit, validate, report, archive.
        
        Returns:
            Dictionary with audit results
        """
        print("📊 Reporting Agent starting...")
        
        # Step 1: Collect audit information
        audit = self._collect_audit()
        print(f"✅ Audit collected: {len(audit['outputs'])} outputs, {len(audit['logs'])} logs")
        
        # Step 2: Validate outputs
        validation = self._validate_outputs(audit)
        print(f"✅ Validation complete: {len(validation['valid'])} valid, {len(validation['invalid'])} invalid")
        
        # Step 3: Write summary
        self._write_summary(audit, validation)
        print(f"✅ Summary written")
        
        # Step 4: Archive old files
        archived_count = self._archive_old()
        print(f"✅ Archived {archived_count} old files")
        
        print("✅ Reporting complete.")
        
        return {
            "audit": audit,
            "validation": validation,
            "archived": archived_count,
            "status": "complete"
        }

    def _collect_audit(self) -> Dict[str, Any]:
        """Collect all outputs and logs for audit."""
        audit = {
            "session": self.session_id,
            "outputs": [],
            "logs": [],
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Collect output files
        if self.outputs.exists():
            for f in self.outputs.glob("*.*"):
                if f.is_file() and not f.name.startswith('.'):
                    audit["outputs"].append({
                        "name": f.name,
                        "size": f.stat().st_size,
                        "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    })
        
        # Collect log files
        if self.logs.exists():
            for f in self.logs.glob("*.log"):
                audit["logs"].append(f.name)
        
        # Save audit JSON
        audit_path = self.report_dir / f"session_audit_{self.session_id}.json"
        audit_path.write_text(json.dumps(audit, indent=2), encoding='utf-8')
        
        return audit

    def _validate_outputs(self, audit: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate all output files."""
        valid = []
        invalid = []
        
        for output_info in audit["outputs"]:
            file = output_info if isinstance(output_info, str) else output_info.get('name')
            path = self.outputs / file
            
            try:
                # Validate based on file type
                if file.endswith(".yaml"):
                    yaml.safe_load(path.read_text(encoding='utf-8'))
                    valid.append(file)
                elif file.endswith(".md"):
                    content = path.read_text(encoding='utf-8')
                    assert len(content) > 0, "Empty file"
                    valid.append(file)
                elif file.endswith(".json"):
                    json.loads(path.read_text(encoding='utf-8'))
                    valid.append(file)
                else:
                    # Unknown type, just check it exists and has content
                    assert path.stat().st_size > 0
                    valid.append(file)
                    
            except Exception as e:
                invalid.append(f"{file} ({e})")
        
        report = {
            "valid": valid,
            "invalid": invalid,
            "timestamp": self.session_id,
        }
        
        # Write validation report
        validation_path = self.report_dir / f"validation_report_{self.session_id}.md"
        validation_text = (
            f"# Validation Report — {self.session_id}\n\n"
            f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC  \n\n"
            f"**Valid Files:** {len(valid)}  \n"
            f"**Invalid Files:** {len(invalid)}  \n\n"
            f"---\n\n"
            f"### ✅ Valid Files\n\n"
        )
        
        for v in valid:
            validation_text += f"- ✅ {v}\n"
        
        if invalid:
            validation_text += "\n### ❌ Invalid Files\n\n"
            for i in invalid:
                validation_text += f"- ❌ {i}\n"
        else:
            validation_text += "\n---\n\n**All files valid!** ✅\n"
        
        validation_path.write_text(validation_text, encoding='utf-8')
        
        return report

    def _write_summary(self, audit: Dict[str, Any], validation: Dict[str, List[str]]):
        """Generate build summary report."""
        summary_path = self.report_dir / f"build_summary_{self.session_id}.md"
        
        text = f"# Build Summary — {self.session_id}\n\n"
        text += f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC  \n\n"
        text += "---\n\n"
        
        # Outputs section
        text += "## 📁 Outputs Generated\n\n"
        for output in audit["outputs"]:
            if isinstance(output, dict):
                name = output['name']
                size = output.get('size', 0)
                text += f"- {name} ({size} bytes)\n"
            else:
                text += f"- {output}\n"
        
        text += "\n---\n\n"
        
        # Logs section
        text += "## 📋 Logs Collected\n\n"
        for log in audit["logs"]:
            text += f"- {log}\n"
        
        text += "\n---\n\n"
        
        # Validation section
        text += "## ✅ Validation Results\n\n"
        text += f"**Valid:** {len(validation['valid'])}  \n"
        text += f"**Invalid:** {len(validation['invalid'])}  \n\n"
        
        if validation['invalid']:
            text += "**Issues:**\n"
            for issue in validation['invalid']:
                text += f"- ❌ {issue}\n"
        else:
            text += "**All outputs validated successfully!** ✅\n"
        
        text += "\n---\n\n"
        text += f"**Generated by:** Reporting Agent v1.0  \n"
        
        summary_path.write_text(text, encoding='utf-8')
        print(f"📄 Build summary: {summary_path}")

    def _archive_old(self) -> int:
        """Archive files older than archive_days."""
        cutoff = datetime.utcnow() - timedelta(days=self.archive_days)
        archived_count = 0
        
        for folder in [self.outputs, self.logs]:
            if not folder.exists():
                continue
                
            for f in folder.glob("*"):
                if not f.is_file():
                    continue
                    
                # Skip reports directory and important files
                if 'reports' in str(f) or 'PHASE' in f.name or 'SYSTEM' in f.name:
                    continue
                
                # Check age
                file_time = datetime.fromtimestamp(f.stat().st_mtime)
                if file_time < cutoff:
                    # Archive
                    archive_dir = folder / "archive"
                    archive_dir.mkdir(exist_ok=True, parents=True)
                    
                    try:
                        shutil.move(str(f), archive_dir / f.name)
                        archived_count += 1
                    except Exception:
                        pass  # Skip if can't move
        
        return archived_count


# ==============================================
# Test Execution
# ==============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("📊 REPORTING AGENT - PHASE 6")
    print("=" * 70 + "\n")
    
    agent = ReportingAgent()
    
    try:
        result = agent.run()
        
        print(f"\n✅ Reporting complete!")
        print(f"\n📊 Results:")
        print(f"   - Outputs audited: {len(result['audit']['outputs'])}")
        print(f"   - Logs found: {len(result['audit']['logs'])}")
        print(f"   - Valid files: {len(result['validation']['valid'])}")
        print(f"   - Invalid files: {len(result['validation']['invalid'])}")
        print(f"   - Files archived: {result['archived']}")
        
        print("\n" + "=" * 70)
        print("✅ REPORTING AGENT TEST COMPLETE")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()

