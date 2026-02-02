# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, get_datetime

class AuditProgram(Document):
	def autoname(self):
		if not self.program_id:
			# Generate program ID in format AP-####
			last_program = frappe.db.sql("""
				SELECT program_id FROM `tabAudit Program`
				WHERE program_id LIKE 'AP-%'
				ORDER BY CAST(SUBSTRING_INDEX(program_id, '-', -1) AS UNSIGNED) DESC
				LIMIT 1
			""", as_dict=True)

			if last_program:
				last_num = int(last_program[0].program_id.split('-')[-1])
				next_num = last_num + 1
			else:
				next_num = 1

			self.program_id = f"AP-{next_num:04d}"

	def validate(self):
		self.validate_template_logic()
		self.calculate_completion_summary()
		self.set_audit_fields()
		self.validate_procedures()

	def validate_template_logic(self):
		"""Validate template vs specific engagement logic"""
		if self.is_template and self.engagement_reference:
			frappe.throw(_("Template programs cannot have an engagement reference"))

		if not self.is_template and not self.engagement_reference:
			frappe.throw(_("Non-template programs must have an engagement reference"))

	def validate_procedures(self):
		"""Validate procedures have required fields"""
		if self.program_procedures:
			for i, procedure in enumerate(self.program_procedures):
				if not procedure.procedure_description:
					frappe.throw(_("Row {0}: Procedure description is required").format(i+1))
				if not procedure.procedure_type:
					frappe.throw(_("Row {0}: Procedure type is required").format(i+1))

	def calculate_completion_summary(self):
		"""Calculate completion statistics with enhanced logic"""
		if not self.program_procedures:
			self.total_procedures = 0
			self.completed_procedures = 0
			self.not_applicable_procedures = 0
			self.completion_percent = 0
			return

		total_procedures = len(self.program_procedures)
		completed_procedures = sum(1 for p in self.program_procedures
								 if p.status == "Completed")
		not_applicable_procedures = sum(1 for p in self.program_procedures
									  if p.status == "Not Applicable")

		# Calculate effective total (excluding not applicable)
		effective_total = total_procedures - not_applicable_procedures

		self.total_procedures = total_procedures
		self.completed_procedures = completed_procedures
		self.not_applicable_procedures = not_applicable_procedures

		if effective_total > 0:
			self.completion_percent = round((completed_procedures / effective_total) * 100)
		else:
			self.completion_percent = 0

	def set_audit_fields(self):
		"""Set audit trail fields"""
		if not self.created_by:
			self.created_by = frappe.session.user
		if not self.created_on:
			self.created_on = get_datetime()

	def on_update(self):
		"""Update related engagement status"""
		if self.engagement_reference and not self.is_template:
			self.update_engagement_status()

	def update_engagement_status(self):
		"""Update the related engagement's program status"""
		engagement = frappe.get_doc("Audit Engagement", self.engagement_reference)

		if self.completion_percent == 100:
			engagement.program_status = "Completed"
		elif self.completion_percent > 0:
			engagement.program_status = "In Progress"
		else:
			engagement.program_status = "Not Started"

		engagement.save()

@frappe.whitelist()
def create_program_from_template(template_name, engagement_name):
	"""Create a program from a template for a specific engagement"""
	template = frappe.get_doc("Audit Program", template_name)

	if not template.is_template:
		frappe.throw(_("Selected program is not a template"))

	engagement = frappe.get_doc("Audit Engagement", engagement_name)

	# Create new program
	program = frappe.new_doc("Audit Program")
	program.program_name = f"{template.program_name} - {engagement.engagement_title}"
	program.audit_type = template.audit_type
	program.is_template = 0
	program.engagement_reference = engagement_name
	program.program_objectives = template.program_objectives

	# Copy procedures
	if template.program_procedures:
		for procedure in template.program_procedures:
			program.append("program_procedures", {
				"procedure_no": procedure.procedure_no,
				"procedure_section": procedure.procedure_section,
				"procedure_description": procedure.procedure_description,
				"procedure_type": procedure.procedure_type,
				"control_objective": procedure.control_objective,
				"assertion": procedure.assertion,
				"bc_data_source": procedure.bc_data_source,
				"sample_size": procedure.sample_size,
				"sampling_method": procedure.sampling_method,
				"budgeted_hours": procedure.budgeted_hours,
				"status": "Not Started"
			})

	# Copy risk areas
	if template.risk_areas:
		for risk in template.risk_areas:
			program.append("risk_areas", {
				"risk_description": risk.risk_description,
				"risk_rating": risk.risk_rating,
				"procedures_addressing_risk": risk.procedures_addressing_risk
			})

	program.save()

	# Update engagement reference
	engagement.audit_program_reference = program.name
	engagement.program_status = "Created"
	engagement.save()

	return program

def get_program_progress_details(self):
		"""Get detailed progress information"""
		if not self.program_procedures:
			return {
				"total": 0,
				"completed": 0,
				"in_progress": 0,
				"not_started": 0,
				"not_applicable": 0,
				"completion_rate": 0
			}

		status_counts = {
			"Not Started": 0,
			"In Progress": 0,
			"Completed": 0,
			"Not Applicable": 0
		}

		for procedure in self.program_procedures:
			status_counts[procedure.status] = status_counts.get(procedure.status, 0) + 1

		effective_total = len(self.program_procedures) - status_counts.get("Not Applicable", 0)
		completion_rate = (status_counts.get("Completed", 0) / effective_total * 100) if effective_total > 0 else 0

		return {
			"total": len(self.program_procedures),
			"completed": status_counts.get("Completed", 0),
			"in_progress": status_counts.get("In Progress", 0),
			"not_started": status_counts.get("Not Started", 0),
			"not_applicable": status_counts.get("Not Applicable", 0),
			"completion_rate": round(completion_rate, 1)
		}@frappe.whitelist()
def get_program_templates(audit_type=None):
	"""Get available program templates"""
	filters = {"is_template": 1}
	if audit_type:
		filters["audit_type"] = audit_type

	templates = frappe.get_all("Audit Program",
		filters=filters,
		fields=["name", "program_name", "audit_type", "description"]
	)

	return templates

@frappe.whitelist()
def create_default_program_templates():
	"""Create default audit program templates"""
	templates = [
		{
			"name": "Inventory Audit Program",
			"type": "Inventory",
			"objectives": "To assess the adequacy of inventory controls, valuation accuracy, and physical inventory processes."
		},
		{
			"name": "Cash & Bank Audit Program",
			"type": "Cash",
			"objectives": "To verify cash balances, bank reconciliations, and cash handling procedures."
		},
		{
			"name": "Sales & Receivables Audit Program",
			"type": "Sales",
			"objectives": "To evaluate sales processes, revenue recognition, and accounts receivable management."
		},
		{
			"name": "Purchases & Payables Audit Program",
			"type": "Procurement",
			"objectives": "To assess procurement processes, vendor management, and accounts payable controls."
		},
		{
			"name": "Payroll Audit Program",
			"type": "Operational",
			"objectives": "To verify payroll calculations, employee data accuracy, and compliance with labor regulations."
		},
		{
			"name": "Fixed Assets Audit Program",
			"type": "Financial",
			"objectives": "To validate fixed asset records, depreciation calculations, and asset disposal procedures."
		},
		{
			"name": "Revenue Audit Program",
			"type": "Financial",
			"objectives": "To assess revenue recognition policies and procedures for accuracy and completeness."
		},
		{
			"name": "Procurement Audit Program",
			"type": "Procurement",
			"objectives": "To evaluate procurement processes, contract management, and vendor selection procedures."
		},
		{
			"name": "IT General Controls Audit Program",
			"type": "IT",
			"objectives": "To assess IT governance, access controls, and system security measures."
		},
		{
			"name": "Compliance Audit Program (Kenya Regulations)",
			"type": "Compliance",
			"objectives": "To ensure compliance with Kenyan laws, regulations, and statutory requirements."
		}
	]

	for template_data in templates:
		# Check if template already exists
		existing = frappe.db.exists("Audit Program", {
			"program_name": template_data["name"],
			"is_template": 1
		})

		if not existing:
			template = frappe.new_doc("Audit Program")
			template.program_name = template_data["name"]
			template.audit_type = template_data["type"]
			template.is_template = 1
			template.program_objectives = template_data["objectives"]

			# Add sample procedures based on template type
			procedures = get_default_procedures(template_data["type"])
			for proc in procedures:
				template.append("program_procedures", proc)

			template.save()
			frappe.msgprint(_("Created template: {0}").format(template.program_name))

	return {"message": "Default templates created successfully"}

def get_default_procedures(audit_type):
	"""Get default procedures for different audit types"""
	procedures = {
		"Inventory": [
			{
				"procedure_no": "A.1",
				"procedure_section": "Understanding",
				"procedure_description": "Obtain understanding of inventory management system and processes",
				"procedure_type": "Inquiry",
				"assertion": "Existence"
			},
			{
				"procedure_no": "A.2",
				"procedure_section": "Testing",
				"procedure_description": "Test inventory count procedures and cut-off",
				"procedure_type": "Observation",
				"assertion": "Completeness"
			},
			{
				"procedure_no": "B.1",
				"procedure_section": "Testing",
				"procedure_description": "Verify inventory valuation and costing methods",
				"procedure_type": "Re-performance",
				"assertion": "Valuation"
			}
		],
		"Cash": [
			{
				"procedure_no": "A.1",
				"procedure_section": "Understanding",
				"procedure_description": "Understand cash handling and banking procedures",
				"procedure_type": "Inquiry",
				"assertion": "Existence"
			},
			{
				"procedure_no": "A.2",
				"procedure_section": "Testing",
				"procedure_description": "Test bank reconciliations for selected periods",
				"procedure_type": "Re-performance",
				"assertion": "Accuracy"
			}
		],
		"Sales": [
			{
				"procedure_no": "A.1",
				"procedure_section": "Understanding",
				"procedure_description": "Understand sales process and revenue recognition",
				"procedure_type": "Inquiry",
				"assertion": "Occurrence"
			},
			{
				"procedure_no": "A.2",
				"procedure_section": "Testing",
				"procedure_description": "Test sales transactions for proper authorization",
				"procedure_type": "Inspection",
				"assertion": "Rights"
			}
		],
		"Procurement": [
			{
				"procedure_no": "A.1",
				"procedure_section": "Understanding",
				"procedure_description": "Understand procurement and vendor management processes",
				"procedure_type": "Inquiry",
				"assertion": "Existence"
			},
			{
				"procedure_no": "A.2",
				"procedure_section": "Testing",
				"procedure_description": "Test purchase orders and receiving procedures",
				"procedure_type": "Inspection",
				"assertion": "Completeness"
			}
		],
		"IT": [
			{
				"procedure_no": "A.1",
				"procedure_section": "Understanding",
				"procedure_description": "Understand IT governance and access controls",
				"procedure_type": "Inquiry",
				"assertion": "Existence"
			},
			{
				"procedure_no": "A.2",
				"procedure_section": "Testing",
				"procedure_description": "Test user access rights and segregation of duties",
				"procedure_type": "Observation",
				"assertion": "Rights"
			}
		],
		"Compliance": [
			{
				"procedure_no": "A.1",
				"procedure_section": "Understanding",
				"procedure_description": "Understand regulatory compliance requirements",
				"procedure_type": "Inquiry",
				"assertion": "Existence"
			},
			{
				"procedure_no": "A.2",
				"procedure_section": "Testing",
				"procedure_description": "Test compliance with specific regulations",
				"procedure_type": "Inspection",
				"assertion": "Completeness"
			}
		]
	}

	return procedures.get(audit_type, [])

@frappe.whitelist()
def get_program_progress(program_id):
	"""Get detailed progress information for a program"""
	program = frappe.get_doc("Audit Program", program_id)
	return program.get_program_progress_details()

@frappe.whitelist()
def duplicate_program(source_program_id, new_name=None):
	"""Duplicate an audit program"""
	source_program = frappe.get_doc("Audit Program", source_program_id)

	new_program = frappe.new_doc("Audit Program")
	new_program.program_name = new_name or f"{source_program.program_name} (Copy)"
	new_program.audit_type = source_program.audit_type
	new_program.is_template = False
	new_program.program_objectives = source_program.program_objectives

	# Copy procedures
	if source_program.program_procedures:
		for procedure in source_program.program_procedures:
			new_program.append("program_procedures", {
				"procedure_no": procedure.procedure_no,
				"procedure_section": procedure.procedure_section,
				"procedure_description": procedure.procedure_description,
				"procedure_type": procedure.procedure_type,
				"control_objective": procedure.control_objective,
				"assertion": procedure.assertion,
				"bc_data_source": procedure.bc_data_source,
				"sample_size": procedure.sample_size,
				"sampling_method": procedure.sampling_method,
				"budgeted_hours": procedure.budgeted_hours,
				"status": "Not Started"
			})

	# Copy risk areas
	if source_program.risk_areas:
		for risk in source_program.risk_areas:
			new_program.append("risk_areas", {
				"risk_description": risk.risk_description,
				"risk_rating": risk.risk_rating,
				"procedures_addressing_risk": risk.procedures_addressing_risk
			})

	new_program.save()
	return new_program