"""
Audit Trail Helper - Centralized audit trail creation
"""
import frappe
from frappe.utils import now
from typing import Optional, Dict, Any

class AuditTrailHelper:
    """Helper class for creating audit trail entries"""

    @staticmethod
    def create_audit_trail_entry(
        doc,
        operation: str,
        module: str,
        changes_summary: Optional[str] = None,
        risk_level: str = 'Low',
        requires_review: bool = False
    ) -> Optional[str]:
        """
        Create a standardized audit trail entry

        Args:
            doc: The document being audited
            operation: Operation type (Create, Update, Delete, etc.)
            module: Module name
            changes_summary: Summary of changes
            risk_level: Risk level (Low, Medium, High)
            requires_review: Whether this requires review

        Returns:
            Name of created audit trail entry or None
        """
        try:
            if not changes_summary:
                changes_summary = f"{doc.doctype} {operation}: {doc.name}"

            trail = frappe.get_doc({
                'doctype': 'Audit Trail Entry',
                'document_type': doc.doctype,
                'document_name': doc.name,
                'operation': operation,
                'user': frappe.session.user,
                'timestamp': now(),
                'module': module,
                'changes_summary': changes_summary,
                'risk_level': risk_level,
                'requires_review': 1 if requires_review else 0
            })

            trail.insert(ignore_permissions=True)
            frappe.db.commit()

            return trail.name

        except Exception as e:
            frappe.log_error(f"Audit Trail Creation Error: {str(e)}", "AuditTrailHelper")
            return None

    @staticmethod
    def assess_document_risk(doc, operation: str) -> str:
        """
        Assess risk level of a document operation

        Args:
            doc: The document being assessed
            operation: Operation type

        Returns:
            Risk level: Low, Medium, or High
        """
        try:
            # High risk operations
            if operation in ['Delete', 'Cancel']:
                return 'High'

            # Check for sensitive doctypes
            sensitive_doctypes = ['User', 'Role', 'Salary Slip', 'Payment Entry']
            if doc.doctype in sensitive_doctypes:
                return 'Medium'

            # Check for large amounts
            amount = AuditTrailHelper._get_document_amount(doc)
            if amount and amount > 100000:
                return 'Medium'

            return 'Low'

        except Exception:
            return 'Low'

    @staticmethod
    def _get_document_amount(doc) -> Optional[float]:
        """Extract amount from document"""
        try:
            from frappe.utils import flt

            amount_fields = ['total', 'grand_total', 'paid_amount', 'received_amount', 'debit', 'credit', 'amount']
            for field in amount_fields:
                if hasattr(doc, field):
                    amount = getattr(doc, field)
                    if amount:
                        return flt(amount)
            return 0
        except Exception:
            return 0