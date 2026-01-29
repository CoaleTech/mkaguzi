"""
Type definitions for Mkaguzi
"""
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Common types
DocType = str  # Document type name
DocName = str  # Document name/ID
UserID = str   # User email or ID

# Audit types
RiskLevel = str  # 'Low', 'Medium', 'High'
AuditOperation = str  # 'Create', 'Update', 'Delete', 'Submit', 'Cancel'
Module = str  # Module name

# API Response types
class APIResponse(Dict[str, Any]):
    """Standard API response type"""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    message: Optional[str]

# Audit Trail types
class AuditTrailEntry(Dict[str, Any]):
    """Audit trail entry type"""
    name: DocName
    document_type: DocType
    document_name: DocName
    operation: AuditOperation
    user: UserID
    timestamp: datetime
    module: Module
    changes_summary: str
    risk_level: RiskLevel
    requires_review: bool

# Dashboard types
class DashboardData(Dict[str, Any]):
    """Dashboard data type"""
    summary: Dict[str, Any]
    charts: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]