#!/usr/bin/env python3
"""
Integration tests for audit system workflows
"""

import unittest
import frappe
from frappe.tests.utils import FrappeTestCase
from mkaguzi.api import AuditAPI
from mkaguzi.controllers.audit_operations_controllers import (
    AuditFindingController,
    AuditExecutionController,
    AuditPlanController
)
from unittest.mock import Mock, patch
from datetime import datetime, timedelta


class TestAuditWorkflowIntegration(FrappeTestCase):
    """Integration tests for complete audit workflows"""

    def setUp(self):
        self.api = AuditAPI()
        self.finding_controller = AuditFindingController()
        self.execution_controller = AuditExecutionController()
        self.plan_controller = AuditPlanController()

    def test_complete_audit_plan_to_execution_workflow(self):
        """Test complete workflow from audit planning to execution"""
        # Step 1: Create audit plan
        plan_doc = Mock()
        plan_doc.doctype = 'Audit Plan'
        plan_doc.name = 'PLAN-2024-001'
        plan_doc.plan_title = 'Q1 Financial Audit Plan'
        plan_doc.audit_scope = 'Financial Statements Review'
        plan_doc.planned_start_date = '2024-01-15'
        plan_doc.planned_end_date = '2024-03-15'
        plan_doc.estimated_hours = 160
        plan_doc.assigned_auditors = ['auditor1@example.com', 'auditor2@example.com']

        # Validate plan
        plan_validation = self.plan_controller.validate_plan(plan_doc)
        self.assertTrue(plan_validation['valid'])

        # Step 2: Create audit execution from plan
        execution_doc = Mock()
        execution_doc.doctype = 'Audit Execution'
        execution_doc.name = 'EXEC-2024-001'
        execution_doc.audit_plan = 'PLAN-2024-001'
        execution_doc.execution_title = 'Q1 Financial Audit Execution'
        execution_doc.actual_start_date = '2024-01-15'
        execution_doc.status = 'In Progress'

        # Validate execution
        execution_validation = self.execution_controller.validate_execution(execution_doc)
        self.assertTrue(execution_validation['valid'])

        # Step 3: Create finding during execution
        finding_doc = Mock()
        finding_doc.doctype = 'Audit Finding'
        finding_doc.name = 'FIND-2024-001'
        finding_doc.audit_execution = 'EXEC-2024-001'
        finding_doc.finding_title = 'Control Weakness in Revenue Recognition'
        finding_doc.severity = 'High'
        finding_doc.status = 'Open'
        finding_doc.description = 'Revenue recognition controls need strengthening'
        finding_doc.recommendation = 'Implement additional approval layers'

        # Validate finding
        finding_validation = self.finding_controller.validate_finding(finding_doc)
        self.assertTrue(finding_validation['valid'])

        # Step 4: Test notification creation for finding
        with patch.object(self.api, 'send_notification') as mock_notify:
            self.finding_controller.create_finding_notification(finding_doc)
            mock_notify.assert_called_with(
                'finding_created',
                unittest.mock.ANY,  # Recipients would be determined dynamically
                unittest.mock.ANY   # Finding data
            )

    def test_integrity_check_to_report_workflow(self):
        """Test workflow from integrity check to report generation"""
        # Step 1: Run integrity check
        check_result = self.api.run_integrity_check('full')
        self.assertIn('checks', check_result)
        self.assertIn('summary', check_result)

        # Step 2: Verify report creation (would be triggered by controller)
        # This would normally create an Audit Integrity Report document
        self.assertIsInstance(check_result['checks'], list)

    def test_audit_trail_workflow(self):
        """Test audit trail creation and retrieval workflow"""
        # Step 1: Create mock document operation
        doc = Mock()
        doc.doctype = 'GL Entry'
        doc.name = 'GLE-TEST-001'
        doc.posting_date = '2024-01-15'
        doc.account = 'Test Revenue Account'
        doc.debit = 5000.00
        doc.credit = 0.00

        # Step 2: Create audit entry
        self.api._create_audit_entry(doc, 'Create', 'Financial')

        # Step 3: Retrieve audit trail
        trail = self.api.get_audit_trail(doctype='GL Entry')
        self.assertIsInstance(trail, dict)
        self.assertIn('entries', trail)

    def test_dashboard_update_workflow(self):
        """Test dashboard update workflow across modules"""
        # Step 1: Update dashboard data
        result = self.api.update_dashboard_data()

        # Step 2: Verify update result structure
        self.assertIn('timestamp', result)
        self.assertIn('modules_updated', result)
        self.assertIn('overall_status', result)

        # Step 3: Verify each module was updated
        modules_updated = result['modules_updated']
        expected_modules = ['audit_trail', 'discovery', 'templates', 'hooks',
                          'analyzer', 'payroll', 'hr', 'inventory', 'procurement', 'access']

        for module in expected_modules:
            self.assertIn(module, modules_updated)

    def test_notification_workflow(self):
        """Test complete notification workflow"""
        notification_types = [
            'finding_created',
            'audit_completed',
            'integrity_check_failed'
        ]

        for notification_type in notification_types:
            with self.subTest(notification_type=notification_type):
                with patch('frappe.sendmail') as mock_sendmail:
                    result = self.api.send_notification(
                        notification_type,
                        ['test@example.com'],
                        {'test': 'data'}
                    )

                    self.assertEqual(result['status'], 'success')
                    self.assertEqual(result['notification_type'], notification_type)
                    mock_sendmail.assert_called_once()


class TestControllerIntegration(FrappeTestCase):
    """Integration tests for controller interactions"""

    def setUp(self):
        self.api = AuditAPI()

    def test_controller_api_integration(self):
        """Test that controllers properly integrate with API"""
        # Test that controllers can access API methods
        self.assertTrue(hasattr(self.api, 'get_audit_trail'))
        self.assertTrue(hasattr(self.api, 'update_dashboard_data'))
        self.assertTrue(hasattr(self.api, 'send_notification'))
        self.assertTrue(hasattr(self.api, '_create_audit_entry'))

    def test_hook_integration_simulation(self):
        """Test hook integration simulation"""
        # Simulate what happens when hooks trigger controllers
        doc = Mock()
        doc.doctype = 'GL Entry'
        doc.name = 'GLE-HOOK-TEST'

        # This would normally be called by the hook system
        # but we can test the API method directly
        self.api._create_audit_entry(doc, 'Update', 'Financial')

        # Verify audit trail was created
        trail = self.api.get_audit_trail(doctype='GL Entry')
        self.assertIsInstance(trail, dict)


class TestSystemHealthIntegration(FrappeTestCase):
    """Integration tests for system health monitoring"""

    def setUp(self):
        self.api = AuditAPI()

    def test_system_status_integration(self):
        """Test system status provides integrated view"""
        status = self.api.get_system_status()

        # Verify all expected components are present
        required_keys = ['overall_status', 'modules', 'timestamp', 'alerts', 'metrics']
        for key in required_keys:
            self.assertIn(key, status)

        # Verify modules section includes all expected modules
        modules = status['modules']
        expected_modules = ['audit_trail', 'discovery', 'templates', 'hooks',
                          'analyzer', 'payroll', 'hr', 'inventory', 'procurement', 'access']

        for module in expected_modules:
            self.assertIn(module, modules)

    def test_metrics_calculation_integration(self):
        """Test metrics calculation across modules"""
        status = self.api.get_system_status()
        metrics = status['metrics']

        # Verify key metrics are calculated
        expected_metrics = [
            'total_audit_entries',
            'active_catalogs',
            'audit_templates',
            'integrity_reports',
            'sync_status',
            'open_findings',
            'completed_audits'
        ]

        for metric in expected_metrics:
            self.assertIn(metric, metrics)

    def test_alert_generation_integration(self):
        """Test alert generation based on system status"""
        # This would test that alerts are properly generated
        # based on module statuses and metrics
        status = self.api.get_system_status()
        alerts = status['alerts']

        self.assertIsInstance(alerts, list)


class TestPerformanceIntegration(FrappeTestCase):
    """Integration tests for performance validation"""

    def setUp(self):
        self.api = AuditAPI()

    def test_bulk_operation_performance(self):
        """Test performance of bulk operations"""
        import time

        # Test multiple API calls
        start_time = time.time()

        for _ in range(10):
            self.api.get_system_status()
            self.api.get_audit_trail(limit=5)

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete within reasonable time (adjust threshold as needed)
        self.assertLess(total_time, 30.0)  # 30 seconds for 20 operations

    def test_concurrent_access_simulation(self):
        """Test simulated concurrent access"""
        # This would test thread safety and concurrent access
        # For now, just verify methods can be called multiple times rapidly
        results = []
        for _ in range(5):
            result = self.api.get_system_status()
            results.append(result)

        self.assertEqual(len(results), 5)
        for result in results:
            self.assertIn('overall_status', result)


if __name__ == '__main__':
    unittest.main()