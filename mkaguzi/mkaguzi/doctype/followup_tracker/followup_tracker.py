# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, getdate

class FollowupTracker(Document):
	def autoname(self):
		"""Generate follow-up ID"""
		if not self.followup_id:
			# Get the audit finding to extract year and sequence
			if self.audit_finding:
				finding = frappe.get_doc("Audit Finding", self.audit_finding)
				year = finding.finding_date.strftime("%Y")
				sequence = frappe.db.count("Followup Tracker", {"audit_finding": self.audit_finding}) + 1
				self.followup_id = f"FU-{year}-{sequence:03d}"
			else:
				# Fallback if no finding linked
				year = now_datetime().strftime("%Y")
				sequence = frappe.db.count("Followup Tracker") + 1
				self.followup_id = f"FU-{year}-{sequence:04d}"

	def validate(self):
		"""Validate follow-up tracker data"""
		self.validate_dates()
		self.validate_finding_link()
		self.populate_finding_data()
		self.update_status_based_on_dates()
		self.update_timestamps()

	def validate_dates(self):
		"""Validate date relationships"""
		if self.scheduled_date and getdate(self.scheduled_date) < getdate():
			if self.followup_status not in ["Completed", "Cancelled"]:
				self.followup_status = "Overdue"

		if self.completed_date and self.scheduled_date:
			if getdate(self.completed_date) < getdate(self.scheduled_date):
				frappe.throw(_("Completion date cannot be before scheduled date"))

	def validate_finding_link(self):
		"""Validate audit finding link"""
		if not self.audit_finding:
			frappe.throw(_("Audit Finding is required"))

		if not frappe.db.exists("Audit Finding", self.audit_finding):
			frappe.throw(_("Invalid Audit Finding reference"))

	def populate_finding_data(self):
		"""Populate data from linked audit finding"""
		if self.audit_finding:
			finding = frappe.get_doc("Audit Finding", self.audit_finding)
			self.audit_engagement = finding.audit_engagement
			self.finding_title = finding.finding_title
			self.business_unit = finding.business_unit_affected

	def update_status_based_on_dates(self):
		"""Update status based on dates and completion"""
		if self.completed_date and not self.followup_status == "Completed":
			self.followup_status = "Completed"
		elif self.scheduled_date and getdate(self.scheduled_date) < getdate() and self.followup_status == "Scheduled":
			self.followup_status = "Overdue"

	def update_timestamps(self):
		"""Update audit trail timestamps"""
		if not self.created_on:
			self.created_on = now_datetime()
		if not self.created_by:
			self.created_by = frappe.session.user
		self.last_updated = now_datetime()

	def on_update(self):
		"""Actions after update"""
		self.update_finding_followup_status()
		self.send_notifications()

	def update_finding_followup_status(self):
		"""Update linked finding's follow-up status"""
		if self.audit_finding:
			finding = frappe.get_doc("Audit Finding", self.audit_finding)

			# Get all follow-ups for this finding
			followups = frappe.get_all("Followup Tracker",
				filters={"audit_finding": self.audit_finding},
				fields=["followup_status"]
			)

			# Determine overall follow-up status
			if all(fu["followup_status"] == "Completed" for fu in followups):
				finding.followup_status = "Completed"
			elif any(fu["followup_status"] in ["In Progress", "Overdue"] for fu in followups):
				finding.followup_status = "In Progress"
			else:
				finding.followup_status = "Scheduled"

			finding.save()

	def send_notifications(self):
		"""Send notifications for status changes"""
		if self.has_value_changed("followup_status"):
			self.notify_status_change()

	def notify_status_change(self):
		"""Notify relevant parties of status changes"""
		subject = f"Follow-up Status Update: {self.followup_title}"
		message = f"""
		The status of Follow-up {self.followup_id} has been updated to {self.followup_status}.

		Finding: {self.finding_title}
		Type: {self.followup_type}
		Responsible Person: {self.responsible_person}
		Scheduled Date: {self.scheduled_date}

		Please review the follow-up for any required actions.
		"""

		# Notify responsible person and audit manager
		recipients = [self.responsible_person]
		audit_managers = frappe.get_all("User",
			filters={"role_profile_name": "Audit Manager"},
			pluck="name")
		recipients.extend(audit_managers)

		frappe.sendmail(
			recipients=recipients,
			subject=subject,
			message=message
		)

@frappe.whitelist()
def get_overdue_followups():
	"""Get follow-ups that are overdue"""
	overdue_followups = frappe.get_all("Followup Tracker",
		filters={
			"scheduled_date": ["<", now_datetime().date()],
			"followup_status": ["in", ["Scheduled", "In Progress"]]
		},
		fields=["name", "followup_title", "responsible_person", "scheduled_date", "audit_finding"]
	)

	return overdue_followups

@frappe.whitelist()
def get_followup_effectiveness_report():
	"""Generate follow-up effectiveness report"""
	report_data = frappe.db.sql("""
		SELECT
			ft.followup_type,
			ft.effectiveness_assessment,
			COUNT(*) as count
		FROM `tabFollowup Tracker` ft
		WHERE ft.followup_status = 'Completed'
			AND ft.effectiveness_assessment IS NOT NULL
		GROUP BY ft.followup_type, ft.effectiveness_assessment
		ORDER BY ft.followup_type, ft.effectiveness_assessment
	""", as_dict=True)

	return report_data

@frappe.whitelist()
def schedule_followup_from_finding(finding_name, followup_type, scheduled_date, responsible_person):
	"""Create a follow-up tracker from an audit finding"""
	finding = frappe.get_doc("Audit Finding", finding_name)

	followup = frappe.get_doc({
		"doctype": "Followup Tracker",
		"audit_finding": finding_name,
		"followup_type": followup_type,
		"followup_title": f"Follow-up: {finding.finding_title}",
		"scheduled_date": scheduled_date,
		"responsible_person": responsible_person,
		"followup_description": f"Follow-up verification for finding: {finding.finding_title}",
		"followup_objectives": f"Verify implementation and effectiveness of corrective actions for {finding.finding_condition}",
		"methodology": "Document review, interviews, and testing as appropriate"
	})

	followup.insert()
	return followup.name