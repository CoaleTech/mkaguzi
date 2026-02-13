# -*- coding: utf-8 -*-
# Copyright (c) 2024, Coale Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now, get_datetime, flt, cint
import json
from datetime import datetime, timedelta


class AuditFindingController:
	"""Controller for Audit Finding doctype"""

	def __init__(self):
		self.doctype = "Audit Finding"

	def validate(self, doc):
		"""Validate audit finding"""
		try:
			# Validate required fields
			if not doc.finding_title:
				frappe.throw(_("Finding title is required"))

			if not doc.description:
				frappe.throw(_("Description is required"))

			# Set default values
			if not doc.severity:
				doc.severity = 'Medium'

			if not doc.status:
				doc.status = 'Open'

			if not doc.reported_date:
				doc.reported_date = now()

			if not doc.reported_by:
				doc.reported_by = frappe.session.user

			# Calculate priority based on severity and impact
			self.calculate_priority(doc)

			# Set target completion date if not set
			if not doc.target_completion_date:
				self.set_target_completion_date(doc)

		except Exception as e:
			frappe.log_error(f"Audit Finding Validation Error: {str(e)}")
			frappe.throw(str(e))

	def calculate_priority(self, doc):
		"""Calculate finding priority based on severity and impact"""
		try:
			severity_score = {'High': 3, 'Medium': 2, 'Low': 1}.get(doc.severity, 2)
			impact_score = {'High': 3, 'Medium': 2, 'Low': 1}.get(doc.impact, 2)

			total_score = severity_score + impact_score

			if total_score >= 5:
				doc.priority = 'Critical'
			elif total_score >= 4:
				doc.priority = 'High'
			elif total_score >= 3:
				doc.priority = 'Medium'
			else:
				doc.priority = 'Low'

		except Exception:
			doc.priority = 'Medium'

	def set_target_completion_date(self, doc):
		"""Set target completion date based on priority"""
		try:
			days_to_complete = {
				'Critical': 7,
				'High': 14,
				'Medium': 30,
				'Low': 60
			}.get(doc.priority, 30)

			doc.target_completion_date = datetime.now() + timedelta(days=days_to_complete)

		except Exception:
			doc.target_completion_date = datetime.now() + timedelta(days=30)

	def on_submit(self, doc):
		"""Actions when finding is submitted"""
		try:
			# Create audit trail entry
			self.create_audit_trail(doc)

			# Send notifications
			self.send_notifications(doc)

			# Update dashboards
			self.update_dashboards(doc)

			# Escalate if critical
			if doc.priority == 'Critical':
				self.escalate_finding(doc)

		except Exception as e:
			frappe.log_error(f"Audit Finding Submit Error: {str(e)}")

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
				'module': 'Findings',
				'changes_summary': f"Audit finding created: {doc.finding_title}",
				'risk_level': doc.severity,
				'requires_review': 1
			})

			trail.insert(ignore_permissions=True)
			frappe.db.commit()

		except Exception as e:
			frappe.log_error(f"Audit Trail Creation Error: {str(e)}")

	def send_notifications(self, doc):
		"""Send notifications for the finding"""
		try:
			recipients = self.get_finding_recipients(doc)

			if recipients:
				subject = f"Audit Finding: {doc.finding_title}"
				message = f"""
				New Audit Finding

				Title: {doc.finding_title}
				Severity: {doc.severity}
				Priority: {doc.priority}
				Status: {doc.status}

				Description: {doc.description}

				Responsible Party: {doc.responsible_party or 'Not assigned'}
				Target Completion: {doc.target_completion_date or 'Not set'}

				Please review and take appropriate action.

				Finding: {doc.name}
				"""

				frappe.sendmail(
					recipients=recipients,
					subject=subject,
					message=message
				)

		except Exception as e:
			frappe.log_error(f"Finding Notification Error: {str(e)}")

	def get_finding_recipients(self, doc):
		"""Get notification recipients for finding"""
		try:
			recipients = []

			# Add responsible party
			if doc.responsible_party:
				user_email = frappe.db.get_value('User', doc.responsible_party, 'email')
				if user_email:
					recipients.append(user_email)

			# Add audit team members
			audit_users = frappe.get_all('User',
				filters={'role_profile_name': ['like', '%Audit%']},
				pluck='email')
			recipients.extend(audit_users)

			# Add default recipients
			default_recipients = frappe.db.get_single_value('Audit Settings', 'finding_notification_recipients')
			if default_recipients:
				recipients.extend(default_recipients.split(','))

			return list(set(recipients))  # Remove duplicates

		except Exception:
			return []

	def update_dashboards(self, doc):
		"""Update dashboard data"""
		try:
			# Update findings dashboard
			self.update_findings_dashboard(doc)

			# Update risk dashboard
			self.update_risk_dashboard(doc)

		except Exception as e:
			frappe.log_error(f"Dashboard Update Error: {str(e)}")

	def update_findings_dashboard(self, doc):
		"""Update findings dashboard"""
		# Implementation for updating findings summary cache
		pass

	def update_risk_dashboard(self, doc):
		"""Update risk dashboard"""
		# Implementation for updating risk metrics
		pass

	def escalate_finding(self, doc):
		"""Escalate critical finding"""
		try:
			# Create escalation record
			escalation = frappe.get_doc({
				'doctype': 'Audit Escalation',
				'finding': doc.name,
				'escalation_reason': 'Critical priority finding',
				'escalated_by': frappe.session.user,
				'escalation_date': now(),
				'status': 'Active'
			})

			escalation.insert(ignore_permissions=True)
			frappe.db.commit()

		except Exception as e:
			frappe.log_error(f"Finding Escalation Error: {str(e)}")

	def on_update(self, doc):
		"""Actions when finding is updated"""
		try:
			# Check for overdue findings
			if doc.status in ['Open', 'In Progress'] and doc.target_completion_date:
				if datetime.now().date() > doc.target_completion_date:
					self.handle_overdue_finding(doc)

			# Update audit trail
			self.update_audit_trail(doc)

		except Exception as e:
			frappe.log_error(f"Finding Update Error: {str(e)}")

	def handle_overdue_finding(self, doc):
		"""Handle overdue finding"""
		try:
			# Send overdue notification
			recipients = self.get_finding_recipients(doc)

			if recipients:
				subject = f"OVERDUE: Audit Finding {doc.finding_title}"
				message = f"""
				OVERDUE AUDIT FINDING

				Finding: {doc.finding_title}
				Target Completion: {doc.target_completion_date}
				Days Overdue: {(datetime.now().date() - doc.target_completion_date).days}

				Please take immediate action to resolve this finding.

				Finding: {doc.name}
				"""

				frappe.sendmail(
					recipients=recipients,
					subject=subject,
					message=message
				)

		except Exception as e:
			frappe.log_error(f"Overdue Finding Handler Error: {str(e)}")

	def update_audit_trail(self, doc):
		"""Update audit trail for finding changes"""
		try:
			trail = frappe.get_doc({
				'doctype': 'Audit Trail Entry',
				'document_type': self.doctype,
				'document_name': doc.name,
				'operation': 'Update',
				'user': frappe.session.user,
				'timestamp': now(),
				'module': 'Findings',
				'changes_summary': f"Finding updated: {doc.finding_title} - Status: {doc.status}",
				'risk_level': doc.severity,
				'requires_review': 0
			})

			trail.insert(ignore_permissions=True)
			frappe.db.commit()

		except Exception as e:
			frappe.log_error(f"Audit Trail Update Error: {str(e)}")


class AuditExecutionController:
	"""Controller for Audit Execution doctype"""

	def __init__(self):
		self.doctype = "Audit Execution"

	def validate(self, doc):
		"""Validate audit execution"""
		try:
			# Validate required fields
			if not doc.audit_plan:
				frappe.throw(_("Audit plan is required"))

			# Set default values
			if not doc.status:
				doc.status = 'Draft'

			if not doc.executed_by:
				doc.executed_by = frappe.session.user

			# Validate plan exists and is approved
			if not frappe.db.exists('Audit Plan', doc.audit_plan):
				frappe.throw(_("Invalid audit plan"))

			plan_status = frappe.db.get_value('Audit Plan', doc.audit_plan, 'status')
			if plan_status != 'Approved':
				frappe.throw(_("Audit plan must be approved before execution"))

		except Exception as e:
			frappe.log_error(f"Audit Execution Validation Error: {str(e)}")
			frappe.throw(str(e))

	def on_submit(self, doc):
		"""Actions when execution is submitted"""
		try:
			# Update audit plan status
			self.update_audit_plan_status(doc)

			# Create audit trail entry
			self.create_audit_trail(doc)

			# Initialize test executions
			self.initialize_planned_tests(doc)

		except Exception as e:
			frappe.log_error(f"Audit Execution Submit Error: {str(e)}")

	def update_audit_plan_status(self, doc):
		"""Update audit plan status to In Execution"""
		try:
			plan = frappe.get_doc('Audit Plan', doc.audit_plan)
			plan.status = 'In Execution'
			plan.save(ignore_permissions=True)
			frappe.db.commit()

		except Exception as e:
			frappe.log_error(f"Plan Status Update Error: {str(e)}")

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
				'module': 'Execution',
				'changes_summary': f"Audit execution started for plan {doc.audit_plan}",
				'risk_level': 'Medium',
				'requires_review': 0
			})

			trail.insert(ignore_permissions=True)
			frappe.db.commit()

		except Exception as e:
			frappe.log_error(f"Audit Trail Creation Error: {str(e)}")

	def initialize_planned_tests(self, doc):
		"""Initialize planned tests from audit plan"""
		try:
			plan = frappe.get_doc('Audit Plan', doc.audit_plan)

			# Copy planned tests to execution
			for test in plan.planned_tests:
				doc.append('executed_tests', {
					'test_name': test.test_name,
					'test_category': test.test_category,
					'description': test.description,
					'planned_hours': test.estimated_hours,
					'status': 'Not Started'
				})

			# Copy team members
			for member in plan.team_members:
				doc.append('execution_team', {
					'user': member.user,
					'role': member.role,
					'responsibilities': member.responsibilities
				})

			doc.save(ignore_permissions=True)

		except Exception as e:
			frappe.log_error(f"Planned Tests Initialization Error: {str(e)}")

	def update_test_status(self, test_id, status, notes=None, actual_hours=None):
		"""Update test status in execution"""
		try:
			# Find the test in executed_tests
			for test in self.executed_tests:
				if test.name == test_id:
					test.status = status
					if notes:
						test.notes = notes
					if actual_hours:
						test.actual_hours = actual_hours

					if status == 'Completed':
						test.completion_date = now()

					self.save(ignore_permissions=True)

					# Check if all tests completed
					self.check_completion_status()
					break

		except Exception as e:
			frappe.log_error(f"Test Status Update Error: {str(e)}")

	def check_completion_status(self):
		"""Check if all tests are completed"""
		try:
			all_completed = all(test.status == 'Completed' for test in self.executed_tests)

			if all_completed and self.status != 'Completed':
				self.status = 'Completed'
				self.execution_end_date = now()
				self.save(ignore_permissions=True)

				# Update plan status
				plan = frappe.get_doc('Audit Plan', self.audit_plan)
				plan.status = 'Completed'
				plan.save(ignore_permissions=True)

		except Exception as e:
			frappe.log_error(f"Completion Check Error: {str(e)}")


class AuditPlanController:
	"""Controller for Audit Plan doctype"""

	def __init__(self):
		self.doctype = "Audit Plan"

	def validate(self, doc):
		"""Validate audit plan"""
		try:
			# Validate required fields
			if not doc.plan_name:
				frappe.throw(_("Plan name is required"))

			if not doc.start_date or not doc.end_date:
				frappe.throw(_("Start and end dates are required"))

			# Validate date range
			if doc.start_date >= doc.end_date:
				frappe.throw(_("End date must be after start date"))

			# Set default values
			if not doc.status:
				doc.status = 'Draft'

			if not doc.audit_type:
				doc.audit_type = 'General'

			# Validate child tables
			self.validate_audit_areas(doc)
			self.validate_team_members(doc)
			self.validate_planned_tests(doc)

		except Exception as e:
			frappe.log_error(f"Audit Plan Validation Error: {str(e)}")
			frappe.throw(str(e))

	def validate_audit_areas(self, doc):
		"""Validate audit areas"""
		if not doc.audit_areas:
			frappe.throw(_("At least one audit area is required"))

		for area in doc.audit_areas:
			if not area.area_name:
				frappe.throw(_("Area name is required for all audit areas"))

	def validate_team_members(self, doc):
		"""Validate team members"""
		for member in doc.team_members:
			if not member.user:
				frappe.throw(_("User is required for all team members"))

			if not frappe.db.exists('User', member.user):
				frappe.throw(_("Invalid user: {0}").format(member.user))

	def validate_planned_tests(self, doc):
		"""Validate planned tests"""
		for test in doc.planned_tests:
			if not test.test_name:
				frappe.throw(_("Test name is required for all planned tests"))

	def on_submit(self, doc):
		"""Actions when plan is submitted"""
		try:
			# Create audit trail entry
			self.create_audit_trail(doc)

			# Send approval notifications
			if doc.status == 'Pending Approval':
				self.send_approval_notifications(doc)

			# Update resource allocation
			self.update_resource_allocation(doc)

		except Exception as e:
			frappe.log_error(f"Audit Plan Submit Error: {str(e)}")

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
				'module': 'Planning',
				'changes_summary': f"Audit plan created: {doc.plan_name}",
				'risk_level': 'Low',
				'requires_review': 0
			})

			trail.insert(ignore_permissions=True)
			frappe.db.commit()

		except Exception as e:
			frappe.log_error(f"Audit Trail Creation Error: {str(e)}")

	def send_approval_notifications(self, doc):
		"""Send approval request notifications"""
		try:
			# Get approvers
			approvers = self.get_plan_approvers()

			if approvers:
				subject = f"Audit Plan Approval Required: {doc.plan_name}"
				message = f"""
				AUDIT PLAN APPROVAL REQUEST

				Plan: {doc.plan_name}
				Type: {doc.audit_type}
				Period: {doc.start_date} to {doc.end_date}

				Description: {doc.description or 'No description provided'}

				Please review and approve the audit plan.

				Plan: {doc.name}
				"""

				frappe.sendmail(
					recipients=approvers,
					subject=subject,
					message=message
				)

		except Exception as e:
			frappe.log_error(f"Approval Notification Error: {str(e)}")

	def get_plan_approvers(self):
		"""Get plan approvers"""
		try:
			# Get users with audit manager role
			approvers = frappe.get_all('User',
				filters={'role_profile_name': ['like', '%Audit Manager%']},
				pluck='email')

			# Add default approvers
			default_approvers = frappe.db.get_single_value('Audit Settings', 'plan_approvers')
			if default_approvers:
				approvers.extend(default_approvers.split(','))

			return list(set(approvers)) if approvers else []

		except Exception:
			return []

	def update_resource_allocation(self, doc):
		"""Update resource allocation for team members"""
		try:
			# Update user availability calendars
			for member in doc.team_members:
				self.allocate_user_time(member.user, doc.start_date, doc.end_date)

		except Exception as e:
			frappe.log_error(f"Resource Allocation Error: {str(e)}")

	def allocate_user_time(self, user, start_date, end_date):
		"""Allocate user time for audit"""
		# Implementation for resource allocation
		pass

	def approve_plan(self, doc):
		"""Approve the audit plan"""
		try:
			doc.status = 'Approved'
			doc.approved_by = frappe.session.user
			doc.approved_date = now()
			doc.save(ignore_permissions=True)

			# Send approval confirmation
			self.send_approval_confirmation(doc)

		except Exception as e:
			frappe.log_error(f"Plan Approval Error: {str(e)}")

	def send_approval_confirmation(self, doc):
		"""Send approval confirmation"""
		try:
			# Notify plan creator and team members
			recipients = [frappe.db.get_value('User', doc.owner, 'email')]
			recipients.extend([frappe.db.get_value('User', member.user, 'email') for member in doc.team_members])

			subject = f"Audit Plan Approved: {doc.plan_name}"
			message = f"""
			AUDIT PLAN APPROVED

			Plan: {doc.plan_name} has been approved.

			You can now proceed with audit execution.

			Plan: {doc.name}
			"""

			frappe.sendmail(
				recipients=list(set(recipients)),
				subject=subject,
				message=message
			)

		except Exception as e:
			frappe.log_error(f"Approval Confirmation Error: {str(e)}")


# Global controller instances
audit_finding_controller = AuditFindingController()
audit_execution_controller = AuditExecutionController()
audit_plan_controller = AuditPlanController()


# API Integration Functions
@frappe.whitelist()
def get_findings_summary(filters=None):
	"""Get findings summary for dashboard"""
	try:
		filter_conditions = {}
		if filters:
			data = json.loads(filters) if isinstance(filters, str) else filters
			for key, value in data.items():
				filter_conditions[key] = value

		summary = frappe.db.sql("""
			SELECT
				COUNT(*) as total_findings,
				SUM(CASE WHEN severity = 'High' THEN 1 ELSE 0 END) as high_severity,
				SUM(CASE WHEN severity = 'Medium' THEN 1 ELSE 0 END) as medium_severity,
				SUM(CASE WHEN severity = 'Low' THEN 1 ELSE 0 END) as low_severity,
				SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_findings,
				SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved_findings,
				SUM(CASE WHEN priority = 'Critical' THEN 1 ELSE 0 END) as critical_priority
			FROM `tabAudit Finding`
			WHERE docstatus = 1
		""", as_dict=True)[0]

		# Calculate overdue findings
		overdue = frappe.db.sql("""
			SELECT COUNT(*) as count
			FROM `tabAudit Finding`
			WHERE docstatus = 1
			AND status IN ('Open', 'In Progress')
			AND target_completion_date < CURDATE()
		""", as_dict=True)[0]['count']

		summary['overdue_findings'] = overdue

		return summary

	except Exception as e:
		frappe.log_error(f"Findings Summary Error: {str(e)}")
		return {}


@frappe.whitelist()
def get_execution_progress(execution_id):
	"""Get execution progress"""
	try:
		execution = frappe.get_doc('Audit Execution', execution_id)

		total_tests = len(execution.executed_tests)
		completed_tests = len([t for t in execution.executed_tests if t.status == 'Completed'])
		in_progress_tests = len([t for t in execution.executed_tests if t.status == 'In Progress'])

		progress = (completed_tests / total_tests * 100) if total_tests > 0 else 0

		return {
			'execution_id': execution_id,
			'status': execution.status,
			'progress_percent': round(progress, 1),
			'total_tests': total_tests,
			'completed_tests': completed_tests,
			'in_progress_tests': in_progress_tests,
			'start_date': execution.execution_start_date,
			'end_date': execution.execution_end_date
		}

	except Exception as e:
		frappe.log_error(f"Execution Progress Error: {str(e)}")
		return {}


@frappe.whitelist()
def get_plan_summary():
	"""Get audit plans summary"""
	try:
		summary = frappe.db.sql("""
			SELECT
				COUNT(*) as total_plans,
				SUM(CASE WHEN status = 'Draft' THEN 1 ELSE 0 END) as draft_plans,
				SUM(CASE WHEN status = 'Pending Approval' THEN 1 ELSE 0 END) as pending_approval,
				SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END) as approved_plans,
				SUM(CASE WHEN status = 'In Execution' THEN 1 ELSE 0 END) as in_execution,
				SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_plans
			FROM `tabAudit Plan`
			WHERE docstatus = 1
		""", as_dict=True)[0]

		return summary

	except Exception as e:
		frappe.log_error(f"Plan Summary Error: {str(e)}")
		return {}