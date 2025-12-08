# -*- coding: utf-8 -*-
# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
import unittest
import time
from mkaguzi.reporting.doctype.report_template_analytics.report_template_analytics import ReportTemplateAnalytics
from mkaguzi.api.templates import track_template_view, track_template_render, get_analytics_dashboard_data


class TestReportTemplateAnalytics(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        # Create unique template ID for this test run
        self.template_id = f"test-template-analytics-{int(time.time())}"

        # Clean up any existing test template with this ID
        if frappe.db.exists("Report Template", self.template_id):
            frappe.delete_doc("Report Template", self.template_id, ignore_permissions=True, force=True)
            frappe.db.commit()

        # Create a test template
        template = frappe.new_doc("Report Template")
        template.template_name = "Test Template Analytics"
        template.template_type = "Executive Summary"
        # Don't set template_id to avoid loading existing data
        # template.template_id = self.template_id
        # Ensure specialized fields are not set for basic template
        template.audit_category = ""
        template.financial_standards = ""
        template.security_framework = ""
        template.compliance_standards = ""
        template.investigation_methodology = ""
        result = template.insert(ignore_permissions=True)
        self.actual_template_name = result.name
        # Clear any fields that might have been set and save again
        template = frappe.get_doc("Report Template", self.actual_template_name)
        template.audit_category = ""
        template.financial_standards = ""
        template.security_framework = ""
        template.compliance_standards = ""
        template.investigation_methodology = ""
        template.template_id = self.template_id
        template.save(ignore_permissions=True)
        frappe.db.commit()

    def tearDown(self):
        """Clean up test data"""
        # Clean up analytics records
        analytics_records = frappe.get_all("Report Template Analytics",
            filters={"template_name": "Test Template Analytics"})
        for record in analytics_records:
            frappe.delete_doc("Report Template Analytics", record.name, ignore_permissions=True, force=True)

        # Clean up test template
        if hasattr(self, 'actual_template_name') and frappe.db.exists("Report Template", self.actual_template_name):
            frappe.delete_doc("Report Template", self.actual_template_name, ignore_permissions=True, force=True)

        frappe.db.commit()

    def test_analytics_creation(self):
        """Test analytics record creation"""
        template_id = self.actual_template_name

        # Verify template exists
        self.assertTrue(frappe.db.exists("Report Template", template_id))

        # Create analytics record
        analytics = ReportTemplateAnalytics.get_or_create_analytics(template_id)

        self.assertEqual(analytics.template_id, template_id)
        self.assertEqual(analytics.template_name, "Test Template Analytics")
        self.assertEqual(analytics.total_views, 0)
        self.assertEqual(analytics.total_uses, 0)

    def test_analytics_tracking(self):
        """Test analytics tracking functionality"""
        template_id = self.actual_template_name

        # Track template view
        track_template_view(template_id)

        # Track template render
        track_template_render(template_id, render_time=2.5, success=True)

        # Get analytics
        analytics = ReportTemplateAnalytics.get_or_create_analytics(template_id)

        # Verify tracking worked
        self.assertEqual(analytics.total_views, 1)
        self.assertEqual(analytics.total_renders, 1)
        self.assertEqual(analytics.total_uses, 1)  # render counts as use
        self.assertEqual(analytics.average_render_time, 2.5)
        self.assertEqual(analytics.success_rate, 100.0)

    def test_analytics_performance_metrics(self):
        """Test performance metrics calculation"""
        template_id = self.actual_template_name

        # Track multiple renders with different times
        track_template_render(template_id, render_time=1.0, success=True)
        track_template_render(template_id, render_time=3.0, success=True)
        track_template_render(template_id, render_time=2.0, success=False)

        # Get analytics
        analytics = ReportTemplateAnalytics.get_or_create_analytics(template_id)

        # Verify performance metrics
        self.assertEqual(analytics.total_renders, 3)
        self.assertEqual(analytics.total_render_errors, 1)
        self.assertAlmostEqual(analytics.average_render_time, 2.0, places=1)
        self.assertAlmostEqual(analytics.success_rate, 66.67, places=2)  # 2 out of 3 successful

    def test_analytics_dashboard_data(self):
        """Test dashboard data retrieval"""
        template_id = self.actual_template_name

        # Create some analytics data
        track_template_view(template_id)
        track_template_render(template_id, render_time=1.5, success=True)

        # Get dashboard data
        dashboard_response = get_analytics_dashboard_data()

        # Verify dashboard data structure
        self.assertTrue(dashboard_response['success'])
        self.assertIn('performance_metrics', dashboard_response['data'])
        self.assertIn('top_templates', dashboard_response['data'])
        self.assertIn('usage_trends', dashboard_response['data'])

    def test_specialized_template_creation(self):
        """Test creation of specialized audit templates"""
        # Test IT Security template
        template_id = self.actual_template_name

        # Get the template and update it to IT Security
        template = frappe.get_doc("Report Template", template_id)
        template.template_type = "IT Security Audit"
        template.audit_category = "IT Security"
        template.security_framework = "ISO 27001"
        template.vulnerability_scanning = 1
        template.access_control_review = 1
        template.save()

        # Verify specialized fields are set
        updated_template = frappe.get_doc("Report Template", template_id)
        self.assertEqual(updated_template.audit_category, "IT Security")
        self.assertEqual(updated_template.security_framework, "ISO 27001")
        self.assertTrue(updated_template.vulnerability_scanning)
        self.assertTrue(updated_template.access_control_review)

        # Test template config includes specialized settings
        from mkaguzi.reporting.doctype.report_template.report_template import get_template_config
        config = get_template_config(template_id)

        self.assertIn('specialized', config)
        self.assertEqual(config['specialized']['audit_category'], 'IT Security')
        self.assertEqual(config['specialized']['it_security']['framework'], 'ISO 27001')
        self.assertTrue(config['specialized']['it_security']['vulnerability_scanning'])