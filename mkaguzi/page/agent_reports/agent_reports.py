# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import json

def get_context(context):
	"""Get context for agent reports page"""
	context.agent_types = [
		{'value': 'Financial', 'label': _('Financial Agent'), 'icon': 'fa-money'},
		{'value': 'Risk', 'label': _('Risk Agent'), 'icon': 'fa-exclamation-triangle'},
		{'value': 'Compliance', 'label': _('Compliance Agent'), 'icon': 'fa-shield'},
		{'value': 'Discovery', 'label': _('Discovery Agent'), 'icon': 'fa-search'},
		{'value': 'Notification', 'label': _('Notification Agent'), 'icon': 'fa-bell'}
	]

	# Get recent executions
	recent_executions = frappe.get_all('Agent Execution Log',
		fields=['name', 'agent_type', 'task_name', 'status', 'creation', 'execution_summary'],
		order_by='creation desc',
		limit=10
	)
	context.recent_executions = recent_executions

	return context


@frappe.whitelist()
def get_execution_report(execution_id):
	"""Get formatted execution report for display"""
	try:
		log = frappe.get_doc('Agent Execution Log', execution_id)

		report_data = {
			'name': log.name,
			'agent_type': log.agent_type,
			'task_name': log.task_name,
			'task_type': log.task_type,
			'status': log.status,
			'start_time': str(log.start_time) if log.start_time else None,
			'end_time': str(log.end_time) if log.end_time else None,
			'duration_seconds': log.duration_seconds,
			'findings_generated': log.findings_generated
		}

		# Parse execution summary
		if log.execution_summary:
			try:
				report_data['execution_summary'] = json.loads(log.execution_summary)
			except:
				report_data['execution_summary'] = {'raw': log.execution_summary}

		# Parse output data
		if log.output_data:
			try:
				report_data['output_data'] = json.loads(log.output_data)
			except:
				report_data['output_data'] = {'raw': log.output_data}

		# Parse input data
		if log.input_data:
			try:
				report_data['input_data'] = json.loads(log.input_data)
			except:
				report_data['input_data'] = {'raw': log.input_data}

		return report_data

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _('Get Execution Report Error'))
		frappe.throw(str(e))
