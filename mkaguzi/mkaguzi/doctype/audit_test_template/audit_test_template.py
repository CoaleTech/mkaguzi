# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, now_datetime
import json

class AuditTestTemplate(Document):
    def validate(self):
        """Validate the audit test template"""
        self.validate_test_procedures()
        self.update_change_log()

    def validate_test_procedures(self):
        """Validate that test procedures are properly defined"""
        if not self.test_procedures:
            frappe.throw(_("At least one test procedure must be defined"))

        for procedure in self.test_procedures:
            if not procedure.procedure_name or not procedure.procedure_description:
                frappe.throw(_("All test procedures must have a name and description"))

    def update_change_log(self):
        """Update the change log with modification details"""
        if not self.change_log:
            self.change_log = ""

        log_entry = f"{now()}: Updated by {frappe.session.user}\n"
        self.change_log += log_entry

    def on_update(self):
        """Called when document is updated"""
        # Set created_by if not set
        if not self.created_by:
            self.created_by = frappe.session.user

    def get_template_summary(self):
        """Get a summary of the test template"""
        return {
            "name": self.template_name,
            "type": self.template_type,
            "category": self.audit_category,
            "active": self.is_active,
            "procedures_count": len(self.test_procedures) if self.test_procedures else 0,
            "frequency": self.test_frequency,
            "automated": self.automated_testing,
            "approval_required": self.approval_required
        }

    def create_audit_program(self, audit_trail=None):
        """Create an audit program from this template"""
        from mkaguzi.mkaguzi.integration.templates import AuditTemplateManager

        manager = AuditTemplateManager()
        return manager.create_audit_program_from_template(self.name, audit_trail)

@frappe.whitelist()
def create_template_from_category(audit_category, template_type="Full Audit Program"):
    """Create a new template based on audit category"""
    if not frappe.has_permission("Audit Test Template", "create"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    # Get base template configuration for the category
    template_config = get_template_config(audit_category, template_type)

    # Create new template
    template = frappe.get_doc({
        "doctype": "Audit Test Template",
        "template_name": f"{audit_category} {template_type} Template",
        "template_type": template_type,
        "audit_category": audit_category,
        "description": template_config.get("description", ""),
        "test_objectives": template_config.get("objectives", ""),
        "expected_results": template_config.get("expected_results", ""),
        "risk_assessment": template_config.get("risk_assessment", ""),
        "control_objectives": template_config.get("control_objectives", ""),
        "sample_size_calculation": template_config.get("sampling", "")
    })

    # Add test procedures
    for procedure in template_config.get("procedures", []):
        template.append("test_procedures", {
            "procedure_name": procedure.get("name", ""),
            "procedure_description": procedure.get("description", ""),
            "expected_result": procedure.get("expected_result", ""),
            "risk_weight": procedure.get("risk_weight", 1)
        })

    template.insert()
    return template.name

def get_template_config(audit_category, template_type):
    """Get template configuration based on category and type"""
    configs = {
        "Financial": {
            "description": "Comprehensive financial audit template covering accounting controls, transaction processing, and financial reporting",
            "objectives": "To ensure accuracy, completeness, and compliance of financial transactions and reporting",
            "expected_results": "All financial transactions properly authorized, recorded, and reported",
            "risk_assessment": "High risk areas include revenue recognition, expense classification, and financial statement preparation",
            "control_objectives": "Ensure proper segregation of duties, authorization controls, and reconciliation procedures",
            "sampling": "Sample size based on transaction volume and risk assessment",
            "procedures": [
                {
                    "name": "Transaction Authorization Testing",
                    "description": "Verify all transactions have proper authorization",
                    "expected_result": "100% of sampled transactions properly authorized",
                    "risk_weight": 3
                },
                {
                    "name": "Journal Entry Review",
                    "description": "Review manual journal entries for appropriateness",
                    "expected_result": "All manual entries supported by documentation",
                    "risk_weight": 4
                },
                {
                    "name": "Account Reconciliation Testing",
                    "description": "Test reconciliation procedures for key accounts",
                    "expected_result": "All reconciliations completed timely and accurately",
                    "risk_weight": 2
                }
            ]
        },
        "HR": {
            "description": "HR audit template covering employee management, payroll processing, and compliance",
            "objectives": "To ensure compliance with labor laws, accuracy of payroll, and proper employee management",
            "expected_results": "All HR processes compliant and accurately processed",
            "risk_assessment": "High risk areas include payroll calculations, employee data privacy, and regulatory compliance",
            "control_objectives": "Ensure proper access controls, data validation, and approval processes",
            "sampling": "Sample size based on employee count and process complexity",
            "procedures": [
                {
                    "name": "Payroll Calculation Testing",
                    "description": "Verify payroll calculations for accuracy",
                    "expected_result": "All payroll calculations accurate within tolerance",
                    "risk_weight": 4
                },
                {
                    "name": "Employee Data Access Review",
                    "description": "Review access to sensitive employee information",
                    "expected_result": "Access limited to authorized personnel only",
                    "risk_weight": 3
                },
                {
                    "name": "Compliance Documentation Check",
                    "description": "Verify compliance with labor regulations",
                    "expected_result": "All required documentation maintained",
                    "risk_weight": 3
                }
            ]
        },
        "Inventory": {
            "description": "Inventory audit template covering stock management, valuation, and physical counts",
            "objectives": "To ensure accurate inventory records, proper valuation, and physical security",
            "expected_results": "Inventory records accurate and inventory properly secured",
            "risk_assessment": "High risk areas include inventory valuation, obsolescence, and physical security",
            "control_objectives": "Ensure proper counting procedures, access controls, and valuation methods",
            "sampling": "Sample size based on inventory value and number of items",
            "procedures": [
                {
                    "name": "Physical Inventory Count",
                    "description": "Observe and test physical inventory counting procedures",
                    "expected_result": "Counting procedures accurate and consistent",
                    "risk_weight": 3
                },
                {
                    "name": "Inventory Valuation Testing",
                    "description": "Verify inventory valuation methods and calculations",
                    "expected_result": "Inventory properly valued at lower of cost or market",
                    "risk_weight": 4
                },
                {
                    "name": "Stock Movement Controls",
                    "description": "Test controls over stock receipts and issues",
                    "expected_result": "All stock movements properly authorized and recorded",
                    "risk_weight": 2
                }
            ]
        },
        "Procurement": {
            "description": "Procurement audit template covering purchasing processes, vendor management, and contract compliance",
            "objectives": "To ensure competitive procurement, proper vendor selection, and contract compliance",
            "expected_results": "All procurement activities competitive and compliant",
            "risk_assessment": "High risk areas include vendor selection, contract terms, and payment processing",
            "control_objectives": "Ensure competitive bidding, proper approvals, and vendor evaluation",
            "sampling": "Sample size based on procurement volume and value",
            "procedures": [
                {
                    "name": "Purchase Order Approval Testing",
                    "description": "Verify purchase orders have proper approvals",
                    "expected_result": "All purchase orders properly approved",
                    "risk_weight": 3
                },
                {
                    "name": "Vendor Selection Review",
                    "description": "Review vendor selection and evaluation processes",
                    "expected_result": "Vendors selected through competitive process",
                    "risk_weight": 4
                },
                {
                    "name": "Contract Compliance Check",
                    "description": "Verify compliance with contract terms",
                    "expected_result": "All contracts monitored and compliant",
                    "risk_weight": 3
                }
            ]
        },
        "Access": {
            "description": "Access control audit template covering user permissions, authentication, and authorization",
            "objectives": "To ensure proper access controls, authentication, and authorization mechanisms",
            "expected_results": "Access controls effective and user permissions appropriate",
            "risk_assessment": "High risk areas include privileged access, password policies, and access reviews",
            "control_objectives": "Ensure least privilege principle, regular access reviews, and strong authentication",
            "sampling": "Sample size based on user count and system complexity",
            "procedures": [
                {
                    "name": "User Access Review",
                    "description": "Review user access rights for appropriateness",
                    "expected_result": "All users have appropriate access levels",
                    "risk_weight": 4
                },
                {
                    "name": "Password Policy Testing",
                    "description": "Test password policies and complexity requirements",
                    "expected_result": "Password policies enforced and effective",
                    "risk_weight": 3
                },
                {
                    "name": "Access Change Controls",
                    "description": "Review controls over access right changes",
                    "expected_result": "Access changes properly authorized and logged",
                    "risk_weight": 3
                }
            ]
        }
    }

    return configs.get(audit_category, {
        "description": f"General audit template for {audit_category}",
        "objectives": f"To ensure proper controls and processes in {audit_category}",
        "procedures": []
    })

@frappe.whitelist()
def get_template_library():
    """Get available templates organized by category"""
    if not frappe.has_permission("Audit Test Template", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    templates = frappe.db.sql("""
        SELECT template_name, template_type, audit_category, description,
               is_active, created_by, modified
        FROM `tabAudit Test Template`
        WHERE is_active = 1
        ORDER BY audit_category, template_type, template_name
    """, as_dict=True)

    # Organize by category
    library = {}
    for template in templates:
        category = template.audit_category
        if category not in library:
            library[category] = []
        library[category].append({
            "name": template.template_name,
            "type": template.template_type,
            "description": template.description,
            "created_by": template.created_by,
            "modified": template.modified
        })

    return library

@frappe.whitelist()
def duplicate_template(template_name, new_name):
    """Duplicate an existing template"""
    if not frappe.has_permission("Audit Test Template", "create"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    # Get original template
    original = frappe.get_doc("Audit Test Template", template_name)

    # Create duplicate
    duplicate = frappe.get_doc({
        "doctype": "Audit Test Template",
        "template_name": new_name,
        "template_type": original.template_type,
        "audit_category": original.audit_category,
        "description": original.description,
        "test_objectives": original.test_objectives,
        "expected_results": original.expected_results,
        "risk_assessment": original.risk_assessment,
        "control_objectives": original.control_objectives,
        "sample_size_calculation": original.sample_size_calculation,
        "test_frequency": original.test_frequency,
        "automated_testing": original.automated_testing,
        "approval_required": original.approval_required
    })

    # Copy test procedures
    if original.test_procedures:
        for procedure in original.test_procedures:
            duplicate.append("test_procedures", {
                "procedure_name": procedure.procedure_name,
                "procedure_description": procedure.procedure_description,
                "expected_result": procedure.expected_result,
                "risk_weight": procedure.risk_weight
            })

    duplicate.insert()
    return duplicate.name