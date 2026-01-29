# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, date_diff

class CorrectiveActionPlan(Document):
	def autoname(self):
		if not self.plan_id:
			# Generate plan ID based on finding
			finding = frappe.get_doc("Audit Finding", self.audit_finding)
			year = getdate().year

			# Get next sequence number for this finding
			existing_plans = frappe.db.count("Corrective Action Plan", {
				"audit_finding": self.audit_finding
			})
			sequence = existing_plans + 1

			self.plan_id = f"CAP-{finding.finding_id}-{sequence:02d}"

	def validate(self):
		self.validate_dates()
		self.update_progress_from_milestones()
		self.validate_status_transitions()
		self.update_completion_percentage()

	def validate_dates(self):
		"""Validate date relationships"""
		if self.start_date and self.target_completion_date:
			if self.start_date > self.target_completion_date:
				frappe.throw(_("Start Date cannot be after Target Completion Date"))

		if self.actual_completion_date and self.target_completion_date:
			if self.actual_completion_date > self.target_completion_date:
				frappe.msgprint(_("Plan completed after target date"))

		if self.status == "Completed" and not self.actual_completion_date:
			self.actual_completion_date = getdate(nowdate())

	def update_progress_from_milestones(self):
		"""Update overall progress based on milestone completion"""
		if not self.milestones:
			return

		total_milestones = len(self.milestones)
		completed_milestones = sum(1 for m in self.milestones if m.status == "Completed")

		if total_milestones > 0:
			completion_pct = (completed_milestones / total_milestones) * 100
			self.completion_percentage = completion_pct

			# Update overall progress based on completion
			if completion_pct == 0:
				self.overall_progress = "Not Started"
			elif completion_pct < 25:
				self.overall_progress = "Planning"
			elif completion_pct < 75:
				self.overall_progress = "In Progress"
			elif completion_pct < 100:
				self.overall_progress = "Review"
			else:
				self.overall_progress = "Completed"

	def validate_status_transitions(self):
		"""Validate status transition rules"""
		valid_transitions = {
			"Draft": ["Approved", "Cancelled"],
			"Approved": ["In Progress", "On Hold", "Cancelled"],
			"In Progress": ["On Hold", "Completed", "Cancelled"],
			"On Hold": ["In Progress", "Completed", "Cancelled"],
			"Completed": [],  # Completed plans cannot be changed
			"Cancelled": []
		}

		if hasattr(self, '_original_status') and self._original_status != self.status:
			if self.status not in valid_transitions.get(self._original_status, []):
				frappe.throw(_("Invalid status transition from {0} to {1}").format(
					self._original_status, self.status))

	def update_completion_percentage(self):
		"""Update completion percentage based on milestones"""
		if self.status == "Completed":
			self.completion_percentage = 100
		elif self.status == "Cancelled":
			self.completion_percentage = 0

	def before_save(self):
		"""Set original status for validation"""
		if not self.is_new():
			original = frappe.get_doc(self.doctype, self.name)
			self._original_status = original.status

	def on_update(self):
		"""Update last progress update"""
		if self.status in ["In Progress", "Completed"]:
			self.last_progress_update = getdate(nowdate())

		# Update the related audit finding status if applicable
		if self.audit_finding:
			self.update_finding_status()

	def update_finding_status(self):
		"""Update the related audit finding status based on plan progress"""
		finding = frappe.get_doc("Audit Finding", self.audit_finding)

		if self.status == "Completed" and finding.finding_status == "Action in Progress":
			finding.finding_status = "Pending Verification"
			finding.save()

	def before_submit(self):
		"""Validation before submission"""
		if self.status != "Completed":
			frappe.throw(_("Only completed action plans can be submitted"))

		if not self.actual_completion_date:
			self.actual_completion_date = getdate(nowdate())

@frappe.whitelist()
def get_plan_summary(finding=None):
	"""Get summary of corrective action plans"""
	filters = {}
	if finding:
		filters["audit_finding"] = finding

	plans = frappe.get_all("Corrective Action Plan",
		filters=filters,
		fields=["status", "priority", "completion_percentage"]
	)

	summary = {
		"total": len(plans),
		"by_status": {},
		"by_priority": {},
		"avg_completion": 0
	}

	total_completion = 0
	for plan in plans:
		# Count by status
		status = plan.status or "Draft"
		summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

		# Count by priority
		priority = plan.priority or "Medium"
		summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1

		# Sum completion percentages
		total_completion += plan.completion_percentage or 0

	if plans:
		summary["avg_completion"] = total_completion / len(plans)

	return summary