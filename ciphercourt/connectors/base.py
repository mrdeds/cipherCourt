"""
Base connector interface for data auditing.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class DataSource(Enum):
    """Enumeration of supported data sources."""
    ATP = "atp"
    CHALLENGER = "challenger"
    ITF = "itf"
    MATCH_STATS = "match_stats"
    ODDS = "odds"
    VENUE = "venue"
    LICENSE = "license"


class AuditStatus(Enum):
    """Audit result status."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    NOT_AVAILABLE = "not_available"


class DataConnector(ABC):
    """
    Base class for all data connectors.
    
    Each connector is responsible for auditing a specific data source
    and ensuring data quality, availability, and proper timestamps.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the connector.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.audit_timestamp = datetime.utcnow()
        
    @abstractmethod
    def get_source_name(self) -> str:
        """Return the name of the data source."""
        pass
    
    @abstractmethod
    def check_availability(self) -> Dict[str, Any]:
        """
        Check if the data source is available.
        
        Returns:
            Dictionary containing availability status and metadata
        """
        pass
    
    @abstractmethod
    def audit_data_quality(self) -> Dict[str, Any]:
        """
        Audit the quality of available data.
        
        Returns:
            Dictionary containing quality metrics and issues
        """
        pass
    
    @abstractmethod
    def check_timestamps(self) -> Dict[str, Any]:
        """
        Verify timestamp integrity and ordering.
        
        Returns:
            Dictionary containing timestamp validation results
        """
        pass
    
    @abstractmethod
    def detect_leakage(self) -> Dict[str, Any]:
        """
        Detect potential data leakage issues.
        
        Returns:
            Dictionary containing leakage detection results
        """
        pass
    
    def run_full_audit(self) -> Dict[str, Any]:
        """
        Run complete audit across all checks.
        
        Returns:
            Comprehensive audit report
        """
        audit_start = datetime.utcnow()
        
        report = {
            "source": self.get_source_name(),
            "audit_timestamp": audit_start.isoformat(),
            "availability": self.check_availability(),
            "data_quality": self.audit_data_quality(),
            "timestamps": self.check_timestamps(),
            "leakage_check": self.detect_leakage(),
        }
        
        audit_end = datetime.utcnow()
        report["audit_duration_seconds"] = (audit_end - audit_start).total_seconds()
        
        # Determine overall status
        statuses = [
            report["availability"].get("status"),
            report["data_quality"].get("status"),
            report["timestamps"].get("status"),
            report["leakage_check"].get("status"),
        ]
        
        if AuditStatus.FAIL.value in statuses:
            report["overall_status"] = AuditStatus.FAIL.value
        elif AuditStatus.WARNING.value in statuses:
            report["overall_status"] = AuditStatus.WARNING.value
        elif AuditStatus.NOT_AVAILABLE.value in statuses:
            report["overall_status"] = AuditStatus.NOT_AVAILABLE.value
        else:
            report["overall_status"] = AuditStatus.PASS.value
            
        return report
