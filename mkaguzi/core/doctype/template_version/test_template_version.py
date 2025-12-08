# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

import unittest
import frappe
from frappe.tests.utils import FrappeTestCase
from mkaguzi.mkaguzi.core.doctype.template_registry.template_registry import create_default_templates

class TestTemplateVersion(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		# Create a test template
		if not frappe.db.exists("Template Registry", "TEST-TEMPLATE-001"):
			template = frappe.new_doc("Template Registry")
			template.template_name = "Test Template"
			template.template_type = "Report"
			template.category = "Test"
			template.template_content = "<h1>Test Template</h1>{{ content }}"
			template.template_config = '{"test": true}'
			template.template_engine = "Jinja2"
			template.is_active = True
			template.save()

	def tearDown(self):
		"""Clean up test data"""
		# Clean up test templates and versions
		frappe.db.sql("DELETE FROM `tabTemplate Version` WHERE template LIKE 'TEST-%'")
		frappe.db.sql("DELETE FROM `tabTemplate Registry` WHERE template_id LIKE 'TEST-%'")

	def test_version_creation(self):
		"""Test creating a new template version"""
		template = frappe.get_doc("Template Registry", {"template_name": "Test Template"})

		# Create first version
		version = frappe.new_doc("Template Version")
		version.template = template.name
		version.change_summary = "Initial version"
		version.change_type = "Initial Version"
		version.version_name = "v1.0"
		version.template_content = template.template_content
		version.template_config = template.template_config
		version.template_engine = template.template_engine
		version.is_current = True
		version.save()

		self.assertEqual(version.version_number, 1)
		self.assertEqual(version.is_current, True)
		self.assertEqual(version.validation_status, "Valid")

	def test_version_numbering(self):
		"""Test automatic version numbering"""
		template = frappe.get_doc("Template Registry", {"template_name": "Test Template"})

		# Create multiple versions
		for i in range(1, 4):
			version = frappe.new_doc("Template Version")
			version.template = template.name
			version.change_summary = f"Version {i}"
			version.change_type = "Minor Update"
			version.version_name = f"v{i}.0"
			version.template_content = f"<h1>Version {i}</h1>{{ content }}"
			version.template_engine = "Jinja2"
			version.is_current = (i == 3)  # Last one is current
			version.save()

			self.assertEqual(version.version_number, i)

	def test_current_version_uniqueness(self):
		"""Test that only one version can be current"""
		template = frappe.get_doc("Template Registry", {"template_name": "Test Template"})

		# Create first current version
		v1 = frappe.new_doc("Template Version")
		v1.template = template.name
		v1.change_summary = "Version 1"
		v1.change_type = "Initial Version"
		v1.version_name = "v1.0"
		v1.template_content = template.template_content
		v1.template_engine = "Jinja2"
		v1.is_current = True
		v1.save()

		# Try to create another current version
		v2 = frappe.new_doc("Template Version")
		v2.template = template.name
		v2.change_summary = "Version 2"
		v2.change_type = "Minor Update"
		v2.version_name = "v2.0"
		v2.template_content = "<h1>Version 2</h1>{{ content }}"
		v2.template_engine = "Jinja2"
		v2.is_current = True

		# This should work and automatically unset v1's current flag
		v2.save()

		# Refresh v1 and check
		v1.reload()
		self.assertEqual(v1.is_current, False)
		self.assertEqual(v2.is_current, True)

	def test_validation(self):
		"""Test template validation"""
		template = frappe.get_doc("Template Registry", {"template_name": "Test Template"})

		# Valid Jinja2 template
		version = frappe.new_doc("Template Version")
		version.template = template.name
		version.change_summary = "Valid template"
		version.change_type = "Minor Update"
		version.version_name = "valid-v1"
		version.template_content = "<h1>Valid</h1>{{ content }}"
		version.template_engine = "Jinja2"
		version.save()

		self.assertEqual(version.validation_status, "Valid")

		# Invalid Jinja2 template
		version_invalid = frappe.new_doc("Template Version")
		version_invalid.template = template.name
		version_invalid.change_summary = "Invalid template"
		version_invalid.change_type = "Minor Update"
		version_invalid.version_name = "invalid-v1"
		version_invalid.template_content = "<h1>Invalid</h1>{{ content"  # Missing closing braces
		version_invalid.template_engine = "Jinja2"
		version_invalid.save()

		self.assertEqual(version_invalid.validation_status, "Invalid")
		self.assertIn("unexpected end of template", version_invalid.validation_errors)

	def test_create_new_version_api(self):
		"""Test the create_new_version API function"""
		template = frappe.get_doc("Template Registry", {"template_name": "Test Template"})

		# Create new version via API
		version_name = frappe.call(
			"mkaguzi.mkaguzi.core.doctype.template_version.template_version.create_new_version",
			template_name=template.name,
			change_summary="API created version",
			change_type="Major Update",
			version_name="api-v1"
		)

		version = frappe.get_doc("Template Version", version_name)
		self.assertEqual(version.change_summary, "API created version")
		self.assertEqual(version.change_type, "Major Update")
		self.assertEqual(version.version_name, "api-v1")
		self.assertEqual(version.is_current, True)

	def test_version_history(self):
		"""Test getting version history"""
		template = frappe.get_doc("Template Registry", {"template_name": "Test Template"})

		# Create a few versions
		for i in range(1, 4):
			frappe.call(
				"mkaguzi.mkaguzi.core.doctype.template_version.template_version.create_new_version",
				template_name=template.name,
				change_summary=f"Version {i}",
				change_type="Minor Update",
				version_name=f"v{i}.0"
			)

		# Get version history
		history = frappe.call(
			"mkaguzi.mkaguzi.core.doctype.template_version.template_version.get_version_history",
			template_name=template.name
		)

		self.assertEqual(len(history), 3)
		# Should be ordered by version number descending
		self.assertEqual(history[0]["version_number"], 3)
		self.assertEqual(history[2]["version_number"], 1)

	def test_rollback_functionality(self):
		"""Test rollback to previous version"""
		template = frappe.get_doc("Template Registry", {"template_name": "Test Template"})

		# Create version 1
		v1_name = frappe.call(
			"mkaguzi.mkaguzi.core.doctype.template_version.template_version.create_new_version",
			template_name=template.name,
			change_summary="Version 1",
			change_type="Initial Version",
			version_name="v1.0"
		)

		v1 = frappe.get_doc("Template Version", v1_name)

		# Create version 2
		v2_name = frappe.call(
			"mkaguzi.mkaguzi.core.doctype.template_version.template_version.create_new_version",
			template_name=template.name,
			change_summary="Version 2",
			change_type="Major Update",
			version_name="v2.0"
		)

		# Mark v1 as available for rollback
		frappe.call(
			"mkaguzi.mkaguzi.core.doctype.template_version.template_version.mark_version_for_rollback",
			version_name=v1_name,
			available=True
		)

		# Rollback to v1
		rollback_version_name = frappe.call(
			"mkaguzi.mkaguzi.core.doctype.template_version.template_version.rollback_to_version",
			version_name=v1_name,
			reason="Testing rollback"
		)

		rollback_version = frappe.get_doc("Template Version", rollback_version_name)
		self.assertEqual(rollback_version.change_type, "Rollback")
		self.assertIn("Rolled back to version 1", rollback_version.change_summary)
		self.assertEqual(rollback_version.is_current, True)