"""
CipherCourt - A data availability audit framework for pre-match tennis modeling.

This is NOT a betting bot. It is designed to audit data availability,
quality, timestamps, and prevent data leakage in tennis analytics.
"""

__version__ = "0.1.0"
__author__ = "CipherCourt Team"

from ciphercourt.audit import AuditFramework

__all__ = ["AuditFramework"]
