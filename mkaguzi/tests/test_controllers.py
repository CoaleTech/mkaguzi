#!/usr/bin/env python3
"""
Unit tests for audit controllers
"""

import unittest
import frappe
from frappe.tests.utils import FrappeTestCase
from mkaguzi.controllers.audit_controllers import (
    AuditGLController,
    AuditDoctypeCatalogController,
    AuditIntegrityReportController,
    AuditTestTemplateController,
    ModuleSyncStatusController
)
from mkaguzi.api import AuditAPI
from unittest.mock import Mock, patch


class TestAuditGLController(FrappeTestCase):
    """Unit tests for Audit GL Controller"""

    def setUp(self):
        self.controller = AuditGLController()
        self.audit_api = AuditAPI()

    def test_validate_gl_entry_valid_data(self):
        """Test GL entry validation with valid data"""
        # Create mock GL entry document
        doc = Mock()
        doc.doctype = 'GL Entry'
        doc.name = 'ACC-GLE-001'
        doc.posting_date = '2024-01-15'
        doc.account = 'Test Account'
        doc.debit = 1000.00
        doc.credit = 0.00

        # Test validation
        result = self.controller.validate_gl_entry(doc)
        self.assertTrue(result['valid'])
        self.assertEqual(result['risk_level'], 'Low')

    def test_validate_gl_entry_missing_data(self):
        """Test GL entry validation with missing data"""
        doc = Mock()
        doc.doctype = 'GL Entry'
        doc.name = 'ACC-GLE-001'
        doc.posting_date = None  # Missing date
        doc.account = 'Test Account'
        doc.debit = 1000.00
        doc.credit = 0.00

        result = self.controller.validate_gl_entry(doc)
        self.assertFalse(result['valid'])
        self.assertIn('posting_date', result['errors'])

    def test_create_audit_trail(self):
        """Test audit trail creation"""
        doc = Mock()
        doc.doctype = 'GL Entry'
        doc.name = 'ACC-GLE-001'
        doc.posting_date = '2024-01-15'

        with patch.object(self.audit_api, '_create_audit_entry') as mock_create:
            self.controller.create_audit_trail(doc, 'Create')
            mock_create.assert_called_once()


class TestAuditDoctypeCatalogController(FrappeTestCase):
    """Unit tests for Audit Doctype Catalog Controller"""

    def setUp(self):
        self.controller = AuditDoctypeCatalogController()
        self.audit_api = AuditAPI()

    def test_validate_catalog_entry(self):
        """Test catalog entry validation"""
        doc = Mock()
        doc.doctype = 'Audit Doctype Catalog'
        doc.doctype_name = 'GL Entry'
        doc.module = 'Accounts'
        doc.is_active = 1

        result = self.controller.validate_catalog_entry(doc)
        self.assertTrue(result['valid'])

    def test_update_discovery_status(self):
        """Test discovery status update"""
        doc = Mock()
        doc.name = 'CAT-001'
        doc.doctype_name = 'GL Entry'

        with patch('frappe.db.set_value') as mock_set:
            self.controller.update_discovery_status(doc, 'Completed')
            mock_set.assert_called()


class TestAuditIntegrityReportController(FrappeTestCase):
    """Unit tests for Audit Integrity Report Controller"""

    def setUp(self):
        self.controller = AuditIntegrityReportController()
        self.audit_api = AuditAPI()

    def test_run_integrity_checks(self):
        """Test integrity check execution"""
        doc = Mock()
        doc.doctype = 'Audit Integrity Report'
        doc.name = 'INT-001'

        with patch.object(self.audit_api, 'run_integrity_check') as mock_check:
            mock_check.return_value = {'status': 'completed'}
            result = self.controller.run_integrity_checks(doc)
            self.assertEqual(result['status'], 'completed')

    def test_generate_integrity_report(self):
        """Test integrity report generation"""
        doc = Mock()
        doc.name = 'INT-001'
        doc.check_type = 'full'

        result = self.controller.generate_integrity_report(doc)
        self.assertIn('report_data', result)


class TestAuditTestTemplateController(FrappeTestCase):
    """Unit tests for Audit Test Template Controller"""

    def setUp(self):
        self.controller = AuditTestTemplateController()
        self.audit_api = AuditAPI()

    def test_validate_template(self):
        """Test template validation"""
        doc = Mock()
        doc.doctype = 'Audit Test Template'
        doc.template_name = 'Test Template'
        doc.test_type = 'data_integrity'
        doc.is_active = 1

        result = self.controller.validate_template(doc)
        self.assertTrue(result['valid'])

    def test_execute_template_tests(self):
        """Test template test execution"""
        doc = Mock()
        doc.name = 'TPL-001'
        doc.test_type = 'data_integrity'

        result = self.controller.execute_template_tests(doc)
        self.assertIn('execution_results', result)


class TestModuleSyncStatusController(FrappeTestCase):
    """Unit tests for Module Sync Status Controller"""

    def setUp(self):
        self.controller = ModuleSyncStatusController()
        self.audit_api = AuditAPI()

    def test_update_sync_status(self):
        """Test sync status update"""
        doc = Mock()
        doc.name = 'SYNC-001'
        doc.module = 'audit_trail'

        result = self.controller.update_sync_status(doc, 'success')
        self.assertEqual(result['status'], 'updated')

    def test_check_sync_health(self):
        """Test sync health check"""
        doc = Mock()
        doc.module = 'audit_trail'
        doc.last_sync = '2024-01-15 10:00:00'

        result = self.controller.check_sync_health(doc)
        self.assertIn('health_status', result)


if __name__ == '__main__':
    unittest.main()