"""Tests for API security"""
import frappe
from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch, MagicMock


class TestAPISecurity(FrappeTestCase):
    def setUp(self):
        # Import API class
        from mkaguzi.api.audit_api import AuditAPI
        self.api = AuditAPI()

    def test_get_audit_trail_with_valid_params(self):
        """Test get_audit_trail with valid parameters"""
        # Should succeed with valid parameters
        result = self.api.get_audit_trail(limit=100, start=0)
        self.assertIn('entries', result)

    def test_get_audit_trail_limit_enforced(self):
        """Test that limit parameter is enforced"""
        from mkaguzi.utils.api_validators import validate_audit_trail_params

        # Should succeed with limit=100
        result = validate_audit_trail_params(limit=100)
        self.assertEqual(result['limit'], 100)

        # Should succeed but cap at 1000
        result = validate_audit_trail_params(limit=5000)
        self.assertEqual(result['limit'], 1000)

    def test_run_integrity_check_invalid_type(self):
        """Test that invalid check type is rejected"""
        from mkaguzi.utils.api_validators import validate_check_type

        # Valid types should pass
        for check_type in ['full', 'data', 'config']:
            result = validate_check_type(check_type)
            self.assertEqual(result, check_type)

        # Invalid type should raise exception
        with self.assertRaises(frappe.ValidationError):
            validate_check_type('invalid_type')

    def test_send_notification_validation(self):
        """Test notification validation"""
        from mkaguzi.utils.api_validators import validate_notification_data

        # Valid notification data
        validate_notification_data(
            'email',
            ['test@example.com'],
            {'key': 'value'}
        )

        # Invalid type should raise exception
        with self.assertRaises(frappe.ValidationError):
            validate_notification_data(
                'invalid_type',
                ['test@example.com'],
                {}
            )

        # Empty recipients should raise exception
        with self.assertRaises(frappe.ValidationError):
            validate_notification_data(
                'email',
                [],
                {}
            )

        # Invalid email should raise exception
        with self.assertRaises(frappe.ValidationError):
            validate_notification_data(
                'email',
                ['not-an-email'],
                {}
            )

    def test_create_audit_program_validation(self):
        """Test audit program data validation"""
        from mkaguzi.utils.api_validators import validate_program_data

        # Valid program data
        valid_data = {
            'name': 'Test Program',
            'audit_areas': [{'name': 'Area 1'}],
            'start_date': '2024-01-01'
        }
        result = validate_program_data(valid_data)
        self.assertEqual(result['name'], 'Test Program')

        # Missing required fields should raise exception
        with self.assertRaises(frappe.ValidationError):
            validate_program_data({'name': 'Test'})

        # Invalid date format should raise exception
        with self.assertRaises(frappe.ValidationError):
            validate_program_data({
                'name': 'Test',
                'audit_areas': [],
                'start_date': 'invalid-date'
            })

    def test_sanitize_input_blocks_sql_injection(self):
        """Test that input sanitization blocks SQL injection"""
        from mkaguzi.utils.api_validators import sanitize_input_string

        # Normal string should pass
        result = sanitize_input_string("Normal input")
        self.assertEqual(result, "Normal input")

        # SQL injection patterns should be blocked
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "'; DELETE FROM users WHERE '1'='1",
            "admin' --",
            "'; SELECT * FROM users; --"
        ]

        for attempt in sql_injection_attempts:
            with self.assertRaises(frappe.ValidationError):
                sanitize_input_string(attempt)

    def test_sanitize_input_blocks_xss(self):
        """Test that input sanitization blocks XSS patterns"""
        from mkaguzi.utils.api_validators import sanitize_input_string

        xss_attempts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<body onload=alert('xss')>"
        ]

        for attempt in xss_attempts:
            with self.assertRaises(frappe.ValidationError):
                sanitize_input_string(attempt)

    def test_validate_module_name(self):
        """Test module name validation"""
        from mkaguzi.utils.api_validators import validate_module_name

        valid_modules = ['Financial', 'HR', 'Inventory', 'Access Control']

        # Valid module should pass
        for module in valid_modules:
            result = validate_module_name(module, valid_modules)
            self.assertEqual(result, module)

        # Invalid module should raise exception
        with self.assertRaises(frappe.ValidationError):
            validate_module_name('InvalidModule', valid_modules)


class TestPermissionChecks(FrappeTestCase):
    def test_safe_insert_with_permission(self):
        """Test safe_insert with proper permissions"""
        from mkaguzi.utils.permissions import safe_insert, is_system_manager

        if is_system_manager():
            # Create a test document
            doc = frappe.get_doc({
                'doctype': 'Comment',
                'comment_type': 'Comment',
                'reference_doctype': 'User',
                'reference_name': frappe.session.user,
                'content': 'Test comment for permission check',
                'comment_email': frappe.session.user
            })

            # Should succeed with System Manager
            result = safe_insert(doc)
            self.assertIsNotNone(result)

            # Clean up
            frappe.delete_doc('Comment', result)

    def test_require_system_manager(self):
        """Test require_system_manager function"""
        from mkaguzi.utils.permissions import require_system_manager, is_system_manager

        if is_system_manager():
            # Should pass for System Manager
            result = require_system_manager(throw=False)
            self.assertTrue(result)
        else:
            # Should fail for non-System Manager
            result = require_system_manager(throw=False)
            self.assertFalse(result)

    def test_require_auditor(self):
        """Test require_auditor function"""
        from mkaguzi.utils.permissions import require_auditor, is_auditor

        if is_auditor():
            # Should pass for users with audit role
            result = require_auditor(throw=False)
            self.assertTrue(result)
        else:
            # Should fail for users without audit role
            result = require_auditor(throw=False)
            self.assertFalse(result)


class TestRateLimitingOnAPI(FrappeTestCase):
    def test_rate_limiting_works(self):
        """Test that rate limiting is applied to API endpoints"""
        from mkaguzi.utils.rate_limiter import RateLimiter

        user = frappe.session.user
        endpoint = 'test_rate_limit_api'

        # Clear any existing rate limits
        RateLimiter.reset_rate_limit(user, endpoint)

        # Make requests up to limit
        limit = 10
        for i in range(limit):
            result = RateLimiter.check_rate_limit(user, endpoint, limit=limit, window=3600)
            self.assertTrue(result)

        # Next request should be rate limited
        result = RateLimiter.check_rate_limit(user, endpoint, limit=limit, window=3600)
        self.assertFalse(result)

        # Clean up
        RateLimiter.reset_rate_limit(user, endpoint)

    def test_rate_limit_headers(self):
        """Test rate limit headers generation"""
        from mkaguzi.utils.rate_limiter import get_rate_limit_headers
        import time

        user = frappe.session.user
        endpoint = 'test_headers'

        headers = get_rate_limit_headers(user, endpoint, limit=100, window=3600)

        self.assertIn('X-RateLimit-Limit', headers)
        self.assertIn('X-RateLimit-Remaining', headers)
        self.assertIn('X-RateLimit-Reset', headers)
        self.assertEqual(headers['X-RateLimit-Limit'], '100')
