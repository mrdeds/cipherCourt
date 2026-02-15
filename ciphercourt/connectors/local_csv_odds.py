"""
Local CSV-based odds connector with strict leakage detection.
"""

import csv
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from ciphercourt.connectors.base import DataConnector, AuditStatus


class LocalCSVOddsConnector(DataConnector):
    """
    Connector for auditing pre-match odds from local CSV files.
    
    CSV Schema:
    - match_id: Match identifier
    - snapshot_timestamp: When odds snapshot was taken
    - player1_odds: Odds for player 1
    - player2_odds: Odds for player 2
    - bookmaker: Bookmaker name
    - available_at: ISO 8601 timestamp when odds became available
    - match_start_time: ISO 8601 timestamp when match started
    
    CRITICAL: Implements hard FAIL rules for odds appearing after match_start_time
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.csv_path = config.get("csv_path") if config else None
        self.data = []
        self._load_data()
        
    def _load_data(self):
        """Load odds data from CSV file."""
        if not self.csv_path:
            return
            
        csv_file = Path(self.csv_path)
        if not csv_file.exists():
            return
            
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            self.data = list(reader)
    
    def get_source_name(self) -> str:
        return "local_csv_odds"
    
    def check_availability(self) -> Dict[str, Any]:
        """Check if CSV file is available and readable."""
        result = {
            "status": AuditStatus.PASS.value,
            "details": {},
            "issues": []
        }
        
        if not self.csv_path:
            result["status"] = AuditStatus.NOT_AVAILABLE.value
            result["issues"].append("No CSV path configured")
            return result
        
        csv_file = Path(self.csv_path)
        if not csv_file.exists():
            result["status"] = AuditStatus.NOT_AVAILABLE.value
            result["issues"].append(f"CSV file not found: {self.csv_path}")
            return result
        
        result["details"]["csv_path"] = str(self.csv_path)
        result["details"]["records_loaded"] = len(self.data)
        result["details"]["file_size_bytes"] = csv_file.stat().st_size
        
        # Count unique matches
        unique_matches = len(set(row.get("match_id") for row in self.data if row.get("match_id")))
        result["details"]["unique_matches"] = unique_matches
        
        return result
    
    def audit_data_quality(self) -> Dict[str, Any]:
        """Audit quality of odds data."""
        result = {
            "status": AuditStatus.PASS.value,
            "checks": {},
            "issues": []
        }
        
        if not self.data:
            result["status"] = AuditStatus.NOT_AVAILABLE.value
            result["issues"].append("No data loaded")
            return result
        
        # Check for required fields
        required_fields = [
            "match_id", "snapshot_timestamp", "player1_odds", "player2_odds",
            "bookmaker", "available_at", "match_start_time"
        ]
        
        missing_fields = []
        if self.data:
            first_row = self.data[0]
            missing_fields = [f for f in required_fields if f not in first_row]
        
        result["checks"]["required_fields"] = {
            "expected": required_fields,
            "missing": missing_fields,
            "status": "pass" if not missing_fields else "fail"
        }
        
        if missing_fields:
            result["status"] = AuditStatus.FAIL.value
            result["issues"].append(f"Missing required fields: {', '.join(missing_fields)}")
            return result
        
        # Check completeness
        incomplete_count = 0
        for row in self.data:
            if any(not row.get(field) for field in required_fields):
                incomplete_count += 1
        
        result["checks"]["completeness"] = {
            "total_snapshots": len(self.data),
            "complete_snapshots": len(self.data) - incomplete_count,
            "incomplete_count": incomplete_count,
            "completeness_rate": (len(self.data) - incomplete_count) / len(self.data) if self.data else 0
        }
        
        if incomplete_count > 0:
            result["status"] = AuditStatus.WARNING.value
            result["issues"].append(f"Found {incomplete_count} incomplete snapshots")
        
        # Validate odds values
        invalid_odds = []
        for row in self.data:
            match_id = row.get("match_id")
            try:
                p1_odds = float(row.get("player1_odds", 0))
                p2_odds = float(row.get("player2_odds", 0))
                
                if p1_odds < 1.0:
                    invalid_odds.append(f"{match_id}: player1_odds < 1.0")
                if p2_odds < 1.0:
                    invalid_odds.append(f"{match_id}: player2_odds < 1.0")
            except (ValueError, TypeError):
                invalid_odds.append(f"{match_id}: invalid odds format")
        
        result["checks"]["odds_validity"] = {
            "invalid_count": len(invalid_odds),
            "examples": invalid_odds[:5] if invalid_odds else []
        }
        
        if invalid_odds:
            result["status"] = AuditStatus.WARNING.value
            result["issues"].append(f"Found {len(invalid_odds)} invalid odds values")
        
        return result
    
    def check_timestamps(self) -> Dict[str, Any]:
        """Verify timestamp integrity."""
        result = {
            "status": AuditStatus.PASS.value,
            "checks": {},
            "issues": []
        }
        
        if not self.data:
            result["status"] = AuditStatus.NOT_AVAILABLE.value
            result["issues"].append("No data loaded")
            return result
        
        invalid_timestamps = []
        
        for row in self.data:
            match_id = row.get("match_id")
            snapshot_ts = row.get("snapshot_timestamp")
            available_at = row.get("available_at")
            match_start = row.get("match_start_time")
            
            # Validate timestamp format
            for field, value in [
                ("snapshot_timestamp", snapshot_ts),
                ("available_at", available_at),
                ("match_start_time", match_start)
            ]:
                try:
                    if value:
                        datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    invalid_timestamps.append(f"{match_id}: invalid {field}")
        
        result["checks"]["timestamp_format"] = {
            "invalid_count": len(invalid_timestamps),
            "examples": invalid_timestamps[:5] if invalid_timestamps else []
        }
        
        if invalid_timestamps:
            result["status"] = AuditStatus.FAIL.value
            result["issues"].append(f"Found {len(invalid_timestamps)} invalid timestamps")
        
        return result
    
    def detect_leakage(self) -> Dict[str, Any]:
        """
        Detect potential data leakage - HARD FAIL for post-match odds.
        
        This is the critical check that enforces odds must be taken before match start.
        Any odds snapshot with available_at >= match_start_time results in FAIL status.
        """
        result = {
            "status": AuditStatus.PASS.value,
            "checks": {},
            "issues": []
        }
        
        if not self.data:
            result["status"] = AuditStatus.NOT_AVAILABLE.value
            result["issues"].append("No data loaded")
            return result
        
        post_match_odds = []
        late_snapshots = []
        
        for row in self.data:
            match_id = row.get("match_id")
            snapshot_ts = row.get("snapshot_timestamp")
            available_at = row.get("available_at")
            match_start = row.get("match_start_time")
            
            try:
                if available_at and match_start:
                    avail_dt = datetime.fromisoformat(available_at.replace('Z', '+00:00'))
                    start_dt = datetime.fromisoformat(match_start.replace('Z', '+00:00'))
                    
                    # HARD FAIL: odds available at or after match start
                    if avail_dt >= start_dt:
                        post_match_odds.append({
                            "match_id": match_id,
                            "available_at": available_at,
                            "match_start_time": match_start,
                            "snapshot_timestamp": snapshot_ts,
                            "delay_seconds": (avail_dt - start_dt).total_seconds()
                        })
                
                # Also check snapshot timestamp
                if snapshot_ts and match_start:
                    snap_dt = datetime.fromisoformat(snapshot_ts.replace('Z', '+00:00'))
                    start_dt = datetime.fromisoformat(match_start.replace('Z', '+00:00'))
                    
                    if snap_dt >= start_dt:
                        late_snapshots.append({
                            "match_id": match_id,
                            "snapshot_timestamp": snapshot_ts,
                            "match_start_time": match_start
                        })
            except ValueError:
                # Skip records with invalid timestamps (caught in check_timestamps)
                pass
        
        result["checks"]["post_match_odds"] = {
            "post_match_count": len(post_match_odds),
            "violations": post_match_odds
        }
        
        result["checks"]["late_snapshots"] = {
            "late_count": len(late_snapshots),
            "examples": late_snapshots[:5] if late_snapshots else []
        }
        
        # HARD FAIL if any post-match odds detected
        if post_match_odds:
            result["status"] = AuditStatus.FAIL.value
            result["issues"].append(
                f"CRITICAL LEAKAGE DETECTED: {len(post_match_odds)} odds snapshots "
                f"have available_at >= match_start_time (look-ahead bias)"
            )
        
        if late_snapshots:
            if result["status"] != AuditStatus.FAIL.value:
                result["status"] = AuditStatus.FAIL.value
            result["issues"].append(
                f"CRITICAL LEAKAGE DETECTED: {len(late_snapshots)} odds snapshots "
                f"have snapshot_timestamp >= match_start_time"
            )
        
        return result
