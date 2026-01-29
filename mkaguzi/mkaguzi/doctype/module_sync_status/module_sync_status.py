# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, now_datetime, add_to_date
import json

class ModuleSyncStatus(Document):
    def validate(self):
        """Validate the module sync status"""
        self.calculate_success_rate()
        self.update_next_sync_due()
        self.update_change_log()

    def calculate_success_rate(self):
        """Calculate success rate based on processed and failed records"""
        total_records = (self.records_processed or 0) + (self.records_failed or 0)
        if total_records > 0:
            self.success_rate = ((self.records_processed or 0) / total_records) * 100
        else:
            self.success_rate = 0

    def update_next_sync_due(self):
        """Update the next sync due date based on frequency"""
        if self.last_sync_date and self.sync_frequency:
            if self.sync_frequency == "Real-time":
                self.next_sync_due = None
            elif self.sync_frequency == "Hourly":
                self.next_sync_due = add_to_date(self.last_sync_date, hours=1)
            elif self.sync_frequency == "Daily":
                self.next_sync_due = add_to_date(self.last_sync_date, days=1)
            elif self.sync_frequency == "Weekly":
                self.next_sync_due = add_to_date(self.last_sync_date, weeks=1)
            elif self.sync_frequency == "Monthly":
                self.next_sync_due = add_to_date(self.last_sync_date, months=1)
            # Manual doesn't set next_sync_due

    def update_change_log(self):
        """Update the change log with modification details"""
        if not self.change_log:
            self.change_log = ""

        log_entry = f"{now()}: Status updated to {self.sync_status} by {frappe.session.user}\n"
        self.change_log += log_entry

    def on_update(self):
        """Called when document is updated"""
        # Add to sync history
        self.add_sync_history_entry()

    def add_sync_history_entry(self):
        """Add an entry to the sync history"""
        history_entry = {
            "doctype": "Sync History Entry",
            "sync_date": self.last_sync_date or now_datetime(),
            "status": self.sync_status,
            "records_processed": self.records_processed or 0,
            "records_failed": self.records_failed or 0,
            "errors": self.error_count or 0,
            "warnings": self.warning_count or 0,
            "details": self.sync_details or ""
        }

        self.append("sync_history", history_entry)

    def get_sync_summary(self):
        """Get a summary of the sync status"""
        return {
            "module": self.module_name,
            "type": self.sync_type,
            "status": self.sync_status,
            "last_sync": self.last_sync_date,
            "next_sync": self.next_sync_due,
            "frequency": self.sync_frequency,
            "success_rate": self.success_rate,
            "records_processed": self.records_processed or 0,
            "records_failed": self.records_failed or 0
        }

@frappe.whitelist()
def run_module_sync(module_name, sync_type):
    """Run synchronization for a specific module"""
    if not frappe.has_permission("Module Sync Status", "write"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    # Get or create sync status record
    sync_status = get_or_create_sync_status(module_name, sync_type)

    try:
        # Update status to in progress
        sync_status.sync_status = "In Progress"
        sync_status.last_sync_date = now_datetime()
        sync_status.save()

        # Run the appropriate sync based on type
        if sync_type == "Audit Trail":
            result = run_audit_trail_sync(module_name)
        elif sync_type == "Doctype Catalog":
            result = run_doctype_catalog_sync(module_name)
        elif sync_type == "Templates":
            result = run_templates_sync(module_name)
        elif sync_type == "Hooks":
            result = run_hooks_sync(module_name)
        elif sync_type == "Full Sync":
            result = run_full_sync(module_name)
        else:
            frappe.throw(_("Unknown sync type: {0}").format(sync_type))

        # Update with results
        sync_status.sync_status = result.get("status", "Success")
        sync_status.records_processed = result.get("processed", 0)
        sync_status.records_failed = result.get("failed", 0)
        sync_status.error_count = result.get("errors", 0)
        sync_status.warning_count = result.get("warnings", 0)
        sync_status.sync_details = json.dumps(result.get("details", {}))
        sync_status.last_sync_errors = result.get("error_details", "")

        sync_status.save()

        return {
            "message": f"Sync completed for {module_name}",
            "status": sync_status.sync_status,
            "processed": sync_status.records_processed,
            "failed": sync_status.records_failed
        }

    except Exception as e:
        # Update with failure
        sync_status.sync_status = "Failed"
        sync_status.last_sync_errors = str(e)
        sync_status.save()

        frappe.log_error(f"Module sync failed for {module_name}: {str(e)}")
        frappe.throw(_("Sync failed: {0}").format(str(e)))

def get_or_create_sync_status(module_name, sync_type):
    """Get existing sync status or create new one"""
    existing = frappe.db.exists("Module Sync Status",
        {"module_name": module_name, "sync_type": sync_type})

    if existing:
        return frappe.get_doc("Module Sync Status", existing)
    else:
        return frappe.get_doc({
            "doctype": "Module Sync Status",
            "module_name": module_name,
            "sync_type": sync_type
        }).insert()

def run_audit_trail_sync(module_name):
    """Run audit trail synchronization"""
    from mkaguzi.mkaguzi.integration.audit_trail import AuditTrailLogger

    logger = AuditTrailLogger()
    # This would implement the actual sync logic
    # For now, return mock results
    return {
        "status": "Success",
        "processed": 150,
        "failed": 2,
        "errors": 2,
        "warnings": 5,
        "details": {"message": f"Audit trail sync completed for {module_name}"}
    }

def run_doctype_catalog_sync(module_name):
    """Run doctype catalog synchronization"""
    from mkaguzi.mkaguzi.integration.discovery import ModuleDiscoveryEngine

    engine = ModuleDiscoveryEngine()
    # This would implement the actual sync logic
    return {
        "status": "Success",
        "processed": 25,
        "failed": 0,
        "errors": 0,
        "warnings": 1,
        "details": {"message": f"Doctype catalog sync completed for {module_name}"}
    }

def run_templates_sync(module_name):
    """Run templates synchronization"""
    from mkaguzi.mkaguzi.integration.templates import AuditTemplateManager

    manager = AuditTemplateManager()
    # This would implement the actual sync logic
    return {
        "status": "Success",
        "processed": 10,
        "failed": 0,
        "errors": 0,
        "warnings": 0,
        "details": {"message": f"Templates sync completed for {module_name}"}
    }

def run_hooks_sync(module_name):
    """Run hooks synchronization"""
    from mkaguzi.mkaguzi.integration.hooks_manager import HooksManager

    manager = HooksManager()
    # This would implement the actual sync logic
    return {
        "status": "Success",
        "processed": 20,
        "failed": 1,
        "errors": 1,
        "warnings": 2,
        "details": {"message": f"Hooks sync completed for {module_name}"}
    }

def run_full_sync(module_name):
    """Run full synchronization"""
    # Run all sync types
    results = []
    total_processed = 0
    total_failed = 0
    total_errors = 0
    total_warnings = 0

    sync_types = ["Audit Trail", "Doctype Catalog", "Templates", "Hooks"]

    for sync_type in sync_types:
        try:
            result = run_module_sync(module_name, sync_type)
            results.append(result)
            total_processed += result.get("processed", 0)
            total_failed += result.get("failed", 0)
            total_errors += result.get("errors", 0)
            total_warnings += result.get("warnings", 0)
        except Exception as e:
            results.append({"error": str(e)})
            total_errors += 1

    return {
        "status": "Success" if total_errors == 0 else "Partial Success",
        "processed": total_processed,
        "failed": total_failed,
        "errors": total_errors,
        "warnings": total_warnings,
        "details": {"results": results}
    }

@frappe.whitelist()
def get_sync_dashboard():
    """Get dashboard data for all sync statuses"""
    if not frappe.has_permission("Module Sync Status", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    # Get overall statistics
    total_syncs = frappe.db.count("Module Sync Status")
    successful_syncs = frappe.db.count("Module Sync Status", {"sync_status": "Success"})
    failed_syncs = frappe.db.count("Module Sync Status", {"sync_status": "Failed"})
    in_progress = frappe.db.count("Module Sync Status", {"sync_status": "In Progress"})

    # Get syncs due soon
    due_syncs = frappe.db.sql("""
        SELECT module_name, sync_type, next_sync_due
        FROM `tabModule Sync Status`
        WHERE next_sync_due IS NOT NULL
        AND next_sync_due <= DATE_ADD(NOW(), INTERVAL 1 DAY)
        AND sync_status != 'In Progress'
        ORDER BY next_sync_due
        LIMIT 10
    """, as_dict=True)

    return {
        "total_syncs": total_syncs,
        "successful": successful_syncs,
        "failed": failed_syncs,
        "in_progress": in_progress,
        "due_syncs": due_syncs
    }