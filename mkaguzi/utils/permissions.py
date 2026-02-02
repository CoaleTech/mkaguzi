"""Permission Helper Utilities for Mkaguzi

This module provides helper functions for checking and enforcing permissions
instead of using ignore_permissions=True.
"""

import frappe
from frappe import _
from typing import Optional


def check_permission_and_insert(doc, throw=True):
    """Check permission and insert document

    Args:
        doc: The document to insert
        throw: Whether to throw an exception if permission is denied

    Returns:
        True if insert succeeded, False otherwise
    """
    doctype = doc.doctype
    if frappe.has_permission(doctype, 'create'):
        doc.insert()
        return True
    elif throw:
        frappe.throw(_("You do not have permission to create {0}").format(doctype))
    return False


def check_permission_and_delete(doctype, docname, throw=True):
    """Check permission and delete document

    Args:
        doctype: The doctype of the document
        docname: The name of the document to delete
        throw: Whether to throw an exception if permission is denied

    Returns:
        True if delete succeeded, False otherwise
    """
    if frappe.has_permission(doctype, 'delete'):
        frappe.delete_doc(doctype, docname)
        return True
    elif throw:
        frappe.throw(_("You do not have permission to delete {0} {1}").format(doctype, docname))
    return False


def check_permission_and_submit(doc, throw=True):
    """Check permission and submit document

    Args:
        doc: The document to submit
        throw: Whether to throw an exception if permission is denied

    Returns:
        True if submit succeeded, False otherwise
    """
    if frappe.has_permission(doc.doctype, 'submit'):
        doc.submit()
        return True
    elif throw:
        frappe.throw(_("You do not have permission to submit {0}").format(doc.doctype))
    return False


def check_permission_and_update(doc, throw=True):
    """Check permission and update document

    Args:
        doc: The document to update
        throw: Whether to throw an exception if permission is denied

    Returns:
        True if update succeeded, False otherwise
    """
    if frappe.has_permission(doc.doctype, 'write'):
        doc.save()
        return True
    elif throw:
        frappe.throw(_("You do not have permission to update {0}").format(doc.doctype))
    return False


def check_permission_and_read(doctype, docname, throw=True):
    """Check permission and read document

    Args:
        doctype: The doctype of the document
        docname: The name of the document
        throw: Whether to throw an exception if permission is denied

    Returns:
        The document if read succeeded, None otherwise
    """
    if frappe.has_permission(doctype, 'read'):
        return frappe.get_doc(doctype, docname)
    elif throw:
        frappe.throw(_("You do not have permission to read {0} {1}").format(doctype, docname))
    return None


def is_system_manager():
    """Check if current user is System Manager

    Returns:
        True if user has System Manager role
    """
    return 'System Manager' in frappe.get_roles()


def is_auditor():
    """Check if current user has any audit-related role

    Returns:
        True if user has any audit role
    """
    audit_roles = ['System Manager', 'Audit Administrator', 'Audit Manager',
                   'Lead Auditor', 'Auditor', 'Audit Viewer', 'Quality Reviewer']
    user_roles = frappe.get_roles()
    return any(role in audit_roles for role in user_roles)


def require_system_manager(throw=True):
    """Require System Manager role for operation

    Args:
        throw: Whether to throw an exception if not System Manager

    Returns:
        True if user is System Manager, False otherwise
    """
    if is_system_manager():
        return True
    elif throw:
        frappe.throw(_("This operation requires System Manager privileges"))
    return False


def require_auditor(throw=True):
    """Require any audit role for operation

    Args:
        throw: Whether to throw an exception if user lacks audit role

    Returns:
        True if user has audit role, False otherwise
    """
    if is_auditor():
        return True
    elif throw:
        frappe.throw(_("This operation requires audit privileges"))
    return False


def can_perform_risky_operation(operation: str, throw=True) -> bool:
    """Check if user can perform high-risk audit operations

    Args:
        operation: The operation being performed (create, delete, etc.)
        throw: Whether to throw an exception if permission is denied

    Returns:
        True if operation is allowed, False otherwise
    """
    # System Managers can do everything
    if is_system_manager():
        return True

    # Audit Administrators can perform most operations
    if 'Audit Administrator' in frappe.get_roles():
        return True

    # Check specific role permissions for operations
    user_roles = frappe.get_roles()

    if operation == 'delete':
        # Only System Managers and Audit Administrators can delete
        allowed = 'Audit Administrator' in user_roles
    elif operation in ['create', 'write']:
        # Lead Auditors and above can create/write
        allowed = any(role in user_roles for role in ['Audit Administrator', 'Audit Manager', 'Lead Auditor'])
    else:
        allowed = is_auditor()

    if not allowed and throw:
        frappe.throw(_("You do not have permission to perform this operation. Required role: Audit Manager or higher"))

    return allowed


def safe_insert(doc, user=None):
    """Safely insert a document with permission checking

    This is a drop-in replacement for doc.insert(ignore_permissions=True)

    Args:
        doc: The document to insert
        user: Optional user to check permissions for (defaults to current user)

    Returns:
        The inserted document name if successful
    """
    original_user = frappe.session.user

    try:
        if user and user != original_user:
            frappe.set_user(user)

        if not frappe.has_permission(doc.doctype, 'create'):
            frappe.throw(_("You do not have permission to create {0}").format(doc.doctype))

        doc.insert()
        return doc.name

    finally:
        if user and user != original_user:
            frappe.set_user(original_user)


def safe_delete(doctype, docname, user=None):
    """Safely delete a document with permission checking

    This is a drop-in replacement for frappe.delete_doc(..., ignore_permissions=True)

    Args:
        doctype: The doctype to delete
        docname: The document name to delete
        user: Optional user to check permissions for (defaults to current user)

    Returns:
        True if successful
    """
    original_user = frappe.session.user

    try:
        if user and user != original_user:
            frappe.set_user(user)

        if not frappe.has_permission(doctype, 'delete'):
            frappe.throw(_("You do not have permission to delete {0}").format(doctype))

        frappe.delete_doc(doctype, docname)
        return True

    finally:
        if user and user != original_user:
            frappe.set_user(original_user)
