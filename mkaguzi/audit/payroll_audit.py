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

class PayrollAuditEngine:
    """
    Specialized audit engine for payroll-related doctypes and processes
    """

    def __init__(self):
        self.payroll_doctypes = [
            'Salary Slip', 'Salary Structure', 'Salary Structure Assignment',
            'Payroll Entry', 'Employee Advance', 'Expense Claim',
            'Employee Incentive', 'Additional Salary', 'Employee Tax Exemption Declaration',
            'Employee Tax Exemption Proof Submission', 'Tax Withholding Category',
            'Salary Component', 'Salary Component Account'
        ]

        self.risk_weights = {
            'salary_increase': 0.8,
            'bonus_payment': 0.6,
            'advance_approval': 0.7,
            'tax_changes': 0.9,
            'bulk_payroll_changes': 0.8,
            'salary_structure_modification': 0.9
        }

    def audit_payroll_transaction(self, doctype_name, docname, action, user, old_doc=None, new_doc=None):
        """
        Audit a payroll-related transaction

        Args:
            doctype_name: The doctype being audited
            docname: Document name
            action: Action performed (insert, update, delete, etc.)
            user: User performing the action
            old_doc: Previous document state
            new_doc: New document state
        """
        try:
            if doctype_name not in self.payroll_doctypes:
                return None

            # Calculate risk score based on transaction type and changes
            risk_score = self._calculate_payroll_risk_score(doctype_name, action, old_doc, new_doc)

            # Generate detailed change summary
            changes_summary = self._generate_payroll_change_summary(doctype_name, action, old_doc, new_doc)

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
                'audit_category': 'Payroll',
                'business_impact': self._assess_business_impact(doctype_name, action, changes_summary),
                'compliance_flags': self._check_compliance_flags(doctype_name, action, new_doc)
            }

            return audit_entry

        except Exception as e:
            logger.error(f"Payroll audit failed for {doctype_name} {docname}: {str(e)}")
            return None

    def _calculate_payroll_risk_score(self, doctype_name, action, old_doc, new_doc):
        """
        Calculate risk score for payroll transactions
        """
        try:
            base_score = 0.0

            if action in ['insert', 'update']:
                if doctype_name == 'Salary Slip':
                    base_score = self._audit_salary_slip_changes(old_doc, new_doc)
                elif doctype_name == 'Salary Structure':
                    base_score = self._audit_salary_structure_changes(old_doc, new_doc)
                elif doctype_name == 'Employee Advance':
                    base_score = self._audit_employee_advance_changes(old_doc, new_doc)
                elif doctype_name == 'Additional Salary':
                    base_score = self._audit_additional_salary_changes(old_doc, new_doc)
                elif doctype_name == 'Payroll Entry':
                    base_score = self._audit_payroll_entry_changes(old_doc, new_doc)
                elif doctype_name in ['Expense Claim', 'Employee Incentive']:
                    base_score = 0.6  # Medium risk for expense and incentive approvals
                else:
                    base_score = 0.3  # Low risk for other payroll changes

            elif action == 'delete':
                base_score = 0.9  # High risk for deletions

            elif action in ['submit', 'cancel']:
                base_score = 0.7  # Medium-high risk for submission/cancellation

            # Apply user role multiplier
            user_role_multiplier = self._get_user_role_multiplier()
            final_score = min(base_score * user_role_multiplier, 1.0)

            return round(final_score, 2)

        except Exception as e:
            logger.error(f"Failed to calculate payroll risk score: {str(e)}")
            return 0.5

    def _audit_salary_slip_changes(self, old_doc, new_doc):
        """
        Audit changes to salary slips
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New salary slip
                if new_doc:
                    gross_pay = flt(new_doc.get('gross_pay', 0))
                    if gross_pay > 10000:  # High salary threshold
                        risk_score = 0.7
                    else:
                        risk_score = 0.4
            else:
                # Existing salary slip changes
                old_gross = flt(old_doc.get('gross_pay', 0))
                new_gross = flt(new_doc.get('gross_pay', 0))

                if new_gross != old_gross:
                    change_percent = abs(new_gross - old_gross) / old_gross if old_gross > 0 else 1
                    if change_percent > 0.5:  # >50% change
                        risk_score = 0.9
                    elif change_percent > 0.2:  # >20% change
                        risk_score = 0.7
                    else:
                        risk_score = 0.5

                # Check for component changes
                old_components = old_doc.get('earnings', []) + old_doc.get('deductions', [])
                new_components = new_doc.get('earnings', []) + new_doc.get('deductions', [])

                if len(old_components) != len(new_components):
                    risk_score = max(risk_score, 0.8)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit salary slip changes: {str(e)}")
            return 0.7

    def _audit_salary_structure_changes(self, old_doc, new_doc):
        """
        Audit changes to salary structures
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New salary structure
                risk_score = 0.6
            else:
                # Check for significant changes in earnings/deductions
                old_earnings = sum(flt(e.get('amount', 0)) for e in old_doc.get('earnings', []))
                new_earnings = sum(flt(e.get('amount', 0)) for e in new_doc.get('earnings', []))
                old_deductions = sum(flt(d.get('amount', 0)) for d in old_doc.get('deductions', []))
                new_deductions = sum(flt(d.get('amount', 0)) for d in new_doc.get('deductions', []))

                earnings_change = abs(new_earnings - old_earnings) / old_earnings if old_earnings > 0 else 1
                deductions_change = abs(new_deductions - old_deductions) / old_deductions if old_deductions > 0 else 1

                max_change = max(earnings_change, deductions_change)

                if max_change > 0.5:
                    risk_score = 0.9
                elif max_change > 0.2:
                    risk_score = 0.7
                else:
                    risk_score = 0.5

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit salary structure changes: {str(e)}")
            return 0.8

    def _audit_employee_advance_changes(self, old_doc, new_doc):
        """
        Audit changes to employee advances
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New advance
                advance_amount = flt(new_doc.get('advance_amount', 0))
                if advance_amount > 50000:  # High advance threshold
                    risk_score = 0.8
                elif advance_amount > 10000:
                    risk_score = 0.6
                else:
                    risk_score = 0.4
            else:
                # Advance modifications
                old_amount = flt(old_doc.get('advance_amount', 0))
                new_amount = flt(new_doc.get('advance_amount', 0))

                if new_amount > old_amount:
                    increase_percent = (new_amount - old_amount) / old_amount if old_amount > 0 else 1
                    if increase_percent > 0.5:
                        risk_score = 0.9
                    else:
                        risk_score = 0.7
                else:
                    risk_score = 0.5  # Modifications generally medium risk

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit employee advance changes: {str(e)}")
            return 0.7

    def _audit_additional_salary_changes(self, old_doc, new_doc):
        """
        Audit changes to additional salary
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New additional salary
                amount = flt(new_doc.get('amount', 0))
                if amount > 50000:
                    risk_score = 0.8
                elif amount > 10000:
                    risk_score = 0.6
                else:
                    risk_score = 0.4
            else:
                # Modifications
                old_amount = flt(old_doc.get('amount', 0))
                new_amount = flt(new_doc.get('amount', 0))

                if new_amount != old_amount:
                    change_percent = abs(new_amount - old_amount) / old_amount if old_amount > 0 else 1
                    if change_percent > 0.5:
                        risk_score = 0.9
                    elif change_percent > 0.2:
                        risk_score = 0.7
                    else:
                        risk_score = 0.5

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit additional salary changes: {str(e)}")
            return 0.6

    def _audit_payroll_entry_changes(self, old_doc, new_doc):
        """
        Audit changes to payroll entries
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New payroll entry
                risk_score = 0.7
            else:
                # Check for employee count changes or status changes
                old_employee_count = len(old_doc.get('employees', []))
                new_employee_count = len(new_doc.get('employees', []))

                if new_employee_count != old_employee_count:
                    risk_score = 0.8  # Bulk payroll changes are high risk

                # Check status changes
                if old_doc.get('docstatus') != new_doc.get('docstatus'):
                    if new_doc.get('docstatus') == 1:  # Submitted
                        risk_score = max(risk_score, 0.8)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit payroll entry changes: {str(e)}")
            return 0.7

    def _generate_payroll_change_summary(self, doctype_name, action, old_doc, new_doc):
        """
        Generate detailed change summary for payroll transactions
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
                    'details': self._extract_key_fields(new_doc, doctype_name)
                })

            elif old_doc and new_doc:
                # Document update
                changes = self._compare_payroll_documents(old_doc, new_doc, doctype_name)
                summary['changes'] = changes

            elif old_doc and not new_doc:
                # Document deletion
                summary['changes'].append({
                    'type': 'deletion',
                    'description': f'{doctype_name} deleted',
                    'details': self._extract_key_fields(old_doc, doctype_name)
                })

            return summary

        except Exception as e:
            logger.error(f"Failed to generate payroll change summary: {str(e)}")
            return {'error': str(e)}

    def _compare_payroll_documents(self, old_doc, new_doc, doctype_name):
        """
        Compare old and new payroll documents
        """
        try:
            changes = []

            if doctype_name == 'Salary Slip':
                changes.extend(self._compare_salary_slip_fields(old_doc, new_doc))
            elif doctype_name == 'Salary Structure':
                changes.extend(self._compare_salary_structure_fields(old_doc, new_doc))
            elif doctype_name == 'Employee Advance':
                changes.extend(self._compare_employee_advance_fields(old_doc, new_doc))
            elif doctype_name == 'Additional Salary':
                changes.extend(self._compare_additional_salary_fields(old_doc, new_doc))
            else:
                # Generic field comparison
                changes.extend(self._compare_generic_fields(old_doc, new_doc))

            return changes

        except Exception as e:
            logger.error(f"Failed to compare payroll documents: {str(e)}")
            return []

    def _compare_salary_slip_fields(self, old_doc, new_doc):
        """Compare salary slip specific fields"""
        changes = []

        key_fields = ['gross_pay', 'net_pay', 'total_deduction', 'employee', 'posting_date']

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

        # Compare earnings and deductions
        changes.extend(self._compare_salary_components(old_doc.get('earnings', []),
                                                      new_doc.get('earnings', []),
                                                      'earnings'))
        changes.extend(self._compare_salary_components(old_doc.get('deductions', []),
                                                      new_doc.get('deductions', []),
                                                      'deductions'))

        return changes

    def _compare_salary_components(self, old_components, new_components, component_type):
        """Compare salary components (earnings/deductions)"""
        changes = []

        old_dict = {c.get('salary_component'): c for c in old_components}
        new_dict = {c.get('salary_component'): c for c in new_components}

        # Added components
        for comp_name, comp_data in new_dict.items():
            if comp_name not in old_dict:
                changes.append({
                    'type': 'component_added',
                    'component_type': component_type,
                    'component': comp_name,
                    'amount': comp_data.get('amount')
                })

        # Removed components
        for comp_name in old_dict:
            if comp_name not in new_dict:
                changes.append({
                    'type': 'component_removed',
                    'component_type': component_type,
                    'component': comp_name,
                    'amount': old_dict[comp_name].get('amount')
                })

        # Modified components
        for comp_name in old_dict:
            if comp_name in new_dict:
                old_amount = flt(old_dict[comp_name].get('amount', 0))
                new_amount = flt(new_dict[comp_name].get('amount', 0))

                if old_amount != new_amount:
                    changes.append({
                        'type': 'component_modified',
                        'component_type': component_type,
                        'component': comp_name,
                        'old_amount': old_amount,
                        'new_amount': new_amount,
                        'change_percent': ((new_amount - old_amount) / old_amount * 100) if old_amount else 0
                    })

        return changes

    def _compare_salary_structure_fields(self, old_doc, new_doc):
        """Compare salary structure specific fields"""
        changes = []

        # Compare earnings and deductions totals
        old_earnings_total = sum(flt(e.get('amount', 0)) for e in old_doc.get('earnings', []))
        new_earnings_total = sum(flt(e.get('amount', 0)) for e in new_doc.get('earnings', []))
        old_deductions_total = sum(flt(d.get('amount', 0)) for d in old_doc.get('deductions', []))
        new_deductions_total = sum(flt(d.get('amount', 0)) for d in new_doc.get('deductions', []))

        if old_earnings_total != new_earnings_total:
            changes.append({
                'field': 'total_earnings',
                'old_value': old_earnings_total,
                'new_value': new_earnings_total,
                'change_percent': ((new_earnings_total - old_earnings_total) / old_earnings_total * 100) if old_earnings_total else 0
            })

        if old_deductions_total != new_deductions_total:
            changes.append({
                'field': 'total_deductions',
                'old_value': old_deductions_total,
                'new_value': new_deductions_total,
                'change_percent': ((new_deductions_total - old_deductions_total) / old_deductions_total * 100) if old_deductions_total else 0
            })

        return changes

    def _compare_employee_advance_fields(self, old_doc, new_doc):
        """Compare employee advance specific fields"""
        changes = []

        key_fields = ['advance_amount', 'purpose', 'posting_date', 'employee']

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

        return changes

    def _compare_additional_salary_fields(self, old_doc, new_doc):
        """Compare additional salary specific fields"""
        changes = []

        key_fields = ['amount', 'salary_component', 'type', 'employee', 'payroll_date']

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

        return changes

    def _compare_generic_fields(self, old_doc, new_doc):
        """Generic field comparison for other doctypes"""
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

    def _extract_key_fields(self, doc, doctype_name):
        """Extract key fields for summary"""
        try:
            key_fields = {
                'Salary Slip': ['employee', 'employee_name', 'gross_pay', 'net_pay', 'posting_date'],
                'Salary Structure': ['name', 'employee', 'base', 'total_earning', 'total_deduction'],
                'Employee Advance': ['employee', 'advance_amount', 'purpose', 'posting_date'],
                'Additional Salary': ['employee', 'amount', 'salary_component', 'payroll_date'],
                'Payroll Entry': ['posting_date', 'payroll_frequency', 'company']
            }

            fields = key_fields.get(doctype_name, ['name', 'owner', 'creation'])
            return {field: doc.get(field) for field in fields if field in doc}

        except Exception as e:
            logger.error(f"Failed to extract key fields: {str(e)}")
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
            elif 'HR Manager' in user_roles:
                return 1.1
            elif 'Accounts Manager' in user_roles:
                return 1.1
            else:
                return 1.0

        except Exception:
            return 1.0

    def _assess_business_impact(self, doctype_name, action, changes_summary):
        """Assess business impact of the change"""
        try:
            impact = 'Low'

            if doctype_name in ['Salary Slip', 'Payroll Entry']:
                if action in ['submit', 'cancel']:
                    impact = 'High'
                elif action == 'update':
                    # Check for significant financial changes
                    changes = changes_summary.get('changes', [])
                    for change in changes:
                        if change.get('change_percent', 0) > 50:
                            impact = 'High'
                            break
                    else:
                        impact = 'Medium'

            elif doctype_name in ['Salary Structure', 'Additional Salary']:
                impact = 'High' if action in ['update', 'delete'] else 'Medium'

            elif doctype_name == 'Employee Advance':
                advance_changes = [c for c in changes_summary.get('changes', [])
                                 if c.get('field') == 'advance_amount']
                if advance_changes:
                    change = advance_changes[0]
                    if change.get('change_percent', 0) > 100:
                        impact = 'High'
                    else:
                        impact = 'Medium'
                else:
                    impact = 'Low'

            return impact

        except Exception as e:
            logger.error(f"Failed to assess business impact: {str(e)}")
            return 'Medium'

    def _check_compliance_flags(self, doctype_name, action, doc):
        """Check for compliance-related flags"""
        try:
            flags = []

            if doctype_name == 'Salary Slip':
                # Check minimum wage compliance
                net_pay = flt(doc.get('net_pay', 0))
                if net_pay < 1000:  # Example minimum wage threshold
                    flags.append('potential_minimum_wage_violation')

                # Check for unusual deductions
                deductions = sum(flt(d.get('amount', 0)) for d in doc.get('deductions', []))
                gross_pay = flt(doc.get('gross_pay', 0))
                if gross_pay > 0 and (deductions / gross_pay) > 0.5:  # >50% deductions
                    flags.append('high_deduction_percentage')

            elif doctype_name == 'Employee Advance':
                # Check advance limits
                advance_amount = flt(doc.get('advance_amount', 0))
                if advance_amount > 100000:  # Example advance limit
                    flags.append('excessive_advance_amount')

            elif doctype_name == 'Additional Salary':
                # Check for frequent bonuses
                amount = flt(doc.get('amount', 0))
                if amount > 50000 and doc.get('type') == 'Bonus':
                    flags.append('large_bonus_payment')

            return flags

        except Exception as e:
            logger.error(f"Failed to check compliance flags: {str(e)}")
            return []

# Global payroll audit engine instance
payroll_audit_engine = PayrollAuditEngine()

@frappe.whitelist()
def audit_payroll_transaction(doctype_name, docname, action, user=None, old_doc=None, new_doc=None):
    """API endpoint for payroll transaction auditing"""
    if not user:
        user = frappe.session.user

    old_doc = json.loads(old_doc) if isinstance(old_doc, str) else old_doc
    new_doc = json.loads(new_doc) if isinstance(new_doc, str) else new_doc

    result = payroll_audit_engine.audit_payroll_transaction(
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
def get_payroll_audit_summary(employee=None, date_range=None):
    """Get payroll audit summary for employee or date range"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    conditions = ["audit_category = 'Payroll'"]

    if employee:
        conditions.append(f"JSON_EXTRACT(changes_summary, '$.employee') = '{employee}'")

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
def get_payroll_compliance_flags(date_range=None):
    """Get payroll compliance flags"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    conditions = ["audit_category = 'Payroll'", "compliance_flags IS NOT NULL"]

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