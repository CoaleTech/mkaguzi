# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, date_diff, add_days
from datetime import datetime

class AuditCalendar(Document):
	def validate(self):
		self.validate_calendar_id()
		self.validate_dates()
		self.check_resource_conflicts()
		self.update_progress()
		self.validate_status_transitions()

	def validate_calendar_id(self):
		"""Auto-generate calendar ID if not provided"""
		if not self.calendar_id:
			# Format: AC-{Year}-{AuditUniverse}-{Sequence}
			year = str(getdate().year)
			universe_code = self.audit_universe.replace('-', '').upper()[:3] if self.audit_universe else 'GEN'
			sequence = self.get_next_sequence(year)
			self.calendar_id = f"AC-{year}-{universe_code}-{sequence:03d}"

	def get_next_sequence(self, year):
		"""Get next sequence number for calendar ID"""
		existing = frappe.db.sql("""
			SELECT calendar_id FROM `tabAudit Calendar`
			WHERE calendar_id LIKE %s
			ORDER BY calendar_id DESC LIMIT 1
		""", f"AC-{year}-%")

		if existing:
			last_id = existing[0][0]
			try:
				sequence = int(last_id.split('-')[-1])
				return sequence + 1
			except (ValueError, IndexError):
				pass
		return 1

	def validate_dates(self):
		"""Validate date logic"""
		if self.planned_start_date and self.planned_end_date:
			if self.planned_end_date < self.planned_start_date:
				frappe.throw(_("Planned end date cannot be before planned start date"))

		if self.actual_start_date and self.actual_end_date:
			if self.actual_end_date < self.actual_start_date:
				frappe.throw(_("Actual end date cannot be before actual start date"))

		if self.status == "Completed" and not self.actual_end_date:
			frappe.throw(_("Actual end date is required when status is Completed"))

	def check_resource_conflicts(self):
		"""Check for resource conflicts with other audits"""
		if self.lead_auditor and self.planned_start_date and self.planned_end_date:
			conflicts = self.get_resource_conflicts(self.lead_auditor, self.planned_start_date, self.planned_end_date)

			if conflicts:
				conflict_details = []
				for conflict in conflicts:
					conflict_details.append(f"{conflict['calendar_id']} ({conflict['audit_universe']})")

				self.conflicts_identified = f"Resource conflicts with: {', '.join(conflict_details)}"
				frappe.msgprint(_("Resource conflicts detected. Please review and resolve."), indicator="orange")

	def get_resource_conflicts(self, auditor, start_date, end_date):
		"""Get list of conflicting audit assignments for a resource"""
		conflicts = frappe.db.sql("""
			SELECT calendar_id, audit_universe, planned_start_date, planned_end_date
			FROM `tabAudit Calendar`
			WHERE lead_auditor = %s
			AND status NOT IN ('Completed', 'Cancelled')
			AND name != %s
			AND (
				(planned_start_date BETWEEN %s AND %s)
				OR (planned_end_date BETWEEN %s AND %s)
				OR (%s BETWEEN planned_start_date AND planned_end_date)
			)
		""", (auditor, self.name if self.name else '', start_date, end_date, start_date, end_date, start_date), as_dict=True)

		return conflicts

	def update_progress(self):
		"""Update progress based on status and dates"""
		if self.status == "Completed":
			self.progress_percentage = 100
		elif self.status == "In Progress" and self.actual_start_date:
			if self.planned_end_date and self.planned_start_date:
				total_days = date_diff(self.planned_end_date, self.planned_start_date) + 1
				days_elapsed = date_diff(getdate(), self.actual_start_date) + 1
				if total_days > 0:
					self.progress_percentage = min(100, (days_elapsed / total_days) * 100)
		elif self.status in ["Planned", "Scheduled"]:
			self.progress_percentage = 0
		else:
			# For other statuses, maintain current progress
			pass

	def validate_status_transitions(self):
		"""Validate logical status transitions"""
		valid_transitions = {
			"Planned": ["Scheduled", "Cancelled"],
			"Scheduled": ["In Progress", "On Hold", "Cancelled", "Rescheduled"],
			"In Progress": ["On Hold", "Completed", "Rescheduled"],
			"On Hold": ["In Progress", "Scheduled", "Cancelled"],
			"Rescheduled": ["Scheduled", "In Progress", "Cancelled"],
			"Completed": [],  # Terminal state
			"Cancelled": []   # Terminal state
		}

		if self.has_value_changed("status"):
			old_status = self.get_doc_before_save().status if self.get_doc_before_save() else None
			if old_status and self.status not in valid_transitions.get(old_status, []):
				frappe.throw(_("Invalid status transition from {0} to {1}").format(old_status, self.status))

	def on_update(self):
		"""Update related records when calendar changes"""
		if self.has_value_changed("status"):
			self.update_audit_universe_status()

	def update_audit_universe_status(self):
		"""Update the audit universe with current audit status"""
		if self.audit_universe:
			universe = frappe.get_doc("Audit Universe", self.audit_universe)
			if self.status == "In Progress":
				universe.last_audit_date = self.actual_start_date or getdate()
			elif self.status == "Completed":
				universe.last_audit_date = self.actual_end_date or getdate()
				universe.last_audit_reference = self.name
			universe.save()

@frappe.whitelist()
def get_calendar_conflicts(start_date, end_date, auditor=None):
	"""Get all calendar conflicts for a date range"""
	filters = {
		"planned_start_date": ["<=", end_date],
		"planned_end_date": [">=", start_date],
		"status": ["not in", ["Completed", "Cancelled"]]
	}

	if auditor:
		filters["lead_auditor"] = auditor

	conflicts = frappe.get_all("Audit Calendar",
		filters=filters,
		fields=["calendar_id", "audit_universe", "lead_auditor", "planned_start_date", "planned_end_date"]
	)

	return conflicts

@frappe.whitelist()
def get_auditor_schedule(auditor, month=None, year=None):
	"""Get audit schedule for a specific auditor"""
	if not month:
		month = getdate().month
	if not year:
		year = getdate().year

	start_date = f"{year}-{month:02d}-01"
	end_date = add_days(getdate(start_date), 31)
	end_date = end_date.replace(day=1, month=end_date.month % 12 + 1, year=end_date.year + (end_date.month // 12)) - datetime.timedelta(days=1)
	end_date = end_date.date()

	schedule = frappe.get_all("Audit Calendar",
		filters={
			"lead_auditor": auditor,
			"planned_start_date": [">=", start_date],
			"planned_end_date": ["<=", end_date],
			"status": ["not in", ["Cancelled"]]
		},
		fields=["calendar_id", "audit_universe", "planned_start_date", "planned_end_date", "status"],
		order_by="planned_start_date"
	)

	return schedule