# -*- coding: utf-8 -*-
# Copyright (c) 2024, Coale Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, get_datetime, add_to_date, getdate, time_diff_in_seconds
import json
import uuid
import time
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
import io
import csv


class AdvancedReportingEngine(Document):
	def validate(self):
		"""Validate the advanced reporting engine"""
		self.validate_report_id()
		self.set_default_values()
		self.validate_configurations()

	def validate_report_id(self):
		"""Auto-generate report ID if not provided"""
		if not self.report_id:
			type_short = self.report_type[:3].upper() if self.report_type else "GEN"
			random_suffix = ''.join(str(uuid.uuid4().hex)[:6])
			self.report_id = f"ARE-{type_short}-{random_suffix}"

	def set_default_values(self):
		"""Set default values"""
		if not self.created_by:
			self.created_by = frappe.session.user

		if not self.created_on:
			self.created_on = now()

		self.modified_by = frappe.session.user
		self.modified_on = now()

		if not self.status:
			self.status = "Draft"

		if not self.version:
			self.version = "1.0"

	def validate_configurations(self):
		"""Validate configuration JSON fields"""
		config_fields = ['data_sources', 'query_config', 'filters_config', 'aggregation_config',
						'visualization_config', 'export_config', 'schedule_config',
						'permissions_config', 'alerts_config', 'performance_config',
						'template_config', 'execution_history', 'performance_metrics']

		for field in config_fields:
			value = getattr(self, field, None)
			if value:
				try:
					json.loads(value)
				except json.JSONDecodeError:
					frappe.throw(_(f"{field.replace('_', ' ').title()} must be valid JSON"))

	def on_update(self):
		"""Called when document is updated"""
		if self.is_scheduled and self.status == "Active":
			self.schedule_report()

	def schedule_report(self):
		"""Schedule report execution"""
		try:
			from frappe.utils.background_jobs import enqueue

			schedule_config = json.loads(self.schedule_config or "{}")
			frequency = schedule_config.get('frequency', 'daily')

			if frequency == "hourly":
				enqueue("mkaguzi.reporting.doctype.advanced_reporting_engine.advanced_reporting_engine.execute_scheduled_report",
					   queue="default", report_id=self.name)
			elif frequency == "daily":
				enqueue("mkaguzi.reporting.doctype.advanced_reporting_engine.advanced_reporting_engine.execute_scheduled_report",
					   queue="long", report_id=self.name)
			elif frequency == "weekly":
				enqueue("mkaguzi.reporting.doctype.advanced_reporting_engine.advanced_reporting_engine.execute_scheduled_report",
					   queue="long", report_id=self.name)
			# Add more frequencies as needed

		except Exception as e:
			frappe.logger().error(f"Report scheduling error: {str(e)}")

	def execute_report(self, custom_filters=None, output_format="json"):
		"""Execute the report and return results"""
		try:
			start_time = time.time()

			# Apply filters
			filters = self.build_filters(custom_filters)

			# Execute queries
			raw_data = self.execute_queries(filters)

			# Apply aggregations
			aggregated_data = self.apply_aggregations(raw_data)

			# Format results
			formatted_data = self.format_results(aggregated_data, output_format)

			# Update execution metrics
			execution_time = time.time() - start_time
			self.update_execution_metrics(execution_time)

			# Log execution
			self.log_execution(execution_time, "success")

			return formatted_data

		except Exception as e:
			# Log failed execution
			self.log_execution(0, "failed", str(e))
			frappe.logger().error(f"Report execution error: {str(e)}")
			return {"error": str(e)}

	def build_filters(self, custom_filters=None):
		"""Build complete filter set"""
		try:
			base_filters = json.loads(self.filters_config or "{}")

			if custom_filters:
				if isinstance(custom_filters, str):
					custom_filters = json.loads(custom_filters)
				base_filters.update(custom_filters)

			# Add date range if not specified
			if 'date_range' not in base_filters:
				base_filters['date_range'] = {
					'start': add_to_date(getdate(), days=-30),
					'end': getdate()
				}

			return base_filters

		except Exception as e:
			frappe.logger().error(f"Filter building error: {str(e)}")
			return {}

	def execute_queries(self, filters):
		"""Execute report queries"""
		try:
			data_sources = json.loads(self.data_sources or "{}")
			query_config = json.loads(self.query_config or "{}")

			results = {}

			for source_name, source_config in data_sources.items():
				source_type = source_config.get('type', 'doctype')

				if source_type == 'doctype':
					results[source_name] = self.query_doctype(source_config, filters)
				elif source_type == 'sql':
					results[source_name] = self.execute_sql_query(source_config, filters)
				elif source_type == 'api':
					results[source_name] = self.call_external_api(source_config, filters)
				else:
					results[source_name] = []

			return results

		except Exception as e:
			frappe.logger().error(f"Query execution error: {str(e)}")
			return {}

	def query_doctype(self, source_config, filters):
		"""Query Frappe DocType"""
		try:
			doctype = source_config.get('doctype')
			fields = source_config.get('fields', ['name'])
			conditions = source_config.get('conditions', {})

			# Apply filters
			filter_conditions = self.convert_filters_to_conditions(filters, doctype)

			# Merge with source conditions
			all_conditions = {**conditions, **filter_conditions}

			return frappe.get_all(doctype,
				filters=all_conditions,
				fields=fields,
				order_by='creation desc'
			)

		except Exception as e:
			frappe.logger().error(f"DocType query error: {str(e)}")
			return []

	def execute_sql_query(self, source_config, filters):
		"""Execute SQL query"""
		try:
			query_template = source_config.get('query', '')
			query_params = source_config.get('params', {})

			# Replace filter placeholders
			query = self.substitute_filters(query_template, filters)

			return frappe.db.sql(query, query_params, as_dict=True)

		except Exception as e:
			frappe.logger().error(f"SQL query error: {str(e)}")
			return []

	def call_external_api(self, source_config, filters):
		"""Call external API"""
		try:
			import requests

			url = source_config.get('url', '')
			method = source_config.get('method', 'GET')
			headers = source_config.get('headers', {})
			params = source_config.get('params', {})

			# Add filter params
			params.update(filters)

			response = requests.request(method, url, headers=headers, params=params)
			response.raise_for_status()

			return response.json()

		except Exception as e:
			frappe.logger().error(f"API call error: {str(e)}")
			return []

	def convert_filters_to_conditions(self, filters, doctype):
		"""Convert filters to Frappe conditions"""
		try:
			conditions = {}

			date_range = filters.get('date_range', {})
			if date_range:
				start_date = date_range.get('start')
				end_date = date_range.get('end')
				if start_date and end_date:
					conditions['creation'] = ['between', [start_date, end_date]]

			# Add other filter mappings as needed
			for filter_key, filter_value in filters.items():
				if filter_key not in ['date_range'] and filter_value is not None:
					field_name = self.map_filter_to_field(filter_key, doctype)
					if field_name:
						conditions[field_name] = filter_value

			return conditions

		except Exception as e:
			return {}

	def map_filter_to_field(self, filter_key, doctype):
		"""Map filter key to actual field name"""
		# This could be enhanced with a mapping configuration
		mappings = {
			'status': 'status',
			'priority': 'priority',
			'severity': 'severity',
			'category': 'category'
		}
		return mappings.get(filter_key)

	def substitute_filters(self, query_template, filters):
		"""Substitute filters in SQL query"""
		try:
			query = query_template

			date_range = filters.get('date_range', {})
			if date_range:
				start_date = date_range.get('start')
				end_date = date_range.get('end')
				query = query.replace('{start_date}', str(start_date) if start_date else '2000-01-01')
				query = query.replace('{end_date}', str(end_date) if end_date else str(getdate()))

			return query

		except Exception as e:
			return query_template

	def apply_aggregations(self, raw_data):
		"""Apply aggregations to data"""
		try:
			aggregation_config = json.loads(self.aggregation_config or "{}")

			if not aggregation_config:
				return raw_data

			aggregated_results = {}

			for source_name, data in raw_data.items():
				if source_name in aggregation_config:
					config = aggregation_config[source_name]
					aggregated_results[source_name] = self.aggregate_data(data, config)
				else:
					aggregated_results[source_name] = data

			return aggregated_results

		except Exception as e:
			frappe.logger().error(f"Data aggregation error: {str(e)}")
			return raw_data

	def aggregate_data(self, data, config):
		"""Aggregate data based on configuration"""
		try:
			if not data:
				return []

			df = pd.DataFrame(data)

			group_by = config.get('group_by', [])
			aggregations = config.get('aggregations', {})

			if group_by and aggregations:
				result = df.groupby(group_by).agg(aggregations).reset_index()
				return result.to_dict('records')
			else:
				return data

		except Exception as e:
			frappe.logger().error(f"Data aggregation processing error: {str(e)}")
			return data

	def format_results(self, data, output_format):
		"""Format results for output"""
		try:
			if output_format == "json":
				return json.dumps(data, indent=2, default=str)
			elif output_format == "csv":
				return self.convert_to_csv(data)
			elif output_format == "excel":
				return self.convert_to_excel(data)
			else:
				return data

		except Exception as e:
			return {"error": str(e)}

	def convert_to_csv(self, data):
		"""Convert data to CSV format"""
		try:
			output = io.StringIO()
			writer = csv.writer(output)

			# Handle multiple data sources
			for source_name, source_data in data.items():
				if source_data:
					# Write source header
					writer.writerow([f"Source: {source_name}"])

					# Write column headers
					if isinstance(source_data, list) and source_data:
						headers = source_data[0].keys()
						writer.writerow(headers)

						# Write data rows
						for row in source_data:
							writer.writerow([row.get(header, '') for header in headers])

					writer.writerow([])  # Empty row between sources

			return output.getvalue()

		except Exception as e:
			return ""

	def convert_to_excel(self, data):
		"""Convert data to Excel format"""
		try:
			output = io.BytesIO()

			with pd.ExcelWriter(output, engine='openpyxl') as writer:
				for source_name, source_data in data.items():
					if source_data:
						df = pd.DataFrame(source_data)
						df.to_excel(writer, sheet_name=source_name[:31], index=False)  # Excel sheet name limit

			output.seek(0)
			return output.getvalue()

		except Exception as e:
			return b""

	def update_execution_metrics(self, execution_time):
		"""Update execution performance metrics"""
		try:
			self.execution_count = (self.execution_count or 0) + 1
			self.last_run = now()

			# Calculate average runtime
			if self.average_runtime:
				self.average_runtime = (self.average_runtime + execution_time) / 2
			else:
				self.average_runtime = execution_time

			# Update performance metrics
			metrics = json.loads(self.performance_metrics or "{}")
			metrics.update({
				"last_execution_time": execution_time,
				"average_execution_time": self.average_runtime,
				"total_executions": self.execution_count,
				"last_updated": now()
			})
			self.performance_metrics = json.dumps(metrics)

			self.save()

		except Exception as e:
			frappe.logger().error(f"Execution metrics update error: {str(e)}")

	def log_execution(self, execution_time, status, error_message=None):
		"""Log report execution"""
		try:
			history = json.loads(self.execution_history or "[]")

			log_entry = {
				"timestamp": now(),
				"status": status,
				"execution_time": execution_time,
				"executed_by": frappe.session.user
			}

			if error_message:
				log_entry["error"] = error_message

			history.append(log_entry)

			# Keep only last 100 executions
			if len(history) > 100:
				history = history[-100:]

			self.execution_history = json.dumps(history)

		except Exception as e:
			frappe.logger().error(f"Execution logging error: {str(e)}")

	def deliver_report(self, report_data, delivery_method=None):
		"""Deliver report to recipients"""
		try:
			if not delivery_method:
				delivery_method = self.delivery_method

			if delivery_method == "email":
				self.deliver_via_email(report_data)
			elif delivery_method == "file_system":
				self.deliver_via_file_system(report_data)
			elif delivery_method == "ftp":
				self.deliver_via_ftp(report_data)
			elif delivery_method == "api":
				self.deliver_via_api(report_data)

		except Exception as e:
			frappe.logger().error(f"Report delivery error: {str(e)}")

	def deliver_via_email(self, report_data):
		"""Deliver report via email"""
		try:
			recipients = [r.email for r in (self.recipients or []) if r.email]

			if recipients:
				subject = f"Report: {self.report_name}"
				message = f"Please find the attached report: {self.report_name}"

				# Create attachment
				attachment = self.create_report_attachment(report_data)

				frappe.sendmail(
					recipients=recipients,
					subject=subject,
					message=message,
					attachments=[attachment]
				)

		except Exception as e:
			frappe.logger().error(f"Email delivery error: {str(e)}")

	def create_report_attachment(self, report_data):
		"""Create report attachment"""
		try:
			export_config = json.loads(self.export_config or "{}")
			format_type = export_config.get('format', 'json')

			if format_type == "json":
				content = json.dumps(report_data, indent=2, default=str)
				file_name = f"{self.report_name}.json"
			elif format_type == "csv":
				content = self.convert_to_csv(report_data)
				file_name = f"{self.report_name}.csv"
			else:
				content = str(report_data)
				file_name = f"{self.report_name}.txt"

			return {
				"fname": file_name,
				"fcontent": content
			}

		except Exception as e:
			return {
				"fname": f"{self.report_name}_error.txt",
				"fcontent": f"Error generating report: {str(e)}"
			}

	def deliver_via_file_system(self, report_data):
		"""Deliver report to file system"""
		try:
			import os

			export_config = json.loads(self.export_config or "{}")
			file_path = export_config.get('file_path', f"/tmp/{self.report_name}")

			# Ensure directory exists
			os.makedirs(os.path.dirname(file_path), exist_ok=True)

			# Write file
			with open(file_path, 'w') as f:
				if isinstance(report_data, str):
					f.write(report_data)
				else:
					json.dump(report_data, f, indent=2, default=str)

		except Exception as e:
			frappe.logger().error(f"File system delivery error: {str(e)}")

	def deliver_via_api(self, report_data):
		"""Deliver report via API"""
		try:
			import requests

			export_config = json.loads(self.export_config or "{}")
			api_url = export_config.get('api_url')
			api_key = export_config.get('api_key')

			if api_url:
				headers = {'Content-Type': 'application/json'}
				if api_key:
					headers['Authorization'] = f"Bearer {api_key}"

				response = requests.post(api_url, json=report_data, headers=headers)
				response.raise_for_status()

		except Exception as e:
			frappe.logger().error(f"API delivery error: {str(e)}")

	def deliver_via_ftp(self, report_data):
		"""Deliver report via FTP"""
		try:
			from ftplib import FTP

			export_config = json.loads(self.export_config or "{}")
			ftp_config = export_config.get('ftp_config', {})

			ftp = FTP(ftp_config.get('host'))
			ftp.login(ftp_config.get('user'), ftp_config.get('password'))

			# Create file content
			content = json.dumps(report_data, indent=2, default=str)

			# Upload file
			from io import BytesIO
			bio = BytesIO(content.encode('utf-8'))
			ftp.storbinary(f"STOR {self.report_name}.json", bio)

			ftp.quit()

		except Exception as e:
			frappe.logger().error(f"FTP delivery error: {str(e)}")


@frappe.whitelist()
def execute_scheduled_report(report_id):
	"""Execute a scheduled report"""
	try:
		report = frappe.get_doc("Advanced Reporting Engine", report_id)

		# Execute report
		report_data = report.execute_report()

		# Deliver report
		report.deliver_report(report_data)

		return {"success": True, "message": "Scheduled report executed successfully"}

	except Exception as e:
		frappe.log_error(f"Scheduled report execution error: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def execute_report_on_demand(report_id, filters=None, output_format="json"):
	"""Execute report on demand"""
	try:
		report = frappe.get_doc("Advanced Reporting Engine", report_id)

		report_data = report.execute_report(filters, output_format)

		return report_data

	except Exception as e:
		frappe.log_error(f"On-demand report execution error: {str(e)}")
		return {"error": str(e)}


@frappe.whitelist()
def create_standard_reports():
	"""Create standard reports"""
	try:
		reports_created = []

		# Compliance Overview Report
		compliance_report = create_compliance_overview_report()
		reports_created.append(compliance_report)

		# Risk Assessment Report
		risk_report = create_risk_assessment_report()
		reports_created.append(risk_report)

		# Audit Findings Report
		audit_report = create_audit_findings_report()
		reports_created.append(audit_report)

		return {
			"success": True,
			"reports": reports_created
		}

	except Exception as e:
		frappe.log_error(f"Standard reports creation error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


def create_compliance_overview_report():
	"""Create compliance overview report"""
	report = frappe.get_doc({
		"doctype": "Advanced Reporting Engine",
		"report_name": "Compliance Overview Report",
		"report_type": "Compliance Report",
		"description": "Comprehensive compliance status overview",
		"status": "Active",
		"data_sources": json.dumps({
			"compliance_assessments": {
				"type": "doctype",
				"doctype": "Compliance Assessment",
				"fields": ["name", "compliance_framework", "compliance_score", "status", "creation"]
			},
			"regulatory_requirements": {
				"type": "doctype",
				"doctype": "Regulatory Requirement",
				"fields": ["name", "regulatory_framework", "compliance_status", "priority"]
			}
		}),
		"filters_config": json.dumps({
			"date_range": {"start": add_to_date(getdate(), days=-90), "end": getdate()},
			"status": ["Active", "Under Review"]
		}),
		"aggregation_config": json.dumps({
			"compliance_assessments": {
				"group_by": ["compliance_framework"],
				"aggregations": {"compliance_score": "mean", "name": "count"}
			}
		})
	})

	report.insert()
	return report.name


def create_risk_assessment_report():
	"""Create risk assessment report"""
	report = frappe.get_doc({
		"doctype": "Advanced Reporting Engine",
		"report_name": "Risk Assessment Report",
		"report_type": "Risk Report",
		"description": "Risk assessment summary and trends",
		"status": "Active",
		"data_sources": json.dumps({
			"risk_assessments": {
				"type": "doctype",
				"doctype": "Risk Assessment",
				"fields": ["name", "risk_category", "risk_severity", "risk_score", "status", "creation"]
			}
		}),
		"aggregation_config": json.dumps({
			"risk_assessments": {
				"group_by": ["risk_category", "risk_severity"],
				"aggregations": {"risk_score": "mean", "name": "count"}
			}
		})
	})

	report.insert()
	return report.name


def create_audit_findings_report():
	"""Create audit findings report"""
	report = frappe.get_doc({
		"doctype": "Advanced Reporting Engine",
		"report_name": "Audit Findings Report",
		"report_type": "Audit Report",
		"description": "Audit findings summary and resolution status",
		"status": "Active",
		"data_sources": json.dumps({
			"audit_findings": {
				"type": "doctype",
				"doctype": "Audit Finding",
				"fields": ["name", "severity", "status", "finding_category", "days_to_resolve", "creation"]
			}
		}),
		"aggregation_config": json.dumps({
			"audit_findings": {
				"group_by": ["severity", "status"],
				"aggregations": {"days_to_resolve": "mean", "name": "count"}
			}
		})
	})

	report.insert()
	return report.name