# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, getdate
import re

class WorkingPaper(Document):
	def autoname(self):
		"""Generate unique Working Paper ID"""
		if not self.working_paper_id:
			# Generate WP-YYYY-NNNN format
			current_year = str(getdate(nowdate()).year)
			prefix = f"WP-{current_year}-"

			# Get the last WP number for this year
			last_wp = frappe.db.sql("""
				SELECT working_paper_id
				FROM `tabWorking Paper`
				WHERE working_paper_id LIKE %s
				ORDER BY working_paper_id DESC
				LIMIT 1
			""", (prefix + "%",))

			if last_wp:
				# Extract the number from the last ID
				last_num = int(last_wp[0][0].split('-')[-1])
				next_num = last_num + 1
			else:
				next_num = 1

			# Format with leading zeros
			self.working_paper_id = f"{prefix}{next_num:04d}"

	def validate(self):
		"""Validate Working Paper data"""
		self.validate_dates()
		self.validate_references()
		self.calculate_test_results()
		self.update_procedure_status()

	def validate_dates(self):
		"""Validate preparation and review dates"""
		if self.preparation_date and getdate(self.preparation_date) > getdate(nowdate()):
			frappe.throw(_("Preparation Date cannot be in the future"))

		if self.review_date and self.preparation_date:
			if getdate(self.review_date) < getdate(self.preparation_date):
				frappe.throw(_("Review Date cannot be before Preparation Date"))

	def validate_references(self):
		"""Validate engagement and procedure references"""
		if self.engagement_reference:
			# Check if engagement exists and is active
			engagement = frappe.get_doc("Audit Engagement", self.engagement_reference)
			if engagement.status not in ["Active", "In Progress"]:
				frappe.throw(_("Cannot create Working Paper for inactive engagement"))

		if self.procedure_reference:
			# Check if procedure belongs to the same engagement
			procedure = frappe.get_doc("Audit Procedure", self.procedure_reference)
			if procedure.parent != self.engagement_reference:
				frappe.throw(_("Procedure does not belong to the selected engagement"))

	def calculate_test_results(self):
		"""Calculate test results summary"""
		if self.sample_selection:
			total_sample = len(self.sample_selection)
			tested_items = sum(1 for item in self.sample_selection if item.test_result != "Not Tested")
			exceptions = sum(1 for item in self.sample_selection if item.exception_found)

			self.total_sample_size = total_sample
			self.items_tested = tested_items
			self.exceptions_found = exceptions

			if tested_items > 0:
				self.exception_rate = (exceptions / tested_items) * 100
			else:
				self.exception_rate = 0

	def update_procedure_status(self):
		"""Update related procedure status"""
		if self.procedure_reference and self.findings_identified:
			findings_count = len([f for f in self.findings_identified if f.status in ["Open", "In Progress"]])

			if findings_count > 0:
				status = "Issues Found"
			else:
				status = "Completed"

			# Update procedure status (this would need to be implemented in audit_procedure.py)
			frappe.db.set_value("Audit Procedure", self.procedure_reference, "status", status)

	def on_update(self):
		"""Handle updates"""
		self.update_version_control()

	def update_version_control(self):
		"""Update version control information"""
		if not self.version_control:
			return

		# Get current version
		current_version = self.version_number or 1.0

		# Check if content has changed significantly
		content_fields = [
			'objective', 'scope', 'methodology', 'work_performed',
			'conclusion', 'recommendations', 'findings_identified'
		]

		changes_detected = False
		for field in content_fields:
			old_value = frappe.db.get_value("Working Paper", self.name, field)
			new_value = getattr(self, field, None)
			if old_value != new_value:
				changes_detected = True
				break

		if changes_detected:
			# Increment version
			new_version = round(current_version + 0.1, 1)
			self.version_number = new_version

			# Add revision history
			if not self.revision_history:
				self.revision_history = []

			self.revision_history.append({
				"version_number": new_version,
				"revision_date": nowdate(),
				"revised_by": frappe.session.user,
				"revision_reason": "Content Update",
				"changes_made": "Working paper content updated"
			})

@frappe.whitelist()
def get_working_papers_by_engagement(engagement_name):
	"""Get all working papers for an engagement"""
	return frappe.get_all("Working Paper",
		filters={"engagement_reference": engagement_name},
		fields=["name", "wp_title", "wp_type", "prepared_by", "preparation_date", "review_status"],
		order_by="creation desc"
	)

@frappe.whitelist()
def get_working_papers_by_procedure(procedure_name):
	"""Get working papers for a specific procedure"""
	return frappe.get_all("Working Paper",
		filters={"procedure_reference": procedure_name},
		fields=["name", "wp_title", "prepared_by", "preparation_date"],
		order_by="creation desc"
	)

@frappe.whitelist()
def create_working_paper_from_procedure(procedure_name):
	"""Create a new working paper from an audit procedure"""
	procedure = frappe.get_doc("Audit Procedure", procedure_name)

	# Create new working paper
	wp = frappe.new_doc("Working Paper")
	wp.engagement_reference = procedure.parent
	wp.procedure_reference = procedure.name
	wp.wp_title = procedure.procedure_name
	wp.wp_type = "Test of Controls" if procedure.procedure_type == "Control Test" else "Substantive Test"
	wp.objective = procedure.objective
	wp.scope = procedure.scope
	wp.prepared_by = frappe.session.user

	wp.insert()
	return wp.name