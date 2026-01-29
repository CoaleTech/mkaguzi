# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import getdate, add_days

class TestManagementDashboard(unittest.TestCase):
	def setUp(self):
		# Clean up any existing test dashboards
		frappe.db.rollback()

	def tearDown(self):
		# Clean up test data
		frappe.db.rollback()

	def test_dashboard_creation(self):
		"""Test management dashboard creation"""
		dashboard = frappe.new_doc("Management Dashboard")
		dashboard.dashboard_title = "Test Management Dashboard"
		dashboard.dashboard_type = "Management Overview"
		dashboard.description = "Test dashboard for management overview"
		dashboard.is_default = 0
		dashboard.is_active = 1
		dashboard.time_period = "Current Month"

		dashboard.insert()

		# Check if dashboard_id was auto-generated
		self.assertTrue(dashboard.dashboard_id.startswith("MD-"))
		self.assertTrue(dashboard.dashboard_id.endswith("-0001"))

		# Check audit fields
		self.assertEqual(dashboard.created_by, "Administrator")
		self.assertIsNotNone(dashboard.creation_date)

	def test_default_dashboard_validation(self):
		"""Test default dashboard validation"""
		# Create first default dashboard
		dashboard1 = frappe.new_doc("Management Dashboard")
		dashboard1.dashboard_title = "Default Dashboard 1"
		dashboard1.dashboard_type = "Management Overview"
		dashboard1.is_default = 1
		dashboard1.is_active = 1
		dashboard1.time_period = "Current Month"
		dashboard1.insert()

		# Try to create second default dashboard for same type
		dashboard2 = frappe.new_doc("Management Dashboard")
		dashboard2.dashboard_title = "Default Dashboard 2"
		dashboard2.dashboard_type = "Management Overview"
		dashboard2.is_default = 1
		dashboard2.is_active = 1
		dashboard2.time_period = "Current Month"

		with self.assertRaises(frappe.ValidationError):
			dashboard2.insert()

	def test_kpi_calculation(self):
		"""Test KPI calculation functionality"""
		# Create test data first
		self.create_test_data()

		dashboard = frappe.new_doc("Management Dashboard")
		dashboard.dashboard_title = "Test KPI Dashboard"
		dashboard.dashboard_type = "Management Overview"
		dashboard.kpi_section = 1
		dashboard.compliance_section = 1
		dashboard.time_period = "All Time"
		dashboard.insert()

		# Check if KPIs were calculated
		self.assertIsNotNone(dashboard.total_engagements)
		self.assertIsNotNone(dashboard.total_findings)
		self.assertIsNotNone(dashboard.compliance_score)

	def create_test_data(self):
		"""Create test data for KPI calculations"""
		# Create test engagement
		if not frappe.db.exists("Audit Engagement", "TEST-KPI-ENG-001"):
			engagement = frappe.new_doc("Audit Engagement")
			engagement.engagement_id = "TEST-KPI-ENG-001"
			engagement.engagement_title = "Test KPI Engagement"
			engagement.audit_universe = "Test Department"
			engagement.start_date = getdate()
			engagement.end_date = add_days(getdate(), 30)
			engagement.engagement_status = "Completed"
			engagement.save()

		# Create test finding
		if not frappe.db.exists("Audit Finding", "TEST-KPI-FIND-001"):
			finding = frappe.new_doc("Audit Finding")
			finding.finding_id = "TEST-KPI-FIND-001"
			finding.finding_title = "Test KPI Finding"
			finding.engagement_reference = "TEST-KPI-ENG-001"
			finding.risk_rating = "High"
			finding.save()

		# Create test compliance requirement
		if not frappe.db.exists("Compliance Requirement", "TEST-KPI-COMP-001"):
			compliance = frappe.new_doc("Compliance Requirement")
			compliance.requirement_id = "TEST-KPI-COMP-001"
			compliance.requirement_title = "Test KPI Compliance"
			compliance.compliance_status = "Compliant"
			compliance.save()

	def test_get_dashboard_data_function(self):
		"""Test the get_dashboard_data whitelisted function"""
		dashboard = frappe.new_doc("Management Dashboard")
		dashboard.dashboard_title = "Test Data Dashboard"
		dashboard.dashboard_type = "Management Overview"
		dashboard.kpi_section = 1
		dashboard.chart_configuration = 1
		dashboard.time_period = "Current Month"
		dashboard.insert()

		data = frappe.call("mkaguzi.doctype.management_dashboard.management_dashboard.get_dashboard_data",
							dashboard_name=dashboard.name)

		self.assertIn("kpis", data)
		self.assertIn("charts", data)
		self.assertIn("last_updated", data)

	def test_refresh_dashboard_function(self):
		"""Test the refresh_dashboard whitelisted function"""
		dashboard = frappe.new_doc("Management Dashboard")
		dashboard.dashboard_title = "Test Refresh Dashboard"
		dashboard.dashboard_type = "Management Overview"
		dashboard.kpi_section = 1
		dashboard.time_period = "Current Month"
		dashboard.insert()

		result = frappe.call("mkaguzi.doctype.management_dashboard.management_dashboard.refresh_dashboard",
							dashboard_name=dashboard.name)

		self.assertEqual(result["message"], "Dashboard refreshed successfully")
		self.assertIn("last_updated", result)

	def test_create_default_dashboards_function(self):
		"""Test the create_default_dashboards whitelisted function"""
		result = frappe.call("mkaguzi.doctype.management_dashboard.management_dashboard.create_default_dashboards")

		self.assertEqual(result["message"], "Default dashboards created successfully")

		# Check if dashboards were created
		dashboards = frappe.get_all("Management Dashboard", filters={"is_default": 1})
		self.assertTrue(len(dashboards) > 0)

		# Check specific dashboard types
		dashboard_types = ["Management Overview", "Compliance Dashboard", "Risk Dashboard",
						 "Operational Dashboard", "Executive Summary"]
		for dashboard_type in dashboard_types:
			dashboard = frappe.get_all("Management Dashboard",
				filters={"dashboard_type": dashboard_type, "is_default": 1})
			self.assertTrue(len(dashboard) > 0)

	def test_generate_chart_data_function(self):
		"""Test the generate_chart_data function"""
		dashboard = frappe.new_doc("Management Dashboard")
		dashboard.dashboard_title = "Test Chart Dashboard"
		dashboard.dashboard_type = "Management Overview"
		dashboard.chart_configuration = 1
		dashboard.chart_1_data_source = "Engagement Status"
		dashboard.chart_2_data_source = "Findings by Risk"
		dashboard.total_engagements = 10
		dashboard.completed_engagements = 7
		dashboard.in_progress_engagements = 2
		dashboard.overdue_engagements = 1
		dashboard.critical_findings = 2
		dashboard.high_findings = 5
		dashboard.medium_findings = 8
		dashboard.low_findings = 3

		from mkaguzi.doctype.management_dashboard.management_dashboard import generate_chart_data
		charts = generate_chart_data(dashboard)

		self.assertIn("chart1", charts)
		self.assertIn("chart2", charts)
		self.assertEqual(charts["chart1"]["data"]["datasets"][0]["data"], [7, 2, 1])
		self.assertEqual(charts["chart2"]["data"]["datasets"][0]["data"], [2, 5, 8, 3])

	def test_dashboard_update_default_flag(self):
		"""Test updating default flag clears other defaults"""
		# Create two dashboards of same type
		dashboard1 = frappe.new_doc("Management Dashboard")
		dashboard1.dashboard_title = "Dashboard 1"
		dashboard1.dashboard_type = "Management Overview"
		dashboard1.is_default = 0
		dashboard1.time_period = "Current Month"
		dashboard1.insert()

		dashboard2 = frappe.new_doc("Management Dashboard")
		dashboard2.dashboard_title = "Dashboard 2"
		dashboard2.dashboard_type = "Management Overview"
		dashboard2.is_default = 0
		dashboard2.time_period = "Current Month"
		dashboard2.insert()

		# Make dashboard2 default
		dashboard2.is_default = 1
		dashboard2.save()

		# Check that dashboard1 is no longer default
		dashboard1.reload()
		self.assertEqual(dashboard1.is_default, 0)
		self.assertEqual(dashboard2.is_default, 1)