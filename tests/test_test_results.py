# -*- coding: utf-8 -*-
"""
Tests for Test Results
"""

import unittest
import frappe
from frappe.tests.utils import FrappeTestCase


class TestTestResults(FrappeTestCase):
    """Test cases for Test Results"""

    def setUp(self):
        """Set up test data"""
        # Create a test library entry
        self.test_library = frappe.new_doc("Audit Test Library")
        self.test_library.test_name = "Results Test Library"
        self.test_library.test_category = "Duplicate Detection"
        self.test_library.description = "Library for results testing"
        self.test_library.test_logic_type = "SQL Query"
        self.test_library.sql_query = "SELECT COUNT(*) as count FROM tabUser"
        self.test_library.status = "Active"
        self.test_library.insert()

        # Create a test execution
        self.test_execution = frappe.new_doc("Test Execution")
        self.test_execution.execution_name = "Results Test Execution"
        self.test_execution.test_library_reference = self.test_library.name
        self.test_execution.execution_type = "Manual"
        self.test_execution.status = "Completed"
        self.test_execution.insert()

    def tearDown(self):
        """Clean up test data"""
        frappe.db.rollback()

    def test_create_test_result(self):
        """Test creating a new test result"""
        result = frappe.new_doc("Test Results")

        result.result_name = "Test Result 001"
        result.test_execution_reference = self.test_execution.name
        result.test_library_reference = self.test_library.name
        result.result_status = "Passed"
        result.severity = "Low"
        result.confidence_score = 95.5

        result.insert()

        # Verify creation
        self.assertTrue(result.name)
        self.assertEqual(result.result_name, "Test Result 001")
        self.assertEqual(result.result_status, "Passed")
        self.assertEqual(result.severity, "Low")
        self.assertEqual(result.confidence_score, 95.5)

    def test_result_status_validation(self):
        """Test result status validation"""
        valid_statuses = ["Passed", "Failed", "Warning", "Error", "Skipped", "Inconclusive"]

        for status in valid_statuses:
            result = frappe.new_doc("Test Results")

            result.result_name = f"Status Test {status}"
            result.test_execution_reference = self.test_execution.name
            result.test_library_reference = self.test_library.name
            result.result_status = status

            result.insert()

            # Verify status
            self.assertEqual(result.result_status, status)

    def test_result_severity_levels(self):
        """Test result severity levels"""
        severities = ["Critical", "High", "Medium", "Low", "Info"]

        for severity in severities:
            result = frappe.new_doc("Test Results")

            result.result_name = f"Severity Test {severity}"
            result.test_execution_reference = self.test_execution.name
            result.test_library_reference = self.test_library.name
            result.result_status = "Failed"
            result.severity = severity

            result.insert()

            # Verify severity
            self.assertEqual(result.severity, severity)

    def test_result_data_storage(self):
        """Test result data storage"""
        result = frappe.new_doc("Test Results")

        result.result_name = "Data Storage Test"
        result.test_execution_reference = self.test_execution.name
        result.test_library_reference = self.test_library.name
        result.result_status = "Passed"

        # Add result data
        result.append("result_data", {
            "field_name": "record_count",
            "field_value": "100",
            "field_type": "Integer",
            "description": "Total records processed"
        })
        result.append("result_data", {
            "field_name": "duplicate_count",
            "field_value": "5",
            "field_type": "Integer",
            "description": "Duplicate records found"
        })

        result.insert()

        # Verify data storage
        self.assertEqual(len(result.result_data), 2)
        field_names = [data.field_name for data in result.result_data]
        self.assertIn("record_count", field_names)
        self.assertIn("duplicate_count", field_names)

    def test_result_findings(self):
        """Test result findings"""
        result = frappe.new_doc("Test Results")

        result.result_name = "Findings Test"
        result.test_execution_reference = self.test_execution.name
        result.test_library_reference = self.test_library.name
        result.result_status = "Failed"

        # Add findings
        result.append("findings", {
            "finding_type": "Duplicate Record",
            "finding_description": "Duplicate user found",
            "affected_records": "User ID: 123, User ID: 456",
            "recommendation": "Remove duplicate records",
            "severity": "Medium",
            "confidence_score": 85.0
        })
        result.append("findings", {
            "finding_type": "Data Inconsistency",
            "finding_description": "Inconsistent date format",
            "affected_records": "Records 100-150",
            "recommendation": "Standardize date formats",
            "severity": "Low",
            "confidence_score": 70.0
        })

        result.insert()

        # Verify findings
        self.assertEqual(len(result.findings), 2)
        finding_types = [finding.finding_type for finding in result.findings]
        self.assertIn("Duplicate Record", finding_types)
        self.assertIn("Data Inconsistency", finding_types)

    def test_result_metrics(self):
        """Test result metrics"""
        result = frappe.new_doc("Test Results")

        result.result_name = "Metrics Test"
        result.test_execution_reference = self.test_execution.name
        result.test_library_reference = self.test_library.name
        result.result_status = "Passed"

        # Set metrics
        result.execution_time_ms = 1500
        result.memory_usage_mb = 120.5
        result.records_processed = 1000
        result.records_failed = 0
        result.records_warning = 5
        result.confidence_score = 98.5
        result.accuracy_score = 95.2
        result.completeness_score = 100.0

        result.insert()

        # Verify metrics
        self.assertEqual(result.execution_time_ms, 1500)
        self.assertEqual(result.memory_usage_mb, 120.5)
        self.assertEqual(result.records_processed, 1000)
        self.assertEqual(result.confidence_score, 98.5)

    def test_result_error_handling(self):
        """Test result error handling"""
        result = frappe.new_doc("Test Results")

        result.result_name = "Error Handling Test"
        result.test_execution_reference = self.test_execution.name
        result.test_library_reference = self.test_library.name
        result.result_status = "Error"

        # Add error details
        result.append("errors", {
            "error_type": "SQL Error",
            "error_message": "Syntax error in SQL query",
            "error_code": "SQL001",
            "stack_trace": "Line 5: Invalid syntax near 'SELECT'",
            "timestamp": "2025-01-01 10:30:00"
        })
        result.append("errors", {
            "error_type": "Validation Error",
            "error_message": "Invalid parameter value",
            "error_code": "VAL001",
            "stack_trace": "Parameter validation failed",
            "timestamp": "2025-01-01 10:35:00"
        })

        result.insert()

        # Verify errors
        self.assertEqual(len(result.errors), 2)
        error_types = [error.error_type for error in result.errors]
        self.assertIn("SQL Error", error_types)
        self.assertIn("Validation Error", error_types)

    def test_result_audit_trail(self):
        """Test result audit trail"""
        result = frappe.new_doc("Test Results")

        result.result_name = "Audit Trail Test"
        result.test_execution_reference = self.test_execution.name
        result.test_library_reference = self.test_library.name
        result.result_status = "Passed"

        result.insert()

        # Verify audit fields
        self.assertTrue(result.created_by)
        self.assertTrue(result.creation_date)
        self.assertTrue(result.last_modified_by)
        self.assertTrue(result.last_modified_date)

    def test_result_validation(self):
        """Test result validation"""
        result = frappe.new_doc("Test Results")

        # Missing required fields
        result.result_name = "Validation Test"
        # test_execution_reference is missing

        with self.assertRaises(frappe.ValidationError):
            result.insert()

    def test_result_summary_calculation(self):
        """Test result summary calculation"""
        result = frappe.new_doc("Test Results")

        result.result_name = "Summary Test"
        result.test_execution_reference = self.test_execution.name
        result.test_library_reference = self.test_library.name
        result.result_status = "Passed"

        # Set summary data
        result.total_checks = 10
        result.passed_checks = 8
        result.failed_checks = 1
        result.warning_checks = 1
        result.success_rate = 80.0

        result.insert()

        # Verify summary
        self.assertEqual(result.total_checks, 10)
        self.assertEqual(result.passed_checks, 8)
        self.assertEqual(result.failed_checks, 1)
        self.assertEqual(result.warning_checks, 1)
        self.assertEqual(result.success_rate, 80.0)

    def test_result_export_capability(self):
        """Test result export capability"""
        result = frappe.new_doc("Test Results")

        result.result_name = "Export Test"
        result.test_execution_reference = self.test_execution.name
        result.test_library_reference = self.test_library.name
        result.result_status = "Passed"

        # Set export options
        result.export_format = "JSON"
        result.export_path = "/tmp/test_results.json"
        result.is_exported = 1
        result.export_date = "2025-01-01 11:00:00"

        result.insert()

        # Verify export capability
        self.assertEqual(result.export_format, "JSON")
        self.assertEqual(result.export_path, "/tmp/test_results.json")
        self.assertTrue(result.is_exported)
        self.assertEqual(str(result.export_date), "2025-01-01 11:00:00")


if __name__ == "__main__":
    unittest.main()