# -*- coding: utf-8 -*-
"""
Integration Tests for Audit Test Framework
"""

import unittest
import frappe
from frappe.tests.utils import FrappeTestCase


class TestAuditTestIntegration(FrappeTestCase):
    """Integration tests for the complete audit test workflow"""

    def setUp(self):
        """Set up test data for integration tests"""
        # Create a test library entry
        self.test_library = frappe.new_doc("Audit Test Library")
        self.test_library.test_name = "Integration Test Library"
        self.test_library.test_category = "Duplicate Detection"
        self.test_library.description = "Library for integration testing"
        self.test_library.test_logic_type = "SQL Query"
        self.test_library.sql_query = "SELECT COUNT(*) as count FROM tabUser WHERE creation > %(start_date)s"
        self.test_library.status = "Active"

        # Add parameters to the test library
        self.test_library.append("test_parameters", {
            "parameter_name": "start_date",
            "parameter_type": "Date",
            "is_required": 1,
            "default_value": "2025-01-01"
        })

        # Add thresholds to the test library
        self.test_library.append("test_thresholds", {
            "threshold_name": "High Duplicate Count",
            "threshold_type": "Count",
            "operator": ">",
            "threshold_value": 10,
            "severity": "High"
        })

        self.test_library.insert()

    def tearDown(self):
        """Clean up test data"""
        frappe.db.rollback()

    def test_complete_test_workflow(self):
        """Test the complete workflow from library to execution to results"""
        # Step 1: Create test execution
        execution = frappe.new_doc("Test Execution")
        execution.execution_name = "Integration Workflow Test"
        execution.test_library_reference = self.test_library.name
        execution.execution_type = "Manual"
        execution.status = "Pending"

        # Add execution parameters
        execution.append("execution_parameters", {
            "parameter_name": "start_date",
            "parameter_value": "2025-01-01",
            "parameter_type": "Date"
        })

        execution.insert()

        # Step 2: Update execution status to running
        execution.status = "Running"
        execution.actual_start_date = "2025-01-01 10:00:00"
        execution.save()

        # Step 3: Create test results
        result = frappe.new_doc("Test Results")
        result.result_name = "Integration Test Result"
        result.test_execution_reference = execution.name
        result.test_library_reference = self.test_library.name
        result.result_status = "Passed"
        result.severity = "Low"
        result.confidence_score = 95.0

        # Add result data
        result.append("result_data", {
            "field_name": "duplicate_count",
            "field_value": "3",
            "field_type": "Integer",
            "description": "Number of duplicates found"
        })

        # Add findings
        result.append("findings", {
            "finding_type": "Duplicate Record",
            "finding_description": "Found 3 duplicate user records",
            "affected_records": "User IDs: 123, 456, 789",
            "recommendation": "Review and merge duplicate records",
            "severity": "Medium",
            "confidence_score": 90.0
        })

        result.insert()

        # Step 4: Complete the execution
        execution.status = "Completed"
        execution.actual_end_date = "2025-01-01 10:05:00"
        execution.duration_seconds = 300
        execution.total_tests = 1
        execution.passed_tests = 1
        execution.failed_tests = 0
        execution.total_records_processed = 1000
        execution.save()

        # Step 5: Verify the complete workflow
        # Verify execution
        self.assertEqual(execution.status, "Completed")
        self.assertEqual(execution.total_tests, 1)
        self.assertEqual(execution.passed_tests, 1)

        # Verify result
        self.assertEqual(result.result_status, "Passed")
        self.assertEqual(len(result.result_data), 1)
        self.assertEqual(len(result.findings), 1)

        # Verify relationships
        self.assertEqual(result.test_execution_reference, execution.name)
        self.assertEqual(result.test_library_reference, self.test_library.name)
        self.assertEqual(execution.test_library_reference, self.test_library.name)

    def test_test_execution_with_multiple_results(self):
        """Test execution with multiple test results"""
        # Create test execution
        execution = frappe.new_doc("Test Execution")
        execution.execution_name = "Multi-Result Test"
        execution.test_library_reference = self.test_library.name
        execution.execution_type = "Batch"
        execution.status = "Running"
        execution.insert()

        # Create multiple results
        results = []
        for i in range(3):
            result = frappe.new_doc("Test Results")
            result.result_name = f"Batch Result {i+1}"
            result.test_execution_reference = execution.name
            result.test_library_reference = self.test_library.name
            result.result_status = "Passed" if i < 2 else "Failed"
            result.severity = "Low" if i < 2 else "High"
            result.confidence_score = 90.0 + i * 2

            result.insert()
            results.append(result)

        # Complete execution
        execution.status = "Completed"
        execution.total_tests = 3
        execution.passed_tests = 2
        execution.failed_tests = 1
        execution.save()

        # Verify execution summary
        self.assertEqual(execution.total_tests, 3)
        self.assertEqual(execution.passed_tests, 2)
        self.assertEqual(execution.failed_tests, 1)

        # Verify results
        passed_results = [r for r in results if r.result_status == "Passed"]
        failed_results = [r for r in results if r.result_status == "Failed"]
        self.assertEqual(len(passed_results), 2)
        self.assertEqual(len(failed_results), 1)

    def test_threshold_breached_workflow(self):
        """Test workflow when threshold is breached"""
        # Create test execution
        execution = frappe.new_doc("Test Execution")
        execution.execution_name = "Threshold Breach Test"
        execution.test_library_reference = self.test_library.name
        execution.execution_type = "Manual"
        execution.status = "Running"
        execution.insert()

        # Create result that breaches threshold
        result = frappe.new_doc("Test Results")
        result.result_name = "Threshold Breach Result"
        result.test_execution_reference = execution.name
        result.test_library_reference = self.test_library.name
        result.result_status = "Failed"
        result.severity = "High"
        result.confidence_score = 98.0

        # Add result data that exceeds threshold
        result.append("result_data", {
            "field_name": "duplicate_count",
            "field_value": "25",  # Exceeds threshold of 10
            "field_type": "Integer",
            "description": "Number of duplicates found"
        })

        # Add critical finding
        result.append("findings", {
            "finding_type": "Duplicate Record",
            "finding_description": "Critical: Found 25 duplicate user records",
            "affected_records": "Multiple user records affected",
            "recommendation": "Immediate review and cleanup required",
            "severity": "Critical",
            "confidence_score": 95.0
        })

        result.insert()

        # Complete execution
        execution.status = "Completed"
        execution.exceptions_found = 1
        execution.critical_findings = 1
        execution.save()

        # Verify threshold breach handling
        self.assertEqual(execution.exceptions_found, 1)
        self.assertEqual(execution.critical_findings, 1)
        self.assertEqual(result.result_status, "Failed")
        self.assertEqual(result.severity, "High")

    def test_parameter_validation_workflow(self):
        """Test parameter validation throughout the workflow"""
        # Create test execution with invalid parameters
        execution = frappe.new_doc("Test Execution")
        execution.execution_name = "Parameter Validation Test"
        execution.test_library_reference = self.test_library.name
        execution.execution_type = "Manual"

        # Add invalid parameter (missing required parameter)
        # Note: start_date is required but not provided

        with self.assertRaises(frappe.ValidationError):
            execution.insert()

        # Now add valid parameters
        execution.append("execution_parameters", {
            "parameter_name": "start_date",
            "parameter_value": "2025-01-01",
            "parameter_type": "Date"
        })

        execution.insert()

        # Verify parameter validation passed
        self.assertEqual(len(execution.execution_parameters), 1)
        param = execution.execution_parameters[0]
        self.assertEqual(param.parameter_name, "start_date")
        self.assertEqual(param.parameter_value, "2025-01-01")

    def test_audit_trail_integrity(self):
        """Test audit trail integrity across the workflow"""
        # Create test execution
        execution = frappe.new_doc("Test Execution")
        execution.execution_name = "Audit Trail Test"
        execution.test_library_reference = self.test_library.name
        execution.execution_type = "Manual"
        execution.status = "Pending"
        execution.insert()

        # Create result
        result = frappe.new_doc("Test Results")
        result.result_name = "Audit Trail Result"
        result.test_execution_reference = execution.name
        result.test_library_reference = self.test_library.name
        result.result_status = "Passed"
        result.insert()

        # Verify audit trail
        self.assertTrue(execution.created_by)
        self.assertTrue(execution.creation_date)
        self.assertTrue(result.created_by)
        self.assertTrue(result.creation_date)

        # Verify relationships maintain audit trail
        self.assertEqual(result.test_execution_reference, execution.name)
        self.assertEqual(execution.test_library_reference, self.test_library.name)

    def test_performance_metrics_tracking(self):
        """Test performance metrics tracking across workflow"""
        # Create test execution
        execution = frappe.new_doc("Test Execution")
        execution.execution_name = "Performance Test"
        execution.test_library_reference = self.test_library.name
        execution.execution_type = "Manual"
        execution.status = "Running"
        execution.actual_start_date = "2025-01-01 09:00:00"
        execution.insert()

        # Create result with performance data
        result = frappe.new_doc("Test Results")
        result.result_name = "Performance Result"
        result.test_execution_reference = execution.name
        result.test_library_reference = self.test_library.name
        result.result_status = "Passed"
        result.execution_time_ms = 2500
        result.memory_usage_mb = 150.5
        result.records_processed = 5000
        result.confidence_score = 92.0
        result.insert()

        # Complete execution with performance metrics
        execution.status = "Completed"
        execution.actual_end_date = "2025-01-01 09:05:00"
        execution.duration_seconds = 300
        execution.execution_time_ms = 300000
        execution.memory_usage_mb = 180.0
        execution.cpu_usage_percent = 65.5
        execution.records_per_second = 16.7
        execution.queries_executed = 5
        execution.save()

        # Verify performance metrics
        self.assertEqual(execution.duration_seconds, 300)
        self.assertEqual(execution.execution_time_ms, 300000)
        self.assertEqual(execution.memory_usage_mb, 180.0)
        self.assertEqual(result.execution_time_ms, 2500)
        self.assertEqual(result.memory_usage_mb, 150.5)

    def test_error_handling_workflow(self):
        """Test error handling throughout the workflow"""
        # Create test execution
        execution = frappe.new_doc("Test Execution")
        execution.execution_name = "Error Handling Test"
        execution.test_library_reference = self.test_library.name
        execution.execution_type = "Manual"
        execution.status = "Running"
        execution.insert()

        # Create result with errors
        result = frappe.new_doc("Test Results")
        result.result_name = "Error Result"
        result.test_execution_reference = execution.name
        result.test_library_reference = self.test_library.name
        result.result_status = "Error"

        # Add error details
        result.append("errors", {
            "error_type": "SQL Error",
            "error_message": "Invalid column name 'invalid_column'",
            "error_code": "SQL001",
            "stack_trace": "Line 1: Invalid column name 'invalid_column'",
            "timestamp": "2025-01-01 10:15:00"
        })

        result.insert()

        # Complete execution with error status
        execution.status = "Failed"
        execution.actual_end_date = "2025-01-01 10:15:30"
        execution.duration_seconds = 30
        execution.failed_tests = 1
        execution.save()

        # Verify error handling
        self.assertEqual(execution.status, "Failed")
        self.assertEqual(execution.failed_tests, 1)
        self.assertEqual(result.result_status, "Error")
        self.assertEqual(len(result.errors), 1)


if __name__ == "__main__":
    unittest.main()