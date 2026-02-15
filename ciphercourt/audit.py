"""
Main audit framework for CipherCourt.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from ciphercourt.connectors.base import DataConnector
from ciphercourt.connectors.match_results import MatchResultsConnector
from ciphercourt.connectors.match_stats import MatchStatsConnector
from ciphercourt.connectors.odds import OddsConnector
from ciphercourt.connectors.venue import VenueConnector
from ciphercourt.connectors.license import LicenseConnector


class AuditFramework:
    """
    Main audit framework that coordinates all data connectors.
    
    This framework:
    - Manages multiple data source connectors
    - Coordinates audit execution
    - Aggregates results across all sources
    - Identifies critical issues
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the audit framework.
        
        Args:
            config: Configuration dictionary for all connectors
        """
        self.config = config or {}
        self.connectors: List[DataConnector] = []
        self._initialize_connectors()
        
    def _initialize_connectors(self):
        """Initialize all data connectors based on configuration."""
        # Initialize match results connector
        match_results_config = self.config.get("match_results", {})
        self.connectors.append(MatchResultsConnector(match_results_config))
        
        # Initialize match stats connector
        match_stats_config = self.config.get("match_stats", {})
        self.connectors.append(MatchStatsConnector(match_stats_config))
        
        # Initialize odds connector
        odds_config = self.config.get("odds", {})
        self.connectors.append(OddsConnector(odds_config))
        
        # Initialize venue connector
        venue_config = self.config.get("venue", {})
        self.connectors.append(VenueConnector(venue_config))
        
        # Initialize license connector
        license_config = self.config.get("license", {})
        self.connectors.append(LicenseConnector(license_config))
    
    def run_audit(self, connectors: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run audit across all or specified connectors.
        
        Args:
            connectors: Optional list of connector names to audit.
                       If None, audits all connectors.
        
        Returns:
            Comprehensive audit report
        """
        audit_start = datetime.utcnow()
        
        results = {
            "audit_framework": "CipherCourt",
            "audit_timestamp": audit_start.isoformat(),
            "connectors_audited": [],
            "results": {},
            "summary": {}
        }
        
        # Run audit for each connector
        for connector in self.connectors:
            source_name = connector.get_source_name()
            
            # Skip if specific connectors requested and this isn't one
            if connectors and source_name not in connectors:
                continue
            
            results["connectors_audited"].append(source_name)
            results["results"][source_name] = connector.run_full_audit()
        
        audit_end = datetime.utcnow()
        
        # Generate summary
        results["summary"] = self._generate_summary(results["results"])
        results["total_audit_duration_seconds"] = (audit_end - audit_start).total_seconds()
        
        return results
    
    def _generate_summary(self, audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of audit results."""
        summary = {
            "total_connectors": len(audit_results),
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "not_available": 0,
            "critical_issues": [],
            "all_issues": []
        }
        
        for source, result in audit_results.items():
            status = result.get("overall_status", "unknown")
            
            if status == "pass":
                summary["passed"] += 1
            elif status == "fail":
                summary["failed"] += 1
                # Collect critical issues
                for check_type in ["availability", "data_quality", "timestamps", "leakage_check"]:
                    if check_type in result:
                        issues = result[check_type].get("issues", [])
                        for issue in issues:
                            summary["critical_issues"].append(f"{source}: {issue}")
            elif status == "warning":
                summary["warnings"] += 1
            elif status == "not_available":
                summary["not_available"] += 1
            
            # Collect all issues
            for check_type in ["availability", "data_quality", "timestamps", "leakage_check"]:
                if check_type in result:
                    issues = result[check_type].get("issues", [])
                    for issue in issues:
                        summary["all_issues"].append(f"{source}.{check_type}: {issue}")
        
        return summary
    
    def get_connector(self, source_name: str) -> Optional[DataConnector]:
        """Get a specific connector by name."""
        for connector in self.connectors:
            if connector.get_source_name() == source_name:
                return connector
        return None
    
    def list_connectors(self) -> List[str]:
        """List all available connector names."""
        return [connector.get_source_name() for connector in self.connectors]
