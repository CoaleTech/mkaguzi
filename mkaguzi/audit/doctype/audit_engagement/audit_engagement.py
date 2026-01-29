# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, date_diff, now_datetime
from datetime import datetime

class AuditEngagement(Document):
	def validate(self):
		self.validate_engagement_id()
		self.validate_dates()
		self.calculate_budget_variance()
		self.update_findings_count()
		self.validate_status_transitions()
		self.set_timeline_dates()

	def validate_engagement_id(self):
		"""Auto-generate engagement ID if not provided"""
		if not self.engagement_id:
			year = str(getdate().year)
			sequence = self.get_next_sequence(year)
			self.engagement_id = f"AE-{year}-{sequence:03d}"

	def get_next_sequence(self, year):
		"""Get next sequence number for engagement ID"""
		existing = frappe.db.sql("""
			SELECT engagement_id FROM `tabAudit Engagement`
			WHERE engagement_id LIKE %s
			ORDER BY engagement_id DESC LIMIT 1
		""", f"AE-{year}-%")

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
		if self.period_start and self.period_end:
			if self.period_end < self.period_start:
				frappe.throw(_("Period end date cannot be before period start date"))

		if self.planning_start and self.planning_end:
			if self.planning_end < self.planning_start:
				frappe.throw(_("Planning end date cannot be before planning start date"))

		if self.fieldwork_start and self.fieldwork_end:
			if self.fieldwork_end < self.fieldwork_start:
				frappe.throw(_("Fieldwork end date cannot be before fieldwork start date"))

		if self.reporting_start and self.reporting_end:
			if self.reporting_end < self.reporting_start:
				frappe.throw(_("Reporting end date cannot be before reporting start date"))

	def set_timeline_dates(self):
		"""Set default timeline dates based on status"""
		if self.status == "Planning" and not self.planning_start:
			self.planning_start = getdate()
		elif self.status == "Fieldwork" and not self.fieldwork_start:
			self.fieldwork_start = getdate()
		elif self.status == "Reporting" and not self.reporting_start:
			self.reporting_start = getdate()
		elif self.status == "Finalized" and not self.actual_completion_date:
			self.actual_completion_date = getdate()

	def calculate_budget_variance(self):
		"""Calculate budget variance based on actual vs budgeted hours"""
		if self.budgeted_hours and self.actual_hours:
			self.budget_variance = self.actual_hours - self.budgeted_hours
			if self.budgeted_hours > 0:
				self.budget_variance_percent = (self.budget_variance / self.budgeted_hours) * 100
		else:
			self.budget_variance = 0
			self.budget_variance_percent = 0

	def update_findings_count(self):
		"""Update findings count from linked audit findings"""
		if self.name:
			findings = frappe.db.sql("""
				SELECT
					COUNT(*) as total_findings,
					SUM(CASE WHEN risk_rating IN ('Critical', 'High') THEN 1 ELSE 0 END) as high_risk_findings
				FROM `tabAudit Finding`
				WHERE engagement_reference = %s AND docstatus = 1
			""", self.name, as_dict=True)

			if findings:
				self.findings_count = findings[0].total_findings or 0
				self.high_risk_findings_count = findings[0].high_risk_findings or 0

	def validate_status_transitions(self):
		"""Validate logical status transitions with support for On Hold and Cancelled"""
		valid_transitions = {
			# Forward transitions
			"Planning": ["Fieldwork", "Reporting", "On Hold", "Cancelled"],
			"Fieldwork": ["Reporting", "Management Review", "Planning", "On Hold", "Cancelled"],
			"Reporting": ["Management Review", "Quality Review", "Fieldwork", "On Hold", "Cancelled"],
			"Management Review": ["Quality Review", "Finalized", "Reporting", "On Hold", "Cancelled"],
			"Quality Review": ["Finalized", "Issued", "Management Review", "On Hold"],
			"Finalized": ["Issued", "Quality Review", "On Hold"],
			"Issued": [],  # Terminal state
			# Recovery transitions
			"On Hold": ["Planning", "Fieldwork", "Reporting", "Management Review", "Quality Review", "Finalized", "Cancelled"],
			"Cancelled": []  # Terminal state - can only be recovered via amendment
		}

		if self.has_value_changed("status"):
			old_status = self.get_doc_before_save().status if self.get_doc_before_save() else None

			# Allow setting initial status
			if not old_status:
				return

			# Validate transition
			if self.status not in valid_transitions.get(old_status, []):
				frappe.throw(_("Invalid status transition from {0} to {1}").format(old_status, self.status))

			# Permission checks for state changes
			self.validate_status_permissions(old_status, self.status)

		# Set completion date when finalized
		if self.status == "Finalized" and not self.actual_completion_date:
			self.actual_completion_date = getdate()

		# Set cancellation date when cancelled
		if self.status == "Cancelled" and not self.cancellation_date:
			self.cancellation_date = getdate()

	def validate_status_permissions(self, old_status, new_status):
		"""Validate that user has permission for status transitions"""
		user = frappe.session.user

		# Only allow cancelling if user has cancel permission
		if new_status == "Cancelled" and not frappe.has_permission("Audit Engagement", "cancel", user=user):
			frappe.throw(_("You don't have permission to cancel this audit engagement"))

		# Only allow placing on hold if user has write permission
		if new_status == "On Hold" and not frappe.has_permission("Audit Engagement", "write", user=user):
			frappe.throw(_("You don't have permission to place this engagement on hold"))

		# Quality Review to Finalized requires reviewer role
		if old_status == "Quality Review" and new_status == "Finalized":
			if not frappe.has_permission("Audit Engagement", "approve", user=user):
				frappe.throw(_("You don't have permission to finalize this audit engagement"))

	def on_update(self):
		"""Update related records when engagement changes"""
		if self.has_value_changed("status"):
			self.update_audit_calendar_status()
			self.update_audit_program_status()
			self.check_for_stale_engagement()

	def check_for_stale_engagement(self):
		"""Check if engagement has been stuck in a status too long and send alerts"""
		from frappe.utils import add_days, nowdate

		# Define stale thresholds (in days)
		stale_thresholds = {
			"Planning": 30,
			"Fieldwork": 60,
			"Reporting": 30,
			"Management Review": 14,
			"Quality Review": 14,
			"On Hold": 90
		}

		if self.status in stale_thresholds:
			threshold = stale_thresholds[self.status]
			modified_date = getdate(self.modified)

			if (nowdate() - modified_date).days > threshold:
				# Send notification to supervisor
				self.send_stale_engagement_alert()

	def send_stale_engagement_alert(self):
		"""Send alert for stale engagement"""
		try:
			# Get engagement owner or lead auditor
			owner = self.lead_auditor or self.owner

			# Send notification
			frappe.sendmail(
				recipients=[owner],
				subject=_("Stale Audit Engagement Alert: {0}").format(self.engagement_id),
				message=_("""
					<h3>Stale Audit Engagement Alert</h3>
					<p>The following audit engagement has been in <strong>{0}</strong> status for an extended period:</p>
					<ul>
						<li>Engagement ID: {1}</li>
						<li>Engagement Title: {2}</li>
						<li>Current Status: {0}</li>
						<li>Last Modified: {3}</li>
					</ul>
					<p>Please take appropriate action to move this engagement forward.</p>
				""").format(self.status, self.engagement_id, self.engagement_title, self.modified),
				reference_doctype="Audit Engagement",
				reference_name=self.name
			)
		except Exception as e:
			frappe.log_error(f"Failed to send stale engagement alert: {str(e)}", "Audit Engagement Alert")

	def update_audit_calendar_status(self):
		"""Update corresponding audit calendar entry"""
		if self.planned_audit_reference:
			calendar_entries = frappe.get_all("Audit Calendar",
				filters={"annual_audit_plan": self.planned_audit_reference, "audit_universe": self.audit_universe},
				fields=["name"]
			)

			for entry in calendar_entries:
				calendar = frappe.get_doc("Audit Calendar", entry.name)
				if self.status == "Planning":
					calendar.status = "Scheduled"
				elif self.status in ["Fieldwork", "Reporting"]:
					calendar.status = "In Progress"
				elif self.status == "Finalized":
					calendar.status = "Completed"
				calendar.save()

	def update_audit_program_status(self):
		"""Update audit program status"""
		if self.audit_program_reference:
			program = frappe.get_doc("Audit Program", self.audit_program_reference)
			if self.status == "Planning":
				program.status = "Draft"
			elif self.status in ["Fieldwork", "Reporting"]:
				program.status = "In Progress"
			elif self.status == "Finalized":
				program.status = "Completed"
			program.save()

	def on_submit(self):
		"""Create audit program if not exists"""
		if not self.audit_program_reference:
			self.create_audit_program()

	def create_audit_program(self):
		"""Create a new audit program for this engagement"""
		program = frappe.get_doc({
			"doctype": "Audit Program",
			"program_name": f"{self.engagement_title} - Audit Program",
			"engagement_reference": self.name,
			"audit_type": self.audit_type,
			"status": "Draft"
		})
		program.insert()
		self.audit_program_reference = program.name

@frappe.whitelist()
def get_engagement_summary():
	"""Get summary of audit engagements for dashboard"""
	data = frappe.db.sql("""
		SELECT
			status,
			COUNT(*) as count,
			SUM(findings_count) as total_findings,
			SUM(high_risk_findings_count) as high_risk_findings,
			AVG(quality_score) as avg_quality_score
		FROM `tabAudit Engagement`
		WHERE docstatus = 1
		GROUP BY status
	""", as_dict=True)

	return data

@frappe.whitelist()
def get_team_utilization(engagement_id):
	"""Get team utilization details for an engagement"""
	engagement = frappe.get_doc("Audit Engagement", engagement_id)

	utilization_data = {
		"team_members": [],
		"total_budgeted": engagement.budgeted_hours or 0,
		"total_actual": engagement.actual_hours or 0
	}

	if engagement.audit_team:
		for member in engagement.audit_team:
			utilization_data["team_members"].append({
				"name": member.team_member_name,
				"role": member.role,
				"budgeted_hours": member.budgeted_hours,
				"actual_hours": member.actual_hours,
				"variance": (member.actual_hours or 0) - (member.budgeted_hours or 0)
			})

	return utilization_data