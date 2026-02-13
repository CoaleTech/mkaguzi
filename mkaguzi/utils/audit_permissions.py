# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

"""
Audit Permissions Module

This module handles audit-related permissions for the Mkaguzi app.
Moved from hooks.py to follow Frappe framework standards.
"""

import frappe

# List of all audit-related DocTypes
AUDIT_DOCTYPES = [
    "Audit Engagement", "Audit Finding", "Audit Report",
    "Risk Assessment", "Compliance Requirement",
    "Audit Universe", "Annual Audit Plan",
    "Integration Hub", "Data Period", "Board Report"
]


def get_audit_permissions(user):
    """
    Get audit permissions for a user based on their role.
    
    Args:
        user: The user to get permissions for
        
    Returns:
        dict: Permission configuration for the user
    """
    if not user:
        return get_default_permissions()

    if "System Manager" in frappe.get_roles(user):
        return get_full_audit_permissions()

    audit_role = frappe.db.get_value("User", user, "audit_role")
    return get_audit_role_permissions(audit_role or "Auditor")


def get_full_audit_permissions():
    """
    Full access for audit administrators.
    
    Returns:
        dict: Full permission set for all audit doctypes
    """
    return {
        "can_create": AUDIT_DOCTYPES,
        "can_edit": AUDIT_DOCTYPES,
        "can_submit": AUDIT_DOCTYPES,
        "can_cancel": AUDIT_DOCTYPES,
        "can_delete": AUDIT_DOCTYPES,
        "can_approve": AUDIT_DOCTYPES,
        "can_export": AUDIT_DOCTYPES
    }


def get_audit_role_permissions(role):
    """
    Get permissions for a specific audit role.
    
    Args:
        role: The audit role name
        
    Returns:
        dict: Permission configuration for the role
    """
    role_perms = {
        "Audit Administrator": get_full_audit_permissions(),
        "Audit Manager": {
            "can_create": AUDIT_DOCTYPES,
            "can_edit": AUDIT_DOCTYPES,
            "can_submit": AUDIT_DOCTYPES,
            "can_approve": ["Audit Engagement", "Audit Finding", "Annual Audit Plan"]
        },
        "Lead Auditor": {
            "can_create": ["Audit Engagement", "Audit Finding", "Working Paper"],
            "can_edit": ["Audit Engagement", "Audit Finding", "Working Paper"],
            "can_submit": ["Audit Engagement", "Audit Finding"]
        },
        "Auditor": {
            "can_create": ["Audit Finding"],
            "can_edit": ["Audit Finding"],
            "can_submit": ["Audit Finding"]
        },
        "Audit Viewer": {
            "can_read": AUDIT_DOCTYPES
        },
        "Quality Reviewer": {
            "can_edit": ["Audit Finding", "Audit Report"],
            "can_submit": ["Audit Finding", "Audit Report"],
            "can_approve": ["Audit Finding", "Audit Report"]
        },
        "Compliance Officer": {
            "can_create": ["Compliance Requirement", "Tax Compliance Tracker"],
            "can_edit": ["Compliance Requirement", "Tax Compliance Tracker"],
            "can_submit": ["Compliance Requirement", "Tax Compliance Tracker"],
            "can_approve": ["Compliance Requirement", "Tax Compliance Tracker"]
        }
    }
    return role_perms.get(role, {"can_read": AUDIT_DOCTYPES})


def get_default_permissions():
    """
    Default permissions for users without audit roles.
    
    Returns:
        dict: Minimal read-only permissions
    """
    return {"can_read": ["Audit Finding", "Audit Report"]}


def has_audit_permission(doctype, ptype="read", user=None):
    """
    Check if user has specific audit permission.
    
    Args:
        doctype: The DocType to check permission for
        ptype: Permission type (read, create, edit, submit, etc.)
        user: The user to check (defaults to current session user)
        
    Returns:
        bool: True if user has the permission
    """
    if not user:
        user = frappe.session.user
    
    perms = get_audit_permissions(user)
    perm_key = f"can_{ptype}"
    
    if perm_key in perms:
        return doctype in perms[perm_key]
    
    return False
