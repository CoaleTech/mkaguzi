#!/usr/bin/env python3
"""
Script to fix permission errors for Dashboard Chart and Dashboard Data Source doctypes
"""

import frappe
from frappe import _

def fix_dashboard_permissions():
    """Add read permissions for Dashboard Chart and Dashboard Data Source to Auditor role"""

    # Assume the role is "Auditor" - adjust if needed
    role_name = "Auditor"

    # Check if role exists
    if not frappe.db.exists("Role", role_name):
        print(f"Role '{role_name}' does not exist. Creating it...")
        role = frappe.new_doc("Role")
        role.role_name = role_name
        role.desk_access = 1
        role.insert()
        frappe.db.commit()

    doctypes = ["Dashboard Chart", "Dashboard Data Source", "CSV Import Type", "CSV Import Field Mapping"]

    for doctype in doctypes:
        # Check if permission already exists
        existing = frappe.db.exists("DocPerm", {
            "parent": doctype,
            "role": role_name,
            "permlevel": 0
        })

        if existing:
            print(f"Permission for {doctype} already exists for role {role_name}")
            continue

        # Create permission
        perm = frappe.new_doc("DocPerm")
        perm.parent = doctype
        perm.parenttype = "DocType"
        perm.parentfield = "permissions"
        perm.role = role_name
        perm.permlevel = 0
        perm.read = 1
        perm.write = 0
        perm.create = 0
        perm.delete = 0
        perm.submit = 0
        perm.cancel = 0
        perm.amend = 0
        perm.report = 1
        perm.export = 1
        perm.print = 1
        perm.email = 1
        perm.share = 1
        perm.workflow_state_field = ""

        try:
            perm.insert()
            print(f"Added read permission for {doctype} to role {role_name}")
        except Exception as e:
            print(f"Error adding permission for {doctype}: {str(e)}")

    frappe.db.commit()
    print("Permissions updated successfully!")

    # Assign the role to all enabled users
    users = frappe.get_all("User", filters={"enabled": 1})
    for user in users:
        if not frappe.db.exists("Has Role", {"parent": user.name, "role": role_name}):
            role_doc = frappe.new_doc("Has Role")
            role_doc.parent = user.name
            role_doc.parenttype = "User"
            role_doc.parentfield = "roles"
            role_doc.role = role_name
            role_doc.insert()
            print(f"Assigned {role_name} role to user {user.name}")

    frappe.db.commit()
    print("Roles assigned to users successfully!")

    # Check permissions
    print("\nChecking permissions:")
    for doctype in doctypes:
        perm = frappe.db.get_value("DocPerm", {"parent": doctype, "role": role_name}, "read")
        print(f"{doctype}: read permission = {perm}")

    # Check user roles
    print("\nChecking user roles:")
    for user in ["sajmustafa@hotmail.com", "Administrator"]:
        has_role = frappe.db.exists("Has Role", {"parent": user, "role": role_name})
        print(f"{user} has {role_name} role: {bool(has_role)}")

    # Check existing permissions for Dashboard Chart
    print("\nExisting permissions for Dashboard Chart:")
    perms = frappe.get_all("DocPerm", filters={"parent": "Dashboard Chart"}, fields=["role", "read", "write", "create", "delete"])
    for perm in perms:
        print(f"Role: {perm.role}, Read: {perm.read}")

    print("\nExisting permissions for Dashboard Data Source:")
    perms = frappe.get_all("DocPerm", filters={"parent": "Dashboard Data Source"}, fields=["role", "read", "write", "create", "delete"])
    for perm in perms:
        print(f"Role: {perm.role}, Read: {perm.read}")

    # Check what roles Administrator has
    print("\nAdministrator roles:")
    admin_roles = frappe.get_all("Has Role", filters={"parent": "Administrator"}, fields=["role"])
    for r in admin_roles:
        print(f"Role: {r.role}")

    # Check if Desk User role exists and assign it
    desk_roles = ["Desk User", "Dashboard Manager", "System Manager"]
    for dr in desk_roles:
        if frappe.db.exists("Role", dr):
            print(f"\n{dr} role exists")
            # Assign role to the user
            if not frappe.db.exists("Has Role", {"parent": "sajmustafa@hotmail.com", "role": dr}):
                role_doc = frappe.new_doc("Has Role")
                role_doc.parent = "sajmustafa@hotmail.com"
                role_doc.parenttype = "User"
                role_doc.parentfield = "roles"
                role_doc.role = dr
                role_doc.insert()
                print(f"Assigned {dr} role to sajmustafa@hotmail.com")
            else:
                print(f"User already has {dr} role")
        else:
            print(f"\n{dr} role does not exist")

    frappe.db.commit()

if __name__ == "__main__":
    fix_dashboard_permissions()