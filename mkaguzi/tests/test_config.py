#!/usr/bin/env python3
"""
Test configuration and utilities for Mkaguzi audit system tests
"""

import os
import sys
import json
from pathlib import Path


class TestConfig:
    """Test configuration management"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.config_file = self.base_path / 'test_config.json'
        self.load_config()

    def load_config(self):
        """Load test configuration"""
        default_config = {
            'test_environment': 'development',
            'mock_external_services': True,
            'enable_performance_tests': True,
            'test_data_cleanup': True,
            'notification_recipients': ['test@example.com'],
            'database_backup': False,
            'parallel_execution': False,
            'coverage_report': True,
            'verbose_logging': True,
            'timeout_seconds': 300,
            'retry_failed_tests': True,
            'max_retries': 3
        }

        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)

        self.config = default_config

    def save_config(self):
        """Save current configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()


class TestDataManager:
    """Test data management utilities"""

    def __init__(self, config):
        self.config = config

    def create_test_audit_plan(self):
        """Create test audit plan data"""
        return {
            'doctype': 'Audit Plan',
            'plan_title': 'Test Audit Plan',
            'audit_scope': 'Test Scope',
            'planned_start_date': '2024-01-01',
            'planned_end_date': '2024-01-31',
            'estimated_hours': 40,
            'assigned_auditors': ['test@example.com']
        }

    def create_test_audit_execution(self):
        """Create test audit execution data"""
        return {
            'doctype': 'Audit Execution',
            'audit_plan': 'PLAN-TEST-001',
            'execution_title': 'Test Audit Execution',
            'actual_start_date': '2024-01-01',
            'status': 'In Progress'
        }

    def create_test_finding(self):
        """Create test audit finding data"""
        return {
            'doctype': 'Audit Finding',
            'audit_execution': 'EXEC-TEST-001',
            'finding_title': 'Test Finding',
            'severity': 'Medium',
            'status': 'Open',
            'description': 'Test finding description',
            'recommendation': 'Test recommendation'
        }

    def create_test_gl_entry(self):
        """Create test GL entry data"""
        return {
            'doctype': 'GL Entry',
            'posting_date': '2024-01-15',
            'account': 'Test Account',
            'debit': 1000.00,
            'credit': 0.00
        }

    def cleanup_test_data(self):
        """Clean up test data if configured"""
        if self.config.get('test_data_cleanup', True):
            # Implementation would clean up test records
            # This is a placeholder for actual cleanup logic
            pass


class TestUtils:
    """General test utilities"""

    @staticmethod
    def assert_response_structure(response, required_keys):
        """Assert that response contains required keys"""
        for key in required_keys:
            assert key in response, f"Missing required key: {key}"

    @staticmethod
    def assert_valid_status_response(response):
        """Assert valid status response structure"""
        required_keys = ['status', 'timestamp']
        TestUtils.assert_response_structure(response, required_keys)
        assert response['status'] in ['success', 'error', 'warning'], f"Invalid status: {response['status']}"

    @staticmethod
    def assert_valid_api_response(response):
        """Assert valid API response structure"""
        assert isinstance(response, dict), "API response must be a dictionary"
        assert 'timestamp' in response, "API response must include timestamp"

    @staticmethod
    def mock_frappe_sendmail():
        """Mock frappe.sendmail for testing"""
        def mock_sendmail(recipients, subject, message, **kwargs):
            # Log the email that would be sent
            print(f"MOCK EMAIL: To {recipients}, Subject: {subject}")
            return True
        return mock_sendmail

    @staticmethod
    def create_mock_document(doctype, name, **fields):
        """Create a mock document object"""
        from unittest.mock import Mock
        doc = Mock()
        doc.doctype = doctype
        doc.name = name
        for field, value in fields.items():
            setattr(doc, field, value)
        return doc


# Global test configuration instance
test_config = TestConfig()
test_data_manager = TestDataManager(test_config)


def setup_test_environment():
    """Set up test environment"""
    # Add test paths to sys.path if needed
    test_paths = [
        str(Path(__file__).parent.parent),
        str(Path(__file__).parent.parent / 'apps' / 'mkaguzi')
    ]

    for path in test_paths:
        if path not in sys.path:
            sys.path.insert(0, path)

    # Set environment variables for testing
    os.environ.setdefault('TESTING', '1')
    os.environ.setdefault('FRAPPE_TESTING', '1')

    return test_config


def teardown_test_environment():
    """Clean up test environment"""
    # Clean up test data if configured
    if test_config.get('test_data_cleanup', True):
        test_data_manager.cleanup_test_data()

    # Reset environment variables
    if 'TESTING' in os.environ:
        del os.environ['TESTING']
    if 'FRAPPE_TESTING' in os.environ:
        del os.environ['FRAPPE_TESTING']


# Test configuration for CI/CD
ci_config = {
    'test_environment': 'ci',
    'mock_external_services': True,
    'enable_performance_tests': False,  # Skip performance tests in CI
    'test_data_cleanup': True,
    'database_backup': False,
    'parallel_execution': True,
    'coverage_report': True,
    'verbose_logging': False,
    'timeout_seconds': 600,  # Longer timeout for CI
    'retry_failed_tests': True,
    'max_retries': 2
}


def load_ci_config():
    """Load CI-specific configuration"""
    for key, value in ci_config.items():
        test_config.set(key, value)


# Export key functions and classes
__all__ = [
    'TestConfig',
    'TestDataManager',
    'TestUtils',
    'test_config',
    'test_data_manager',
    'setup_test_environment',
    'teardown_test_environment',
    'load_ci_config'
]