"""Tests for rate limiter"""
import frappe
from frappe.tests.utils import FrappeTestCase
from mkaguzi.utils.rate_limiter import RateLimiter, rate_limit


class TestRateLimiter(FrappeTestCase):
    def setUp(self):
        self.user = frappe.session.user
        # Clear existing rate limit data before each test
        cache = frappe.cache()
        cache.delete_keys(f"mkaguzi:rate_limit:{self.user}:*")

    def test_rate_limit_check_under_limit(self):
        """Test rate limit when under threshold"""
        # Should pass under limit
        for i in range(10):
            result = RateLimiter.check_rate_limit(self.user, 'test_endpoint', limit=100, window=3600)
            self.assertTrue(result)

    def test_rate_limit_check_exceeds_limit(self):
        """Test rate limit when exceeding threshold"""
        # Set to limit
        for i in range(100):
            RateLimiter.check_rate_limit(self.user, 'test_endpoint_exceed', limit=100, window=3600)

        # Should fail on 101st request
        result = RateLimiter.check_rate_limit(self.user, 'test_endpoint_exceed', limit=100, window=3600)
        self.assertFalse(result)

    def test_get_remaining_requests(self):
        """Test getting remaining requests"""
        # Make some requests
        for i in range(50):
            RateLimiter.check_rate_limit(self.user, 'test_remaining', limit=100, window=3600)

        remaining = RateLimiter.get_remaining_requests(self.user, 'test_remaining', limit=100)
        self.assertEqual(remaining, 50)

    def test_reset_rate_limit(self):
        """Test resetting rate limit"""
        # Make some requests
        for i in range(10):
            RateLimiter.check_rate_limit(self.user, 'test_reset', limit=100, window=3600)

        # Reset
        RateLimiter.reset_rate_limit(self.user, 'test_reset')

        # Should be able to make requests again
        remaining = RateLimiter.get_remaining_requests(self.user, 'test_reset', limit=100)
        self.assertEqual(remaining, 100)

    def test_get_usage_stats(self):
        """Test getting usage statistics"""
        # Make some requests
        for i in range(25):
            RateLimiter.check_rate_limit(self.user, 'test_stats', limit=100, window=3600)

        stats = RateLimiter.get_usage_stats(self.user, 'test_stats')
        self.assertEqual(stats['user'], self.user)
        self.assertEqual(stats['endpoint'], 'test_stats')
        self.assertEqual(stats['requests_used'], 25)
        self.assertEqual(stats['remaining'], 75)

    def test_rate_limit_decorator(self):
        """Test rate limiting decorator"""
        @rate_limit(limit=5, window=3600)
        def test_function():
            return "success"

        # Should work for first 5 calls
        for i in range(5):
            result = test_function()
            self.assertEqual(result, "success")

        # 6th call should raise exception
        with self.assertRaises(frappe.TooManyRequestsError):
            test_function()

    def test_different_endpoints_separate_limits(self):
        """Test that different endpoints have separate rate limits"""
        # Use up limit on endpoint1
        for i in range(100):
            RateLimiter.check_rate_limit(self.user, 'endpoint1', limit=100, window=3600)

        # endpoint1 should be at limit
        self.assertFalse(RateLimiter.check_rate_limit(self.user, 'endpoint1', limit=100, window=3600))

        # endpoint2 should still be available
        self.assertTrue(RateLimiter.check_rate_limit(self.user, 'endpoint2', limit=100, window=3600))


class TestRateLimiterBypass(FrappeTestCase):
    def setUp(self):
        # Create a test user with System Manager role
        if not frappe.db.exists('User', 'test_rate_limit_user@example.com'):
            self.test_user = frappe.get_doc({
                'doctype': 'User',
                'email': 'test_rate_limit_user@example.com',
                'first_name': 'Test Rate Limit',
                'send_welcome_email': 0
            }).insert()

        self.test_user = frappe.get_doc('User', 'test_rate_limit_user@example.com')
        frappe.set_user(self.test_user.name)

    def tearDown(self):
        frappe.set_user('Administrator')
        # Clean up
        if frappe.db.exists('User', 'test_rate_limit_user@example.com'):
            try:
                frappe.delete_doc('User', 'test_rate_limit_user@example.com')
            except:
                pass

    def test_system_manager_bypass(self):
        """Test that System Manager bypasses rate limits"""
        # Add System Manager role
        self.test_user.add_roles('System Manager')
        self.test_user.save()

        try:
            # Even after exceeding limit, System Manager should pass
            for i in range(150):
                result = RateLimiter.check_rate_limit(self.test_user.name, 'test_bypass', limit=100, window=3600)
                self.assertTrue(result)
        finally:
            self.test_user.remove_roles('System Manager')
            self.test_user.save()


class TestTokenBucketRateLimiter(FrappeTestCase):
    def setUp(self):
        self.user = frappe.session.user
        from mkaguzi.utils.rate_limiter import TokenBucketRateLimiter
        # Clear existing rate limit data
        cache = frappe.cache()
        cache.delete_keys(f"mkaguzi:token_bucket:{self.user}:*")

    def test_token_bucket_under_limit(self):
        """Test token bucket when under limit"""
        from mkaguzi.utils.rate_limiter import TokenBucketRateLimiter

        # Should all pass under capacity
        for i in range(10):
            result = TokenBucketRateLimiter.check_rate_limit(
                self.user, 'test_token_bucket',
                capacity=100, refill_rate=10
            )
            self.assertTrue(result)

    def test_token_bucket_refill(self):
        """Test token bucket refill over time"""
        from mkaguzi.utils.rate_limiter import TokenBucketRateLimiter
        import time

        # Use up most tokens
        for i in range(95):
            TokenBucketRateLimiter.check_rate_limit(
                self.user, 'test_refill',
                capacity=100, refill_rate=50  # 50 tokens per second
            )

        # Wait for refill (1 second should add 50 tokens)
        time.sleep(1.1)

        # Should have tokens available again
        result = TokenBucketRateLimiter.check_rate_limit(
            self.user, 'test_refill',
            capacity=100, refill_rate=50
        )
        self.assertTrue(result)
