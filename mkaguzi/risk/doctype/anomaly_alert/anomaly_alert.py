# -*- coding: utf-8 -*-
# Copyright (c) 2024, Coale Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, get_datetime, add_days
import json


class AnomalyAlert(Document):
	def validate(self):
		"""Validate the anomaly alert"""
		self.validate_alert_details()
		self.set_default_values()
		self.update_confidence_score()

	def validate_alert_details(self):
		"""Validate alert details"""
		if not self.alert_description:
			frappe.throw(_("Alert Description is required"))

		if self.severity not in ["Low", "Medium", "High", "Critical"]:
			frappe.throw(_("Invalid severity level"))

	def set_default_values(self):
		"""Set default values"""
		if not self.detected_date:
			self.detected_date = now()

		if not self.alert_id:
			self.alert_id = f"ALERT-{frappe.generate_hash(length=8).upper()}"

		if not self.confidence_score:
			self.confidence_score = self.calculate_default_confidence()

	def update_confidence_score(self):
		"""Update confidence score based on detection method"""
		if self.detection_method == "Machine Learning":
			if not self.confidence_score:
				self.confidence_score = 85.0
		elif self.detection_method == "Statistical":
			if not self.confidence_score:
				self.confidence_score = 75.0
		elif self.detection_method == "Rule-based":
			if not self.confidence_score:
				self.confidence_score = 95.0
		elif self.detection_method == "Pattern Recognition":
			if not self.confidence_score:
				self.confidence_score = 80.0

	def calculate_default_confidence(self):
		"""Calculate default confidence score"""
		severity_scores = {
			"Low": 60.0,
			"Medium": 75.0,
			"High": 90.0,
			"Critical": 95.0
		}
		return severity_scores.get(self.severity, 70.0)

	def on_update(self):
		"""Handle updates to anomaly alerts"""
		if self.has_value_changed('status'):
			self.handle_status_change()

		if self.status == 'Resolved' and not self.resolution_date:
			self.resolution_date = now()

	def handle_status_change(self):
		"""Handle status changes"""
		if self.status == 'Resolved':
			self.resolution_date = now()
		elif self.status == 'False Positive':
			self.false_positive = 1

	def get_related_audit_trail(self):
		"""Get related audit trail entry"""
		if self.audit_trail_reference:
			try:
				return frappe.get_doc('Audit Trail Entry', self.audit_trail_reference)
			except:
				return None
		return None

	def get_related_findings_list(self):
		"""Get list of related findings"""
		if not self.related_findings:
			return []

		try:
			findings_data = json.loads(self.related_findings)
			return findings_data
		except:
			return []

	def escalate_alert(self, escalation_reason=None):
		"""Escalate the alert to higher authority"""
		try:
			if self.severity in ["High", "Critical"]:
				# Auto-escalate high/critical alerts
				self.escalated_to = self.get_escalation_recipient()
				self.add_comment("Comment", f"Alert escalated: {escalation_reason or 'High severity alert'}")

			self.save()

		except Exception as e:
			frappe.log_error(f"Alert Escalation Error: {str(e)}")

	def get_escalation_recipient(self):
		"""Get escalation recipient based on alert type and severity"""
		# This would implement escalation logic based on roles/permissions
		# For now, return a default
		return frappe.db.get_single_value('Audit Settings', 'chief_auditor') or 'Administrator'

	def create_follow_up_task(self):
		"""Create a follow-up task for investigation"""
		try:
			task = frappe.get_doc({
				'doctype': 'Task',
				'subject': f"Investigate Anomaly Alert: {self.alert_id}",
				'description': self.alert_description,
				'priority': 'High' if self.severity in ['High', 'Critical'] else 'Medium',
				'assigned_to': self.assigned_to,
				'exp_start_date': now(),
				'exp_end_date': get_datetime(add_days(now(), 7))  # 1 week deadline
			})

			task.insert()
			frappe.db.commit()

			return task.name

		except Exception as e:
			frappe.log_error(f"Follow-up Task Creation Error: {str(e)}")
			return None

	def update_from_audit_trail(self, audit_trail_entry):
		"""Update alert details from audit trail entry"""
		try:
			self.source_doctype = audit_trail_entry.source_doctype
			self.source_document = audit_trail_entry.source_document
			self.audit_trail_reference = audit_trail_entry.name

			# Update anomaly details
			anomaly_data = {
				"operation": audit_trail_entry.operation,
				"user": audit_trail_entry.user,
				"timestamp": audit_trail_entry.timestamp,
				"risk_level": audit_trail_entry.risk_level,
				"module": audit_trail_entry.module
			}

			if audit_trail_entry.changes:
				try:
					anomaly_data["changes"] = json.loads(audit_trail_entry.changes)
				except:
					anomaly_data["changes"] = audit_trail_entry.changes

			self.anomaly_details = json.dumps(anomaly_data)

		except Exception as e:
			frappe.log_error(f"Alert Update from Audit Trail Error: {str(e)}")


@frappe.whitelist()
def create_anomaly_alert(alert_data):
	"""Create a new anomaly alert"""
	try:
		if isinstance(alert_data, str):
			alert_data = json.loads(alert_data)

		alert = frappe.get_doc({
			'doctype': 'Anomaly Alert',
			'alert_type': alert_data.get('alert_type'),
			'severity': alert_data.get('severity', 'Medium'),
			'alert_description': alert_data.get('description'),
			'source_doctype': alert_data.get('source_doctype'),
			'source_document': alert_data.get('source_document'),
			'audit_trail_reference': alert_data.get('audit_trail_reference'),
			'detection_method': alert_data.get('detection_method', 'Rule-based'),
			'confidence_score': alert_data.get('confidence_score'),
			'anomaly_details': json.dumps(alert_data.get('anomaly_details', {}))
		})

		alert.insert()
		frappe.db.commit()

		# Auto-assign based on severity
		if alert.severity in ['High', 'Critical']:
			alert.escalate_alert("High severity anomaly detected")

		return {
			'success': True,
			'alert_id': alert.alert_id,
			'name': alert.name
		}

	except Exception as e:
		frappe.log_error(f"Anomaly Alert Creation Error: {str(e)}")
		return {
			'success': False,
			'error': str(e)
		}


@frappe.whitelist()
def get_alerts_summary(filters=None):
	"""Get summary of anomaly alerts"""
	try:
		filter_conditions = {}
		if filters:
			filters_dict = json.loads(filters) if isinstance(filters, str) else filters
			for key, value in filters_dict.items():
				filter_conditions[key] = value

		# Get summary statistics
		summary = frappe.db.sql("""
			SELECT
				COUNT(*) as total_alerts,
				COUNT(CASE WHEN status = 'Open' THEN 1 END) as open_alerts,
				COUNT(CASE WHEN status = 'Investigating' THEN 1 END) as investigating_alerts,
				COUNT(CASE WHEN status = 'Resolved' THEN 1 END) as resolved_alerts,
				COUNT(CASE WHEN severity = 'Critical' THEN 1 END) as critical_alerts,
				COUNT(CASE WHEN severity = 'High' THEN 1 END) as high_alerts,
				COUNT(CASE WHEN false_positive = 1 THEN 1 END) as false_positives,
				AVG(confidence_score) as avg_confidence
			FROM `tabAnomaly Alert`
			WHERE %(filter_conditions)s
		""", {"filter_conditions": filter_conditions}, as_dict=True)[0]

		# Get alerts by type
		by_type = frappe.db.sql("""
			SELECT alert_type, COUNT(*) as count
			FROM `tabAnomaly Alert`
			WHERE %(filter_conditions)s
			GROUP BY alert_type
			ORDER BY count DESC
		""", {"filter_conditions": filter_conditions}, as_dict=True)

		# Get recent alerts
		recent_alerts = frappe.get_all('Anomaly Alert',
			filters=filter_conditions,
			fields=['alert_id', 'alert_type', 'severity', 'status', 'detected_date', 'alert_description'],
			order_by='detected_date desc',
			limit=10)

		return {
			'summary': summary,
			'by_type': by_type,
			'recent_alerts': recent_alerts
		}

	except Exception as e:
		frappe.log_error(f"Alerts Summary Error: {str(e)}")
		return {
			'error': str(e)
		}


@frappe.whitelist()
def bulk_resolve_alerts(alert_ids, resolution_notes=None):
	"""Bulk resolve multiple alerts"""
	try:
		if isinstance(alert_ids, str):
			alert_ids = json.loads(alert_ids)

		resolved_count = 0
		for alert_id in alert_ids:
			alert = frappe.get_doc('Anomaly Alert', alert_id)
			alert.status = 'Resolved'
			alert.resolution_date = now()
			if resolution_notes:
				alert.preventive_actions = resolution_notes
			alert.save()
			resolved_count += 1

		frappe.db.commit()

		return {
			'success': True,
			'resolved_count': resolved_count
		}

	except Exception as e:
		frappe.log_error(f"Bulk Resolution Error: {str(e)}")
		frappe.throw(_("Failed to resolve alerts"))


@frappe.whitelist()
def get_alert_effectiveness():
	"""Get alert effectiveness metrics"""
	try:
		# Calculate true positive rate, false positive rate, etc.
		total_alerts = frappe.db.count('Anomaly Alert')

		if total_alerts == 0:
			return {
				'true_positive_rate': 0,
				'false_positive_rate': 0,
				'resolution_rate': 0,
				'avg_resolution_time': 0
			}

		false_positives = frappe.db.count('Anomaly Alert', {'false_positive': 1})
		resolved_alerts = frappe.db.count('Anomaly Alert', {'status': 'Resolved'})

		false_positive_rate = (false_positives / total_alerts) * 100
		resolution_rate = (resolved_alerts / total_alerts) * 100

		# Calculate average resolution time
		resolution_times = frappe.db.sql("""
			SELECT AVG(TIMESTAMPDIFF(HOUR, detected_date, resolution_date)) as avg_hours
			FROM `tabAnomaly Alert`
			WHERE status = 'Resolved' AND resolution_date IS NOT NULL
		""", as_dict=True)

		avg_resolution_time = resolution_times[0]['avg_hours'] if resolution_times else 0

		return {
			'total_alerts': total_alerts,
			'false_positive_rate': round(false_positive_rate, 2),
			'resolution_rate': round(resolution_rate, 2),
			'avg_resolution_time_hours': round(avg_resolution_time, 2) if avg_resolution_time else 0
		}

	except Exception as e:
		frappe.log_error(f"Alert Effectiveness Error: {str(e)}")
		return {
			'error': str(e)
		}