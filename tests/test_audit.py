"""
Tests for CipherCourt audit framework.
"""

import pytest
from ciphercourt.audit import AuditFramework
from ciphercourt.connectors.base import AuditStatus


def test_audit_framework_initialization():
    """Test that audit framework initializes correctly."""
    framework = AuditFramework()
    assert framework is not None
    assert len(framework.connectors) == 5


def test_list_connectors():
    """Test listing available connectors."""
    framework = AuditFramework()
    connectors = framework.list_connectors()
    
    expected = [
        "match_results",
        "match_stats",
        "pre_match_odds",
        "venue_metadata",
        "license_status"
    ]
    
    assert set(connectors) == set(expected)


def test_run_full_audit():
    """Test running full audit."""
    framework = AuditFramework()
    results = framework.run_audit()
    
    assert "audit_framework" in results
    assert results["audit_framework"] == "CipherCourt"
    assert "audit_timestamp" in results
    assert "results" in results
    assert "summary" in results


def test_audit_results_structure():
    """Test that audit results have correct structure."""
    framework = AuditFramework()
    results = framework.run_audit()
    
    # Check summary structure
    summary = results["summary"]
    assert "total_connectors" in summary
    assert "passed" in summary
    assert "failed" in summary
    assert "warnings" in summary
    assert "not_available" in summary
    
    # Check individual connector results
    for connector_name, connector_result in results["results"].items():
        assert "source" in connector_result
        assert "audit_timestamp" in connector_result
        assert "availability" in connector_result
        assert "data_quality" in connector_result
        assert "timestamps" in connector_result
        assert "leakage_check" in connector_result
        assert "overall_status" in connector_result


def test_run_specific_connectors():
    """Test running audit on specific connectors."""
    framework = AuditFramework()
    results = framework.run_audit(connectors=["match_results", "match_stats"])
    
    assert len(results["connectors_audited"]) == 2
    assert "match_results" in results["connectors_audited"]
    assert "match_stats" in results["connectors_audited"]
    assert len(results["results"]) == 2


def test_custom_config():
    """Test audit framework with custom configuration."""
    config = {
        "match_results": {
            "circuits": ["ATP"],
            "data_path": "/test/path"
        }
    }
    
    framework = AuditFramework(config)
    assert framework.config == config
    
    # Get match results connector
    connector = framework.get_connector("match_results")
    assert connector is not None
    assert connector.circuits == ["ATP"]


def test_connector_audit_methods():
    """Test that each connector implements required methods."""
    framework = AuditFramework()
    
    for connector in framework.connectors:
        # Test that each method returns a dict
        availability = connector.check_availability()
        assert isinstance(availability, dict)
        assert "status" in availability
        
        quality = connector.audit_data_quality()
        assert isinstance(quality, dict)
        assert "status" in quality
        
        timestamps = connector.check_timestamps()
        assert isinstance(timestamps, dict)
        assert "status" in timestamps
        
        leakage = connector.detect_leakage()
        assert isinstance(leakage, dict)
        assert "status" in leakage


def test_audit_status_values():
    """Test that audit status values are valid."""
    framework = AuditFramework()
    results = framework.run_audit()
    
    valid_statuses = [s.value for s in AuditStatus]
    
    for connector_result in results["results"].values():
        assert connector_result["overall_status"] in valid_statuses
        assert connector_result["availability"]["status"] in valid_statuses
        assert connector_result["data_quality"]["status"] in valid_statuses
        assert connector_result["timestamps"]["status"] in valid_statuses
        assert connector_result["leakage_check"]["status"] in valid_statuses


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
