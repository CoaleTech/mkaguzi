# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def get_context(context):
	"""Setup context for template marketplace page"""
	context.no_cache = 1

	# Check permissions
	if not frappe.has_permission("Template Marketplace", "read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	# Add page metadata
	context.title = _("Template Marketplace")
	context.description = _("Discover, share, and import templates from the community")

	# Add any additional context data
	context.template_types = [
		"Report", "Component", "Page", "Email", "Base", "Utility"
	]

	context.categories = [
		"Audit Report", "Compliance", "Risk Assessment", "Dashboard",
		"Form", "Email Notification", "Print Template", "API Response"
	]

	# Get marketplace statistics
	context.stats = get_marketplace_stats()

def get_marketplace_stats():
	"""Get marketplace statistics for dashboard"""
	try:
		stats = frappe.db.sql("""
			SELECT
				COUNT(*) as total_templates,
				SUM(CASE WHEN status = 'Published' THEN 1 ELSE 0 END) as published_templates,
				SUM(CASE WHEN is_featured = 1 THEN 1 ELSE 0 END) as featured_templates,
				SUM(download_count) as total_downloads,
				AVG(rating) as avg_rating
			FROM `tabTemplate Marketplace`
			WHERE is_public = 1
		""", as_dict=True)[0]

		# Get templates by type
		type_stats = frappe.db.sql("""
			SELECT template_type, COUNT(*) as count
			FROM `tabTemplate Marketplace`
			WHERE status = 'Published' AND is_public = 1
			GROUP BY template_type
		""", as_dict=True)

		stats.type_breakdown = type_stats

		return stats
	except Exception:
		return {
			"total_templates": 0,
			"published_templates": 0,
			"featured_templates": 0,
			"total_downloads": 0,
			"avg_rating": 0,
			"type_breakdown": []
		}