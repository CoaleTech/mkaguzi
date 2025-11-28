# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, get_datetime

class ReportTemplate(Document):
	def autoname(self):
		if not self.template_id:
			# Generate template ID in format RT-YYYY-####
			current_year = getdate().year

			last_template = frappe.db.sql("""
				SELECT template_id FROM `tabReport Template`
				WHERE template_id LIKE 'RT-{}-%'
				ORDER BY CAST(SUBSTRING_INDEX(template_id, '-', -1) AS UNSIGNED) DESC
				LIMIT 1
			""".format(current_year), as_dict=True)

			if last_template:
				last_num = int(last_template[0].template_id.split('-')[-1])
				next_num = last_num + 1
			else:
				next_num = 1

			self.template_id = f"RT-{current_year}-{next_num:04d}"

	def validate(self):
		self.validate_default_template()
		self.set_audit_fields()

	def validate_default_template(self):
		"""Ensure only one default template per type"""
		if self.is_default:
			existing_default = frappe.db.exists("Report Template", {
				"template_type": self.template_type,
				"is_default": 1,
				"name": ["!=", self.name]
			})

			if existing_default:
				frappe.throw(_("A default template already exists for {0}. Please uncheck 'Is Default Template' for the existing template first.").format(self.template_type))

	def set_audit_fields(self):
		"""Set audit trail fields"""
		if not self.created_by:
			self.created_by = frappe.session.user
		if not self.creation_date:
			self.creation_date = getdate()

		self.modified_by = frappe.session.user
		self.last_modified = get_datetime()

	def on_update(self):
		"""Handle template updates"""
		if self.has_value_changed("is_default") and self.is_default:
			# Clear default flag from other templates of same type
			frappe.db.sql("""
				UPDATE `tabReport Template`
				SET is_default = 0
				WHERE template_type = %s AND name != %s
			""", (self.template_type, self.name))

@frappe.whitelist()
def get_default_template(template_type):
	"""Get the default template for a given type"""
	template = frappe.get_all("Report Template",
		filters={
			"template_type": template_type,
			"is_default": 1,
			"is_active": 1
		},
		fields=["name", "template_name"]
	)

	if template:
		return template[0]
	else:
		# Return first active template if no default
		template = frappe.get_all("Report Template",
			filters={
				"template_type": template_type,
				"is_active": 1
			},
			fields=["name", "template_name"],
			limit=1
		)
		return template[0] if template else None

@frappe.whitelist()
def get_template_config(template_name):
	"""Get template configuration for report generation"""
	template = frappe.get_doc("Report Template", template_name)

	config = {
		"header": {
			"include_header": template.header_section,
			"logo": template.logo_attachment,
			"company_name": template.company_name,
			"title_format": template.report_title_format,
			"background_color": template.header_background_color,
			"text_color": template.header_text_color,
			"font_size": template.header_font_size
		},
		"body": {
			"font_family": template.font_family,
			"font_size": template.font_size,
			"line_height": template.line_height,
			"margins": template.page_margins,
			"orientation": template.page_orientation,
			"paper_size": template.paper_size
		},
		"content": {
			"executive_summary": template.include_executive_summary,
			"background": template.include_background,
			"scope": template.include_audit_scope,
			"objectives": template.include_audit_objectives,
			"findings_summary": template.include_findings_summary,
			"detailed_findings": template.include_detailed_findings,
			"recommendations": template.include_recommendations,
			"appendices": template.include_appendices
		},
		"styling": {
			"table_border": template.table_border_style,
			"table_header_bg": template.table_header_background,
			"alternate_rows": template.table_alternate_rows,
			"critical_highlight": template.highlight_critical_findings,
			"high_highlight": template.highlight_high_findings,
			"medium_highlight": template.highlight_medium_findings
		},
		"footer": {
			"include_footer": template.footer_section,
			"text": template.footer_text,
			"page_numbering": template.page_numbering,
			"font_size": template.footer_font_size,
			"alignment": template.footer_alignment
		}
	}

	return config

@frappe.whitelist()
def create_default_templates():
	"""Create default report templates for each type"""
	template_types = [
		"Full Audit Report",
		"Executive Summary",
		"Management Report",
		"Board Report",
		"Compliance Report"
	]

	for template_type in template_types:
		# Check if default template already exists
		existing = frappe.db.exists("Report Template", {
			"template_type": template_type,
			"is_default": 1
		})

		if not existing:
			template = frappe.new_doc("Report Template")
			template.template_name = f"Default {template_type}"
			template.template_type = template_type
			template.description = f"Default template for {template_type.lower()}"
			template.is_default = 1
			template.is_active = 1

			# Set type-specific defaults
			if template_type == "Executive Summary":
				template.include_detailed_findings = 0
				template.include_appendices = 0
				template.page_orientation = "Landscape"
			elif template_type == "Board Report":
				template.header_background_color = "#2E4057"
				template.header_text_color = "#FFFFFF"
				template.highlight_critical_findings = "#DC143C"
			elif template_type == "Compliance Report":
				template.template_name = "Default Compliance Report"
				template.include_executive_summary = 0
				template.include_background = 0

			template.save()
			frappe.msgprint(_("Created default template: {0}").format(template.template_name))

	return {"message": "Default templates created successfully"}