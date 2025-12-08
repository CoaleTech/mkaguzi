# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def get_context(context):
	"""Setup context for template manager page"""
	context.no_cache = 1

	# Check permissions
	if not frappe.has_permission("Template Registry", "read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	# Add page metadata
	context.title = _("Template Manager")
	context.description = _("Manage and organize templates for reports, components, and pages")

	# Add any additional context data
	context.template_types = [
		"Report", "Component", "Page", "Email", "Base", "Utility"
	]

	context.categories = [
		"Audit Report", "Compliance", "Risk Assessment", "Dashboard",
		"Form", "Email Notification", "Print Template", "API Response"
	]

	# Get template statistics
	context.stats = get_template_stats()

def get_template_stats():
	"""Get template statistics for dashboard"""
	try:
		stats = frappe.db.sql("""
			SELECT
				COUNT(*) as total_templates,
				SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_templates,
				SUM(CASE WHEN is_default = 1 THEN 1 ELSE 0 END) as default_templates,
				SUM(usage_count) as total_usage
			FROM `tabTemplate Registry`
		""", as_dict=True)[0]

		# Get templates by type
		type_stats = frappe.db.sql("""
			SELECT template_type, COUNT(*) as count
			FROM `tabTemplate Registry`
			WHERE is_active = 1
			GROUP BY template_type
		""", as_dict=True)

		stats.type_breakdown = type_stats

		return stats
	except Exception:
		return {
			"total_templates": 0,
			"active_templates": 0,
			"default_templates": 0,
			"total_usage": 0,
			"type_breakdown": []
		}