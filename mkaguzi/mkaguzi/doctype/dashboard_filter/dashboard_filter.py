# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import json

class DashboardFilter(Document):
	def validate(self):
		"""Validate filter configuration"""
		self.validate_filter_type()
		self.validate_options()
		self.set_default_position()

	def validate_filter_type(self):
		"""Validate filter type and required fields"""
		valid_types = ["Text", "Select", "Multi-Select", "Date", "Date Range", "Number", "Number Range"]

		if self.filter_type not in valid_types:
			frappe.throw(_("Invalid filter type. Valid types: {0}").format(", ".join(valid_types)))

		# Validate required fields based on type
		if self.filter_type in ["Select", "Multi-Select"]:
			if not self.filter_options:
				frappe.throw(_("Filter options are required for {0}").format(self.filter_type))

		if self.filter_type in ["Date Range", "Number Range"]:
			if not self.min_value or not self.max_value:
				frappe.throw(_("Min and max values are required for {0}").format(self.filter_type))

	def validate_options(self):
		"""Validate filter options"""
		if self.filter_options:
			try:
				options = json.loads(self.filter_options)
				if not isinstance(options, list):
					frappe.throw(_("Filter options must be a JSON array"))
			except json.JSONDecodeError:
				frappe.throw(_("Invalid JSON in filter options"))

	def set_default_position(self):
		"""Set default filter position"""
		if not self.position:
			# Get max position for this dashboard
			max_pos = frappe.db.sql("""
				SELECT MAX(position) as max_pos
				FROM `tabDashboard Filter`
				WHERE parent = %s
			""", self.parent)

			self.position = (max_pos[0][0] or 0) + 1

	def before_save(self):
		"""Handle before save operations"""
		if not self.filter_id:
			# Generate unique filter ID
			import uuid
			self.filter_id = str(uuid.uuid4())[:8].upper()

@frappe.whitelist()
def get_filter_types():
	"""Get available filter types"""
	return [
		{"value": "Text", "label": "Text Input"},
		{"value": "Select", "label": "Single Select"},
		{"value": "Multi-Select", "label": "Multi Select"},
		{"value": "Date", "label": "Date Picker"},
		{"value": "Date Range", "label": "Date Range"},
		{"value": "Number", "label": "Number Input"},
		{"value": "Number Range", "label": "Number Range"}
	]

@frappe.whitelist()
def get_filter_options(filter_name):
	"""Get filter options for a specific filter"""
	try:
		filter_doc = frappe.get_doc("Dashboard Filter", filter_name)

		if filter_doc.filter_type in ["Select", "Multi-Select"]:
			if filter_doc.filter_options:
				return json.loads(filter_doc.filter_options)
			else:
				# Generate dynamic options based on field
				return get_dynamic_filter_options(filter_doc)

		return []

	except Exception as e:
		frappe.throw(_("Failed to get filter options: {0}").format(str(e)))

def get_dynamic_filter_options(filter_doc):
	"""Generate dynamic filter options based on field configuration"""
	try:
		if filter_doc.field_name == "status":
			# Get unique statuses from Test Execution
			statuses = frappe.db.get_all("Test Execution",
				fields=["DISTINCT status"],
				filters={"status": ["!=", ""]}
			)
			return [{"value": s.status, "label": s.status} for s in statuses]

		elif filter_doc.field_name == "test_category":
			# Get test categories from Audit Test Library
			categories = frappe.db.get_all("Audit Test Library",
				fields=["DISTINCT test_category"],
				filters={"test_category": ["!=", ""]}
			)
			return [{"value": c.test_category, "label": c.test_category} for c in categories]

		elif filter_doc.field_name == "assigned_to":
			# Get assigned users
			users = frappe.db.get_all("Test Execution",
				fields=["DISTINCT assigned_to"],
				filters={"assigned_to": ["!=", ""]}
			)
			return [{"value": u.assigned_to, "label": u.assigned_to} for u in users]

		return []

	except Exception as e:
		frappe.log_error(f"Failed to generate dynamic filter options: {str(e)}")
		return []

@frappe.whitelist()
def apply_dashboard_filters(dashboard_id, filters):
	"""Apply filters to dashboard and return filtered data"""
	try:
		from mkaguzi.mkaguzi.doctype.data_analytics_dashboard.data_analytics_dashboard import get_dashboard_data

		if isinstance(filters, str):
			filters = json.loads(filters)

		return get_dashboard_data(dashboard_id, filters)

	except Exception as e:
		frappe.throw(_("Failed to apply filters: {0}").format(str(e)))