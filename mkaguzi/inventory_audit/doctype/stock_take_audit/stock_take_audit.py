# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, nowdate, getdate, add_days
import csv
import io


class StockTakeAudit(Document):
    def validate(self):
        self.set_deadlines()
        self.calculate_totals()
        self.update_resolution_summary()
        self.record_approvals()
        self.update_status()
        self.set_created_by()

    def set_deadlines(self):
        """Set resolution and investigation deadlines based on stock take type"""
        if not self.audit_date:
            return
            
        audit_date = getdate(self.audit_date)
        
        # Set resolution deadline based on stock take type
        if not self.resolution_deadline:
            if self.stock_take_type == "Sales Return":
                # Same-day resolution for sales returns
                self.resolution_deadline = self.audit_date
            elif self.stock_take_type == "Daily Stock Take":
                # Same-day resolution for daily
                self.resolution_deadline = self.audit_date
            elif self.stock_take_type == "Weekly Stock Take":
                # 2-day resolution for weekly
                self.resolution_deadline = add_days(audit_date, 2)
            elif self.stock_take_type == "Monthly Stock Take":
                # 5-day resolution for monthly
                self.resolution_deadline = add_days(audit_date, 5)
            else:
                self.resolution_deadline = self.audit_date
        
        # Set investigation deadline based on stock take type
        if not self.investigation_deadline:
            if self.stock_take_type in ["Sales Return", "Daily Stock Take"]:
                self.investigation_deadline = add_days(audit_date, 3)
            elif self.stock_take_type == "Weekly Stock Take":
                self.investigation_deadline = add_days(audit_date, 5)
            elif self.stock_take_type == "Monthly Stock Take":
                self.investigation_deadline = add_days(audit_date, 10)
            else:
                self.investigation_deadline = add_days(audit_date, 3)

    def calculate_totals(self):
        """Calculate summary totals from stock take items"""
        if not self.stock_take_items:
            return
        
        self.total_items = len(self.stock_take_items)
        self.total_system_qty = sum(float(item.system_quantity or 0) for item in self.stock_take_items)
        self.total_physical_qty = sum(float(item.physical_quantity or 0) for item in self.stock_take_items)
        self.total_variance_value = sum(abs(float(item.variance_value or 0)) for item in self.stock_take_items)

    def update_resolution_summary(self):
        """Update counts of items by verification status"""
        if not self.stock_take_items:
            return
        
        self.items_pending = 0
        self.items_verified_match = 0
        self.items_verified_discrepancy = 0
        self.items_resolved = 0
        
        for item in self.stock_take_items:
            if item.verification_status == "Pending":
                self.items_pending += 1
            elif item.verification_status == "Verified-Match":
                self.items_verified_match += 1
            elif item.verification_status == "Verified-Discrepancy":
                self.items_verified_discrepancy += 1
            elif item.verification_status == "Resolved":
                self.items_resolved += 1

    def set_created_by(self):
        """Set created_by to current user if not set"""
        if not self.created_by:
            self.created_by = frappe.session.user

    def record_approvals(self):
        """Record approval timestamps"""
        now = now_datetime()

        if self.physical_count_submitted and not self.physical_count_submitted_date:
            self.physical_count_submitted_date = now
            if not self.physical_count_submitted_by:
                self.physical_count_submitted_by = frappe.session.user

        if self.analyst_reviewed and not self.analyst_review_date:
            self.analyst_review_date = now
            if not self.stock_analyst:
                self.stock_analyst = frappe.session.user

        if self.hod_approved and not self.hod_approval_date:
            self.hod_approval_date = now
            if not self.hod_approver:
                self.hod_approver = frappe.session.user

    def update_status(self):
        """Update audit status based on workflow progress"""
        # Check if any items under investigation
        has_investigation = any(
            item.resolution_type == "Under Investigation" 
            for item in (self.stock_take_items or [])
        )
        
        if has_investigation:
            self.status = "Under Investigation"
            return
        
        # Check workflow progress
        if self.hod_approved:
            self.status = "HOD Approved"
        elif self.analyst_reviewed:
            self.status = "Analyst Reviewed"
        elif self.physical_count_submitted:
            self.status = "Physical Count Submitted"
        else:
            self.status = "Draft"

    @frappe.whitelist()
    def submit_physical_count(self):
        """Stock Taker submits physical count with signed manager copy"""
        # Check all items have physical counts
        incomplete = [
            item.item_code for item in self.stock_take_items 
            if item.physical_quantity is None
        ]
        if incomplete:
            frappe.throw(f"Physical count missing for items: {', '.join(incomplete)}")
        
        # Check signed copy is attached
        if not self.signed_stock_take_copy:
            frappe.throw("Signed stock take copy must be attached before submission")
        
        self.physical_count_submitted = 1
        self.physical_count_submitted_date = now_datetime()
        self.physical_count_submitted_by = frappe.session.user
        self.status = "Physical Count Submitted"
        self.save()
        return {"message": "Physical count submitted successfully. Awaiting analyst review."}

    @frappe.whitelist()
    def analyst_review(self):
        """Analyst reviews physical counts and adds resolutions"""
        # Check all discrepancies have resolution types
        unresolved = [
            item.item_code for item in self.stock_take_items 
            if item.verification_status == "Verified-Discrepancy" and not item.resolution_type
        ]
        if unresolved:
            frappe.throw(f"Resolution type required for discrepant items: {', '.join(unresolved)}")
        
        self.analyst_reviewed = 1
        self.analyst_review_date = now_datetime()
        self.stock_analyst = frappe.session.user
        self.status = "Analyst Reviewed"
        self.save()
        return {"message": "Analyst review complete. Awaiting HOD approval."}

    @frappe.whitelist()
    def hod_approve(self):
        """HOD approves the audit and generates final report"""
        self.hod_approved = 1
        self.hod_approval_date = now_datetime()
        self.hod_approver = frappe.session.user
        self.status = "HOD Approved"
        
        # Generate final report
        self.generate_final_report()
        
        self.save()
        return {"message": "HOD approval complete. Final report generated."}

    def generate_final_report(self):
        """Generate final PDF report using print format"""
        try:
            # Check if print format exists
            print_format_exists = frappe.db.exists('Print Format', 'Stock Take Audit Summary')
            if not print_format_exists:
                frappe.log_error("Print format 'Stock Take Audit Summary' not found. Skipping PDF generation.", "Stock Take Report Generation")
                return
            
            # Use Frappe's print format to generate PDF
            from frappe.utils.print_format import download_pdf
            
            # Generate PDF content
            pdf_content = download_pdf(self.doctype, self.name, 'Stock Take Audit Summary', doc=self)
            
            # Save PDF as attachment
            file_name = f"Stock_Take_Report_{self.name}_{frappe.utils.nowdate()}.pdf"
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": file_name,
                "content": pdf_content,
                "attached_to_doctype": self.doctype,
                "attached_to_name": self.name,
                "is_private": 1
            })
            file_doc.insert()
            
            self.final_report_file = file_doc.file_url
            self.final_report_generated = 1
            self.final_report_date = frappe.utils.now_datetime()
            
        except Exception as e:
            frappe.log_error(f"Error generating final report: {str(e)}", "Stock Take Report Generation")
            # Don't throw error, just log it - approval should still proceed

    @frappe.whitelist()
    def create_staff_charge(self, item_row_name, employee, charge_reason=None):
        """Create Staff Charge Record for a specific item"""
        from mkaguzi.inventory_audit.doctype.staff_charge_record.staff_charge_record import (
            create_staff_charge_from_stock_take_item
        )
        
        charge_name = create_staff_charge_from_stock_take_item(
            self.name, item_row_name, employee, charge_reason
        )
        
        return {"message": f"Staff Charge Record {charge_name} created", "charge_record": charge_name}


@frappe.whitelist()
def import_stock_take_from_csv(file_content, warehouse, stock_take_type="Daily Stock Take", audit_date=None):
    """
    Import stock take items from CSV file content.
    Expected columns: Item Code, Description, System Qty, Value, Warehouse, Date
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
            "system_quantity": float(row.get("System Qty", 0) or row.get("Return Qty", 0) or 0),
            "unit_value": float(row.get("Value", 0) or 0),
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
        
        # Create Stock Take Audit
        audit = frappe.get_doc({
            "doctype": "Stock Take Audit",
            "stock_take_type": stock_take_type,
            "audit_date": audit_date,
            "warehouse": warehouse_doc,
            "import_date": nowdate(),
            "import_batch_id": batch_id,
            "created_by": frappe.session.user,
            "status": "Draft",
            "stock_take_items": items
        })
        
        audit.insert()
        created_audits.append(audit.name)
    
    return {
        "message": f"Created {len(created_audits)} stock take audit records",
        "audits": created_audits,
        "batch_id": batch_id
    }


@frappe.whitelist()
def get_stock_take_audits(filters=None, page=1, page_size=50):
    """Get stock take audits with filtering and pagination"""
    try:
        filter_conditions = {}
        if filters:
            data = frappe.parse_json(filters) if isinstance(filters, str) else filters
            if data.get("status"):
                filter_conditions["status"] = data["status"]
            if data.get("warehouse"):
                filter_conditions["warehouse"] = data["warehouse"]
            if data.get("stock_take_type"):
                filter_conditions["stock_take_type"] = data["stock_take_type"]
        
        offset = (int(page) - 1) * int(page_size)
        
        audits = frappe.get_all(
            "Stock Take Audit",
            filters=filter_conditions,
            fields=[
                "name", "stock_take_type", "status", "audit_date", "warehouse",
                "import_date", "resolution_deadline", "investigation_deadline",
                "total_items", "total_system_qty", "total_physical_qty",
                "total_variance_value", "items_pending", "items_verified_match",
                "items_verified_discrepancy", "items_resolved",
                "physical_count_submitted", "analyst_reviewed", "hod_approved",
                "modified"
            ],
            order_by="modified desc",
            limit_page_length=int(page_size),
            limit_start=offset
        )
        
        total_count = frappe.db.count("Stock Take Audit", filters=filter_conditions)
        
        # Get summary stats
        pending_resolution = frappe.db.count("Stock Take Audit", 
            filters={"status": ["in", ["Draft", "Physical Count Submitted", "Analyst Reviewed"]]})
        under_investigation = frappe.db.count("Stock Take Audit", 
            filters={"status": "Under Investigation"})
        total_variance = frappe.db.sql("""
            SELECT COALESCE(SUM(total_variance_value), 0) as total
            FROM `tabStock Take Audit`
            WHERE status NOT IN ('HOD Approved')
        """, as_dict=True)[0].get('total', 0)
        
        return {
            "audits": audits,
            "total_count": total_count,
            "page": int(page),
            "page_size": int(page_size),
            "total_pages": (total_count + int(page_size) - 1) // int(page_size),
            "stats": {
                "pending_resolution": pending_resolution,
                "under_investigation": under_investigation,
                "total_variance": total_variance
            }
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error fetching stock take audits")
        frappe.throw(str(e))


@frappe.whitelist()
def get_pending_stock_takes_for_warehouse(warehouse, status=None):
    """Get pending stock takes for a specific warehouse"""
    filters = {"warehouse": warehouse}
    
    if status:
        filters["status"] = status
    else:
        filters["status"] = ["not in", ["HOD Approved", "Under Investigation"]]
    
    return frappe.get_all(
        "Stock Take Audit",
        filters=filters,
        fields=["name", "stock_take_type", "audit_date", "status", "total_items", "items_pending", "total_variance_value"],
        order_by="audit_date desc"
    )


@frappe.whitelist()
def get_overdue_stock_take_investigations():
    """Get stock takes with investigation items past deadline"""
    today = getdate(nowdate())
    
    audits = frappe.get_all(
        "Stock Take Audit",
        filters={
            "status": "Under Investigation",
            "investigation_deadline": ["<", today]
        },
        fields=["name", "stock_take_type", "audit_date", "warehouse", "investigation_deadline", "total_variance_value"]
    )
    
    return audits



