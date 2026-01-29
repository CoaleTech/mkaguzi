# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, get_datetime

class AuditProcedure(Document):
	def validate(self):
		self.validate_dates()
		self.calculate_findings_count()
		self.update_status_based_on_completion()

	def validate_dates(self):
		"""Validate completion date is not before assignment"""
		if self.completion_date and self.assigned_to:
			# Check if completion date is reasonable
			if self.completion_date < getdate():
				frappe.msgprint(_("Completion date is in the past"))

	def calculate_findings_count(self):
		"""Calculate findings count from related findings"""
		if self.name:
			findings_count = frappe.db.count("Audit Finding", {
				"procedure_reference": self.name
			})
			self.findings_count = findings_count

	def update_status_based_on_completion(self):
		"""Update status based on completion criteria"""
		if self.status == "Completed" and not self.completion_date:
			self.completion_date = getdate()
		elif self.status != "Completed" and self.completion_date:
			# If status changed from completed, clear completion date
			if self.get_db_value("status") == "Completed":
				self.completion_date = None

	def before_save(self):
		"""Set audit fields"""
		if not self.created_by and self.assigned_to:
			self.created_by = frappe.session.user

	def on_update(self):
		"""Update parent program completion status"""
		if self.parent and self.parenttype == "Audit Program":
			parent_program = frappe.get_doc("Audit Program", self.parent)
			parent_program.calculate_completion_summary()
			parent_program.save()

@frappe.whitelist()
def get_procedure_findings(procedure_id):
	"""Get findings related to a procedure"""
	findings = frappe.get_all("Audit Finding",
		filters={"procedure_reference": procedure_id},
		fields=["name", "finding_id", "finding_title", "severity", "status"]
	)
	return findings

@frappe.whitelist()
def update_procedure_status(procedure_id, status, notes=None):
	"""Update procedure status with validation"""
	procedure = frappe.get_doc("Audit Procedure", procedure_id)

	# Validate status transition
	valid_transitions = {
		"Not Started": ["In Progress", "Not Applicable"],
		"In Progress": ["Completed", "Not Applicable"],
		"Completed": ["In Progress"],  # Allow reopening
		"Not Applicable": ["Not Started", "In Progress"]
	}

	if procedure.status in valid_transitions and status not in valid_transitions[procedure.status]:
		frappe.throw(_("Invalid status transition from {0} to {1}").format(procedure.status, status))

	procedure.status = status
	if notes:
		procedure.notes = (procedure.notes or "") + "\n" + get_datetime().strftime("%Y-%m-%d %H:%M") + ": " + notes

	procedure.save()
	return procedure
