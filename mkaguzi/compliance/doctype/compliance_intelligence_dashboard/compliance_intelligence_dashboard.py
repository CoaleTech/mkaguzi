# -*- coding: utf-8 -*-
# Copyright (c) 2024, Coale Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, get_datetime, add_to_date, getdate, date_diff, formatdate
import json
import uuid
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import calendar


class ComplianceIntelligenceDashboard(Document):
	def validate(self):
		"""Validate the compliance intelligence dashboard"""
		self.validate_dashboard_id()
		self.set_default_values()
		self.validate_configurations()

	def validate_dashboard_id(self):
		"""Auto-generate dashboard ID if not provided"""
		if not self.dashboard_id:
			type_short = self.dashboard_type[:3].upper() if self.dashboard_type else "GEN"
			random_suffix = ''.join(str(uuid.uuid4().hex)[:6])
			self.dashboard_id = f"CID-{type_short}-{random_suffix}"

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

	def validate_configurations(self):
		"""Validate configuration JSON fields"""
		config_fields = ['widgets_config', 'filters_config', 'alerts_config',
						'permissions_config', 'export_config']

		for field in config_fields:
			value = getattr(self, field, None)
			if value:
				try:
					json.loads(value)
				except json.JSONDecodeError:
					frappe.throw(_(f"{field.replace('_', ' ').title()} must be valid JSON"))

	def on_update(self):
		"""Called when document is updated"""
		if self.status == "Active" and self.auto_refresh:
			self.schedule_refresh()

	def schedule_refresh(self):
		"""Schedule dashboard refresh"""
		try:
			from frappe.utils.background_jobs import enqueue

			# Schedule refresh based on interval
			if self.refresh_interval == "5 Minutes":
				enqueue("mkaguzi.compliance.doctype.compliance_intelligence_dashboard.compliance_intelligence_dashboard.refresh_dashboard",
					   queue="short", dashboard_id=self.name)
			elif self.refresh_interval == "15 Minutes":
				enqueue("mkaguzi.compliance.doctype.compliance_intelligence_dashboard.compliance_intelligence_dashboard.refresh_dashboard",
					   queue="short", dashboard_id=self.name)
			elif self.refresh_interval == "30 Minutes":
				enqueue("mkaguzi.compliance.doctype.compliance_intelligence_dashboard.compliance_intelligence_dashboard.refresh_dashboard",
					   queue="default", dashboard_id=self.name)
			# Add more intervals as needed

		except Exception as e:
			frappe.logger().error(f"Dashboard refresh scheduling error: {str(e)}")

	def get_dashboard_data(self, filters=None):
		"""Get comprehensive dashboard data"""
		try:
			# Apply filters
			applied_filters = self.apply_filters(filters)

			# Get widgets configuration
			widgets_config = json.loads(self.widgets_config or "{}")

			dashboard_data = {
				"dashboard_id": self.dashboard_id,
				"dashboard_name": self.dashboard_name,
				"dashboard_type": self.dashboard_type,
				"last_refreshed": now(),
				"time_range": applied_filters.get('time_range'),
				"widgets": []
			}

			# Generate data for each widget
			for widget in widgets_config.get('widgets', []):
				widget_data = self.get_widget_data(widget, applied_filters)
				if widget_data:
					dashboard_data["widgets"].append(widget_data)

			# Update last refreshed timestamp
			self.last_refreshed = now()
			self.save()

			return dashboard_data

		except Exception as e:
			frappe.logger().error(f"Dashboard data retrieval error: {str(e)}")
			return {"error": str(e)}

	def apply_filters(self, custom_filters=None):
		"""Apply and merge filters"""
		try:
			base_filters = {
				"time_range": self.time_range,
				"compliance_frameworks": json.loads(self.compliance_frameworks or "[]"),
				"risk_categories": json.loads(self.risk_categories or "[]"),
				"audit_types": json.loads(self.audit_types or "[]")
			}

			# Merge with custom filters
			if custom_filters:
				base_filters.update(custom_filters)

			# Convert time range to date range
			base_filters["date_range"] = self.get_date_range(base_filters["time_range"])

			return base_filters

		except Exception as e:
			frappe.logger().error(f"Filter application error: {str(e)}")
			return {}

	def get_date_range(self, time_range):
		"""Convert time range to actual date range"""
		try:
			today = getdate()

			if time_range == "Last 7 Days":
				return [add_to_date(today, days=-7), today]
			elif time_range == "Last 30 Days":
				return [add_to_date(today, days=-30), today]
			elif time_range == "Last 90 Days":
				return [add_to_date(today, days=-90), today]
			elif time_range == "Last 6 Months":
				return [add_to_date(today, months=-6), today]
			elif time_range == "Last Year":
				return [add_to_date(today, years=-1), today]
			elif time_range == "All Time":
				return [getdate("2000-01-01"), today]
			else:  # Custom Range or default
				return [add_to_date(today, days=-30), today]

		except Exception as e:
			return [add_to_date(getdate(), days=-30), getdate()]

	def get_widget_data(self, widget_config, filters):
		"""Get data for a specific widget"""
		try:
			widget_type = widget_config.get('type')
			widget_id = widget_config.get('id')

			if widget_type == "compliance_overview":
				return self.get_compliance_overview_data(filters)
			elif widget_type == "risk_heatmap":
				return self.get_risk_heatmap_data(filters)
			elif widget_type == "audit_trends":
				return self.get_audit_trends_data(filters)
			elif widget_type == "findings_summary":
				return self.get_findings_summary_data(filters)
			elif widget_type == "regulatory_compliance":
				return self.get_regulatory_compliance_data(filters)
			elif widget_type == "performance_metrics":
				return self.get_performance_metrics_data(filters)
			else:
				return None

		except Exception as e:
			frappe.logger().error(f"Widget data retrieval error for {widget_config.get('type')}: {str(e)}")
			return None

	def get_compliance_overview_data(self, filters):
		"""Get compliance overview data"""
		try:
			date_range = filters.get('date_range', [])

			# Compliance status summary
			compliance_data = frappe.db.sql("""
				SELECT
					status,
					COUNT(*) as count
				FROM `tabCompliance Assessment`
				WHERE creation BETWEEN %s AND %s
				GROUP BY status
			""", (date_range[0], date_range[1]), as_dict=True)

			# Framework compliance scores
			framework_scores = frappe.db.sql("""
				SELECT
					compliance_framework,
					AVG(compliance_score) as avg_score,
					COUNT(*) as assessment_count
				FROM `tabCompliance Assessment`
				WHERE creation BETWEEN %s AND %s
				GROUP BY compliance_framework
			""", (date_range[0], date_range[1]), as_dict=True)

			return {
				"widget_id": "compliance_overview",
				"title": "Compliance Overview",
				"type": "summary_cards",
				"data": {
					"status_summary": compliance_data,
					"framework_scores": framework_scores,
					"overall_score": self.calculate_overall_compliance_score(framework_scores)
				}
			}

		except Exception as e:
			return {"error": str(e)}

	def get_risk_heatmap_data(self, filters):
		"""Get risk heatmap data"""
		try:
			date_range = filters.get('date_range', [])

			# Risk by category and severity
			risk_data = frappe.db.sql("""
				SELECT
					risk_category,
					risk_severity,
					COUNT(*) as count,
					AVG(risk_score) as avg_score
				FROM `tabRisk Assessment`
				WHERE creation BETWEEN %s AND %s
				GROUP BY risk_category, risk_severity
				ORDER BY risk_category, risk_severity
			""", (date_range[0], date_range[1]), as_dict=True)

			# Create heatmap matrix
			heatmap = defaultdict(lambda: defaultdict(int))
			for row in risk_data:
				heatmap[row.risk_category][row.risk_severity] = {
					"count": row.count,
					"avg_score": row.avg_score
				}

			return {
				"widget_id": "risk_heatmap",
				"title": "Risk Heatmap",
				"type": "heatmap",
				"data": dict(heatmap)
			}

		except Exception as e:
			return {"error": str(e)}

	def get_audit_trends_data(self, filters):
		"""Get audit trends data"""
		try:
			date_range = filters.get('date_range', [])

			# Monthly audit trends
			trends_data = frappe.db.sql("""
				SELECT
					DATE_FORMAT(creation, '%Y-%m') as month,
					audit_type,
					status,
					COUNT(*) as count
				FROM `tabAudit Plan`
				WHERE creation BETWEEN %s AND %s
				GROUP BY DATE_FORMAT(creation, '%Y-%m'), audit_type, status
				ORDER BY month
			""", (date_range[0], date_range[1]), as_dict=True)

			# Process into time series
			time_series = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
			for row in trends_data:
				time_series[row.month][row.audit_type][row.status] = row.count

			return {
				"widget_id": "audit_trends",
				"title": "Audit Trends",
				"type": "line_chart",
				"data": {
					"time_series": dict(time_series),
					"periods": sorted(time_series.keys())
				}
			}

		except Exception as e:
			return {"error": str(e)}

	def get_findings_summary_data(self, filters):
		"""Get findings summary data"""
		try:
			date_range = filters.get('date_range', [])

			# Findings by severity and status
			findings_data = frappe.db.sql("""
				SELECT
					severity,
					status,
					COUNT(*) as count,
					AVG(days_to_resolve) as avg_resolution_time
				FROM `tabAudit Finding`
				WHERE creation BETWEEN %s AND %s
				GROUP BY severity, status
			""", (date_range[0], date_range[1]), as_dict=True)

			# Top finding categories
			category_data = frappe.db.sql("""
				SELECT
					finding_category,
					COUNT(*) as count
				FROM `tabAudit Finding`
				WHERE creation BETWEEN %s AND %s
				GROUP BY finding_category
				ORDER BY count DESC
				LIMIT 10
			""", (date_range[0], date_range[1]), as_dict=True)

			return {
				"widget_id": "findings_summary",
				"title": "Findings Summary",
				"type": "bar_chart",
				"data": {
					"severity_status": findings_data,
					"top_categories": category_data
				}
			}

		except Exception as e:
			return {"error": str(e)}

	def get_regulatory_compliance_data(self, filters):
		"""Get regulatory compliance data"""
		try:
			date_range = filters.get('date_range', [])

			# Regulatory requirement compliance
			regulatory_data = frappe.db.sql("""
				SELECT
					regulatory_framework,
					requirement_type,
					compliance_status,
					COUNT(*) as count
				FROM `tabRegulatory Requirement`
				WHERE creation BETWEEN %s AND %s
				GROUP BY regulatory_framework, requirement_type, compliance_status
			""", (date_range[0], date_range[1]), as_dict=True)

			# Compliance gaps
			gaps_data = frappe.db.sql("""
				SELECT
					regulatory_framework,
					COUNT(*) as total_requirements,
					SUM(CASE WHEN compliance_status = 'Non-Compliant' THEN 1 ELSE 0 END) as non_compliant
				FROM `tabRegulatory Requirement`
				WHERE creation BETWEEN %s AND %s
				GROUP BY regulatory_framework
			""", (date_range[0], date_range[1]), as_dict=True)

			return {
				"widget_id": "regulatory_compliance",
				"title": "Regulatory Compliance",
				"type": "compliance_gauge",
				"data": {
					"requirements": regulatory_data,
					"compliance_gaps": gaps_data
				}
			}

		except Exception as e:
			return {"error": str(e)}

	def get_performance_metrics_data(self, filters):
		"""Get performance metrics data"""
		try:
			date_range = filters.get('date_range', [])

			# Audit completion rates
			completion_data = frappe.db.sql("""
				SELECT
					audit_type,
					AVG(completion_percentage) as avg_completion,
					COUNT(*) as total_audits,
					SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_audits
				FROM `tabAudit Plan`
				WHERE creation BETWEEN %s AND %s
				GROUP BY audit_type
			""", (date_range[0], date_range[1]), as_dict=True)

			# Finding resolution times
			resolution_data = frappe.db.sql("""
				SELECT
					severity,
					AVG(days_to_resolve) as avg_resolution_days,
					MIN(days_to_resolve) as min_resolution_days,
					MAX(days_to_resolve) as max_resolution_days
				FROM `tabAudit Finding`
				WHERE creation BETWEEN %s AND %s AND status = 'Resolved'
				GROUP BY severity
			""", (date_range[0], date_range[1]), as_dict=True)

			return {
				"widget_id": "performance_metrics",
				"title": "Performance Metrics",
				"type": "metrics_cards",
				"data": {
					"completion_rates": completion_data,
					"resolution_times": resolution_data
				}
			}

		except Exception as e:
			return {"error": str(e)}

	def calculate_overall_compliance_score(self, framework_scores):
		"""Calculate overall compliance score"""
		try:
			if not framework_scores:
				return 0

			total_weighted_score = 0
			total_weight = 0

			for score in framework_scores:
				weight = score.get('assessment_count', 1)
				total_weighted_score += score.get('avg_score', 0) * weight
				total_weight += weight

			return total_weighted_score / total_weight if total_weight > 0 else 0

		except Exception as e:
			return 0

	def check_alerts(self):
		"""Check and trigger dashboard alerts"""
		try:
			alerts_config = json.loads(self.alerts_config or "{}")
			alerts = alerts_config.get('alerts', [])

			for alert in alerts:
				if self.evaluate_alert_condition(alert):
					self.trigger_alert(alert)

		except Exception as e:
			frappe.logger().error(f"Alert check error: {str(e)}")

	def evaluate_alert_condition(self, alert):
		"""Evaluate alert condition"""
		try:
			condition = alert.get('condition', {})
			metric = condition.get('metric')
			operator = condition.get('operator', '>')
			threshold = condition.get('value', 0)

			# Get current metric value
			current_value = self.get_metric_value(metric)

			if operator == '>':
				return current_value > threshold
			elif operator == '<':
				return current_value < threshold
			elif operator == '>=':
				return current_value >= threshold
			elif operator == '<=':
				return current_value <= threshold

			return False

		except Exception as e:
			return False

	def get_metric_value(self, metric):
		"""Get current metric value"""
		try:
			if metric == "overall_compliance_score":
				framework_scores = frappe.db.sql("""
					SELECT AVG(compliance_score) as score FROM `tabCompliance Assessment`
					WHERE status = 'Active'
				""", as_dict=True)
				return framework_scores[0].score if framework_scores else 0

			elif metric == "open_findings_count":
				return frappe.db.count("Audit Finding", {"status": "Open"})

			elif metric == "overdue_audits":
				return frappe.db.sql("""
					SELECT COUNT(*) as count FROM `tabAudit Plan`
					WHERE due_date < CURDATE() AND status != 'Completed'
				""")[0][0]

			return 0

		except Exception as e:
			return 0

	def trigger_alert(self, alert):
		"""Trigger dashboard alert"""
		try:
			alert_type = alert.get('type', 'notification')
			message = alert.get('message', 'Alert triggered')
			recipients = alert.get('recipients', [])

			if alert_type == 'email':
				frappe.sendmail(
					recipients=recipients,
					subject=f"Compliance Dashboard Alert: {self.dashboard_name}",
					message=message
				)
			elif alert_type == 'notification':
				# Create in-app notification
				for recipient in recipients:
					frappe.get_doc({
						"doctype": "Notification Log",
						"subject": f"Compliance Alert: {self.dashboard_name}",
						"email_content": message,
						"document_type": "Compliance Intelligence Dashboard",
						"document_name": self.name,
						"for_user": recipient
					}).insert()

		except Exception as e:
			frappe.logger().error(f"Alert trigger error: {str(e)}")

	def export_dashboard_data(self, export_format="json"):
		"""Export dashboard data"""
		try:
			dashboard_data = self.get_dashboard_data()

			if export_format == "json":
				return json.dumps(dashboard_data, indent=2, default=str)
			elif export_format == "csv":
				# Convert to CSV format
				return self.convert_to_csv(dashboard_data)
			else:
				return dashboard_data

		except Exception as e:
			return {"error": str(e)}

	def convert_to_csv(self, data):
		"""Convert dashboard data to CSV format"""
		try:
			import csv
			from io import StringIO

			output = StringIO()
			writer = csv.writer(output)

			# Write header
			writer.writerow(["Widget", "Metric", "Value"])

			# Write data
			for widget in data.get('widgets', []):
				widget_title = widget.get('title', '')
				widget_data = widget.get('data', {})

				if isinstance(widget_data, dict):
					for key, value in widget_data.items():
						if isinstance(value, list):
							for item in value:
								if isinstance(item, dict):
									writer.writerow([widget_title, key, str(item)])
								else:
									writer.writerow([widget_title, key, str(value)])
						else:
							writer.writerow([widget_title, key, str(value)])

			return output.getvalue()

		except Exception as e:
			return ""


@frappe.whitelist()
def refresh_dashboard(dashboard_id):
	"""Refresh dashboard data"""
	try:
		dashboard = frappe.get_doc("Compliance Intelligence Dashboard", dashboard_id)

		# Update last refreshed timestamp
		dashboard.last_refreshed = now()
		dashboard.view_count = (dashboard.view_count or 0) + 1
		dashboard.save()

		# Check alerts
		dashboard.check_alerts()

		return {"success": True, "message": "Dashboard refreshed successfully"}

	except Exception as e:
		frappe.log_error(f"Dashboard refresh error: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_dashboard_data(dashboard_id, filters=None):
	"""Get dashboard data via API"""
	try:
		dashboard = frappe.get_doc("Compliance Intelligence Dashboard", dashboard_id)

		if filters:
			filters = json.loads(filters)

		return dashboard.get_dashboard_data(filters)

	except Exception as e:
		frappe.log_error(f"Dashboard data retrieval error: {str(e)}")
		return {"error": str(e)}


@frappe.whitelist()
def create_default_dashboards():
	"""Create default compliance intelligence dashboards"""
	try:
		dashboards_created = []

		# Executive Dashboard
		exec_dashboard = create_executive_dashboard()
		dashboards_created.append(exec_dashboard)

		# Compliance Officer Dashboard
		compliance_dashboard = create_compliance_officer_dashboard()
		dashboards_created.append(compliance_dashboard)

		# Auditor Dashboard
		auditor_dashboard = create_auditor_dashboard()
		dashboards_created.append(auditor_dashboard)

		return {
			"success": True,
			"dashboards": dashboards_created
		}

	except Exception as e:
		frappe.log_error(f"Default dashboards creation error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


def create_executive_dashboard():
	"""Create executive dashboard"""
	dashboard = frappe.get_doc({
		"doctype": "Compliance Intelligence Dashboard",
		"dashboard_name": "Executive Compliance Overview",
		"dashboard_type": "Executive",
		"description": "High-level compliance and risk overview for executives",
		"status": "Active",
		"is_default": True,
		"time_range": "Last 30 Days",
		"refresh_interval": "1 Hour",
		"auto_refresh": True,
		"widgets_config": json.dumps({
			"widgets": [
				{"id": "compliance_overview", "type": "compliance_overview"},
				{"id": "risk_heatmap", "type": "risk_heatmap"},
				{"id": "performance_metrics", "type": "performance_metrics"}
			]
		}),
		"alerts_config": json.dumps({
			"alerts": [
				{
					"condition": {"metric": "overall_compliance_score", "operator": "<", "value": 80},
					"type": "email",
					"message": "Overall compliance score has dropped below 80%",
					"recipients": ["ceo@company.com", "cfo@company.com"]
				}
			]
		})
	})

	dashboard.insert()
	return dashboard.name


def create_compliance_officer_dashboard():
	"""Create compliance officer dashboard"""
	dashboard = frappe.get_doc({
		"doctype": "Compliance Intelligence Dashboard",
		"dashboard_name": "Compliance Officer Dashboard",
		"dashboard_type": "Compliance Officer",
		"description": "Detailed compliance monitoring and management dashboard",
		"status": "Active",
		"time_range": "Last 90 Days",
		"refresh_interval": "30 Minutes",
		"auto_refresh": True,
		"widgets_config": json.dumps({
			"widgets": [
				{"id": "compliance_overview", "type": "compliance_overview"},
				{"id": "regulatory_compliance", "type": "regulatory_compliance"},
				{"id": "findings_summary", "type": "findings_summary"},
				{"id": "audit_trends", "type": "audit_trends"}
			]
		})
	})

	dashboard.insert()
	return dashboard.name


def create_auditor_dashboard():
	"""Create auditor dashboard"""
	dashboard = frappe.get_doc({
		"doctype": "Compliance Intelligence Dashboard",
		"dashboard_name": "Audit Intelligence Dashboard",
		"dashboard_type": "Auditor",
		"description": "Comprehensive audit findings and trends analysis",
		"status": "Active",
		"time_range": "Last 6 Months",
		"refresh_interval": "15 Minutes",
		"auto_refresh": True,
		"widgets_config": json.dumps({
			"widgets": [
				{"id": "findings_summary", "type": "findings_summary"},
				{"id": "audit_trends", "type": "audit_trends"},
				{"id": "risk_heatmap", "type": "risk_heatmap"},
				{"id": "performance_metrics", "type": "performance_metrics"}
			]
		})
	})

	dashboard.insert()
	return dashboard.name