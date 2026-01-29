# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, add_years

class AuditCharter(Document):
	def validate(self):
		self.validate_effective_date()
		self.validate_version_format()
		self.set_default_review_date()

	def validate_effective_date(self):
		"""Validate effective date is not in the past"""
		if self.effective_date and getdate(self.effective_date) < getdate():
			frappe.msgprint(_("Warning: Effective Date is in the past"))

	def validate_version_format(self):
		"""Validate version format (e.g., 1.0, 2.0)"""
		if self.version:
			try:
				major, minor = self.version.split('.')
				if not major.isdigit() or not minor.isdigit():
					frappe.throw(_("Version must be in format X.Y (e.g., 1.0, 2.0)"))
			except ValueError:
				frappe.throw(_("Version must be in format X.Y (e.g., 1.0, 2.0)"))

	def set_default_review_date(self):
		"""Set default review date to 1 year from effective date"""
		if self.effective_date and not self.review_schedule:
			self.review_schedule = "Annually"

	def before_save(self):
		"""Set status based on approval"""
		if self.approval_status == "Approved" and self.status == "Draft":
			self.status = "Active"
			if not self.approval_date:
				self.approval_date = getdate()

	def on_update(self):
		"""Handle version changes and amendments"""
		self.check_duplicate_active_charter()

	def check_duplicate_active_charter(self):
		"""Ensure only one active charter at a time"""
		if self.status == "Active":
			existing_active = frappe.db.exists("Audit Charter", {
				"status": "Active",
				"name": ["!=", self.name]
			})
			if existing_active:
				frappe.msgprint(_("Warning: There is already an active Audit Charter. Previous charter will be marked as Superseded."))
				frappe.db.set_value("Audit Charter", existing_active, "status", "Superseded")

@frappe.whitelist()
def get_active_charter():
	"""Get the currently active audit charter"""
	charter = frappe.db.get_value("Audit Charter",
		{"status": "Active"},
		["name", "charter_name", "version", "effective_date", "purpose_statement",
		 "authority_definition", "responsibility_definition", "cae_name"]
	)
	return charter

@frappe.whitelist()
def amend_charter(source_name):
	"""Create a new version of the charter (amendment)"""
	source_charter = frappe.get_doc("Audit Charter", source_name)

	# Increment version
	try:
		major, minor = map(int, source_charter.version.split('.'))
		minor += 1
		new_version = f"{major}.{minor}"
	except ValueError:
		new_version = "2.0"

	# Create new charter
	new_charter = frappe.new_doc("Audit Charter")
	new_charter.charter_name = source_charter.charter_name
	new_charter.version = new_version
	new_charter.effective_date = getdate()
	new_charter.purpose_statement = source_charter.purpose_statement
	new_charter.authority_definition = source_charter.authority_definition
	new_charter.responsibility_definition = source_charter.responsibility_definition
	new_charter.reporting_structure = source_charter.reporting_structure
	new_charter.audit_scope = source_charter.audit_scope
	new_charter.audit_objectives = source_charter.audit_objectives
	new_charter.independence_clause = source_charter.independence_clause
	new_charter.cae_name = source_charter.cae_name
	new_charter.cae_title = source_charter.cae_title
	new_charter.audit_committee_chair = source_charter.audit_committee_chair
	new_charter.review_schedule = source_charter.review_schedule
	new_charter.standard_compliance = source_charter.standard_compliance
	new_charter.iiacompliant = source_charter.iiacompliant
	new_charter.governance_framework = source_charter.governance_framework
	new_charter.amended_from = source_charter.name
	new_charter.amendment_date = getdate()

	# Mark previous as superseded
	source_charter.status = "Superseded"
	source_charter.save()

	new_charter.save()
	return new_charter.name
