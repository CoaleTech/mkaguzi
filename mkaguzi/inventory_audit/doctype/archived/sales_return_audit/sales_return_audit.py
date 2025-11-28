# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, nowdate, getdate, add_days
import csv
import io


class SalesReturnAudit(Document):
    def validate(self):
        self.set_deadlines()
        self.calculate_totals()
        self.update_resolution_summary()
        self.record_approvals()
        self.update_status()
        self.set_default_assignees()

    def set_deadlines(self):
        """Set resolution and investigation deadlines"""
        if not self.resolution_deadline and self.audit_date:
            # Same-day resolution requirement
            self.resolution_deadline = self.audit_date
        
        if not self.investigation_deadline and self.audit_date:
            # 3-day investigation deadline
            self.investigation_deadline = add_days(getdate(self.audit_date), 3)

    def calculate_totals(self):
        """Calculate summary totals from return items"""
        if not self.return_items:
            return
        
        self.total_items = len(self.return_items)
        self.total_system_qty = sum(item.system_quantity or 0 for item in self.return_items)
        self.total_physical_qty = sum(item.physical_quantity or 0 for item in self.return_items)
        self.total_variance_value = sum(abs(item.variance_value or 0) for item in self.return_items)

    def update_resolution_summary(self):
        """Update counts of items by verification status"""
        if not self.return_items:
            return
        
        self.items_pending = 0
        self.items_verified_match = 0
        self.items_verified_discrepancy = 0
        self.items_resolved = 0
        
        for item in self.return_items:
            if item.verification_status == "Pending":
                self.items_pending += 1
            elif item.verification_status == "Verified-Match":
                self.items_verified_match += 1
            elif item.verification_status == "Verified-Discrepancy":
                self.items_verified_discrepancy += 1
            elif item.verification_status == "Resolved":
                self.items_resolved += 1

    def set_default_assignees(self):
        """Set default assignees from warehouse if not set"""
        if self.warehouse:
            warehouse_doc = frappe.get_cached_doc("Warehouse Master", self.warehouse)
            
            if not self.stock_analyst and warehouse_doc.default_stock_analyst:
                self.stock_analyst = warehouse_doc.default_stock_analyst
            
            if not self.stock_taker and warehouse_doc.default_stock_taker:
                self.stock_taker = warehouse_doc.default_stock_taker
            
            if not self.store_manager and warehouse_doc.store_manager:
                self.store_manager = warehouse_doc.store_manager
            
            if not self.hod_approver and warehouse_doc.hod_approver:
                self.hod_approver = warehouse_doc.hod_approver

    def record_approvals(self):
        """Record approval timestamps"""
        now = now_datetime()

        if self.analyst_verified and not self.analyst_date:
            self.analyst_date = now
            if not self.stock_analyst:
                self.stock_analyst = frappe.session.user

        if self.taker_verified and not self.taker_date:
            self.taker_date = now
            if not self.stock_taker:
                self.stock_taker = frappe.session.user

        if self.manager_confirmed and not self.manager_date:
            self.manager_date = now
            if not self.store_manager:
                self.store_manager = frappe.session.user

        if self.hod_approved and not self.hod_approval_date:
            self.hod_approval_date = now
            if not self.hod_approver:
                self.hod_approver = frappe.session.user

    def update_status(self):
        """Update audit status based on workflow progress"""
        # Check if any items under investigation
        has_investigation = any(
            item.resolution_type == "Under Investigation" 
            for item in (self.return_items or [])
        )
        
        if has_investigation:
            self.status = "Under Investigation"
            return
        
        # Check approval workflow
        if self.hod_approved:
            if self.items_pending == 0 and self.items_verified_discrepancy == 0:
                self.status = "Resolved"
            else:
                self.status = "Partially Resolved"
        elif self.manager_confirmed:
            self.status = "Pending HOD Approval"
        elif self.taker_verified:
            self.status = "Pending Manager Confirmation"
        elif self.analyst_verified:
            self.status = "Pending Verification"
        elif self.return_items and len(self.return_items) > 0:
            self.status = "Pending Physical Count"
        else:
            self.status = "Draft"

    @frappe.whitelist()
    def analyst_verify(self):
        """Stock Analyst verifies the items are ready for physical count"""
        self.analyst_verified = 1
        self.analyst_date = now_datetime()
        self.stock_analyst = frappe.session.user
        self.workflow_status = "Awaiting Physical Count"
        self.save()
        return {"message": "Analyst verification complete. Awaiting physical count."}

    @frappe.whitelist()
    def stock_taker_verify(self):
        """Stock Taker verifies physical counts are complete"""
        # Check all items have physical counts
        incomplete = [
            item.item_code for item in self.return_items 
            if item.physical_quantity is None
        ]
        if incomplete:
            frappe.throw(f"Physical count missing for items: {', '.join(incomplete)}")
        
        self.taker_verified = 1
        self.taker_date = now_datetime()
        self.stock_taker = frappe.session.user
        self.workflow_status = "Awaiting Manager Confirmation"
        self.save()
        return {"message": "Physical count verification complete."}

    @frappe.whitelist()
    def manager_confirm(self):
        """Store Manager confirms the audit findings"""
        # Check all discrepancies have resolution types
        unresolved = [
            item.item_code for item in self.return_items 
            if item.verification_status == "Verified-Discrepancy" and not item.resolution_type
        ]
        if unresolved:
            frappe.throw(f"Resolution type required for discrepant items: {', '.join(unresolved)}")
        
        self.manager_confirmed = 1
        self.manager_date = now_datetime()
        self.store_manager = frappe.session.user
        self.workflow_status = "Awaiting HOD Approval"
        self.save()
        return {"message": "Manager confirmation complete. Awaiting HOD approval."}

    @frappe.whitelist()
    def hod_approve(self):
        """HOD approves the audit resolutions"""
        self.hod_approved = 1
        self.hod_approval_date = now_datetime()
        self.hod_approver = frappe.session.user
        self.workflow_status = "Completed"
        
        # Mark all items as resolved
        for item in self.return_items:
            if item.verification_status in ["Verified-Discrepancy", "Pending"]:
                if item.resolution_type:
                    item.verification_status = "Resolved"
        
        self.save()
        return {"message": "HOD approval complete. Audit closed."}

    @frappe.whitelist()
    def create_staff_charge(self, item_row_name, employee, charge_reason=None):
        """Create Staff Charge Record for a specific item"""
        from mkaguzi.inventory_audit.doctype.staff_charge_record.staff_charge_record import (
            create_staff_charge_from_audit_item
        )
        
        charge_name = create_staff_charge_from_audit_item(
            self.name, item_row_name, employee, charge_reason
        )
        
        return {"message": f"Staff Charge Record {charge_name} created", "charge_record": charge_name}


@frappe.whitelist()
def import_returns_from_csv(file_content, warehouse, audit_date=None):
    """
    Import return items from CSV file content.
    Expected columns: Item Code, Description, Return Qty, Value, Warehouse, Date, Invoice No, Reason
    """
    if not audit_date:
        audit_date = nowdate()
    
    # Parse CSV content
    reader = csv.DictReader(io.StringIO(file_content))
    
    # Group items by warehouse
    items_by_warehouse = {}
    
    for row in reader:
        row_warehouse = row.get("Warehouse", "").strip() or warehouse
        
        if row_warehouse not in items_by_warehouse:
            items_by_warehouse[row_warehouse] = []
        
        items_by_warehouse[row_warehouse].append({
            "item_code": row.get("Item Code", "").strip(),
            "item_description": row.get("Description", "").strip(),
            "system_quantity": float(row.get("Return Qty", 0) or 0),
            "unit_value": float(row.get("Value", 0) or 0),
            "invoice_no": row.get("Invoice No", "").strip(),
            "return_reason": row.get("Reason", "").strip(),
            "return_date": row.get("Date", "").strip() or audit_date,
            "verification_status": "Pending"
        })
    
    # Create audit records per warehouse
    created_audits = []
    batch_id = f"IMP-{nowdate()}-{frappe.generate_hash(length=6)}"
    
    for wh, items in items_by_warehouse.items():
        if not items:
            continue
        
        # Find or validate warehouse
        warehouse_doc = frappe.db.get_value("Warehouse Master", {"warehouse_code": wh}, "name")
        if not warehouse_doc:
            warehouse_doc = frappe.db.get_value("Warehouse Master", {"warehouse_name": wh}, "name")
        
        if not warehouse_doc:
            frappe.log_error(f"Warehouse not found: {wh}", "CSV Import Error")
            continue
        
        # Create Sales Return Audit
        audit = frappe.get_doc({
            "doctype": "Sales Return Audit",
            "audit_date": audit_date,
            "warehouse": warehouse_doc,
            "import_date": nowdate(),
            "import_batch_id": batch_id,
            "status": "Draft",
            "return_items": items
        })
        
        audit.insert()
        created_audits.append(audit.name)
    
    return {
        "message": f"Created {len(created_audits)} audit records",
        "audits": created_audits,
        "batch_id": batch_id
    }


@frappe.whitelist()
def get_pending_audits_for_warehouse(warehouse, status=None):
    """Get pending audits for a specific warehouse"""
    filters = {"warehouse": warehouse}
    
    if status:
        filters["status"] = status
    else:
        filters["status"] = ["not in", ["Resolved", "Closed"]]
    
    return frappe.get_all(
        "Sales Return Audit",
        filters=filters,
        fields=["name", "audit_date", "status", "total_items", "items_pending", "total_variance_value"],
        order_by="audit_date desc"
    )


@frappe.whitelist()
def get_overdue_investigations():
    """Get audits with investigation items past deadline"""
    today = getdate(nowdate())
    
    audits = frappe.get_all(
        "Sales Return Audit",
        filters={
            "status": "Under Investigation",
            "investigation_deadline": ["<", today]
        },
        fields=["name", "audit_date", "warehouse", "investigation_deadline", "total_variance_value"]
    )
    
    return audits


@frappe.whitelist()
def get_daily_audit_summary(audit_date=None):
    """Get summary of audits for a specific date"""
    if not audit_date:
        audit_date = nowdate()
    
    audits = frappe.get_all(
        "Sales Return Audit",
        filters={"audit_date": audit_date},
        fields=[
            "name", "warehouse", "status", "total_items", 
            "items_pending", "items_resolved", "items_verified_discrepancy",
            "total_variance_value"
        ]
    )
    
    summary = {
        "date": audit_date,
        "total_audits": len(audits),
        "total_items": sum(a.total_items or 0 for a in audits),
        "items_pending": sum(a.items_pending or 0 for a in audits),
        "items_resolved": sum(a.items_resolved or 0 for a in audits),
        "total_variance_value": sum(a.total_variance_value or 0 for a in audits),
        "audits": audits
    }
    
    return summary
