# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import getdate, add_days

class TestBoardReport(unittest.TestCase):
	def setUp(self):
		# Clean up any existing test reports
		frappe.db.rollback()

	def tearDown(self):
		# Clean up test data
		frappe.db.rollback()

	def test_report_creation(self):
		"""Test board report creation"""
		report = frappe.new_doc("Board Report")
		report.report_title = "Test Board Report Q1 2025"
		report.reporting_period = "Q1"
		report.report_type = "Board Report"
		report.report_status = "Draft"
		report.is_active = 1
		report.executive_summary = "Test executive summary for board report"

		report.insert()

		# Check if report_id was auto-generated
		self.assertTrue(report.report_id.startswith("BR-"))
		self.assertTrue("Q1" in report.report_id)

		# Check audit fields
		self.assertEqual(report.prepared_by, "Administrator")
		self.assertIsNotNone(report.prepared_date)

	def test_date_validation(self):
		"""Test date validation logic"""
		report = frappe.new_doc("Board Report")
		report.report_title = "Test Board Report"
		report.reporting_period = "Q1"
		report.report_type = "Board Report"
		report.report_status = "Draft"
		report.prepared_date = getdate()
		report.review_date = add_days(getdate(), -1)  # Review before preparation

		with self.assertRaises(frappe.ValidationError):
			report.insert()

	def test_quarterly_metrics_calculation(self):
		"""Test quarterly metrics calculation"""
		# Create test data first
		self.create_test_data()

		report = frappe.new_doc("Board Report")
		report.report_title = "Test Metrics Report"
		report.reporting_period = "Q1"
		report.quarterly_metrics = 1
		report.financial_impact = 1

		report.insert()

		# Check if metrics were calculated
		self.assertIsNotNone(report.q1_engagements)
		self.assertIsNotNone(report.q1_findings)
		self.assertIsNotNone(report.potential_savings_identified)

	def create_test_data(self):
		"""Create test data for metrics calculation"""
		# Create test engagement
		if not frappe.db.exists("Audit Engagement", "TEST-BR-ENG-001"):
			engagement = frappe.new_doc("Audit Engagement")
			engagement.engagement_id = "TEST-BR-ENG-001"
			engagement.engagement_title = "Test Board Report Engagement"
			engagement.audit_universe = "Test Department"
			engagement.start_date = getdate()
			engagement.end_date = add_days(getdate(), 30)
			engagement.engagement_status = "Completed"
			engagement.save()

		# Create test finding
		if not frappe.db.exists("Audit Finding", "TEST-BR-FIND-001"):
			finding = frappe.new_doc("Audit Finding")
			finding.finding_id = "TEST-BR-FIND-001"
			finding.finding_title = "Test Board Report Finding"
			finding.engagement_reference = "TEST-BR-ENG-001"
			finding.risk_rating = "Critical"
			finding.save()

		# Create test compliance requirement
		if not frappe.db.exists("Compliance Requirement", "TEST-BR-COMP-001"):
			compliance = frappe.new_doc("Compliance Requirement")
			compliance.requirement_id = "TEST-BR-COMP-001"
			compliance.requirement_title = "Test Board Report Compliance"
			compliance.compliance_status = "Compliant"
			compliance.save()

		# Create test corrective action
		if not frappe.db.exists("Corrective Action Plan", "TEST-BR-ACTION-001"):
			action = frappe.new_doc("Corrective Action Plan")
			action.action_id = "TEST-BR-ACTION-001"
			action.finding_reference = "TEST-BR-FIND-001"
			action.action_description = "Test corrective action"
			action.estimated_savings = 50000
			action.action_status = "Completed"
			action.save()

	def test_status_change_handling(self):
		"""Test status change handling"""
		report = frappe.new_doc("Board Report")
		report.report_title = "Test Status Report"
		report.reporting_period = "Q1"
		report.report_type = "Board Report"
		report.report_status = "Draft"
		report.insert()

		# Change status to Approved
		report.report_status = "Approved"
		report.save()

		# Check if approval fields were set
		self.assertIsNotNone(report.approval_date)
		self.assertEqual(report.approved_by, "Administrator")

	def test_create_quarterly_board_report_function(self):
		"""Test the create_quarterly_board_report whitelisted function"""
		report = frappe.call("mkaguzi.doctype.board_report.board_report.create_quarterly_board_report",
							quarter=1, year=2025)

		self.assertEqual(report.reporting_period, "Q1")
		self.assertEqual(report.report_type, "Board Report")
		self.assertEqual(report.report_status, "Draft")
		self.assertIn("Quarter 1, 2025", report.executive_summary)

	def test_get_board_report_summary_function(self):
		"""Test the get_board_report_summary whitelisted function"""
		report = frappe.new_doc("Board Report")
		report.report_title = "Test Summary Report"
		report.reporting_period = "Q1"
		report.report_type = "Board Report"
		report.report_status = "Draft"
		report.total_engagements_completed = 5
		report.total_critical_findings = 2
		report.compliance_score = 85.5
		report.insert()

		summary = frappe.call("mkaguzi.doctype.board_report.board_report.get_board_report_summary",
							 report_name=report.name)

		self.assertEqual(summary["report_id"], report.report_id)
		self.assertEqual(summary["title"], "Test Summary Report")
		self.assertEqual(summary["total_engagements"], 5)
		self.assertEqual(summary["critical_findings"], 2)
		self.assertEqual(summary["compliance_score"], 85.5)

	def test_get_quarterly_trends_function(self):
		"""Test the get_quarterly_trends whitelisted function"""
		trends = frappe.call("mkaguzi.doctype.board_report.board_report.get_quarterly_trends")

		self.assertIn("engagements", trends)
		self.assertIn("findings", trends)
		self.assertIn("compliance_scores", trends)
		self.assertIn("quarters", trends)
		self.assertEqual(len(trends["quarters"]), 4)
		self.assertEqual(len(trends["engagements"]), 4)

	def test_generate_board_presentation_function(self):
		"""Test the generate_board_presentation whitelisted function"""
		report = frappe.new_doc("Board Report")
		report.report_title = "Test Presentation Report"
		report.reporting_period = "Q1"
		report.report_type = "Board Report"
		report.report_status = "Draft"
		report.insert()

		result = frappe.call("mkaguzi.doctype.board_report.board_report.generate_board_presentation",
							report_name=report.name)

		self.assertEqual(result["message"], "Presentation generation started")

	def test_financial_impact_calculation(self):
		"""Test financial impact calculation"""
		# Create test corrective action with savings
		if not frappe.db.exists("Corrective Action Plan", "TEST-FIN-ACTION-001"):
			action = frappe.new_doc("Corrective Action Plan")
			action.action_id = "TEST-FIN-ACTION-001"
			action.action_description = "Test financial action"
			action.estimated_savings = 100000
			action.action_status = "Completed"
			action.save()

		report = frappe.new_doc("Board Report")
		report.report_title = "Test Financial Report"
		report.reporting_period = "Q1"
		report.financial_impact = 1

		report.insert()

		# Check if financial metrics were calculated
		self.assertEqual(report.actual_savings_achieved, 100000)
		self.assertIsNotNone(report.roi_on_audit_investments)