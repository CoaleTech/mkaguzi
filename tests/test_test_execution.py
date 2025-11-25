# -*- coding: utf-8 -*-
"""
Tests for Test Execution
"""

import unittest
import frappe
from frappe.tests.utils import FrappeTestCase


class TestTestExecution(FrappeTestCase):
    """Test cases for Test Execution"""

    def setUp(self):
        """Set up test data"""
        # Create a test library entry first
        self.test_library = frappe.new_doc("Audit Test Library")
        self.test_library.test_name = "Test Execution Library"
        self.test_library.test_category = "Duplicate Detection"
        self.test_library.description = "Library for test execution"
        self.test_library.test_logic_type = "SQL Query"
        self.test_library.sql_query = "SELECT COUNT(*) as count FROM tabUser"
        self.test_library.status = "Active"
        self.test_library.insert()

    def tearDown(self):
        """Clean up test data"""
        frappe.db.rollback()

    def test_create_test_execution(self):
        """Test creating a new test execution"""
        execution = frappe.new_doc("Test Execution")

        execution.execution_name = "Test Execution 001"
        execution.test_library_reference = self.test_library.name
        execution.execution_type = "Manual"
        execution.priority = "Medium"
        execution.status = "Pending"

        execution.insert()

        # Verify creation
        self.assertTrue(execution.name)
        self.assertTrue(execution.execution_id)
        self.assertEqual(execution.execution_name, "Test Execution 001")
        self.assertEqual(execution.status, "Pending")

    def test_execution_id_autogeneration(self):
        """Test automatic execution ID generation"""
        execution = frappe.new_doc("Test Execution")

        execution.execution_name = "Auto ID Test"
        execution.test_library_reference = self.test_library.name
        execution.execution_type = "Manual"

        execution.insert()

        # Verify execution_id was generated
        self.assertTrue(execution.execution_id)
        # Should follow some pattern - let's check it starts with TE or similar
        self.assertTrue(len(execution.execution_id) > 0)

    def test_execution_status_workflow(self):
        """Test execution status transitions"""
        execution = frappe.new_doc("Test Execution")

        execution.execution_name = "Status Workflow Test"
        execution.test_library_reference = self.test_library.name
        execution.execution_type = "Manual"
        execution.status = "Pending"

        execution.insert()

        # Test status changes
        valid_statuses = ["Pending", "Queued", "Running", "Completed", "Failed", "Cancelled", "Paused"]

        for status in valid_statuses:
            execution.status = status
            execution.save()
            execution.reload()
            self.assertEqual(execution.status, status)

    def test_execution_with_parameters(self):
        """Test execution with parameters"""
        execution = frappe.new_doc("Test Execution")

        execution.execution_name = "Parameter Test"
        execution.test_library_reference = self.test_library.name
        execution.execution_type = "Manual"

        # Add execution parameters
        execution.append("execution_parameters", {
            "parameter_name": "start_date",
            "parameter_value": "2025-01-01",
            "parameter_type": "Date"
        })
        execution.append("execution_parameters", {
            "parameter_name": "end_date",
            "parameter_value": "2025-12-31",
            "parameter_type": "Date"
        })

        execution.insert()

        # Verify parameters were saved
        self.assertEqual(len(execution.execution_parameters), 2)
        param_names = [p.parameter_name for p in execution.execution_parameters]
        self.assertIn("start_date", param_names)
        self.assertIn("end_date", param_names)

    def test_execution_performance_metrics(self):
        """Test execution performance metrics tracking"""
        execution = frappe.new_doc("Test Execution")

        execution.execution_name = "Performance Test"
        execution.test_library_reference = self.test_library.name
        execution.execution_type = "Manual"
        execution.performance_metrics = 1

        execution.insert()

        # Simulate execution completion
        execution.status = "Completed"
        execution.actual_start_date = "2025-01-01 10:00:00"
        execution.actual_end_date = "2025-01-01 10:05:30"
        execution.duration_seconds = 330
        execution.execution_time_ms = 330000
        execution.memory_usage_mb = 150.5
        execution.cpu_usage_percent = 45.2
        execution.records_per_second = 100.5
        execution.queries_executed = 5

        execution.save()

        # Verify metrics
        self.assertEqual(execution.duration_seconds, 330)
        self.assertEqual(execution.execution_time_ms, 330000)
        self.assertEqual(execution.memory_usage_mb, 150.5)
        self.assertEqual(execution.cpu_usage_percent, 45.2)

    def test_execution_result_summary(self):
        """Test execution result summary"""
        execution = frappe.new_doc("Test Execution")

        execution.execution_name = "Result Summary Test"
        execution.test_library_reference = self.test_library.name
        execution.execution_type = "Manual"
        execution.result_summary = 1

        execution.insert()

        # Set result summary
        execution.total_tests = 10
        execution.passed_tests = 7
        execution.failed_tests = 2
        execution.warning_tests = 1
        execution.total_records_processed = 1000
        execution.exceptions_found = 3
        execution.critical_findings = 1

        execution.save()

        # Verify summary
        self.assertEqual(execution.total_tests, 10)
        self.assertEqual(execution.passed_tests, 7)
        self.assertEqual(execution.failed_tests, 2)
        self.assertEqual(execution.warning_tests, 1)
        self.assertEqual(execution.total_records_processed, 1000)

    def test_execution_logs(self):
        """Test execution logging"""
        execution = frappe.new_doc("Test Execution")

        execution.execution_name = "Log Test"
        execution.test_library_reference = self.test_library.name
        execution.execution_type = "Manual"

        execution.insert()

        # Add execution logs
        execution.append("execution_logs", {
            "log_level": "INFO",
            "log_message": "Test execution started",
            "timestamp": "2025-01-01 10:00:00"
        })
        execution.append("execution_logs", {
            "log_level": "ERROR",
            "log_message": "Test failed with error",
            "timestamp": "2025-01-01 10:05:00"
        })

        execution.save()

        # Verify logs
        self.assertEqual(len(execution.execution_logs), 2)
        log_levels = [log.log_level for log in execution.execution_logs]
        self.assertIn("INFO", log_levels)
        self.assertIn("ERROR", log_levels)

    def test_execution_audit_trail(self):
        """Test execution audit trail"""
        execution = frappe.new_doc("Test Execution")

        execution.execution_name = "Audit Trail Test"
        execution.test_library_reference = self.test_library.name
        execution.execution_type = "Manual"

        execution.insert()

        # Verify audit fields are set
        self.assertTrue(execution.created_by)
        self.assertTrue(execution.creation_date)
        self.assertTrue(execution.last_modified_by)
        self.assertTrue(execution.last_modified_date)

    def test_execution_validation(self):
        """Test execution validation"""
        execution = frappe.new_doc("Test Execution")

        # Missing required fields
        execution.execution_name = "Validation Test"
        # test_library_reference is missing

        with self.assertRaises(frappe.ValidationError):
            execution.insert()

    def test_execution_scheduling(self):
        """Test execution scheduling"""
        execution = frappe.new_doc("Test Execution")

        execution.execution_name = "Schedule Test"
        execution.test_library_reference = self.test_library.name
        execution.execution_type = "Scheduled"
        execution.scheduled_start_date = "2025-01-01 09:00:00"
        execution.scheduled_end_date = "2025-01-01 17:00:00"

        execution.insert()

        # Verify scheduling
        self.assertEqual(str(execution.scheduled_start_date), "2025-01-01 09:00:00")
        self.assertEqual(str(execution.scheduled_end_date), "2025-01-01 17:00:00")


if __name__ == "__main__":
    unittest.main()