# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import now, now_datetime, cstr, flt
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ModuleDiscoveryEngine:
    """
    Automatic doctype discovery and cataloging system
    Discovers all ERPNext/HRMS doctypes and determines audit requirements
    """

    def __init__(self):
        self.discovered_doctypes = {}
        self.audit_categories = {
            'Financial': ['GL Entry', 'Journal Entry', 'Payment Entry', 'Sales Invoice', 'Purchase Invoice', 'Sales Order', 'Purchase Order'],
            'Payroll': ['Salary Slip', 'Salary Structure', 'Employee', 'Payroll Entry'],
            'HR': ['Leave Application', 'Attendance', 'Expense Claim', 'Employee Advance', 'Appraisal'],
            'Inventory': ['Stock Entry', 'Stock Reconciliation', 'Delivery Note', 'Purchase Receipt', 'Item', 'Warehouse'],
            'Procurement': ['Supplier', 'Supplier Quotation', 'Purchase Order', 'Purchase Invoice', 'Purchase Receipt'],
            'Access': ['User', 'Role', 'User Permission', 'DocShare', 'Role Permission'],
            'Sales': ['Customer', 'Sales Order', 'Sales Invoice', 'Delivery Note', 'Quotation'],
            'Assets': ['Asset', 'Asset Movement', 'Asset Maintenance'],
            'Projects': ['Project', 'Task', 'Timesheet'],
            'Support': ['Issue', 'Warranty Claim']
        }

    def discover_all_doctypes(self):
        """
        Discover all doctypes in the system and catalog them
        """
        try:
            frappe.publish_progress(0, "Starting doctype discovery...")

            # Get all doctypes from DocType table
            all_doctypes = frappe.get_all('DocType',
                fields=['name', 'module', 'is_submittable', 'is_table', 'custom'],
                filters={'is_table': 0}  # Exclude child tables
            )

            total_doctypes = len(all_doctypes)
            processed = 0

            for doctype_info in all_doctypes:
                try:
                    # Analyze doctype
                    analysis = self.analyze_doctype(doctype_info.name)

                    # Categorize doctype
                    category = self.categorize_doctype(doctype_info.name, analysis)

                    # Create or update catalog entry
                    self.update_doctype_catalog(doctype_info, analysis, category)

                    processed += 1
                    if processed % 10 == 0:
                        frappe.publish_progress((processed / total_doctypes) * 100,
                            f"Discovered {processed}/{total_doctypes} doctypes...")

                except Exception as e:
                    logger.error(f"Failed to analyze doctype {doctype_info.name}: {str(e)}")
                    continue

            frappe.publish_progress(100, f"Discovery complete! Processed {processed} doctypes.")
            return {"success": True, "discovered": processed}

        except Exception as e:
            logger.error(f"Doctype discovery failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def analyze_doctype(self, doctype_name):
        """
        Analyze a doctype to determine its audit requirements

        Args:
            doctype_name: Name of the doctype to analyze

        Returns:
            dict: Analysis results
        """
        try:
            # Get doctype metadata
            doctype_meta = frappe.get_meta(doctype_name)

            analysis = {
                'doctype_name': doctype_name,
                'module': doctype_meta.module,
                'is_submittable': doctype_meta.is_submittable,
                'has_workflow': bool(doctype_meta.workflow),
                'fields': [],
                'critical_fields': [],
                'audit_triggers': [],
                'risk_factors': []
            }

            # Analyze fields
            for field in doctype_meta.fields:
                field_info = {
                    'fieldname': field.fieldname,
                    'fieldtype': field.fieldtype,
                    'label': field.label,
                    'reqd': field.reqd,
                    'unique': field.unique
                }
                analysis['fields'].append(field_info)

                # Identify critical fields
                if self._is_critical_field(field):
                    analysis['critical_fields'].append(field.fieldname)

            # Determine audit triggers
            analysis['audit_triggers'] = self._determine_audit_triggers(doctype_name, analysis)

            # Assess risk factors
            analysis['risk_factors'] = self._assess_risk_factors(doctype_name, analysis)

            return analysis

        except Exception as e:
            logger.error(f"Doctype analysis failed for {doctype_name}: {str(e)}")
            return {
                'doctype_name': doctype_name,
                'error': str(e),
                'fields': [],
                'critical_fields': [],
                'audit_triggers': [],
                'risk_factors': ['analysis_failed']
            }

    def categorize_doctype(self, doctype_name, analysis):
        """
        Categorize a doctype into audit categories

        Args:
            doctype_name: Name of the doctype
            analysis: Analysis results

        Returns:
            str: Audit category
        """
        # Check predefined categories
        for category, doctypes in self.audit_categories.items():
            if doctype_name in doctypes:
                return category

        # Intelligent categorization based on analysis
        if analysis.get('module') == 'Accounts':
            return 'Financial'
        elif analysis.get('module') == 'HR':
            return 'HR'
        elif analysis.get('module') == 'Stock':
            return 'Inventory'
        elif analysis.get('module') == 'Buying':
            return 'Procurement'
        elif analysis.get('module') == 'Selling':
            return 'Sales'
        elif 'User' in doctype_name or 'Role' in doctype_name or 'Permission' in doctype_name:
            return 'Access'
        else:
            return 'Other'

    def update_doctype_catalog(self, doctype_info, analysis, category):
        """
        Update or create doctype catalog entry

        Args:
            doctype_info: Basic doctype info from database
            analysis: Detailed analysis results
            category: Audit category
        """
        try:
            # Check if catalog entry exists
            catalog_name = f"{doctype_info.name}"

            if frappe.db.exists('Audit Doctype Catalog', catalog_name):
                catalog_doc = frappe.get_doc('Audit Doctype Catalog', catalog_name)
            else:
                catalog_doc = frappe.new_doc('Audit Doctype Catalog')
                catalog_doc.doctype_name = catalog_name

            # Update catalog information
            catalog_doc.module = analysis.get('module', doctype_info.module)
            catalog_doc.audit_category = category
            catalog_doc.is_submittable = analysis.get('is_submittable', doctype_info.is_submittable)
            catalog_doc.has_workflow = analysis.get('has_workflow', False)
            catalog_doc.critical_fields = json.dumps(analysis.get('critical_fields', []))
            catalog_doc.audit_triggers = json.dumps(analysis.get('audit_triggers', []))
            catalog_doc.risk_factors = json.dumps(analysis.get('risk_factors', []))
            catalog_doc.last_discovered = now_datetime()
            catalog_doc.is_audit_enabled = self._should_enable_audit(analysis, category)

            catalog_doc.save(ignore_permissions=True)

        except Exception as e:
            logger.error(f"Failed to update catalog for {doctype_info.name}: {str(e)}")

    def _is_critical_field(self, field):
        """Determine if a field is critical for auditing"""
        critical_fieldnames = [
            'amount', 'total', 'grand_total', 'debit', 'credit', 'balance',
            'salary', 'basic', 'gross_pay', 'net_pay',
            'quantity', 'rate', 'price', 'valuation_rate',
            'user', 'owner', 'modified_by', 'role', 'permission'
        ]

        critical_types = ['Currency', 'Float', 'Int', 'Percent', 'Date', 'Datetime']

        return (
            field.fieldname in critical_fieldnames or
            field.fieldtype in critical_types or
            field.reqd or
            field.unique
        )

    def _determine_audit_triggers(self, doctype_name, analysis):
        """Determine what events should trigger audits"""
        triggers = ['after_insert', 'on_update']

        if analysis.get('is_submittable'):
            triggers.extend(['on_submit', 'on_cancel'])

        # Add specific triggers based on doctype
        if doctype_name in ['Journal Entry', 'Payment Entry', 'Salary Slip']:
            triggers.append('validate')

        if doctype_name in ['User', 'Role']:
            triggers.append('before_save')

        return list(set(triggers))  # Remove duplicates

    def _assess_risk_factors(self, doctype_name, analysis):
        """Assess risk factors for the doctype"""
        risk_factors = []

        # High-risk doctypes
        if doctype_name in ['Journal Entry', 'Payment Entry', 'User', 'Role', 'Salary Slip']:
            risk_factors.append('high_risk_doctype')

        # Financial amount fields
        if any(field['fieldname'] in ['grand_total', 'total_amount', 'debit', 'credit']
               for field in analysis.get('fields', [])):
            risk_factors.append('financial_amounts')

        # User access fields
        if any(field['fieldname'] in ['user', 'role', 'permission', 'owner']
               for field in analysis.get('fields', [])):
            risk_factors.append('access_control')

        # Submittable documents
        if analysis.get('is_submittable'):
            risk_factors.append('submittable_document')

        # Workflow documents
        if analysis.get('has_workflow'):
            risk_factors.append('workflow_document')

        return risk_factors

    def _should_enable_audit(self, analysis, category):
        """Determine if audit should be enabled by default"""
        # Always audit high-risk categories
        if category in ['Financial', 'Payroll', 'Access']:
            return True

        # Audit submittable documents
        if analysis.get('is_submittable'):
            return True

        # Audit documents with critical fields
        if analysis.get('critical_fields'):
            return True

        return False

    def get_discovery_stats(self):
        """Get statistics about discovered doctypes"""
        try:
            total_cataloged = frappe.db.count('Audit Doctype Catalog')

            category_stats = frappe.db.sql("""
                SELECT audit_category, COUNT(*) as count
                FROM `tabAudit Doctype Catalog`
                GROUP BY audit_category
                ORDER BY count DESC
            """, as_dict=True)

            enabled_audits = frappe.db.count('Audit Doctype Catalog',
                filters={'is_audit_enabled': 1})

            return {
                'total_cataloged': total_cataloged,
                'category_breakdown': category_stats,
                'audits_enabled': enabled_audits,
                'last_discovery': frappe.db.get_value('Audit Doctype Catalog',
                    {}, 'last_discovered', order_by='last_discovered desc')
            }

        except Exception as e:
            logger.error(f"Failed to get discovery stats: {str(e)}")
            return {}

    def enable_doctype_audit(self, doctype_name, enable=True):
        """Enable or disable audit for a specific doctype"""
        try:
            catalog_doc = frappe.get_doc('Audit Doctype Catalog', doctype_name)
            catalog_doc.is_audit_enabled = enable
            catalog_doc.save(ignore_permissions=True)

            # Update hooks if needed
            if enable:
                self._add_doctype_hooks(doctype_name, catalog_doc)
            else:
                self._remove_doctype_hooks(doctype_name)

            return {"success": True, "message": f"Audit {'enabled' if enable else 'disabled'} for {doctype_name}"}

        except Exception as e:
            logger.error(f"Failed to {'enable' if enable else 'disable'} audit for {doctype_name}: {str(e)}")
            return {"success": False, "error": str(e)}

    def _add_doctype_hooks(self, doctype_name, catalog_doc):
        """Add audit hooks for a doctype"""
        try:
            # This would integrate with hooks_manager.py
            frappe.enqueue(
                'mkaguzi.integration.hooks_manager.add_doctype_hooks',
                doctype_name=doctype_name,
                audit_triggers=json.loads(catalog_doc.audit_triggers or '[]'),
                queue='short'
            )
        except Exception as e:
            logger.error(f"Failed to add hooks for {doctype_name}: {str(e)}")

    def _remove_doctype_hooks(self, doctype_name):
        """Remove audit hooks for a doctype"""
        try:
            # This would integrate with hooks_manager.py
            frappe.enqueue(
                'mkaguzi.integration.hooks_manager.remove_doctype_hooks',
                doctype_name=doctype_name,
                queue='short'
            )
        except Exception as e:
            logger.error(f"Failed to remove hooks for {doctype_name}: {str(e)}")

# Global discovery engine instance
discovery_engine = ModuleDiscoveryEngine()

@frappe.whitelist()
def discover_doctypes():
    """API endpoint to trigger doctype discovery"""
    if not frappe.has_permission('Audit Doctype Catalog', 'write'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    result = discovery_engine.discover_all_doctypes()
    return result

@frappe.whitelist()
def get_discovery_stats():
    """API endpoint to get discovery statistics"""
    return discovery_engine.get_discovery_stats()

@frappe.whitelist()
def enable_audit_for_doctype(doctype_name, enable=1):
    """API endpoint to enable/disable audit for a doctype"""
    if not frappe.has_permission('Audit Doctype Catalog', 'write'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    result = discovery_engine.enable_doctype_audit(doctype_name, bool(int(enable)))
    return result