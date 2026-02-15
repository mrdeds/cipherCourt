"""
Tests for local CSV connectors.
"""

import pytest
from pathlib import Path
from ciphercourt.connectors.local_csv_match_results import LocalCSVMatchResultsConnector
from ciphercourt.connectors.local_csv_odds import LocalCSVOddsConnector
from ciphercourt.connectors.base import AuditStatus


def test_local_csv_match_results_connector():
    """Test LocalCSVMatchResultsConnector with sample data."""
    config = {
        "csv_path": "data/samples/match_results.csv"
    }
    
    connector = LocalCSVMatchResultsConnector(config)
    
    # Check that data was loaded
    assert len(connector.data) > 0
    
    # Run availability check
    availability = connector.check_availability()
    assert availability["status"] == AuditStatus.PASS.value
    assert availability["details"]["records_loaded"] > 0
    
    # Run data quality check
    quality = connector.audit_data_quality()
    assert quality["status"] in [AuditStatus.PASS.value, AuditStatus.WARNING.value]
    
    # Run timestamp check
    timestamps = connector.check_timestamps()
    assert timestamps["status"] in [AuditStatus.PASS.value, AuditStatus.WARNING.value]
    
    # Run leakage detection
    leakage = connector.detect_leakage()
    assert leakage["status"] in [AuditStatus.PASS.value, AuditStatus.FAIL.value]


def test_local_csv_odds_connector_no_leakage():
    """Test LocalCSVOddsConnector with clean data."""
    config = {
        "csv_path": "data/samples/odds.csv"
    }
    
    connector = LocalCSVOddsConnector(config)
    
    # Check that data was loaded
    assert len(connector.data) > 0
    
    # Run full audit
    result = connector.run_full_audit()
    
    # Should pass all checks with clean data
    assert result["overall_status"] == AuditStatus.PASS.value
    assert result["leakage_check"]["status"] == AuditStatus.PASS.value


def test_local_csv_odds_connector_with_leakage():
    """Test LocalCSVOddsConnector detects leakage."""
    config = {
        "csv_path": "data/samples/odds_with_leakage.csv"
    }
    
    connector = LocalCSVOddsConnector(config)
    
    # Run leakage detection
    leakage = connector.detect_leakage()
    
    # Should FAIL due to post-match odds
    assert leakage["status"] == AuditStatus.FAIL.value
    assert leakage["checks"]["post_match_odds"]["post_match_count"] > 0
    assert "CRITICAL LEAKAGE DETECTED" in leakage["issues"][0]


def test_audit_output_files_created():
    """Test that audit outputs are created in correct directory."""
    from ciphercourt.audit import AuditFramework
    from ciphercourt.reports import generate_reports
    
    config = {
        "local_csv_match_results": {
            "csv_path": "data/samples/match_results.csv"
        },
        "local_csv_odds": {
            "csv_path": "data/samples/odds.csv"
        }
    }
    
    framework = AuditFramework(config)
    results = framework.run_audit(connectors=["local_csv_match_results", "local_csv_odds"])
    
    # Generate reports
    output_dir = "data/audit_outputs"
    generated = generate_reports(results, output_dir=output_dir, formats=["json", "markdown"])
    
    # Verify files were created
    assert "json" in generated
    assert "markdown" in generated
    
    json_path = Path(generated["json"])
    md_path = Path(generated["markdown"])
    
    assert json_path.exists()
    assert md_path.exists()
    assert json_path.name == "audit_summary.json"
    assert md_path.name == "audit_report.md"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
