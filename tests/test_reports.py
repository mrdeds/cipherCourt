"""
Tests for report generators.
"""

import pytest
import json
from ciphercourt.audit import AuditFramework
from ciphercourt.reports import (
    JSONReportGenerator,
    CSVReportGenerator,
    MarkdownReportGenerator,
    generate_reports
)


def test_json_report_generator():
    """Test JSON report generation."""
    framework = AuditFramework()
    results = framework.run_audit()
    
    generator = JSONReportGenerator(results)
    json_str = generator.to_string()
    
    # Verify it's valid JSON
    parsed = json.loads(json_str)
    assert parsed["audit_framework"] == "CipherCourt"
    assert "results" in parsed


def test_csv_report_generator():
    """Test CSV report generation."""
    framework = AuditFramework()
    results = framework.run_audit()
    
    generator = CSVReportGenerator(results)
    csv_str = generator.to_string()
    
    # Verify CSV has header and data
    lines = csv_str.strip().split('\n')
    assert len(lines) > 1  # At least header + 1 data row
    
    # Check header
    header = lines[0]
    assert "Source" in header
    assert "Overall Status" in header


def test_markdown_report_generator():
    """Test Markdown report generation."""
    framework = AuditFramework()
    results = framework.run_audit()
    
    generator = MarkdownReportGenerator(results)
    md_str = generator.to_string()
    
    # Verify Markdown structure
    assert "# CipherCourt Audit Report" in md_str
    assert "## Summary" in md_str
    assert "## Detailed Results" in md_str


def test_generate_all_reports(tmp_path):
    """Test generating all report formats."""
    framework = AuditFramework()
    results = framework.run_audit()
    
    generated = generate_reports(results, output_dir=str(tmp_path))
    
    # Should generate all three formats by default
    assert "json" in generated
    assert "csv" in generated
    assert "markdown" in generated
    
    # Verify files exist
    for path in generated.values():
        assert tmp_path / path.split('/')[-1] in tmp_path.iterdir()


def test_generate_specific_formats(tmp_path):
    """Test generating specific report formats."""
    framework = AuditFramework()
    results = framework.run_audit()
    
    generated = generate_reports(
        results,
        output_dir=str(tmp_path),
        formats=["json", "markdown"]
    )
    
    assert "json" in generated
    assert "markdown" in generated
    assert "csv" not in generated


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
