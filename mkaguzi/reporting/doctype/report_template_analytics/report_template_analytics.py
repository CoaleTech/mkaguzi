# -*- coding: utf-8 -*-
# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, get_datetime, time_diff_in_seconds, cstr
import json
import time
from datetime import datetime, timedelta


class ReportTemplateAnalytics(Document):
	def autoname(self):
		"""Generate name based on template name"""
		if self.template_name:
			self.name = f"analytics_{self.template_name.lower().replace(' ', '_')}_{self.template_id}"

	def validate(self):
		"""Validate analytics data"""
		self.validate_metrics()
		self.update_calculated_fields()

	def validate_metrics(self):
		"""Validate performance and usage metrics"""
		if self.average_render_time and self.average_render_time < 0:
			frappe.throw(_("Average render time cannot be negative"))

		if self.success_rate and (self.success_rate < 0 or self.success_rate > 100):
			frappe.throw(_("Success rate must be between 0 and 100"))

		if self.cache_hit_rate and (self.cache_hit_rate < 0 or self.cache_hit_rate > 100):
			frappe.throw(_("Cache hit rate must be between 0 and 100"))

	def update_calculated_fields(self):
		"""Update calculated fields based on raw data"""
		# Calculate success rate based on current data
		if self.total_renders and self.total_renders > 0:
			if self.total_render_errors is None:
				self.total_render_errors = 0
			successful_renders = self.total_renders - self.total_render_errors
			self.success_rate = (successful_renders / self.total_renders) * 100
		elif not self.success_rate:
			self.success_rate = 0.0

		# Set default values for counters
		if self.total_views is None:
			self.total_views = 0
		if self.total_uses is None:
			self.total_uses = 0
		if self.total_renders is None:
			self.total_renders = 0
		if self.total_render_errors is None:
			self.total_render_errors = 0
		if self.unique_users is None:
			self.unique_users = 0
		if self.variable_error_count is None:
			self.variable_error_count = 0

	def before_save(self):
		"""Set timestamps and update metadata"""
		if not self.first_used_date and (self.total_views > 0 or self.total_uses > 0):
			self.first_used_date = now()

		if self.total_views > 0 or self.total_uses > 0 or self.total_renders > 0:
			self.last_used_date = now()

	@staticmethod
	def track_template_view(template_id, user=None):
		"""Track when a template is viewed"""
		analytics = ReportTemplateAnalytics.get_or_create_analytics(template_id)
		analytics.total_views = (analytics.total_views or 0) + 1
		analytics.last_used_date = now()

		# Update usage logs
		usage_logs = analytics.get_usage_logs()
		usage_logs.append({
			'action': 'view',
			'user': user or frappe.session.user,
			'timestamp': now(),
			'template_id': template_id
		})
		analytics.usage_logs = json.dumps(usage_logs[-1000:])  # Keep last 1000 entries

		analytics.save(ignore_permissions=True)
		frappe.db.commit()

	@staticmethod
	def track_template_usage(template_id, user=None, render_time=None, success=True, variables=None, error_details=None):
		"""Track when a template is used/rendered"""
		analytics = ReportTemplateAnalytics.get_or_create_analytics(template_id)
		analytics.total_uses = (analytics.total_uses or 0) + 1
		analytics.total_renders = (analytics.total_renders or 0) + 1
		analytics.last_used_date = now()

		# Track render performance
		if render_time is not None:
			analytics.update_render_metrics(render_time)

		# Track errors
		if not success:
			analytics.total_render_errors = (analytics.total_render_errors or 0) + 1

		# Track variable usage
		if variables:
			analytics.update_variable_usage(variables)

		# Track variable errors
		if error_details and 'variable_errors' in error_details:
			analytics.variable_error_count = (analytics.variable_error_count or 0) + len(error_details['variable_errors'])

		# Update usage logs
		usage_logs = analytics.get_usage_logs()
		log_entry = {
			'action': 'render',
			'user': user or frappe.session.user,
			'timestamp': now(),
			'template_id': template_id,
			'success': success,
			'render_time': render_time,
			'variables_count': len(variables) if variables else 0
		}

		if error_details:
			log_entry['error'] = str(error_details)

		usage_logs.append(log_entry)
		analytics.usage_logs = json.dumps(usage_logs[-1000:])  # Keep last 1000 entries

		# Update render logs
		render_logs = analytics.get_render_logs()
		render_logs.append(log_entry)
		analytics.render_logs = json.dumps(render_logs[-500:])  # Keep last 500 entries

		# Update error logs if there was an error
		if not success and error_details:
			error_logs = analytics.get_error_logs()
			error_logs.append({
				'timestamp': now(),
				'user': user or frappe.session.user,
				'error': str(error_details),
				'template_id': template_id
			})
			analytics.error_logs = json.dumps(error_logs[-200:])  # Keep last 200 entries

		analytics.save(ignore_permissions=True)
		frappe.db.commit()

	def update_render_metrics(self, render_time):
		"""Update render time metrics"""
		current_count = self.total_renders or 1

		if not self.average_render_time:
			self.average_render_time = render_time
			self.min_render_time = render_time
			self.max_render_time = render_time
		else:
			# Calculate running average
			self.average_render_time = ((self.average_render_time * (current_count - 1)) + render_time) / current_count

			# Update min/max
			if render_time < self.min_render_time:
				self.min_render_time = render_time
			if render_time > self.max_render_time:
				self.max_render_time = render_time

	def update_variable_usage(self, variables):
		"""Update variable usage statistics"""
		if not variables:
			return

		popular_vars = self.get_popular_variables()

		for var_name in variables.keys():
			if var_name in popular_vars:
				popular_vars[var_name] += 1
			else:
				popular_vars[var_name] = 1

		# Keep only top 20 most used variables
		sorted_vars = sorted(popular_vars.items(), key=lambda x: x[1], reverse=True)
		self.popular_variables = json.dumps(dict(sorted_vars[:20]))

	def get_usage_logs(self):
		"""Get usage logs as list"""
		try:
			return json.loads(self.usage_logs or '[]')
		except:
			return []

	def get_render_logs(self):
		"""Get render logs as list"""
		try:
			return json.loads(self.render_logs or '[]')
		except:
			return []

	def get_error_logs(self):
		"""Get error logs as list"""
		try:
			return json.loads(self.error_logs or '[]')
		except:
			return []

	def get_popular_variables(self):
		"""Get popular variables as dict"""
		try:
			return json.loads(self.popular_variables or '{}')
		except:
			return {}

	@staticmethod
	def get_or_create_analytics(template_id):
		"""Get existing analytics or create new one"""
		template = frappe.get_doc("Report Template", template_id)

		analytics_name = f"analytics_{template.template_name.lower().replace(' ', '_')}_{template_id}"

		if frappe.db.exists("Report Template Analytics", analytics_name):
			return frappe.get_doc("Report Template Analytics", analytics_name)
		else:
			# Create new analytics record
			analytics = frappe.new_doc("Report Template Analytics")
			analytics.template_id = template_id
			analytics.template_name = template.template_name
			
			# Map audit category to analytics category
			audit_category = getattr(template, 'audit_category', None)
			category_mapping = {
				"Financial": "Financial Report",
				"Compliance": "Compliance Report", 
				"IT Security": "Audit Report",
				"Operational": "Audit Report",
				"Fraud": "Audit Report",
				"Risk Assessment": "Risk Assessment",
				"Performance": "Audit Report",
				"Special Projects": "Custom Report"
			}
			analytics.category = category_mapping.get(audit_category, 'Audit Report')
			
			analytics.insert(ignore_permissions=True)
			return analytics

	@staticmethod
	def get_analytics_summary(template_id=None, date_from=None, date_to=None):
		"""Get analytics summary for dashboard"""
		filters = {}

		if template_id:
			filters['template_id'] = template_id

		if date_from and date_to:
			filters['last_used_date'] = ['between', [date_from, date_to]]

		analytics = frappe.get_all(
			"Report Template Analytics",
			filters=filters,
			fields=[
				"name", "template_name", "template_id", "category",
				"total_views", "total_uses", "total_renders",
				"average_render_time", "success_rate",
				"unique_users", "last_used_date"
			],
			order_by="total_uses desc"
		)

		return analytics

	@staticmethod
	def get_performance_metrics():
		"""Get overall performance metrics"""
		result = frappe.db.sql("""
			SELECT
				COUNT(*) as total_templates,
				SUM(total_views) as total_views,
				SUM(total_uses) as total_uses,
				SUM(total_renders) as total_renders,
				AVG(average_render_time) as avg_render_time,
				AVG(success_rate) as avg_success_rate,
				SUM(total_render_errors) as total_errors
			FROM `tabReport Template Analytics`
		""", as_dict=True)

		return result[0] if result else {}

	@staticmethod
	def cleanup_old_logs(days_to_keep=90):
		"""Clean up old analytics logs"""
		cutoff_date = datetime.now() - timedelta(days=days_to_keep)

		analytics_records = frappe.get_all("Report Template Analytics")

		for record in analytics_records:
			doc = frappe.get_doc("Report Template Analytics", record.name)

			# Clean usage logs
			usage_logs = doc.get_usage_logs()
			recent_logs = [log for log in usage_logs
						 if get_datetime(log.get('timestamp', '2000-01-01')) > cutoff_date]
			if len(recent_logs) != len(usage_logs):
				doc.usage_logs = json.dumps(recent_logs)
				doc.save(ignore_permissions=True)

			# Clean render logs
			render_logs = doc.get_render_logs()
			recent_renders = [log for log in render_logs
							if get_datetime(log.get('timestamp', '2000-01-01')) > cutoff_date]
			if len(recent_renders) != len(render_logs):
				doc.render_logs = json.dumps(recent_renders)
				doc.save(ignore_permissions=True)

			# Clean error logs
			error_logs = doc.get_error_logs()
			recent_errors = [log for log in error_logs
						   if get_datetime(log.get('timestamp', '2000-01-01')) > cutoff_date]
			if len(recent_errors) != len(error_logs):
				doc.error_logs = json.dumps(recent_errors)
				doc.save(ignore_permissions=True)

		frappe.db.commit()