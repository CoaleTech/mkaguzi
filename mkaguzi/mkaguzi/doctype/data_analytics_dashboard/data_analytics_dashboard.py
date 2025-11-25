# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, now_datetime, getdate, cint
import json
import time
from frappe.utils.background_jobs import enqueue

class DataAnalyticsDashboard(Document):
	def autoname(self):
		"""Generate unique Dashboard ID"""
		if not self.dashboard_id:
			# Generate DAD-YYYY-NNNN format
			current_year = str(getdate(nowdate()).year)
			prefix = f"DAD-{current_year}-"

			# Get the last DAD number for this year
			last_dashboard = frappe.db.sql("""
				SELECT dashboard_id
				FROM `tabData Analytics Dashboard`
				WHERE dashboard_id LIKE %s
				ORDER BY dashboard_id DESC
				LIMIT 1
			""", (prefix + "%",))

			if last_dashboard:
				# Extract the number from the last ID
				last_num = int(last_dashboard[0][0].split('-')[-1])
				next_num = last_num + 1
			else:
				next_num = 1

			# Format with leading zeros
			self.dashboard_id = f"{prefix}{next_num:04d}"

	def validate(self):
		"""Validate dashboard data"""
		self.validate_permissions()
		self.validate_layout()
		self.validate_data_sources()
		self.set_metadata()

	def validate_permissions(self):
		"""Validate user permissions"""
		if self.dashboard_type == "Private" and self.user_permissions:
			frappe.throw(_("Private dashboards cannot have user permissions"))

		if self.user_permissions:
			for perm in self.user_permissions:
				if not perm.user and not perm.user_role:
					frappe.throw(_("Each permission must have either a user or role specified"))

	def validate_layout(self):
		"""Validate layout configuration"""
		if self.layout_configuration:
			try:
				layout = json.loads(self.layout_configuration)
				# Basic validation - could be enhanced
			except json.JSONDecodeError:
				frappe.throw(_("Invalid JSON in layout configuration"))

	def validate_data_sources(self):
		"""Validate data sources"""
		if self.data_sources:
			source_names = []
			for source in self.data_sources:
				if source.data_source_name in source_names:
					frappe.throw(_("Duplicate data source name: {0}").format(source.data_source_name))
				source_names.append(source.data_source_name)

	def set_metadata(self):
		"""Set creation and modification metadata"""
		if not self.created_by:
			self.created_by = frappe.session.user
		if not self.creation_date:
			self.creation_date = now_datetime()

	def on_update(self):
		"""Handle updates"""
		self.update_default_dashboard()

	def update_default_dashboard(self):
		"""Ensure only one default dashboard exists"""
		if self.is_default:
			# Unset default flag for other dashboards
			frappe.db.sql("""
				UPDATE `tabData Analytics Dashboard`
				SET is_default = 0
				WHERE name != %s AND is_default = 1
			""", self.name)

	def before_save(self):
		"""Handle before save operations"""
		if self.is_default and not self.is_active:
			frappe.throw(_("Default dashboard must be active"))

@frappe.whitelist()
def get_dashboard_data(dashboard_id, filters=None):
	"""Get dashboard data for rendering"""
	try:
		dashboard = frappe.get_doc("Data Analytics Dashboard", dashboard_id)

		# Check permissions
		if not has_dashboard_access(dashboard, frappe.session.user):
			frappe.throw(_("Access denied to dashboard"))

		# Update view metrics
		update_dashboard_metrics(dashboard_id)

		# Prepare filters
		filter_params = {}
		if filters:
			if isinstance(filters, str):
				filter_params = json.loads(filters)
			else:
				filter_params = filters

		# Get data for each chart
		chart_data = {}
		if dashboard.dashboard_charts:
			for chart in dashboard.dashboard_charts:
				if chart.is_active:
					chart_data[chart.chart_name] = get_chart_data(chart, filter_params)

		# Get data source information
		data_sources = {}
		if dashboard.data_sources:
			for source in dashboard.data_sources:
				if source.is_active:
					data_sources[source.data_source_name] = {
						"type": source.data_source_type,
						"last_refresh": source.last_refresh
					}

		return {
			"dashboard": {
				"id": dashboard.dashboard_id,
				"name": dashboard.dashboard_name,
				"description": dashboard.description,
				"type": dashboard.dashboard_type,
				"layout": json.loads(dashboard.layout_configuration) if dashboard.layout_configuration else {},
				"auto_refresh": dashboard.auto_refresh_interval or 0,
				"export_enabled": dashboard.export_enabled,
				"sharing_enabled": dashboard.sharing_enabled
			},
			"charts": chart_data,
			"data_sources": data_sources,
			"filters": get_dashboard_filters(dashboard)
		}

	except Exception as e:
		frappe.log_error(f"Dashboard data retrieval failed: {str(e)}", "Dashboard Data")
		frappe.throw(_("Failed to load dashboard data: {0}").format(str(e)))

def get_chart_data(chart, filters):
	"""Get data for a specific chart"""
	try:
		if chart.data_source not in ["Test Execution", "Audit Test Library", "Database"]:
			return {"error": "Unsupported data source type"}

		# Build query based on chart configuration
		if chart.data_source == "Test Execution":
			data = get_test_execution_data(chart, filters)
		elif chart.data_source == "Audit Test Library":
			data = get_test_library_data(chart, filters)
		else:
			data = get_database_chart_data(chart, filters)

		return {
			"type": chart.chart_type,
			"title": chart.chart_title,
			"data": data,
			"config": {
				"x_axis": chart.x_axis_field,
				"y_axis": chart.y_axis_field,
				"show_legend": chart.show_legend,
				"show_grid": chart.show_grid,
				"color_scheme": chart.color_scheme
			}
		}

	except Exception as e:
		return {"error": str(e)}

def get_test_execution_data(chart, filters):
	"""Get test execution data for charts"""
	query_filters = {}

	# Apply dashboard filters
	if filters:
		if "date_from" in filters:
			query_filters["actual_start_date"] = [">=", filters["date_from"]]
		if "date_to" in filters:
			query_filters["actual_end_date"] = ["<=", filters["date_to"]]
		if "status" in filters:
			query_filters["status"] = filters["status"]

	# Build query based on chart type
	if chart.chart_type == "Bar Chart":
		# Status distribution
		data = frappe.db.get_all("Test Execution",
			filters=query_filters,
			fields=["status", "COUNT(*) as count"],
			group_by="status"
		)
		return [{"label": d.status, "value": d.count} for d in data]

	elif chart.chart_type == "Line Chart":
		# Execution trends over time
		data = frappe.db.sql("""
			SELECT DATE(actual_start_date) as date, COUNT(*) as count
			FROM `tabTest Execution`
			WHERE actual_start_date IS NOT NULL
			GROUP BY DATE(actual_start_date)
			ORDER BY date
		""", as_dict=True)
		return [{"date": str(d.date), "executions": d.count} for d in data]

	return []

def get_test_library_data(chart, filters):
	"""Get test library data for charts"""
	if chart.chart_type == "Pie Chart":
		# Test categories distribution
		data = frappe.db.get_all("Audit Test Library",
			filters={"status": "Active"},
			fields=["test_category", "COUNT(*) as count"],
			group_by="test_category"
		)
		return [{"label": d.test_category, "value": d.count} for d in data]

	elif chart.chart_type == "Bar Chart":
		# Usage statistics
		data = frappe.db.sql("""
			SELECT test_name, usage_count
			FROM `tabAudit Test Library`
			WHERE status = 'Active' AND usage_count > 0
			ORDER BY usage_count DESC
			LIMIT 10
		""", as_dict=True)
		return [{"test": d.test_name, "usage": d.usage_count} for d in data]

	return []

def get_database_chart_data(chart, filters):
	"""Get data from database queries"""
	# This would execute custom SQL queries defined in data sources
	# For security, this should be restricted and validated
	return {"message": "Database queries not implemented in sandbox"}

def get_dashboard_filters(dashboard):
	"""Get dashboard filter configuration"""
	filters = []
	if dashboard.dashboard_filters:
		for f in dashboard.dashboard_filters:
			filters.append({
				"name": f.filter_name,
				"type": f.filter_type,
				"field": f.field_name,
				"default": f.default_value,
				"required": f.is_required,
				"global": f.is_global
			})
	return filters

def has_dashboard_access(dashboard, user):
	"""Check if user has access to dashboard"""
	if dashboard.dashboard_type == "Public":
		return True

	if dashboard.created_by == user:
		return True

	# Check user permissions
	if dashboard.user_permissions:
		for perm in dashboard.user_permissions:
			if perm.permission_type == "User" and perm.user == user and perm.can_view:
				return True
			elif perm.permission_type == "Role":
				user_roles = frappe.get_roles(user)
				if perm.user_role in user_roles and perm.can_view:
					return True

	return False

def update_dashboard_metrics(dashboard_id):
	"""Update dashboard view metrics"""
	try:
		dashboard = frappe.get_doc("Data Analytics Dashboard", dashboard_id)

		# Update view count
		dashboard.total_views = (dashboard.total_views or 0) + 1
		dashboard.last_viewed_by = frappe.session.user
		dashboard.last_viewed_date = now_datetime()

		# Calculate average load time (simplified)
		if dashboard.average_load_time:
			dashboard.average_load_time = (dashboard.average_load_time + 1.5) / 2  # Mock load time
		else:
			dashboard.average_load_time = 1.5

		dashboard.save(ignore_permissions=True)

	except Exception as e:
		frappe.log_error(f"Failed to update dashboard metrics: {str(e)}")

@frappe.whitelist()
def create_default_dashboard():
	"""Create a default analytics dashboard"""
	try:
		# Check if default dashboard exists
		existing = frappe.db.exists("Data Analytics Dashboard", {"is_default": 1})
		if existing:
			frappe.throw(_("Default dashboard already exists"))

		# Create default dashboard
		dashboard = frappe.new_doc("Data Analytics Dashboard")
		dashboard.dashboard_name = "Audit Analytics Overview"
		dashboard.dashboard_type = "Public"
		dashboard.description = "Default dashboard showing key audit analytics and test execution metrics"
		dashboard.is_active = 1
		dashboard.is_default = 1
		dashboard.auto_refresh_interval = 300  # 5 minutes
		dashboard.manual_refresh_enabled = 1
		dashboard.export_enabled = 1

		# Add data sources
		dashboard.append("data_sources", {
			"data_source_name": "Test Executions",
			"data_source_type": "Test Execution",
			"refresh_interval": 60
		})

		dashboard.append("data_sources", {
			"data_source_name": "Test Library",
			"data_source_type": "Audit Test Library",
			"refresh_interval": 300
		})

		# Add charts
		dashboard.append("dashboard_charts", {
			"chart_name": "Test Status Distribution",
			"chart_type": "Pie Chart",
			"data_source": "Test Executions",
			"chart_title": "Test Execution Status Distribution",
			"width": 6,
			"height": 4,
			"position_x": 0,
			"position_y": 0
		})

		dashboard.append("dashboard_charts", {
			"chart_name": "Execution Trends",
			"chart_type": "Line Chart",
			"data_source": "Test Executions",
			"chart_title": "Test Execution Trends",
			"width": 6,
			"height": 4,
			"position_x": 6,
			"position_y": 0
		})

		dashboard.append("dashboard_charts", {
			"chart_name": "Test Categories",
			"chart_type": "Bar Chart",
			"data_source": "Test Library",
			"chart_title": "Test Library Categories",
			"width": 6,
			"height": 4,
			"position_x": 0,
			"position_y": 4
		})

		# Add filters
		dashboard.append("dashboard_filters", {
			"filter_name": "Date Range",
			"filter_type": "Date Range",
			"field_name": "date_range",
			"is_global": 1,
			"position": 1
		})

		dashboard.append("dashboard_filters", {
			"filter_name": "Status",
			"filter_type": "Select",
			"field_name": "status",
			"is_global": 1,
			"position": 2
		})

		dashboard.insert()
		return dashboard.name

	except Exception as e:
		frappe.throw(_("Failed to create default dashboard: {0}").format(str(e)))

@frappe.whitelist()
def export_dashboard_data(dashboard_id, format="json"):
	"""Export dashboard data"""
	try:
		dashboard = frappe.get_doc("Data Analytics Dashboard", dashboard_id)

		if not dashboard.export_enabled:
			frappe.throw(_("Export not enabled for this dashboard"))

		if not has_dashboard_access(dashboard, frappe.session.user):
			frappe.throw(_("Access denied"))

		data = get_dashboard_data(dashboard_id)

		if format == "json":
			return json.dumps(data, indent=2)
		else:
			frappe.throw(_("Unsupported export format"))

	except Exception as e:
		frappe.throw(_("Export failed: {0}").format(str(e)))

@frappe.whitelist()
def refresh_dashboard_data(dashboard_id):
	"""Manually refresh dashboard data"""
	try:
		dashboard = frappe.get_doc("Data Analytics Dashboard", dashboard_id)

		if not dashboard.manual_refresh_enabled:
			frappe.throw(_("Manual refresh not enabled"))

		dashboard.last_refresh_date = now_datetime()
		dashboard.save()

		# Update data sources last refresh
		if dashboard.data_sources:
			for source in dashboard.data_sources:
				source.last_refresh = now_datetime()

		return {"status": "success", "message": "Dashboard refreshed successfully"}

	except Exception as e:
		frappe.throw(_("Refresh failed: {0}").format(str(e)))

@frappe.whitelist()
def get_user_dashboards(user=None):
	"""Get dashboards accessible to user"""
	if not user:
		user = frappe.session.user

	dashboards = []

	# Get public dashboards
	public_dashboards = frappe.get_all("Data Analytics Dashboard",
		filters={"dashboard_type": "Public", "is_active": 1},
		fields=["name", "dashboard_id", "dashboard_name", "description", "is_default"]
	)
	dashboards.extend(public_dashboards)

	# Get user's private dashboards
	private_dashboards = frappe.get_all("Data Analytics Dashboard",
		filters={"created_by": user, "dashboard_type": "Private", "is_active": 1},
		fields=["name", "dashboard_id", "dashboard_name", "description", "is_default"]
	)
	dashboards.extend(private_dashboards)

	# Get shared dashboards (simplified - would need more complex permission checking)
	shared_dashboards = frappe.db.sql("""
		SELECT DISTINCT d.name, d.dashboard_id, d.dashboard_name, d.description, d.is_default
		FROM `tabData Analytics Dashboard` d
		INNER JOIN `tabDashboard User Permission` p ON d.name = p.parent
		WHERE d.dashboard_type = 'Shared' AND d.is_active = 1
		AND (p.user = %s OR p.user_role IN (
			SELECT role FROM `tabHas Role` WHERE parent = %s
		))
	""", (user, user), as_dict=True)
	dashboards.extend(shared_dashboards)

	return dashboards