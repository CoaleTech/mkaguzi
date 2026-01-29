#!/usr/bin/env python3
"""
Unit tests for Audit API methods
"""

import unittest
import frappe
from frappe.tests.utils import FrappeTestCase
from mkaguzi.api import AuditAPI
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta


class TestAuditAPIMethods(FrappeTestCase):
    """Unit tests for Audit API methods"""

    def setUp(self):
        self.api = AuditAPI()

    def test_get_system_status_structure(self):
        """Test system status response structure"""
        with patch('frappe.db.count') as mock_count:
            mock_count.return_value = 10

            status = self.api.get_system_status()

            self.assertIn('overall_status', status)
            self.assertIn('modules', status)
            self.assertIn('timestamp', status)
            self.assertIn('alerts', status)
            self.assertIn('metrics', status)

    def test_get_audit_trail_with_filters(self):
        """Test audit trail retrieval with filters"""
        with patch('frappe.get_all') as mock_get_all, \
             patch('frappe.db.count') as mock_count:

            mock_get_all.return_value = [
                {'name': 'TRAIL-001', 'document_type': 'GL Entry', 'operation': 'Create'}
            ]
            mock_count.return_value = 1

            result = self.api.get_audit_trail(doctype='GL Entry', limit=10)

            self.assertEqual(len(result['entries']), 1)
            self.assertEqual(result['total'], 1)
            mock_get_all.assert_called_with(
                'Audit Trail Entry',
                filters={'document_type': 'GL Entry'},
                fields=['name', 'document_type', 'document_name', 'operation',
                       'user', 'timestamp', 'module', 'changes_summary',
                       'risk_level', 'requires_review'],
                order_by='timestamp desc',
                limit=10,
                start=0
            )

    def test_update_dashboard_data_all_modules(self):
        """Test dashboard data update for all modules"""
        with patch.object(self.api, '_update_audit_trail_dashboard') as mock_trail, \
             patch.object(self.api, '_update_discovery_dashboard') as mock_discovery, \
             patch.object(self.api, '_update_templates_dashboard') as mock_templates:

            mock_trail.return_value = {'status': 'success'}
            mock_discovery.return_value = {'status': 'success'}
            mock_templates.return_value = {'status': 'success'}

            result = self.api.update_dashboard_data()

            self.assertEqual(result['overall_status'], 'success')
            self.assertIn('audit_trail', result['modules_updated'])
            self.assertIn('discovery', result['modules_updated'])
            self.assertIn('templates', result['modules_updated'])

    def test_update_dashboard_data_specific_module(self):
        """Test dashboard data update for specific module"""
        with patch.object(self.api, '_update_audit_trail_dashboard') as mock_update:
            mock_update.return_value = {'status': 'success'}

            result = self.api.update_dashboard_data('audit_trail')

            self.assertEqual(result['overall_status'], 'success')
            self.assertIn('audit_trail', result['modules_updated'])
            self.assertEqual(len(result['modules_updated']), 1)

    def test_send_finding_notification(self):
        """Test finding notification sending"""
        with patch('frappe.sendmail') as mock_sendmail:
            result = self.api.send_notification(
                'finding_created',
                ['test@example.com'],
                {
                    'finding_title': 'Test Finding',
                    'severity': 'High',
                    'status': 'Open',
                    'description': 'Test description'
                }
            )

            self.assertEqual(result['status'], 'success')
            self.assertEqual(result['notification_type'], 'finding_created')
            mock_sendmail.assert_called_once()

    def test_send_completion_notification(self):
        """Test audit completion notification"""
        with patch('frappe.sendmail') as mock_sendmail:
            result = self.api.send_notification(
                'audit_completed',
                ['manager@example.com'],
                {
                    'audit_title': 'Q4 Financial Audit',
                    'findings_count': 5
                }
            )

            self.assertEqual(result['status'], 'success')
            self.assertEqual(result['notification_type'], 'audit_completed')
            mock_sendmail.assert_called_once()

    def test_send_integrity_notification(self):
        """Test integrity check failure notification"""
        with patch('frappe.sendmail') as mock_sendmail:
            result = self.api.send_notification(
                'integrity_check_failed',
                ['admin@example.com'],
                {
                    'module': 'audit_trail',
                    'check_type': 'data',
                    'failed_count': 3
                }
            )

            self.assertEqual(result['status'], 'success')
            self.assertEqual(result['notification_type'], 'integrity_check_failed')
            mock_sendmail.assert_called_once()

    def test_send_generic_notification(self):
        """Test generic notification sending"""
        with patch('frappe.sendmail') as mock_sendmail:
            result = self.api.send_notification(
                'system_alert',
                ['user@example.com'],
                {'message': 'System alert test'}
            )

            self.assertEqual(result['status'], 'success')
            self.assertEqual(result['notification_type'], 'system_alert')
            mock_sendmail.assert_called_once()

    def test_run_integrity_check_data_only(self):
        """Test integrity check for data only"""
        with patch.object(self.api, '_get_data_integrity_checks') as mock_get_checks, \
             patch.object(self.api, '_execute_integrity_check') as mock_execute, \
             patch.object(self.api, '_create_integrity_report') as mock_create_report:

            mock_get_checks.return_value = [
                {'name': 'Test Check', 'module': 'audit_trail', 'type': 'data', 'query': 'SELECT 1'}
            ]
            mock_execute.return_value = {
                'check_name': 'Test Check',
                'status': 'passed',
                'message': 'No issues found'
            }

            result = self.api.run_integrity_check('data')

            self.assertIn('checks', result)
            self.assertIn('summary', result)
            self.assertEqual(result['summary']['total_checks'], 1)
            self.assertEqual(result['summary']['passed'], 1)
            self.assertEqual(result['summary']['failed'], 0)

    def test_run_integrity_check_with_failures(self):
        """Test integrity check with failures"""
        with patch.object(self.api, '_get_data_integrity_checks') as mock_get_checks, \
             patch.object(self.api, '_execute_integrity_check') as mock_execute, \
             patch.object(self.api, '_create_integrity_report') as mock_create_report:

            mock_get_checks.return_value = [
                {'name': 'Failing Check', 'module': 'audit_trail', 'type': 'data', 'query': 'SELECT 1'}
            ]
            mock_execute.return_value = {
                'check_name': 'Failing Check',
                'status': 'failed',
                'message': 'Found 5 integrity violations'
            }

            result = self.api.run_integrity_check('data')

            self.assertEqual(result['summary']['passed'], 0)
            self.assertEqual(result['summary']['failed'], 1)
            self.assertEqual(result['overall_status'], 'Failed')

    def test_get_audit_dashboard(self):
        """Test audit dashboard data retrieval"""
        with patch.object(self.api, '_get_dashboard_summary') as mock_summary, \
             patch.object(self.api, '_get_dashboard_charts') as mock_charts, \
             patch.object(self.api, '_get_dashboard_alerts') as mock_alerts, \
             patch.object(self.api, '_get_recent_activity_feed') as mock_activity:

            mock_summary.return_value = {'total_entries': 100}
            mock_charts.return_value = {'activity_chart': []}
            mock_alerts.return_value = []
            mock_activity.return_value = []

            result = self.api.get_audit_dashboard('30')

            self.assertIn('summary', result)
            self.assertIn('charts', result)
            self.assertIn('alerts', result)
            self.assertIn('recent_activity', result)
            self.assertEqual(result['period'], '30 days')

    def test_create_audit_entry(self):
        """Test audit entry creation"""
        # Create mock document
        doc = Mock()
        doc.doctype = 'GL Entry'
        doc.name = 'GLE-001'
        doc.total = 1000.00

        with patch('frappe.get_doc') as mock_get_doc, \
             patch('frappe.db.commit') as mock_commit:

            mock_doc = Mock()
            mock_get_doc.return_value = mock_doc

            self.api._create_audit_entry(doc, 'Create', 'Financial')

            mock_get_doc.assert_called_with({
                'doctype': 'Audit Trail Entry',
                'document_type': 'GL Entry',
                'document_name': 'GLE-001',
                'operation': 'Create',
                'user': frappe.session.user,
                'timestamp': unittest.mock.ANY,
                'module': 'Financial',
                'changes_summary': 'GL Entry Create: GLE-001',
                'risk_level': unittest.mock.ANY,
                'requires_review': unittest.mock.ANY
            })
            mock_doc.insert.assert_called_with(ignore_permissions=True)
            mock_commit.assert_called_once()

    def test_assess_operation_risk(self):
        """Test operation risk assessment"""
        doc = Mock()
        doc.doctype = 'GL Entry'

        # Test high risk operation
        risk = self.api._assess_operation_risk(doc, 'Delete')
        self.assertEqual(risk, 'High')

        # Test sensitive doctype
        doc.doctype = 'User'
        risk = self.api._assess_operation_risk(doc, 'Update')
        self.assertEqual(risk, 'Medium')

        # Test large amount
        doc.doctype = 'GL Entry'
        doc.total = 150000
        risk = self.api._assess_operation_risk(doc, 'Create')
        self.assertEqual(risk, 'Medium')

    def test_get_document_amount(self):
        """Test document amount extraction"""
        doc = Mock()

        # Test with total field
        doc.total = 1000.00
        amount = self.api._get_document_amount(doc)
        self.assertEqual(amount, 1000.00)

        # Test with grand_total field
        doc.total = None
        doc.grand_total = 2000.00
        amount = self.api._get_document_amount(doc)
        self.assertEqual(amount, 2000.00)

        # Test with no amount fields
        doc.grand_total = None
        amount = self.api._get_document_amount(doc)
        self.assertEqual(amount, 0)


if __name__ == '__main__':
    unittest.main()