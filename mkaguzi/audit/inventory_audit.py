# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import now, now_datetime, cstr, flt, getdate, add_days, date_diff
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)

class InventoryAuditEngine:
    """
    Specialized audit engine for inventory and stock-related doctypes and processes
    """

    def __init__(self):
        self.inventory_doctypes = [
            'Item', 'Stock Entry', 'Stock Reconciliation', 'Delivery Note',
            'Purchase Receipt', 'Purchase Invoice', 'Sales Invoice', 'Stock Transfer',
            'Material Request', 'BOM', 'Work Order', 'Production Plan',
            'Item Price', 'Pricing Rule', 'Warehouse', 'Bin', 'Stock Ledger Entry',
            'Serial No', 'Batch', 'Quality Inspection', 'Item Variant',
            'Product Bundle', 'UOM', 'Item Group', 'Item Attribute'
        ]

        self.high_value_items = []  # Will be populated from Item Price
        self.critical_items = []    # Will be populated from Item master

        self.risk_weights = {
            'stock_adjustment': 0.8,
            'price_change': 0.7,
            'item_master_change': 0.6,
            'bulk_transaction': 0.7,
            'warehouse_transfer': 0.5,
            'quality_issue': 0.9,
            'serial_batch_change': 0.8
        }

    def audit_inventory_transaction(self, doctype_name, docname, action, user, old_doc=None, new_doc=None):
        """
        Audit an inventory-related transaction

        Args:
            doctype_name: The doctype being audited
            docname: Document name
            action: Action performed (insert, update, delete, etc.)
            user: User performing the action
            old_doc: Previous document state
            new_doc: New document state
        """
        try:
            if doctype_name not in self.inventory_doctypes:
                return None

            # Calculate risk score based on transaction type and changes
            risk_score = self._calculate_inventory_risk_score(doctype_name, action, old_doc, new_doc)

            # Generate detailed change summary
            changes_summary = self._generate_inventory_change_summary(doctype_name, action, old_doc, new_doc)

            # Determine risk level
            risk_level = self._determine_risk_level(risk_score)

            # Create audit trail entry
            audit_entry = {
                'doctype': 'Audit Trail',
                'doctype_name': doctype_name,
                'docname': docname,
                'user': user,
                'action': action,
                'risk_level': risk_level,
                'risk_score': risk_score,
                'changes_summary': json.dumps(changes_summary),
                'audit_category': 'Inventory',
                'business_impact': self._assess_business_impact(doctype_name, action, changes_summary),
                'compliance_flags': self._check_compliance_flags(doctype_name, action, new_doc)
            }

            return audit_entry

        except Exception as e:
            logger.error(f"Inventory audit failed for {doctype_name} {docname}: {str(e)}")
            return None

    def _calculate_inventory_risk_score(self, doctype_name, action, old_doc, new_doc):
        """
        Calculate risk score for inventory transactions
        """
        try:
            base_score = 0.0

            if action in ['insert', 'update']:
                if doctype_name == 'Stock Entry':
                    base_score = self._audit_stock_entry_changes(old_doc, new_doc)
                elif doctype_name == 'Stock Reconciliation':
                    base_score = self._audit_stock_reconciliation_changes(old_doc, new_doc)
                elif doctype_name == 'Item Price':
                    base_score = self._audit_item_price_changes(old_doc, new_doc)
                elif doctype_name == 'Item':
                    base_score = self._audit_item_master_changes(old_doc, new_doc)
                elif doctype_name in ['Delivery Note', 'Purchase Receipt', 'Sales Invoice', 'Purchase Invoice']:
                    base_score = self._audit_transaction_changes(old_doc, new_doc)
                elif doctype_name in ['Serial No', 'Batch']:
                    base_score = self._audit_serial_batch_changes(old_doc, new_doc)
                elif doctype_name == 'Quality Inspection':
                    base_score = self._audit_quality_changes(old_doc, new_doc)
                elif doctype_name == 'Warehouse':
                    base_score = 0.7  # Medium-high risk for warehouse changes
                elif doctype_name in ['Material Request', 'BOM', 'Work Order']:
                    base_score = 0.5  # Medium risk for planning documents
                else:
                    base_score = 0.3  # Low risk for other inventory changes

            elif action == 'delete':
                if doctype_name in ['Stock Entry', 'Stock Reconciliation']:
                    base_score = 0.9  # High risk for stock adjustments
                elif doctype_name == 'Item':
                    base_score = 0.8  # High risk for item deletion
                else:
                    base_score = 0.7  # Medium-high risk for other deletions

            elif action in ['submit', 'cancel']:
                base_score = 0.6  # Medium risk for submission/cancellation

            # Apply user role multiplier
            user_role_multiplier = self._get_user_role_multiplier()
            final_score = min(base_score * user_role_multiplier, 1.0)

            return round(final_score, 2)

        except Exception as e:
            logger.error(f"Failed to calculate inventory risk score: {str(e)}")
            return 0.5

    def _audit_stock_entry_changes(self, old_doc, new_doc):
        """
        Audit changes to stock entries
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New stock entry
                stock_entry_type = new_doc.get('stock_entry_type', '')
                if stock_entry_type in ['Material Transfer', 'Material Issue', 'Material Receipt']:
                    risk_score = 0.6
                elif stock_entry_type in ['Manufacture', 'Repack']:
                    risk_score = 0.7
                else:
                    risk_score = 0.5
            else:
                # Check for quantity changes
                old_items = old_doc.get('items', [])
                new_items = new_doc.get('items', [])

                total_old_qty = sum(flt(item.get('qty', 0)) for item in old_items)
                total_new_qty = sum(flt(item.get('qty', 0)) for item in new_items)

                if total_new_qty != total_old_qty:
                    change_percent = abs(total_new_qty - total_old_qty) / total_old_qty if total_old_qty > 0 else 1
                    if change_percent > 0.5:  # >50% change
                        risk_score = 0.9
                    elif change_percent > 0.2:  # >20% change
                        risk_score = 0.7
                    else:
                        risk_score = 0.5

                # Check for high-value items
                for item in new_items:
                    item_code = item.get('item_code')
                    if item_code in self.high_value_items:
                        risk_score = max(risk_score, 0.8)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit stock entry changes: {str(e)}")
            return 0.7

    def _audit_stock_reconciliation_changes(self, old_doc, new_doc):
        """
        Audit changes to stock reconciliations
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New reconciliation
                risk_score = 0.8  # High risk for stock reconciliations
            else:
                # Check for quantity adjustments
                old_items = old_doc.get('items', [])
                new_items = new_doc.get('items', [])

                significant_adjustments = 0
                for old_item, new_item in zip(old_items, new_items):
                    old_qty = flt(old_item.get('qty', 0))
                    new_qty = flt(new_item.get('qty', 0))

                    if abs(new_qty - old_qty) > 10:  # Significant adjustment
                        significant_adjustments += 1

                if significant_adjustments > 0:
                    risk_score = min(0.9, 0.6 + (significant_adjustments * 0.1))

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit stock reconciliation changes: {str(e)}")
            return 0.8

    def _audit_item_price_changes(self, old_doc, new_doc):
        """
        Audit changes to item prices
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New price
                price = flt(new_doc.get('price_list_rate', 0))
                if price > 10000:  # High-value item
                    risk_score = 0.8
                else:
                    risk_score = 0.5
            else:
                # Price changes
                old_price = flt(old_doc.get('price_list_rate', 0))
                new_price = flt(new_doc.get('price_list_rate', 0))

                if new_price != old_price:
                    change_percent = abs(new_price - old_price) / old_price if old_price > 0 else 1
                    if change_percent > 0.3:  # >30% change
                        risk_score = 0.9
                    elif change_percent > 0.1:  # >10% change
                        risk_score = 0.7
                    else:
                        risk_score = 0.5

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit item price changes: {str(e)}")
            return 0.6

    def _audit_item_master_changes(self, old_doc, new_doc):
        """
        Audit changes to item master
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New item
                risk_score = 0.4
            else:
                # Check for critical field changes
                critical_fields = ['item_name', 'item_group', 'valuation_rate', 'is_stock_item']

                for field in critical_fields:
                    if old_doc.get(field) != new_doc.get(field):
                        if field == 'valuation_rate':
                            old_val = flt(old_doc.get(field, 0))
                            new_val = flt(new_doc.get(field, 0))
                            change_percent = abs(new_val - old_val) / old_val if old_val > 0 else 1
                            if change_percent > 0.5:
                                risk_score = max(risk_score, 0.8)
                            else:
                                risk_score = max(risk_score, 0.6)
                        else:
                            risk_score = max(risk_score, 0.7)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit item master changes: {str(e)}")
            return 0.6

    def _audit_transaction_changes(self, old_doc, new_doc):
        """
        Audit changes to inventory transactions
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New transaction
                risk_score = 0.5
            else:
                # Check for item changes
                old_items = old_doc.get('items', [])
                new_items = new_doc.get('items', [])

                if len(old_items) != len(new_items):
                    risk_score = 0.7  # Item count changed

                # Check total value changes
                old_total = sum(flt(item.get('amount', 0)) for item in old_items)
                new_total = sum(flt(item.get('amount', 0)) for item in new_items)

                if new_total != old_total:
                    change_percent = abs(new_total - old_total) / old_total if old_total > 0 else 1
                    if change_percent > 0.5:
                        risk_score = max(risk_score, 0.8)
                    elif change_percent > 0.2:
                        risk_score = max(risk_score, 0.6)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit transaction changes: {str(e)}")
            return 0.6

    def _audit_serial_batch_changes(self, old_doc, new_doc):
        """
        Audit changes to serial numbers and batches
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New serial/batch
                risk_score = 0.6
            else:
                # Check for status changes
                if old_doc.get('status') != new_doc.get('status'):
                    if new_doc.get('status') in ['Expired', 'Damaged']:
                        risk_score = 0.9
                    else:
                        risk_score = 0.7

                # Check for warehouse changes
                if old_doc.get('warehouse') != new_doc.get('warehouse'):
                    risk_score = max(risk_score, 0.8)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit serial/batch changes: {str(e)}")
            return 0.7

    def _audit_quality_changes(self, old_doc, new_doc):
        """
        Audit changes to quality inspections
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New quality inspection
                risk_score = 0.7
            else:
                # Check for status changes
                if old_doc.get('status') != new_doc.get('status'):
                    if new_doc.get('status') == 'Rejected':
                        risk_score = 0.9
                    elif new_doc.get('status') == 'Accepted':
                        risk_score = 0.6

                # Check for reading changes
                old_readings = old_doc.get('readings', [])
                new_readings = new_doc.get('readings', [])

                if len(old_readings) != len(new_readings):
                    risk_score = max(risk_score, 0.8)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit quality changes: {str(e)}")
            return 0.8

    def _generate_inventory_change_summary(self, doctype_name, action, old_doc, new_doc):
        """
        Generate detailed change summary for inventory transactions
        """
        try:
            summary = {
                'action': action,
                'doctype': doctype_name,
                'timestamp': now(),
                'changes': []
            }

            if not old_doc and new_doc:
                # New document
                summary['changes'].append({
                    'type': 'creation',
                    'description': f'New {doctype_name} created',
                    'details': self._extract_key_inventory_fields(new_doc, doctype_name)
                })

            elif old_doc and new_doc:
                # Document update
                changes = self._compare_inventory_documents(old_doc, new_doc, doctype_name)
                summary['changes'] = changes

            elif old_doc and not new_doc:
                # Document deletion
                summary['changes'].append({
                    'type': 'deletion',
                    'description': f'{doctype_name} deleted',
                    'details': self._extract_key_inventory_fields(old_doc, doctype_name)
                })

            return summary

        except Exception as e:
            logger.error(f"Failed to generate inventory change summary: {str(e)}")
            return {'error': str(e)}

    def _compare_inventory_documents(self, old_doc, new_doc, doctype_name):
        """
        Compare old and new inventory documents
        """
        try:
            changes = []

            if doctype_name == 'Stock Entry':
                changes.extend(self._compare_stock_entry_fields(old_doc, new_doc))
            elif doctype_name == 'Item Price':
                changes.extend(self._compare_item_price_fields(old_doc, new_doc))
            elif doctype_name == 'Item':
                changes.extend(self._compare_item_fields(old_doc, new_doc))
            elif doctype_name in ['Serial No', 'Batch']:
                changes.extend(self._compare_serial_batch_fields(old_doc, new_doc))
            elif doctype_name == 'Quality Inspection':
                changes.extend(self._compare_quality_fields(old_doc, new_doc))
            else:
                # Generic field comparison
                changes.extend(self._compare_generic_inventory_fields(old_doc, new_doc))

            return changes

        except Exception as e:
            logger.error(f"Failed to compare inventory documents: {str(e)}")
            return []

    def _compare_stock_entry_fields(self, old_doc, new_doc):
        """Compare stock entry specific fields"""
        changes = []

        key_fields = ['stock_entry_type', 'posting_date', 'purpose']

        for field in key_fields:
            old_val = old_doc.get(field)
            new_val = new_doc.get(field)

            if old_val != new_val:
                changes.append({
                    'field': field,
                    'old_value': old_val,
                    'new_value': new_val,
                    'type': 'field_change'
                })

        # Compare items
        changes.extend(self._compare_stock_items(old_doc.get('items', []),
                                                new_doc.get('items', [])))

        return changes

    def _compare_stock_items(self, old_items, new_items):
        """Compare stock entry items"""
        changes = []

        # Compare totals
        old_total_qty = sum(flt(item.get('qty', 0)) for item in old_items)
        new_total_qty = sum(flt(item.get('qty', 0)) for item in new_items)
        old_total_value = sum(flt(item.get('amount', 0)) for item in old_items)
        new_total_value = sum(flt(item.get('amount', 0)) for item in new_items)

        if old_total_qty != new_total_qty:
            changes.append({
                'field': 'total_quantity',
                'old_value': old_total_qty,
                'new_value': new_total_qty,
                'change_percent': ((new_total_qty - old_total_qty) / old_total_qty * 100) if old_total_qty else 0,
                'type': 'quantity_change'
            })

        if old_total_value != new_total_value:
            changes.append({
                'field': 'total_value',
                'old_value': old_total_value,
                'new_value': new_total_value,
                'change_percent': ((new_total_value - old_total_value) / old_total_value * 100) if old_total_value else 0,
                'type': 'value_change'
            })

        return changes

    def _compare_item_price_fields(self, old_doc, new_doc):
        """Compare item price specific fields"""
        changes = []

        price_fields = ['item_code', 'price_list', 'price_list_rate', 'currency']

        for field in price_fields:
            old_val = old_doc.get(field)
            new_val = new_doc.get(field)

            if old_val != new_val:
                if field == 'price_list_rate':
                    change_percent = ((new_val - old_val) / old_val * 100) if old_val else 0
                    changes.append({
                        'field': field,
                        'old_value': old_val,
                        'new_value': new_val,
                        'change_percent': change_percent,
                        'type': 'price_change'
                    })
                else:
                    changes.append({
                        'field': field,
                        'old_value': old_val,
                        'new_value': new_val,
                        'type': 'field_change'
                    })

        return changes

    def _compare_item_fields(self, old_doc, new_doc):
        """Compare item specific fields"""
        changes = []

        item_fields = ['item_name', 'item_group', 'valuation_rate', 'is_stock_item',
                      'has_serial_no', 'has_batch_no']

        for field in item_fields:
            old_val = old_doc.get(field)
            new_val = new_doc.get(field)

            if old_val != new_val:
                changes.append({
                    'field': field,
                    'old_value': old_val,
                    'new_value': new_val,
                    'type': 'field_change'
                })

        return changes

    def _compare_serial_batch_fields(self, old_doc, new_doc):
        """Compare serial/batch specific fields"""
        changes = []

        serial_fields = ['item_code', 'warehouse', 'status', 'purchase_rate']

        for field in serial_fields:
            old_val = old_doc.get(field)
            new_val = new_doc.get(field)

            if old_val != new_val:
                changes.append({
                    'field': field,
                    'old_value': old_val,
                    'new_value': new_val,
                    'type': 'field_change'
                })

        return changes

    def _compare_quality_fields(self, old_doc, new_doc):
        """Compare quality inspection specific fields"""
        changes = []

        quality_fields = ['item_code', 'status', 'inspected_by', 'verified_by']

        for field in quality_fields:
            old_val = old_doc.get(field)
            new_val = new_doc.get(field)

            if old_val != new_val:
                changes.append({
                    'field': field,
                    'old_value': old_val,
                    'new_value': new_val,
                    'type': 'field_change'
                })

        return changes

    def _compare_generic_inventory_fields(self, old_doc, new_doc):
        """Generic field comparison for other inventory doctypes"""
        changes = []

        # Compare common fields
        common_fields = ['name', 'owner', 'modified_by', 'docstatus']

        for field in common_fields:
            old_val = old_doc.get(field)
            new_val = new_doc.get(field)

            if old_val != new_val:
                changes.append({
                    'field': field,
                    'old_value': old_val,
                    'new_value': new_val,
                    'type': 'field_change'
                })

        return changes

    def _extract_key_inventory_fields(self, doc, doctype_name):
        """Extract key fields for inventory summary"""
        try:
            key_fields = {
                'Stock Entry': ['stock_entry_type', 'posting_date', 'purpose'],
                'Item Price': ['item_code', 'price_list', 'price_list_rate'],
                'Item': ['item_name', 'item_group', 'valuation_rate'],
                'Serial No': ['item_code', 'warehouse', 'status'],
                'Batch': ['item_code', 'batch_id', 'expiry_date'],
                'Quality Inspection': ['item_code', 'status', 'inspected_by']
            }

            fields = key_fields.get(doctype_name, ['name', 'owner', 'creation'])
            return {field: doc.get(field) for field in fields if field in doc}

        except Exception as e:
            logger.error(f"Failed to extract key inventory fields: {str(e)}")
            return {}

    def _determine_risk_level(self, risk_score):
        """Determine risk level based on score"""
        if risk_score >= 0.8:
            return 'High'
        elif risk_score >= 0.5:
            return 'Medium'
        else:
            return 'Low'

    def _get_user_role_multiplier(self):
        """Get risk multiplier based on user role"""
        try:
            user_roles = frappe.get_roles(frappe.session.user)

            if 'System Manager' in user_roles:
                return 1.2
            elif 'Stock Manager' in user_roles:
                return 1.1
            elif 'Purchase Manager' in user_roles:
                return 1.1
            else:
                return 1.0

        except Exception:
            return 1.0

    def _assess_business_impact(self, doctype_name, action, changes_summary):
        """Assess business impact of the inventory change"""
        try:
            impact = 'Low'

            if doctype_name in ['Stock Entry', 'Stock Reconciliation']:
                if action in ['submit', 'cancel']:
                    impact = 'High'
                elif action == 'update':
                    # Check for significant value changes
                    changes = changes_summary.get('changes', [])
                    for change in changes:
                        if change.get('change_percent', 0) > 50:
                            impact = 'High'
                            break
                    else:
                        impact = 'Medium'

            elif doctype_name == 'Item Price':
                impact = 'High' if action in ['update', 'delete'] else 'Medium'

            elif doctype_name in ['Serial No', 'Batch']:
                impact = 'High' if action == 'update' else 'Medium'

            elif doctype_name == 'Quality Inspection':
                impact = 'High' if action == 'submit' else 'Medium'

            return impact

        except Exception as e:
            logger.error(f"Failed to assess business impact: {str(e)}")
            return 'Medium'

    def _check_compliance_flags(self, doctype_name, action, doc):
        """Check for compliance-related flags in inventory"""
        try:
            flags = []

            if doctype_name == 'Stock Entry':
                # Check for negative stock
                items = doc.get('items', [])
                for item in items:
                    qty = flt(item.get('qty', 0))
                    if qty < 0:
                        flags.append('negative_stock_entry')

                # Check posting date in future
                posting_date = doc.get('posting_date')
                if posting_date and getdate(posting_date) > getdate(now()):
                    flags.append('future_posting_date')

            elif doctype_name == 'Item Price':
                # Check for negative prices
                price = flt(doc.get('price_list_rate', 0))
                if price < 0:
                    flags.append('negative_price')

                # Check for unusually high prices
                if price > 1000000:  # Example threshold
                    flags.append('excessive_price')

            elif doctype_name == 'Serial No':
                # Check for expired items
                expiry_date = doc.get('expiry_date')
                if expiry_date and getdate(expiry_date) < getdate(now()):
                    flags.append('expired_serial')

            elif doctype_name == 'Batch':
                # Check for expired batches
                expiry_date = doc.get('expiry_date')
                if expiry_date and getdate(expiry_date) < getdate(now()):
                    flags.append('expired_batch')

            elif doctype_name == 'Quality Inspection':
                # Check for failed inspections
                status = doc.get('status')
                if status == 'Rejected':
                    flags.append('quality_rejection')

            return flags

        except Exception as e:
            logger.error(f"Failed to check compliance flags: {str(e)}")
            return []

# Global inventory audit engine instance
inventory_audit_engine = InventoryAuditEngine()

@frappe.whitelist()
def audit_inventory_transaction(doctype_name, docname, action, user=None, old_doc=None, new_doc=None):
    """API endpoint for inventory transaction auditing"""
    if not user:
        user = frappe.session.user

    old_doc = json.loads(old_doc) if isinstance(old_doc, str) else old_doc
    new_doc = json.loads(new_doc) if isinstance(new_doc, str) else new_doc

    result = inventory_audit_engine.audit_inventory_transaction(
        doctype_name, docname, action, user, old_doc, new_doc
    )

    if result:
        # Create the audit trail entry
        audit_doc = frappe.get_doc(result)
        audit_doc.insert(ignore_permissions=True)
        return {"success": True, "audit_entry": audit_doc.name}
    else:
        return {"success": False, "message": "No audit required"}

@frappe.whitelist()
def get_inventory_audit_summary(item_code=None, warehouse=None, date_range=None):
    """Get inventory audit summary for item, warehouse or date range"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    conditions = ["audit_category = 'Inventory'"]

    if item_code:
        conditions.append(f"JSON_EXTRACT(changes_summary, '$.item_code') = '{item_code}'")

    if warehouse:
        conditions.append(f"JSON_EXTRACT(changes_summary, '$.warehouse') = '{warehouse}'")

    if date_range:
        start_date, end_date = date_range
        conditions.append(f"creation >= '{start_date}' AND creation <= '{end_date}'")

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT COUNT(*) as total_audits,
               SUM(CASE WHEN risk_level = 'High' THEN 1 ELSE 0 END) as high_risk_count,
               SUM(CASE WHEN risk_level = 'Medium' THEN 1 ELSE 0 END) as medium_risk_count,
               AVG(risk_score) as avg_risk_score
        FROM `tabAudit Trail`
        WHERE {where_clause}
    """

    result = frappe.db.sql(query, as_dict=True)

    return result[0] if result else {}

@frappe.whitelist()
def get_inventory_compliance_flags(date_range=None):
    """Get inventory compliance flags"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    conditions = ["audit_category = 'Inventory'", "compliance_flags IS NOT NULL"]

    if date_range:
        start_date, end_date = date_range
        conditions.append(f"creation >= '{start_date}' AND creation <= '{end_date}'")

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT doctype_name, docname, compliance_flags, creation
        FROM `tabAudit Trail`
        WHERE {where_clause}
        ORDER BY creation DESC
        LIMIT 100
    """

    return frappe.db.sql(query, as_dict=True)

@frappe.whitelist()
def get_stock_movement_audit(item_code, date_range=None):
    """Get stock movement audit trail for an item"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    conditions = ["audit_category = 'Inventory'", f"JSON_EXTRACT(changes_summary, '$.item_code') = '{item_code}'"]

    if date_range:
        start_date, end_date = date_range
        conditions.append(f"creation >= '{start_date}' AND creation <= '{end_date}'")

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT doctype_name, docname, action, risk_level, creation, changes_summary
        FROM `tabAudit Trail`
        WHERE {where_clause}
        ORDER BY creation DESC
        LIMIT 50
    """

    return frappe.db.sql(query, as_dict=True)