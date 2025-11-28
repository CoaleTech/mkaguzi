# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class FindingTemplate(Document):
	def validate(self):
		"""Validate template data"""
		if not self.condition_template and not self.criteria_template:
			frappe.throw(_("At least Condition or Criteria template must be provided"))

	def on_update(self):
		"""Update usage statistics"""
		pass  # Will be updated when template is used to create findings

@frappe.whitelist()
def apply_finding_template(template_name, finding_doc=None):
	"""Apply finding template to create or update an audit finding"""
	template = frappe.get_doc("Finding Template", template_name)

	if not finding_doc:
		# Create new finding from template
		finding = frappe.new_doc("Audit Finding")
	else:
		finding = frappe.get_doc("Audit Finding", finding_doc)

	# Apply template fields
	if template.condition_template:
		finding.condition = template.condition_template
	if template.criteria_template:
		finding.criteria = template.criteria_template
	if template.cause_template:
		finding.cause = template.cause_template
	if template.effect_template:
		finding.effect = template.effect_template
	if template.recommendation_template:
		finding.recommendation = template.recommendation_template

	finding.finding_category = template.finding_category
	finding.risk_category = template.risk_category

	# Update usage count
	template.usage_count = (template.usage_count or 0) + 1
	template.last_used = frappe.utils.nowdate()
	template.save()

	return finding

@frappe.whitelist()
def get_template_suggestions(finding_category=None, risk_category=None):
	"""Get template suggestions based on finding characteristics"""
	filters = {"is_active": 1}

	if finding_category:
		filters["finding_category"] = finding_category
	if risk_category:
		filters["risk_category"] = risk_category

	templates = frappe.get_all("Finding Template",
		filters=filters,
		fields=["name", "template_name", "description", "usage_count"],
		order_by="usage_count desc, modified desc",
		limit=10
	)

	return templates