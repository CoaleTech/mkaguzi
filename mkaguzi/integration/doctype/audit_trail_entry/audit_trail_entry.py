# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import json


class AuditTrailEntry(Document):
    """Audit Trail Entry DocType Controller"""

    def autoname(self):
        """Generate name for audit trail entry"""
        if not self.name:
            # Create a naming series pattern
            prefix = {
                'CREATE': 'AT-CREATE',
                'UPDATE': 'AT-UPDATE',
                'DELETE': 'AT-DELETE',
                'SUBMIT': 'AT-SUBMIT',
                'CANCEL': 'AT-CANCEL',
                'RENAME': 'AT-RENAME'
            }.get(self.operation, 'AT-ENTRY')

            # Generate unique name with microseconds and random suffix for uniqueness
            import random
            timestamp = frappe.utils.now_datetime().strftime('%Y%m%d%H%M%S%f')
            doctype_part = (self.source_doctype or 'Unknown').replace(' ', '-')[:20]
            random_suffix = random.randint(1000, 9999)
            self.name = f"{prefix}-{doctype_part}-{timestamp}-{random_suffix}"

    def validate(self):
        """Validate audit trail entry"""
        # Ensure source document exists
        if self.source_doctype and self.source_document:
            if not frappe.db.exists(self.source_doctype, self.source_document):
                # For deleted documents, this is expected
                if self.operation != 'DELETE':
                    frappe.msgprint(
                        _("Warning: Source document {0} {1} may not exist").format(
                            self.source_doctype, self.source_document
                        )
                    )

        # Validate risk level
        valid_risk_levels = ['Low', 'Medium', 'High', 'Critical']
        if self.risk_level not in valid_risk_levels:
            self.risk_level = 'Low'

        # Validate operation
        valid_operations = ['CREATE', 'UPDATE', 'DELETE', 'SUBMIT', 'CANCEL', 'RENAME']
        if self.operation not in valid_operations:
            frappe.throw(_("Invalid operation: {0}").format(self.operation))

        # Calculate risk score if not set
        if not self.risk_score:
            self.risk_score = self.calculate_risk_score()

        # Mark as high risk if requires_review is checked and risk_level is Low/Medium
        if self.requires_review and self.risk_level in ['Low', 'Medium']:
            self.risk_level = 'High'

    def before_save(self):
        """Actions before saving"""
        # Parse JSON fields if they're strings
        if isinstance(self.old_values, str) and self.old_values:
            try:
                json.loads(self.old_values)
            except:
                self.old_values = '{}'

        if isinstance(self.new_values, str) and self.new_values:
            try:
                json.loads(self.new_values)
            except:
                self.new_values = '{}'

        if isinstance(self.changes, str) and self.changes:
            try:
                json.loads(self.changes)
            except:
                self.changes = '{}'

    def calculate_risk_score(self):
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
        score += operation_weights.get(self.operation, 50)

        # Factor in module
        module_weights = {
            'Financial': 30,
            'Payroll': 25,
            'Inventory': 20,
            'HR': 15,
            'Access': 35,
            'Other': 10
        }
        score += module_weights.get(self.module, 10)

        # Factor in risk level
        risk_weights = {
            'Critical': 50,
            'High': 30,
            'Medium': 15,
            'Low': 5
        }
        score += risk_weights.get(self.risk_level, 5)

        return min(score, 100)

    def on_trash(self):
        """Prevent deletion of audit trail entries"""
        # Only System Manager can delete audit entries
        if 'System Manager' not in frappe.get_roles():
            frappe.throw(_("Only System Manager can delete Audit Trail Entries"))

    def get_document_changes(self):
        """Get parsed document changes"""
        if not self.changes or self.changes == '{}':
            return {}

        try:
            return json.loads(self.changes)
        except:
            return {}

    def get_old_values_dict(self):
        """Get parsed old values"""
        if not self.old_values or self.old_values == '{}':
            return {}

        try:
            return json.loads(self.old_values)
        except:
            return {}

    def get_new_values_dict(self):
        """Get parsed new values"""
        if not self.new_values or self.new_values == '{}':
            return {}

        try:
            return json.loads(self.new_values)
        except:
            return {}


# Whitelisted functions for API access

@frappe.whitelist()
def get_audit_trail_entries(doctype, document_name, limit=100):
    """Get all audit trail entries for a specific document"""
    entries = frappe.get_all('Audit Trail Entry',
        filters={
            'source_doctype': doctype,
            'source_document': document_name
        },
        fields=['name', 'operation', 'timestamp', 'user', 'risk_level', 'status'],
        order_by='timestamp desc',
        limit=limit
    )
    return entries


@frappe.whitelist()
def get_high_risk_entries(limit=50):
    """Get high risk audit trail entries"""
    entries = frappe.get_all('Audit Trail Entry',
        filters={
            'risk_level': ['in', ['High', 'Critical']],
            'status': 'Open'
        },
        fields=['name', 'source_doctype', 'source_document', 'operation', 'timestamp', 'user', 'risk_score'],
        order_by='timestamp desc',
        limit=limit
    )
    return entries


@frappe.whitelist()
def mark_as_reviewed(entry_name):
    """Mark an audit trail entry as reviewed"""
    if not frappe.has_permission('Audit Trail Entry', 'write'):
        frappe.throw(_("You don't have permission to update Audit Trail Entries"))

    frappe.db.set_value('Audit Trail Entry', entry_name, 'status', 'Reviewed')
    return {'success': True}
