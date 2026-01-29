# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, now_datetime
import json

class AuditDoctypeCatalog(Document):
    def validate(self):
        """Validate the audit doctype catalog entry"""
        self.validate_doctype_exists()
        self.validate_audit_configuration()
        self.update_change_log()

    def validate_doctype_exists(self):
        """Validate that the doctype exists in the system"""
        if not frappe.db.exists("DocType", self.doctype_name):
            frappe.throw(_("DocType '{0}' does not exist").format(self.doctype_name))

    def validate_audit_configuration(self):
        """Validate audit configuration settings"""
        # Ensure at least one audit trigger is defined
        if not self.audit_triggers:
            frappe.throw(_("At least one audit trigger must be defined"))

        # Validate audit rules if present
        if self.audit_rules:
            for rule in self.audit_rules:
                if not rule.rule_type or not rule.condition:
                    frappe.throw(_("All audit rules must have a type and condition"))

    def update_change_log(self):
        """Update the change log with modification details"""
        if not self.change_log:
            self.change_log = ""

        log_entry = f"{now()}: Updated by {frappe.session.user}\n"
        self.change_log += log_entry

    def on_update(self):
        """Called when document is updated"""
        # Update last discovered timestamp
        self.last_discovered = now_datetime()

        # Trigger hooks update if audit configuration changed
        if self.has_value_changed("audit_triggers") or self.has_value_changed("fields_to_audit"):
            self.update_audit_hooks()

    def update_audit_hooks(self):
        """Update audit hooks based on configuration changes"""
        try:
            from mkaguzi.mkaguzi.integration.hooks_manager import HooksManager
            hooks_manager = HooksManager()

            if self.is_active:
                hooks_manager.add_doctype_hooks(self.doctype_name, self.audit_triggers)
            else:
                hooks_manager.remove_doctype_hooks(self.doctype_name)

        except Exception as e:
            frappe.log_error(f"Failed to update hooks for {self.doctype_name}: {str(e)}")

    def get_audit_summary(self):
        """Get a summary of the doctype audit configuration"""
        return {
            "doctype": self.doctype_name,
            "module": self.module,
            "category": self.audit_category,
            "risk_level": self.risk_level,
            "active": self.is_active,
            "triggers_count": len(self.audit_triggers) if self.audit_triggers else 0,
            "fields_count": len(self.fields_to_audit) if self.fields_to_audit else 0,
            "rules_count": len(self.audit_rules) if self.audit_rules else 0
        }

@frappe.whitelist()
def discover_doctypes():
    """Discover and catalog all doctypes in the system"""
    if not frappe.has_permission("Audit Doctype Catalog", "create"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    try:
        from mkaguzi.mkaguzi.integration.discovery import ModuleDiscoveryEngine
        discovery_engine = ModuleDiscoveryEngine()
        discovered_doctypes = discovery_engine.discover_all_doctypes()

        created_count = 0
        updated_count = 0

        for doctype_info in discovered_doctypes:
            # Check if catalog entry already exists
            existing = frappe.db.exists("Audit Doctype Catalog", doctype_info["name"])

            if existing:
                # Update existing entry
                doc = frappe.get_doc("Audit Doctype Catalog", doctype_info["name"])
                doc.module = doctype_info.get("module", "Core")
                doc.description = doctype_info.get("description", "")
                doc.audit_category = doctype_info.get("category", "General")
                doc.risk_level = doctype_info.get("risk_level", "Medium")
                doc.last_discovered = now_datetime()
                doc.save()
                updated_count += 1
            else:
                # Create new catalog entry
                doc = frappe.get_doc({
                    "doctype": "Audit Doctype Catalog",
                    "doctype_name": doctype_info["name"],
                    "module": doctype_info.get("module", "Core"),
                    "description": doctype_info.get("description", ""),
                    "audit_category": doctype_info.get("category", "General"),
                    "risk_level": doctype_info.get("risk_level", "Medium"),
                    "is_active": 1,
                    "auto_discover": 1,
                    "last_discovered": now_datetime()
                })
                doc.insert()
                created_count += 1

        return {
            "message": f"Discovery complete. Created: {created_count}, Updated: {updated_count}",
            "created": created_count,
            "updated": updated_count
        }

    except Exception as e:
        frappe.log_error(f"Doctype discovery failed: {str(e)}")
        frappe.throw(_("Doctype discovery failed: {0}").format(str(e)))

@frappe.whitelist()
def get_catalog_summary():
    """Get a summary of the audit doctype catalog"""
    if not frappe.has_permission("Audit Doctype Catalog", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    # Get counts by category
    categories = frappe.db.sql("""
        SELECT audit_category, COUNT(*) as count
        FROM `tabAudit Doctype Catalog`
        WHERE is_active = 1
        GROUP BY audit_category
    """, as_dict=True)

    # Get counts by risk level
    risk_levels = frappe.db.sql("""
        SELECT risk_level, COUNT(*) as count
        FROM `tabAudit Doctype Catalog`
        WHERE is_active = 1
        GROUP BY risk_level
    """, as_dict=True)

    # Get total counts
    total_active = frappe.db.count("Audit Doctype Catalog", {"is_active": 1})
    total_inactive = frappe.db.count("Audit Doctype Catalog", {"is_active": 0})

    return {
        "total_active": total_active,
        "total_inactive": total_inactive,
        "categories": categories,
        "risk_levels": risk_levels
    }

@frappe.whitelist()
def update_doctype_hooks(doctype_name):
    """Update audit hooks for a specific doctype"""
    if not frappe.has_permission("Audit Doctype Catalog", "write"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    catalog_entry = frappe.get_doc("Audit Doctype Catalog", doctype_name)
    catalog_entry.update_audit_hooks()

    return {"message": f"Hooks updated for {doctype_name}"}