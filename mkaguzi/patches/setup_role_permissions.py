import frappe
from frappe import _

def execute():
    """Setup role-based permissions for audit department"""

    roles_permissions = {
        "Audit Administrator": {"full_access": 1},
        "Audit Manager": {
            "can_create": ["Audit Engagement", "Audit Finding", "Audit Report"],
            "can_edit": ["Audit Engagement", "Audit Finding", "Audit Report"],
            "can_submit": ["Audit Engagement", "Audit Finding", "Audit Report"],
            "can_approve": ["Audit Engagement", "Audit Finding", "Annual Audit Plan"]
        },
        "Lead Auditor": {
            "can_create": ["Audit Engagement", "Audit Finding", "Working Paper"],
            "can_edit": ["Audit Engagement", "Audit Finding", "Working Paper"],
            "can_submit": ["Audit Engagement", "Audit Finding"],
            "can_approve": []
        },
        "Auditor": {
            "can_create": ["Audit Finding"],
            "can_edit": ["Audit Finding"],
            "can_submit": ["Audit Finding"],
            "can_approve": []
        },
        "Audit Viewer": {
            "can_read": 1
        },
        "Quality Reviewer": {
            "can_edit": ["Audit Finding"],
            "can_submit": ["Audit Finding"],
            "can_approve": ["Audit Finding", "Audit Report"]
        },
        "Compliance Officer": {
            "can_create": ["Compliance Requirement", "Tax Compliance Tracker"],
            "can_edit": ["Compliance Requirement", "Tax Compliance Tracker"],
            "can_submit": ["Compliance Requirement", "Tax Compliance Tracker"],
            "can_approve": ["Compliance Requirement", "Tax Compliance Tracker"]
        }
    }

    doctypes_to_update = [
        "Audit Engagement", "Audit Finding", "Audit Report",
        "Risk Assessment", "Compliance Requirement",
        "Tax Compliance Tracker", "Audit Universe",
        "Annual Audit Plan",
        "Integration Hub", "Data Period", "Board Report"
    ]

    for doctype in doctypes_to_update:
        apply_role_permissions(doctype, roles_permissions)

    frappe.db.commit()
    frappe.msgprint(_("Role-based permissions setup completed"))

def apply_role_permissions(doctype, roles_permissions):
    """Apply role permissions to a DocType"""
    for role, perms in roles_permissions.items():
        if role not in ["Audit Administrator", "System Manager"]:
            update_role_permissions(doctype, role, perms)

def update_role_permissions(doctype, role, perms):
    """Update permissions for a specific role on a DocType"""
    try:
        existing_perms = frappe.db.get_all("Custom DocPerm",
            filters={"parent": doctype, "role": role})

        for perm in existing_perms:
            frappe.delete_doc("Custom DocPerm", perm)

        if perms.get("full_access"):
            create_full_access_perm(doctype, role)
        else:
            create_limited_perms(doctype, role, perms)

    except Exception as e:
        frappe.log_error(f"Error setting permissions for {doctype}/{role}: {str(e)}")

def create_full_access_perm(doctype, role):
    """Create full access permission entry"""
    frappe.get_doc({
        "doctype": "Custom DocPerm",
        "parent": doctype,
        "parenttype": "DocType",
        "parentfield": "permissions",
        "role": role,
        "permlevel": 0,
        "read": 1,
        "write": 1,
        "create": 1,
        "delete": 1,
        "submit": 1,
        "cancel": 1,
        "amend": 1
    }).insert(ignore_permissions=True)

def create_limited_perms(doctype, role, perms):
    """Create limited permission entries based on role definition"""
    perm_actions = {
        "can_create": "create",
        "can_edit": "write",
        "can_submit": "submit",
        "can_approve": "submit",
        "can_delete": "delete",
        "can_cancel": "cancel"
    }

    for perm_key, action in perm_actions.items():
        if doctype in perms.get(perm_key, []):
            create_perm_entry(doctype, role, action)

    if perms.get("can_read"):
        create_perm_entry(doctype, role, "read")

def create_perm_entry(doctype, role, action):
    """Create a single permission entry"""
    existing = frappe.db.get_all("Custom DocPerm",
        filters={"parent": doctype, "role": role, "permlevel": 0})

    if existing:
        doc = frappe.get_doc("Custom DocPerm", existing[0].name)
    else:
        doc = frappe.get_doc({
            "doctype": "Custom DocPerm",
            "parent": doctype,
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": role,
            "permlevel": 0
        })

    doc.set(action, 1)
    doc.save(ignore_permissions=True)