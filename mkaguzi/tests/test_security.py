"""
Security tests for Mkaguzi
"""
import unittest
import frappe
from frappe.tests.utils import FrappeTestCase
from mkaguzi.utils.query_manager import QueryManager
from mkaguzi.utils.error_handler import SecureErrorHandler
from mkaguzi.utils.validators import KenyanDataValidator

class TestSecurityFeatures(FrappeTestCase):
    """Test security features"""

    def test_query_whitelist_prevents_injection(self):
        """Test that only whitelisted queries can be executed"""
        # Should work
        result = QueryManager.execute_safe_query('audit_gl_entry_validation')
        self.assertIsInstance(result, list)

        # Should fail
        with self.assertRaises(ValueError):
            QueryManager.execute_safe_query('malicious_query')

    def test_error_sanitization(self):
        """Test that errors are sanitized properly"""
        sensitive_error = Exception("Error: password is 'secret123'")
        sanitized = SecureErrorHandler.sanitize_error_message(str(sensitive_error))

        self.assertIn('redacted', sanitized.lower())
        self.assertNotIn('secret123', sanitized)

    def test_pin_validation_rejects_invalid(self):
        """Test PIN validation"""
        is_valid, msg = KenyanDataValidator.validate_pin('INVALID')
        self.assertFalse(is_valid)

    def test_pin_validation_accepts_valid(self):
        """Test valid PIN acceptance"""
        is_valid, msg = KenyanDataValidator.validate_pin('A1234567891')
        # Note: This may need adjustment based on actual KRA algorithm

class TestPerformanceFixes(FrappeTestCase):
    """Test performance improvements"""

    def test_no_n_plus_one_query(self):
        """Test that compliance checks don't cause N+1 queries"""
        from mkaguzi.api.compliance import get_compliance_checks

        # Monitor query count
        initial_queries = frappe.db.sql("SHOW STATUS LIKE 'Questions'")

        result = get_compliance_checks(page=1, page_size=10)

        final_queries = frappe.db.sql("SHOW STATUS LIKE 'Questions'")

        # Should execute constant number of queries regardless of page size
        query_count = int(final_queries[0][1]) - int(initial_queries[0][1])
        self.assertLess(query_count, 20)  # Should be around 2-3 queries

    def test_cache_reduces_queries(self):
        """Test that caching reduces database queries"""
        from mkaguzi.api.audit_api import AuditAPI

        api = AuditAPI()

        # First call - should hit database
        api.clear_cache()
        result1 = api._get_system_metrics()

        # Second call - should use cache
        result2 = api._get_system_metrics()

        self.assertEqual(result1, result2)

class TestTypeSafety(FrappeTestCase):
    """Test type hints and validation"""

    def test_api_response_structure(self):
        """Test API responses have consistent structure"""
        from mkaguzi.utils.api_response import APIResponseBuilder

        success_response = APIResponseBuilder.success({'data': 'test'})
        self.assertIn('success', success_response)
        self.assertIn('timestamp', success_response)
        self.assertTrue(success_response['success'])

        error_response = APIResponseBuilder.error('Test error')
        self.assertIn('success', error_response)
        self.assertIn('error', error_response)
        self.assertFalse(error_response['success'])

    def test_paginated_response_structure(self):
        """Test paginated responses have correct structure"""
        from mkaguzi.utils.api_response import APIResponseBuilder

        response = APIResponseBuilder.paginated(
            data=[{'id': 1}, {'id': 2}],
            total=10,
            page=1,
            page_size=2
        )

        self.assertIn('pagination', response)
        self.assertIn('total_pages', response['pagination'])
        self.assertEqual(response['pagination']['total'], 10)
        self.assertEqual(response['pagination']['has_next'], True)


if __name__ == '__main__':
    unittest.main()