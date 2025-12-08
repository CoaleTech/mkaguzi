# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import unittest

class TestTemplateRegistry(unittest.TestCase):
	def setUp(self):
		# Clean up any existing test templates
		frappe.db.sql("DELETE FROM `tabTemplate Registry` WHERE template_name LIKE 'Test%'")

	def tearDown(self):
		# Clean up test templates
		frappe.db.sql("DELETE FROM `tabTemplate Registry` WHERE template_name LIKE 'Test%'")

	def test_template_creation(self):
		"""Test basic template creation"""
		template = frappe.new_doc("Template Registry")
		template.template_name = "Test Template"
		template.template_type = "Report"
		template.category = "Audit Report"
		template.description = "Test template for unit testing"
		template.template_content = "<h1>Test Template</h1>"
		template.template_engine = "Jinja2"

		template.save()

		# Verify template was created
		self.assertEqual(template.template_name, "Test Template")
		self.assertTrue(template.template_id.startswith("TPL-"))
		self.assertEqual(template.is_active, 1)

	def test_default_template_validation(self):
		"""Test that only one default template per type/category is allowed"""
		# Create first default template
		template1 = frappe.new_doc("Template Registry")
		template1.template_name = "Default Test Template 1"
		template1.template_type = "Report"
		template1.category = "Audit Report"
		template1.is_default = 1
		template1.template_content = "<h1>Template 1</h1>"
		template1.save()

		# Try to create second default template - should fail
		template2 = frappe.new_doc("Template Registry")
		template2.template_name = "Default Test Template 2"
		template2.template_type = "Report"
		template2.category = "Audit Report"
		template2.is_default = 1
		template2.template_content = "<h1>Template 2</h1>"

		with self.assertRaises(frappe.ValidationError):
			template2.save()

	def test_template_content_validation(self):
		"""Test template content validation"""
		# Test missing content
		template = frappe.new_doc("Template Registry")
		template.template_name = "Invalid Template"
		template.template_type = "Report"

		with self.assertRaises(frappe.ValidationError):
			template.save()

		# Test invalid Jinja2 syntax
		template.template_content = "{{ unclosed_tag"

		with self.assertRaises(frappe.ValidationError):
			template.save()

	def test_get_default_template(self):
		"""Test getting default template"""
		# Create a default template
		template = frappe.new_doc("Template Registry")
		template.template_name = "Default Report Template"
		template.template_type = "Report"
		template.category = "Audit Report"
		template.is_default = 1
		template.template_content = "<h1>Default Template</h1>"
		template.save()

		# Get default template
		from mkaguzi.core.doctype.template_registry.template_registry import get_default_template
		default_template = get_default_template("Report", "Audit Report")

		self.assertIsNotNone(default_template)
		self.assertEqual(default_template.template_name, "Default Report Template")

	def test_template_usage_tracking(self):
		"""Test template usage tracking"""
		template = frappe.new_doc("Template Registry")
		template.template_name = "Usage Test Template"
		template.template_type = "Report"
		template.template_content = "<h1>Usage Template</h1>"
		template.save()

		initial_usage = template.usage_count or 0

		# Update usage
		from mkaguzi.core.doctype.template_registry.template_registry import update_template_usage
		result = update_template_usage(template.name)

		# Refresh template and check usage
		template.reload()
		self.assertEqual(template.usage_count, initial_usage + 1)
		self.assertIsNotNone(template.last_used)