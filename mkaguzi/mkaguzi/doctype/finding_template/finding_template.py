# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

class FindingTemplate(Document):
	def autoname(self):
		"""Generate template ID based on category and sequence"""
		if not self.template_id:
			category_prefix = {
				"Control Deficiency": "CD",
				"Non-Compliance": "NC",
				"Inefficiency": "IE",
				"Error": "ER",
				"Fraud Indicator": "FI",
				"Best Practice Opportunity": "BP"
			}.get(self.finding_category, "FT")

			# Get next sequence number
			sequence = frappe.db.count("Finding Template", {"finding_category": self.finding_category}) + 1
			self.template_id = f"{category_prefix}-{sequence:03d}"

	def validate(self):
		"""Validate template data"""
		self.validate_template_fields()
		self.validate_cause_options()
		self.update_timestamps()

	def validate_template_fields(self):
		"""Validate required template fields"""
		required_fields = [
			"condition_template",
			"criteria_template",
			"effect_template",
			"recommendation_template"
		]

		for field in required_fields:
			if not getattr(self, field, None):
				frappe.throw(_(f"{field.replace('_', ' ').title()} is required"))

	def validate_cause_options(self):
		"""Validate cause options table"""
		if self.cause_options:
			default_count = sum(1 for cause in self.cause_options if cause.is_default)
			if default_count > 1:
				frappe.throw(_("Only one cause option can be marked as default"))

	def update_timestamps(self):
		"""Update creation and modification timestamps"""
		if not self.created_on:
			self.created_on = now_datetime()
		if not self.created_by:
			self.created_by = frappe.session.user
		self.last_modified = now_datetime()

	def before_save(self):
		"""Actions before saving"""
		self.update_usage_count()

	def update_usage_count(self):
		"""Update usage count based on findings using this template"""
		if self.template_id:
			usage_count = frappe.db.count("Audit Finding", {"finding_template": self.template_id})
			self.usage_count = usage_count

@frappe.whitelist()
def get_template_suggestions(finding_category=None, risk_area=None):
	"""Get template suggestions based on category and risk area"""
	filters = {"is_active": 1}

	if finding_category:
		filters["finding_category"] = finding_category
	if risk_area:
		filters["risk_area"] = risk_area

	templates = frappe.get_all("Finding Template",
		filters=filters,
		fields=["template_id", "template_name", "template_title", "typical_risk_rating"],
		order_by="usage_count desc, modified desc"
	)

	return templates

@frappe.whitelist()
def apply_template(template_id, finding_doc):
	"""Apply template data to a finding document"""
	if not frappe.has_permission("Finding Template", "read"):
		frappe.throw(_("Not permitted to read Finding Templates"))

	template = frappe.get_doc("Finding Template", template_id)

	# Apply template data to finding
	finding_doc.finding_category = template.finding_category
	finding_doc.finding_title = template.template_title
	finding_doc.condition = template.condition_template
	finding_doc.criteria = template.criteria_template
	finding_doc.effect = template.effect_template
	finding_doc.recommendation = template.recommendation_template
	finding_doc.risk_rating = template.typical_risk_rating

	# Apply default cause if available
	if template.cause_options:
		default_causes = [cause for cause in template.cause_options if cause.is_default]
		if default_causes:
			finding_doc.cause = default_causes[0].cause_description

	return finding_doc