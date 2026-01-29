# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

class TestEnvironmentalAudit(FrappeTestCase):
	def test_audit_id_generation(self):
		"""Test automatic audit ID generation"""
		audit = frappe.get_doc({
			"doctype": "Environmental Audit",
			"audit_title": "Test Environmental Audit",
			"audit_type": "ESG Assessment",
			"start_date": "2025-01-01"
		})
		audit.insert()
		self.assertTrue(audit.audit_id.startswith("ENV-2025-"))

	def test_esg_score_calculation(self):
		"""Test ESG score calculation based on sustainability rating"""
		audit = frappe.get_doc({
			"doctype": "Environmental Audit",
			"audit_title": "Test ESG Audit",
			"audit_type": "ESG Assessment",
			"sustainability_rating": "Good",
			"start_date": "2025-01-01"
		})
		audit.insert()
		self.assertEqual(audit.esg_score, 75)

	def test_compliance_status_auto_set(self):
		"""Test compliance status is set based on ESG score"""
		audit = frappe.get_doc({
			"doctype": "Environmental Audit",
			"audit_title": "Test Compliance",
			"audit_type": "Environmental Compliance",
			"esg_score": 85,
			"start_date": "2025-01-01"
		})
		audit.insert()
		self.assertEqual(audit.compliance_status, "Mostly Compliant")

	def test_carbon_footprint_summary(self):
		"""Test carbon footprint summary function"""
		from mkaguzi.mkaguzi.audit.doctype.environmental_audit.environmental_audit import get_carbon_footprint_summary

		# Create test audit with metrics
		audit = frappe.get_doc({
			"doctype": "Environmental Audit",
			"audit_title": "Carbon Test",
			"audit_type": "Carbon Footprint Audit",
			"carbon_emissions": 100,
			"energy_consumption": 5000,
			"start_date": "2025-01-01"
		})
		audit.insert()

		summary = get_carbon_footprint_summary(2025)
		self.assertGreater(summary["total_carbon_emissions"], 0)
