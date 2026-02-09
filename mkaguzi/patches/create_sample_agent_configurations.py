# -*- coding: utf-8 -*-
# Copyright (c) 2025, mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute():
	"""
	Create sample Agent Configuration records for each agent type.
	This patch is run during bench migrate.
	"""

	sample_configs = [
		{
			'agent_type': 'Financial',
			'configuration_name': 'Default Financial Analysis',
			'description': 'Standard configuration for financial transaction analysis and fraud detection',
			'is_active': 1,
			'priority': 'High',
			'config_json': '''{
				"max_batch_size": 1000,
				"timeout_seconds": 300,
				"retry_count": 3,
				"log_level": "INFO",
				"anomaly_threshold": 2.5,
				"enable_benford_analysis": true,
				"enable_duplicate_detection": true,
				"enable_round_number_detection": true,
				"min_transaction_amount": 0.01
			}''',
			'execution_schedule': None,
			'timeout_seconds': 300,
			'max_memory_mb': 512,
			'max_cpu_percent': 80,
			'max_concurrent_tasks': 1,
			'enable_logging': 1,
			'log_level': 'INFO',
			'notification_on_failure': 1
		},
		{
			'agent_type': 'Financial',
			'configuration_name': 'High Volume Financial Processing',
			'description': 'Configuration for processing large volumes of financial data with increased batch size',
			'is_active': 1,
			'priority': 'Medium',
			'config_json': '''{
				"max_batch_size": 5000,
				"timeout_seconds": 600,
				"retry_count": 2,
				"log_level": "WARNING",
				"anomaly_threshold": 3.0,
				"enable_benford_analysis": false,
				"enable_duplicate_detection": true,
				"enable_round_number_detection": false,
				"min_transaction_amount": 100.0
			}''',
			'execution_schedule': '0 2 * * *',
			'timeout_seconds': 600,
			'max_memory_mb': 1024,
			'max_cpu_percent': 90,
			'max_concurrent_tasks': 2,
			'enable_logging': 1,
			'log_level': 'WARNING',
			'notification_on_failure': 1
		},
		{
			'agent_type': 'Risk',
			'configuration_name': 'Default Risk Assessment',
			'description': 'Standard configuration for predictive risk assessment and dynamic threshold adjustment',
			'is_active': 1,
			'priority': 'High',
			'config_json': '''{
				"prediction_horizon_days": 30,
				"threshold_sensitivity": 0.5,
				"min_data_points": 100,
				"log_level": "INFO",
				"enable_ml_prediction": true,
				"risk_decay_factor": 0.95,
				"trend_analysis_window_days": 90
			}''',
			'execution_schedule': '0 3 * * *',
			'timeout_seconds': 300,
			'max_memory_mb': 512,
			'max_cpu_percent': 75,
			'max_concurrent_tasks': 1,
			'enable_logging': 1,
			'log_level': 'INFO',
			'notification_on_failure': 1
		},
		{
			'agent_type': 'Risk',
			'configuration_name': 'Conservative Risk Assessment',
			'description': 'Conservative risk configuration with higher sensitivity and longer prediction horizon',
			'is_active': 0,
			'priority': 'Medium',
			'config_json': '''{
				"prediction_horizon_days": 60,
				"threshold_sensitivity": 0.3,
				"min_data_points": 50,
				"log_level": "DEBUG",
				"enable_ml_prediction": true,
				"risk_decay_factor": 0.9,
				"trend_analysis_window_days": 180
			}''',
			'execution_schedule': None,
			'timeout_seconds': 600,
			'max_memory_mb': 1024,
			'max_cpu_percent': 70,
			'max_concurrent_tasks': 1,
			'enable_logging': 1,
			'log_level': 'DEBUG',
			'notification_on_failure': 1
		},
		{
			'agent_type': 'Compliance',
			'configuration_name': 'Default Compliance Verification',
			'description': 'Standard configuration for regulatory compliance verification and gap analysis',
			'is_active': 1,
			'priority': 'High',
			'config_json': '''{
				"auto_update_checks": true,
				"severity_threshold": "medium",
				"log_level": "INFO",
				"regulatory_sources": [],
				"gap_analysis_enabled": true,
				"evidence_collection_enabled": true
			}''',
			'execution_schedule': '0 1 * * *',
			'timeout_seconds': 300,
			'max_memory_mb': 256,
			'max_cpu_percent': 70,
			'max_concurrent_tasks': 1,
			'enable_logging': 1,
			'log_level': 'INFO',
			'notification_on_failure': 1
		},
		{
			'agent_type': 'Compliance',
			'configuration_name': 'High Sensitivity Compliance',
			'description': 'High sensitivity compliance checking with low severity threshold for critical requirements',
			'is_active': 0,
			'priority': 'Medium',
			'config_json': '''{
				"auto_update_checks": true,
				"severity_threshold": "low",
				"log_level": "DEBUG",
				"regulatory_sources": [],
				"gap_analysis_enabled": true,
				"evidence_collection_enabled": true,
				"detailed_reporting": true
			}''',
			'execution_schedule': None,
			'timeout_seconds': 600,
			'max_memory_mb': 512,
			'max_cpu_percent': 80,
			'max_concurrent_tasks': 1,
			'enable_logging': 1,
			'log_level': 'DEBUG',
			'notification_on_failure': 1
		},
		{
			'agent_type': 'Discovery',
			'configuration_name': 'Default Doctype Discovery',
			'description': 'Standard configuration for automatic doctype discovery and catalog updates',
			'is_active': 1,
			'priority': 'High',
			'config_json': '''{
				"scan_frequency_hours": 24,
				"include_custom_doctypes": true,
				"auto_update_catalog": true,
				"detect_field_changes": true,
				"validate_relationships": true,
				"log_level": "INFO"
			}''',
			'execution_schedule': '0 4 * * *',
			'timeout_seconds': 300,
			'max_memory_mb': 256,
			'max_cpu_percent': 60,
			'max_concurrent_tasks': 1,
			'enable_logging': 1,
			'log_level': 'INFO',
			'notification_on_failure': 0
		},
		{
			'agent_type': 'Discovery',
			'configuration_name': 'Rapid Discovery Scan',
			'description': 'Faster discovery scan with more frequent execution for development environments',
			'is_active': 0,
			'priority': 'Low',
			'config_json': '''{
				"scan_frequency_hours": 6,
				"include_custom_doctypes": true,
				"auto_update_catalog": true,
				"detect_field_changes": true,
				"validate_relationships": false,
				"log_level": "DEBUG"
			}''',
			'execution_schedule': None,
			'timeout_seconds': 180,
			'max_memory_mb': 256,
			'max_cpu_percent': 70,
			'max_concurrent_tasks': 2,
			'enable_logging': 1,
			'log_level': 'DEBUG',
			'notification_on_failure': 0
		},
		{
			'agent_type': 'Notification',
			'configuration_name': 'Default Notification Settings',
			'description': 'Standard configuration for intelligent alerting and notification management',
			'is_active': 1,
			'priority': 'High',
			'config_json': '''{
				"aggregation_window_minutes": 5,
				"escalation_timeout_minutes": 60,
				"digest_frequency": "daily",
				"log_level": "INFO",
				"max_digest_items": 50,
				"enable_smart_routing": true,
				"enable_alert_deduplication": true
			}''',
			'execution_schedule': '*/30 * * * *',
			'timeout_seconds': 120,
			'max_memory_mb': 128,
			'max_cpu_percent': 50,
			'max_concurrent_tasks': 3,
			'enable_logging': 1,
			'log_level': 'INFO',
			'notification_on_failure': 1
		},
		{
			'agent_type': 'Notification',
			'configuration_name': 'High Volume Notification Processing',
			'description': 'Configuration for high-volume alert processing with extended aggregation window',
			'is_active': 0,
			'priority': 'Medium',
			'config_json': '''{
				"aggregation_window_minutes": 15,
				"escalation_timeout_minutes": 120,
				"digest_frequency": "daily",
				"log_level": "WARNING",
				"max_digest_items": 200,
				"enable_smart_routing": true,
				"enable_alert_deduplication": true
			}''',
			'execution_schedule': None,
			'timeout_seconds': 180,
			'max_memory_mb': 256,
			'max_cpu_percent': 70,
			'max_concurrent_tasks': 5,
			'enable_logging': 1,
			'log_level': 'WARNING',
			'notification_on_failure': 1
		}
	]

	# Create each configuration if it doesn't exist
	for config in sample_configs:
		# Check if configuration already exists
		existing = frappe.db.exists('Agent Configuration', {
			'configuration_name': config['configuration_name']
		})

		if not existing:
			try:
				doc = frappe.get_doc({
					'doctype': 'Agent Configuration',
					**config
				})
				doc.insert()
				frappe.msgprint(frappe._("Created Agent Configuration: {0}").format(config['configuration_name']))
			except Exception as e:
				frappe.log_error(frappe._("Failed to create Agent Configuration {0}: {1}").format(
					config['configuration_name'], str(e)))
		else:
			# Update existing configuration if needed
			try:
				doc = frappe.get_doc('Agent Configuration', config['configuration_name'])
				doc.update(config)
				doc.save()
				frappe.msgprint(frappe._("Updated Agent Configuration: {0}").format(config['configuration_name']))
			except Exception as e:
				frappe.log_error(frappe._("Failed to update Agent Configuration {0}: {1}").format(
					config['configuration_name'], str(e)))

	frappe.msgprint(frappe._("Agent Configuration setup complete!"))
