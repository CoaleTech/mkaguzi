"""
Query Manager - Safe query execution with whitelisting
"""
import frappe
from typing import Dict, List, Any, Optional

class QueryManager:
    """Manages safe SQL query execution"""

    # Whitelisted query templates
    WHITELISTED_QUERIES = {
        'audit_gl_entry_validation': """
            SELECT COUNT(*) as count
            FROM `tabAudit GL Entry`
            WHERE amount IS NULL OR posting_date IS NULL
        """,
        'doctype_catalog_completeness': """
            SELECT COUNT(*) as count
            FROM `tabAudit Doctype Catalog`
            WHERE doctype_name IS NULL
        """,
        'test_template_validation': """
            SELECT COUNT(*) as count
            FROM `tabAudit Test Template`
            WHERE template_name IS NULL
        """,
        'audit_triggers_config': """
            SELECT COUNT(*) as count
            FROM `tabAudit Trigger`
            WHERE is_active = 1 AND trigger_condition IS NULL
        """,
        'audit_rules_validation': """
            SELECT COUNT(*) as count
            FROM `tabAudit Rule`
            WHERE is_active = 1 AND condition IS NULL
        """
    }

    @classmethod
    def execute_safe_query(cls, query_key: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Execute a whitelisted query safely

        Args:
            query_key: Key from WHITELISTED_QUERIES
            params: Optional parameters for query

        Returns:
            Query results as list of dictionaries

        Raises:
            ValueError: If query_key is not whitelisted
        """
        if query_key not in cls.WHITELISTED_QUERIES:
            frappe.log_error(f"Query not whitelisted: {query_key}")
            raise ValueError(f"Query '{query_key}' is not whitelisted for execution")

        query = cls.WHITELISTED_QUERIES[query_key]

        try:
            if params:
                result = frappe.db.sql(query, params, as_dict=True)
            else:
                result = frappe.db.sql(query, as_dict=True)
            return result
        except Exception as e:
            frappe.log_error(f"Safe query execution failed: {str(e)}", "QueryManager Error")
            raise

    @classmethod
    def add_whitelisted_query(cls, key: str, query: str) -> None:
        """
        Add a new query to the whitelist (only for system administrators)

        Args:
            key: Unique identifier for the query
            query: SQL query string

        Raises:
            PermissionError: If user is not System Manager
        """
        if "System Manager" not in frappe.get_roles(frappe.session.user):
            raise PermissionError("Only System Managers can add whitelisted queries")

        cls.WHITELISTED_QUERIES[key] = query