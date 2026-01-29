# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class ComplianceRequirement(Document):
	def autoname(self):
		if not self.requirement_id:
			# Generate requirement ID in format CR-####
			last_req = frappe.db.sql("""
				SELECT requirement_id FROM `tabCompliance Requirement`
				WHERE requirement_id LIKE 'CR-%'
				ORDER BY CAST(SUBSTRING(requirement_id, 4) AS UNSIGNED) DESC
				LIMIT 1
			""", as_dict=True)

			if last_req:
				last_num = int(last_req[0].requirement_id.split('-')[1])
				next_num = last_num + 1
			else:
				next_num = 1

			self.requirement_id = f"CR-{next_num:04d}"

	def validate(self):
		self.validate_due_date_calculation()
		self.validate_penalty_amounts()

	def validate_due_date_calculation(self):
		"""Validate due date calculation settings"""
		if self.due_date_calculation == "Fixed Date" and not self.fixed_due_day:
			frappe.throw(_("Fixed Due Day is required when Due Date Calculation is 'Fixed Date'"))

		if self.due_date_calculation == "X Days After Period End" and not self.due_days_after_period:
			frappe.throw(_("Due Days After Period is required when Due Date Calculation is 'X Days After Period End'"))

	def validate_penalty_amounts(self):
		"""Validate penalty amount ranges"""
		if self.penalties_for_non_compliance:
			for penalty in self.penalties_for_non_compliance:
				if penalty.penalty_type == "Fine" and not penalty.penalty_amount_range:
					frappe.msgprint(_("Consider specifying penalty amount range for fine penalties"))

@frappe.whitelist()
def get_compliance_requirements_by_category(category=None, regulatory_body=None):
	"""Get compliance requirements filtered by category and/or regulatory body"""
	filters = {"is_active": 1}

	if category:
		filters["compliance_category"] = category
	if regulatory_body:
		filters["regulatory_body"] = regulatory_body

	requirements = frappe.get_all("Compliance Requirement",
		filters=filters,
		fields=["name", "requirement_id", "requirement_name", "regulatory_body",
				"compliance_category", "frequency", "responsible_person", "responsible_department"],
		order_by="regulatory_body, compliance_category"
	)

	return requirements

@frappe.whitelist()
def get_upcoming_due_dates(days_ahead=30):
	"""Get compliance requirements with due dates in the next X days"""
	from frappe.utils import add_days, getdate, nowdate

	today = getdate(nowdate())
	future_date = add_days(today, days_ahead)

	# This would typically involve calculating due dates based on the requirement's schedule
	# For now, return active requirements (actual due date calculation would be more complex)
	requirements = frappe.get_all("Compliance Requirement",
		filters={"is_active": 1},
		fields=["name", "requirement_id", "requirement_name", "frequency",
				"due_date_calculation", "fixed_due_day", "due_days_after_period"]
	)

	return requirements

@frappe.whitelist()
def create_standard_kenya_requirements():
	"""Create standard Kenya compliance requirements"""
	standard_requirements = [
		{
			"requirement_name": "VAT Returns",
			"regulatory_body": "KRA",
			"regulation_reference": "Value Added Tax Act CAP 473",
			"compliance_category": "Tax",
			"description": "Monthly VAT returns filing",
			"frequency": "Monthly",
			"due_date_calculation": "Fixed Date",
			"fixed_due_day": 20,
			"responsible_department": "Finance"
		},
		{
			"requirement_name": "PAYE Returns",
			"regulatory_body": "KRA",
			"regulation_reference": "Income Tax Act CAP 470",
			"compliance_category": "Tax",
			"description": "Monthly Pay As You Earn returns",
			"frequency": "Monthly",
			"due_date_calculation": "Fixed Date",
			"fixed_due_day": 9,
			"responsible_department": "Finance"
		},
		{
			"requirement_name": "Withholding Tax Returns",
			"regulatory_body": "KRA",
			"regulation_reference": "Income Tax Act CAP 470",
			"compliance_category": "Tax",
			"description": "Monthly withholding tax returns",
			"frequency": "Monthly",
			"due_date_calculation": "Fixed Date",
			"fixed_due_day": 20,
			"responsible_department": "Finance"
		},
		{
			"requirement_name": "NSSF Returns",
			"regulatory_body": "NSSF",
			"regulation_reference": "NSSF Act CAP 258",
			"compliance_category": "Social Security",
			"description": "Monthly NSSF contributions returns",
			"frequency": "Monthly",
			"due_date_calculation": "Fixed Date",
			"fixed_due_day": 15,
			"responsible_department": "HR"
		},
		{
			"requirement_name": "NHIF Returns",
			"regulatory_body": "NHIF",
			"regulation_reference": "NHIF Act CAP 256",
			"compliance_category": "Social Security",
			"description": "Monthly NHIF contributions returns",
			"frequency": "Monthly",
			"due_date_calculation": "Fixed Date",
			"fixed_due_day": 9,
			"responsible_department": "HR"
		},
		{
			"requirement_name": "Annual Income Tax Returns",
			"regulatory_body": "KRA",
			"regulation_reference": "Income Tax Act CAP 470",
			"compliance_category": "Tax",
			"description": "Annual corporate income tax returns",
			"frequency": "Annual",
			"due_date_calculation": "X Days After Period End",
			"due_days_after_period": 180,  # 6 months after year-end
			"responsible_department": "Finance"
		},
		{
			"requirement_name": "County Business Permits",
			"regulatory_body": "County Government",
			"compliance_category": "Licensing",
			"description": "Annual county business permit renewal",
			"frequency": "Annual",
			"due_date_calculation": "Fixed Date",
			"fixed_due_day": 31,  # December 31
			"responsible_department": "Administration"
		},
		{
			"requirement_name": "Fire Certificate",
			"regulatory_body": "County Government",
			"compliance_category": "Health & Safety",
			"description": "Annual fire safety certificate",
			"frequency": "Annual",
			"due_date_calculation": "Fixed Date",
			"fixed_due_day": 31,
			"responsible_department": "Administration"
		},
		{
			"requirement_name": "NEMA Environmental Audit",
			"regulatory_body": "NEMA",
			"regulation_reference": "Environmental Management and Co-ordination Act CAP 387",
			"compliance_category": "Environmental",
			"description": "Annual environmental audit report",
			"frequency": "Annual",
			"due_date_calculation": "X Days After Period End",
			"due_days_after_period": 180,
			"responsible_department": "Operations"
		},
		{
			"requirement_name": "Financial Statements Filing",
			"regulatory_body": "KRA",
			"compliance_category": "Tax",
			"description": "Annual financial statements filing with KRA",
			"frequency": "Annual",
			"due_date_calculation": "X Days After Period End",
			"due_days_after_period": 180,
			"responsible_department": "Finance"
		}
	]

	created_requirements = []
	for req_data in standard_requirements:
		if not frappe.db.exists("Compliance Requirement", {"requirement_name": req_data["requirement_name"]}):
			req = frappe.new_doc("Compliance Requirement")
			req.update(req_data)
			req.save()
			created_requirements.append(req.name)

	return created_requirements