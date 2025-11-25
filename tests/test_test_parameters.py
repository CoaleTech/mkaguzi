# -*- coding: utf-8 -*-
"""
Tests for Test Parameters
"""

import unittest
import frappe
from frappe.tests.utils import FrappeTestCase


class TestTestParameters(FrappeTestCase):
    """Test cases for Test Parameters"""

    def setUp(self):
        """Set up test data"""
        # Create a test library entry first
        self.test_library = frappe.new_doc("Audit Test Library")
        self.test_library.test_name = "Parameter Test Library"
        self.test_library.test_category = "Duplicate Detection"
        self.test_library.description = "Library for parameter testing"
        self.test_library.test_logic_type = "SQL Query"
        self.test_library.sql_query = "SELECT COUNT(*) as count FROM tabUser WHERE creation > %(start_date)s"
        self.test_library.status = "Active"
        self.test_library.insert()

    def tearDown(self):
        """Clean up test data"""
        frappe.db.rollback()

    def test_create_test_parameter(self):
        """Test creating a new test parameter"""
        param = frappe.new_doc("Test Parameters")

        param.parameter_name = "start_date"
        param.parameter_type = "Date"
        param.parameter_description = "Start date for filtering"
        param.is_required = 1
        param.default_value = "2025-01-01"
        param.test_library_reference = self.test_library.name

        param.insert()

        # Verify creation
        self.assertTrue(param.name)
        self.assertEqual(param.parameter_name, "start_date")
        self.assertEqual(param.parameter_type, "Date")
        self.assertTrue(param.is_required)

    def test_parameter_validation(self):
        """Test parameter validation"""
        param = frappe.new_doc("Test Parameters")

        param.parameter_name = "test_param"
        param.parameter_type = "String"
        param.is_required = 1
        param.test_library_reference = self.test_library.name

        # Test valid values
        param.parameter_value = "Valid String"
        param.validate()  # Should not raise error

        # Test invalid date for date type
        param.parameter_type = "Date"
        param.parameter_value = "invalid-date"
        with self.assertRaises(frappe.ValidationError):
            param.validate()

    def test_parameter_types(self):
        """Test different parameter types"""
        parameter_types = ["String", "Integer", "Float", "Date", "DateTime", "Boolean", "List"]

        for param_type in parameter_types:
            param = frappe.new_doc("Test Parameters")

            param.parameter_name = f"test_{param_type.lower()}"
            param.parameter_type = param_type
            param.test_library_reference = self.test_library.name

            # Set appropriate default values
            if param_type == "String":
                param.default_value = "default_string"
            elif param_type == "Integer":
                param.default_value = "42"
            elif param_type == "Float":
                param.default_value = "3.14"
            elif param_type == "Date":
                param.default_value = "2025-01-01"
            elif param_type == "DateTime":
                param.default_value = "2025-01-01 12:00:00"
            elif param_type == "Boolean":
                param.default_value = "1"
            elif param_type == "List":
                param.default_value = "option1,option2,option3"

            param.insert()

            # Verify type-specific validation
            self.assertEqual(param.parameter_type, param_type)
            self.assertTrue(param.default_value)

    def test_parameter_constraints(self):
        """Test parameter constraints"""
        param = frappe.new_doc("Test Parameters")

        param.parameter_name = "constrained_param"
        param.parameter_type = "Integer"
        param.test_library_reference = self.test_library.name

        # Set constraints
        param.min_value = 0
        param.max_value = 100
        param.allowed_values = "10,20,30,40,50"

        param.insert()

        # Test valid value
        param.parameter_value = "25"
        param.validate()  # Should not raise error

        # Test value below minimum
        param.parameter_value = "-5"
        with self.assertRaises(frappe.ValidationError):
            param.validate()

        # Test value above maximum
        param.parameter_value = "150"
        with self.assertRaises(frappe.ValidationError):
            param.validate()

        # Test value not in allowed list
        param.parameter_value = "35"
        with self.assertRaises(frappe.ValidationError):
            param.validate()

    def test_parameter_dependencies(self):
        """Test parameter dependencies"""
        # Create parent parameter
        parent_param = frappe.new_doc("Test Parameters")
        parent_param.parameter_name = "parent_param"
        parent_param.parameter_type = "Boolean"
        parent_param.test_library_reference = self.test_library.name
        parent_param.insert()

        # Create dependent parameter
        dependent_param = frappe.new_doc("Test Parameters")
        dependent_param.parameter_name = "dependent_param"
        dependent_param.parameter_type = "String"
        dependent_param.test_library_reference = self.test_library.name
        dependent_param.depends_on_parameter = parent_param.name
        dependent_param.dependency_condition = "equals"
        dependent_param.dependency_value = "1"

        dependent_param.insert()

        # Verify dependency
        self.assertEqual(dependent_param.depends_on_parameter, parent_param.name)
        self.assertEqual(dependent_param.dependency_condition, "equals")
        self.assertEqual(dependent_param.dependency_value, "1")

    def test_parameter_uniqueness(self):
        """Test parameter name uniqueness within test library"""
        # Create first parameter
        param1 = frappe.new_doc("Test Parameters")
        param1.parameter_name = "unique_param"
        param1.parameter_type = "String"
        param1.test_library_reference = self.test_library.name
        param1.insert()

        # Try to create duplicate parameter name
        param2 = frappe.new_doc("Test Parameters")
        param2.parameter_name = "unique_param"  # Same name
        param2.parameter_type = "Integer"
        param2.test_library_reference = self.test_library.name

        with self.assertRaises(frappe.ValidationError):
            param2.insert()

    def test_parameter_audit_trail(self):
        """Test parameter audit trail"""
        param = frappe.new_doc("Test Parameters")

        param.parameter_name = "audit_param"
        param.parameter_type = "String"
        param.test_library_reference = self.test_library.name

        param.insert()

        # Verify audit fields
        self.assertTrue(param.created_by)
        self.assertTrue(param.creation_date)
        self.assertTrue(param.last_modified_by)
        self.assertTrue(param.last_modified_date)

    def test_parameter_usage_tracking(self):
        """Test parameter usage tracking"""
        param = frappe.new_doc("Test Parameters")

        param.parameter_name = "usage_param"
        param.parameter_type = "String"
        param.test_library_reference = self.test_library.name
        param.usage_count = 0

        param.insert()

        # Simulate usage
        param.usage_count = 5
        param.last_used_date = "2025-01-01 10:00:00"

        param.save()

        # Verify usage tracking
        self.assertEqual(param.usage_count, 5)
        self.assertEqual(str(param.last_used_date), "2025-01-01 10:00:00")

    def test_parameter_required_validation(self):
        """Test required parameter validation"""
        param = frappe.new_doc("Test Parameters")

        param.parameter_name = "required_param"
        param.parameter_type = "String"
        param.is_required = 1
        param.test_library_reference = self.test_library.name

        param.insert()

        # Test missing required value
        param.parameter_value = ""
        with self.assertRaises(frappe.ValidationError):
            param.validate()

        # Test valid required value
        param.parameter_value = "Valid Value"
        param.validate()  # Should not raise error


if __name__ == "__main__":
    unittest.main()