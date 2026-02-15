"""
Match statistics connector for detailed match-level stats.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from ciphercourt.connectors.base import DataConnector, AuditStatus


class MatchStatsConnector(DataConnector):
    """
    Connector for auditing match statistics data.
    
    Validates:
    - Availability of detailed match stats
    - Stats completeness (aces, double faults, break points, etc.)
    - Timestamp alignment with match results
    - Statistical consistency and reasonableness
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.data_path = config.get("data_path") if config else None
        
    def get_source_name(self) -> str:
        return "match_stats"
    
    def check_availability(self) -> Dict[str, Any]:
        """Check if match stats data is available."""
        result = {
            "status": AuditStatus.PASS.value,
            "details": {
                "data_source_available": True,
                "last_update": datetime.utcnow().isoformat()
            },
            "issues": []
        }
        
        # In production, would check actual data source
        stats_available = self._check_stats_availability()
        
        if not stats_available:
            result["status"] = AuditStatus.NOT_AVAILABLE.value
            result["details"]["data_source_available"] = False
            result["issues"].append("Match stats data source not available")
        
        return result
    
    def audit_data_quality(self) -> Dict[str, Any]:
        """Audit quality of match statistics."""
        result = {
            "status": AuditStatus.PASS.value,
            "checks": {},
            "issues": []
        }
        
        # Check for required stat fields
        required_stats = [
            "aces", "double_faults", "first_serve_pct",
            "first_serve_points_won", "second_serve_points_won",
            "break_points_faced", "break_points_saved",
            "service_games", "return_games"
        ]
        result["checks"]["required_stats"] = {
            "expected": required_stats,
            "status": "pass"
        }
        
        # Check stats completeness
        completeness = self._check_stats_completeness()
        result["checks"]["completeness"] = completeness
        
        if completeness["missing_stats_count"] > 0:
            result["issues"].append(f"Found {completeness['missing_stats_count']} matches with incomplete stats")
            result["status"] = AuditStatus.WARNING.value
        
        # Check statistical consistency
        consistency = self._check_statistical_consistency()
        result["checks"]["consistency"] = consistency
        
        if consistency["inconsistencies"] > 0:
            result["issues"].append(f"Found {consistency['inconsistencies']} statistical inconsistencies")
            result["status"] = AuditStatus.WARNING.value
        
        return result
    
    def check_timestamps(self) -> Dict[str, Any]:
        """Verify timestamp alignment with match results."""
        result = {
            "status": AuditStatus.PASS.value,
            "checks": {},
            "issues": []
        }
        
        # Check alignment with match results
        alignment = self._check_timestamp_alignment()
        result["checks"]["match_result_alignment"] = alignment
        
        if alignment["misaligned_count"] > 0:
            result["issues"].append(f"Found {alignment['misaligned_count']} stats with misaligned timestamps")
            result["status"] = AuditStatus.WARNING.value
        
        return result
    
    def detect_leakage(self) -> Dict[str, Any]:
        """Detect potential data leakage in match stats."""
        result = {
            "status": AuditStatus.PASS.value,
            "checks": {},
            "issues": []
        }
        
        # Check for stats appearing before match completion
        premature_check = self._check_premature_stats()
        result["checks"]["premature_stats"] = premature_check
        
        if premature_check["premature_count"] > 0:
            result["issues"].append(f"Found {premature_check['premature_count']} stats appearing before match completion")
            result["status"] = AuditStatus.FAIL.value
        
        return result
    
    def _check_stats_availability(self) -> bool:
        """Check if stats data source is available."""
        # Placeholder
        return True
    
    def _check_stats_completeness(self) -> Dict[str, Any]:
        """Check completeness of match statistics."""
        # Placeholder
        return {
            "total_matches": 1000,
            "matches_with_stats": 950,
            "missing_stats_count": 50,
            "coverage_rate": 0.95
        }
    
    def _check_statistical_consistency(self) -> Dict[str, Any]:
        """Check for statistical inconsistencies."""
        # Placeholder - would verify stats like aces <= total service points
        return {
            "total_matches_checked": 950,
            "inconsistencies": 3,
            "consistency_rate": 0.997
        }
    
    def _check_timestamp_alignment(self) -> Dict[str, Any]:
        """Check timestamp alignment with match results."""
        # Placeholder
        return {
            "total_matches": 950,
            "aligned_count": 948,
            "misaligned_count": 2
        }
    
    def _check_premature_stats(self) -> Dict[str, Any]:
        """Check for stats appearing before match completion."""
        # Placeholder
        return {
            "premature_count": 0,
            "total_checked": 950
        }
