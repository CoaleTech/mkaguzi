# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, date_diff, add_days

class ComplianceChecklist(Document):
	def autoname(self):
		if not self.checklist_id:
			# Generate checklist ID in format CC-YYYY-MM-####
			from frappe.utils import nowdate
			current_date = getdate(nowdate())
			year = current_date.year
			month = current_date.month

			last_checklist = frappe.db.sql("""
				SELECT checklist_id FROM `tabCompliance Checklist`
				WHERE checklist_id LIKE 'CC-{}-{:02d}-%'
				ORDER BY CAST(SUBSTRING_INDEX(checklist_id, '-', -1) AS UNSIGNED) DESC
				LIMIT 1
			""".format(year, month), as_dict=True)

			if last_checklist:
				last_num = int(last_checklist[0].checklist_id.split('-')[-1])
				next_num = last_num + 1
			else:
				next_num = 1

			self.checklist_id = f"CC-{year}-{month:02d}-{next_num:04d}"

	def validate(self):
		self.populate_checklist_items()
		self.calculate_summary()
		self.generate_alerts()
		self.set_prepared_by()

	def populate_checklist_items(self):
		"""Populate checklist items based on active compliance requirements"""
		if not self.checklist_items:
			# Get all active compliance requirements
			requirements = frappe.get_all("Compliance Requirement",
				filters={"is_active": 1},
				fields=["name", "requirement_name", "regulatory_body", "description",
						"frequency", "due_date_calculation", "fixed_due_day", "due_days_after_period"]
			)

			for req in requirements:
				# Calculate due date based on period
				due_date = self.calculate_due_date(req)

				item = {
					"requirement": req.name,
					"regulatory_body": req.regulatory_body,
					"description": req.requirement_name,
					"due_date": due_date,
					"status": "Not Started"
				}

				self.append("checklist_items", item)

	def calculate_due_date(self, requirement):
		"""Calculate due date for a requirement based on checklist period"""
		if requirement.due_date_calculation == "Fixed Date" and requirement.fixed_due_day:
			# For monthly checklists, use the fixed day of the period month
			if self.period_type == "Monthly" and self.period_month:
				# Parse period_month (assuming format like "2025-11")
				try:
					period_year, period_month_num = map(int, self.period_month.split('-'))
					# For monthly, due date is fixed_due_day of following month
					if period_month_num == 12:
						due_year = period_year + 1
						due_month = 1
					else:
						due_year = period_year
						due_month = period_month_num + 1

					return getdate(f"{due_year}-{due_month:02d}-{requirement.fixed_due_day:02d}")
				except:
					pass

		# Default fallback
		return None

	def calculate_summary(self):
		"""Calculate summary statistics"""
		if not self.checklist_items:
			return

		total = len(self.checklist_items)
		completed = sum(1 for item in self.checklist_items if item.status in ["Completed", "Filed"])
		overdue = sum(1 for item in self.checklist_items if item.status == "Overdue")

		self.total_requirements = total
		self.completed_requirements = completed
		self.overdue_requirements = overdue
		self.completion_percent = (completed / total * 100) if total > 0 else 0

	def generate_alerts(self):
		"""Generate alerts for overdue or due soon items"""
		if not self.checklist_items:
			return

		today = getdate(nowdate())
		self.alerts = []  # Clear existing alerts

		for item in self.checklist_items:
			if item.due_date:
				days_until_due = date_diff(item.due_date, today)

				if days_until_due < 0 and item.status not in ["Completed", "Filed"]:
					# Overdue
					alert = {
						"requirement": item.requirement,
						"alert_type": "Overdue",
						"alert_message": f"Requirement '{item.description}' is overdue by {abs(days_until_due)} days",
						"severity": "Critical"
					}
					self.append("alerts", alert)

				elif 0 <= days_until_due <= 7 and item.status == "Not Started":
					# Due soon
					alert = {
						"requirement": item.requirement,
						"alert_type": "Due Soon",
						"alert_message": f"Requirement '{item.description}' is due in {days_until_due} days",
						"severity": "High"
					}
					self.append("alerts", alert)

	def set_prepared_by(self):
		"""Set prepared_by if not set"""
		if not self.prepared_by:
			self.prepared_by = frappe.session.user

	def on_update(self):
		"""Update item statuses based on completion"""
		for item in self.checklist_items:
			if item.status in ["Completed", "Filed"] and not item.completion_date:
				item.completion_date = getdate(nowdate())
				if not item.completed_by:
					item.completed_by = frappe.session.user

@frappe.whitelist()
def create_monthly_checklist(period_month, fiscal_year=None):
	"""Create a monthly compliance checklist"""
	checklist = frappe.new_doc("Compliance Checklist")
	checklist.period_type = "Monthly"
	checklist.period_month = period_month
	if fiscal_year:
		checklist.fiscal_year = fiscal_year

	checklist.save()
	return checklist

@frappe.whitelist()
def get_checklist_summary(checklist_name):
	"""Get detailed summary for a checklist"""
	checklist = frappe.get_doc("Compliance Checklist", checklist_name)

	summary = {
		"checklist_id": checklist.checklist_id,
		"period_type": checklist.period_type,
		"total_requirements": checklist.total_requirements,
		"completed_requirements": checklist.completed_requirements,
		"overdue_requirements": checklist.overdue_requirements,
		"completion_percent": checklist.completion_percent,
		"alerts_count": len(checklist.alerts) if checklist.alerts else 0,
		"by_status": {},
		"by_regulatory_body": {}
	}

	# Count by status
	if checklist.checklist_items:
		for item in checklist.checklist_items:
			status = item.status or "Not Started"
			summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

			reg_body = item.regulatory_body or "Other"
			summary["by_regulatory_body"][reg_body] = summary["by_regulatory_body"].get(reg_body, 0) + 1

	return summary

@frappe.whitelist()
def update_item_status(checklist_name, item_name, status, notes=None):
	"""Update status of a checklist item"""
	checklist = frappe.get_doc("Compliance Checklist", checklist_name)

	for item in checklist.checklist_items:
		if item.name == item_name:
			item.status = status
			if notes:
				item.notes = notes
			break

	checklist.save()
	return checklist