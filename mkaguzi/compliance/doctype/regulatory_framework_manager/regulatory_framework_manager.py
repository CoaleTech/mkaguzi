# -*- coding: utf-8 -*-
# Copyright (c) 2024, Coale Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, get_datetime, add_to_date, getdate, date_diff
import json
import uuid
from datetime import datetime, timedelta
from collections import defaultdict


class RegulatoryFrameworkManager(Document):
	def validate(self):
		"""Validate the regulatory framework manager"""
		self.validate_framework_id()
		self.set_default_values()
		self.validate_configurations()
		self.validate_dates()
		self.update_compliance_score()

	def validate_framework_id(self):
		"""Auto-generate framework ID if not provided"""
		if not self.framework_id:
			type_short = self.framework_type[:3].upper() if self.framework_type else "GEN"
			random_suffix = ''.join(str(uuid.uuid4().hex)[:6])
			self.framework_id = f"RFM-{type_short}-{random_suffix}"

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
		config_fields = ['monitoring_config', 'alerts_config', 'integration_config',
						'change_management', 'version_history', 'performance_metrics']

		for field in config_fields:
			value = getattr(self, field, None)
			if value:
				try:
					json.loads(value)
				except json.JSONDecodeError:
					frappe.throw(_(f"{field.replace('_', ' ').title()} must be valid JSON"))

	def validate_dates(self):
		"""Validate date fields"""
		if self.next_review_date and self.last_reviewed:
			if self.next_review_date <= self.last_reviewed:
				frappe.throw(_("Next Review Date must be after Last Reviewed Date"))

		if self.effective_date and self.effective_date < getdate():
			if self.status == "Active":
				frappe.msgprint(_("Framework is active but effective date is in the past"))

	def update_compliance_score(self):
		"""Update compliance score based on requirements"""
		try:
			if not self.requirements_table:
				return

			total_requirements = len(self.requirements_table)
			if total_requirements == 0:
				return

			compliant_count = 0
			for requirement in self.requirements_table:
				if requirement.compliance_status == "Compliant":
					compliant_count += 1

			self.compliance_score = (compliant_count / total_requirements) * 100

		except Exception as e:
			frappe.logger().error(f"Compliance score update error: {str(e)}")

	def on_update(self):
		"""Called when document is updated"""
		self.track_version_changes()
		self.check_compliance_alerts()
		self.update_related_assessments()

	def track_version_changes(self):
		"""Track version changes in history"""
		try:
			if not self.version_history:
				self.version_history = json.dumps([])

			history = json.loads(self.version_history)

			# Add new version entry if version changed
			if not history or history[-1].get('version') != self.version:
				history.append({
					"version": self.version,
					"changed_on": now(),
					"changed_by": frappe.session.user,
					"status": self.status,
					"effective_date": str(self.effective_date) if self.effective_date else None,
					"changes": "Framework updated"
				})

				# Keep only last 10 versions
				if len(history) > 10:
					history = history[-10:]

				self.version_history = json.dumps(history)

		except Exception as e:
			frappe.logger().error(f"Version tracking error: {str(e)}")

	def check_compliance_alerts(self):
		"""Check and trigger compliance alerts"""
		try:
			if self.status != "Active":
				return

			alerts_config = json.loads(self.alerts_config or "{}")
			alerts = alerts_config.get('alerts', [])

			for alert in alerts:
				if self.evaluate_alert_condition(alert):
					self.trigger_alert(alert)

		except Exception as e:
			frappe.logger().error(f"Compliance alert check error: {str(e)}")

	def evaluate_alert_condition(self, alert):
		"""Evaluate alert condition"""
		try:
			condition = alert.get('condition', {})
			metric = condition.get('metric')
			operator = condition.get('operator', '>')
			threshold = condition.get('value', 0)

			current_value = self.get_metric_value(metric)

			if operator == '>':
				return current_value > threshold
			elif operator == '<':
				return current_value < threshold
			elif operator == '>=':
				return current_value >= threshold
			elif operator == '<=':
				return current_value <= threshold
			elif operator == '==':
				return current_value == threshold

			return False

		except Exception as e:
			return False

	def get_metric_value(self, metric):
		"""Get current metric value"""
		try:
			if metric == "compliance_score":
				return self.compliance_score or 0
			elif metric == "days_to_expiry":
				if self.next_review_date:
					return date_diff(self.next_review_date, getdate())
				return 999
			elif metric == "non_compliant_requirements":
				if self.requirements_table:
					return len([r for r in self.requirements_table if r.compliance_status != "Compliant"])
				return 0
			elif metric == "overdue_milestones":
				if self.timeline:
					return len([t for t in self.timeline if t.due_date and t.due_date < getdate() and t.status != "Completed"])
				return 0

			return 0

		except Exception as e:
			return 0

	def trigger_alert(self, alert):
		"""Trigger framework alert"""
		try:
			alert_type = alert.get('type', 'notification')
			message = alert.get('message', 'Alert triggered')
			recipients = alert.get('recipients', [])

			if alert_type == 'email':
				frappe.sendmail(
					recipients=recipients,
					subject=f"Regulatory Framework Alert: {self.framework_name}",
					message=message
				)
			elif alert_type == 'notification':
				for recipient in recipients:
					frappe.get_doc({
						"doctype": "Notification Log",
						"subject": f"Framework Alert: {self.framework_name}",
						"email_content": message,
						"document_type": "Regulatory Framework Manager",
						"document_name": self.name,
						"for_user": recipient
					}).insert()

		except Exception as e:
			frappe.logger().error(f"Alert trigger error: {str(e)}")

	def update_related_assessments(self):
		"""Update related compliance assessments"""
		try:
			# Find related compliance assessments
			assessments = frappe.get_all("Compliance Assessment",
				filters={"compliance_framework": self.framework_name},
				fields=["name"]
			)

			for assessment in assessments:
				assessment_doc = frappe.get_doc("Compliance Assessment", assessment.name)
				assessment_doc.flags.ignore_validate = True
				assessment_doc.save()

		except Exception as e:
			frappe.logger().error(f"Related assessments update error: {str(e)}")

	def create_implementation_task(self, requirement_name, task_details):
		"""Create implementation task for a requirement"""
		try:
			task = frappe.get_doc({
				"doctype": "Task",
				"subject": f"Implement {requirement_name} - {self.framework_name}",
				"description": task_details.get('description', ''),
				"priority": task_details.get('priority', 'Medium'),
				"exp_start_date": task_details.get('start_date'),
				"exp_end_date": task_details.get('end_date'),
				"assigned_to": task_details.get('assigned_to'),
				"project": self.get_implementation_project()
			})

			task.insert()
			return task.name

		except Exception as e:
			frappe.logger().error(f"Implementation task creation error: {str(e)}")
			return None

	def get_implementation_project(self):
		"""Get or create implementation project"""
		try:
			project_name = f"Regulatory Implementation - {self.framework_name}"

			if not frappe.db.exists("Project", project_name):
				project = frappe.get_doc({
					"doctype": "Project",
					"project_name": project_name,
					"status": "Open",
					"expected_start_date": getdate(),
					"expected_end_date": self.next_review_date
				})
				project.insert()
				return project.name

			return project_name

		except Exception as e:
			frappe.logger().error(f"Implementation project error: {str(e)}")
			return None

	def generate_gap_analysis_report(self):
		"""Generate gap analysis report"""
		try:
			gaps = []

			if self.requirements_table:
				for requirement in self.requirements_table:
					if requirement.compliance_status != "Compliant":
						gaps.append({
							"requirement": requirement.requirement_name,
							"current_status": requirement.compliance_status,
							"gap_description": requirement.gap_description or "Not assessed",
							"priority": requirement.priority,
							"estimated_effort": requirement.estimated_effort
						})

			report = {
				"framework_name": self.framework_name,
				"total_requirements": len(self.requirements_table) if self.requirements_table else 0,
				"compliant_requirements": len([r for r in (self.requirements_table or []) if r.compliance_status == "Compliant"]),
				"gaps_identified": len(gaps),
				"gap_details": gaps,
				"generated_on": now()
			}

			self.gap_analysis = json.dumps(report, indent=2)
			self.save()

			return report

		except Exception as e:
			frappe.logger().error(f"Gap analysis report generation error: {str(e)}")
			return {"error": str(e)}

	def schedule_review_reminder(self):
		"""Schedule review reminder"""
		try:
			if not self.next_review_date:
				return

			# Schedule reminder 30 days before review date
			reminder_date = add_to_date(self.next_review_date, days=-30)

			if reminder_date > getdate():
				frappe.get_doc({
					"doctype": "ToDo",
					"description": f"Review Regulatory Framework: {self.framework_name}",
					"date": reminder_date,
					"assigned_by": self.created_by,
					"reference_type": "Regulatory Framework Manager",
					"reference_name": self.name
				}).insert()

		except Exception as e:
			frappe.logger().error(f"Review reminder scheduling error: {str(e)}")

	def get_compliance_trends(self, months=12):
		"""Get compliance trends over time"""
		try:
			end_date = getdate()
			start_date = add_to_date(end_date, months=-months)

			trends = frappe.db.sql("""
				SELECT
					DATE_FORMAT(modified, '%Y-%m') as month,
					AVG(compliance_score) as avg_score,
					COUNT(*) as assessments_count
				FROM `tabCompliance Assessment`
				WHERE compliance_framework = %s
				AND modified BETWEEN %s AND %s
				GROUP BY DATE_FORMAT(modified, '%Y-%m')
				ORDER BY month
			""", (self.framework_name, start_date, end_date), as_dict=True)

			return {
				"framework": self.framework_name,
				"period_months": months,
				"trends": trends
			}

		except Exception as e:
			return {"error": str(e)}

	def export_framework_data(self, export_format="json"):
		"""Export framework data"""
		try:
			data = {
				"framework_info": {
					"id": self.framework_id,
					"name": self.framework_name,
					"type": self.framework_type,
					"version": self.version,
					"status": self.status,
					"compliance_score": self.compliance_score
				},
				"requirements": self.get_requirements_data(),
				"implementation": {
					"status": self.implementation_status,
					"gap_analysis": json.loads(self.gap_analysis or "{}"),
					"responsible_parties": self.get_responsible_parties_data(),
					"timeline": self.get_timeline_data()
				},
				"exported_on": now()
			}

			if export_format == "json":
				return json.dumps(data, indent=2, default=str)
			else:
				return data

		except Exception as e:
			return {"error": str(e)}

	def get_requirements_data(self):
		"""Get requirements data for export"""
		try:
			if not self.requirements_table:
				return []

			return [{
				"name": req.requirement_name,
				"type": req.requirement_type,
				"status": req.compliance_status,
				"priority": req.priority,
				"description": req.description,
				"evidence": req.compliance_evidence
			} for req in self.requirements_table]

		except Exception as e:
			return []

	def get_responsible_parties_data(self):
		"""Get responsible parties data"""
		try:
			if not self.responsible_parties:
				return []

			return [{
				"party": party.responsible_party,
				"role": party.role,
				"contact": party.contact_info
			} for party in self.responsible_parties]

		except Exception as e:
			return []

	def get_timeline_data(self):
		"""Get timeline data"""
		try:
			if not self.timeline:
				return []

			return [{
				"milestone": item.milestone,
				"due_date": str(item.due_date) if item.due_date else None,
				"status": item.status,
				"description": item.description
			} for item in self.timeline]

		except Exception as e:
			return []


@frappe.whitelist()
def create_framework_from_template(template_name, customizations=None):
	"""Create framework from template"""
	try:
		template = get_framework_template(template_name)

		if customizations:
			customizations = json.loads(customizations)
			template.update(customizations)

		framework = frappe.get_doc({
			"doctype": "Regulatory Framework Manager",
			**template
		})

		framework.insert()
		return framework.name

	except Exception as e:
		frappe.log_error(f"Framework creation from template error: {str(e)}")
		return {"error": str(e)}


@frappe.whitelist()
def get_framework_templates():
	"""Get available framework templates"""
	return {
		"templates": [
			{
				"name": "GDPR Compliance",
				"type": "Data Protection",
				"description": "EU General Data Protection Regulation framework"
			},
			{
				"name": "SOX Compliance",
				"type": "Financial Regulation",
				"description": "Sarbanes-Oxley Act compliance framework"
			},
			{
				"name": "ISO 27001",
				"type": "International Standard",
				"description": "Information Security Management System"
			},
			{
				"name": "PCI DSS",
				"type": "Financial Regulation",
				"description": "Payment Card Industry Data Security Standard"
			}
		]
	}


def get_framework_template(template_name):
	"""Get framework template data"""
	templates = {
		"GDPR Compliance": {
			"framework_name": "GDPR Compliance Framework",
			"framework_type": "Data Protection",
			"description": "EU General Data Protection Regulation compliance framework",
			"version": "1.0",
			"effective_date": getdate(),
			"key_requirements": "Data protection principles, lawful processing, data subject rights, breach notification, DPIA requirements",
			"reporting_requirements": "Data breach notifications within 72 hours, annual reports to supervisory authorities",
			"audit_requirements": "Regular data protection audits, DPIA documentation"
		},
		"SOX Compliance": {
			"framework_name": "SOX Compliance Framework",
			"framework_type": "Financial Regulation",
			"description": "Sarbanes-Oxley Act compliance framework",
			"version": "1.0",
			"effective_date": getdate(),
			"key_requirements": "Internal controls, financial reporting accuracy, CEO/CFO certifications",
			"reporting_requirements": "Quarterly and annual financial reports, internal control assessments",
			"audit_requirements": "External auditor attestation, internal control testing"
		}
	}

	return templates.get(template_name, {})


@frappe.whitelist()
def bulk_update_compliance_status(framework_names, status):
	"""Bulk update compliance status for multiple frameworks"""
	try:
		updated = []

		for framework_name in framework_names:
			framework = frappe.get_doc("Regulatory Framework Manager", framework_name)
			framework.implementation_status = status
			framework.save()
			updated.append(framework_name)

		return {
			"success": True,
			"updated": updated,
			"count": len(updated)
		}

	except Exception as e:
		frappe.log_error(f"Bulk compliance status update error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def generate_compliance_report(framework_name, report_type="summary"):
	"""Generate compliance report"""
	try:
		framework = frappe.get_doc("Regulatory Framework Manager", framework_name)

		if report_type == "summary":
			return framework.generate_gap_analysis_report()
		elif report_type == "detailed":
			return framework.export_framework_data()
		elif report_type == "trends":
			return framework.get_compliance_trends()

		return {"error": "Invalid report type"}

	except Exception as e:
		frappe.log_error(f"Compliance report generation error: {str(e)}")
		return {"error": str(e)}