# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, getdate, date_diff

class CorrectiveActionPlan(Document):
	def autoname(self):
		"""Generate action plan ID"""
		if not self.action_plan_id:
			# Get the audit finding to extract year and sequence
			if self.audit_finding:
				finding = frappe.get_doc("Audit Finding", self.audit_finding)
				year = finding.finding_date.strftime("%Y")
				sequence = frappe.db.count("Corrective Action Plan", {"audit_finding": self.audit_finding}) + 1
				self.action_plan_id = f"CAP-{year}-{sequence:03d}"
			else:
				# Fallback if no finding linked
				year = now_datetime().strftime("%Y")
				sequence = frappe.db.count("Corrective Action Plan") + 1
				self.action_plan_id = f"CAP-{year}-{sequence:04d}"

	def validate(self):
		"""Validate action plan data"""
		self.validate_dates()
		self.validate_finding_link()
		self.populate_finding_data()
		self.validate_action_items()
		self.validate_milestones()
		self.update_timestamps()
		self.calculate_overall_progress()

	def validate_dates(self):
		"""Validate date relationships"""
		if self.target_completion_date and getdate(self.target_completion_date) < getdate():
			frappe.throw(_("Target completion date cannot be in the past"))

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
			self.risk_rating = finding.risk_rating
			self.business_unit = finding.business_unit_affected

	def validate_action_items(self):
		"""Validate action items"""
		if not self.action_items:
			frappe.throw(_("At least one action item is required"))

		# Validate action item IDs are unique within this plan
		item_ids = []
		for item in self.action_items:
			if item.action_item_id in item_ids:
				frappe.throw(_("Action Item IDs must be unique within the plan"))
			item_ids.append(item.action_item_id)

			# Validate target dates
			if item.target_date and getdate(item.target_date) > getdate(self.target_completion_date):
				frappe.throw(_("Action item target date cannot be after plan completion date"))

	def validate_milestones(self):
		"""Validate milestones"""
		if self.milestones:
			milestone_ids = []
			for milestone in self.milestones:
				if milestone.milestone_id in milestone_ids:
					frappe.throw(_("Milestone IDs must be unique within the plan"))
				milestone_ids.append(milestone.milestone_id)

				if milestone.target_date and getdate(milestone.target_date) > getdate(self.target_completion_date):
					frappe.throw(_("Milestone target date cannot be after plan completion date"))

	def update_timestamps(self):
		"""Update audit trail timestamps"""
		if not self.created_on:
			self.created_on = now_datetime()
		if not self.created_by:
			self.created_by = frappe.session.user
		self.last_updated = now_datetime()

	def calculate_overall_progress(self):
		"""Calculate overall progress based on action items and milestones"""
		if self.action_items:
			total_items = len(self.action_items)
			completed_items = sum(1 for item in self.action_items if item.status == "Completed")
			if total_items > 0:
				self.overall_progress = (completed_items / total_items) * 100
			else:
				self.overall_progress = 0

	def before_save(self):
		"""Actions before saving"""
		self.update_progress_tracking()

	def update_progress_tracking(self):
		"""Update progress tracking table with latest entry"""
		if self.progress_tracking:
			latest_progress = max(self.progress_tracking, key=lambda x: x.progress_date)
			latest_progress.updated_by = frappe.session.user

	def on_update(self):
		"""Actions after update"""
		self.update_finding_status()
		self.send_notifications()

	def update_finding_status(self):
		"""Update linked finding status based on action plan progress"""
		if self.audit_finding and self.action_plan_status in ["Completed", "In Progress"]:
			finding = frappe.get_doc("Audit Finding", self.audit_finding)
			if self.action_plan_status == "Completed":
				finding.corrective_action_status = "Implemented"
			elif self.action_plan_status == "In Progress":
				finding.corrective_action_status = "In Progress"
			finding.save()

	def send_notifications(self):
		"""Send notifications for status changes"""
		if self.has_value_changed("action_plan_status"):
			self.notify_status_change()

	def notify_status_change(self):
		"""Notify relevant parties of status changes"""
		subject = f"Action Plan Status Update: {self.action_plan_title}"
		message = f"""
		The status of Action Plan {self.action_plan_id} has been updated to {self.action_plan_status}.

		Finding: {self.finding_title}
		Responsible Party: {self.responsible_party}
		Target Completion: {self.target_completion_date}

		Please review the action plan for any required actions.
		"""

		# Notify responsible party and audit manager
		recipients = [self.responsible_party]
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
def get_overdue_action_plans():
	"""Get action plans that are overdue"""
	overdue_plans = frappe.get_all("Corrective Action Plan",
		filters={
			"target_completion_date": ["<", now_datetime().date()],
			"action_plan_status": ["in", ["Draft", "In Progress", "Approved"]]
		},
		fields=["name", "action_plan_title", "responsible_party", "target_completion_date"]
	)

	return overdue_plans

@frappe.whitelist()
def approve_action_plan(action_plan_name, approver_comments=None):
	"""Approve an action plan"""
	if not frappe.has_permission("Corrective Action Plan", "write"):
		frappe.throw(_("Not permitted to approve action plans"))

	action_plan = frappe.get_doc("Corrective Action Plan", action_plan_name)

	# Check if user can approve
	user_roles = frappe.get_roles(frappe.session.user)
	can_approve = any(role in ["Audit Manager", "System Manager"] for role in user_roles)

	if not can_approve:
		frappe.throw(_("You do not have permission to approve action plans"))

	# Update approval workflow
	if action_plan.approval_workflow:
		for approval in action_plan.approval_workflow:
			if approval.approver == frappe.session.user and approval.approval_status == "Pending":
				approval.approval_status = "Approved"
				approval.approval_date = now_datetime()
				if approver_comments:
					approval.comments = approver_comments
				break

	# Check if all approvals are complete
	all_approved = all(approval.approval_status == "Approved" for approval in action_plan.approval_workflow)
	if all_approved:
		action_plan.action_plan_status = "Approved"
		action_plan.approved_by = frappe.session.user
		action_plan.approved_on = now_datetime()

	action_plan.save()

	return {"success": True, "message": "Action plan approved successfully"}