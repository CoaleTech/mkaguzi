# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, now_datetime, getdate, add_months


class StaffChargeRecord(Document):
    def validate(self):
        self.validate_charge_amount()
        self.set_deduction_month()
        self.fetch_employee_details()
    
    def validate_charge_amount(self):
        """Ensure charge amount is positive"""
        if self.charge_amount and self.charge_amount < 0:
            frappe.throw("Charge Amount cannot be negative")
    
    def set_deduction_month(self):
        """Set default deduction month if not provided"""
        if not self.deduction_month:
            # Default to next month for payroll processing
            next_month = add_months(getdate(nowdate()), 1)
            self.deduction_month = next_month.strftime("%B %Y")
    
    def fetch_employee_details(self):
        """Fetch employee name if not set"""
        if self.employee and not self.employee_name:
            self.employee_name = frappe.db.get_value("User", self.employee, "full_name")
    
    def before_save(self):
        """Calculate charge amount if not set"""
        if not self.charge_amount and self.quantity and self.unit_value:
            self.charge_amount = abs(self.quantity * self.unit_value)
    
    @frappe.whitelist()
    def recommend(self):
        """Store Manager recommends the charge"""
        if self.status != "Draft":
            frappe.throw("Only Draft records can be recommended")
        
        self.status = "Pending Approval"
        self.recommended_by = frappe.session.user
        self.recommended_date = now_datetime()
        self.save()
        
        return {"message": "Staff charge recommended for HOD approval"}
    
    @frappe.whitelist()
    def approve(self):
        """HOD approves the charge"""
        if self.status != "Pending Approval":
            frappe.throw("Only records pending approval can be approved")
        
        self.status = "Approved"
        self.approved_by = frappe.session.user
        self.approval_date = now_datetime()
        self.save()
        
        return {"message": "Staff charge approved"}
    
    @frappe.whitelist()
    def mark_processed(self):
        """Mark as processed after payroll deduction"""
        if self.status != "Approved":
            frappe.throw("Only approved records can be marked as processed")
        
        self.status = "Processed"
        self.save()
        
        return {"message": "Staff charge marked as processed"}
    
    @frappe.whitelist()
    def acknowledge(self):
        """Employee acknowledges the charge"""
        self.employee_acknowledgement = 1
        self.acknowledgement_date = now_datetime()
        self.save()
        
        return {"message": "Employee acknowledgement recorded"}


@frappe.whitelist()
def create_staff_charge_from_audit_item(audit_name, item_row_name, employee, charge_reason=None):
    """Create Staff Charge Record from Stock Take Audit Item"""
    
    # Get the audit and item details
    audit = frappe.get_doc("Stock Take Audit", audit_name)
    item = None
    
    for row in audit.stock_take_items:
        if row.name == item_row_name:
            item = row
            break
    
    if not item:
        frappe.throw(f"Item row {item_row_name} not found in stock take {audit_name}")
    
    # Calculate charge amount (absolute value of variance)
    charge_amount = abs(item.variance_value) if item.variance_value else abs(item.variance_quantity * (item.unit_value or 0))
    
    # Create Staff Charge Record
    charge_record = frappe.get_doc({
        "doctype": "Staff Charge Record",
        "charge_date": audit.audit_date or nowdate(),
        "employee": employee,
        "item_code": item.item_code,
        "item_description": item.item_description,
        "quantity": abs(item.variance_quantity),
        "unit_value": item.unit_value,
        "charge_amount": charge_amount,
        "charge_reason": charge_reason or f"Stock discrepancy from Stock Take Audit {audit_name}",
        "source_audit": audit_name,
        "source_audit_item": item_row_name,
        "warehouse": audit.warehouse,
        "audit_date": audit.audit_date
    })
    
    charge_record.insert()
    
    # Update the audit item with the charge record reference
    frappe.db.set_value("Stock Take Audit Item", item_row_name, {
        "staff_charge_record": charge_record.name,
        "charge_amount": charge_amount
    })
    
    return charge_record.name


@frappe.whitelist()
def create_staff_charge_from_stock_take_item(audit_name, item_row_name, employee, charge_reason=None):
    """Create Staff Charge Record from Stock Take Audit Item"""
    
    # Get the audit and item details
    audit = frappe.get_doc("Stock Take Audit", audit_name)
    item = None
    
    for row in audit.stock_take_items:
        if row.name == item_row_name:
            item = row
            break
    
    if not item:
        frappe.throw(f"Item row {item_row_name} not found in stock take {audit_name}")
    
    # Calculate charge amount (absolute value of variance)
    charge_amount = abs(item.variance_value) if item.variance_value else abs(item.variance_quantity * (item.unit_value or 0))
    
    # Create Staff Charge Record
    charge_record = frappe.get_doc({
        "doctype": "Staff Charge Record",
        "charge_date": audit.audit_date or nowdate(),
        "employee": employee,
        "item_code": item.item_code,
        "item_description": item.item_description,
        "quantity": abs(item.variance_quantity),
        "unit_value": item.unit_value,
        "charge_amount": charge_amount,
        "charge_reason": charge_reason or f"Stock discrepancy from Stock Take Audit {audit_name}",
        "source_audit": audit_name,
        "source_audit_item": item_row_name,
        "warehouse": audit.warehouse,
        "audit_date": audit.audit_date
    })
    
    charge_record.insert()
    
    # Update the audit item with the charge record reference
    frappe.db.set_value("Stock Take Audit Item", item_row_name, {
        "staff_charge_record": charge_record.name,
        "charge_amount": charge_amount
    })
    
    return charge_record.name
