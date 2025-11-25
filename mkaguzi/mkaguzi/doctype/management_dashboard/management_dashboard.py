# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, get_datetime, add_months, add_days

class ManagementDashboard(Document):
	def autoname(self):
		if not self.dashboard_id:
			# Generate dashboard ID in format MD-YYYY-####
			current_year = getdate().year

			last_dashboard = frappe.db.sql("""
				SELECT dashboard_id FROM `tabManagement Dashboard`
				WHERE dashboard_id LIKE 'MD-{}-%'
				ORDER BY CAST(SUBSTRING_INDEX(dashboard_id, '-', -1) AS UNSIGNED) DESC
				LIMIT 1
			""".format(current_year), as_dict=True)

			if last_dashboard:
				last_num = int(last_dashboard[0].dashboard_id.split('-')[-1])
				next_num = last_num + 1
			else:
				next_num = 1

			self.dashboard_id = f"MD-{current_year}-{next_num:04d}"

	def validate(self):
		self.validate_default_dashboard()
		self.set_audit_fields()
		self.calculate_kpis()

	def validate_default_dashboard(self):
		"""Ensure only one default dashboard per type"""
		if self.is_default:
			existing_default = frappe.db.exists("Management Dashboard", {
				"dashboard_type": self.dashboard_type,
				"is_default": 1,
				"name": ["!=", self.name]
			})

			if existing_default:
				frappe.throw(_("A default dashboard already exists for {0}. Please uncheck 'Is Default Dashboard' for the existing dashboard first.").format(self.dashboard_type))

	def set_audit_fields(self):
		"""Set audit trail fields"""
		if not self.created_by:
			self.created_by = frappe.session.user
		if not self.creation_date:
			self.creation_date = getdate()

		self.modified_by = frappe.session.user
		self.last_modified = get_datetime()

	def calculate_kpis(self):
		"""Calculate KPI values based on time period and filters"""
		if not self.kpi_section:
			return

		date_filters = self.get_date_filters()

		# Calculate engagement KPIs
		self.calculate_engagement_kpis(date_filters)

		# Calculate findings KPIs
		self.calculate_findings_kpis(date_filters)

		# Calculate compliance KPIs
		self.calculate_compliance_kpis(date_filters)

		# Calculate action KPIs
		self.calculate_action_kpis(date_filters)

		# Update last updated timestamp
		self.last_updated = get_datetime()

	def get_date_filters(self):
		"""Get date filters based on time period"""
		today = getdate()

		if self.time_period == "Current Month":
			start_date = today.replace(day=1)
			end_date = add_days(add_months(start_date, 1), -1)
		elif self.time_period == "Last Month":
			end_date = add_days(today.replace(day=1), -1)
			start_date = end_date.replace(day=1)
		elif self.time_period == "Current Quarter":
			quarter = (today.month - 1) // 3 + 1
			start_date = today.replace(month=(quarter-1)*3 + 1, day=1)
			end_date = add_days(add_months(start_date, 3), -1)
		elif self.time_period == "Last Quarter":
			current_quarter = (today.month - 1) // 3 + 1
			last_quarter = current_quarter - 1 if current_quarter > 1 else 4
			last_quarter_year = today.year if current_quarter > 1 else today.year - 1
			start_date = getdate(f"{last_quarter_year}-{((last_quarter-1)*3)+1}-01")
			end_date = add_days(add_months(start_date, 3), -1)
		elif self.time_period == "Current Year":
			start_date = today.replace(month=1, day=1)
			end_date = today.replace(month=12, day=31)
		elif self.time_period == "Last Year":
			start_date = getdate(f"{today.year-1}-01-01")
			end_date = getdate(f"{today.year-1}-12-31")
		elif self.time_period == "Custom Range":
			start_date = self.start_date
			end_date = self.end_date
		else:  # All Time
			start_date = None
			end_date = None

		return {"start_date": start_date, "end_date": end_date}

	def calculate_engagement_kpis(self, date_filters):
		"""Calculate engagement-related KPIs"""
		filters = {}
		if date_filters["start_date"] and date_filters["end_date"]:
			filters["start_date"] = [">=", date_filters["start_date"]]
			filters["end_date"] = ["<=", date_filters["end_date"]]

		# Total engagements
		total = frappe.db.count("Audit Engagement", filters=filters)
		self.total_engagements = total

		# Completed engagements
		completed_filters = filters.copy()
		completed_filters["engagement_status"] = "Completed"
		self.completed_engagements = frappe.db.count("Audit Engagement", filters=completed_filters)

		# In progress engagements
		progress_filters = filters.copy()
		progress_filters["engagement_status"] = "In Progress"
		self.in_progress_engagements = frappe.db.count("Audit Engagement", filters=progress_filters)

		# Overdue engagements
		overdue_filters = filters.copy()
		overdue_filters["end_date"] = ["<", getdate()]
		overdue_filters["engagement_status"] = ["!=", "Completed"]
		self.overdue_engagements = frappe.db.count("Audit Engagement", filters=overdue_filters)

	def calculate_findings_kpis(self, date_filters):
		"""Calculate findings-related KPIs"""
		# Get engagements in the date range
		engagement_filters = {}
		if date_filters["start_date"] and date_filters["end_date"]:
			engagement_filters["start_date"] = [">=", date_filters["start_date"]]
			engagement_filters["end_date"] = ["<=", date_filters["end_date"]]

		engagements = frappe.get_all("Audit Engagement",
			filters=engagement_filters,
			fields=["name"]
		)

		if not engagements:
			self.total_findings = 0
			self.critical_findings = 0
			self.high_findings = 0
			self.medium_findings = 0
			self.low_findings = 0
			return

		engagement_names = [e.name for e in engagements]

		# Total findings
		total_findings = frappe.db.count("Audit Finding",
			filters={"engagement_reference": ["in", engagement_names]}
		)
		self.total_findings = total_findings

		# Findings by risk level
		risk_levels = ["Critical", "High", "Medium", "Low"]
		for risk in risk_levels:
			count = frappe.db.count("Audit Finding",
				filters={
					"engagement_reference": ["in", engagement_names],
					"risk_rating": risk
				}
			)
			setattr(self, f"{risk.lower()}_findings", count)

	def calculate_compliance_kpis(self, date_filters):
		"""Calculate compliance-related KPIs"""
		if not self.compliance_section:
			return

		# Get compliance requirements in date range
		filters = {}
		if date_filters["start_date"] and date_filters["end_date"]:
			filters["creation"] = [">=", date_filters["start_date"]]
			filters["creation"] = ["<=", date_filters["end_date"]]

		total_requirements = frappe.db.count("Compliance Requirement", filters=filters)

		if total_requirements == 0:
			self.compliance_score = 0
			self.compliant_items = 0
			self.non_compliant_items = 0
			self.pending_reviews = 0
			return

		# Compliant items
		compliant = frappe.db.count("Compliance Requirement",
			filters={**filters, "compliance_status": "Compliant"}
		)
		self.compliant_items = compliant

		# Non-compliant items
		non_compliant = frappe.db.count("Compliance Requirement",
			filters={**filters, "compliance_status": "Non-Compliant"}
		)
		self.non_compliant_items = non_compliant

		# Pending reviews
		pending = frappe.db.count("Compliance Requirement",
			filters={**filters, "compliance_status": "Under Review"}
		)
		self.pending_reviews = pending

		# Compliance score
		if total_requirements > 0:
			self.compliance_score = (compliant / total_requirements) * 100

	def calculate_action_kpis(self, date_filters):
		"""Calculate corrective action KPIs"""
		# Get action plans in date range
		filters = {}
		if date_filters["start_date"] and date_filters["end_date"]:
			filters["creation"] = [">=", date_filters["start_date"]]
			filters["creation"] = ["<=", date_filters["end_date"]]

		# Overdue actions
		overdue = frappe.db.count("Corrective Action Plan",
			filters={
				**filters,
				"target_completion_date": ["<", getdate()],
				"action_status": ["!=", "Completed"]
			}
		)
		self.overdue_actions = overdue

		# Completed actions
		completed = frappe.db.count("Corrective Action Plan",
			filters={**filters, "action_status": "Completed"}
		)
		self.completed_actions = completed

		# In progress actions
		in_progress = frappe.db.count("Corrective Action Plan",
			filters={**filters, "action_status": "In Progress"}
		)
		self.in_progress_actions = in_progress

	def on_update(self):
		"""Handle dashboard updates"""
		if self.has_value_changed("is_default") and self.is_default:
			# Clear default flag from other dashboards of same type
			frappe.db.sql("""
				UPDATE `tabManagement Dashboard`
				SET is_default = 0
				WHERE dashboard_type = %s AND name != %s
			""", (self.dashboard_type, self.name))

@frappe.whitelist()
def get_dashboard_data(dashboard_name):
	"""Get dashboard data for frontend display"""
	dashboard = frappe.get_doc("Management Dashboard", dashboard_name)

	data = {
		"kpis": {
			"total_engagements": dashboard.total_engagements,
			"completed_engagements": dashboard.completed_engagements,
			"in_progress_engagements": dashboard.in_progress_engagements,
			"overdue_engagements": dashboard.overdue_engagements,
			"total_findings": dashboard.total_findings,
			"critical_findings": dashboard.critical_findings,
			"high_findings": dashboard.high_findings,
			"medium_findings": dashboard.medium_findings,
			"low_findings": dashboard.low_findings,
			"compliance_score": dashboard.compliance_score,
			"compliant_items": dashboard.compliant_items,
			"non_compliant_items": dashboard.non_compliant_items,
			"pending_reviews": dashboard.pending_reviews,
			"overdue_actions": dashboard.overdue_actions,
			"completed_actions": dashboard.completed_actions,
			"in_progress_actions": dashboard.in_progress_actions
		},
		"charts": {},
		"last_updated": dashboard.last_updated
	}

	# Generate chart data if charts are enabled
	if dashboard.chart_configuration:
		data["charts"] = generate_chart_data(dashboard)

	return data

@frappe.whitelist()
def generate_chart_data(dashboard):
	"""Generate chart data for dashboard"""
	charts = {}

	# Chart 1: Engagement Status
	if dashboard.chart_1_data_source == "Engagement Status":
		charts["chart1"] = {
			"type": dashboard.chart_1_type,
			"title": dashboard.chart_1_title,
			"data": {
				"labels": ["Completed", "In Progress", "Overdue"],
				"datasets": [{
					"data": [
						dashboard.completed_engagements,
						dashboard.in_progress_engagements,
						dashboard.overdue_engagements
					],
					"backgroundColor": ["#28a745", "#ffc107", "#dc3545"]
				}]
			}
		}

	# Chart 2: Findings by Risk
	if dashboard.chart_2_data_source == "Findings by Risk":
		charts["chart2"] = {
			"type": dashboard.chart_2_type,
			"title": dashboard.chart_2_title,
			"data": {
				"labels": ["Critical", "High", "Medium", "Low"],
				"datasets": [{
					"data": [
						dashboard.critical_findings,
						dashboard.high_findings,
						dashboard.medium_findings,
						dashboard.low_findings
					],
					"backgroundColor": ["#dc3545", "#fd7e14", "#ffc107", "#28a745"]
				}]
			}
		}

	# Chart 3: Compliance Status
	if dashboard.chart_3_data_source == "Compliance Status":
		charts["chart3"] = {
			"type": dashboard.chart_3_type,
			"title": dashboard.chart_3_title,
			"data": {
				"labels": ["Compliant", "Non-Compliant", "Under Review"],
				"datasets": [{
					"data": [
						dashboard.compliant_items,
						dashboard.non_compliant_items,
						dashboard.pending_reviews
					],
					"backgroundColor": ["#28a745", "#dc3545", "#ffc107"]
				}]
			}
		}

	# Chart 4: Action Items Status
	if dashboard.chart_4_data_source == "Actions Status":
		charts["chart4"] = {
			"type": dashboard.chart_4_type,
			"title": dashboard.chart_4_title,
			"data": {
				"labels": ["Completed", "In Progress", "Overdue"],
				"datasets": [{
					"data": [
						dashboard.completed_actions,
						dashboard.in_progress_actions,
						dashboard.overdue_actions
					],
					"backgroundColor": ["#28a745", "#ffc107", "#dc3545"]
				}]
			}
		}

	return charts

@frappe.whitelist()
def refresh_dashboard(dashboard_name):
	"""Refresh dashboard KPIs and data"""
	dashboard = frappe.get_doc("Management Dashboard", dashboard_name)
	dashboard.calculate_kpis()
	dashboard.save()

	return {"message": "Dashboard refreshed successfully", "last_updated": dashboard.last_updated}

@frappe.whitelist()
def create_default_dashboards():
	"""Create default dashboards for each type"""
	dashboard_types = [
		"Management Overview",
		"Compliance Dashboard",
		"Risk Dashboard",
		"Operational Dashboard",
		"Executive Summary"
	]

	for dashboard_type in dashboard_types:
		# Check if default dashboard already exists
		existing = frappe.db.exists("Management Dashboard", {
			"dashboard_type": dashboard_type,
			"is_default": 1
		})

		if not existing:
			dashboard = frappe.new_doc("Management Dashboard")
			dashboard.dashboard_title = f"Default {dashboard_type}"
			dashboard.dashboard_type = dashboard_type
			dashboard.description = f"Default dashboard for {dashboard_type.lower()}"
			dashboard.is_default = 1
			dashboard.is_active = 1
			dashboard.time_period = "Current Month"
			dashboard.auto_refresh = 1
			dashboard.refresh_interval = "30 minutes"

			# Set type-specific defaults
			if dashboard_type == "Compliance Dashboard":
				dashboard.compliance_section = 1
				dashboard.chart_1_data_source = "Compliance Status"
				dashboard.chart_2_data_source = "Actions Status"
			elif dashboard_type == "Risk Dashboard":
				dashboard.chart_1_data_source = "Findings by Risk"
				dashboard.chart_2_data_source = "Engagement Status"
			elif dashboard_type == "Executive Summary":
				dashboard.kpi_section = 1
				dashboard.compliance_section = 1
				dashboard.chart_1_type = "Bar Chart"
				dashboard.chart_2_type = "Pie Chart"

			dashboard.save()
			frappe.msgprint(_("Created default dashboard: {0}").format(dashboard.dashboard_title))

	return {"message": "Default dashboards created successfully"}