# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, get_first_day, get_last_day
from datetime import datetime

class AnnualAuditPlan(Document):
	def validate(self):
		self.validate_plan_id()
		self.calculate_resource_utilization()
		self.validate_planned_audits()
		self.validate_approval_workflow()
		self.validate_plan_year()

	def validate_plan_id(self):
		"""Auto-generate plan ID if not provided"""
		if not self.plan_id:
			year = str(self.plan_year) if self.plan_year else str(getdate().year)
			period_code = {
				"Annual": "ANN",
				"Semi-Annual": "SEM",
				"Quarterly": "QTR"
			}.get(self.plan_period, "ANN")

			sequence = self.get_next_sequence(year)
			self.plan_id = f"AAP-{year}-{period_code}-{sequence:03d}"

	def get_next_sequence(self, year):
		"""Get next sequence number for plan ID"""
		existing = frappe.db.sql("""
			SELECT plan_id FROM `tabAnnual Audit Plan`
			WHERE plan_id LIKE %s
			ORDER BY plan_id DESC LIMIT 1
		""", f"AAP-{year}-%")

		if existing:
			last_id = existing[0][0]
			try:
				sequence = int(last_id.split('-')[-1])
				return sequence + 1
			except (ValueError, IndexError):
				pass
		return 1

	def validate_plan_year(self):
		"""Validate plan year is not in the past"""
		current_year = getdate().year
		if self.plan_year and self.plan_year < current_year:
			frappe.throw(_("Plan year cannot be in the past"))

	def calculate_resource_utilization(self):
		"""Calculate total available days and utilization percentage"""
		if self.resource_allocation:
			total_available = sum([resource.available_days for resource in self.resource_allocation if resource.available_days])
			self.total_available_days = total_available

		if self.planned_audits:
			total_planned = sum([audit.planned_days for audit in self.planned_audits if audit.planned_days])
			self.total_planned_days = total_planned

		if self.total_available_days and self.total_available_days > 0:
			self.utilization_percentage = (self.total_planned_days / self.total_available_days) * 100
		else:
			self.utilization_percentage = 0

		# Warning if utilization exceeds 100%
		if self.utilization_percentage > 100:
			frappe.msgprint(_("Warning: Planned audit days exceed available resource days by {0}%".format(
				round(self.utilization_percentage - 100, 1)
			)), indicator="orange")

	def validate_planned_audits(self):
		"""Validate planned audits table"""
		if self.planned_audits:
			# Check for duplicate audit universe entries
			universes = []
			for audit in self.planned_audits:
				if audit.audit_universe in universes:
					frappe.throw(_("Duplicate audit universe '{0}' in planned audits").format(audit.audit_universe))
				universes.append(audit.audit_universe)

			# Validate audit dates are within plan year
			plan_start = get_first_day(f"{self.plan_year}-01-01")
			plan_end = get_last_day(f"{self.plan_year}-12-31")

			for audit in self.planned_audits:
				if audit.planned_start_date and (audit.planned_start_date < plan_start or audit.planned_start_date > plan_end):
					frappe.throw(_("Planned start date for '{0}' is outside the plan year").format(audit.audit_universe))

				if audit.planned_end_date and (audit.planned_end_date < plan_start or audit.planned_end_date > plan_end):
					frappe.throw(_("Planned end date for '{0}' is outside the plan year").format(audit.audit_universe))

	def validate_approval_workflow(self):
		"""Validate approval workflow transitions"""
		if self.status in ["Approved", "Rejected"]:
			if not self.approved_by:
				frappe.throw(_("Approved By is required when status is {0}").format(self.status))
			if not self.approved_date:
				self.approved_date = getdate()
		elif self.status == "Submitted for Approval":
			if not self.prepared_by:
				frappe.throw(_("Prepared By is required before submitting for approval"))

	def on_submit(self):
		"""Create audit calendar entries when plan is approved"""
		if self.status == "Approved":
			self.create_audit_calendar_entries()

	def create_audit_calendar_entries(self):
		"""Create corresponding entries in Audit Calendar"""
		for audit in self.planned_audits:
			calendar_entry = frappe.get_doc({
				"doctype": "Audit Calendar",
				"annual_audit_plan": self.name,
				"audit_universe": audit.audit_universe,
				"planned_start_date": audit.planned_start_date,
				"planned_end_date": audit.planned_end_date,
				"audit_type": audit.audit_type,
				"lead_auditor": audit.lead_auditor,
				"estimated_days": audit.planned_days,
				"status": "Planned"
			})
			calendar_entry.insert()

@frappe.whitelist()
def get_plan_summary(year=None):
	"""Get audit plan summary for dashboard"""
	if not year:
		year = getdate().year

	data = frappe.db.sql("""
		SELECT
			status,
			COUNT(*) as count,
			SUM(total_planned_days) as total_days,
			AVG(utilization_percentage) as avg_utilization
		FROM `tabAnnual Audit Plan`
		WHERE plan_year = %s
		GROUP BY status
	""", year, as_dict=True)

	return data

@frappe.whitelist()
def get_resource_utilization(plan_id):
	"""Get detailed resource utilization for a plan"""
	plan = frappe.get_doc("Annual Audit Plan", plan_id)

	utilization_data = {
		"resources": [],
		"audits": []
	}

	# Get resource allocation details
	if plan.resource_allocation:
		for resource in plan.resource_allocation:
			utilization_data["resources"].append({
				"name": resource.auditor_name,
				"available_days": resource.available_days,
				"allocated_days": resource.allocated_days,
				"utilization": (resource.allocated_days / resource.available_days * 100) if resource.available_days > 0 else 0
			})

	# Get audit details
	if plan.planned_audits:
		for audit in plan.planned_audits:
			utilization_data["audits"].append({
				"universe": audit.audit_universe,
				"days": audit.planned_days,
				"type": audit.audit_type,
				"priority": audit.priority
			})

	return utilization_data