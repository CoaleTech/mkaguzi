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
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class AccessAuditEngine:
    """
    Specialized audit engine for access control and user management-related doctypes and processes
    """

    def __init__(self):
        self.access_doctypes = [
            'User', 'Role', 'User Permission', 'Role Permission', 'User Role',
            'Role Profile', 'Department', 'Employee', 'User Group', 'User Type',
            'Page', 'Report', 'DocType', 'Module Def', 'Custom Role',
            'User Permission for Page and Report', 'Role Permission for Page and Report',
            'User Permission for Doctypes', 'Role Permission for Doctypes'
        ]

        self.critical_roles = ['System Manager', 'Administrator', 'HR Manager', 'Accounts Manager']
        self.sensitive_permissions = ['write', 'delete', 'cancel', 'amend', 'submit']

        self.risk_weights = {
            'user_creation': 0.7,
            'role_assignment': 0.9,
            'permission_change': 0.8,
            'system_role_access': 0.9,
            'bulk_access_changes': 0.8,
            'sensitive_data_access': 0.9,
            'unauthorized_access': 0.9
        }

    def audit_access_transaction(self, doctype_name, docname, action, user, old_doc=None, new_doc=None):
        """
        Audit an access control-related transaction

        Args:
            doctype_name: The doctype being audited
            docname: Document name
            action: Action performed (insert, update, delete, etc.)
            user: User performing the action
            old_doc: Previous document state
            new_doc: New document state
        """
        try:
            if doctype_name not in self.access_doctypes:
                return None

            # Calculate risk score based on transaction type and changes
            risk_score = self._calculate_access_risk_score(doctype_name, action, old_doc, new_doc)

            # Generate detailed change summary
            changes_summary = self._generate_access_change_summary(doctype_name, action, old_doc, new_doc)

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
                'audit_category': 'Access',
                'business_impact': self._assess_business_impact(doctype_name, action, changes_summary),
                'compliance_flags': self._check_compliance_flags(doctype_name, action, new_doc)
            }

            return audit_entry

        except Exception as e:
            logger.error(f"Access audit failed for {doctype_name} {docname}: {str(e)}")
            return None

    def _calculate_access_risk_score(self, doctype_name, action, old_doc, new_doc):
        """
        Calculate risk score for access control transactions
        """
        try:
            base_score = 0.0

            if action in ['insert', 'update']:
                if doctype_name == 'User':
                    base_score = self._audit_user_changes(old_doc, new_doc)
                elif doctype_name in ['Role', 'Role Profile']:
                    base_score = self._audit_role_changes(old_doc, new_doc)
                elif doctype_name in ['User Permission', 'User Role']:
                    base_score = self._audit_user_permission_changes(old_doc, new_doc)
                elif doctype_name in ['Role Permission', 'Role Permission for Page and Report', 'Role Permission for Doctypes']:
                    base_score = self._audit_role_permission_changes(old_doc, new_doc)
                elif doctype_name == 'User Permission for Page and Report':
                    base_score = self._audit_user_page_report_permissions(old_doc, new_doc)
                elif doctype_name == 'Department':
                    base_score = self._audit_department_changes(old_doc, new_doc)
                elif doctype_name in ['Page', 'Report', 'DocType']:
                    base_score = 0.6  # Medium risk for system object changes
                else:
                    base_score = 0.4  # Medium risk for other access changes

            elif action == 'delete':
                if doctype_name in ['User', 'Role']:
                    base_score = 0.9  # Very high risk for deleting users/roles
                elif doctype_name in ['User Permission', 'Role Permission']:
                    base_score = 0.8  # High risk for removing permissions
                else:
                    base_score = 0.7  # Medium-high risk for other deletions

            elif action in ['submit', 'cancel']:
                base_score = 0.5  # Medium risk for submission/cancellation

            # Apply user role multiplier
            user_role_multiplier = self._get_user_role_multiplier()
            final_score = min(base_score * user_role_multiplier, 1.0)

            return round(final_score, 2)

        except Exception as e:
            logger.error(f"Failed to calculate access risk score: {str(e)}")
            return 0.5

    def _audit_user_changes(self, old_doc, new_doc):
        """
        Audit changes to user accounts
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New user creation
                risk_score = 0.7
            else:
                # Check for critical user field changes
                critical_fields = ['enabled', 'user_type', 'role_profile_name']

                for field in critical_fields:
                    old_val = old_doc.get(field)
                    new_val = new_doc.get(field)

                    if old_val != new_val:
                        if field == 'enabled' and new_val == 0:
                            risk_score = max(risk_score, 0.9)  # Disabling user
                        elif field == 'role_profile_name':
                            risk_score = max(risk_score, 0.8)  # Role profile change
                        else:
                            risk_score = max(risk_score, 0.7)

                # Check for email changes
                if old_doc.get('email') != new_doc.get('email'):
                    risk_score = max(risk_score, 0.8)

                # Check for module access changes
                old_modules = set(old_doc.get('block_modules', []))
                new_modules = set(new_doc.get('block_modules', []))

                if old_modules != new_modules:
                    risk_score = max(risk_score, 0.7)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit user changes: {str(e)}")
            return 0.7

    def _audit_role_changes(self, old_doc, new_doc):
        """
        Audit changes to roles and role profiles
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New role/profile creation
                role_name = new_doc.get('role_name', '') if 'role_name' in new_doc else new_doc.get('name', '')
                if role_name in self.critical_roles:
                    risk_score = 0.9  # Critical role creation
                else:
                    risk_score = 0.7
            else:
                # Check for role name changes
                if old_doc.get('role_name') != new_doc.get('role_name'):
                    risk_score = 0.8

                # Check for desk access changes
                if old_doc.get('desk_access') != new_doc.get('desk_access'):
                    risk_score = max(risk_score, 0.7)

                # Check for two factor auth requirements
                if old_doc.get('two_factor_auth') != new_doc.get('two_factor_auth'):
                    risk_score = max(risk_score, 0.6)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit role changes: {str(e)}")
            return 0.8

    def _audit_user_permission_changes(self, old_doc, new_doc):
        """
        Audit changes to user-specific permissions
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New user permission
                # Check if it's for sensitive doctypes
                doctype = new_doc.get('doctype', '')
                allow = new_doc.get('allow', '')

                if allow in self.sensitive_permissions and self._is_sensitive_doctype(doctype):
                    risk_score = 0.9
                elif allow in self.sensitive_permissions:
                    risk_score = 0.8
                else:
                    risk_score = 0.6
            else:
                # Permission modifications
                old_allow = old_doc.get('allow', '')
                new_allow = new_doc.get('allow', '')

                if old_allow != new_allow:
                    if new_allow in self.sensitive_permissions:
                        risk_score = 0.8

                # Check for user changes
                if old_doc.get('user') != new_doc.get('user'):
                    risk_score = max(risk_score, 0.7)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit user permission changes: {str(e)}")
            return 0.7

    def _audit_role_permission_changes(self, old_doc, new_doc):
        """
        Audit changes to role-based permissions
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New role permission
                role = new_doc.get('role', '')
                allow = new_doc.get('allow', '')
                doctype = new_doc.get('doctype', '')

                # Higher risk for critical roles
                if role in self.critical_roles:
                    risk_score = 0.9
                elif allow in self.sensitive_permissions and self._is_sensitive_doctype(doctype):
                    risk_score = 0.9
                elif allow in self.sensitive_permissions:
                    risk_score = 0.8
                else:
                    risk_score = 0.7
            else:
                # Permission modifications
                old_allow = old_doc.get('allow', '')
                new_allow = new_doc.get('allow', '')

                if old_allow != new_allow and new_allow in self.sensitive_permissions:
                    risk_score = 0.8

                # Check for role changes
                old_role = old_doc.get('role', '')
                new_role = new_doc.get('role', '')

                if old_role != new_role:
                    if new_role in self.critical_roles or old_role in self.critical_roles:
                        risk_score = max(risk_score, 0.9)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit role permission changes: {str(e)}")
            return 0.8

    def _audit_user_page_report_permissions(self, old_doc, new_doc):
        """
        Audit changes to user permissions for pages and reports
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New permission
                page_report = new_doc.get('page_or_report', '')
                if self._is_sensitive_page_report(page_report):
                    risk_score = 0.8
                else:
                    risk_score = 0.6
            else:
                # Permission changes
                old_page = old_doc.get('page_or_report', '')
                new_page = new_doc.get('page_or_report', '')

                if old_page != new_page:
                    if self._is_sensitive_page_report(new_page):
                        risk_score = 0.8

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit user page/report permissions: {str(e)}")
            return 0.6

    def _audit_department_changes(self, old_doc, new_doc):
        """
        Audit changes to department structure
        """
        try:
            risk_score = 0.0

            if not old_doc:
                # New department
                risk_score = 0.5
            else:
                # Check for hierarchy changes
                if old_doc.get('parent_department') != new_doc.get('parent_department'):
                    risk_score = 0.7

                # Check for manager changes
                if old_doc.get('department_manager') != new_doc.get('department_manager'):
                    risk_score = max(risk_score, 0.6)

            return risk_score

        except Exception as e:
            logger.error(f"Failed to audit department changes: {str(e)}")
            return 0.5

    def _is_sensitive_doctype(self, doctype):
        """Check if a doctype contains sensitive information"""
        sensitive_doctypes = [
            'User', 'Employee', 'Salary Slip', 'Salary Structure',
            'Purchase Order', 'Purchase Invoice', 'Journal Entry',
            'Payment Entry', 'Bank Account', 'Cheque'
        ]
        return doctype in sensitive_doctypes

    def _is_sensitive_page_report(self, page_report):
        """Check if a page or report is sensitive"""
        sensitive_pages = [
            'user-properties', 'role-permissions-manager', 'data-import-tool',
            'bulk-update', 'system-settings', 'global-search'
        ]
        return page_report in sensitive_pages

    def _generate_access_change_summary(self, doctype_name, action, old_doc, new_doc):
        """
        Generate detailed change summary for access control transactions
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
                    'details': self._extract_key_access_fields(new_doc, doctype_name)
                })

            elif old_doc and new_doc:
                # Document update
                changes = self._compare_access_documents(old_doc, new_doc, doctype_name)
                summary['changes'] = changes

            elif old_doc and not new_doc:
                # Document deletion
                summary['changes'].append({
                    'type': 'deletion',
                    'description': f'{doctype_name} deleted',
                    'details': self._extract_key_access_fields(old_doc, doctype_name)
                })

            return summary

        except Exception as e:
            logger.error(f"Failed to generate access change summary: {str(e)}")
            return {'error': str(e)}

    def _compare_access_documents(self, old_doc, new_doc, doctype_name):
        """
        Compare old and new access control documents
        """
        try:
            changes = []

            if doctype_name == 'User':
                changes.extend(self._compare_user_fields(old_doc, new_doc))
            elif doctype_name in ['Role', 'Role Profile']:
                changes.extend(self._compare_role_fields(old_doc, new_doc))
            elif doctype_name in ['User Permission', 'Role Permission']:
                changes.extend(self._compare_permission_fields(old_doc, new_doc))
            elif doctype_name == 'Department':
                changes.extend(self._compare_department_fields(old_doc, new_doc))
            else:
                # Generic field comparison
                changes.extend(self._compare_generic_access_fields(old_doc, new_doc))

            return changes

        except Exception as e:
            logger.error(f"Failed to compare access documents: {str(e)}")
            return []

    def _compare_user_fields(self, old_doc, new_doc):
        """Compare user specific fields"""
        changes = []

        user_fields = ['email', 'enabled', 'user_type', 'role_profile_name', 'first_name', 'last_name']

        for field in user_fields:
            old_val = old_doc.get(field)
            new_val = new_doc.get(field)

            if old_val != new_val:
                change_type = 'critical' if field in ['enabled', 'role_profile_name'] else 'standard'
                changes.append({
                    'field': field,
                    'old_value': old_val,
                    'new_value': new_val,
                    'type': 'field_change',
                    'change_type': change_type
                })

        # Check blocked modules
        old_modules = set(old_doc.get('block_modules', []))
        new_modules = set(new_doc.get('block_modules', []))

        if old_modules != new_modules:
            changes.append({
                'field': 'block_modules',
                'old_value': list(old_modules),
                'new_value': list(new_modules),
                'type': 'module_access_change'
            })

        return changes

    def _compare_role_fields(self, old_doc, new_doc):
        """Compare role specific fields"""
        changes = []

        role_fields = ['role_name', 'desk_access', 'two_factor_auth', 'is_custom']

        for field in role_fields:
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

    def _compare_permission_fields(self, old_doc, new_doc):
        """Compare permission specific fields"""
        changes = []

        perm_fields = ['user', 'role', 'doctype', 'allow', 'for_value', 'is_default']

        for field in perm_fields:
            old_val = old_doc.get(field)
            new_val = new_doc.get(field)

            if old_val != new_val:
                changes.append({
                    'field': field,
                    'old_value': old_val,
                    'new_value': new_val,
                    'type': 'permission_change'
                })

        return changes

    def _compare_department_fields(self, old_doc, new_doc):
        """Compare department specific fields"""
        changes = []

        dept_fields = ['department_name', 'parent_department', 'department_manager', 'is_group']

        for field in dept_fields:
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

    def _compare_generic_access_fields(self, old_doc, new_doc):
        """Generic field comparison for other access doctypes"""
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

    def _extract_key_access_fields(self, doc, doctype_name):
        """Extract key fields for access summary"""
        try:
            key_fields = {
                'User': ['email', 'enabled', 'user_type', 'role_profile_name'],
                'Role': ['role_name', 'desk_access', 'two_factor_auth'],
                'User Permission': ['user', 'doctype', 'allow', 'for_value'],
                'Role Permission': ['role', 'doctype', 'allow', 'for_value'],
                'Department': ['department_name', 'parent_department', 'department_manager']
            }

            fields = key_fields.get(doctype_name, ['name', 'owner', 'creation'])
            return {field: doc.get(field) for field in fields if field in doc}

        except Exception as e:
            logger.error(f"Failed to extract key access fields: {str(e)}")
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
            elif 'Administrator' in user_roles:
                return 1.1
            else:
                return 1.0

        except Exception:
            return 1.0

    def _assess_business_impact(self, doctype_name, action, changes_summary):
        """Assess business impact of the access change"""
        try:
            impact = 'Low'

            if doctype_name == 'User':
                if action == 'delete':
                    impact = 'Critical'
                elif action == 'update':
                    # Check for critical changes
                    changes = changes_summary.get('changes', [])
                    critical_changes = [c for c in changes if c.get('change_type') == 'critical']
                    if critical_changes:
                        impact = 'High'
                    else:
                        impact = 'Medium'

            elif doctype_name in ['Role', 'Role Permission']:
                impact = 'High' if action in ['update', 'delete'] else 'Medium'

            elif doctype_name == 'User Permission':
                impact = 'High' if action in ['update', 'delete'] else 'Medium'

            elif doctype_name == 'Department':
                impact = 'Medium'

            return impact

        except Exception as e:
            logger.error(f"Failed to assess business impact: {str(e)}")
            return 'Medium'

    def _check_compliance_flags(self, doctype_name, action, doc):
        """Check for compliance-related flags in access control"""
        try:
            flags = []

            if doctype_name == 'User':
                # Check for disabled users
                if not doc.get('enabled'):
                    flags.append('disabled_user')

                # Check for users without two-factor auth (if required)
                user_type = doc.get('user_type')
                if user_type in ['System User', 'Website User'] and not doc.get('two_factor_auth'):
                    flags.append('missing_two_factor_auth')

                # Check for users with excessive roles
                roles = doc.get('roles', [])
                if len(roles) > 10:  # Arbitrary threshold
                    flags.append('excessive_roles')

            elif doctype_name == 'Role':
                # Check for roles with dangerous permissions
                role_name = doc.get('role_name', '')
                if role_name in ['System Manager', 'Administrator']:
                    flags.append('system_level_role')

            elif doctype_name in ['User Permission', 'Role Permission']:
                # Check for overly broad permissions
                allow = doc.get('allow', '')
                for_value = doc.get('for_value')

                if allow in ['write', 'delete'] and not for_value:
                    flags.append('overly_broad_permission')

            elif doctype_name == 'Department':
                # Check for departments without managers
                if not doc.get('department_manager'):
                    flags.append('department_without_manager')

            return flags

        except Exception as e:
            logger.error(f"Failed to check compliance flags: {str(e)}")
            return []

# Global access audit engine instance
access_audit_engine = AccessAuditEngine()

@frappe.whitelist()
def audit_access_transaction(doctype_name, docname, action, user=None, old_doc=None, new_doc=None):
    """API endpoint for access control transaction auditing"""
    if not user:
        user = frappe.session.user

    old_doc = json.loads(old_doc) if isinstance(old_doc, str) else old_doc
    new_doc = json.loads(new_doc) if isinstance(new_doc, str) else new_doc

    result = access_audit_engine.audit_access_transaction(
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
def get_access_audit_summary(user=None, role=None, date_range=None):
    """Get access audit summary for user, role or date range"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    conditions = ["audit_category = 'Access'"]

    if user:
        conditions.append(f"JSON_EXTRACT(changes_summary, '$.user') = '{user}'")

    if role:
        conditions.append(f"JSON_EXTRACT(changes_summary, '$.role') = '{role}'")

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
def get_access_compliance_flags(date_range=None):
    """Get access control compliance flags"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    conditions = ["audit_category = 'Access'", "compliance_flags IS NOT NULL"]

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
def get_user_access_history(user, date_range=None):
    """Get access change history for a user"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    conditions = ["audit_category = 'Access'", f"docname = '{user}'"]

    if date_range:
        start_date, end_date = date_range
        conditions.append(f"creation >= '{start_date}' AND creation <= '{end_date}'")

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT doctype_name, action, risk_level, creation, changes_summary
        FROM `tabAudit Trail`
        WHERE {where_clause}
        ORDER BY creation DESC
        LIMIT 50
    """

    return frappe.db.sql(query, as_dict=True)

@frappe.whitelist()
def get_role_access_changes(role, date_range=None):
    """Get access changes for a role"""
    if not frappe.has_permission('Audit Trail', 'read'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    conditions = ["audit_category = 'Access'", f"JSON_EXTRACT(changes_summary, '$.role') = '{role}'"]

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