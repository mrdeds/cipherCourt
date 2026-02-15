"""
Pre-match odds connector with timestamp tracking.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from ciphercourt.connectors.base import DataConnector, AuditStatus


class OddsConnector(DataConnector):
    """
    Connector for auditing pre-match odds snapshots.
    
    Critical for preventing look-ahead bias:
    - Validates odds are truly pre-match
    - Tracks odds snapshot timestamps
    - Detects odds appearing after match start
    - Monitors odds movement patterns
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.bookmakers = config.get("bookmakers", []) if config else []
        self.data_path = config.get("data_path") if config else None
        
    def get_source_name(self) -> str:
        return "pre_match_odds"
    
    def check_availability(self) -> Dict[str, Any]:
        """Check if odds data is available."""
        result = {
            "status": AuditStatus.PASS.value,
            "bookmakers_checked": self.bookmakers if self.bookmakers else ["generic"],
            "details": {},
            "issues": []
        }
        
        bookmakers_to_check = self.bookmakers if self.bookmakers else ["generic"]
        
        for bookmaker in bookmakers_to_check:
            availability = self._check_bookmaker_availability(bookmaker)
            result["details"][bookmaker] = {
                "available": availability,
                "last_snapshot": datetime.utcnow().isoformat() if availability else None
            }
            
            if not availability:
                result["issues"].append(f"{bookmaker} odds not available")
                result["status"] = AuditStatus.WARNING.value
        
        return result
    
    def audit_data_quality(self) -> Dict[str, Any]:
        """Audit quality of odds data."""
        result = {
            "status": AuditStatus.PASS.value,
            "checks": {},
            "issues": []
        }
        
        # Check for required fields
        required_fields = ["match_id", "snapshot_timestamp", "player1_odds", "player2_odds", "bookmaker"]
        result["checks"]["required_fields"] = {
            "expected": required_fields,
            "status": "pass"
        }
        
        # Check odds validity
        odds_validity = self._check_odds_validity()
        result["checks"]["odds_validity"] = odds_validity
        
        if odds_validity["invalid_count"] > 0:
            result["issues"].append(f"Found {odds_validity['invalid_count']} invalid odds values")
            result["status"] = AuditStatus.WARNING.value
        
        # Check snapshot completeness
        snapshot_completeness = self._check_snapshot_completeness()
        result["checks"]["snapshot_completeness"] = snapshot_completeness
        
        if snapshot_completeness["missing_snapshots"] > 0:
            result["issues"].append(f"Found {snapshot_completeness['missing_snapshots']} matches without odds snapshots")
            result["status"] = AuditStatus.WARNING.value
        
        return result
    
    def check_timestamps(self) -> Dict[str, Any]:
        """Verify odds snapshot timestamps are valid."""
        result = {
            "status": AuditStatus.PASS.value,
            "checks": {},
            "issues": []
        }
        
        # Check snapshot timing
        timing_check = self._check_snapshot_timing()
        result["checks"]["snapshot_timing"] = timing_check
        
        if timing_check["late_snapshots"] > 0:
            result["issues"].append(f"Found {timing_check['late_snapshots']} snapshots taken too close to match start")
            result["status"] = AuditStatus.WARNING.value
        
        # Check timestamp chronology
        chronology = self._check_timestamp_chronology()
        result["checks"]["chronology"] = chronology
        
        if not chronology["is_chronological"]:
            result["issues"].append("Timestamp chronology issues detected")
            result["status"] = AuditStatus.WARNING.value
        
        return result
    
    def detect_leakage(self) -> Dict[str, Any]:
        """Detect potential look-ahead bias in odds data."""
        result = {
            "status": AuditStatus.PASS.value,
            "checks": {},
            "issues": []
        }
        
        # Check for post-match odds
        post_match_check = self._check_post_match_odds()
        result["checks"]["post_match_odds"] = post_match_check
        
        if post_match_check["post_match_count"] > 0:
            result["issues"].append(f"CRITICAL: Found {post_match_check['post_match_count']} odds snapshots after match start")
            result["status"] = AuditStatus.FAIL.value
        
        # Check for suspicious odds movements
        suspicious_movements = self._check_suspicious_movements()
        result["checks"]["suspicious_movements"] = suspicious_movements
        
        if suspicious_movements["suspicious_count"] > 0:
            result["issues"].append(f"Found {suspicious_movements['suspicious_count']} suspicious odds movements")
            result["status"] = AuditStatus.WARNING.value
        
        return result
    
    def _check_bookmaker_availability(self, bookmaker: str) -> bool:
        """Check if specific bookmaker data is available."""
        # Placeholder
        return True
    
    def _check_odds_validity(self) -> Dict[str, Any]:
        """Check if odds values are valid."""
        # Placeholder - would verify odds are > 1.0, sum properly, etc.
        return {
            "total_odds": 5000,
            "valid_odds": 4995,
            "invalid_count": 5,
            "validity_rate": 0.999
        }
    
    def _check_snapshot_completeness(self) -> Dict[str, Any]:
        """Check completeness of odds snapshots."""
        # Placeholder
        return {
            "total_matches": 1000,
            "matches_with_odds": 980,
            "missing_snapshots": 20,
            "coverage_rate": 0.98
        }
    
    def _check_snapshot_timing(self) -> Dict[str, Any]:
        """Check timing of odds snapshots relative to matches."""
        # Placeholder - would verify snapshots are taken before match start
        return {
            "total_snapshots": 4900,
            "early_snapshots": 4850,
            "late_snapshots": 50,
            "average_lead_time_hours": 2.5
        }
    
    def _check_timestamp_chronology(self) -> Dict[str, Any]:
        """Check if timestamps are in chronological order."""
        # Placeholder
        return {
            "is_chronological": True,
            "out_of_order_count": 0
        }
    
    def _check_post_match_odds(self) -> Dict[str, Any]:
        """Check for odds appearing after match start (critical leakage)."""
        # Placeholder
        return {
            "post_match_count": 0,
            "total_checked": 4900
        }
    
    def _check_suspicious_movements(self) -> Dict[str, Any]:
        """Check for suspicious odds movements."""
        # Placeholder - would detect unusual patterns
        return {
            "suspicious_count": 5,
            "total_movements_checked": 15000,
            "movement_threshold": 0.20
        }
