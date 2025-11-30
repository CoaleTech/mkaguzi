# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, date_diff, add_days
from frappe.model.mapper import get_mapped_doc

class AuditFinding(Document):
	def autoname(self):
		if not self.finding_id:
			# Generate finding ID based on engagement and sequence
			engagement = frappe.get_doc("Audit Engagement", self.engagement_reference)
			year = getdate(engagement.start_date).year

			# Get next sequence number for this engagement
			existing_findings = frappe.db.count("Audit Finding", {
				"engagement_reference": self.engagement_reference
			})
			sequence = existing_findings + 1

			self.finding_id = f"FND-{engagement.name}-{year}-{sequence:03d}"

	def validate(self):
		self.validate_dates()
		self.calculate_risk_score()
		self.calculate_exception_rate()
		self.validate_status_transitions()
		self.update_overdue_status()
		self.set_next_follow_up_date()

	def validate_dates(self):
		"""Validate date relationships"""
		if self.target_completion_date and self.response_date:
			if self.target_completion_date < self.response_date:
				frappe.throw(_("Target Completion Date cannot be before Response Date"))

		if self.closure_date and self.target_completion_date:
			if self.closure_date > self.target_completion_date:
				frappe.msgprint(_("Finding closed after target completion date"))

		if self.verification_date and self.closure_date:
			if self.verification_date < self.closure_date:
				frappe.throw(_("Verification Date cannot be before Closure Date"))

	def calculate_risk_score(self):
		"""Calculate risk score based on likelihood and impact"""
		likelihood_scores = {
			"Rare": 1,
			"Unlikely": 2,
			"Possible": 3,
			"Likely": 4,
			"Almost Certain": 5
		}

		impact_scores = {
			"Insignificant": 1,
			"Minor": 2,
			"Moderate": 3,
			"Major": 4,
			"Catastrophic": 5
		}

		if self.likelihood and self.impact:
			likelihood_score = likelihood_scores.get(self.likelihood, 0)
			impact_score = impact_scores.get(self.impact, 0)
			self.risk_score = likelihood_score * impact_score

			# Set risk rating based on score
			if self.risk_score >= 16:
				self.risk_rating = "Critical"
			elif self.risk_score >= 10:
				self.risk_rating = "High"
			elif self.risk_score >= 6:
				self.risk_rating = "Medium"
			else:
				self.risk_rating = "Low"

	def calculate_exception_rate(self):
		"""Calculate exception rate percentage"""
		if self.sample_size and self.sample_size > 0 and self.exceptions_found is not None:
			self.exception_rate = (self.exceptions_found / self.sample_size) * 100

	def validate_status_transitions(self):
		"""Validate status transition rules"""
		valid_transitions = {
			"Open": ["Action in Progress", "Accepted as Risk", "Management Override"],
			"Action in Progress": ["Pending Verification", "Accepted as Risk", "Management Override"],
			"Pending Verification": ["Closed", "Action in Progress"],
			"Closed": [],  # Closed findings cannot be reopened
			"Accepted as Risk": [],
			"Management Override": []
		}

		if hasattr(self, '_original_status') and self._original_status != self.finding_status:
			if self.finding_status not in valid_transitions.get(self._original_status, []):
				frappe.throw(_("Invalid status transition from {0} to {1}").format(
					self._original_status, self.finding_status))

	def update_overdue_status(self):
		"""Update overdue days and escalation status"""
		today = getdate(nowdate())

		if self.target_completion_date:
			self.overdue_days = date_diff(today, getdate(self.target_completion_date))
			if self.overdue_days > 0:
				self.escalation_required = 1
				# Set escalation level based on overdue days
				if self.overdue_days > 90:
					self.escalation_level = "Board"
				elif self.overdue_days > 60:
					self.escalation_level = "Audit Committee"
				elif self.overdue_days > 30:
					self.escalation_level = "CAE"
				else:
					self.escalation_level = "Manager"
			else:
				self.escalation_required = 0
				self.escalation_level = ""

	def set_next_follow_up_date(self):
		"""Set next follow-up date based on frequency"""
		if not self.follow_up_required or not self.follow_up_frequency:
			return

		base_date = self.response_date or self.created_on or nowdate()

		frequency_map = {
			"Monthly": 30,
			"Quarterly": 90,
			"Semi-Annual": 180,
			"Annual": 365,
			"One-time": None
		}

		days = frequency_map.get(self.follow_up_frequency)
		if days:
			self.next_follow_up_date = add_days(base_date, days)

	def before_save(self):
		"""Set original status for validation"""
		if not self.is_new():
			original = frappe.get_doc(self.doctype, self.name)
			self._original_status = original.finding_status

	def on_update(self):
		"""Handle status changes and create status history"""
		if hasattr(self, '_original_status') and self._original_status != self.finding_status:
			self.add_status_change_entry()

	def add_status_change_entry(self):
		"""Add entry to status change history"""
		if not self.status_history:
			self.status_history = []

		self.append("status_history", {
			"previous_status": self._original_status,
			"new_status": self.finding_status,
			"changed_on": nowdate(),
			"changed_by": frappe.session.user,
			"reason": "Status updated via system"
		})

	def before_submit(self):
		"""Validation before submission"""
		if self.finding_status != "Closed":
			frappe.throw(_("Only closed findings can be submitted"))

		if not self.closure_date:
			self.closure_date = nowdate()

		if not self.closed_by:
			self.closed_by = frappe.session.user

@frappe.whitelist()
def make_corrective_action_plan(source_name, target_doc=None):
	"""Create Corrective Action Plan from Audit Finding"""
	def set_missing_values(source, target):
		target.audit_finding = source.name
		target.finding_title = source.finding_title
		target.responsible_person = source.responsible_person
		target.responsible_department = source.responsible_department
		target.target_completion_date = source.target_completion_date

	doc = get_mapped_doc("Audit Finding", source_name, {
		"Audit Finding": {
			"doctype": "Corrective Action Plan",
			"field_map": {
				"name": "audit_finding",
				"finding_title": "title",
				"recommendation": "action_description"
			}
		}
	}, target_doc, set_missing_values)

	return doc

@frappe.whitelist()
def get_finding_summary(engagement=None):
	"""Get summary of findings for an engagement"""
	if not engagement:
		return {}

	findings = frappe.get_all("Audit Finding",
		filters={"engagement_reference": engagement},
		fields=["finding_status", "risk_rating", "finding_category"]
	)

	summary = {
		"total": len(findings),
		"by_status": {},
		"by_risk": {},
		"by_category": {}
	}

	for finding in findings:
		# Count by status
		status = finding.finding_status or "Open"
		summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

		# Count by risk rating
		risk = finding.risk_rating or "Low"
		summary["by_risk"][risk] = summary["by_risk"].get(risk, 0) + 1

		# Count by category
		category = finding.finding_category or "Other"
		summary["by_category"][category] = summary["by_category"].get(category, 0) + 1

	return summary

@frappe.whitelist()
def get_open_findings():
	"""Get open findings for chat room creation"""
	try:
		# Get open findings that can be associated with chat rooms
		findings = frappe.get_all("Audit Finding",
			filters={
				"finding_status": ["in", ["Open", "Action in Progress", "Pending Verification"]],
				"docstatus": ["!=", 2]  # Not cancelled
			},
			fields=[
				"name",
				"finding_id",
				"finding_title",
				"engagement_reference",
				"finding_status",
				"risk_rating",
				"responsible_person",
				"responsible_department",
				"target_completion_date",
				"overdue_days"
			],
			order_by="creation desc",
			limit=100
		)

		# Format findings for the frontend
		formatted_findings = []
		for finding in findings:
			formatted_findings.append({
				"name": finding.name,
				"finding_id": finding.finding_id,
				"title": finding.finding_title,
				"engagement": finding.engagement_reference,
				"status": finding.finding_status,
				"risk_rating": finding.risk_rating,
				"responsible_person": finding.responsible_person,
				"responsible_department": finding.responsible_department,
				"target_completion_date": finding.target_completion_date,
				"overdue_days": finding.overdue_days or 0,
				"display_name": f"{finding.finding_id}: {finding.finding_title}",
				"is_overdue": (finding.overdue_days or 0) > 0
			})

		return {
			"success": True,
			"findings": formatted_findings,
			"total_count": len(formatted_findings)
		}

	except Exception as e:
		frappe.log_error(f"Failed to get open findings: {str(e)}")
		return {
			"success": False,
			"error": str(e),
			"findings": []
		}