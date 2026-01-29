# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime
import json

class DashboardAlert(Document):
	def validate(self):
		"""Validate alert configuration"""
		self.validate_alert_type()
		self.validate_conditions()
		self.validate_notification_settings()

	def validate_alert_type(self):
		"""Validate alert type and required fields"""
		valid_types = ["Threshold", "Trend", "Anomaly", "Schedule", "Custom"]

		if self.alert_type not in valid_types:
			frappe.throw(_("Invalid alert type. Valid types: {0}").format(", ".join(valid_types)))

		# Validate required fields based on type
		if self.alert_type == "Threshold":
			if not self.threshold_value or not self.threshold_operator:
				frappe.throw(_("Threshold value and operator are required for threshold alerts"))

		if self.alert_type == "Trend":
			if not self.trend_period or not self.trend_direction:
				frappe.throw(_("Trend period and direction are required for trend alerts"))

	def validate_conditions(self):
		"""Validate alert conditions"""
		if self.alert_conditions:
			try:
				conditions = json.loads(self.alert_conditions)
				# Basic validation - could be enhanced
			except json.JSONDecodeError:
				frappe.throw(_("Invalid JSON in alert conditions"))

	def validate_notification_settings(self):
		"""Validate notification settings"""
		if self.notification_methods:
			valid_methods = ["Email", "SMS", "In-App", "Webhook"]
			methods = self.notification_methods.split(",")

			for method in methods:
				method = method.strip()
				if method not in valid_methods:
					frappe.throw(_("Invalid notification method: {0}").format(method))

		if "Email" in (self.notification_methods or "") and not self.email_recipients:
			frappe.throw(_("Email recipients are required when Email notification is selected"))

	def before_save(self):
		"""Handle before save operations"""
		if not self.alert_id:
			# Generate unique alert ID
			import uuid
			self.alert_id = str(uuid.uuid4())[:8].upper()

		# Set default status
		if not self.status:
			self.status = "Active"

@frappe.whitelist()
def get_alert_types():
	"""Get available alert types"""
	return [
		{"value": "Threshold", "label": "Threshold Alert"},
		{"value": "Trend", "label": "Trend Alert"},
		{"value": "Anomaly", "label": "Anomaly Detection"},
		{"value": "Schedule", "label": "Scheduled Alert"},
		{"value": "Custom", "label": "Custom Alert"}
	]

@frappe.whitelist()
def get_threshold_operators():
	"""Get available threshold operators"""
	return [
		{"value": ">", "label": "Greater than"},
		{"value": "<", "label": "Less than"},
		{"value": ">=", "label": "Greater than or equal"},
		{"value": "<=", "label": "Less than or equal"},
		{"value": "==", "label": "Equal to"},
		{"value": "!=", "label": "Not equal to"}
	]

@frappe.whitelist()
def test_alert_condition(alert_name):
	"""Test alert condition"""
	try:
		alert = frappe.get_doc("Dashboard Alert", alert_name)

		# Simulate condition evaluation
		if alert.alert_type == "Threshold":
			# Mock current value
			current_value = 85  # This would be calculated from actual data
			threshold = float(alert.threshold_value)

			if alert.threshold_operator == ">":
				triggered = current_value > threshold
			elif alert.threshold_operator == "<":
				triggered = current_value < threshold
			elif alert.threshold_operator == ">=":
				triggered = current_value >= threshold
			elif alert.threshold_operator == "<=":
				triggered = current_value <= threshold
			elif alert.threshold_operator == "==":
				triggered = current_value == threshold
			else:  # !=
				triggered = current_value != threshold

			return {
				"current_value": current_value,
				"threshold": threshold,
				"operator": alert.threshold_operator,
				"triggered": triggered,
				"message": "Alert would be triggered" if triggered else "Alert would not be triggered"
			}

		return {"message": "Alert type not supported for testing"}

	except Exception as e:
		frappe.throw(_("Alert test failed: {0}").format(str(e)))

@frappe.whitelist()
def trigger_alert(alert_name):
	"""Manually trigger an alert"""
	try:
		alert = frappe.get_doc("Dashboard Alert", alert_name)

		if alert.status != "Active":
			frappe.throw(_("Alert is not active"))

		# Send notifications
		send_alert_notifications(alert)

		# Update alert metrics
		alert.last_triggered = now_datetime()
		alert.trigger_count = (alert.trigger_count or 0) + 1
		alert.save()

		return {"status": "success", "message": "Alert triggered successfully"}

	except Exception as e:
		frappe.throw(_("Failed to trigger alert: {0}").format(str(e)))

def send_alert_notifications(alert):
	"""Send alert notifications"""
	try:
		notification_methods = (alert.notification_methods or "").split(",")

		message = f"Alert: {alert.alert_name}\n{alert.alert_message or 'Alert condition met'}"

		for method in notification_methods:
			method = method.strip()

			if method == "Email":
				send_email_notification(alert, message)
			elif method == "SMS":
				send_sms_notification(alert, message)
			elif method == "In-App":
				send_in_app_notification(alert, message)
			elif method == "Webhook":
				send_webhook_notification(alert, message)

	except Exception as e:
		frappe.log_error(f"Failed to send alert notifications: {str(e)}")

def send_email_notification(alert, message):
	"""Send email notification"""
	try:
		if alert.email_recipients:
			recipients = alert.email_recipients.split(",")

			frappe.sendmail(
				recipients=[r.strip() for r in recipients],
				subject=f"Dashboard Alert: {alert.alert_name}",
				message=message
			)
	except Exception as e:
		frappe.log_error(f"Failed to send email notification: {str(e)}")

def send_sms_notification(alert, message):
	"""Send SMS notification"""
	# This would integrate with SMS service
	frappe.log_error("SMS notification not implemented")

def send_in_app_notification(alert, message):
	"""Send in-app notification"""
	try:
		# Create notification for dashboard users
		dashboard_users = get_dashboard_users(alert.parent)

		for user in dashboard_users:
			if user.get("can_view"):
				frappe.get_doc({
					"doctype": "Notification Log",
					"subject": f"Dashboard Alert: {alert.alert_name}",
					"email_content": message,
					"document_type": "Data Analytics Dashboard",
					"document_name": alert.parent,
					"for_user": user.get("user"),
					"type": "Alert"
				}).insert(ignore_permissions=True)

	except Exception as e:
		frappe.log_error(f"Failed to send in-app notification: {str(e)}")

def send_webhook_notification(alert, message):
	"""Send webhook notification"""
	try:
		if alert.webhook_url:
			import requests

			payload = {
				"alert_id": alert.alert_id,
				"alert_name": alert.alert_name,
				"message": message,
				"timestamp": str(now_datetime()),
				"dashboard_id": alert.parent
			}

			headers = {"Content-Type": "application/json"}
			if alert.webhook_secret:
				headers["X-Webhook-Secret"] = alert.webhook_secret

			response = requests.post(alert.webhook_url, json=payload, headers=headers, timeout=10)

			if response.status_code not in [200, 201, 202]:
				frappe.log_error(f"Webhook notification failed: {response.status_code} - {response.text}")

	except Exception as e:
		frappe.log_error(f"Failed to send webhook notification: {str(e)}")

def get_dashboard_users(dashboard_id):
	"""Get users with access to dashboard"""
	from mkaguzi.mkaguzi.doctype.dashboard_user_permission.dashboard_user_permission import get_dashboard_users
	return get_dashboard_users(dashboard_id)

@frappe.whitelist()
def get_alert_history(alert_name, limit=50):
	"""Get alert trigger history"""
	try:
		alert = frappe.get_doc("Dashboard Alert", alert_name)

		history = frappe.get_all("Dashboard Alert",
			filters={"name": alert_name},
			fields=["last_triggered", "trigger_count", "status"]
		)

		# This would typically query a separate log table
		# For now, return basic info
		return {
			"alert_name": alert.alert_name,
			"status": alert.status,
			"last_triggered": alert.last_triggered,
			"trigger_count": alert.trigger_count or 0,
			"history": []  # Would contain detailed trigger history
		}

	except Exception as e:
		frappe.throw(_("Failed to get alert history: {0}").format(str(e)))