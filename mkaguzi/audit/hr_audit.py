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

class HRAuditEngine:
    """
    Specialized audit engine for HR-related doctypes and processes
    """

    def __init__(self):
        self.hr_doctypes = [
            'Employee', 'Employee Promotion', 'Employee Transfer', 'Employee Separation',
            'Attendance', 'Leave Application', 'Leave Allocation', 'Holiday List',
            'Employee Checkin', 'Shift Assignment', 'Employee Grade', 'Employee Group',
            'Job Opening', 'Job Applicant', 'Job Offer', 'Appointment Letter',
            'Employee Onboarding', 'Employee Separation', 'Employee Skill', 'Employee Education',
            'Employee Experience', 'Employee Internal Work History', 'Employee External Work History',
            'Training Program', 'Training Event', 'Training Feedback', 'Training Result',
            'Appraisal', 'Appraisal Template', 'Employee Benefit Application',
            'Employee Benefit Claim', 'Employee Tax Exemption Declaration'
        ]

        self.sensitive_fields = [
            'salary', 'date_of_birth', 'personal_email', 'cell_number',
            'emergency_phone_number', 'permanent_address', 'current_address',
            'bank_ac_no', 'pan_number', 'aadhaar_number', 'passport_number'
        ]

        self.risk_weights = {
            'employee_data_change': 0.7,
            'salary_information': 0.9,
            'personal_information': 0.8,
            'employment_status_change': 0.8,
            'bulk_hr_changes': 0.8,
            'access_rights_change': 0.9
        }

    def audit_hr_transaction(self, doctype_name, docname, action, user, old_doc=None, new_doc=None):
        """
        Audit an HR-related transaction

        Args:
            doctype_name: The doctype being audited
            docname: Document name
            action: Action performed (insert, update, delete, etc.)
            user: User performing the action
            old_doc: Previous document state
            new_doc: New document state
        """
        try:
            if doctype_name not in self.hr_doctypes:
                return None

            # Calculate risk score based on transaction type and changes
            risk_score = self._calculate_hr_risk_score(doctype_name, action, old_doc, new_doc)

            # Generate detailed change summary
            changes_summary = self._generate_hr_change_summary(doctype_name, action, old_doc, new_doc)

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
                'audit_category': 'HR',
                'business_impact': self._assess_business_impact(doctype_name, action, changes_summary),
                'compliance_flags': self._check_compliance_flags(doctype_name, action, new_doc)
            }

            return audit_entry

        except Exception as e:
            logger.error(f"HR audit failed for {doctype_name} {docname}: {str(e)}")
            return None

    def _calculate_hr_risk_score(self, doctype_name, action, old_doc, new_doc):
        """
        Calculate risk score for HR transactions
        """
        try:
            base_score = 0.0

            if action in ['insert', 'update']:
                if doctype_name == 'Employee':
                    base_score = self._audit_employee_changes(old_doc, new_doc)
                elif doctype_name in ['Employee Promotion', 'Employee Transfer']:
                    base_score = self._audit_employee_movement_changes(old_doc, new_doc)
                elif doctype_name == 'Employee Separation':
                    base_score = self._audit_employee_separation_changes(old_doc, new_doc)
                elif doctype_name in ['Leave Application', 'Leave Allocation']:
                    base_score = self._audit_leave_changes(old_doc, new_doc)
                elif doctype_name in ['Appraisal', 'Appraisal Template']:
                    base_score = self._audit_appraisal_changes(old_doc, new_doc)
                elif doctype_name in ['Job Offer', 'Appointment Letter']:
                    base_score = self._audit_recruitment_changes(old_doc, new_doc)
                elif doctype_name in ['Training Program', 'Training Event']:
                    base_score = 0.5  # Medium risk for training changes
                elif doctype_name == 'Attendance':
                    base_score = 0.3  # Lower risk for attendance changes
                else:
                    base_score = 0.4  # Medium risk for other HR changes

            elif action == 'delete':
                if doctype_name == 'Employee':
                    base_score = 0.9  # Very high risk for employee deletion
                else:
                    base_score = 0.8  # High risk for other deletions

            elif action in ['submit', 'cancel']:
                base_score = 0.6  # Medium risk for submission/cancellation

            # Apply user role multiplier
            user_role_multiplier = self._get_user_role_multiplier()
            final_score = min(base_score * user_role_multiplier, 1.0)

            return round(final_score, 2)

        except Exception as e:
            logger.error(f"Failed to calculate HR risk score: {str(e)}")
            return 0.5

    def _audit_employee_changes(self, old_doc, new_doc):
        """
        Audit changes to employee records
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New employee
                risk_score = 0.6
            else:
                # Check for sensitive field changes
                sensitive_changes = 0
                for field in self.sensitive_fields:
                    old_val = old_doc.get(field)
                    new_val = new_doc.get(field)

                    if old_val != new_val and (old_val or new_val):  # Changed from/to non-empty
                        sensitive_changes += 1

                        # Higher risk for salary changes
                        if field == 'salary':
                            risk_score = max(risk_score, 0.9)
                        elif field in ['personal_email', 'cell_number', 'permanent_address']:
                            risk_score = max(risk_score, 0.8)

                # Employment status changes
                old_status = old_doc.get('status')
                new_status = new_doc.get('status')

                if old_status != new_status:
                    if new_status in ['Left', 'Terminated']:
                        risk_score = max(risk_score, 0.9)
                    else:
                        risk_score = max(risk_score, 0.7)

                # Department/Designation changes
                if old_doc.get('department') != new_doc.get('department'):
                    risk_score = max(risk_score, 0.6)

                if old_doc.get('designation') != new_doc.get('designation'):
                    risk_score = max(risk_score, 0.6)

                # Base risk for any employee changes
                if risk_score == 0.0 and sensitive_changes > 0:
                    risk_score = 0.5

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit employee changes: {str(e)}")
            return 0.7

    def _audit_employee_movement_changes(self, old_doc, new_doc):
        """
        Audit employee promotion/transfer changes
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New promotion/transfer
                risk_score = 0.7
            else:
                # Check for significant changes
                if old_doc.get('new_designation') != new_doc.get('new_designation'):
                    risk_score = max(risk_score, 0.8)

                if old_doc.get('new_department') != new_doc.get('new_department'):
                    risk_score = max(risk_score, 0.8)

                # Salary changes in promotion
                if 'new_salary' in new_doc:
                    old_salary = flt(old_doc.get('current_salary', 0))
                    new_salary = flt(new_doc.get('new_salary', 0))

                    if new_salary > old_salary:
                        increase_percent = (new_salary - old_salary) / old_salary if old_salary > 0 else 1
                        if increase_percent > 0.5:  # >50% increase
                            risk_score = max(risk_score, 0.9)
                        elif increase_percent > 0.2:  # >20% increase
                            risk_score = max(risk_score, 0.7)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit employee movement changes: {str(e)}")
            return 0.7

    def _audit_employee_separation_changes(self, old_doc, new_doc):
        """
        Audit employee separation changes
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New separation
                risk_score = 0.9  # High risk for terminations/resignations
            else:
                # Check for changes in separation details
                key_fields = ['employee', 'separation_type', 'resignation_letter_date', 'relieving_date']

                for field in key_fields:
                    if old_doc.get(field) != new_doc.get(field):
                        risk_score = max(risk_score, 0.8)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit employee separation changes: {str(e)}")
            return 0.9

    def _audit_leave_changes(self, old_doc, new_doc):
        """
        Audit leave-related changes
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New leave application/allocation
                if new_doc.get('doctype') == 'Leave Application':
                    leave_days = flt(new_doc.get('total_leave_days', 0))
                    if leave_days > 10:  # Extended leave
                        risk_score = 0.7
                    else:
                        risk_score = 0.4
                else:
                    risk_score = 0.5
            else:
                # Check for leave duration changes
                if 'total_leave_days' in new_doc:
                    old_days = flt(old_doc.get('total_leave_days', 0))
                    new_days = flt(new_doc.get('total_leave_days', 0))

                    if new_days > old_days:
                        increase = new_days - old_days
                        if increase > 5:  # Significant increase
                            risk_score = 0.8
                        else:
                            risk_score = 0.6

                # Status changes
                if old_doc.get('status') != new_doc.get('status'):
                    if new_doc.get('status') == 'Approved':
                        risk_score = max(risk_score, 0.6)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit leave changes: {str(e)}")
            return 0.5

    def _audit_appraisal_changes(self, old_doc, new_doc):
        """
        Audit appraisal-related changes
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New appraisal
                risk_score = 0.6
            else:
                # Check for rating changes
                if 'overall_rating' in new_doc:
                    old_rating = flt(old_doc.get('overall_rating', 0))
                    new_rating = flt(new_doc.get('overall_rating', 0))

                    if abs(new_rating - old_rating) > 1:  # Significant rating change
                        risk_score = 0.8
                    elif abs(new_rating - old_rating) > 0.5:
                        risk_score = 0.6

                # Goal changes
                old_goals = len(old_doc.get('goals', []))
                new_goals = len(new_doc.get('goals', []))

                if abs(new_goals - old_goals) > 2:  # Significant goal changes
                    risk_score = max(risk_score, 0.7)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit appraisal changes: {str(e)}")
            return 0.6

    def _audit_recruitment_changes(self, old_doc, new_doc):
        """
        Audit recruitment-related changes
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New job offer/appointment
                if new_doc.get('doctype') == 'Job Offer':
                    offered_salary = flt(new_doc.get('offered_salary', 0))
                    if offered_salary > 100000:  # High salary offer
                        risk_score = 0.8
                    else:
                        risk_score = 0.6
                else:
                    risk_score = 0.7
            else:
                # Check for offer changes
                if 'offered_salary' in new_doc:
                    old_salary = flt(old_doc.get('offered_salary', 0))
                    new_salary = flt(new_doc.get('offered_salary', 0))

                    if new_salary != old_salary:
                        change_percent = abs(new_salary - old_salary) / old_salary if old_salary > 0 else 1
                        if change_percent > 0.2:  # >20% change
                            risk_score = 0.9
                        else:
                            risk_score = 0.7

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit recruitment changes: {str(e)}")
            return 0.7

    def _generate_hr_change_summary(self, doctype_name, action, old_doc, new_doc):
        """
        Generate detailed change summary for HR transactions
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
                    'details': self._extract_key_hr_fields(new_doc, doctype_name)
                })

            elif old_doc and new_doc:
                # Document update
                changes = self._compare_hr_documents(old_doc, new_doc, doctype_name)
                summary['changes'] = changes

            elif old_doc and not new_doc:
                # Document deletion
                summary['changes'].append({
                    'type': 'deletion',
                    'description': f'{doctype_name} deleted',
                    'details': self._extract_key_hr_fields(old_doc, doctype_name)
                })

            return summary

        except Exception as e:
            logger.error(f"Failed to generate HR change summary: {str(e)}")
            return {'error': str(e)}

    def _compare_hr_documents(self, old_doc, new_doc, doctype_name):
        """
        Compare old and new HR documents
        """
        try:
            changes = []

            if doctype_name == 'Employee':
                changes.extend(self._compare_employee_fields(old_doc, new_doc))
            elif doctype_name in ['Employee Promotion', 'Employee Transfer']:
                changes.extend(self._compare_employee_movement_fields(old_doc, new_doc))
            elif doctype_name == 'Employee Separation':
                changes.extend(self._compare_employee_separation_fields(old_doc, new_doc))
            elif doctype_name in ['Leave Application', 'Leave Allocation']:
                changes.extend(self._compare_leave_fields(old_doc, new_doc))
            elif doctype_name in ['Appraisal']:
                changes.extend(self._compare_appraisal_fields(old_doc, new_doc))
            elif doctype_name in ['Job Offer', 'Appointment Letter']:
                changes.extend(self._compare_recruitment_fields(old_doc, new_doc))
            else:
                # Generic field comparison
                changes.extend(self._compare_generic_hr_fields(old_doc, new_doc))

            return changes

        except Exception as e:
            logger.error(f"Failed to compare HR documents: {str(e)}")
            return []

    def _compare_employee_fields(self, old_doc, new_doc):
        """Compare employee specific fields"""
        changes = []

        key_fields = ['employee_name', 'department', 'designation', 'status', 'salary']

        for field in key_fields:
            old_val = old_doc.get(field)
            new_val = new_doc.get(field)

            if old_val != new_val:
                change_type = 'sensitive' if field in self.sensitive_fields else 'standard'
                changes.append({
                    'field': field,
                    'old_value': old_val,
                    'new_value': new_val,
                    'type': 'field_change',
                    'change_type': change_type
                })

        # Check sensitive fields separately (may be masked)
        for field in self.sensitive_fields:
            if field not in key_fields:  # Avoid duplication
                old_val = old_doc.get(field)
                new_val = new_doc.get(field)

                if old_val != new_val:
                    changes.append({
                        'field': field,
                        'old_value': '***masked***' if old_val else None,
                        'new_value': '***masked***' if new_val else None,
                        'type': 'sensitive_field_change',
                        'change_type': 'sensitive'
                    })

        return changes

    def _compare_employee_movement_fields(self, old_doc, new_doc):
        """Compare employee movement specific fields"""
        changes = []

        movement_fields = ['employee', 'current_designation', 'new_designation',
                          'current_department', 'new_department', 'effective_date']

        for field in movement_fields:
            old_val = old_doc.get(field)
            new_val = new_doc.get(field)

            if old_val != new_val:
                changes.append({
                    'field': field,
                    'old_value': old_val,
                    'new_value': new_val,
                    'type': 'field_change'
                })

        # Salary changes
        if 'new_salary' in new_doc:
            old_salary = flt(old_doc.get('current_salary', 0))
            new_salary = flt(new_doc.get('new_salary', 0))

            if old_salary != new_salary:
                changes.append({
                    'field': 'salary',
                    'old_value': old_salary,
                    'new_value': new_salary,
                    'change_percent': ((new_salary - old_salary) / old_salary * 100) if old_salary else 0,
                    'type': 'salary_change'
                })

        return changes

    def _compare_employee_separation_fields(self, old_doc, new_doc):
        """Compare employee separation specific fields"""
        changes = []

        separation_fields = ['employee', 'separation_type', 'resignation_letter_date',
                           'relieving_date', 'reason_for_leaving']

        for field in separation_fields:
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

    def _compare_leave_fields(self, old_doc, new_doc):
        """Compare leave specific fields"""
        changes = []

        leave_fields = ['employee', 'leave_type', 'from_date', 'to_date',
                       'total_leave_days', 'status', 'reason']

        for field in leave_fields:
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

    def _compare_appraisal_fields(self, old_doc, new_doc):
        """Compare appraisal specific fields"""
        changes = []

        appraisal_fields = ['employee', 'appraisal_template', 'start_date', 'end_date',
                           'overall_rating', 'goal_score', 'status']

        for field in appraisal_fields:
            old_val = old_doc.get(field)
            new_val = new_doc.get(field)

            if old_val != new_val:
                changes.append({
                    'field': field,
                    'old_value': old_val,
                    'new_value': new_val,
                    'type': 'field_change'
                })

        # Compare goals
        old_goals = old_doc.get('goals', [])
        new_goals = new_doc.get('goals', [])

        if len(old_goals) != len(new_goals):
            changes.append({
                'field': 'goals_count',
                'old_value': len(old_goals),
                'new_value': len(new_goals),
                'type': 'goals_change'
            })

        return changes

    def _compare_recruitment_fields(self, old_doc, new_doc):
        """Compare recruitment specific fields"""
        changes = []

        recruitment_fields = ['job_applicant', 'job_opening', 'offered_salary',
                             'designation', 'department', 'status']

        for field in recruitment_fields:
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

    def _compare_generic_hr_fields(self, old_doc, new_doc):
        """Generic field comparison for other HR doctypes"""
        changes = []

        # Compare common fields
        common_fields = ['name', 'owner', 'modified_by', 'docstatus', 'status']

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

    def _extract_key_hr_fields(self, doc, doctype_name):
        """Extract key fields for HR summary"""
        try:
            key_fields = {
                'Employee': ['employee_name', 'department', 'designation', 'status'],
                'Employee Promotion': ['employee', 'current_designation', 'new_designation'],
                'Employee Transfer': ['employee', 'current_department', 'new_department'],
                'Employee Separation': ['employee', 'separation_type', 'relieving_date'],
                'Leave Application': ['employee', 'leave_type', 'total_leave_days', 'status'],
                'Appraisal': ['employee', 'overall_rating', 'status'],
                'Job Offer': ['job_applicant', 'offered_salary', 'designation']
            }

            fields = key_fields.get(doctype_name, ['name', 'owner', 'creation'])
            return {field: doc.get(field) for field in fields if field in doc}

        except Exception as e:
            logger.error(f"Failed to extract key HR fields: {str(e)}")
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
            elif 'Employee' in user_roles and 'HR User' not in user_roles:
                return 0.8  # Lower risk for basic employee access
            else:
                return 1.0

        except Exception:
            return 1.0

    def _assess_business_impact(self, doctype_name, action, changes_summary):
        """Assess business impact of the HR change"""
        try:
            impact = 'Low'

            if doctype_name == 'Employee':
                if action == 'delete':
                    impact = 'Critical'
                elif action == 'update':
                    # Check for sensitive changes
                    changes = changes_summary.get('changes', [])
                    sensitive_changes = [c for c in changes if c.get('change_type') == 'sensitive']
                    if sensitive_changes:
                        impact = 'High'
                    else:
                        impact = 'Medium'

            elif doctype_name in ['Employee Separation', 'Employee Promotion', 'Employee Transfer']:
                impact = 'High' if action in ['update', 'submit'] else 'Medium'

            elif doctype_name in ['Leave Application', 'Appraisal']:
                impact = 'Medium'

            elif doctype_name in ['Job Offer', 'Appointment Letter']:
                impact = 'High' if action == 'submit' else 'Medium'

            return impact

        except Exception as e:
            logger.error(f"Failed to assess business impact: {str(e)}")
            return 'Medium'

    def _check_compliance_flags(self, doctype_name, action, doc):
        """Check for compliance-related flags in HR"""
        try:
            flags = []

            if doctype_name == 'Employee':
                # Check age compliance
                date_of_birth = doc.get('date_of_birth')
                if date_of_birth:
                    age = date_diff(now(), date_of_birth) / 365
                    if age < 18:  # Underage employee
                        flags.append('underage_employee')

                # Check for missing required information
                required_fields = ['employee_name', 'date_of_birth', 'department', 'designation']
                for field in required_fields:
                    if not doc.get(field):
                        flags.append(f'missing_{field}')

            elif doctype_name == 'Employee Separation':
                # Check notice period compliance
                resignation_date = doc.get('resignation_letter_date')
                relieving_date = doc.get('relieving_date')

                if resignation_date and relieving_date:
                    notice_days = date_diff(relieving_date, resignation_date)
                    if notice_days < 30:  # Example notice period
                        flags.append('insufficient_notice_period')

            elif doctype_name == 'Leave Application':
                # Check leave balance
                total_days = flt(doc.get('total_leave_days', 0))
                if total_days > 30:  # Excessive leave
                    flags.append('excessive_leave_request')

            elif doctype_name == 'Appraisal':
                # Check rating anomalies
                rating = flt(doc.get('overall_rating', 0))
                if rating < 1 or rating > 5:  # Invalid rating range
                    flags.append('invalid_appraisal_rating')

            return flags

        except Exception as e:
            logger.error(f"Failed to check compliance flags: {str(e)}")
            return []

# Global HR audit engine instance
hr_audit_engine = HRAuditEngine()

@frappe.whitelist()
def audit_hr_transaction(doctype_name, docname, action, user=None, old_doc=None, new_doc=None):
    """API endpoint for HR transaction auditing"""
    if not user:
        user = frappe.session.user

    old_doc = json.loads(old_doc) if isinstance(old_doc, str) else old_doc
    new_doc = json.loads(new_doc) if isinstance(new_doc, str) else new_doc

    result = hr_audit_engine.audit_hr_transaction(
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
def get_hr_audit_summary(employee=None, department=None, date_range=None):
    """Get HR audit summary for employee, department or date range"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    conditions = ["audit_category = 'HR'"]

    if employee:
        conditions.append(f"JSON_EXTRACT(changes_summary, '$.employee') = '{employee}'")

    if department:
        conditions.append(f"JSON_EXTRACT(changes_summary, '$.department') = '{department}'")

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
def get_hr_compliance_flags(date_range=None):
    """Get HR compliance flags"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    conditions = ["audit_category = 'HR'", "compliance_flags IS NOT NULL"]

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
def get_employee_data_access_log(employee, date_range=None):
    """Get access log for employee data"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    conditions = ["doctype_name = 'Employee'", f"docname = '{employee}'"]

    if date_range:
        start_date, end_date = date_range
        conditions.append(f"creation >= '{start_date}' AND creation <= '{end_date}'")

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT user, action, risk_level, creation, changes_summary
        FROM `tabAudit Trail`
        WHERE {where_clause}
        ORDER BY creation DESC
        LIMIT 50
    """

    return frappe.db.sql(query, as_dict=True)