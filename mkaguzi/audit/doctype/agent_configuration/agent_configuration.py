# -*- coding: utf-8 -*-
# Copyright (c) 2025, mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
import json


class AgentConfiguration(Document):
	"""Agent Configuration Document Controller"""

	def validate(self):
		"""Validate the configuration before saving"""
		self.validate_config_json()
		self.validate_agent_type()
		self.set_defaults()

	def validate_config_json(self):
		"""Validate that config_json contains valid JSON"""
		if self.config_json:
			try:
				config = json.loads(self.config_json)
				# Ensure it's a dictionary
				if not isinstance(config, dict):
					frappe.throw(_("Configuration JSON must be an object/dictionary"))
			except json.JSONDecodeError:
				frappe.throw(_("Invalid JSON format in Configuration"))

	def validate_agent_type(self):
		"""Validate agent type against registry"""
		from mkaguzi.agents.agent_registry import AgentRegistry

		agent_type_lower = self.agent_type.lower() if self.agent_type else ""
		if not AgentRegistry.agent_exists(agent_type_lower):
			frappe.throw(_("Unknown agent type: {0}").format(self.agent_type))

	def set_defaults(self):
		"""Set default values"""
		if not self.created_by:
			self.created_by = frappe.session.user

		self.modified_by = frappe.session.user

		# Set default priority if not set
		if not self.priority:
			self.priority = "Medium"

		# Validate timeout is positive
		if self.timeout_seconds and self.timeout_seconds <= 0:
			frappe.throw(_("Timeout must be greater than 0 seconds"))

		# Validate resource limits are positive
		if self.max_memory_mb and self.max_memory_mb <= 0:
			frappe.throw(_("Max Memory must be greater than 0 MB"))

		if self.max_cpu_percent and (self.max_cpu_percent <= 0 or self.max_cpu_percent > 100):
			frappe.throw(_("Max CPU must be between 0 and 100 percent"))

		if self.max_concurrent_tasks and self.max_concurrent_tasks <= 0:
			frappe.throw(_("Max Concurrent Tasks must be greater than 0"))

	def on_update(self):
		"""Actions when configuration is updated"""
		self.reload_registry()

	def on_trash(self):
		"""Actions when configuration is deleted"""
		self.reload_registry()

	def reload_registry(self):
		"""Reload agent registry from database"""
		try:
			from mkaguzi.agents.agent_registry import AgentRegistry
			AgentRegistry.load_from_db()
		except Exception as e:
			frappe.log_error(_("Registry Reload Error: {0}").format(str(e)), "Agent Configuration")

	def get_merged_config(self):
		"""
		Get merged configuration (default + custom)

		Returns:
			dict: Merged configuration dictionary
		"""
		from mkaguzi.agents.agent_registry import AgentRegistry

		# Get default config from registry
		default_config = AgentRegistry.get_default_config(self.agent_type.lower()) or {}

		# Parse custom config
		custom_config = {}
		if self.config_json:
			try:
				custom_config = json.loads(self.config_json)
			except json.JSONDecodeError:
				pass

		# Merge: custom overrides default
		merged_config = default_config.copy()
		merged_config.update(custom_config)

		# Add resource limits
		if self.timeout_seconds:
			merged_config['timeout_seconds'] = self.timeout_seconds
		if self.max_memory_mb:
			merged_config['max_memory_mb'] = self.max_memory_mb
		if self.max_cpu_percent:
			merged_config['max_cpu_percent'] = self.max_cpu_percent
		if self.max_concurrent_tasks:
			merged_config['max_concurrent_tasks'] = self.max_concurrent_tasks
		if self.enable_logging is not None:
			merged_config['enable_logging'] = self.enable_logging
		if self.log_level:
			merged_config['log_level'] = self.log_level
		if self.notification_on_failure is not None:
			merged_config['notification_on_failure'] = self.notification_on_failure

		return merged_config


# Whitelisted functions

@frappe.whitelist()
def get_agent_config(agent_type):
	"""
	Get active configuration for an agent type

	Args:
		agent_type: Type of agent (financial, risk, compliance, discovery, notification)

	Returns:
		dict: Configuration dictionary with merged config
	"""
	try:
		agent_type_title = agent_type.title() if agent_type else ""

		configs = frappe.get_all('Agent Configuration',
			filters={
				'agent_type': agent_type_title,
				'is_active': 1
			},
			fields=['name', 'config_json', 'timeout_seconds', 'priority',
			       'max_memory_mb', 'max_cpu_percent', 'max_concurrent_tasks',
			       'enable_logging', 'log_level', 'notification_on_failure'],
			order_by='priority desc',
			limit=1
		)

		if configs:
			config_doc = frappe.get_doc('Agent Configuration', configs[0]['name'])
			result = config_doc.get_merged_config()
			result['configuration_name'] = config_doc.configuration_name
			result['name'] = config_doc.name
			return result
		else:
			# Return default from registry
			from mkaguzi.agents.agent_registry import AgentRegistry
			return AgentRegistry.get_default_config(agent_type.lower())

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _('Get Agent Config Error'))
		frappe.throw(str(e))


@frappe.whitelist()
def get_all_agent_configurations():
	"""
	Get all agent configurations

	Returns:
		list: List of all configurations
	"""
	try:
		configs = frappe.get_all('Agent Configuration',
			fields=['name', 'agent_type', 'configuration_name', 'is_active',
			       'priority', 'execution_schedule', 'timeout_seconds', 'modified'],
			order_by='agent_type, priority desc'
		)
		return configs

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _('Get Agent Configurations Error'))
		frappe.throw(str(e))


@frappe.whitelist()
def get_agent_config_schema(agent_type):
	"""
	Get the configuration schema for an agent type

	Args:
		agent_type: Type of agent

	Returns:
		dict: Schema showing available configuration options
	"""
	from mkaguzi.agents.agent_registry import AgentRegistry

	try:
		# Get agent class to understand config options
		agent_class = AgentRegistry.get_agent_class(agent_type.lower())

		if agent_class:
			# Return default config as schema reference
			default_config = AgentRegistry.get_default_config(agent_type.lower())

			# Define schema based on agent type
			schema = {
				'agent_type': agent_type.title(),
				'default_config': default_config,
				'description': _get_agent_description(agent_type.lower()),
				'available_parameters': _get_available_parameters(agent_type.lower())
			}

			return schema
		else:
			return {'error': 'Unknown agent type'}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _('Get Agent Config Schema Error'))
		return {'error': str(e)}


@frappe.whitelist()
def test_agent_config(config_name):
	"""
	Test an agent configuration by validating it

	Args:
		config_name: Name of the Agent Configuration document

	Returns:
		dict: Test results with validity status
	"""
	try:
		config_doc = frappe.get_doc('Agent Configuration', config_name)

		# Get merged config
		merged_config = config_doc.get_merged_config()

		# Validate against agent registry
		from mkaguzi.agents.agent_registry import AgentRegistry
		agent_class = AgentRegistry.get_agent_class(config_doc.agent_type.lower())

		result = {
			'valid': True,
			'configuration_name': config_doc.configuration_name,
			'agent_type': config_doc.agent_type,
			'merged_config': merged_config,
			'message': 'Configuration is valid'
		}

		if agent_class:
			result['agent_class'] = agent_class.__name__
		else:
			result['valid'] = False
			result['message'] = 'Agent class not found'

		return result

	except Exception as e:
		return {
			'valid': False,
			'error': str(e),
			'message': 'Configuration validation failed'
		}


def _get_agent_description(agent_type):
	"""Get description for an agent type"""
	descriptions = {
		'financial': 'Financial transaction analysis and fraud detection',
		'risk': 'Predictive risk assessment and dynamic threshold adjustment',
		'compliance': 'Regulatory compliance verification and gap analysis',
		'discovery': 'Automatic doctype discovery and catalog updates',
		'notification': 'Intelligent alerting and notification management'
	}
	return descriptions.get(agent_type, 'Unknown agent type')


def _get_available_parameters(agent_type):
	"""Get available configuration parameters for an agent type"""
	parameters = {
		'financial': {
			'max_batch_size': {'type': 'int', 'default': 1000, 'description': 'Maximum records to process per batch'},
			'timeout_seconds': {'type': 'int', 'default': 300, 'description': 'Execution timeout in seconds'},
			'retry_count': {'type': 'int', 'default': 3, 'description': 'Number of retries on failure'},
			'anomaly_threshold': {'type': 'float', 'default': 2.5, 'description': 'Standard deviations for anomaly detection'},
			'enable_benford_analysis': {'type': 'bool', 'default': True, 'description': 'Enable Benford\'s Law analysis'},
			'enable_duplicate_detection': {'type': 'bool', 'default': True, 'description': 'Enable duplicate payment detection'}
		},
		'risk': {
			'prediction_horizon_days': {'type': 'int', 'default': 30, 'description': 'Days ahead to predict risks'},
			'threshold_sensitivity': {'type': 'float', 'default': 0.5, 'description': 'Sensitivity for dynamic thresholds (0-1)'},
			'min_data_points': {'type': 'int', 'default': 100, 'description': 'Minimum data points for prediction'},
			'enable_ml_prediction': {'type': 'bool', 'default': True, 'description': 'Enable ML-based risk prediction'}
		},
		'compliance': {
			'auto_update_checks': {'type': 'bool', 'default': True, 'description': 'Automatically update compliance checks'},
			'severity_threshold': {'type': 'select', 'default': 'medium', 'options': ['low', 'medium', 'high', 'critical'], 'description': 'Minimum severity for gaps'}
		},
		'discovery': {
			'scan_frequency_hours': {'type': 'int', 'default': 24, 'description': 'Hours between discovery scans'},
			'include_custom_doctypes': {'type': 'bool', 'default': True, 'description': 'Include custom doctypes in discovery'}
		},
		'notification': {
			'aggregation_window_minutes': {'type': 'int', 'default': 5, 'description': 'Minutes to aggregate similar alerts'},
			'escalation_timeout_minutes': {'type': 'int', 'default': 60, 'description': 'Minutes before escalation'},
			'digest_frequency': {'type': 'select', 'default': 'daily', 'options': ['hourly', 'daily', 'weekly'], 'description': 'Digest frequency'}
		}
	}
	return parameters.get(agent_type, {})
