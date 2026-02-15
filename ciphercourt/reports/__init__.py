"""
Report generators for CipherCourt audit results.
"""

import json
import csv
from typing import Dict, Any, List
from datetime import datetime
from io import StringIO
from pathlib import Path


class ReportGenerator:
    """Base class for report generators."""
    
    def __init__(self, audit_results: Dict[str, Any]):
        """
        Initialize report generator.
        
        Args:
            audit_results: Audit results dictionary from AuditFramework
        """
        self.audit_results = audit_results
    
    def generate(self, output_path: str) -> str:
        """
        Generate report and save to file.
        
        Args:
            output_path: Path to save the report
            
        Returns:
            Path to generated report
        """
        raise NotImplementedError


class JSONReportGenerator(ReportGenerator):
    """Generate audit reports in JSON format."""
    
    def generate(self, output_path: str) -> str:
        """Generate JSON report."""
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.audit_results, f, indent=2)
        return output_path
    
    def to_string(self) -> str:
        """Return report as JSON string."""
        return json.dumps(self.audit_results, indent=2)


class CSVReportGenerator(ReportGenerator):
    """Generate audit reports in CSV format."""
    
    def generate(self, output_path: str) -> str:
        """Generate CSV report."""
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            self._write_csv(writer)
        return output_path
    
    def to_string(self) -> str:
        """Return report as CSV string."""
        output = StringIO()
        writer = csv.writer(output)
        self._write_csv(writer)
        return output.getvalue()
    
    def _write_csv(self, writer):
        """Write CSV content."""
        # Header
        writer.writerow([
            "Source",
            "Overall Status",
            "Availability Status",
            "Data Quality Status",
            "Timestamps Status",
            "Leakage Check Status",
            "Issues"
        ])
        
        # Data rows
        results = self.audit_results.get("results", {})
        for source, result in results.items():
            issues = []
            for check_type in ["availability", "data_quality", "timestamps", "leakage_check"]:
                if check_type in result:
                    issues.extend(result[check_type].get("issues", []))
            
            writer.writerow([
                source,
                result.get("overall_status", "unknown"),
                result.get("availability", {}).get("status", "unknown"),
                result.get("data_quality", {}).get("status", "unknown"),
                result.get("timestamps", {}).get("status", "unknown"),
                result.get("leakage_check", {}).get("status", "unknown"),
                "; ".join(issues) if issues else "None"
            ])


class MarkdownReportGenerator(ReportGenerator):
    """Generate audit reports in Markdown format."""
    
    def generate(self, output_path: str) -> str:
        """Generate Markdown report."""
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(self._generate_markdown())
        return output_path
    
    def to_string(self) -> str:
        """Return report as Markdown string."""
        return self._generate_markdown()
    
    def _generate_markdown(self) -> str:
        """Generate Markdown content."""
        lines = []
        
        # Title
        lines.append("# CipherCourt Audit Report")
        lines.append("")
        
        # Metadata
        audit_timestamp = self.audit_results.get("audit_timestamp", "unknown")
        lines.append(f"**Audit Timestamp:** {audit_timestamp}")
        lines.append(f"**Framework:** {self.audit_results.get('audit_framework', 'CipherCourt')}")
        duration = self.audit_results.get("total_audit_duration_seconds", 0)
        lines.append(f"**Audit Duration:** {duration:.2f} seconds")
        lines.append("")
        
        # Summary
        summary = self.audit_results.get("summary", {})
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total Connectors:** {summary.get('total_connectors', 0)}")
        lines.append(f"- **Passed:** {summary.get('passed', 0)}")
        lines.append(f"- **Failed:** {summary.get('failed', 0)}")
        lines.append(f"- **Warnings:** {summary.get('warnings', 0)}")
        lines.append(f"- **Not Available:** {summary.get('not_available', 0)}")
        lines.append("")
        
        # Critical Issues
        critical_issues = summary.get("critical_issues", [])
        if critical_issues:
            lines.append("### ⚠️ Critical Issues")
            lines.append("")
            for issue in critical_issues:
                lines.append(f"- {issue}")
            lines.append("")
        
        # Detailed Results
        lines.append("## Detailed Results")
        lines.append("")
        
        results = self.audit_results.get("results", {})
        for source, result in results.items():
            lines.append(f"### {source}")
            lines.append("")
            
            # Overall status
            status = result.get("overall_status", "unknown")
            status_emoji = self._get_status_emoji(status)
            lines.append(f"**Overall Status:** {status_emoji} {status.upper()}")
            lines.append("")
            
            # Availability
            lines.append("#### Availability")
            self._add_check_details(lines, result.get("availability", {}))
            lines.append("")
            
            # Data Quality
            lines.append("#### Data Quality")
            self._add_check_details(lines, result.get("data_quality", {}))
            lines.append("")
            
            # Timestamps
            lines.append("#### Timestamps")
            self._add_check_details(lines, result.get("timestamps", {}))
            lines.append("")
            
            # Leakage Check
            lines.append("#### Leakage Detection")
            self._add_check_details(lines, result.get("leakage_check", {}))
            lines.append("")
            
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
    
    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for status."""
        emoji_map = {
            "pass": "✅",
            "fail": "❌",
            "warning": "⚠️",
            "not_available": "❓"
        }
        return emoji_map.get(status.lower(), "❔")
    
    def _add_check_details(self, lines: List[str], check: Dict[str, Any]):
        """Add check details to lines."""
        status = check.get("status", "unknown")
        status_emoji = self._get_status_emoji(status)
        lines.append(f"**Status:** {status_emoji} {status.upper()}")
        
        issues = check.get("issues", [])
        if issues:
            lines.append("")
            lines.append("**Issues:**")
            for issue in issues:
                lines.append(f"- {issue}")


def generate_reports(audit_results: Dict[str, Any], 
                     output_dir: str = ".",
                     formats: List[str] = None) -> Dict[str, str]:
    """
    Generate audit reports in multiple formats with specific filenames.
    
    Args:
        audit_results: Audit results from AuditFramework
        output_dir: Directory to save reports
        formats: List of formats to generate (json, csv, markdown)
                If None, generates all formats
    
    Returns:
        Dictionary mapping format to output path
    """
    if formats is None:
        formats = ["json", "csv", "markdown"]
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    generated_reports = {}
    
    for fmt in formats:
        if fmt == "json":
            generator = JSONReportGenerator(audit_results)
            output_path = f"{output_dir}/audit_summary.json"
            generated_reports["json"] = generator.generate(output_path)
        
        elif fmt == "csv":
            generator = CSVReportGenerator(audit_results)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = f"{output_dir}/audit_report_{timestamp}.csv"
            generated_reports["csv"] = generator.generate(output_path)
        
        elif fmt == "markdown":
            generator = MarkdownReportGenerator(audit_results)
            output_path = f"{output_dir}/audit_report.md"
            generated_reports["markdown"] = generator.generate(output_path)
    
    return generated_reports
