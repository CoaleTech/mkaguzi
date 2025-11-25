# -*- coding: utf-8 -*-
"""
Tests for Test Thresholds
"""

import unittest
import frappe
from frappe.tests.utils import FrappeTestCase


class TestTestThresholds(FrappeTestCase):
    """Test cases for Test Thresholds"""

    def setUp(self):
        """Set up test data"""
        # Create a test library entry
        self.test_library = frappe.new_doc("Audit Test Library")
        self.test_library.test_name = "Threshold Test Library"
        self.test_library.test_category = "Duplicate Detection"
        self.test_library.description = "Library for threshold testing"
        self.test_library.test_logic_type = "SQL Query"
        self.test_library.sql_query = "SELECT COUNT(*) as count FROM tabUser"
        self.test_library.status = "Active"
        self.test_library.insert()

    def tearDown(self):
        """Clean up test data"""
        frappe.db.rollback()

    def test_create_test_threshold(self):
        """Test creating a new test threshold"""
        threshold = frappe.new_doc("Test Thresholds")

        threshold.threshold_name = "Duplicate Threshold"
        threshold.test_library_reference = self.test_library.name
        threshold.threshold_type = "Count"
        threshold.operator = ">"
        threshold.threshold_value = 5
        threshold.severity = "Medium"
        threshold.description = "Alert when duplicates exceed 5"

        threshold.insert()

        # Verify creation
        self.assertTrue(threshold.name)
        self.assertEqual(threshold.threshold_name, "Duplicate Threshold")
        self.assertEqual(threshold.threshold_type, "Count")
        self.assertEqual(threshold.operator, ">")
        self.assertEqual(threshold.threshold_value, 5)
        self.assertEqual(threshold.severity, "Medium")

    def test_threshold_validation(self):
        """Test threshold validation"""
        threshold = frappe.new_doc("Test Thresholds")

        threshold.threshold_name = "Validation Test"
        threshold.test_library_reference = self.test_library.name
        threshold.threshold_type = "Percentage"
        threshold.operator = ">="
        threshold.threshold_value = 10.5
        threshold.severity = "High"

        # Test valid threshold
        threshold.validate()  # Should not raise error

        # Test invalid operator
        threshold.operator = "invalid"
        with self.assertRaises(frappe.ValidationError):
            threshold.validate()

        # Reset operator
        threshold.operator = ">="

        # Test invalid threshold value for percentage
        threshold.threshold_value = 150  # Over 100%
        with self.assertRaises(frappe.ValidationError):
            threshold.validate()

    def test_threshold_types(self):
        """Test different threshold types"""
        threshold_types = ["Count", "Percentage", "Amount", "Ratio", "Score"]

        for threshold_type in threshold_types:
            threshold = frappe.new_doc("Test Thresholds")

            threshold.threshold_name = f"{threshold_type} Threshold"
            threshold.test_library_reference = self.test_library.name
            threshold.threshold_type = threshold_type
            threshold.operator = ">"

            # Set appropriate values based on type
            if threshold_type == "Count":
                threshold.threshold_value = 10
            elif threshold_type == "Percentage":
                threshold.threshold_value = 5.5
            elif threshold_type == "Amount":
                threshold.threshold_value = 1000.00
            elif threshold_type == "Ratio":
                threshold.threshold_value = 1.5
            elif threshold_type == "Score":
                threshold.threshold_value = 85.0

            threshold.severity = "Medium"

            threshold.insert()

            # Verify type-specific validation
            self.assertEqual(threshold.threshold_type, threshold_type)
            self.assertTrue(threshold.threshold_value)

    def test_threshold_operators(self):
        """Test threshold operators"""
        operators = ["=", "!=", ">", "<", ">=", "<="]

        for operator in operators:
            threshold = frappe.new_doc("Test Thresholds")

            threshold.threshold_name = f"Operator {operator} Test"
            threshold.test_library_reference = self.test_library.name
            threshold.threshold_type = "Count"
            threshold.operator = operator
            threshold.threshold_value = 5
            threshold.severity = "Low"

            threshold.insert()

            # Verify operator
            self.assertEqual(threshold.operator, operator)

    def test_threshold_ranges(self):
        """Test threshold ranges"""
        threshold = frappe.new_doc("Test Thresholds")

        threshold.threshold_name = "Range Threshold"
        threshold.test_library_reference = self.test_library.name
        threshold.threshold_type = "Count"
        threshold.operator = "between"
        threshold.threshold_value = 5
        threshold.threshold_value_max = 15
        threshold.severity = "Medium"

        threshold.insert()

        # Verify range
        self.assertEqual(threshold.operator, "between")
        self.assertEqual(threshold.threshold_value, 5)
        self.assertEqual(threshold.threshold_value_max, 15)

    def test_threshold_severity_levels(self):
        """Test threshold severity levels"""
        severities = ["Critical", "High", "Medium", "Low", "Info"]

        for severity in severities:
            threshold = frappe.new_doc("Test Thresholds")

            threshold.threshold_name = f"Severity {severity} Test"
            threshold.test_library_reference = self.test_library.name
            threshold.threshold_type = "Count"
            threshold.operator = ">"
            threshold.threshold_value = 10
            threshold.severity = severity

            threshold.insert()

            # Verify severity
            self.assertEqual(threshold.severity, severity)

    def test_threshold_actions(self):
        """Test threshold actions"""
        threshold = frappe.new_doc("Test Thresholds")

        threshold.threshold_name = "Action Threshold"
        threshold.test_library_reference = self.test_library.name
        threshold.threshold_type = "Count"
        threshold.operator = ">"
        threshold.threshold_value = 20
        threshold.severity = "High"

        # Set actions
        threshold.append("threshold_actions", {
            "action_type": "Email Notification",
            "action_description": "Send email to audit team",
            "recipient_email": "audit@company.com",
            "email_subject": "Threshold Exceeded Alert",
            "email_body": "A threshold has been exceeded in the audit test."
        })
        threshold.append("threshold_actions", {
            "action_type": "Create Task",
            "action_description": "Create investigation task",
            "task_title": "Investigate Threshold Breach",
            "task_description": "Review the threshold breach and take corrective action.",
            "assigned_to": "audit_manager"
        })

        threshold.insert()

        # Verify actions
        self.assertEqual(len(threshold.threshold_actions), 2)
        action_types = [action.action_type for action in threshold.threshold_actions]
        self.assertIn("Email Notification", action_types)
        self.assertIn("Create Task", action_types)

    def test_threshold_uniqueness(self):
        """Test threshold name uniqueness within test library"""
        # Create first threshold
        threshold1 = frappe.new_doc("Test Thresholds")
        threshold1.threshold_name = "Unique Threshold"
        threshold1.test_library_reference = self.test_library.name
        threshold1.threshold_type = "Count"
        threshold1.operator = ">"
        threshold1.threshold_value = 5
        threshold1.severity = "Medium"
        threshold1.insert()

        # Try to create duplicate threshold name
        threshold2 = frappe.new_doc("Test Thresholds")
        threshold2.threshold_name = "Unique Threshold"  # Same name
        threshold2.test_library_reference = self.test_library.name
        threshold2.threshold_type = "Percentage"
        threshold2.operator = ">"
        threshold2.threshold_value = 10.0
        threshold2.severity = "High"

        with self.assertRaises(frappe.ValidationError):
            threshold2.insert()

    def test_threshold_audit_trail(self):
        """Test threshold audit trail"""
        threshold = frappe.new_doc("Test Thresholds")

        threshold.threshold_name = "Audit Trail Test"
        threshold.test_library_reference = self.test_library.name
        threshold.threshold_type = "Count"
        threshold.operator = ">"
        threshold.threshold_value = 10
        threshold.severity = "Medium"

        threshold.insert()

        # Verify audit fields
        self.assertTrue(threshold.created_by)
        self.assertTrue(threshold.creation_date)
        self.assertTrue(threshold.last_modified_by)
        self.assertTrue(threshold.last_modified_date)

    def test_threshold_usage_tracking(self):
        """Test threshold usage tracking"""
        threshold = frappe.new_doc("Test Thresholds")

        threshold.threshold_name = "Usage Tracking Test"
        threshold.test_library_reference = self.test_library.name
        threshold.threshold_type = "Count"
        threshold.operator = ">"
        threshold.threshold_value = 15
        threshold.severity = "High"
        threshold.usage_count = 0

        threshold.insert()

        # Simulate usage
        threshold.usage_count = 3
        threshold.last_triggered_date = "2025-01-01 14:30:00"

        threshold.save()

        # Verify usage tracking
        self.assertEqual(threshold.usage_count, 3)
        self.assertEqual(str(threshold.last_triggered_date), "2025-01-01 14:30:00")

    def test_threshold_validation_rules(self):
        """Test threshold validation rules"""
        threshold = frappe.new_doc("Test Thresholds")

        threshold.threshold_name = "Validation Rules Test"
        threshold.test_library_reference = self.test_library.name
        threshold.threshold_type = "Percentage"
        threshold.operator = ">="
        threshold.threshold_value = 25.0
        threshold.severity = "Medium"

        # Test valid percentage
        threshold.validate()  # Should not raise error

        # Test percentage over 100
        threshold.threshold_value = 125.0
        with self.assertRaises(frappe.ValidationError):
            threshold.validate()

        # Test negative percentage
        threshold.threshold_value = -5.0
        with self.assertRaises(frappe.ValidationError):
            threshold.validate()

    def test_threshold_required_fields(self):
        """Test required fields validation"""
        threshold = frappe.new_doc("Test Thresholds")

        # Missing required fields
        threshold.threshold_name = "Required Fields Test"
        # test_library_reference is missing
        threshold.threshold_type = "Count"
        threshold.operator = ">"
        threshold.threshold_value = 10

        with self.assertRaises(frappe.ValidationError):
            threshold.insert()


if __name__ == "__main__":
    unittest.main()