# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import now, now_datetime, cstr, flt, get_datetime, add_days
import json
import logging
from datetime import datetime, timedelta
import hashlib
import threading

logger = logging.getLogger(__name__)

class AuditTrailLogger:
    """
    Central audit trail logging system for Mkaguzi
    Handles all document change logging and audit trail management
    """

    def __init__(self):
        self.lock = threading.Lock()

    def log_document_change(self, doc, method, old_doc=None):
        """
        Log any document change to the audit trail

        Args:
            doc: The document object
            method: The method that triggered the change
            old_doc: The old document state (for updates)
        """
        try:
            with self.lock:
                # Skip audit trail entries themselves to prevent recursion
                if doc.doctype == "Audit Trail Entry":
                    return

                # Determine operation type
                operation = self._get_operation_type(method)

                # Create audit trail entry
                audit_entry = {
                    'doctype': 'Audit Trail Entry',
                    'source_doctype': doc.doctype,
                    'source_document': doc.name,
                    'operation': operation,
                    'timestamp': now_datetime(),
                    'user': frappe.session.user or 'System',
                    'module': self._get_module_for_doctype(doc.doctype),
                    'risk_level': self._assess_risk_level(doc),
                    'requires_review': self._requires_manual_review(doc),
                    'ip_address': self._get_client_ip(),
                    'user_agent': self._get_user_agent()
                }

                # Handle old and new values
                if operation == 'UPDATE' and old_doc:
                    audit_entry['old_values'] = json.dumps(old_doc.as_dict())
                    audit_entry['new_values'] = json.dumps(doc.as_dict())
                    audit_entry['changes'] = json.dumps(self._calculate_changes(old_doc.as_dict(), doc.as_dict()))
                elif operation in ['CREATE', 'SUBMIT']:
                    audit_entry['new_values'] = json.dumps(doc.as_dict())
                    audit_entry['old_values'] = '{}'
                    audit_entry['changes'] = '{}'
                elif operation == 'DELETE':
                    audit_entry['old_values'] = json.dumps(doc.as_dict()) if hasattr(doc, 'as_dict') else '{}'
                    audit_entry['new_values'] = '{}'
                    audit_entry['changes'] = json.dumps({'deleted': True})

                # Calculate risk score
                audit_entry['risk_score'] = self._calculate_risk_score(audit_entry)

                # Insert audit entry
                audit_doc = frappe.get_doc(audit_entry)
                audit_doc.insert(ignore_permissions=True)

                # Trigger additional processing
                self._trigger_additional_processing(audit_doc, doc, method)

                frappe.db.commit()

        except Exception as e:
            logger.error(f"Audit trail logging failed: {str(e)}")
            frappe.log_error(f"Audit Trail Error: {str(e)}", "Audit Trail")

    def _get_operation_type(self, method):
        """Map frappe method to operation type"""
        method_mapping = {
            'after_insert': 'CREATE',
            'on_update': 'UPDATE',
            'on_trash': 'DELETE',
            'on_submit': 'SUBMIT',
            'on_cancel': 'CANCEL',
            'after_rename': 'RENAME'
        }
        return method_mapping.get(method, 'UPDATE')

    def _get_module_for_doctype(self, doctype):
        """Determine module for a given doctype"""
        module_mapping = {
            # Financial
            'GL Entry': 'Financial',
            'Journal Entry': 'Financial',
            'Payment Entry': 'Financial',
            'Sales Invoice': 'Financial',
            'Purchase Invoice': 'Financial',
            'Sales Order': 'Financial',
            'Purchase Order': 'Financial',

            # Payroll
            'Salary Slip': 'Payroll',
            'Salary Structure': 'Payroll',
            'Employee': 'Payroll',

            # HR
            'Leave Application': 'HR',
            'Attendance': 'HR',
            'Expense Claim': 'HR',

            # Inventory
            'Stock Entry': 'Inventory',
            'Stock Reconciliation': 'Inventory',
            'Delivery Note': 'Inventory',
            'Purchase Receipt': 'Inventory',
            'Item': 'Inventory',

            # Access Control
            'User': 'Access',
            'Role': 'Access',
            'User Permission': 'Access'
        }

        return module_mapping.get(doctype, 'Other')

    def _assess_risk_level(self, doc):
        """Assess risk level for a document"""
        # High-risk doctypes
        high_risk_doctypes = ['Journal Entry', 'Payment Entry', 'Salary Slip', 'User', 'Role']
        critical_doctypes = ['GL Entry', 'Stock Entry']

        if doc.doctype in critical_doctypes:
            return 'Critical'
        elif doc.doctype in high_risk_doctypes:
            return 'High'

        # Check for large amounts (financial documents)
        if hasattr(doc, 'grand_total') and flt(doc.grand_total) > 100000:
            return 'High'
        elif hasattr(doc, 'grand_total') and flt(doc.grand_total) > 50000:
            return 'Medium'

        if hasattr(doc, 'total_amount') and flt(doc.total_amount) > 50000:
            return 'High'
        elif hasattr(doc, 'total_amount') and flt(doc.total_amount) > 25000:
            return 'Medium'

        return 'Low'

    def _requires_manual_review(self, doc):
        """Determine if document requires manual review"""
        # Always review critical and high-risk operations
        risk_level = self._assess_risk_level(doc)
        if risk_level in ['Critical', 'High']:
            return True

        # Review large financial transactions
        if hasattr(doc, 'grand_total') and flt(doc.grand_total) > 100000:
            return True

        # Review system-level changes
        if doc.doctype in ['User', 'Role', 'User Permission']:
            return True

        return False

    def _calculate_risk_score(self, audit_entry):
        """Calculate risk score based on various factors"""
        score = 50  # Base score

        # Factor in operation type
        operation_weights = {
            'DELETE': 100,
            'UPDATE': 60,
            'CREATE': 40,
            'SUBMIT': 80,
            'CANCEL': 70,
            'RENAME': 30
        }
        score += operation_weights.get(audit_entry.get('operation'), 0)

        # Factor in module
        module_weights = {
            'Financial': 30,
            'Payroll': 25,
            'Inventory': 20,
            'HR': 15,
            'Access': 35,
            'Other': 10
        }
        score += module_weights.get(audit_entry.get('module'), 0)

        # Factor in risk level
        risk_weights = {
            'Critical': 50,
            'High': 30,
            'Medium': 15,
            'Low': 5
        }
        score += risk_weights.get(audit_entry.get('risk_level'), 0)

        # Factor in user role (simplified)
        user = audit_entry.get('user', '').lower()
        if 'admin' in user or 'system' in user:
            score += 20

        return min(score, 100)

    def _calculate_changes(self, old_data, new_data):
        """Calculate what changed between old and new data"""
        changes = {}

        # Get all unique keys
        all_keys = set(old_data.keys()) | set(new_data.keys())

        for key in all_keys:
            old_value = old_data.get(key)
            new_value = new_data.get(key)

            if old_value != new_value:
                changes[key] = {
                    'old': old_value,
                    'new': new_value
                }

        return changes

    def _get_client_ip(self):
        """Get client IP address"""
        try:
            return frappe.local.request_ip or 'Unknown'
        except:
            return 'Unknown'

    def _get_user_agent(self):
        """Get user agent string"""
        try:
            return frappe.local.request.headers.get('User-Agent', 'Unknown')
        except:
            return 'Unknown'

    def _trigger_additional_processing(self, audit_doc, source_doc, method):
        """Trigger additional processing based on audit entry"""
        try:
            # Trigger notifications for high-risk events
            if audit_doc.risk_level in ['High', 'Critical']:
                self._trigger_notifications(audit_doc)

            # Trigger compliance checks
            if audit_doc.module == 'Financial':
                self._trigger_financial_checks(audit_doc, source_doc)

            # Trigger security monitoring
            if audit_doc.module == 'Access':
                self._trigger_security_checks(audit_doc, source_doc)

        except Exception as e:
            logger.error(f"Additional processing failed: {str(e)}")

    def _trigger_notifications(self, audit_doc):
        """Trigger notifications for high-risk audit events"""
        try:
            # Create notification for auditors
            notification = frappe.get_doc({
                'doctype': 'Notification Log',
                'subject': f"High Risk Audit Event: {audit_doc.source_doctype}",
                'email_content': f"""
                <p>A {audit_doc.risk_level} risk audit event has been detected:</p>
                <ul>
                    <li><strong>Document:</strong> {audit_doc.source_doctype} - {audit_doc.source_document}</li>
                    <li><strong>Operation:</strong> {audit_doc.operation}</li>
                    <li><strong>User:</strong> {audit_doc.user}</li>
                    <li><strong>Risk Score:</strong> {audit_doc.risk_score}</li>
                </ul>
                <p>Please review this event in the Audit Trail.</p>
                """,
                'document_type': 'Audit Trail Entry',
                'document_name': audit_doc.name,
                'type': 'Alert'
            })

            # Get auditors from role
            auditors = frappe.get_all('User',
                filters={'role_profile_name': ['like', '%Audit%']},
                pluck='email'
            )

            if auditors:
                notification.for_user = auditors[0]  # Send to first auditor
                notification.insert(ignore_permissions=True)

        except Exception as e:
            logger.error(f"Notification trigger failed: {str(e)}")

    def _trigger_financial_checks(self, audit_doc, source_doc):
        """Trigger financial compliance checks"""
        try:
            # Trigger segregation of duties check
            if source_doc.doctype == 'Journal Entry':
                frappe.enqueue(
                    'mkaguzi.integration.financial_checks.check_segregation_of_duties',
                    journal_entry=source_doc.name,
                    queue='short'
                )

            # Trigger duplicate transaction check
            frappe.enqueue(
                'mkaguzi.integration.financial_checks.check_duplicate_transactions',
                document=source_doc,
                queue='short'
            )

        except Exception as e:
            logger.error(f"Financial checks trigger failed: {str(e)}")

    def _trigger_security_checks(self, audit_doc, source_doc):
        """Trigger security monitoring checks"""
        try:
            # Trigger privilege escalation check
            if source_doc.doctype == 'User':
                frappe.enqueue(
                    'mkaguzi.integration.security_checks.check_privilege_escalation',
                    user=source_doc.name,
                    queue='short'
                )

            # Log security event
            frappe.enqueue(
                'mkaguzi.security.doctype.security_analytics_engine.security_analytics_engine.log_security_event',
                event_type='access_change',
                document=source_doc.doctype,
                document_name=source_doc.name,
                user=audit_doc.user,
                queue='short'
            )

        except Exception as e:
            logger.error(f"Security checks trigger failed: {str(e)}")

# Global audit trail logger instance
audit_trail_logger = AuditTrailLogger()

def log_gl_entry(doc, method):
    """Log GL Entry changes"""
    audit_trail_logger.log_document_change(doc, method)

def log_journal_entry(doc, method):
    """Log Journal Entry changes"""
    audit_trail_logger.log_document_change(doc, method)

def log_payment_entry(doc, method):
    """Log Payment Entry changes"""
    audit_trail_logger.log_document_change(doc, method)

def log_sales_invoice(doc, method):
    """Log Sales Invoice changes"""
    audit_trail_logger.log_document_change(doc, method)

def log_purchase_invoice(doc, method):
    """Log Purchase Invoice changes"""
    audit_trail_logger.log_document_change(doc, method)

def log_employee_changes(doc, method):
    """Log Employee changes"""
    audit_trail_logger.log_document_change(doc, method)

def log_salary_submission(doc, method):
    """Log Salary Slip submission"""
    audit_trail_logger.log_document_change(doc, method)

def log_stock_movement(doc, method):
    """Log Stock Entry changes"""
    audit_trail_logger.log_document_change(doc, method)

def log_user_changes(doc, method):
    """Log User changes"""
    audit_trail_logger.log_document_change(doc, method)

def log_attendance(doc, method):
    """Log Attendance changes"""
    audit_trail_logger.log_document_change(doc, method)

def log_leave_application(doc, method):
    """Log Leave Application changes"""
    audit_trail_logger.log_document_change(doc, method)