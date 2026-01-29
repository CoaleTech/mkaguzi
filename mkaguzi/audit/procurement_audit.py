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

class ProcurementAuditEngine:
    """
    Specialized audit engine for procurement and purchasing-related doctypes and processes
    """

    def __init__(self):
        self.procurement_doctypes = [
            'Supplier', 'Purchase Order', 'Purchase Receipt', 'Purchase Invoice',
            'Request for Quotation', 'Supplier Quotation', 'Material Request',
            'Purchase Taxes and Charges Template', 'Pricing Rule', 'Supplier Group',
            'Item Supplier', 'Purchase Order Item', 'Purchase Receipt Item',
            'Purchase Invoice Item', 'Supplier Scorecard', 'Supplier Scorecard Variable',
            'Blanket Order', 'Contract', 'Purchase Agreement', 'Subcontracting Order'
        ]

        self.high_value_suppliers = []  # Will be populated based on transaction history
        self.critical_suppliers = []    # Will be populated from supplier master

        self.risk_weights = {
            'supplier_master_change': 0.7,
            'purchase_order_change': 0.8,
            'price_variance': 0.9,
            'supplier_terms_change': 0.8,
            'bulk_purchase': 0.7,
            'contract_change': 0.9,
            'supplier_performance': 0.6
        }

    def audit_procurement_transaction(self, doctype_name, docname, action, user, old_doc=None, new_doc=None):
        """
        Audit a procurement-related transaction

        Args:
            doctype_name: The doctype being audited
            docname: Document name
            action: Action performed (insert, update, delete, etc.)
            user: User performing the action
            old_doc: Previous document state
            new_doc: New document state
        """
        try:
            if doctype_name not in self.procurement_doctypes:
                return None

            # Calculate risk score based on transaction type and changes
            risk_score = self._calculate_procurement_risk_score(doctype_name, action, old_doc, new_doc)

            # Generate detailed change summary
            changes_summary = self._generate_procurement_change_summary(doctype_name, action, old_doc, new_doc)

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
                'audit_category': 'Procurement',
                'business_impact': self._assess_business_impact(doctype_name, action, changes_summary),
                'compliance_flags': self._check_compliance_flags(doctype_name, action, new_doc)
            }

            return audit_entry

        except Exception as e:
            logger.error(f"Procurement audit failed for {doctype_name} {docname}: {str(e)}")
            return None

    def _calculate_procurement_risk_score(self, doctype_name, action, old_doc, new_doc):
        """
        Calculate risk score for procurement transactions
        """
        try:
            base_score = 0.0

            if action in ['insert', 'update']:
                if doctype_name == 'Purchase Order':
                    base_score = self._audit_purchase_order_changes(old_doc, new_doc)
                elif doctype_name == 'Supplier':
                    base_score = self._audit_supplier_changes(old_doc, new_doc)
                elif doctype_name in ['Purchase Receipt', 'Purchase Invoice']:
                    base_score = self._audit_purchase_transaction_changes(old_doc, new_doc)
                elif doctype_name == 'Supplier Quotation':
                    base_score = self._audit_supplier_quotation_changes(old_doc, new_doc)
                elif doctype_name == 'Request for Quotation':
                    base_score = self._audit_rfq_changes(old_doc, new_doc)
                elif doctype_name in ['Contract', 'Purchase Agreement', 'Blanket Order']:
                    base_score = self._audit_contract_changes(old_doc, new_doc)
                elif doctype_name == 'Pricing Rule':
                    base_score = self._audit_pricing_rule_changes(old_doc, new_doc)
                elif doctype_name == 'Material Request':
                    base_score = 0.5  # Medium risk for material requests
                else:
                    base_score = 0.4  # Medium risk for other procurement changes

            elif action == 'delete':
                if doctype_name in ['Purchase Order', 'Contract', 'Purchase Agreement']:
                    base_score = 0.9  # High risk for deleting commitments
                elif doctype_name == 'Supplier':
                    base_score = 0.8  # High risk for supplier deletion
                else:
                    base_score = 0.7  # Medium-high risk for other deletions

            elif action in ['submit', 'cancel']:
                base_score = 0.6  # Medium risk for submission/cancellation

            # Apply user role multiplier
            user_role_multiplier = self._get_user_role_multiplier()
            final_score = min(base_score * user_role_multiplier, 1.0)

            return round(final_score, 2)

        except Exception as e:
            logger.error(f"Failed to calculate procurement risk score: {str(e)}")
            return 0.5

    def _audit_purchase_order_changes(self, old_doc, new_doc):
        """
        Audit changes to purchase orders
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New purchase order
                total_amount = sum(flt(item.get('amount', 0)) for item in new_doc.get('items', []))
                if total_amount > 100000:  # High value PO
                    risk_score = 0.8
                elif total_amount > 25000:
                    risk_score = 0.6
                else:
                    risk_score = 0.4
            else:
                # Check for changes in existing PO
                old_total = sum(flt(item.get('amount', 0)) for item in old_doc.get('items', []))
                new_total = sum(flt(item.get('amount', 0)) for item in new_doc.get('items', []))

                if new_total != old_total:
                    change_percent = abs(new_total - old_total) / old_total if old_total > 0 else 1
                    if change_percent > 0.5:  # >50% change
                        risk_score = 0.9
                    elif change_percent > 0.2:  # >20% change
                        risk_score = 0.7
                    else:
                        risk_score = 0.5

                # Check supplier changes
                if old_doc.get('supplier') != new_doc.get('supplier'):
                    risk_score = max(risk_score, 0.8)

                # Check schedule date changes
                if old_doc.get('schedule_date') != new_doc.get('schedule_date'):
                    risk_score = max(risk_score, 0.6)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit purchase order changes: {str(e)}")
            return 0.7

    def _audit_supplier_changes(self, old_doc, new_doc):
        """
        Audit changes to supplier master
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New supplier
                risk_score = 0.5
            else:
                # Check for critical field changes
                critical_fields = ['supplier_name', 'supplier_group', 'supplier_type', 'is_frozen']

                for field in critical_fields:
                    if old_doc.get(field) != new_doc.get(field):
                        if field == 'is_frozen':
                            risk_score = max(risk_score, 0.9)  # Freezing/unfreezing supplier
                        else:
                            risk_score = max(risk_score, 0.7)

                # Check payment terms changes
                if old_doc.get('payment_terms') != new_doc.get('payment_terms'):
                    risk_score = max(risk_score, 0.8)

                # Check credit limit changes
                old_limit = flt(old_doc.get('credit_limit', 0))
                new_limit = flt(new_doc.get('credit_limit', 0))

                if new_limit != old_limit:
                    change_percent = abs(new_limit - old_limit) / old_limit if old_limit > 0 else 1
                    if change_percent > 0.5:
                        risk_score = max(risk_score, 0.8)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit supplier changes: {str(e)}")
            return 0.6

    def _audit_purchase_transaction_changes(self, old_doc, new_doc):
        """
        Audit changes to purchase receipts and invoices
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New transaction
                total_amount = sum(flt(item.get('amount', 0)) for item in new_doc.get('items', []))
                if total_amount > 50000:
                    risk_score = 0.7
                else:
                    risk_score = 0.5
            else:
                # Check for quantity/amount discrepancies
                old_items = old_doc.get('items', [])
                new_items = new_doc.get('items', [])

                # Compare totals
                old_total = sum(flt(item.get('amount', 0)) for item in old_items)
                new_total = sum(flt(item.get('amount', 0)) for item in new_items)

                if new_total != old_total:
                    change_percent = abs(new_total - old_total) / old_total if old_total > 0 else 1
                    if change_percent > 0.3:  # >30% change
                        risk_score = 0.9
                    elif change_percent > 0.1:  # >10% change
                        risk_score = 0.7

                # Check for item count changes
                if len(old_items) != len(new_items):
                    risk_score = max(risk_score, 0.6)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit purchase transaction changes: {str(e)}")
            return 0.6

    def _audit_supplier_quotation_changes(self, old_doc, new_doc):
        """
        Audit changes to supplier quotations
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New quotation
                total_amount = sum(flt(item.get('amount', 0)) for item in new_doc.get('items', []))
                if total_amount > 75000:
                    risk_score = 0.7
                else:
                    risk_score = 0.5
            else:
                # Check for price changes
                old_total = sum(flt(item.get('amount', 0)) for item in old_doc.get('items', []))
                new_total = sum(flt(item.get('amount', 0)) for item in new_doc.get('items', []))

                if new_total != old_total:
                    change_percent = abs(new_total - old_total) / old_total if old_total > 0 else 1
                    if change_percent > 0.4:  # >40% change
                        risk_score = 0.8
                    elif change_percent > 0.15:  # >15% change
                        risk_score = 0.6

                # Check validity period changes
                if old_doc.get('valid_till') != new_doc.get('valid_till'):
                    risk_score = max(risk_score, 0.5)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit supplier quotation changes: {str(e)}")
            return 0.6

    def _audit_rfq_changes(self, old_doc, new_doc):
        """
        Audit changes to request for quotations
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New RFQ
                risk_score = 0.4
            else:
                # Check for supplier list changes
                old_suppliers = len(old_doc.get('suppliers', []))
                new_suppliers = len(new_doc.get('suppliers', []))

                if abs(new_suppliers - old_suppliers) > 2:
                    risk_score = 0.7  # Significant change in supplier count

                # Check for item changes
                old_items = len(old_doc.get('items', []))
                new_items = len(new_doc.get('items', []))

                if abs(new_items - old_items) > 1:
                    risk_score = max(risk_score, 0.6)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit RFQ changes: {str(e)}")
            return 0.5

    def _audit_contract_changes(self, old_doc, new_doc):
        """
        Audit changes to contracts and agreements
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New contract
                risk_score = 0.8  # High risk for new contracts
            else:
                # Check for critical contract changes
                critical_fields = ['supplier', 'contract_terms', 'start_date', 'end_date', 'contract_value']

                for field in critical_fields:
                    if old_doc.get(field) != new_doc.get(field):
                        if field == 'contract_value':
                            old_val = flt(old_doc.get(field, 0))
                            new_val = flt(new_doc.get(field, 0))
                            change_percent = abs(new_val - old_val) / old_val if old_val > 0 else 1
                            if change_percent > 0.3:
                                risk_score = max(risk_score, 0.9)
                        else:
                            risk_score = max(risk_score, 0.8)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit contract changes: {str(e)}")
            return 0.8

    def _audit_pricing_rule_changes(self, old_doc, new_doc):
        """
        Audit changes to pricing rules
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New pricing rule
                risk_score = 0.6
            else:
                # Check for discount/percentage changes
                discount_fields = ['discount_percentage', 'discount_amount', 'rate']

                for field in discount_fields:
                    old_val = flt(old_doc.get(field, 0))
                    new_val = flt(new_doc.get(field, 0))

                    if new_val != old_val:
                        change_percent = abs(new_val - old_val) / old_val if old_val > 0 else 1
                        if change_percent > 0.5:
                            risk_score = max(risk_score, 0.9)
                        elif change_percent > 0.2:
                            risk_score = max(risk_score, 0.7)

                # Check applicability changes
                if old_doc.get('applicable_for') != new_doc.get('applicable_for'):
                    risk_score = max(risk_score, 0.8)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit pricing rule changes: {str(e)}")
            return 0.7

    def _generate_procurement_change_summary(self, doctype_name, action, old_doc, new_doc):
        """
        Generate detailed change summary for procurement transactions
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
                    'details': self._extract_key_procurement_fields(new_doc, doctype_name)
                })

            elif old_doc and new_doc:
                # Document update
                changes = self._compare_procurement_documents(old_doc, new_doc, doctype_name)
                summary['changes'] = changes

            elif old_doc and not new_doc:
                # Document deletion
                summary['changes'].append({
                    'type': 'deletion',
                    'description': f'{doctype_name} deleted',
                    'details': self._extract_key_procurement_fields(old_doc, doctype_name)
                })

            return summary

        except Exception as e:
            logger.error(f"Failed to generate procurement change summary: {str(e)}")
            return {'error': str(e)}

    def _compare_procurement_documents(self, old_doc, new_doc, doctype_name):
        """
        Compare old and new procurement documents
        """
        try:
            changes = []

            if doctype_name == 'Purchase Order':
                changes.extend(self._compare_purchase_order_fields(old_doc, new_doc))
            elif doctype_name == 'Supplier':
                changes.extend(self._compare_supplier_fields(old_doc, new_doc))
            elif doctype_name in ['Purchase Receipt', 'Purchase Invoice']:
                changes.extend(self._compare_purchase_transaction_fields(old_doc, new_doc))
            elif doctype_name == 'Supplier Quotation':
                changes.extend(self._compare_supplier_quotation_fields(old_doc, new_doc))
            elif doctype_name in ['Contract', 'Purchase Agreement']:
                changes.extend(self._compare_contract_fields(old_doc, new_doc))
            elif doctype_name == 'Pricing Rule':
                changes.extend(self._compare_pricing_rule_fields(old_doc, new_doc))
            else:
                # Generic field comparison
                changes.extend(self._compare_generic_procurement_fields(old_doc, new_doc))

            return changes

        except Exception as e:
            logger.error(f"Failed to compare procurement documents: {str(e)}")
            return []

    def _compare_purchase_order_fields(self, old_doc, new_doc):
        """Compare purchase order specific fields"""
        changes = []

        key_fields = ['supplier', 'transaction_date', 'schedule_date', 'currency']

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

        # Compare totals
        old_total = flt(old_doc.get('grand_total', 0))
        new_total = flt(new_doc.get('grand_total', 0))

        if old_total != new_total:
            changes.append({
                'field': 'grand_total',
                'old_value': old_total,
                'new_value': new_total,
                'change_percent': ((new_total - old_total) / old_total * 100) if old_total else 0,
                'type': 'total_change'
            })

        return changes

    def _compare_supplier_fields(self, old_doc, new_doc):
        """Compare supplier specific fields"""
        changes = []

        supplier_fields = ['supplier_name', 'supplier_group', 'supplier_type', 'is_frozen',
                          'payment_terms', 'credit_limit']

        for field in supplier_fields:
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

    def _compare_purchase_transaction_fields(self, old_doc, new_doc):
        """Compare purchase transaction specific fields"""
        changes = []

        transaction_fields = ['supplier', 'posting_date', 'bill_no', 'bill_date']

        for field in transaction_fields:
            old_val = old_doc.get(field)
            new_val = new_doc.get(field)

            if old_val != new_val:
                changes.append({
                    'field': field,
                    'old_value': old_val,
                    'new_value': new_val,
                    'type': 'field_change'
                })

        # Compare totals
        old_total = flt(old_doc.get('grand_total', 0))
        new_total = flt(new_doc.get('grand_total', 0))

        if old_total != new_total:
            changes.append({
                'field': 'grand_total',
                'old_value': old_total,
                'new_value': new_total,
                'change_percent': ((new_total - old_total) / old_total * 100) if old_total else 0,
                'type': 'total_change'
            })

        return changes

    def _compare_supplier_quotation_fields(self, old_doc, new_doc):
        """Compare supplier quotation specific fields"""
        changes = []

        quotation_fields = ['supplier', 'valid_till', 'currency']

        for field in quotation_fields:
            old_val = old_doc.get(field)
            new_val = new_doc.get(field)

            if old_val != new_val:
                changes.append({
                    'field': field,
                    'old_value': old_val,
                    'new_value': new_val,
                    'type': 'field_change'
                })

        # Compare totals
        old_total = flt(old_doc.get('grand_total', 0))
        new_total = flt(new_doc.get('grand_total', 0))

        if old_total != new_total:
            changes.append({
                'field': 'grand_total',
                'old_value': old_total,
                'new_value': new_total,
                'change_percent': ((new_total - old_total) / old_total * 100) if old_total else 0,
                'type': 'quotation_change'
            })

        return changes

    def _compare_contract_fields(self, old_doc, new_doc):
        """Compare contract specific fields"""
        changes = []

        contract_fields = ['supplier', 'contract_terms', 'start_date', 'end_date', 'contract_value']

        for field in contract_fields:
            old_val = old_doc.get(field)
            new_val = new_doc.get(field)

            if old_val != new_val:
                if field == 'contract_value':
                    change_percent = ((new_val - old_val) / old_val * 100) if old_val else 0
                    changes.append({
                        'field': field,
                        'old_value': old_val,
                        'new_value': new_val,
                        'change_percent': change_percent,
                        'type': 'contract_value_change'
                    })
                else:
                    changes.append({
                        'field': field,
                        'old_value': old_val,
                        'new_value': new_val,
                        'type': 'field_change'
                    })

        return changes

    def _compare_pricing_rule_fields(self, old_doc, new_doc):
        """Compare pricing rule specific fields"""
        changes = []

        pricing_fields = ['applicable_for', 'discount_percentage', 'discount_amount', 'rate']

        for field in pricing_fields:
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

    def _compare_generic_procurement_fields(self, old_doc, new_doc):
        """Generic field comparison for other procurement doctypes"""
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

    def _extract_key_procurement_fields(self, doc, doctype_name):
        """Extract key fields for procurement summary"""
        try:
            key_fields = {
                'Purchase Order': ['supplier', 'transaction_date', 'grand_total'],
                'Supplier': ['supplier_name', 'supplier_group', 'supplier_type'],
                'Purchase Receipt': ['supplier', 'posting_date', 'grand_total'],
                'Purchase Invoice': ['supplier', 'posting_date', 'grand_total'],
                'Supplier Quotation': ['supplier', 'valid_till', 'grand_total'],
                'Contract': ['supplier', 'start_date', 'end_date', 'contract_value'],
                'Pricing Rule': ['applicable_for', 'discount_percentage', 'rate']
            }

            fields = key_fields.get(doctype_name, ['name', 'owner', 'creation'])
            return {field: doc.get(field) for field in fields if field in doc}

        except Exception as e:
            logger.error(f"Failed to extract key procurement fields: {str(e)}")
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
            elif 'Purchase Manager' in user_roles:
                return 1.1
            elif 'Purchase User' in user_roles:
                return 1.0
            else:
                return 1.0

        except Exception:
            return 1.0

    def _assess_business_impact(self, doctype_name, action, changes_summary):
        """Assess business impact of the procurement change"""
        try:
            impact = 'Low'

            if doctype_name in ['Purchase Order', 'Contract', 'Purchase Agreement']:
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

            elif doctype_name == 'Supplier':
                impact = 'High' if action in ['update', 'delete'] else 'Medium'

            elif doctype_name in ['Purchase Receipt', 'Purchase Invoice']:
                impact = 'Medium' if action == 'submit' else 'Low'

            elif doctype_name == 'Pricing Rule':
                impact = 'High' if action in ['update', 'delete'] else 'Medium'

            return impact

        except Exception as e:
            logger.error(f"Failed to assess business impact: {str(e)}")
            return 'Medium'

    def _check_compliance_flags(self, doctype_name, action, doc):
        """Check for compliance-related flags in procurement"""
        try:
            flags = []

            if doctype_name == 'Purchase Order':
                # Check for unusually high PO values
                grand_total = flt(doc.get('grand_total', 0))
                if grand_total > 500000:  # Example threshold
                    flags.append('high_value_purchase_order')

                # Check transaction date vs schedule date
                transaction_date = doc.get('transaction_date')
                schedule_date = doc.get('schedule_date')

                if transaction_date and schedule_date:
                    if getdate(schedule_date) < getdate(transaction_date):
                        flags.append('backdated_schedule')

            elif doctype_name == 'Supplier':
                # Check for frozen suppliers
                if doc.get('is_frozen'):
                    flags.append('frozen_supplier')

                # Check credit limit
                credit_limit = flt(doc.get('credit_limit', 0))
                if credit_limit < 0:
                    flags.append('negative_credit_limit')

            elif doctype_name in ['Purchase Receipt', 'Purchase Invoice']:
                # Check bill date vs posting date
                bill_date = doc.get('bill_date')
                posting_date = doc.get('posting_date')

                if bill_date and posting_date:
                    if getdate(bill_date) > getdate(posting_date):
                        flags.append('future_bill_date')

            elif doctype_name == 'Contract':
                # Check contract expiry
                end_date = doc.get('end_date')
                if end_date and getdate(end_date) < getdate(now()):
                    flags.append('expired_contract')

            elif doctype_name == 'Pricing Rule':
                # Check for negative discounts
                discount_pct = flt(doc.get('discount_percentage', 0))
                discount_amt = flt(doc.get('discount_amount', 0))

                if discount_pct < 0 or discount_amt < 0:
                    flags.append('negative_discount')

            return flags

        except Exception as e:
            logger.error(f"Failed to check compliance flags: {str(e)}")
            return []

# Global procurement audit engine instance
procurement_audit_engine = ProcurementAuditEngine()

@frappe.whitelist()
def audit_procurement_transaction(doctype_name, docname, action, user=None, old_doc=None, new_doc=None):
    """API endpoint for procurement transaction auditing"""
    if not user:
        user = frappe.session.user

    old_doc = json.loads(old_doc) if isinstance(old_doc, str) else old_doc
    new_doc = json.loads(new_doc) if isinstance(new_doc, str) else new_doc

    result = procurement_audit_engine.audit_procurement_transaction(
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
def get_procurement_audit_summary(supplier=None, date_range=None):
    """Get procurement audit summary for supplier or date range"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    conditions = ["audit_category = 'Procurement'"]

    if supplier:
        conditions.append(f"JSON_EXTRACT(changes_summary, '$.supplier') = '{supplier}'")

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
def get_procurement_compliance_flags(date_range=None):
    """Get procurement compliance flags"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    conditions = ["audit_category = 'Procurement'", "compliance_flags IS NOT NULL"]

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
def get_supplier_performance_audit(supplier, date_range=None):
    """Get supplier performance audit trail"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    conditions = ["audit_category = 'Procurement'", f"JSON_EXTRACT(changes_summary, '$.supplier') = '{supplier}'"]

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