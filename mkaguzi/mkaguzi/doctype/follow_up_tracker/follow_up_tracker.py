# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, date_diff, add_days, add_months

class FollowupTracker(Document):
	def autoname(self):
		if not self.tracker_id:
			# Generate tracker ID based on finding
			finding = frappe.get_doc("Audit Finding", self.audit_finding)
			year = getdate().year

			# Get next sequence number for this finding
			existing_trackers = frappe.db.count("Follow-up Tracker", {
				"audit_finding": self.audit_finding
			})
			sequence = existing_trackers + 1

			self.tracker_id = f"FUT-{finding.finding_id}-{sequence:02d}"

	def validate(self):
		self.set_finding_title()
		self.calculate_next_due_date()
		self.update_from_activities()
		self.validate_closure_criteria()

	def set_finding_title(self):
		"""Set finding title from linked audit finding"""
		if self.audit_finding and not self.finding_title:
			finding = frappe.get_doc("Audit Finding", self.audit_finding)
			self.finding_title = finding.finding_title

	def calculate_next_due_date(self):
		"""Calculate next due date based on frequency"""
		if not self.start_date or not self.frequency:
			return

		base_date = self.last_follow_up_date or self.start_date

		frequency_map = {
			"Monthly": lambda d: add_months(d, 1),
			"Quarterly": lambda d: add_months(d, 3),
			"Semi-Annual": lambda d: add_months(d, 6),
			"Annual": lambda d: add_months(d, 12),
			"One-time": lambda d: None,
			"As Needed": lambda d: None
		}

		next_date_func = frequency_map.get(self.frequency)
		if next_date_func:
			self.next_due_date = next_date_func(getdate(base_date))

	def update_from_activities(self):
		"""Update tracker from latest follow-up activities"""
		if not self.follow_up_activities:
			return

		# Get the most recent activity
		latest_activity = max(self.follow_up_activities,
			key=lambda x: x.follow_up_date if x.follow_up_date else "1900-01-01")

		if latest_activity:
			self.last_follow_up_date = latest_activity.follow_up_date
			self.last_follow_up_by = latest_activity.follow_up_by
			self.last_findings = latest_activity.findings

			# Update next due date
			self.calculate_next_due_date()

	def validate_closure_criteria(self):
		"""Validate closure criteria"""
		if self.closure_criteria_met and not self.closure_date:
			self.closure_date = getdate(nowdate())

		if self.status == "Completed" and not self.closure_criteria_met:
			frappe.throw(_("Cannot mark as completed without meeting closure criteria"))

	def on_update(self):
		"""Update related audit finding if needed"""
		if self.status == "Completed" and self.audit_finding:
			# Check if this completes the follow-up requirement for the finding
			finding = frappe.get_doc("Audit Finding", self.audit_finding)
			if finding.follow_up_required and finding.finding_status == "Pending Verification":
				# Check if all trackers for this finding are completed
				active_trackers = frappe.db.count("Follow-up Tracker", {
					"audit_finding": self.audit_finding,
					"status": ["!=", "Completed"]
				})
				if active_trackers == 0:
					finding.finding_status = "Closed"
					finding.save()

@frappe.whitelist()
def create_follow_up_tracker(finding_name):
	"""Create a follow-up tracker for an audit finding"""
	finding = frappe.get_doc("Audit Finding", finding_name)

	# Check if tracker already exists
	existing = frappe.db.exists("Follow-up Tracker", {"audit_finding": finding_name})
	if existing:
		frappe.throw(_("Follow-up tracker already exists for this finding"))

	tracker = frappe.new_doc("Follow-up Tracker")
	tracker.audit_finding = finding_name
	tracker.finding_title = finding.finding_title
	tracker.follow_up_type = "Corrective Action Monitoring"
	tracker.frequency = finding.follow_up_frequency or "Quarterly"
	tracker.start_date = getdate(nowdate())
	tracker.responsible_person = finding.responsible_person
	tracker.responsible_department = finding.responsible_department
	tracker.follow_up_objective = f"Monitor implementation and effectiveness of corrective actions for finding: {finding.finding_title}"
	tracker.status = "Active"

	return tracker

@frappe.whitelist()
def get_overdue_trackers():
	"""Get list of overdue follow-up trackers"""
	today = getdate(nowdate())

	overdue_trackers = frappe.get_all("Follow-up Tracker",
		filters={
			"status": "Active",
			"next_due_date": ["<", today]
		},
		fields=["name", "tracker_id", "audit_finding", "finding_title", "next_due_date", "responsible_person"]
	)

	return overdue_trackers

@frappe.whitelist()
def get_tracker_summary():
	"""Get summary of follow-up trackers"""
	trackers = frappe.get_all("Follow-up Tracker",
		fields=["status", "follow_up_type", "current_status"]
	)

	summary = {
		"total": len(trackers),
		"by_status": {},
		"by_type": {},
		"by_current_status": {},
		"overdue": 0
	}

	today = getdate(nowdate())

	for tracker in trackers:
		# Count by status
		status = tracker.status or "Active"
		summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

		# Count by type
		follow_type = tracker.follow_up_type or "Other"
		summary["by_type"][follow_type] = summary["by_type"].get(follow_type, 0) + 1

		# Count by current status
		current_status = tracker.current_status or "On Track"
		summary["by_current_status"][current_status] = summary["by_current_status"].get(current_status, 0) + 1

	# Count overdue trackers
	overdue = frappe.db.count("Follow-up Tracker", {
		"status": "Active",
		"next_due_date": ["<", today]
	})
	summary["overdue"] = overdue

	return summary