"""Tests for API validators"""
import frappe
from frappe.tests.utils import FrappeTestCase
from mkaguzi.utils.api_validators import (
    validate_audit_trail_params,
    validate_check_type,
    validate_notification_data,
    sanitize_input_string,
    validate_period_days,
    validate_risk_level,
    validate_severity
)


class TestAPIValidators(FrappeTestCase):
    def test_validate_audit_trail_params_valid(self):
        """Test validation with valid parameters"""
        result = validate_audit_trail_params(
            doctype='Audit Finding',
            docname='TEST-001',
            limit=50,
            start=0
        )
        self.assertEqual(result['doctype'], 'Audit Finding')
        self.assertEqual(result['limit'], 50)
        self.assertEqual(result['start'], 0)

    def test_validate_audit_trail_params_invalid_limit(self):
        """Test validation with invalid limit"""
        with self.assertRaises(frappe.ValidationError):
            validate_audit_trail_params(limit=2000)

    def test_validate_audit_trail_params_negative_limit(self):
        """Test validation with negative limit"""
        with self.assertRaises(frappe.ValidationError):
            validate_audit_trail_params(limit=-1)

    def test_validate_audit_trail_params_invalid_start(self):
        """Test validation with invalid start"""
        with self.assertRaises(frappe.ValidationError):
            validate_audit_trail_params(start=-1)

    def test_validate_audit_trail_params_docname_without_doctype(self):
        """Test validation with docname but no doctype"""
        with self.assertRaises(frappe.ValidationError):
            validate_audit_trail_params(docname='TEST-001')

    def test_validate_check_type_valid(self):
        """Test valid check types"""
        for check_type in ['full', 'data', 'config']:
            result = validate_check_type(check_type)
            self.assertEqual(result, check_type)

    def test_validate_check_type_invalid(self):
        """Test invalid check type"""
        with self.assertRaises(frappe.ValidationError):
            validate_check_type('invalid_type')

    def test_sanitize_input_string_normal(self):
        """Test sanitization of normal string"""
        result = sanitize_input_string("Normal String")
        self.assertEqual(result, "Normal String")

    def test_sanitize_input_string_sql_injection(self):
        """Test sanitization blocks SQL injection"""
        with self.assertRaises(frappe.ValidationError):
            sanitize_input_string("'; DROP TABLE users; --")

    def test_sanitize_input_string_truncation(self):
        """Test string truncation"""
        long_string = "A" * 500
        result = sanitize_input_string(long_string, max_length=100)
        self.assertEqual(len(result), 100)

    def test_sanitize_input_string_xss(self):
        """Test sanitization blocks XSS patterns"""
        with self.assertRaises(frappe.ValidationError):
            sanitize_input_string("<script>alert('xss')</script>")

    def test_validate_notification_data_valid(self):
        """Test valid notification data"""
        # Should not raise exception
        validate_notification_data(
            'email',
            ['test@example.com'],
            {'key': 'value'}
        )

    def test_validate_notification_data_invalid_type(self):
        """Test invalid notification type"""
        with self.assertRaises(frappe.ValidationError):
            validate_notification_data(
                'invalid_type',
                ['test@example.com'],
                {}
            )

    def test_validate_notification_data_empty_recipients(self):
        """Test empty recipients list"""
        with self.assertRaises(frappe.ValidationError):
            validate_notification_data(
                'email',
                [],
                {}
            )

    def test_validate_notification_data_invalid_email(self):
        """Test invalid email address"""
        with self.assertRaises(frappe.ValidationError):
            validate_notification_data(
                'email',
                ['not-an-email'],
                {}
            )

    def test_validate_period_days_valid(self):
        """Test valid period days"""
        for days in [1, 30, 365, 3650]:
            result = validate_period_days(days)
            self.assertEqual(result, days)

    def test_validate_period_days_invalid(self):
        """Test invalid period days"""
        with self.assertRaises(frappe.ValidationError):
            validate_period_days(0)

    def test_validate_period_days_exceeds_max(self):
        """Test period days exceeds maximum"""
        with self.assertRaises(frappe.ValidationError):
            validate_period_days(4000)

    def test_validate_risk_level_valid(self):
        """Test valid risk levels"""
        for level in ['Low', 'Medium', 'High', 'Critical']:
            result = validate_risk_level(level)
            self.assertEqual(result, level)

    def test_validate_risk_level_invalid(self):
        """Test invalid risk level"""
        with self.assertRaises(frappe.ValidationError):
            validate_risk_level('Invalid')

    def test_validate_severity_valid(self):
        """Test valid severities"""
        for severity in ['Low', 'Medium', 'High', 'Critical']:
            result = validate_severity(severity)
            self.assertEqual(result, severity)

    def test_validate_severity_invalid(self):
        """Test invalid severity"""
        with self.assertRaises(frappe.ValidationError):
            validate_severity('Invalid')
