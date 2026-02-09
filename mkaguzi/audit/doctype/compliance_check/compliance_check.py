# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today, add_days, date_diff


class ComplianceCheck(Document):
	def validate(self):
		"""Validate the compliance check"""
		self.validate_compliance_requirement()
		self.validate_dates()
		self.validate_status_severity()
		self.set_check_date()
		self.auto_populate_reminder()

	def validate_compliance_requirement(self):
		"""Validate that the compliance requirement exists"""
		if self.compliance_requirement:
			if not frappe.db.exists("Compliance Requirement", self.compliance_requirement):
				frappe.throw(_("Compliance Requirement {0} does not exist").format(self.compliance_requirement))

	def validate_dates(self):
		"""Validate that due date is not in the past for new records"""
		if self.due_date and getdate(self.due_date) < getdate(today()) and not self.completed_date:
			# Allow due date in past if completed
			if self.status not in ["Compliant", "Partially Compliant"]:
				frappe.msgprint(_("Warning: Due date is in the past"), alert=True, indicator="orange")

		if self.completed_date and self.due_date:
			if getdate(self.completed_date) > getdate(self.due_date):
				frappe.msgprint(_("Warning: Completion date is after due date"), alert=True, indicator="orange")

	def validate_status_severity(self):
		"""Validate status and severity combinations"""
		if self.status == "Non-Compliant" and self.severity == "Low":
			frappe.msgprint(_("Warning: Non-Compliant status typically requires High or Medium severity"),
				alert=True, indicator="orange")

		if self.status in ["Compliant", "Not Applicable"] and not self.findings and not self.gap_description:
			# Clear severity for compliant/not applicable
			self.severity = "Low"

	def set_check_date(self):
		"""Set check date if not set"""
		if not self.check_date:
			self.check_date = today()

	def auto_populate_reminder(self):
		"""Auto-populate remediation details based on status"""
		if self.status in ["Non-Compliant", "Partially Compliant"]:
			if not self.remediation_plan:
				# Set default remediation plan
				self.remediation_plan = "Develop and implement corrective actions to address compliance gaps."

			if not self.remediation_owner:
				# Default to current user
				self.remediation_owner = frappe.session.user

			if not self.remediation_due_date and self.due_date:
				# Set remediation due date to 30 days after check date
				self.remediation_due_date = add_days(self.check_date, 30)

	def on_submit(self):
		"""Actions when compliance check is submitted"""
		self.update_compliance_status()
		self.create_notifications()

	def on_cancel(self):
		"""Actions when compliance check is cancelled"""
		pass

	def update_compliance_status(self):
		"""Update compliance requirement status if needed"""
		pass

	def create_notifications(self):
		"""Create notifications based on status"""
		if self.status in ["Non-Compliant", "Partially Compliant"]:
			if self.remediation_owner:
				# Create notification for remediation owner
				pass


@frappe.whitelist()
def get_compliance_requirement_details(requirement_name):
	"""Get compliance requirement details"""
	frappe.has_permission("Compliance Requirement", "read", throw=True)

	requirement = frappe.get_doc("Compliance Requirement", requirement_name)

	return {
		"description": requirement.description,
		"control_reference": requirement.control_reference,
		"compliance_framework": requirement.compliance_framework,
		"compliance_frequency": getattr(requirement, "compliance_frequency", None)
	}


@frappe.whitelist()
def create_compliance_check(compliance_requirement, agent_config, due_date=None):
	"""Create a new compliance check"""
	frappe.has_permission("Compliance Check", "create", throw=True)

	# Check if compliance requirement exists
	if not frappe.db.exists("Compliance Requirement", compliance_requirement):
		frappe.throw(_("Compliance Requirement {0} does not exist").format(compliance_requirement))

	# Set default due date if not provided
	if not due_date:
		due_date = add_days(today(), 30)

	# Create Compliance Check
	check = frappe.get_doc({
		"doctype": "Compliance Check",
		"compliance_requirement": compliance_requirement,
		"verified_by": agent_config,
		"check_date": today(),
		"due_date": due_date,
		"status": "Not Applicable",
		"severity": "Medium"
	})

	check.insert()

	return {
		"success": True,
		"message": _("Compliance Check created successfully"),
		"check_name": check.name
	}


@frappe.whitelist()
def get_pending_compliance_checks():
	"""Get all pending compliance checks"""
	frappe.has_permission("Compliance Check", "read", throw=True)

	return frappe.get_all("Compliance Check",
		filters={
			"status": ["in", ["Non-Compliant", "Partially Compliant", "Not Applicable"]],
			"docstatus": ("!=", 2)
		},
		fields=["name", "compliance_requirement", "check_date", "due_date", "status", "severity"],
		order_by="due_date asc"
	)


@frappe.whitelist()
def get_overdue_compliance_checks():
	"""Get all overdue compliance checks"""
	frappe.has_permission("Compliance Check", "read", throw=True)

	return frappe.get_all("Compliance Check",
		filters={
			"due_date": ("<", today()),
			"status": ["in", ["Non-Compliant", "Partially Compliant", "Not Applicable"]],
			"docstatus": ("!=", 2)
		},
		fields=["name", "compliance_requirement", "check_date", "due_date", "status", "severity"],
		order_by="due_date asc"
	)


@frappe.whitelist()
def get_compliance_summary_by_framework():
	"""Get compliance summary grouped by framework"""
	frappe.has_permission("Compliance Check", "read", throw=True)

	checks = frappe.get_all("Compliance Check",
		filters={"docstatus": ("!=", 2)},
		fields=["compliance_framework", "status", "severity"]
	)

	summary = {}
	for check in checks:
		framework = check.compliance_framework or "Unassigned"
		if framework not in summary:
			summary[framework] = {
				"framework": framework,
				"total_checks": 0,
				"compliant": 0,
				"non_compliant": 0,
				"partially_compliant": 0,
				"not_applicable": 0,
				"high_severity": 0,
				"medium_severity": 0,
				"low_severity": 0
			}

		summary[framework]["total_checks"] += 1

		if check.status == "Compliant":
			summary[framework]["compliant"] += 1
		elif check.status == "Non-Compliant":
			summary[framework]["non_compliant"] += 1
		elif check.status == "Partially Compliant":
			summary[framework]["partially_compliant"] += 1
		elif check.status == "Not Applicable":
			summary[framework]["not_applicable"] += 1

		if check.severity == "High":
			summary[framework]["high_severity"] += 1
		elif check.severity == "Medium":
			summary[framework]["medium_severity"] += 1
		elif check.severity == "Low":
			summary[framework]["low_severity"] += 1

	return list(summary.values())


@frappe.whitelist()
def update_compliance_status(check_name, status, findings=None, evidence=None, severity=None):
	"""Update compliance check status"""
	frappe.has_permission("Compliance Check", "write", throw=True)

	doc = frappe.get_doc("Compliance Check", check_name)

	# Validate status
	if status not in ["Compliant", "Non-Compliant", "Partially Compliant", "Not Applicable"]:
		frappe.throw(_("Invalid status"))

	doc.status = status

	if findings:
		doc.findings = findings
	if evidence:
		doc.evidence = evidence
	if severity:
		doc.severity = severity

	# Set completed date if status is Compliant or Partially Compliant
	if status in ["Compliant", "Partially Compliant"] and not doc.completed_date:
		doc.completed_date = today()

	doc.save()

	return {
		"success": True,
		"message": _("Compliance status updated successfully")
	}


@frappe.whitelist()
def schedule_compliance_checks(requirement_names, agent_config, due_days=30):
	"""Schedule multiple compliance checks"""
	frappe.has_permission("Compliance Check", "create", throw=True)

	results = []
	due_date = add_days(today(), due_days)

	for requirement in requirement_names:
		try:
			result = create_compliance_check(requirement, agent_config, due_date)
			results.append({
				"requirement": requirement,
				"success": result.get("success", False),
				"message": result.get("message", ""),
				"check_name": result.get("check_name", "")
			})
		except Exception as e:
			results.append({
				"requirement": requirement,
				"success": False,
				"message": str(e),
				"check_name": ""
			})

	return results
