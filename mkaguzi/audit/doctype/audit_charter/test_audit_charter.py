# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from mkaguzi.mkaguzi.audit.doctype.audit_charter.audit_charter import amend_charter

class TestAuditCharter(FrappeTestCase):
	def test_charter_creation(self):
		"""Test basic charter creation"""
		charter = frappe.get_doc({
			"doctype": "Audit Charter",
			"charter_name": "Test Internal Audit Charter",
			"version": "1.0",
			"effective_date": "2025-01-01",
			"purpose_statement": "To provide independent assurance...",
			"authority_definition": "The audit function has authority...",
			"responsibility_definition": "Responsibilities include...",
			"reporting_structure": "Reports to Audit Committee",
			"cae_name": "Administrator"
		})
		charter.insert()
		self.assertTrue(charter.name)

	def test_version_format_validation(self):
		"""Test version format validation"""
		charter = frappe.get_doc({
			"doctype": "Audit Charter",
			"charter_name": "Test Charter",
			"version": "invalid",
			"effective_date": "2025-01-01",
			"purpose_statement": "Test",
			"authority_definition": "Test",
			"responsibility_definition": "Test",
			"reporting_structure": "Test",
			"cae_name": "Administrator"
		})
		with self.assertRaises(frappe.ValidationError):
			charter.save()

	def test_amend_charter(self):
		"""Test charter amendment creates new version"""
		# Create original charter
		charter = frappe.get_doc({
			"doctype": "Audit Charter",
			"charter_name": "Test Charter",
			"version": "1.0",
			"effective_date": "2025-01-01",
			"purpose_statement": "Test",
			"authority_definition": "Test",
			"responsibility_definition": "Test",
			"reporting_structure": "Test",
			"cae_name": "Administrator",
			"status": "Active"
		})
		charter.insert()

		# Amend charter
		new_charter_name = amend_charter(charter.name)
		new_charter = frappe.get_doc("Audit Charter", new_charter_name)

		self.assertEqual(new_charter.version, "1.1")
		self.assertEqual(new_charter.amended_from, charter.name)

		# Check original is superseded
		original_charter = frappe.get_doc("Audit Charter", charter.name)
		self.assertEqual(original_charter.status, "Superseded")
