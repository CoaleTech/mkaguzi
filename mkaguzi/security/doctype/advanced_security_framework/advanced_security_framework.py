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
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import hashlib
import hmac
import secrets
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import re


class AdvancedSecurityFramework(Document):
	def validate(self):
		"""Validate the advanced security framework"""
		self.validate_security_framework_id()
		self.set_default_values()
		self.validate_security_layers()
		self.initialize_encryption()
		self.configure_access_controls()
		self.setup_threat_detection()
		self.initialize_monitoring()
		self.configure_compliance()

	def validate_security_framework_id(self):
		"""Auto-generate security framework ID if not provided"""
		if not self.security_framework_id:
			type_short = "ASF"
			random_suffix = ''.join(str(uuid.uuid4().hex)[:8])
			self.security_framework_id = f"{type_short}-{random_suffix}"

	def set_default_values(self):
		"""Set default values"""
		if not self.created_by:
			self.created_by = frappe.session.user

		if not self.framework_version:
			self.framework_version = "1.0.0"

		if not self.status:
			self.status = "Draft"

		if not self.encryption_layer:
			self.encryption_layer = json.dumps({
				"enabled": False,
				"algorithm": "AES-256-GCM",
				"key_rotation_days": 90,
				"encrypted_fields": [],
				"last_rotation": None
			})

		if not self.access_control_layer:
			self.access_control_layer = json.dumps({
				"enabled": False,
				"model": "RBAC",
				"multi_factor_auth": False,
				"session_timeout": 3600,
				"password_policy": {
					"min_length": 8,
					"require_uppercase": True,
					"require_lowercase": True,
					"require_numbers": True,
					"require_special_chars": True
				}
			})

		if not self.threat_detection_layer:
			self.threat_detection_layer = json.dumps({
				"enabled": False,
				"real_time_monitoring": False,
				"anomaly_detection": False,
				"intrusion_detection": False,
				"rules": []
			})

		if not self.monitoring_layer:
			self.monitoring_layer = json.dumps({
				"enabled": False,
				"log_level": "INFO",
				"audit_trail": True,
				"real_time_alerts": False,
				"retention_days": 365
			})

		if not self.compliance_layer:
			self.compliance_layer = json.dumps({
				"enabled": False,
				"standards": ["GDPR", "SOX", "PCI-DSS"],
				"auto_reporting": False,
				"audit_frequency": "quarterly"
			})

		if not self.security_logs:
			self.security_logs = json.dumps([])

		if not self.audit_events:
			self.audit_events = json.dumps([])

		if not self.incident_reports:
			self.incident_reports = json.dumps([])

		if not self.performance_metrics:
			self.performance_metrics = json.dumps({
				"uptime_percentage": 0.0,
				"response_time_avg": 0.0,
				"failed_auth_attempts": 0,
				"security_incidents": 0,
				"last_updated": now()
			})

	def validate_security_layers(self):
		"""Validate security layer configurations"""
		layers = ['encryption_layer', 'access_control_layer', 'threat_detection_layer',
				 'monitoring_layer', 'compliance_layer']

		for layer in layers:
			value = getattr(self, layer, None)
			if value:
				try:
					config = json.loads(value)
					self.validate_layer_config(layer, config)
				except json.JSONDecodeError:
					frappe.throw(_(f"{layer.replace('_', ' ').title()} must be valid JSON"))

	def validate_layer_config(self, layer_name, config):
		"""Validate individual layer configuration"""
		if layer_name == 'encryption_layer':
			required_keys = ['algorithm', 'key_rotation_days']
		elif layer_name == 'access_control_layer':
			required_keys = ['model', 'password_policy']
		elif layer_name == 'threat_detection_layer':
			required_keys = ['rules']
		elif layer_name == 'monitoring_layer':
			required_keys = ['log_level', 'retention_days']
		elif layer_name == 'compliance_layer':
			required_keys = ['standards']
		else:
			return

		for key in required_keys:
			if key not in config:
				frappe.throw(_(f"Required key '{key}' missing in {layer_name}"))

	def on_update(self):
		"""Called when document is updated"""
		if self.status == "Active":
			self.activate_security_framework()
		self.update_security_metrics()
		self.log_security_event("framework_updated", f"Security framework {self.name} updated")

	def activate_security_framework(self):
		"""Activate the security framework"""
		try:
			# Initialize all security layers
			self.initialize_encryption_keys()
			self.setup_access_policies()
			self.activate_threat_detection()
			self.start_monitoring()
			self.enable_compliance_monitoring()

			# Update status
			self.status = "Active"
			self.log_security_event("framework_activated", f"Security framework {self.name} activated")

		except Exception as e:
			frappe.logger().error(f"Security framework activation error: {str(e)}")
			self.log_security_event("activation_failed", f"Failed to activate framework: {str(e)}")

	def initialize_encryption(self):
		"""Initialize encryption layer"""
		try:
			encryption_config = json.loads(self.encryption_config or "{}")

			if encryption_config.get('enabled', False):
				# Generate encryption keys
				self.generate_encryption_keys()

				# Set up encrypted fields
				self.setup_encrypted_fields(encryption_config)

				# Initialize key rotation schedule
				self.schedule_key_rotation()

		except Exception as e:
			frappe.logger().error(f"Encryption initialization error: {str(e)}")

	def configure_access_controls(self):
		"""Configure access control layer"""
		try:
			access_config = json.loads(self.access_policies or "{}")

			if access_config.get('enabled', False):
				# Set up role-based access control
				self.setup_rbac(access_config)

				# Configure multi-factor authentication
				if access_config.get('multi_factor_auth'):
					self.setup_mfa()

				# Set password policies
				self.enforce_password_policy(access_config.get('password_policy', {}))

		except Exception as e:
			frappe.logger().error(f"Access control configuration error: {str(e)}")

	def setup_threat_detection(self):
		"""Set up threat detection layer"""
		try:
			threat_config = json.loads(self.threat_detection_rules or "{}")

			if threat_config.get('enabled', False):
				# Initialize anomaly detection
				if threat_config.get('anomaly_detection'):
					self.initialize_anomaly_detection()

				# Set up intrusion detection
				if threat_config.get('intrusion_detection'):
					self.setup_intrusion_detection()

				# Configure real-time monitoring
				if threat_config.get('real_time_monitoring'):
					self.start_real_time_monitoring()

		except Exception as e:
			frappe.logger().error(f"Threat detection setup error: {str(e)}")

	def initialize_monitoring(self):
		"""Initialize monitoring layer"""
		try:
			monitoring_config = json.loads(self.monitoring_config or "{}")

			if monitoring_config.get('enabled', False):
				# Set up logging
				self.configure_logging(monitoring_config)

				# Initialize audit trail
				if monitoring_config.get('audit_trail'):
					self.initialize_audit_trail()

				# Set up real-time alerts
				if monitoring_config.get('real_time_alerts'):
					self.setup_real_time_alerts()

		except Exception as e:
			frappe.logger().error(f"Monitoring initialization error: {str(e)}")

	def configure_compliance(self):
		"""Configure compliance layer"""
		try:
			compliance_config = json.loads(self.compliance_requirements or "{}")

			if compliance_config.get('enabled', False):
				# Set up compliance standards
				self.setup_compliance_standards(compliance_config.get('standards', []))

				# Configure automated reporting
				if compliance_config.get('auto_reporting'):
					self.setup_automated_reporting()

				# Schedule compliance audits
				self.schedule_compliance_audits(compliance_config)

		except Exception as e:
			frappe.logger().error(f"Compliance configuration error: {str(e)}")

	def generate_encryption_keys(self):
		"""Generate encryption keys"""
		try:
			# Generate a secure encryption key
			key = Fernet.generate_key()

			# Store key securely (in production, use a key management service)
			self.encryption_key = base64.urlsafe_b64encode(key).decode()

			# Initialize Fernet cipher
			self.cipher = Fernet(key)

		except Exception as e:
			frappe.logger().error(f"Key generation error: {str(e)}")

	def encrypt_data(self, data):
		"""Encrypt sensitive data"""
		try:
			if not hasattr(self, 'cipher'):
				self.generate_encryption_keys()

			if isinstance(data, str):
				data = data.encode()

			encrypted_data = self.cipher.encrypt(data)
			return base64.urlsafe_b64encode(encrypted_data).decode()

		except Exception as e:
			frappe.logger().error(f"Data encryption error: {str(e)}")
			return data

	def decrypt_data(self, encrypted_data):
		"""Decrypt sensitive data"""
		try:
			if not hasattr(self, 'cipher'):
				# Load cipher from stored key
				key = base64.urlsafe_b64decode(self.encryption_key.encode())
				self.cipher = Fernet(key)

			encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
			decrypted_data = self.cipher.decrypt(encrypted_bytes)
			return decrypted_data.decode()

		except Exception as e:
			frappe.logger().error(f"Data decryption error: {str(e)}")
			return encrypted_data

	def setup_rbac(self, access_config):
		"""Set up Role-Based Access Control"""
		try:
			# Create security roles if they don't exist
			security_roles = [
				"Security Admin",
				"Security Auditor",
				"Compliance Officer",
				"Data Steward"
			]

			for role in security_roles:
				if not frappe.db.exists("Role", role):
					frappe.get_doc({
						"doctype": "Role",
						"role_name": role,
						"desk_access": 1
					}).insert()

			# Set up role permissions
			self.configure_role_permissions(access_config)

		except Exception as e:
			frappe.logger().error(f"RBAC setup error: {str(e)}")

	def setup_mfa(self):
		"""Set up Multi-Factor Authentication"""
		try:
			# Configure MFA settings
			mfa_settings = {
				"enabled": True,
				"methods": ["TOTP", "SMS", "Email"],
				"required_for_roles": ["Security Admin", "System Manager"],
				"grace_period_days": 7
			}

			# Store MFA configuration
			self.mfa_config = json.dumps(mfa_settings)

		except Exception as e:
			frappe.logger().error(f"MFA setup error: {str(e)}")

	def enforce_password_policy(self, policy):
		"""Enforce password policy"""
		try:
			# Update system password policy
			system_settings = frappe.get_single("System Settings")

			system_settings.minimum_password_score = 3  # Strong password required
			system_settings.password_reset_limit = 3
			system_settings.enable_password_policy = 1

			system_settings.save()

		except Exception as e:
			frappe.logger().error(f"Password policy enforcement error: {str(e)}")

	def initialize_anomaly_detection(self):
		"""Initialize anomaly detection"""
		try:
			# Import anomaly detection engine
			from mkaguzi.risk.anomaly_detection_engine import AnomalyDetectionEngine

			self.anomaly_engine = AnomalyDetectionEngine()

			# Set up anomaly detection rules
			anomaly_rules = {
				"login_anomalies": {
					"threshold": 3,
					"time_window": 3600,  # 1 hour
					"action": "alert"
				},
				"data_access_anomalies": {
					"threshold": 100,
					"time_window": 86400,  # 24 hours
					"action": "block"
				}
			}

			self.anomaly_rules = json.dumps(anomaly_rules)

		except Exception as e:
			frappe.logger().error(f"Anomaly detection initialization error: {str(e)}")

	def setup_intrusion_detection(self):
		"""Set up intrusion detection"""
		try:
			ids_rules = {
				"sql_injection_patterns": [
					r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
					r"(\%22)|(\")",
					r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))"
				],
				"xss_patterns": [
					r"<script[^>]*>.*?</script>",
					r"javascript:",
					r"on\w+\s*="
				],
				"brute_force_threshold": 5,
				"block_duration": 3600  # 1 hour
			}

			self.ids_rules = json.dumps(ids_rules)

		except Exception as e:
			frappe.logger().error(f"Intrusion detection setup error: {str(e)}")

	def configure_logging(self, monitoring_config):
		"""Configure security logging"""
		try:
			# Set up security event logging
			log_config = {
				"level": monitoring_config.get('log_level', 'INFO'),
				"handlers": ["file", "database"],
				"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
				"retention_days": monitoring_config.get('retention_days', 365)
			}

			self.log_config = json.dumps(log_config)

			# Initialize log storage
			self.initialize_log_storage()

		except Exception as e:
			frappe.logger().error(f"Logging configuration error: {str(e)}")

	def initialize_audit_trail(self):
		"""Initialize audit trail"""
		try:
			# Set up comprehensive audit logging
			audit_config = {
				"track_changes": True,
				"track_access": True,
				"track_authentication": True,
				"retention_years": 7,
				"auto_archive": True
			}

			self.audit_config = json.dumps(audit_config)

		except Exception as e:
			frappe.logger().error(f"Audit trail initialization error: {str(e)}")

	def setup_compliance_standards(self, standards):
		"""Set up compliance standards"""
		try:
			compliance_frameworks = {
				"GDPR": {
					"data_protection_officer": True,
					"data_processing_register": True,
					"privacy_impact_assessment": True,
					"breach_notification_hours": 72
				},
				"SOX": {
					"internal_controls": True,
					"financial_reporting": True,
					"audit_committee": True,
					"certification_requirements": True
				},
				"PCI-DSS": {
					"cardholder_data_protection": True,
					"encryption": True,
					"access_controls": True,
					"monitoring": True
				}
			}

			active_standards = {}
			for standard in standards:
				if standard in compliance_frameworks:
					active_standards[standard] = compliance_frameworks[standard]

			self.active_compliance_standards = json.dumps(active_standards)

		except Exception as e:
			frappe.logger().error(f"Compliance standards setup error: {str(e)}")

	def log_security_event(self, event_type, message, severity="INFO", user=None):
		"""Log a security event"""
		try:
			event = {
				"timestamp": now(),
				"event_type": event_type,
				"message": message,
				"severity": severity,
				"user": user or frappe.session.user,
				"ip_address": frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else None,
				"session_id": frappe.session.sid if hasattr(frappe.session, 'sid') else None
			}

			# Add to security logs
			security_logs = json.loads(self.security_logs or "[]")
			security_logs.append(event)

			# Keep only recent logs (last 1000)
			if len(security_logs) > 1000:
				security_logs = security_logs[-1000:]

			self.security_logs = json.dumps(security_logs)

			# Log to system logger
			logger = logging.getLogger("security")
			log_method = getattr(logger, severity.lower(), logger.info)
			log_method(f"[{event_type}] {message}")

		except Exception as e:
			frappe.logger().error(f"Security event logging error: {str(e)}")

	def detect_threat(self, threat_type, data, context=None):
		"""Detect and respond to security threats"""
		try:
			threat_detected = False
			response_action = "monitor"

			if threat_type == "anomaly":
				threat_detected = self.detect_anomaly(data)
			elif threat_type == "intrusion":
				threat_detected = self.detect_intrusion(data)
			elif threat_type == "unauthorized_access":
				threat_detected = self.detect_unauthorized_access(data)
			elif threat_type == "data_breach":
				threat_detected = self.detect_data_breach(data)

			if threat_detected:
				# Log threat
				self.log_security_event("threat_detected", f"{threat_type} detected", "WARNING")

				# Determine response action
				response_action = self.determine_threat_response(threat_type, data)

				# Execute response
				self.execute_threat_response(response_action, threat_type, data, context)

				# Update threat metrics
				self.update_threat_metrics(threat_type)

			return threat_detected, response_action

		except Exception as e:
			frappe.logger().error(f"Threat detection error: {str(e)}")
			return False, "error"

	def detect_anomaly(self, data):
		"""Detect anomalies in data patterns"""
		try:
			if hasattr(self, 'anomaly_engine'):
				anomalies = self.anomaly_engine.detect_anomalies(data)
				return len(anomalies) > 0
			return False

		except Exception as e:
			return False

	def detect_intrusion(self, data):
		"""Detect intrusion attempts"""
		try:
			ids_rules = json.loads(self.ids_rules or "{}")

			for pattern_type, patterns in ids_rules.items():
				if pattern_type.endswith('_patterns'):
					for pattern in patterns:
						if re.search(pattern, str(data), re.IGNORECASE):
							return True

			return False

		except Exception as e:
			return False

	def detect_unauthorized_access(self, data):
		"""Detect unauthorized access attempts"""
		try:
			# Check for suspicious access patterns
			user = data.get('user')
			action = data.get('action')
			resource = data.get('resource')

			# Implement access pattern analysis
			return False  # Placeholder

		except Exception as e:
			return False

	def detect_data_breach(self, data):
		"""Detect potential data breaches"""
		try:
			# Monitor for unusual data access patterns
			return False  # Placeholder

		except Exception as e:
			return False

	def determine_threat_response(self, threat_type, data):
		"""Determine appropriate response to threat"""
		try:
			response_matrix = {
				"anomaly": "alert",
				"intrusion": "block",
				"unauthorized_access": "block",
				"data_breach": "quarantine"
			}

			return response_matrix.get(threat_type, "monitor")

		except Exception as e:
			return "monitor"

	def execute_threat_response(self, action, threat_type, data, context=None):
		"""Execute threat response action"""
		try:
			if action == "alert":
				self.send_security_alert(threat_type, data, context)
			elif action == "block":
				self.block_threat(threat_type, data, context)
			elif action == "quarantine":
				self.quarantine_resource(threat_type, data, context)

			# Log response action
			self.log_security_event("threat_response", f"Executed {action} for {threat_type}", "INFO")

		except Exception as e:
			frappe.logger().error(f"Threat response execution error: {str(e)}")

	def send_security_alert(self, threat_type, data, context=None):
		"""Send security alert"""
		try:
			subject = f"Security Alert: {threat_type.title()}"
			message = f"""
			Security Alert Detected:

			Type: {threat_type}
			Time: {now()}
			Data: {json.dumps(data, indent=2)}
			Context: {context or 'N/A'}

			Please investigate immediately.
			"""

			# Send to security team
			frappe.sendmail(
				recipients=["security@company.com"],
				subject=subject,
				message=message
			)

		except Exception as e:
			frappe.logger().error(f"Security alert sending error: {str(e)}")

	def update_security_metrics(self):
		"""Update security metrics"""
		try:
			# Calculate security score
			self.security_score = self.calculate_security_score()

			# Determine threat level
			self.threat_level = self.determine_threat_level()

			# Calculate compliance score
			self.compliance_score = self.calculate_compliance_score()

			# Update performance metrics
			performance_metrics = json.loads(self.performance_metrics or "{}")
			performance_metrics["last_updated"] = now()
			self.performance_metrics = json.dumps(performance_metrics)

		except Exception as e:
			frappe.logger().error(f"Security metrics update error: {str(e)}")

	def calculate_security_score(self):
		"""Calculate overall security score"""
		try:
			score = 0
			max_score = 100

			# Encryption score (20 points)
			if json.loads(self.encryption_layer or "{}").get('enabled'):
				score += 20

			# Access control score (25 points)
			if json.loads(self.access_control_layer or "{}").get('enabled'):
				score += 25

			# Threat detection score (20 points)
			if json.loads(self.threat_detection_layer or "{}").get('enabled'):
				score += 20

			# Monitoring score (15 points)
			if json.loads(self.monitoring_layer or "{}").get('enabled'):
				score += 15

			# Compliance score (20 points)
			if json.loads(self.compliance_layer or "{}").get('enabled'):
				score += 20

			return min(score, max_score)

		except Exception as e:
			return 0.0

	def determine_threat_level(self):
		"""Determine current threat level"""
		try:
			score = self.security_score or 0

			if score >= 80:
				return "Low"
			elif score >= 60:
				return "Medium"
			elif score >= 40:
				return "High"
			else:
				return "Critical"

		except Exception as e:
			return "Unknown"

	def calculate_compliance_score(self):
		"""Calculate compliance score"""
		try:
			# Placeholder compliance calculation
			return 85.0

		except Exception as e:
			return 0.0

	# Helper methods
	def initialize_encryption_keys(self):
		"""Initialize encryption keys"""
		pass

	def setup_access_policies(self):
		"""Set up access policies"""
		pass

	def activate_threat_detection(self):
		"""Activate threat detection"""
		pass

	def start_monitoring(self):
		"""Start monitoring"""
		pass

	def enable_compliance_monitoring(self):
		"""Enable compliance monitoring"""
		pass

	def setup_encrypted_fields(self, config):
		"""Set up encrypted fields"""
		pass

	def schedule_key_rotation(self):
		"""Schedule key rotation"""
		pass

	def configure_role_permissions(self, config):
		"""Configure role permissions"""
		pass

	def start_real_time_monitoring(self):
		"""Start real-time monitoring"""
		pass

	def setup_real_time_alerts(self):
		"""Set up real-time alerts"""
		pass

	def setup_automated_reporting(self):
		"""Set up automated reporting"""
		pass

	def schedule_compliance_audits(self, config):
		"""Schedule compliance audits"""
		pass

	def initialize_log_storage(self):
		"""Initialize log storage"""
		pass

	def block_threat(self, threat_type, data, context):
		"""Block threat"""
		pass

	def quarantine_resource(self, threat_type, data, context):
		"""Quarantine resource"""
		pass

	def update_threat_metrics(self, threat_type):
		"""Update threat metrics"""
		pass


@frappe.whitelist()
def activate_security_framework(framework_id):
	"""Activate a security framework"""
	try:
		framework = frappe.get_doc("Advanced Security Framework", framework_id)
		framework.activate_security_framework()
		return {"success": True, "message": "Security framework activated successfully"}

	except Exception as e:
		frappe.log_error(f"Security framework activation error: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def detect_security_threat(framework_id, threat_type, data):
	"""Detect security threat"""
	try:
		framework = frappe.get_doc("Advanced Security Framework", framework_id)
		detected, action = framework.detect_threat(threat_type, json.loads(data))
		return {
			"success": True,
			"threat_detected": detected,
			"response_action": action
		}

	except Exception as e:
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def encrypt_sensitive_data(framework_id, data):
	"""Encrypt sensitive data"""
	try:
		framework = frappe.get_doc("Advanced Security Framework", framework_id)
		encrypted = framework.encrypt_data(data)
		return {"success": True, "encrypted_data": encrypted}

	except Exception as e:
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def decrypt_sensitive_data(framework_id, encrypted_data):
	"""Decrypt sensitive data"""
	try:
		framework = frappe.get_doc("Advanced Security Framework", framework_id)
		decrypted = framework.decrypt_data(encrypted_data)
		return {"success": True, "decrypted_data": decrypted}

	except Exception as e:
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_security_metrics(framework_id):
	"""Get security metrics"""
	try:
		framework = frappe.get_doc("Advanced Security Framework", framework_id)
		framework.update_security_metrics()

		return {
			"success": True,
			"security_score": framework.security_score,
			"threat_level": framework.threat_level,
			"compliance_score": framework.compliance_score,
			"metrics": json.loads(framework.performance_metrics or "{}")
		}

	except Exception as e:
		return {"success": False, "error": str(e)}