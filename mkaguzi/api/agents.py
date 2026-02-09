# -*- coding: utf-8 -*-
# Copyright (c) 2025, mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import json
from frappe.utils import now


@frappe.whitelist()
def get_available_agents():
	"""
	Get list of available agent types that can be executed.

	API Endpoint: /api/method/mkaguzi.agents.get_available_agents

	Returns:
		list: Available agent types with descriptions
	"""
	try:
		from mkaguzi.agents.agent_registry import AgentRegistry

		agents = AgentRegistry.get_registered_agents()

		return [
			{
				'agent_type': agent.get('agent_type'),
				'category': agent.get('category'),
				'description': agent.get('description'),
				'class_path': agent.get('class_path'),
				'has_active_config': frappe.db.exists('Agent Configuration') and
					frappe.db.count('Agent Configuration', {'agent_type': agent.get('agent_type'), 'is_active': 1}) > 0
			}
			for agent in agents
		]

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Get Available Agents Error"))
		frappe.throw(str(e))


@frappe.whitelist()
def get_agent_tasks(agent_type):
	"""
	Get available task types for a specific agent.

	API Endpoint: /api/method/mkaguzi.agents.get_agent_tasks

	Args:
		agent_type: Type of agent (financial, risk, compliance, discovery, notification)

	Returns:
		dict: Available tasks with descriptions
	"""
	try:
		tasks = {
			'financial': [
				{'task_type': 'analyze_transactions', 'description': 'Analyze financial transactions for anomalies and risk patterns', 'parameters': ['limit', 'start_date', 'end_date']},
				{'task_type': 'detect_fraud', 'description': 'Detect fraudulent transaction patterns', 'parameters': ['limit', 'threshold']},
				{'task_type': 'reconcile_gl', 'description': 'Perform intelligent GL reconciliation', 'parameters': ['accounts', 'period']},
				{'task_type': 'analyze_journal_entries', 'description': 'Scrutinize journal entries for issues', 'parameters': ['limit', 'posting_date']},
				{'task_type': 'duplicate_payment_check', 'description': 'Check for duplicate payments', 'parameters': ['limit']},
				{'task_type': 'benford_analysis', 'description': 'Apply Benford\'s Law test for digit analysis', 'parameters': ['account', 'period']}
			],
			'risk': [
				{'task_type': 'predict_risks', 'description': 'Predict future risks based on historical data', 'parameters': ['days_ahead', 'min_data_points']},
				{'task_type': 'assess_financial_risk', 'description': 'Assess financial risk levels', 'parameters': ['limit', 'module']},
				{'task_type': 'assess_hr_risk', 'description': 'Assess HR-related risks', 'parameters': ['limit']},
				{'task_type': 'assess_inventory_risk', 'description': 'Assess inventory management risks', 'parameters': ['limit']}
			],
			'compliance': [
				{'task_type': 'verify_compliance', 'description': 'Verify regulatory compliance requirements', 'parameters': ['requirement_type', 'severity_filter']},
				{'task_type': 'identify_gaps', 'description': 'Identify compliance gaps', 'parameters': ['compliance_framework']},
				{'task_type': 'run_compliance_check', 'description': 'Run specific compliance check', 'parameters': ['check_name']},
				{'task_type': 'get_compliance_status', 'description': 'Get current compliance status', 'parameters': []}
			],
			'discovery': [
				{'task_type': 'discover_doctypes', 'description': 'Discover and catalog new doctypes', 'parameters': ['include_custom']},
				{'task_type': 'detect_schema_changes', 'description': 'Detect schema changes in existing doctypes', 'parameters': ['doctype_name']},
				{'task_type': 'update_catalog', 'description': 'Update audit doctype catalog', 'parameters': []}
			],
			'notification': [
				{'task_type': 'send_notification', 'description': 'Send a notification', 'parameters': ['recipients', 'message', 'priority']},
				{'task_type': 'aggregate_alerts', 'description': 'Aggregate similar alerts to reduce noise', 'parameters': ['window_minutes']},
				{'task_type': 'escalate', 'description': 'Escalate alerts based on severity and age', 'parameters': ['alert_name']},
				{'task_type': 'send_digest', 'description': 'Send digest of notifications', 'parameters': ['digest_type', 'period']},
				{'task_type': 'process_pending', 'description': 'Process pending notification queue', 'parameters': []}
			]
		}

		agent_tasks = tasks.get(agent_type.lower())
		if agent_tasks:
			return agent_tasks

		# Return empty if agent type not found
		return []

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Get Agent Tasks Error"))
		frappe.throw(str(e))


@frappe.whitelist()
def execute_agent(agent_type, task_type, task_data=None):
	"""
	Execute an agent with a specific task.

	API Endpoint: /api/method/mkaguzi.agents.execute_agent

	Args:
		agent_type: Type of agent (financial, risk, compliance, discovery, notification)
		task_type: Type of task to execute
		task_data: Additional task parameters (dict)

	Returns:
		dict: Execution result with status and data
	"""
	try:
		from mkaguzi.agents.scheduler import run_agent_manually

		# Validate agent type
		available_agents = get_available_agents()
		agent_types = [a['agent_type'] for a in available_agents]

		if agent_type.title() not in agent_types:
			frappe.throw(_("Unknown agent type: {0}. Available: {1}").format(
				agent_type, ', '.join(agent_types)))

		# Execute the agent
		result = run_agent_manually(agent_type, task_type, task_data)

		# Log the execution
		log_entry = frappe.get_doc({
			'doctype': 'Agent Execution Log',
			'agent_type': agent_type.title(),
			'task_type': task_type,
			'task_name': task_type,
			'status': 'Completed' if result.get('success') else 'Failed',
			'start_time': now(),
			'end_time': now(),
			'duration_seconds': 1,
			'input_data': json.dumps(task_data or {}, default=str),
			'output_data': json.dumps(result.get('result', {}), default=str),
			'execution_summary': json.dumps({
				'agent_type': agent_type,
				'task_type': task_type,
				'success': result.get('success', False),
				'has_findings': len(result.get('result', {}).get('findings', [])) > 0
			}, default=str)
		})

		if result.get('result') and result['result'].get('findings'):
			log_entry.findings_generated = 1
			log_entry.finding_ids = ','.join([
				f['name'] for f in result['result']['findings']
			])

		log_entry.save()

		return result

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Execute Agent Error"))
		frappe.throw(str(e))


@frappe.whitelist()
def run_all_agents_background(task_data=None):
	"""
	Run all active agents in the background with their default tasks.

	API Endpoint: /api/method/mkaguzi.agents.run_all_agents_background

	Args:
		task_data: Optional override data for tasks

	Returns:
		dict: Job ID for background execution
	"""
	try:
		from frappe.utils.background_jobs import enqueue

		# Enqueue background job
		job_id = enqueue(
			"mkaguzi.agents.scheduler.run_sunday_midnight_agents",
			queue="long",
			kwargs={},
			timeout=3600
		)

		return {
			'success': True,
			'job_id': job_id,
			'message': 'All agents execution started in background'
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Run All Agents Background Error"))
		frappe.throw(str(e))


@frappe.whitelist()
def get_agent_executions(limit=20, agent_type=None, status=None):
	"""
	Get recent agent execution logs.

	API Endpoint: /api/method/mkaguzi.agents.get_agent_executions

	Args:
		limit: Maximum number of executions to return
		agent_type: Filter by agent type
		status: Filter by status

	Returns:
		list: Recent agent execution records
	"""
	try:
		filters = {}

		if agent_type:
			filters['agent_type'] = agent_type.title()

		if status:
			filters['status'] = status

		executions = frappe.get_all('Agent Execution Log',
			filters=filters,
			fields=['name', 'agent_type', 'task_type', 'task_name', 'status',
			       'duration_seconds', 'findings_generated', 'creation'],
			order_by='creation desc',
			limit=limit
		)

		return executions

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Get Agent Executions Error"))
		frappe.throw(str(e))


@frappe.whitelist()
def get_agent_execution_details(execution_id):
	"""
	Get detailed information about an agent execution.

	API Endpoint: /api/method/mkaguzi.agents.get_agent_execution_details

	Args:
		execution_id: Name of the Agent Execution Log record

	Returns:
		dict: Complete execution details with input/output data
	"""
	try:
		log_entry = frappe.get_doc('Agent Execution Log', execution_id)

		return {
		'name': log_entry.name,
		'agent_type': log_entry.agent_type,
		'task_type': log_entry.task_type,
		'task_name': log_entry.task_name,
		'status': log_entry.status,
		'start_time': log_entry.start_time,
		'end_time': log_entry.end_time,
		'duration_seconds': log_entry.duration_seconds,
		'input_data': json.loads(log_entry.input_data) if log_entry.input_data else {},
		'output_data': json.loads(log_entry.output_data) if log_entry.output_data else {},
		'execution_summary': json.loads(log_entry.execution_summary) if log_entry.execution_summary else {},
		'findings_generated': log_entry.findings_generated,
		'finding_ids': log_entry.finding_ids.split(',') if log_entry.finding_ids else [],
		'created': log_entry.creation,
		'modified': log_entry.modified
	}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Get Agent Execution Details Error"))
		frappe.throw(str(e))


@frappe.whitelist()
def cancel_agent_execution(execution_id):
	"""
	Cancel a running or pending agent execution.

	API Endpoint: /api/method/mkaguzi.agents.cancel_agent_execution

	Args:
		execution_id: Name of the Agent Execution Log record to cancel

	Returns:
		dict: Cancellation result
	"""
	try:
		log_entry = frappe.get_doc('Agent Execution Log', execution_id)

		if log_entry.status not in ['Pending', 'Running']:
			frappe.throw(_("Can only cancel Pending or Running executions"))

		# Update the execution log
		log_entry.status = 'Cancelled'
		log_entry.end_time = now()
		log_entry.execution_summary = json.dumps({
			'cancelled_by': frappe.session.user,
			'cancelled_at': now()
		})
		log_entry.save()

		# TODO: Stop the actual agent if it's still running

		return {
			'success': True,
			'message': 'Agent execution cancelled'
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Cancel Agent Execution Error"))
		frappe.throw(str(e))
