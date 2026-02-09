# -*- coding: utf-8 -*-
# Copyright (c) 2025, mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import json
from datetime import datetime, timedelta


def run_quarterly_agents():
	"""
	Run all agents quarterly (Jan 1, Apr 1, Jul 1, Oct 1).
	This is scheduled via hooks.py scheduler_events using Frappe v16 cron.
	"""
	try:
		frappe.log("Starting quarterly agent execution", "Agent Scheduler")

		# Load scheduling config from Mkaguzi Settings
		try:
			from mkaguzi.utils.settings import get_scheduling_config
			sched_cfg = get_scheduling_config()
		except Exception:
			sched_cfg = {
				"financial_task_limit": 1000,
				"fraud_detection_limit": 500,
				"risk_assessment_limit": 100,
				"risk_prediction_days": 30,
			}

		# Get all active agent configurations
		active_configs = frappe.get_all('Agent Configuration',
			filters={'is_active': 1},
			fields=['agent_type', 'configuration_name', 'config_json']
		)

		# Group by agent type (use highest priority config per type)
		agent_configs = {}
		for config in active_configs:
			agent_type = config['agent_type']
			if agent_type not in agent_configs:
				agent_configs[agent_type] = config

		# Define tasks for each agent type
		agent_tasks = {
			'Financial': [
				{'task_type': 'analyze_transactions', 'limit': sched_cfg['financial_task_limit']},
				{'task_type': 'detect_fraud', 'limit': sched_cfg['fraud_detection_limit']}
			],
			'Risk': [
				{'task_type': 'assess_financial_risk', 'limit': sched_cfg['risk_assessment_limit']},
				{'task_type': 'predict_risks', 'days_ahead': sched_cfg['risk_prediction_days']}
			],
			'Compliance': [
				{'task_type': 'verify_compliance', 'severity_filter': 'high'}
			],
			'Discovery': [
				{'task_type': 'discover_doctypes', 'include_custom': True}
			],
			'Notification': [
				{'task_type': 'aggregate_alerts', 'aggregation_window_minutes': 60}
			],
			'Asset': [
				{'task_type': 'analyze_assets', 'limit': sched_cfg.get('asset_analysis_limit', 500)},
				{'task_type': 'review_depreciation', 'limit': sched_cfg.get('depreciation_review_limit', 200)}
			]
		}

		# Execute each agent with its tasks
		results = {}
		for agent_type, config in agent_configs.items():
			try:
				results[agent_type] = run_agent_with_config(agent_type, config, agent_tasks.get(agent_type, []))
			except Exception as e:
				frappe.log_error(_("Failed to run {0} agent: {1}").format(agent_type, str(e)), "Agent Scheduler")
				results[agent_type] = {'status': 'failed', 'error': str(e)}

		# Log summary
		successful_count = sum(1 for r in results.values() if r.get('status') == 'success')
		frappe.log(_("Quarterly agent execution completed: {0}/{1} successful").format(
			successful_count, len(results)), "Agent Scheduler")

	except Exception as e:
		frappe.log_error(_("Quarterly agent execution failed: {0}").format(str(e)), "Agent Scheduler")


def run_agent_with_config(agent_type, config, tasks):
	"""
	Run an agent with its configuration and specified tasks.

	Args:
		agent_type: Type of agent (Financial, Risk, Compliance, Discovery, Notification)
		config: Agent Configuration document
		tasks: List of task dictionaries to execute

	Returns:
		dict: Execution results
	"""
	from mkaguzi.agents.agent_manager import get_agent_manager

	try:
		# Parse config JSON if available
		config_data = {}
		if config.get('config_json'):
			try:
				config_data = json.loads(config['config_json'])
			except json.JSONDecodeError:
				pass

		# Add resource limits from config
		if config.get('timeout_seconds'):
			config_data['timeout_seconds'] = config['timeout_seconds']
		if config.get('max_memory_mb'):
			config_data['max_memory_mb'] = config['max_memory_mb']

		# Get agent manager and spawn agent
		manager = get_agent_manager()
		agent_id = f"{agent_type.lower()}_scheduler_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

		agent = manager.spawn_agent(
			agent_type=agent_type.lower(),
			config=config_data,
			agent_id=agent_id
		)

		if not agent:
			return {
				'status': 'failed',
				'error': f'Failed to spawn {agent_type} agent'
			}

		# Execute all tasks for this agent
		task_results = []
		for task in tasks:
			try:
				result = agent.execute_task(task)
				task_results.append({
					'task_type': task.get('task_type'),
					'status': 'success' if result else 'failed',
					'result': result
				})
			except Exception as e:
				task_results.append({
					'task_type': task.get('task_type'),
					'status': 'error',
					'error': str(e)
				})

		# Stop the agent
		agent.stop()

		return {
			'status': 'success',
			'agent_id': agent_id,
			'configuration_name': config.get('configuration_name'),
			'tasks_executed': len(task_results),
			'task_results': task_results
		}

	except Exception as e:
		return {
			'status': 'failed',
			'error': str(e)
		}


@frappe.whitelist()
def run_agent_manually(agent_type, task_type, task_data=None):
	"""
	Manually run an agent with a specific task.

	API Endpoint: /api/method/mkaguzi.agents.scheduler.run_agent_manually

	Args:
		agent_type: Type of agent (financial, risk, compliance, discovery, notification)
		task_type: Type of task to execute
		task_data: Additional parameters for the task

	Returns:
		dict: Execution result
	"""
	try:
		from mkaguzi.agents.agent_manager import get_agent_manager

		# Get active configuration for this agent type
		config = frappe.get_all('Agent Configuration',
			filters={
				'agent_type': agent_type.title(),
				'is_active': 1
			},
			fields=['name', 'config_json', 'timeout_seconds', 'max_memory_mb'],
			order_by='priority desc',
			limit=1
		)

		if not config:
			# Use default configuration from registry
			from mkaguzi.agents.agent_registry import AgentRegistry
			config_data = AgentRegistry.get_default_config(agent_type.lower())
		else:
			# Parse configuration JSON
			config_data = {}
			if config[0].get('config_json'):
				try:
					config_data = json.loads(config[0]['config_json'])
				except json.JSONDecodeError:
					pass
			if config[0].get('timeout_seconds'):
				config_data['timeout_seconds'] = config[0]['timeout_seconds']
			if config[0].get('max_memory_mb'):
				config_data['max_memory_mb'] = config[0].get('max_memory_mb')

		# Spawn agent
		manager = get_agent_manager()
		agent = manager.spawn_agent(
			agent_type=agent_type.lower(),
			config=config_data
		)

		if not agent:
			frappe.throw(_("Failed to spawn {0} agent").format(agent_type))

		# Execute task
		result = agent.execute_task({
			'task_type': task_type,
			**(task_data or {})
		})

		# Stop agent and return result
		agent.stop()

		return {
			'success': True,
			'agent_type': agent_type,
			'task_type': task_type,
			'result': result
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Run Agent Manually Error"))
		frappe.throw(str(e))


@frappe.whitelist()
def run_all_agents(task_data=None):
	"""
	Run all active agents with their default tasks.

	API Endpoint: /api/method/mkaguzi.agents.scheduler.run_all_agents

	Args:
		task_data: Optional override data for tasks

	Returns:
		dict: Execution results for all agents
	"""
	try:
		frappe.log("Starting execution of all agents", "Agent Scheduler")

		# Get all active agent configurations
		active_configs = frappe.get_all('Agent Configuration',
			filters={'is_active': 1},
			fields=['agent_type', 'configuration_name', 'config_json']
		)

		# Group by agent type (use highest priority config per type)
		agent_configs = {}
		for config in active_configs:
			agent_type = config['agent_type']
			if agent_type not in agent_configs:
				agent_configs[agent_type] = config

		# Define default tasks for each agent type
		agent_tasks = {
			'Financial': {
				'task_type': 'analyze_transactions',
				'limit': 100
			},
			'Risk': {
				'task_type': 'assess_financial_risk',
				'limit': 100
			},
			'Compliance': {
				'task_type': 'verify_compliance'
			},
			'Discovery': {
				'task_type': 'discover_doctypes'
			},
			'Notification': {
				'task_type': 'process_pending'
			}
		}

		# Override with custom task data if provided
		if task_data:
			for agent_type, custom_tasks in task_data.items():
				if agent_type in agent_tasks:
					agent_tasks[agent_type].update(custom_tasks)

		# Execute each agent
		results = {}
		for agent_type, config in agent_configs.items():
			try:
				task = agent_tasks.get(agent_type, {})
				result = run_agent_with_config(agent_type, config, [task])
				results[agent_type] = result
			except Exception as e:
				frappe.log_error(_("Failed to run {0} agent: {1}").format(agent_type, str(e)), "Agent Scheduler")
				results[agent_type] = {'status': 'failed', 'error': str(e)}

		# Count successful executions
		successful = sum(1 for r in results.values() if r.get('status') == 'success')
		total = len(results)

		frappe.log(_("All agents execution completed: {0}/{1} successful").format(successful, total), "Agent Scheduler")

		return {
			'success': True,
			'message': f'{successful}/{total} agents executed successfully',
			'results': results
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Run All Agents Error"))
		frappe.throw(str(e))


@frappe.whitelist()
def get_agent_status():
	"""
	Get the current status of all agents.

	API Endpoint: /api/method/mkaguzi.agents.scheduler.get_agent_status

	Returns:
		dict: Status of all agents (active, running, etc.)
	"""
	try:
		from mkaguzi.agents.agent_manager import get_agent_manager

		manager = get_agent_manager()
		status = manager.get_system_status()

		# Add active configurations
		active_configs = frappe.get_all('Agent Configuration',
			filters={'is_active': 1},
			fields=['agent_type', 'configuration_name', 'priority', 'modified']
		)

		# Get recent execution logs
		recent_logs = frappe.get_all('Agent Execution Log',
			filters={'creation': ['>=', frappe.utils.nowdate() - timedelta(days=7)]},
			fields=['agent_type', 'task_type', 'status', 'duration_seconds', 'creation'],
			order_by='creation desc',
			limit=20
		)

		return {
		'active_agents': status.get('active_agents', 0),
		'total_agents': status.get('total_agents', 0),
			'active_configurations': active_configs,
			'recent_executions': recent_logs,
			'system_status': 'healthy'
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Get Agent Status Error"))
		frappe.throw(str(e))


@frappe.whitelist()
def test_agent(agent_type, task_type='analyze_transactions', task_data=None):
	"""
	Test an agent with a sample task to verify it works.

	API Endpoint: /api/method/mkaguzi.agents.scheduler.test_agent

	Args:
		agent_type: Type of agent to test
		task_type: Type of task to execute
		task_data: Optional task parameters

	Returns:
		dict: Test results
	"""
	try:
		frappe.log(_("Testing {0} agent with {1} task").format(agent_type, task_type), "Agent Scheduler")

		result = run_agent_manually(agent_type, task_type, task_data)

		# Log the test execution
		execution_log = frappe.get_doc({
			'doctype': 'Agent Execution Log',
			'agent_type': agent_type.title(),
			'task_type': task_type,
			'task_name': f"Test: {task_type}",
			'status': 'Completed' if result.get('success') else 'Failed',
			'start_time': frappe.utils.now(),
			'end_time': frappe.utils.now(),
			'duration_seconds': 1,
			'execution_summary': json.dumps(result, default=str),
			'output_data': json.dumps(result.get('result', {}), default=str)
		})
		execution_log.insert()

		return result

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Test Agent Error"))
		return {
			'success': False,
			'error': str(e),
			'agent_type': agent_type,
			'task_type': task_type
		}
