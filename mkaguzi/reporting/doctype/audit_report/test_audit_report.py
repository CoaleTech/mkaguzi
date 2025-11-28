# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import getdate, add_days

class TestAuditReport(unittest.TestCase):
	def setUp(self):
		# Create test data
		self.create_test_engagement()
		self.create_test_findings()

	def tearDown(self):
		# Clean up test data
		frappe.db.rollback()

	def create_test_engagement(self):
		"""Create a test audit engagement"""
		if not frappe.db.exists("Audit Engagement", "TEST-ENG-001"):
			engagement = frappe.new_doc("Audit Engagement")
			engagement.engagement_id = "TEST-ENG-001"
			engagement.engagement_title = "Test Audit Engagement"
			engagement.audit_universe = "Test Department"
			engagement.start_date = getdate()
			engagement.end_date = add_days(getdate(), 30)
			engagement.audit_scope = "Test audit scope"
			engagement.audit_objectives = "Test audit objectives"
			engagement.engagement_status = "In Progress"
			engagement.save()
			self.engagement_name = engagement.name

	def create_test_findings(self):
		"""Create test audit findings"""
		if not frappe.db.exists("Audit Finding", "TEST-FIND-001"):
			finding = frappe.new_doc("Audit Finding")
			finding.finding_id = "TEST-FIND-001"
			finding.finding_title = "Test Critical Finding"
			finding.engagement_reference = self.engagement_name
			finding.risk_rating = "Critical"
			finding.condition = "Test condition"
			finding.criteria = "Test criteria"
			finding.cause = "Test cause"
			finding.effect = "Test effect"
			finding.recommendation = "Test recommendation"
			finding.management_comments = "Test management response"
			finding.action_plan_description = "Test action plan"
			finding.target_completion_date = add_days(getdate(), 60)
			finding.save()

	def test_report_creation(self):
		"""Test audit report creation"""
		report = frappe.new_doc("Audit Report")
		report.engagement_reference = self.engagement_name
		report.report_title = "Test Audit Report"
		report.report_type = "Full Audit Report"
		report.report_date = getdate()
		report.report_period = f"{getdate()} to {add_days(getdate(), 30)}"
		report.report_status = "Draft"
		report.prepared_by = "Administrator"
		report.preparation_date = getdate()

		report.insert()

		# Check if report_id was auto-generated
		self.assertTrue(report.report_id.startswith("AR-"))
		self.assertTrue(report.report_id.endswith("-0001"))

		# Check if findings were populated
		self.assertTrue(len(report.key_findings_summary) > 0)
		self.assertTrue(len(report.detailed_findings) > 0)

	def test_date_validation(self):
		"""Test date validation logic"""
		report = frappe.new_doc("Audit Report")
		report.engagement_reference = self.engagement_name
		report.report_title = "Test Audit Report"
		report.report_type = "Full Audit Report"
		report.report_date = getdate()
		report.preparation_date = add_days(getdate(), 1)  # Preparation after report date
		report.report_status = "Draft"

		with self.assertRaises(frappe.ValidationError):
			report.insert()

	def test_version_control(self):
		"""Test version control functionality"""
		report = frappe.new_doc("Audit Report")
		report.engagement_reference = self.engagement_name
		report.report_title = "Test Audit Report"
		report.report_type = "Full Audit Report"
		report.report_date = getdate()
		report.report_status = "Draft"
		report.insert()

		# Check initial version
		self.assertEqual(report.version_number, 1.0)

		# Update status and check version increment
		report.report_status = "Under Review"
		report.save()

		self.assertEqual(report.version_number, 1.1)
		self.assertTrue(len(report.revision_history) > 0)

	def test_create_audit_report_function(self):
		"""Test the create_audit_report whitelisted function"""
		report = frappe.call("mkaguzi.doctype.audit_report.audit_report.create_audit_report",
							engagement_name=self.engagement_name)

		self.assertEqual(report.engagement_reference, self.engagement_name)
		self.assertEqual(report.report_type, "Full Audit Report")
		self.assertEqual(report.report_status, "Draft")

	def test_get_report_summary_function(self):
		"""Test the get_report_summary whitelisted function"""
		report = frappe.new_doc("Audit Report")
		report.engagement_reference = self.engagement_name
		report.report_title = "Test Audit Report"
		report.report_type = "Full Audit Report"
		report.report_date = getdate()
		report.report_status = "Draft"
		report.insert()

		summary = frappe.call("mkaguzi.doctype.audit_report.audit_report.get_report_summary",
							 report_name=report.name)

		self.assertEqual(summary["report_id"], report.report_id)
		self.assertEqual(summary["engagement"], self.engagement_name)
		self.assertEqual(summary["status"], "Draft")
		self.assertTrue("total_findings" in summary)
		self.assertTrue("critical_findings" in summary)