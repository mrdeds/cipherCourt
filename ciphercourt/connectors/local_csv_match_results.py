"""
Local CSV-based match results connector.
"""

import csv
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from ciphercourt.connectors.base import DataConnector, AuditStatus


class LocalCSVMatchResultsConnector(DataConnector):
    """
    Connector for auditing match results from local CSV files.
    
    CSV Schema:
    - match_id: Unique identifier for the match
    - date: Match date
    - tournament: Tournament name
    - circuit: ATP/Challenger/ITF
    - player1: First player name
    - player2: Second player name
    - score: Match score
    - winner: Winner name
    - match_start_time: ISO 8601 timestamp when match started
    - available_at: ISO 8601 timestamp when data became available
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.csv_path = config.get("csv_path") if config else None
        self.data = []
        self._load_data()
        
    def _load_data(self):
        """Load match results from CSV file."""
        if not self.csv_path:
            return
            
        csv_file = Path(self.csv_path)
        if not csv_file.exists():
            return
            
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            self.data = list(reader)
    
    def get_source_name(self) -> str:
        return "local_csv_match_results"
    
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
        
        return result
    
    def audit_data_quality(self) -> Dict[str, Any]:
        """Audit quality of match results data."""
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
            "match_id", "date", "tournament", "circuit",
            "player1", "player2", "score", "winner",
            "match_start_time", "available_at"
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
            "total_records": len(self.data),
            "complete_records": len(self.data) - incomplete_count,
            "incomplete_count": incomplete_count,
            "completeness_rate": (len(self.data) - incomplete_count) / len(self.data)
        }
        
        if incomplete_count > 0:
            result["status"] = AuditStatus.WARNING.value
            result["issues"].append(f"Found {incomplete_count} incomplete records")
        
        # Check for duplicates
        match_ids = [row.get("match_id") for row in self.data]
        unique_ids = set(match_ids)
        duplicate_count = len(match_ids) - len(unique_ids)
        
        result["checks"]["duplicates"] = {
            "total_records": len(self.data),
            "unique_records": len(unique_ids),
            "duplicate_count": duplicate_count
        }
        
        if duplicate_count > 0:
            result["status"] = AuditStatus.WARNING.value
            result["issues"].append(f"Found {duplicate_count} duplicate match IDs")
        
        # Check circuit values
        valid_circuits = {"ATP", "Challenger", "ITF"}
        invalid_circuits = []
        for row in self.data:
            circuit = row.get("circuit", "")
            if circuit and circuit not in valid_circuits:
                invalid_circuits.append(circuit)
        
        if invalid_circuits:
            result["status"] = AuditStatus.WARNING.value
            result["issues"].append(f"Found invalid circuit values: {set(invalid_circuits)}")
        
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
        out_of_order = []
        
        for row in self.data:
            match_id = row.get("match_id")
            match_start = row.get("match_start_time")
            available_at = row.get("available_at")
            
            # Validate timestamp format
            try:
                if match_start:
                    datetime.fromisoformat(match_start.replace('Z', '+00:00'))
            except ValueError:
                invalid_timestamps.append(f"{match_id}: invalid match_start_time")
            
            try:
                if available_at:
                    datetime.fromisoformat(available_at.replace('Z', '+00:00'))
            except ValueError:
                invalid_timestamps.append(f"{match_id}: invalid available_at")
            
            # Check temporal ordering (available_at should be before match_start_time)
            try:
                if match_start and available_at:
                    start_dt = datetime.fromisoformat(match_start.replace('Z', '+00:00'))
                    avail_dt = datetime.fromisoformat(available_at.replace('Z', '+00:00'))
                    if avail_dt > start_dt:
                        out_of_order.append(f"{match_id}: available_at after match_start_time")
            except ValueError:
                pass
        
        result["checks"]["timestamp_format"] = {
            "invalid_count": len(invalid_timestamps),
            "examples": invalid_timestamps[:5] if invalid_timestamps else []
        }
        
        result["checks"]["temporal_ordering"] = {
            "out_of_order_count": len(out_of_order),
            "examples": out_of_order[:5] if out_of_order else []
        }
        
        if invalid_timestamps:
            result["status"] = AuditStatus.FAIL.value
            result["issues"].append(f"Found {len(invalid_timestamps)} invalid timestamps")
        
        if out_of_order:
            result["status"] = AuditStatus.WARNING.value
            result["issues"].append(f"Found {len(out_of_order)} records with temporal ordering issues")
        
        return result
    
    def detect_leakage(self) -> Dict[str, Any]:
        """Detect potential data leakage."""
        result = {
            "status": AuditStatus.PASS.value,
            "checks": {},
            "issues": []
        }
        
        if not self.data:
            result["status"] = AuditStatus.NOT_AVAILABLE.value
            result["issues"].append("No data loaded")
            return result
        
        future_dates = []
        now = datetime.utcnow()
        
        for row in self.data:
            match_id = row.get("match_id")
            match_start = row.get("match_start_time")
            
            try:
                if match_start:
                    start_dt = datetime.fromisoformat(match_start.replace('Z', '+00:00'))
                    # Remove timezone for comparison
                    start_dt_naive = start_dt.replace(tzinfo=None)
                    if start_dt_naive > now:
                        future_dates.append(match_id)
            except ValueError:
                pass
        
        result["checks"]["future_dates"] = {
            "future_count": len(future_dates),
            "examples": future_dates[:5] if future_dates else []
        }
        
        if future_dates:
            result["status"] = AuditStatus.FAIL.value
            result["issues"].append(f"CRITICAL: Found {len(future_dates)} future-dated matches")
        
        return result
