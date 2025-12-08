# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, get_datetime
import json
import os

class TemplateRegistry(Document):
	def autoname(self):
		if not self.template_id:
			# Generate template ID in format TPL-YYYY-####
			current_year = get_datetime().year

			last_template = frappe.db.sql("""
				SELECT template_id FROM `tabTemplate Registry`
				WHERE template_id LIKE 'TPL-{}-%'
				ORDER BY CAST(SUBSTRING_INDEX(template_id, '-', -1) AS UNSIGNED) DESC
				LIMIT 1
			""".format(current_year), as_dict=True)

			if last_template:
				last_num = int(last_template[0].template_id.split('-')[-1])
				next_num = last_num + 1
			else:
				next_num = 1

			self.template_id = f"TPL-{current_year}-{next_num:04d}"

	def validate(self):
		self.validate_template_content()
		self.validate_template_config()
		self.validate_default_template()
		self.set_audit_fields()

	def validate_template_content(self):
		"""Validate template content based on template engine"""
		if not self.template_content and not self.file_path:
			frappe.throw(_("Either Template Content or File Path must be provided"))

		if self.template_content and self.file_path:
			frappe.throw(_("Cannot specify both Template Content and File Path"))

		if self.template_engine == "Jinja2" and self.template_content:
			# Basic Jinja2 validation
			try:
				from jinja2 import Template
				Template(self.template_content)
			except Exception as e:
				frappe.throw(_("Invalid Jinja2 template syntax: {0}").format(str(e)))

	def validate_template_config(self):
		"""Validate template configuration JSON"""
		if self.template_config:
			try:
				config = json.loads(self.template_config)
				# Validate required config structure
				if not isinstance(config, dict):
					frappe.throw(_("Template configuration must be a valid JSON object"))
			except json.JSONDecodeError:
				frappe.throw(_("Invalid JSON in template configuration"))

	def validate_default_template(self):
		"""Validate default template logic - allow multiple defaults, on_update will handle clearing others"""
		# This validation is now handled in on_update to allow proper default switching
		pass

	def set_audit_fields(self):
		"""Set audit trail fields"""
		if not self.created_by:
			self.created_by = frappe.session.user
		if not self.creation_date:
			self.creation_date = now()

		self.modified_by = frappe.session.user
		self.last_modified = get_datetime()

	def on_update(self):
		"""Handle template updates"""
		if self.has_value_changed("is_default") and self.is_default:
			# Clear default flag from other templates of same type/category
			frappe.db.sql("""
				UPDATE `tabTemplate Registry`
				SET is_default = 0
				WHERE template_type = %s AND category = %s AND name != %s
			""", (self.template_type, self.category, self.name))

		# Create version if content has changed and versioning is enabled
		if self.should_create_version():
			self.create_version()

	def should_create_version(self):
		"""Check if a version should be created for this update"""
		# Only create versions for content/config changes, not metadata changes
		content_changed = self.has_value_changed("template_content")
		config_changed = self.has_value_changed("template_config")
		engine_changed = self.has_value_changed("template_engine")
		file_changed = self.has_value_changed("file_path")

		return content_changed or config_changed or engine_changed or file_changed

	def create_version(self):
		"""Create a new version for this template"""
		try:
			from mkaguzi.mkaguzi.core.doctype.template_version.template_version import create_new_version

			# Determine change type based on what changed
			change_type = "Minor Update"
			if self.has_value_changed("template_engine"):
				change_type = "Major Update"
			elif self.has_value_changed("template_content"):
				change_type = "Minor Update"
			else:
				change_type = "Bug Fix"

			# Generate change summary
			changes = []
			if self.has_value_changed("template_content"):
				changes.append("content")
			if self.has_value_changed("template_config"):
				changes.append("configuration")
			if self.has_value_changed("template_engine"):
				changes.append("engine")
			if self.has_value_changed("file_path"):
				changes.append("file path")

			change_summary = f"Updated {', '.join(changes)}"

			# Create the version
			version_name = create_new_version(
				self.name,
				change_summary,
				change_type,
				f"Auto-generated v{self.get_next_version_number()}"
			)

			frappe.msgprint(_("New version created: {0}").format(version_name))

		except Exception as e:
			# Log error but don't fail the template update
			frappe.log_error(f"Failed to create template version: {str(e)}", "Template Registry")

	def get_next_version_number(self):
		"""Get the next version number for this template"""
		max_version = frappe.db.sql("""
			SELECT MAX(version_number) as max_version
			FROM `tabTemplate Version`
			WHERE template = %s
		""", self.name, as_dict=True)

		return (max_version[0].max_version or 0) + 1

@frappe.whitelist()
def get_template_content(template_name):
	"""Get template content for rendering"""
	template = frappe.get_doc("Template Registry", template_name)

	if not template.is_active:
		frappe.throw(_("Template is not active"))

	content = template.template_content

	# If file path is specified, read from file
	if template.file_path and not content:
		template_dir = os.path.join(frappe.get_app_path("mkaguzi"), "templates")
		file_path = os.path.join(template_dir, template.file_path)

		if os.path.exists(file_path):
			with open(file_path, 'r') as f:
				content = f.read()
		else:
			frappe.throw(_("Template file not found: {0}").format(file_path))

	return {
		"content": content,
		"engine": template.template_engine,
		"config": json.loads(template.template_config) if template.template_config else {}
	}

@frappe.whitelist()
def get_default_template(template_type, category=None):
	"""Get the default template for a given type and category"""
	filters = {
		"template_type": template_type,
		"is_default": 1,
		"is_active": 1
	}

	if category:
		filters["category"] = category

	template = frappe.get_all("Template Registry",
		filters=filters,
		fields=["name", "template_name", "template_id"],
		limit=1
	)

	if template:
		return template[0]
	else:
		# Return first active template if no default
		template = frappe.get_all("Template Registry",
			filters={
				"template_type": template_type,
				"is_active": 1
			},
			fields=["name", "template_name", "template_id"],
			order_by="modified desc",
			limit=1
		)
		return template[0] if template else None

@frappe.whitelist()
def get_templates_by_category(template_type=None, category=None):
	"""Get templates filtered by type and category"""
	filters = {"is_active": 1}

	if template_type:
		filters["template_type"] = template_type
	if category:
		filters["category"] = category

	templates = frappe.get_all("Template Registry",
		filters=filters,
		fields=["name", "template_name", "template_type", "category", "description", "is_default", "usage_count"],
		order_by="is_default desc, usage_count desc, modified desc"
	)

	return templates

@frappe.whitelist()
def create_default_templates():
	"""Create default templates for common use cases"""
	default_templates = [
		{
			"template_name": "Standard Audit Report",
			"template_type": "Report",
			"category": "Audit Report",
			"description": "Standard audit report template with executive summary, findings, and recommendations",
			"template_engine": "Jinja2",
			"is_default": 1,
			"template_config": json.dumps({
				"sections": ["header", "executive_summary", "scope", "findings", "recommendations", "footer"],
				"styling": {
					"font_family": "Arial",
					"font_size": "11pt",
					"margins": "1in"
				}
			})
		},
		{
			"template_name": "Compliance Checklist",
			"template_type": "Component",
			"category": "Compliance",
			"description": "Reusable compliance checklist component",
			"template_engine": "Vue",
			"is_default": 1
		},
		{
			"template_name": "Risk Assessment Dashboard",
			"template_type": "Page",
			"category": "Risk Assessment",
			"description": "Risk assessment dashboard page template",
			"template_engine": "Vue",
			"is_default": 1
		}
	]

	created_templates = []

	for template_data in default_templates:
		# Check if template already exists
		existing = frappe.db.exists("Template Registry", {
			"template_name": template_data["template_name"],
			"template_type": template_data["template_type"]
		})

		if not existing:
			template = frappe.new_doc("Template Registry")
			template.update(template_data)
			template.save()
			created_templates.append(template.template_name)
			frappe.msgprint(_("Created default template: {0}").format(template.template_name))

	return {"message": f"Created {len(created_templates)} default templates", "templates": created_templates}

@frappe.whitelist()
def update_template_usage(template_name):
	"""Update usage statistics for a template"""
	template = frappe.get_doc("Template Registry", template_name)
	template.usage_count = (template.usage_count or 0) + 1
	template.last_used = get_datetime()
	template.save()

	return {"usage_count": template.usage_count}

@frappe.whitelist()
def render_template(template_name, context=None, output_format="html"):
	"""Render a template with given context"""
	try:
		template = frappe.get_doc("Template Registry", template_name)

		if not template.is_active:
			frappe.throw(_("Template is not active"))

		# Get template content
		content = template.template_content
		if template.file_path and not content:
			template_dir = os.path.join(frappe.get_app_path("mkaguzi"), "templates")
			file_path = os.path.join(template_dir, template.file_path)

			if os.path.exists(file_path):
				with open(file_path, 'r') as f:
					content = f.read()
			else:
				frappe.throw(_("Template file not found: {0}").format(file_path))

		if not content:
			frappe.throw(_("No template content found"))

		# Parse context
		template_context = {}
		if context:
			if isinstance(context, str):
				template_context = json.loads(context)
			else:
				template_context = context

		# Render based on engine
		if template.template_engine == "Jinja2":
			from jinja2 import Template
			jinja_template = Template(content)
			rendered = jinja_template.render(**template_context)
		elif template.template_engine == "Handlebars":
			try:
				import pybars3
				compiler = pybars3.Compiler()
				handlebars_template = compiler.compile(content)
				rendered = handlebars_template(template_context)
			except ImportError:
				frappe.throw(_("Handlebars templating requires pybars3. Please install it with: pip install pybars3"))
		elif template.template_engine == "Vue":
			# For Vue templates, return as-is for frontend rendering
			rendered = content
		else:
			# Plain text
			rendered = content

		# Update usage statistics
		update_template_usage(template_name)

		# Format output
		if output_format == "json":
			return {"content": rendered, "template": template_name, "rendered_at": now()}
		else:
			return rendered

	except Exception as e:
		frappe.log_error(f"Template rendering error: {str(e)}", "Template Registry")
		frappe.throw(_("Error rendering template: {0}").format(str(e)))