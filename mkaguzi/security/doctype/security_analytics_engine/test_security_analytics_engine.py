# -*- coding: utf-8 -*-
import unittest
import frappe
from mkaguzi.security.doctype.security_analytics_engine.security_analytics_engine import SecurityAnalyticsEngine
import json

class TestSecurityAnalyticsEngine(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        self.test_engine_data = {
            'analytics_engine_id': 'TEST-SAE-001',
            'engine_name': 'Test Security Analytics Engine',
            'engine_version': '1.0.0',
            'description': 'Test engine for security analytics',
            'status': 'Draft',
            'security_data_sources': json.dumps({
                'sources': [{
                    'type': 'log',
                    'source': 'system_logs',
                    'frequency': 'real_time',
                    'retention': '30_days'
                }]
            }),
            'log_sources': json.dumps({
                'sources': [{
                    'name': 'system_logs',
                    'type': 'syslog',
                    'location': '/var/log/syslog'
                }]
            }),
            'threat_intelligence_feeds': json.dumps({
                'feeds': [{
                    'name': 'threat_feed_1',
                    'url': 'https://threatfeed.example.com',
                    'format': 'json'
                }]
            }),
            'real_time_analytics': json.dumps({
                'enabled': True,
                'processing_interval': 60,
                'batch_size': 1000
            }),
            'batch_analytics': json.dumps({
                'enabled': True,
                'schedule': 'daily',
                'historical_window': '7_days'
            }),
            'predictive_analytics': json.dumps({
                'enabled': True,
                'models': ['threat_prediction', 'behavior_analysis']
            }),
            'behavioral_analytics': json.dumps({
                'enabled': True,
                'user_profiling': True,
                'anomaly_detection': True
            }),
            'anomaly_detection': json.dumps({
                'algorithm': 'isolation_forest',
                'threshold': 0.8,
                'sensitivity': 'high'
            }),
            'pattern_recognition': json.dumps({
                'enabled': True,
                'patterns': ['brute_force', 'data_exfiltration']
            }),
            'correlation_engine': json.dumps({
                'enabled': True,
                'correlation_window': '5_minutes',
                'min_events': 3
            }),
            'risk_scoring': json.dumps({
                'enabled': True,
                'scoring_model': 'weighted_average',
                'factors': ['severity', 'frequency', 'impact']
            }),
            'alert_rules': json.dumps({
                'rules': [{
                    'name': 'high_severity_alert',
                    'condition': 'severity == "high"',
                    'severity': 'high',
                    'action': 'notify_security_team'
                }]
            }),
            'escalation_policies': json.dumps({
                'policies': [{
                    'name': 'critical_escalation',
                    'threshold': 'critical',
                    'escalate_to': 'security_manager'
                }]
            }),
            'notification_channels': json.dumps({
                'email': {
                    'enabled': True,
                    'recipients': ['security@mkaguzi.com']
                },
                'slack': {
                    'enabled': False
                }
            }),
            'suppression_rules': json.dumps({
                'rules': [{
                    'name': 'maintenance_window',
                    'condition': 'time between 02:00 and 04:00',
                    'suppress_alerts': True
                }]
            }),
            'security_dashboards': json.dumps({
                'dashboards': [{
                    'name': 'security_overview',
                    'widgets': ['threat_map', 'alert_summary', 'risk_score']
                }]
            }),
            'executive_reports': json.dumps({
                'reports': [{
                    'name': 'monthly_security_report',
                    'schedule': 'monthly',
                    'recipients': ['executives@mkaguzi.com']
                }]
            }),
            'compliance_reports': json.dumps({
                'reports': [{
                    'name': 'gdpr_compliance',
                    'framework': 'GDPR',
                    'schedule': 'quarterly'
                }]
            }),
            'custom_reports': json.dumps({
                'reports': []
            }),
            'processing_throughput': 1500.0,
            'detection_accuracy': 97.5,
            'false_positive_rate': 2.3,
            'response_time': 120.0,
            'uptime_percentage': 99.8,
            'threat_feeds': json.dumps({
                'feeds': [{
                    'name': 'alienvault_otx',
                    'url': 'https://otx.alienvault.com/api/v1/indicators',
                    'format': 'json',
                    'api_key': 'test_key'
                }]
            }),
            'ioc_database': json.dumps({
                'ip': [],
                'domain': [],
                'hash': []
            }),
            'vulnerability_scanning': json.dumps({
                'enabled': True,
                'scanner': 'nessus',
                'schedule': 'weekly'
            }),
            'asset_discovery': json.dumps({
                'enabled': True,
                'methods': ['nmap', 'shodan'],
                'frequency': 'daily'
            }),
            'machine_learning_models': json.dumps({
                'models': [{
                    'name': 'threat_classifier',
                    'type': 'classification',
                    'algorithm': 'random_forest',
                    'accuracy': 0.95
                }]
            }),
            'statistical_models': json.dumps({
                'models': [{
                    'name': 'anomaly_detector',
                    'type': 'unsupervised',
                    'algorithm': 'isolation_forest'
                }]
            }),
            'rule_based_engines': json.dumps({
                'engines': [{
                    'name': 'signature_engine',
                    'rules_count': 1000,
                    'last_updated': '2025-01-29'
                }]
            }),
            'model_performance': json.dumps({
                'metrics': {
                    'accuracy': 0.96,
                    'precision': 0.94,
                    'recall': 0.92,
                    'f1_score': 0.93
                }
            }),
            'security_events': json.dumps([]),
            'analytics_logs': json.dumps([]),
            'model_predictions': json.dumps([]),
            'alert_history': json.dumps([]),
            'performance_logs': json.dumps([])
        }

    def test_engine_creation(self):
        """Test creating a security analytics engine"""
        engine = frappe.get_doc({
            'doctype': 'Security Analytics Engine',
            **self.test_engine_data
        })

        # Test autoname
        engine.autoname()
        self.assertTrue(engine.analytics_engine_id.startswith('SAE-'))

        # Test validation
        try:
            engine.validate()
            validation_passed = True
        except Exception:
            validation_passed = False

        self.assertTrue(validation_passed, "Engine validation should pass with valid data")

    def test_data_sources_validation(self):
        """Test data sources validation"""
        engine = frappe.get_doc({
            'doctype': 'Security Analytics Engine',
            **self.test_engine_data
        })

        # Test with missing data sources
        engine.security_data_sources = None
        with self.assertRaises(frappe.ValidationError):
            engine.validate_data_sources()

        # Test with invalid JSON
        engine.security_data_sources = '{"invalid": json}'
        with self.assertRaises(frappe.ValidationError):
            engine.validate_data_sources()

    def test_analytics_configuration_validation(self):
        """Test analytics configuration validation"""
        engine = frappe.get_doc({
            'doctype': 'Security Analytics Engine',
            **self.test_engine_data
        })

        # Test with missing real-time analytics
        engine.real_time_analytics = None
        with self.assertRaises(frappe.ValidationError):
            engine.validate_analytics_configuration()

    def test_performance_metrics_validation(self):
        """Test performance metrics validation"""
        engine = frappe.get_doc({
            'doctype': 'Security Analytics Engine',
            **self.test_engine_data
        })

        # Test negative throughput
        engine.processing_throughput = -100
        with self.assertRaises(frappe.ValidationError):
            engine.validate_performance_metrics()

        # Test invalid accuracy percentage
        engine.processing_throughput = 1500.0
        engine.detection_accuracy = 150.0
        with self.assertRaises(frappe.ValidationError):
            engine.validate_performance_metrics()

    def test_diagnostic_check(self):
        """Test diagnostic check functionality"""
        engine = frappe.get_doc({
            'doctype': 'Security Analytics Engine',
            **self.test_engine_data
        })

        diagnostics = engine.run_diagnostic_check()

        self.assertIn('data_sources', diagnostics)
        self.assertIn('analytics_models', diagnostics)
        self.assertIn('threat_feeds', diagnostics)
        self.assertIn('performance', diagnostics)
        self.assertIn('timestamp', diagnostics)

    def test_engine_operations(self):
        """Test engine start/stop operations"""
        engine = frappe.get_doc({
            'doctype': 'Security Analytics Engine',
            **self.test_engine_data
        })

        # Test start engine
        initial_status = engine.status
        engine.start_engine()
        self.assertEqual(engine.status, 'Active')

        # Test stop engine
        engine.stop_engine()
        self.assertEqual(engine.status, 'Suspended')

if __name__ == '__main__':
    unittest.main()