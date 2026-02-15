"""
License status connector for tracking data source licenses.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from ciphercourt.connectors.base import DataConnector, AuditStatus


class LicenseConnector(DataConnector):
    """
    Connector for auditing license status of data sources.
    
    Ensures:
    - All data sources have valid licenses
    - License expiration tracking
    - Terms of use compliance
    - Attribution requirements met
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.sources = config.get("sources", []) if config else []
        
    def get_source_name(self) -> str:
        return "license_status"
    
    def check_availability(self) -> Dict[str, Any]:
        """Check if license information is available for all sources."""
        result = {
            "status": AuditStatus.PASS.value,
            "sources_checked": self.sources if self.sources else ["default"],
            "details": {},
            "issues": []
        }
        
        sources_to_check = self.sources if self.sources else ["default"]
        
        for source in sources_to_check:
            license_info = self._get_license_info(source)
            result["details"][source] = license_info
            
            if not license_info["has_license"]:
                result["issues"].append(f"No license information for {source}")
                result["status"] = AuditStatus.WARNING.value
        
        return result
    
    def audit_data_quality(self) -> Dict[str, Any]:
        """Audit quality of license data."""
        result = {
            "status": AuditStatus.PASS.value,
            "checks": {},
            "issues": []
        }
        
        # Check for required license fields
        required_fields = ["license_type", "license_holder", "expiration_date", "terms_url"]
        result["checks"]["required_fields"] = {
            "expected": required_fields,
            "status": "pass"
        }
        
        # Check license completeness
        completeness = self._check_license_completeness()
        result["checks"]["completeness"] = completeness
        
        if completeness["incomplete_licenses"] > 0:
            result["issues"].append(f"Found {completeness['incomplete_licenses']} incomplete license records")
            result["status"] = AuditStatus.WARNING.value
        
        return result
    
    def check_timestamps(self) -> Dict[str, Any]:
        """Verify license expiration dates."""
        result = {
            "status": AuditStatus.PASS.value,
            "checks": {},
            "issues": []
        }
        
        # Check for expired licenses
        expiration_check = self._check_license_expiration()
        result["checks"]["expiration"] = expiration_check
        
        if expiration_check["expired_count"] > 0:
            result["issues"].append(f"CRITICAL: Found {expiration_check['expired_count']} expired licenses")
            result["status"] = AuditStatus.FAIL.value
        elif expiration_check["expiring_soon_count"] > 0:
            result["issues"].append(f"Warning: {expiration_check['expiring_soon_count']} licenses expiring within 30 days")
            result["status"] = AuditStatus.WARNING.value
        
        return result
    
    def detect_leakage(self) -> Dict[str, Any]:
        """Detect potential license violations."""
        result = {
            "status": AuditStatus.PASS.value,
            "checks": {},
            "issues": []
        }
        
        # Check for terms of use compliance
        compliance_check = self._check_terms_compliance()
        result["checks"]["terms_compliance"] = compliance_check
        
        if compliance_check["violations"] > 0:
            result["issues"].append(f"Found {compliance_check['violations']} potential terms violations")
            result["status"] = AuditStatus.WARNING.value
        
        # Check for attribution requirements
        attribution_check = self._check_attribution()
        result["checks"]["attribution"] = attribution_check
        
        if attribution_check["missing_attribution"] > 0:
            result["issues"].append(f"Found {attribution_check['missing_attribution']} sources missing required attribution")
            result["status"] = AuditStatus.WARNING.value
        
        return result
    
    def _get_license_info(self, source: str) -> Dict[str, Any]:
        """Get license information for a source."""
        # Placeholder - would query license database
        return {
            "has_license": True,
            "license_type": "Commercial",
            "status": "active",
            "expiration": (datetime.utcnow() + timedelta(days=180)).isoformat()
        }
    
    def _check_license_completeness(self) -> Dict[str, Any]:
        """Check completeness of license records."""
        # Placeholder
        return {
            "total_sources": len(self.sources) if self.sources else 5,
            "complete_licenses": len(self.sources) - 1 if self.sources else 4,
            "incomplete_licenses": 1,
            "completeness_rate": 0.80
        }
    
    def _check_license_expiration(self) -> Dict[str, Any]:
        """Check for expired or expiring licenses."""
        # Placeholder
        return {
            "total_licenses": len(self.sources) if self.sources else 5,
            "active_licenses": len(self.sources) if self.sources else 5,
            "expired_count": 0,
            "expiring_soon_count": 1,
            "expiring_soon_threshold_days": 30
        }
    
    def _check_terms_compliance(self) -> Dict[str, Any]:
        """Check compliance with terms of use."""
        # Placeholder - would verify usage patterns against terms
        return {
            "total_sources_checked": len(self.sources) if self.sources else 5,
            "compliant": len(self.sources) if self.sources else 5,
            "violations": 0
        }
    
    def _check_attribution(self) -> Dict[str, Any]:
        """Check if attribution requirements are met."""
        # Placeholder
        return {
            "sources_requiring_attribution": 2,
            "attributed_correctly": 2,
            "missing_attribution": 0
        }
