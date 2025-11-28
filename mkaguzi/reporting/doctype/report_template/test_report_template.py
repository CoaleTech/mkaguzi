# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

import frappe
import unittest

class TestReportTemplate(unittest.TestCase):
	def setUp(self):
		# Clean up any existing test templates
		frappe.db.rollback()

	def tearDown(self):
		# Clean up test data
		frappe.db.rollback()

	def test_template_creation(self):
		"""Test report template creation"""
		template = frappe.new_doc("Report Template")
		template.template_name = "Test Full Audit Report Template"
		template.template_type = "Full Audit Report"
		template.description = "Test template for full audit reports"
		template.is_default = 0
		template.is_active = 1

		template.insert()

		# Check if template_id was auto-generated
		self.assertTrue(template.template_id.startswith("RT-"))
		self.assertTrue(template.template_id.endswith("-0001"))

		# Check audit fields
		self.assertEqual(template.created_by, "Administrator")
		self.assertIsNotNone(template.creation_date)

	def test_default_template_validation(self):
		"""Test default template validation"""
		# Create first default template
		template1 = frappe.new_doc("Report Template")
		template1.template_name = "Default Template 1"
		template1.template_type = "Full Audit Report"
		template1.is_default = 1
		template1.is_active = 1
		template1.insert()

		# Try to create second default template for same type
		template2 = frappe.new_doc("Report Template")
		template2.template_name = "Default Template 2"
		template2.template_type = "Full Audit Report"
		template2.is_default = 1
		template2.is_active = 1

		with self.assertRaises(frappe.ValidationError):
			template2.insert()

	def test_get_default_template_function(self):
		"""Test the get_default_template whitelisted function"""
		# Create a default template
		template = frappe.new_doc("Report Template")
		template.template_name = "Default Test Template"
		template.template_type = "Executive Summary"
		template.is_default = 1
		template.is_active = 1
		template.insert()

		# Test getting default template
		result = frappe.call("mkaguzi.doctype.report_template.report_template.get_default_template",
							template_type="Executive Summary")

		self.assertEqual(result["name"], template.name)
		self.assertEqual(result["template_name"], "Default Test Template")

	def test_get_template_config_function(self):
		"""Test the get_template_config whitelisted function"""
		template = frappe.new_doc("Report Template")
		template.template_name = "Config Test Template"
		template.template_type = "Full Audit Report"
		template.font_family = "Arial"
		template.font_size = "12pt"
		template.header_background_color = "#FFFFFF"
		template.table_border_style = "Standard"
		template.footer_text = "Test Footer"
		template.insert()

		config = frappe.call("mkaguzi.doctype.report_template.report_template.get_template_config",
							template_name=template.name)

		self.assertEqual(config["body"]["font_family"], "Arial")
		self.assertEqual(config["body"]["font_size"], "12pt")
		self.assertEqual(config["header"]["background_color"], "#FFFFFF")
		self.assertEqual(config["styling"]["table_border"], "Standard")
		self.assertEqual(config["footer"]["text"], "Test Footer")

	def test_create_default_templates_function(self):
		"""Test the create_default_templates whitelisted function"""
		result = frappe.call("mkaguzi.doctype.report_template.report_template.create_default_templates")

		self.assertEqual(result["message"], "Default templates created successfully")

		# Check if templates were created
		templates = frappe.get_all("Report Template", filters={"is_default": 1})
		self.assertTrue(len(templates) > 0)

		# Check specific template types
		template_types = ["Full Audit Report", "Executive Summary", "Management Report",
						 "Board Report", "Compliance Report"]
		for template_type in template_types:
			template = frappe.get_all("Report Template",
				filters={"template_type": template_type, "is_default": 1})
			self.assertTrue(len(template) > 0)

	def test_template_update_default_flag(self):
		"""Test updating default flag clears other defaults"""
		# Create two templates of same type
		template1 = frappe.new_doc("Report Template")
		template1.template_name = "Template 1"
		template1.template_type = "Management Report"
		template1.is_default = 0
		template1.insert()

		template2 = frappe.new_doc("Report Template")
		template2.template_name = "Template 2"
		template2.template_type = "Management Report"
		template2.is_default = 0
		template2.insert()

		# Make template2 default
		template2.is_default = 1
		template2.save()

		# Check that template1 is no longer default
		template1.reload()
		self.assertEqual(template1.is_default, 0)
		self.assertEqual(template2.is_default, 1)