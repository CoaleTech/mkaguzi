# -*- coding: utf-8 -*-
# Copyright (c) 2024, Coale Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now, get_datetime, flt, cint
import json
from datetime import datetime, timedelta
from mkaguzi.api import audit_api
from mkaguzi.utils.config import MkaguziConfig
from mkaguzi.utils.audit_trail_helper import AuditTrailHelper


class AuditGLController:
	"""Controller for Audit GL Entry doctype"""

	def __init__(self):
		self.doctype = "Audit GL Entry"

	def validate(self, doc):
		"""Validate audit GL entry"""
		try:
			# Validate required fields
			if not doc.account_no:
				frappe.throw(_("Account number is required"))

			if not doc.posting_date:
				frappe.throw(_("Posting date is required"))

			if not doc.amount:
				doc.amount = 0

			# Validate amount is not zero for non-system entries
			if doc.entry_type not in ['Opening', 'Closing'] and doc.amount == 0:
				frappe.throw(_("Amount cannot be zero for transaction entries"))

			# Set risk level based on amount
			self.set_risk_level(doc)

			# Check for duplicate entries
			self.check_duplicates(doc)

		except Exception as e:
			frappe.log_error(f"Audit GL Validation Error: {str(e)}")
			frappe.throw(str(e))

	def set_risk_level(self, doc):
		"""Set risk level based on transaction characteristics"""
		try:
			risk_score = 0

			# Amount-based risk
			amount = abs(flt(doc.amount))
			if amount > 1000000:
				risk_score += 3
			elif amount > 100000:
				risk_score += 2
			elif amount > 10000:
				risk_score += 1

			# Round number risk
			if amount > 0 and amount % 1000 == 0:
				risk_score += 1

			# Weekend posting risk
			if doc.posting_date:
				posting_datetime = get_datetime(doc.posting_date)
				if posting_datetime.weekday() >= 5:  # Saturday = 5, Sunday = 6
					risk_score += 1

			# Set risk level
			if risk_score >= 4:
				doc.risk_level = "High"
			elif risk_score >= 2:
				doc.risk_level = "Medium"
			else:
				doc.risk_level = "Low"

		except Exception as e:
			doc.risk_level = "Low"  # Default to low risk

	def check_duplicates(self, doc):
		"""Check for potential duplicate entries"""
		try:
			if doc.is_new():
				# Check for similar entries within 24 hours
				duplicates = frappe.db.sql("""
					SELECT name, posting_date, amount
					FROM `tabAudit GL Entry`
					WHERE account_no = %s
					AND ABS(amount - %s) < 0.01
					AND posting_date BETWEEN %s AND %s
					AND name != %s
				""", (
					doc.account_no,
					doc.amount,
					doc.posting_date - timedelta(hours=24),
					doc.posting_date + timedelta(hours=24),
					doc.name
				), as_dict=True)

				if duplicates:
					doc.duplicate_flag = 1
					doc.duplicate_reference = duplicates[0].name

		except Exception as e:
			frappe.log_error(f"Duplicate Check Error: {str(e)}")

	def on_submit(self, doc):
		"""Actions when audit GL entry is submitted"""
		try:
			# Update audit trail
			self.update_audit_trail(doc)

			# Check integrity rules
			self.check_integrity_rules(doc)

			# Update dashboards
			self.update_dashboards(doc)

		except Exception as e:
			frappe.log_error(f"Audit GL Submit Error: {str(e)}")

	def update_audit_trail(self, doc):
		"""Update audit trail with GL entry"""
		risk_level = AuditTrailHelper.assess_document_risk(doc, 'Create')
		changes_summary = f"GL Entry created: {doc.account_no} - {doc.amount}"
		requires_review = risk_level == 'High'

		AuditTrailHelper.create_audit_trail_entry(
			doc=doc,
			operation='Create',
			module='Financial',
			changes_summary=changes_summary,
			risk_level=risk_level,
			requires_review=requires_review
		)

	def check_integrity_rules(self, doc):
		"""Check integrity rules for GL entry"""
		try:
			# Get applicable rules
			rules = frappe.get_all('Audit Rule',
				filters={
					'is_active': 1,
					'doctype_name': self.doctype
				},
				fields=['name', 'rule_name', 'condition', 'action', 'severity'])

			for rule in rules:
				if self.evaluate_rule(doc, rule):
					self.execute_rule_action(doc, rule)

		except Exception as e:
			frappe.log_error(f"Integrity Rule Check Error: {str(e)}")

	def evaluate_rule(self, doc, rule):
		"""Evaluate if a rule condition is met"""
		try:
			condition = rule.condition

			# Simple condition evaluation (can be enhanced with a proper expression evaluator)
			if 'amount > 100000' in condition and doc.amount > 100000:
				return True
			if 'risk_level == "High"' in condition and doc.risk_level == 'High':
				return True
			if 'duplicate_flag == 1' in condition and doc.duplicate_flag:
				return True

			return False

		except Exception:
			return False

	def execute_rule_action(self, doc, rule):
		"""Execute rule action"""
		try:
			action = rule.action

			if 'create_finding' in action:
				self.create_rule_finding(doc, rule)
			elif 'flag_for_review' in action:
				doc.requires_review = 1
			elif 'escalate' in action:
				doc.escalation_required = 1

		except Exception as e:
			frappe.log_error(f"Rule Action Execution Error: {str(e)}")

	def create_rule_finding(self, doc, rule):
		"""Create a finding based on rule violation"""
		try:
			finding = frappe.get_doc({
				'doctype': 'Audit Finding',
				'finding_title': f"Rule Violation: {rule.rule_name}",
				'description': f"GL Entry {doc.name} violated rule '{rule.rule_name}'",
				'finding_type': 'Rule Violation',
				'severity': rule.severity,
				'impact': 'Medium',
				'recommendation': f"Review and correct the GL entry according to rule '{rule.rule_name}'",
				'status': 'Open',
				'reported_date': now(),
				'reported_by': frappe.session.user,
				'audit_trail_reference': f"{self.doctype}:{doc.name}"
			})

			finding.insert(ignore_permissions=True)
			frappe.db.commit()

		except Exception as e:
			frappe.log_error(f"Rule Finding Creation Error: {str(e)}")

	def update_dashboards(self, doc):
		"""Update dashboard data"""
		try:
			# Update GL summary dashboard
			self.update_gl_summary(doc)

			# Update risk dashboard
			self.update_risk_dashboard(doc)

		except Exception as e:
			frappe.log_error(f"Dashboard Update Error: {str(e)}")

	def update_gl_summary(self, doc):
		"""Update GL summary dashboard"""
		# Implementation for updating GL summary cache
		pass

	def update_risk_dashboard(self, doc):
		"""Update risk dashboard"""
		# Implementation for updating risk metrics
		pass


class AuditDoctypeCatalogController:
	"""Controller for Audit Doctype Catalog doctype"""

	def __init__(self):
		self.doctype = "Audit Doctype Catalog"

	def validate(self, doc):
		"""Validate doctype catalog entry"""
		try:
			# Validate required fields
			if not doc.doctype_name:
				frappe.throw(_("Doctype name is required"))

			# Check if doctype exists in system
			if not frappe.db.exists('DocType', doc.doctype_name):
				frappe.throw(_("Doctype '{0}' does not exist in the system").format(doc.doctype_name))

			# Set default values
			if not doc.audit_frequency:
				doc.audit_frequency = 'Monthly'

			if not doc.risk_level:
				doc.risk_level = 'Medium'

			# Validate child tables
			self.validate_triggers(doc)
			self.validate_fields(doc)
			self.validate_rules(doc)

		except Exception as e:
			frappe.log_error(f"Doctype Catalog Validation Error: {str(e)}")
			frappe.throw(str(e))

	def validate_triggers(self, doc):
		"""Validate audit triggers"""
		for trigger in doc.audit_triggers:
			if not trigger.trigger_type:
				frappe.throw(_("Trigger type is required for all audit triggers"))

			if not trigger.trigger_condition:
				frappe.throw(_("Trigger condition is required for all audit triggers"))

	def validate_fields(self, doc):
		"""Validate auditable fields"""
		for field in doc.auditable_fields:
			if not field.field_name:
				frappe.throw(_("Field name is required for all auditable fields"))

			# Check if field exists in doctype
			doctype_fields = frappe.get_meta(doc.doctype_name).get_fieldnames()
			if field.field_name not in doctype_fields:
				frappe.throw(_("Field '{0}' does not exist in doctype '{1}'").format(
					field.field_name, doc.doctype_name))

	def validate_rules(self, doc):
		"""Validate audit rules"""
		for rule in doc.audit_rules:
			if not rule.rule_name:
				frappe.throw(_("Rule name is required for all audit rules"))

			if not rule.condition:
				frappe.throw(_("Condition is required for all audit rules"))

	def on_submit(self, doc):
		"""Actions when doctype catalog is submitted"""
		try:
			# Create audit trail entry
			self.create_audit_trail(doc)

			# Register hooks for the doctype
			self.register_doctype_hooks(doc)

			# Update discovery engine
			self.update_discovery_engine(doc)

		except Exception as e:
			frappe.log_error(f"Doctype Catalog Submit Error: {str(e)}")

	def create_audit_trail(self, doc):
		"""Create audit trail entry"""
		try:
			trail = frappe.get_doc({
				'doctype': 'Audit Trail Entry',
				'document_type': self.doctype,
				'document_name': doc.name,
				'operation': 'Create',
				'user': frappe.session.user,
				'timestamp': now(),
				'module': 'Discovery',
				'changes_summary': f"Doctype catalog created for {doc.doctype_name}",
				'risk_level': doc.risk_level,
				'requires_review': 0
			})

			trail.insert(ignore_permissions=True)
			frappe.db.commit()

		except Exception as e:
			frappe.log_error(f"Audit Trail Creation Error: {str(e)}")

	def register_doctype_hooks(self, doc):
		"""Register hooks for the doctype"""
		try:
			# Create hook configuration
			hook_config = {
				'doctype': doc.doctype_name,
				'triggers': [],
				'fields': [],
				'rules': []
			}

			# Add triggers
			for trigger in doc.audit_triggers:
				if trigger.is_active:
					hook_config['triggers'].append({
						'type': trigger.trigger_type,
						'condition': trigger.trigger_condition,
						'priority': trigger.priority
					})

			# Add fields
			for field in doc.auditable_fields:
				if field.is_sensitive:
					hook_config['fields'].append({
						'name': field.field_name,
						'type': field.field_type,
						'risk_level': field.risk_level
					})

			# Add rules
			for rule in doc.audit_rules:
				if rule.is_active:
					hook_config['rules'].append({
						'name': rule.rule_name,
						'condition': rule.condition,
						'action': rule.action,
						'severity': rule.severity
					})

			# Register with hooks manager
			from mkaguzi.hooks_manager import register_doctype_hooks
			register_doctype_hooks(doc.doctype_name, hook_config)

		except Exception as e:
			frappe.log_error(f"Hook Registration Error: {str(e)}")

	def update_discovery_engine(self, doc):
		"""Update discovery engine with new catalog"""
		try:
			# Update discovery engine cache
			from mkaguzi.discovery_engine import update_catalog_cache
			update_catalog_cache(doc.doctype_name)

		except Exception as e:
			frappe.log_error(f"Discovery Engine Update Error: {str(e)}")


class AuditIntegrityReportController:
	"""Controller for Audit Integrity Report doctype"""

	def __init__(self):
		self.doctype = "Audit Integrity Report"

	def validate(self, doc):
		"""Validate integrity report"""
		try:
			# Validate required fields
			if not doc.report_title:
				doc.report_title = f"Integrity Check - {now()}"

			if not doc.execution_date:
				doc.execution_date = now()

			# Set default values
			if not doc.overall_status:
				doc.overall_status = 'Pending'

		except Exception as e:
			frappe.log_error(f"Integrity Report Validation Error: {str(e)}")
			frappe.throw(str(e))

	def on_submit(self, doc):
		"""Actions when integrity report is submitted"""
		try:
			# Create audit trail entry
			self.create_audit_trail(doc)

			# Send notifications if critical issues found
			if doc.failed_checks > 0:
				self.send_notifications(doc)

			# Update system health status
			self.update_system_health(doc)

		except Exception as e:
			frappe.log_error(f"Integrity Report Submit Error: {str(e)}")

	def create_audit_trail(self, doc):
		"""Create audit trail entry"""
		try:
			status_summary = f"Checks: {doc.total_checks}, Passed: {doc.passed_checks}, Failed: {doc.failed_checks}"

			trail = frappe.get_doc({
				'doctype': 'Audit Trail Entry',
				'document_type': self.doctype,
				'document_name': doc.name,
				'operation': 'Create',
				'user': frappe.session.user,
				'timestamp': now(),
				'module': 'Integrity',
				'changes_summary': f"Integrity report generated: {status_summary}",
				'risk_level': 'High' if doc.failed_checks > 0 else 'Low',
				'requires_review': 1 if doc.failed_checks > 0 else 0
			})

			trail.insert(ignore_permissions=True)
			frappe.db.commit()

		except Exception as e:
			frappe.log_error(f"Audit Trail Creation Error: {str(e)}")

	def send_notifications(self, doc):
		"""Send notifications for failed integrity checks"""
		try:
			# Get recipients (audit administrators)
			recipients = self.get_notification_recipients()

			if recipients:
				subject = f"Critical: Integrity Check Failed - {doc.failed_checks} issues found"
				message = f"""
				Integrity Check Report: {doc.report_title}

				Summary:
				- Total Checks: {doc.total_checks}
				- Passed: {doc.passed_checks}
				- Failed: {doc.failed_checks}
				- Warnings: {doc.warning_checks}

				Please review the integrity report for details.

				Report: {doc.name}
				"""

				frappe.sendmail(
					recipients=recipients,
					subject=subject,
					message=message
				)

		except Exception as e:
			frappe.log_error(f"Notification Send Error: {str(e)}")

	def get_notification_recipients(self):
		"""Get notification recipients"""
		try:
			# Get users with audit administrator role
			recipients = frappe.get_all('User',
				filters={'role_profile_name': ['like', '%Audit%']},
				pluck='email')

			# Add default recipients
			default_recipients = frappe.db.get_single_value('Audit Settings', 'notification_recipients')
			if default_recipients:
				recipients.extend(default_recipients.split(','))

			return list(set(recipients))  # Remove duplicates

		except Exception:
			return []

	def update_system_health(self, doc):
		"""Update system health status"""
		try:
			# Update system health based on integrity results
			health_status = 'Healthy'
			if doc.failed_checks > 0:
				health_status = 'Critical'
			elif doc.warning_checks > 0:
				health_status = 'Warning'

			# Update system health record
			health = frappe.get_doc('System Health Status', 'System Health')
			health.integrity_status = health_status
			health.last_integrity_check = doc.execution_date
			health.save(ignore_permissions=True)

		except Exception as e:
			frappe.log_error(f"System Health Update Error: {str(e)}")


class AuditTestTemplateController:
	"""Controller for Audit Test Template doctype"""

	def __init__(self):
		self.doctype = "Audit Test Template"

	def validate(self, doc):
		"""Validate test template"""
		try:
			# Validate required fields
			if not doc.template_name:
				frappe.throw(_("Template name is required"))

			if not doc.category:
				frappe.throw(_("Category is required"))

			# Validate child tables
			self.validate_procedures(doc)

			# Set default values
			if not doc.estimated_hours:
				doc.estimated_hours = 4

			if not doc.priority:
				doc.priority = 'Medium'

		except Exception as e:
			frappe.log_error(f"Test Template Validation Error: {str(e)}")
			frappe.throw(str(e))

	def validate_procedures(self, doc):
		"""Validate test procedures"""
		for procedure in doc.test_procedures:
			if not procedure.procedure_name:
				frappe.throw(_("Procedure name is required for all test procedures"))

			if not procedure.expected_result:
				frappe.throw(_("Expected result is required for all test procedures"))

	def on_submit(self, doc):
		"""Actions when test template is submitted"""
		try:
			# Create audit trail entry
			self.create_audit_trail(doc)

			# Register with test library
			self.register_with_test_library(doc)

			# Update template cache
			self.update_template_cache(doc)

		except Exception as e:
			frappe.log_error(f"Test Template Submit Error: {str(e)}")

	def create_audit_trail(self, doc):
		"""Create audit trail entry"""
		try:
			trail = frappe.get_doc({
				'doctype': 'Audit Trail Entry',
				'document_type': self.doctype,
				'document_name': doc.name,
				'operation': 'Create',
				'user': frappe.session.user,
				'timestamp': now(),
				'module': 'Templates',
				'changes_summary': f"Test template created: {doc.template_name}",
				'risk_level': 'Low',
				'requires_review': 0
			})

			trail.insert(ignore_permissions=True)
			frappe.db.commit()

		except Exception as e:
			frappe.log_error(f"Audit Trail Creation Error: {str(e)}")

	def register_with_test_library(self, doc):
		"""Register template with test library"""
		try:
			# Create test library entry
			test_lib = frappe.get_doc({
				'doctype': 'Audit Test Library',
				'test_id': f"TPL-{doc.name}",
				'test_name': doc.template_name,
				'test_category': doc.category,
				'description': doc.description,
				'objective': doc.objective,
				'status': 'Active',
				'is_template': 1
			})

			# Add test parameters
			for procedure in doc.test_procedures:
				test_lib.append('test_parameters', {
					'parameter_name': 'procedure',
					'parameter_type': 'Data',
					'default_value': procedure.procedure_name,
					'description': procedure.procedure_description
				})

			test_lib.insert(ignore_permissions=True)
			frappe.db.commit()

		except Exception as e:
			frappe.log_error(f"Test Library Registration Error: {str(e)}")

	def update_template_cache(self, doc):
		"""Update template cache"""
		try:
			# Update templates module cache
			from mkaguzi.audit_templates import update_template_cache
			update_template_cache(doc.category)

		except Exception as e:
			frappe.log_error(f"Template Cache Update Error: {str(e)}")


class ModuleSyncStatusController:
	"""Controller for Module Sync Status doctype"""

	def __init__(self):
		self.doctype = "Module Sync Status"

	def validate(self, doc):
		"""Validate sync status"""
		try:
			# Validate required fields
			if not doc.module_name:
				frappe.throw(_("Module name is required"))

			# Set default values
			if not doc.sync_status:
				doc.sync_status = 'Pending'

			if not doc.last_sync:
				doc.last_sync = now()

		except Exception as e:
			frappe.log_error(f"Sync Status Validation Error: {str(e)}")
			frappe.throw(str(e))

	def on_submit(self, doc):
		"""Actions when sync status is submitted"""
		try:
			# Create audit trail entry
			self.create_audit_trail(doc)

			# Update system dashboard
			self.update_system_dashboard(doc)

			# Send alerts if sync failed
			if doc.sync_status == 'Failed':
				self.send_sync_failure_alert(doc)

		except Exception as e:
			frappe.log_error(f"Sync Status Submit Error: {str(e)}")

	def create_audit_trail(self, doc):
		"""Create audit trail entry"""
		try:
			status_summary = f"Module: {doc.module_name}, Status: {doc.sync_status}, Records: {doc.records_processed}"

			trail = frappe.get_doc({
				'doctype': 'Audit Trail Entry',
				'document_type': self.doctype,
				'document_name': doc.name,
				'operation': 'Update',
				'user': frappe.session.user,
				'timestamp': now(),
				'module': 'Sync',
				'changes_summary': f"Module sync status updated: {status_summary}",
				'risk_level': 'High' if doc.sync_status == 'Failed' else 'Low',
				'requires_review': 1 if doc.sync_status == 'Failed' else 0
			})

			trail.insert(ignore_permissions=True)
			frappe.db.commit()

		except Exception as e:
			frappe.log_error(f"Audit Trail Creation Error: {str(e)}")

	def update_system_dashboard(self, doc):
		"""Update system dashboard with sync status"""
		try:
			# Update dashboard cache
			from mkaguzi.api import audit_api
			audit_api._update_sync_status([{
				'module': doc.module_name,
				'status': doc.sync_status,
				'records_processed': doc.records_processed,
				'timestamp': doc.last_sync
			}])

		except Exception as e:
			frappe.log_error(f"Dashboard Update Error: {str(e)}")

	def send_sync_failure_alert(self, doc):
		"""Send alert for sync failure"""
		try:
			recipients = self.get_sync_alert_recipients()

			if recipients:
				subject = f"Alert: Module Sync Failed - {doc.module_name}"
				message = f"""
				Module Sync Failure Alert

				Module: {doc.module_name}
				Status: {doc.sync_status}
				Error: {doc.error_message or 'Unknown error'}
				Last Sync: {doc.last_sync}

				Please investigate and resolve the sync issue.
				"""

				frappe.sendmail(
					recipients=recipients,
					subject=subject,
					message=message
				)

		except Exception as e:
			frappe.log_error(f"Sync Alert Send Error: {str(e)}")

	def get_sync_alert_recipients(self):
		"""Get sync alert recipients"""
		try:
			return MkaguziConfig.get_sync_alert_recipients()
		except Exception:
			return MkaguziConfig.get_default_notification_recipients()


# Global controller instances
audit_gl_controller = AuditGLController()
audit_catalog_controller = AuditDoctypeCatalogController()
audit_integrity_controller = AuditIntegrityReportController()
audit_template_controller = AuditTestTemplateController()
sync_status_controller = ModuleSyncStatusController()


# API Integration Functions
@frappe.whitelist()
def get_audit_gl_summary(filters=None):
	"""Get audit GL summary for dashboard"""
	try:
		filter_conditions = {}
		if filters:
			data = json.loads(filters) if isinstance(filters, str) else filters
			for key, value in data.items():
				filter_conditions[key] = value

		# Get summary statistics
		summary = frappe.db.sql("""
			SELECT
				COUNT(*) as total_entries,
				SUM(CASE WHEN risk_level = 'High' THEN 1 ELSE 0 END) as high_risk,
				SUM(CASE WHEN risk_level = 'Medium' THEN 1 ELSE 0 END) as medium_risk,
				SUM(CASE WHEN risk_level = 'Low' THEN 1 ELSE 0 END) as low_risk,
				SUM(CASE WHEN duplicate_flag = 1 THEN 1 ELSE 0 END) as duplicates,
				SUM(amount) as total_amount
			FROM `tabAudit GL Entry`
			WHERE docstatus = 1
		""", as_dict=True)[0]

		return summary

	except Exception as e:
		frappe.log_error(f"GL Summary Error: {str(e)}")
		return {}


@frappe.whitelist()
def get_catalog_status():
	"""Get doctype catalog status"""
	try:
		status = frappe.db.sql("""
			SELECT
				COUNT(*) as total_catalogs,
				SUM(CASE WHEN risk_level = 'High' THEN 1 ELSE 0 END) as high_risk_catalogs,
				SUM(CASE WHEN audit_frequency = 'Daily' THEN 1 ELSE 0 END) as daily_audits,
				SUM(CASE WHEN audit_frequency = 'Weekly' THEN 1 ELSE 0 END) as weekly_audits,
				SUM(CASE WHEN audit_frequency = 'Monthly' THEN 1 ELSE 0 END) as monthly_audits
			FROM `tabAudit Doctype Catalog`
			WHERE docstatus = 1
		""", as_dict=True)[0]

		return status

	except Exception as e:
		frappe.log_error(f"Catalog Status Error: {str(e)}")
		return {}


@frappe.whitelist()
def get_integrity_health():
	"""Get system integrity health"""
	try:
		# Get latest integrity report
		latest_report = frappe.get_all('Audit Integrity Report',
			fields=['overall_status', 'passed_checks', 'failed_checks', 'execution_date'],
			order_by='execution_date desc',
			limit=1)

		if latest_report:
			report = latest_report[0]
			health_score = (report.passed_checks / (report.passed_checks + report.failed_checks)) * 100 if (report.passed_checks + report.failed_checks) > 0 else 0

			return {
				'status': report.overall_status,
				'health_score': round(health_score, 1),
				'last_check': report.execution_date,
				'passed_checks': report.passed_checks,
				'failed_checks': report.failed_checks
			}
		else:
			return {
				'status': 'Unknown',
				'health_score': 0,
				'last_check': None,
				'message': 'No integrity checks performed yet'
			}

	except Exception as e:
		frappe.log_error(f"Integrity Health Error: {str(e)}")
		return {}