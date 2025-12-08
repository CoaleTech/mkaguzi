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

class TemplateVersion(Document):
	def autoname(self):
		"""Generate name as TemplateID-VersionNumber"""
		if self.template and self.version_number:
			template_id = frappe.get_value("Template Registry", self.template, "template_id")
			self.name = f"{template_id}-v{self.version_number}"

	def validate(self):
		self.validate_template_reference()
		self.validate_version_number()
		self.validate_content()
		self.set_audit_fields()
		self.validate_uniqueness()

	def validate_template_reference(self):
		"""Ensure template exists and is valid"""
		if not frappe.db.exists("Template Registry", self.template):
			frappe.throw(_("Invalid template reference"))

	def validate_version_number(self):
		"""Ensure version number is sequential"""
		if self.version_number <= 0:
			frappe.throw(_("Version number must be greater than 0"))

		# Check if version number already exists for this template
		existing = frappe.db.exists("Template Version", {
			"template": self.template,
			"version_number": self.version_number,
			"name": ["!=", self.name]
		})

		if existing:
			frappe.throw(_("Version {0} already exists for this template").format(self.version_number))

	def validate_content(self):
		"""Validate template content based on engine"""
		if self.template_engine == "Jinja2" and self.template_content:
			try:
				from jinja2 import Template
				Template(self.template_content)
				self.validation_status = "Valid"
				self.validation_errors = ""
			except Exception as e:
				self.validation_status = "Invalid"
				self.validation_errors = str(e)
		else:
			self.validation_status = "Valid"
			self.validation_errors = ""

	def validate_uniqueness(self):
		"""Ensure only one current version per template"""
		if self.is_current:
			existing_current = frappe.db.exists("Template Version", {
				"template": self.template,
				"is_current": 1,
				"name": ["!=", self.name]
			})

			if existing_current:
				frappe.throw(_("Another version is already marked as current for this template"))

	def set_audit_fields(self):
		"""Set audit trail fields"""
		if not self.created_by:
			self.created_by = frappe.session.user
		if not self.creation_date:
			self.creation_date = now()

	def before_save(self):
		"""Handle version creation logic"""
		if self.is_new():
			self.set_next_version_number()

	def set_next_version_number(self):
		"""Set the next version number for the template"""
		if not self.version_number:
			max_version = frappe.db.sql("""
				SELECT MAX(version_number) as max_version
				FROM `tabTemplate Version`
				WHERE template = %s
			""", self.template, as_dict=True)

			self.version_number = (max_version[0].max_version or 0) + 1

	def on_update(self):
		"""Handle version updates"""
		if self.has_value_changed("is_current") and self.is_current:
			# Clear current flag from other versions
			frappe.db.sql("""
				UPDATE `tabTemplate Version`
				SET is_current = 0
				WHERE template = %s AND name != %s
			""", (self.template, self.name))

			# Update the template registry with this version's content
			self.update_template_registry()

	def update_template_registry(self):
		"""Update the parent template with this version's content"""
		template = frappe.get_doc("Template Registry", self.template)
		template.template_content = self.template_content
		template.template_config = self.template_config
		template.file_path = self.file_path
		template.template_engine = self.template_engine
		template.save()

@frappe.whitelist()
def create_new_version(template_name, change_summary, change_type="Minor Update", version_name=None):
	"""Create a new version of a template"""
	template = frappe.get_doc("Template Registry", template_name)

	# Get current version
	current_version = frappe.get_all("Template Version",
		filters={"template": template_name, "is_current": 1},
		fields=["name", "version_number"],
		limit=1
	)

	previous_version = current_version[0].name if current_version else None

	# Create new version
	version = frappe.new_doc("Template Version")
	version.template = template_name
	version.change_summary = change_summary
	version.change_type = change_type
	version.version_name = version_name or f"Version {get_next_version_number(template_name)}"
	version.template_content = template.template_content
	version.template_config = template.template_config
	version.file_path = template.file_path
	version.template_engine = template.template_engine
	version.previous_version = previous_version
	version.is_current = True

	version.save()

	return version.name

@frappe.whitelist()
def rollback_to_version(version_name, reason="Manual rollback"):
	"""Rollback template to a specific version"""
	version = frappe.get_doc("Template Version", version_name)

	if not version.rollback_available:
		frappe.throw(_("This version is not available for rollback"))

	# Create a new version with rollback change
	new_version = create_new_version(
		version.template,
		f"Rolled back to version {version.version_number}: {reason}",
		"Rollback",
		f"Rollback to v{version.version_number}"
	)

	# Update the new version with the old content
	new_version_doc = frappe.get_doc("Template Version", new_version)
	new_version_doc.template_content = version.template_content
	new_version_doc.template_config = version.template_config
	new_version_doc.file_path = version.file_path
	new_version_doc.template_engine = version.template_engine
	new_version_doc.save()

	return new_version

@frappe.whitelist()
def get_version_history(template_name, limit=50):
	"""Get version history for a template"""
	versions = frappe.get_all("Template Version",
		filters={"template": template_name},
		fields=[
			"name", "version_number", "version_name", "change_summary",
			"change_type", "created_by", "creation_date", "is_current",
			"validation_status", "rollback_available"
		],
		order_by="version_number desc",
		limit=limit
	)

	return versions

@frappe.whitelist()
def compare_versions(version1, version2):
	"""Compare two template versions"""
	v1 = frappe.get_doc("Template Version", version1)
	v2 = frappe.get_doc("Template Version", version2)

	# Simple diff - in production, you might want to use a proper diff library
	differences = {
		"content_changed": v1.template_content != v2.template_content,
		"config_changed": v1.template_config != v2.template_config,
		"engine_changed": v1.template_engine != v2.template_engine,
		"file_path_changed": v1.file_path != v2.file_path
	}

	return {
		"version1": {
			"name": v1.version_name,
			"number": v1.version_number,
			"date": v1.creation_date
		},
		"version2": {
			"name": v2.version_name,
			"number": v2.version_number,
			"date": v2.creation_date
		},
		"differences": differences,
		"content_diff": generate_content_diff(v1.template_content, v2.template_content) if differences["content_changed"] else None
	}

def generate_content_diff(content1, content2):
	"""Generate a simple content diff"""
	# This is a basic implementation - you might want to use difflib for better diffs
	lines1 = content1.split('\n') if content1 else []
	lines2 = content2.split('\n') if content2 else []

	return {
		"lines_added": len(lines2) - len(lines1),
		"lines_removed": len(lines1) - len(lines2),
		"total_changes": abs(len(lines2) - len(lines1))
	}

def get_next_version_number(template_name):
	"""Get the next version number for a template"""
	max_version = frappe.db.sql("""
		SELECT MAX(version_number) as max_version
		FROM `tabTemplate Version`
		WHERE template = %s
	""", template_name, as_dict=True)

	return (max_version[0].max_version or 0) + 1

@frappe.whitelist()
def mark_version_for_rollback(version_name, available=True):
	"""Mark a version as available/unavailable for rollback"""
	version = frappe.get_doc("Template Version", version_name)
	version.rollback_available = available
	version.save()

	return {"status": "success"}