# -*- coding: utf-8 -*-
"""
Tests for Audit Test Library
"""

import unittest
import frappe
from frappe.tests.utils import FrappeTestCase


class TestAuditTestLibrary(FrappeTestCase):
    """Test cases for Audit Test Library"""

    def setUp(self):
        """Set up test data"""
        self.test_data = {
            "test_name": "Test Duplicate Invoice Detection",
            "test_category": "Duplicate Detection",
            "description": "Detects duplicate invoices based on key fields",
            "objective": "Identify potential duplicate payments",
            "risk_area": "Accounts Payable",
            "data_source_type": "Database Table",
            "test_logic_type": "SQL Query",
            "sql_query": """
                SELECT invoice_number, vendor_id, COUNT(*) as count
                FROM `tabPurchase Invoice`
                GROUP BY invoice_number, vendor_id
                HAVING COUNT(*) > 1
            """,
            "status": "Active",
            "is_template": 1
        }

    def tearDown(self):
        """Clean up test data"""
        # Clean up any test records created
        frappe.db.rollback()

    def test_create_audit_test_library(self):
        """Test creating a new audit test library entry"""
        test = frappe.new_doc("Audit Test Library")

        # Set test data
        for key, value in self.test_data.items():
            setattr(test, key, value)

        # Save the document
        test.insert()

        # Verify the document was created
        self.assertTrue(test.name)
        self.assertEqual(test.test_name, self.test_data["test_name"])
        self.assertEqual(test.test_category, self.test_data["test_category"])
        self.assertEqual(test.status, "Active")

    def test_autoname_generation(self):
        """Test automatic test ID generation"""
        test = frappe.new_doc("Audit Test Library")

        # Set required fields
        test.test_name = "Test Auto Name Generation"
        test.test_category = "Duplicate Detection"
        test.description = "Test autoname functionality"
        test.test_logic_type = "SQL Query"
        test.sql_query = "SELECT 1"

        # Save to trigger autoname
        test.insert()

        # Verify test_id was generated
        self.assertTrue(test.test_id)
        self.assertTrue(test.test_id.startswith("ATL-"))
        self.assertTrue(len(test.test_id) >= 12)  # ATL-YYYY-NNNN format

    def test_validation_sql_query_required(self):
        """Test that SQL query is required for SQL Query logic type"""
        test = frappe.new_doc("Audit Test Library")

        test.test_name = "Test Validation"
        test.test_category = "Duplicate Detection"
        test.description = "Test validation"
        test.test_logic_type = "SQL Query"
        # Note: sql_query is not set

        with self.assertRaises(frappe.ValidationError):
            test.insert()

    def test_validation_python_script_required(self):
        """Test that Python script is required for Python Script logic type"""
        test = frappe.new_doc("Audit Test Library")

        test.test_name = "Test Python Validation"
        test.test_category = "Duplicate Detection"
        test.description = "Test python validation"
        test.test_logic_type = "Python Script"
        # Note: python_script is not set

        with self.assertRaises(frappe.ValidationError):
            test.insert()

    def test_sql_query_validation(self):
        """Test SQL query validation for dangerous operations"""
        test = frappe.new_doc("Audit Test Library")

        test.test_name = "Test SQL Validation"
        test.test_category = "Duplicate Detection"
        test.description = "Test SQL validation"
        test.test_logic_type = "SQL Query"
        test.sql_query = "SELECT * FROM users; DROP TABLE users;"  # Dangerous SQL

        with self.assertRaises(frappe.ValidationError):
            test.insert()

    def test_python_script_validation(self):
        """Test Python script validation for dangerous imports"""
        test = frappe.new_doc("Audit Test Library")

        test.test_name = "Test Python Script Validation"
        test.test_category = "Duplicate Detection"
        test.description = "Test python script validation"
        test.test_logic_type = "Python Script"
        test.python_script = "import os; os.system('rm -rf /')"  # Dangerous import

        with self.assertRaises(frappe.ValidationError):
            test.insert()

    def test_parameter_validation(self):
        """Test parameter validation for duplicates"""
        test = frappe.new_doc("Audit Test Library")

        test.test_name = "Test Parameter Validation"
        test.test_category = "Duplicate Detection"
        test.description = "Test parameter validation"
        test.test_logic_type = "SQL Query"
        test.sql_query = "SELECT 1"

        # Add duplicate parameters
        test.append("test_parameters", {
            "parameter_name": "test_param",
            "parameter_type": "String",
            "default_value": "test"
        })
        test.append("test_parameters", {
            "parameter_name": "test_param",  # Duplicate name
            "parameter_type": "Integer",
            "default_value": "123"
        })

        with self.assertRaises(frappe.ValidationError):
            test.insert()

    def test_threshold_validation(self):
        """Test threshold validation"""
        test = frappe.new_doc("Audit Test Library")

        test.test_name = "Test Threshold Validation"
        test.test_category = "Duplicate Detection"
        test.description = "Test threshold validation"
        test.test_logic_type = "SQL Query"
        test.sql_query = "SELECT 1"

        # Add threshold without value
        test.append("threshold_settings", {
            "threshold_name": "count",
            "comparison_operator": ">",
            "notification_level": "Warning"
            # threshold_value is missing
        })

        with self.assertRaises(frappe.ValidationError):
            test.insert()

    def test_execute_test_sql(self):
        """Test executing a SQL-based test"""
        # Create test
        test = frappe.new_doc("Audit Test Library")
        test.test_name = "Test SQL Execution"
        test.test_category = "Duplicate Detection"
        test.description = "Test SQL execution"
        test.test_logic_type = "SQL Query"
        test.sql_query = "SELECT COUNT(*) as count FROM tabUser"
        test.status = "Active"
        test.insert()

        # Execute test
        result = frappe.call(
            "mkaguzi.api.execute_test",
            test_id=test.name,
            parameters={}
        )

        # Verify result structure
        self.assertIn("test_id", result)
        self.assertIn("test_name", result)
        self.assertIn("result", result)
        self.assertIn("status", result)
        self.assertEqual(result["test_id"], test.test_id)

    def test_get_tests_by_category(self):
        """Test filtering tests by category"""
        # Create test
        test = frappe.new_doc("Audit Test Library")
        test.test_name = "Test Category Filter"
        test.test_category = "Duplicate Detection"
        test.description = "Test category filtering"
        test.test_logic_type = "SQL Query"
        test.sql_query = "SELECT 1"
        test.status = "Active"
        test.insert()

        # Get tests by category
        tests = frappe.call(
            "mkaguzi.api.get_tests_by_category",
            category="Duplicate Detection"
        )

        # Verify results
        self.assertTrue(len(tests) > 0)
        found_test = next((t for t in tests if t["test_id"] == test.test_id), None)
        self.assertIsNotNone(found_test)

    def test_create_sample_templates(self):
        """Test creating sample test templates"""
        # Call the function
        result = frappe.call("mkaguzi.api.create_sample_templates")

        # Verify result
        self.assertIn("Created", result)
        self.assertTrue("sample test templates" in result)

        # Verify templates were created
        templates = frappe.get_all("Audit Test Library",
            filters={"is_template": 1},
            fields=["name", "test_name"]
        )
        self.assertTrue(len(templates) > 0)


if __name__ == "__main__":
    unittest.main()