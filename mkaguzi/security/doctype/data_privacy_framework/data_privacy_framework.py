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
import re


class DataPrivacyFramework(Document):
	def validate(self):
		"""Validate the data privacy framework"""
		self.validate_privacy_framework_id()
		self.set_default_values()
		self.validate_privacy_configurations()
		self.initialize_gdpr_compliance()
		self.initialize_ccpa_compliance()
		self.setup_data_inventory()
		self.configure_consent_management()
		self.setup_data_subject_rights()
		self.initialize_breach_response()
		self.configure_privacy_impact_assessment()

	def validate_privacy_framework_id(self):
		"""Auto-generate privacy framework ID if not provided"""
		if not self.privacy_framework_id:
			type_short = "DPF"
			random_suffix = ''.join(str(uuid.uuid4().hex)[:8])
			self.privacy_framework_id = f"{type_short}-{random_suffix}"

	def set_default_values(self):
		"""Set default values"""
		if not self.created_by:
			self.created_by = frappe.session.user

		if not self.framework_version:
			self.framework_version = "1.0.0"

		if not self.status:
			self.status = "Draft"

		if not self.privacy_policy_version:
			self.privacy_policy_version = "1.0"

		if not self.gdpr_compliance:
			self.gdpr_compliance = json.dumps({
				"enabled": False,
				"data_protection_officer_assigned": False,
				"records_of_processing_activities": False,
				"data_processing_register": False,
				"privacy_impact_assessment": False,
				"compliance_score": 0
			})

		if not self.ccpa_compliance:
			self.ccpa_compliance = json.dumps({
				"enabled": False,
				"privacy_notice_posted": False,
				"do_not_sell_mechanism": False,
				"data_request_response_time": 45,
				"compliance_score": 0
			})

		if not self.data_inventory:
			self.data_inventory = json.dumps({
				"personal_data_categories": [],
				"data_subjects": [],
				"processing_purposes": [],
				"data_recipients": [],
				"international_transfers": [],
				"retention_schedules": []
			})

		if not self.consent_management:
			self.consent_management = json.dumps({
				"consent_required": True,
				"consent_types": ["marketing", "analytics", "third_party"],
				"consent_withdrawal_period": 30,
				"consent_logs_retention": 365,
				"granular_consent": True
			})

		if not self.privacy_logs:
			self.privacy_logs = json.dumps([])

		if not self.consent_logs:
			self.consent_logs = json.dumps([])

		if not self.access_logs:
			self.access_logs = json.dumps([])

		if not self.violation_reports:
			self.violation_reports = json.dumps([])

		if not self.performance_metrics:
			self.performance_metrics = json.dumps({
				"consent_request_response_time": 0.0,
				"data_subject_rights_fulfilled": 0,
				"privacy_violations_detected": 0,
				"last_updated": now()
			})

	def validate_privacy_configurations(self):
		"""Validate privacy configuration JSON fields"""
		config_fields = ['gdpr_compliance', 'ccpa_compliance', 'data_inventory', 'processing_activities',
						'legal_basis_matrix', 'consent_management', 'access_rights', 'rectification_rights',
						'erasure_rights', 'portability_rights', 'objection_rights', 'restriction_rights',
						'breach_response_plan', 'breach_notification_log', 'breach_impact_assessment',
						'automated_decision_making', 'privacy_impact_assessments', 'data_sharing_agreements',
						'international_data_transfers', 'cookie_consent_management', 'privacy_training_records',
						'data_retention_schedules', 'anonymization_procedures', 'privacy_logs', 'consent_logs',
						'access_logs', 'violation_reports', 'performance_metrics']

		for field in config_fields:
			value = getattr(self, field, None)
			if value:
				try:
					json.loads(value)
				except json.JSONDecodeError:
					frappe.throw(_(f"{field.replace('_', ' ').title()} must be valid JSON"))

	def on_update(self):
		"""Called when document is updated"""
		if self.status == "Active":
			self.activate_privacy_framework()
		self.update_compliance_metrics()
		self.log_privacy_event("framework_updated", f"Privacy framework {self.name} updated")

	def activate_privacy_framework(self):
		"""Activate the privacy framework"""
		try:
			# Initialize all privacy components
			self.initialize_data_inventory()
			self.setup_consent_mechanisms()
			self.configure_data_subject_rights()
			self.setup_breach_notification_system()
			self.initialize_privacy_monitoring()

			# Update status
			self.status = "Active"
			self.log_privacy_event("framework_activated", f"Privacy framework {self.name} activated")

		except Exception as e:
			frappe.logger().error(f"Privacy framework activation error: {str(e)}")
			self.log_privacy_event("activation_failed", f"Failed to activate privacy framework: {str(e)}")

	def initialize_gdpr_compliance(self):
		"""Initialize GDPR compliance components"""
		try:
			gdpr_config = json.loads(self.gdpr_compliance or "{}")

			if gdpr_config.get('enabled', False):
				# Set up GDPR-specific requirements
				self.setup_gdpr_data_protection_officer()
				self.initialize_records_of_processing()
				self.setup_data_processing_register()
				self.configure_privacy_impact_assessment()

		except Exception as e:
			frappe.logger().error(f"GDPR compliance initialization error: {str(e)}")

	def initialize_ccpa_compliance(self):
		"""Initialize CCPA compliance components"""
		try:
			ccpa_config = json.loads(self.ccpa_compliance or "{}")

			if ccpa_config.get('enabled', False):
				# Set up CCPA-specific requirements
				self.setup_ccpa_privacy_notice()
				self.configure_do_not_sell_mechanism()
				self.setup_ccpa_data_request_handling()

		except Exception as e:
			frappe.logger().error(f"CCPA compliance initialization error: {str(e)}")

	def setup_data_inventory(self):
		"""Set up data inventory"""
		try:
			data_inventory = json.loads(self.data_inventory or "{}")

			# Initialize data categories
			data_categories = {
				"personal_identifiers": ["name", "email", "phone", "address", "id_number"],
				"financial_data": ["bank_details", "payment_info", "credit_score"],
				"health_data": ["medical_records", "health_history"],
				"online_identifiers": ["ip_address", "cookies", "device_id"],
				"geolocation_data": ["location_coordinates", "address"],
				"biometric_data": ["fingerprints", "facial_recognition"],
				"educational_data": ["education_records", "certifications"],
				"employment_data": ["job_history", "performance_reviews"]
			}

			data_inventory["data_categories"] = data_categories
			self.data_inventory = json.dumps(data_inventory)

		except Exception as e:
			frappe.logger().error(f"Data inventory setup error: {str(e)}")

	def configure_consent_management(self):
		"""Configure consent management system"""
		try:
			consent_config = json.loads(self.consent_management or "{}")

			if consent_config.get('consent_required', True):
				# Set up consent collection mechanisms
				self.setup_consent_collection()
				self.configure_consent_withdrawal()
				self.initialize_consent_audit_trail()

		except Exception as e:
			frappe.logger().error(f"Consent management configuration error: {str(e)}")

	def setup_data_subject_rights(self):
		"""Set up data subject rights implementation"""
		try:
			# Initialize all data subject rights
			rights_config = {
				"access": {
					"enabled": True,
					"response_time_days": 30,
					"free_of_charge": True,
					"electronic_format": True
				},
				"rectification": {
					"enabled": True,
					"response_time_days": 30,
					"verification_required": True
				},
				"erasure": {
					"enabled": True,
					"response_time_days": 30,
					"grounds_check_required": True,
					"anonymization_allowed": True
				},
				"portability": {
					"enabled": True,
					"response_time_days": 30,
					"structured_format": True,
					"machine_readable": True
				},
				"objection": {
					"enabled": True,
					"response_time_days": 30,
					"automated_decision_making": True,
					"direct_marketing": True
				},
				"restriction": {
					"enabled": True,
					"response_time_days": 30,
					"verification_required": True
				}
			}

			self.access_rights = json.dumps(rights_config["access"])
			self.rectification_rights = json.dumps(rights_config["rectification"])
			self.erasure_rights = json.dumps(rights_config["erasure"])
			self.portability_rights = json.dumps(rights_config["portability"])
			self.objection_rights = json.dumps(rights_config["objection"])
			self.restriction_rights = json.dumps(rights_config["restriction"])

		except Exception as e:
			frappe.logger().error(f"Data subject rights setup error: {str(e)}")

	def initialize_breach_response(self):
		"""Initialize data breach response system"""
		try:
			breach_response_plan = {
				"breach_detection": {
					"automated_monitoring": True,
					"manual_reporting": True,
					"detection_thresholds": {
						"data_records_affected": 100,
						"response_time_hours": 24
					}
				},
				"breach_assessment": {
					"risk_evaluation": True,
					"impact_assessment": True,
					"notification_required": True
				},
				"notification_procedures": {
					"supervisory_authority_hours": 72,
					"data_subjects_days": 30,
					"notification_template": True,
					"communication_channels": ["email", "phone", "mail"]
				},
				"containment_measures": {
					"isolate_affected_systems": True,
					"preserve_evidence": True,
					"notify_security_team": True
				},
				"recovery_procedures": {
					"system_restoration": True,
					"data_recovery": True,
					"post_incident_review": True
				}
			}

			self.breach_response_plan = json.dumps(breach_response_plan)
			self.breach_notification_log = json.dumps([])
			self.breach_impact_assessment = json.dumps({})

		except Exception as e:
			frappe.logger().error(f"Breach response initialization error: {str(e)}")

	def configure_privacy_impact_assessment(self):
		"""Configure privacy impact assessment system"""
		try:
			pia_config = {
				"pia_required_thresholds": {
					"data_subjects_affected": 1000,
					"high_risk_processing": True,
					"new_technology": True,
					"systematic_monitoring": True
				},
				"pia_process": {
					"screening_phase": True,
					"assessment_phase": True,
					"mitigation_phase": True,
					"approval_phase": True,
					"monitoring_phase": True
				},
				"pia_template": {
					"project_description": True,
					"data_processing_description": True,
					"necessity_proportionality": True,
					"risks_rights_freedoms": True,
					"mitigation_measures": True
				},
				"pia_review_cycle": "annual"
			}

			self.privacy_impact_assessments = json.dumps(pia_config)

		except Exception as e:
			frappe.logger().error(f"Privacy impact assessment configuration error: {str(e)}")

	def log_privacy_event(self, event_type, message, severity="INFO", data_subject=None):
		"""Log a privacy event"""
		try:
			event = {
				"timestamp": now(),
				"event_type": event_type,
				"message": message,
				"severity": severity,
				"user": frappe.session.user,
				"data_subject": data_subject,
				"ip_address": getattr(frappe.local, 'request_ip', None),
				"session_id": getattr(frappe.session, 'sid', None)
			}

			# Add to privacy logs
			privacy_logs = json.loads(self.privacy_logs or "[]")
			privacy_logs.append(event)

			# Keep only recent logs (last 1000)
			if len(privacy_logs) > 1000:
				privacy_logs = privacy_logs[-1000:]

			self.privacy_logs = json.dumps(privacy_logs)

			# Log to system logger
			logger = logging.getLogger("privacy")
			log_method = getattr(logger, severity.lower(), logger.info)
			log_method(f"[{event_type}] {message}")

		except Exception as e:
			frappe.logger().error(f"Privacy event logging error: {str(e)}")

	def handle_data_subject_request(self, request_type, data_subject_id, request_data=None):
		"""Handle data subject rights requests"""
		try:
			request_handlers = {
				"access": self.handle_access_request,
				"rectification": self.handle_rectification_request,
				"erasure": self.handle_erasure_request,
				"portability": self.handle_portability_request,
				"objection": self.handle_objection_request,
				"restriction": self.handle_restriction_request
			}

			if request_type not in request_handlers:
				frappe.throw(f"Unknown request type: {request_type}")

			handler = request_handlers[request_type]
			result = handler(data_subject_id, request_data)

			# Log the request
			self.log_privacy_event("data_subject_request",
				f"{request_type.title()} request processed for data subject {data_subject_id}",
				"INFO", data_subject_id)

			# Update access logs
			self.log_data_access(data_subject_id, request_type, "granted")

			return result

		except Exception as e:
			frappe.logger().error(f"Data subject request handling error: {str(e)}")
			self.log_privacy_event("data_subject_request_failed",
				f"Failed to process {request_type} request: {str(e)}",
				"ERROR", data_subject_id)
			return {"success": False, "error": str(e)}

	def handle_access_request(self, data_subject_id, request_data=None):
		"""Handle data access request"""
		try:
			# Collect all personal data for the data subject
			personal_data = self.collect_personal_data(data_subject_id)

			# Format for response
			response_data = {
				"data_subject_id": data_subject_id,
				"data_collected": personal_data,
				"processing_purposes": self.get_processing_purposes(data_subject_id),
				"legal_basis": self.get_legal_basis(data_subject_id),
				"recipients": self.get_data_recipients(data_subject_id),
				"retention_period": self.get_retention_period(data_subject_id),
				"response_date": now()
			}

			return {"success": True, "data": response_data}

		except Exception as e:
			return {"success": False, "error": str(e)}

	def handle_rectification_request(self, data_subject_id, request_data):
		"""Handle data rectification request"""
		try:
			if not request_data:
				frappe.throw("Rectification data is required")

			# Update personal data
			self.update_personal_data(data_subject_id, request_data)

			return {"success": True, "message": "Data rectified successfully"}

		except Exception as e:
			return {"success": False, "error": str(e)}

	def handle_erasure_request(self, data_subject_id, request_data=None):
		"""Handle data erasure request"""
		try:
			# Check if erasure is allowed
			if not self.can_erase_data(data_subject_id):
				return {"success": False, "error": "Data erasure not permitted under current legal basis"}

			# Anonymize or delete personal data
			self.erase_personal_data(data_subject_id)

			return {"success": True, "message": "Data erased successfully"}

		except Exception as e:
			return {"success": False, "error": str(e)}

	def handle_portability_request(self, data_subject_id, request_data=None):
		"""Handle data portability request"""
		try:
			# Collect all personal data in structured format
			personal_data = self.collect_personal_data(data_subject_id)

			# Convert to machine-readable format (JSON)
			portable_data = {
				"data_subject_id": data_subject_id,
				"export_date": now(),
				"data": personal_data,
				"metadata": {
					"framework_version": self.framework_version,
					"export_format": "JSON",
					"compliance_standard": "GDPR Article 20"
				}
			}

			return {"success": True, "portable_data": portable_data}

		except Exception as e:
			return {"success": False, "error": str(e)}

	def handle_objection_request(self, data_subject_id, request_data=None):
		"""Handle objection request"""
		try:
			objection_type = request_data.get("objection_type", "general")

			# Stop processing for the specified purpose
			self.stop_processing(data_subject_id, objection_type)

			return {"success": True, "message": f"Objection to {objection_type} processing recorded"}

		except Exception as e:
			return {"success": False, "error": str(e)}

	def handle_restriction_request(self, data_subject_id, request_data=None):
		"""Handle restriction request"""
		try:
			restriction_type = request_data.get("restriction_type", "general")

			# Restrict processing
			self.restrict_processing(data_subject_id, restriction_type)

			return {"success": True, "message": f"Processing restricted for {restriction_type}"}

		except Exception as e:
			return {"success": False, "error": str(e)}

	def manage_consent(self, data_subject_id, consent_type, action, scope=None):
		"""Manage data subject consent"""
		try:
			consent_record = {
				"data_subject_id": data_subject_id,
				"consent_type": consent_type,
				"action": action,
				"scope": scope,
				"timestamp": now(),
				"user": frappe.session.user,
				"ip_address": getattr(frappe.local, 'request_ip', None)
			}

			# Add to consent logs
			consent_logs = json.loads(self.consent_logs or "[]")
			consent_logs.append(consent_record)

			# Keep only recent logs (last 10000)
			if len(consent_logs) > 10000:
				consent_logs = consent_logs[-10000:]

			self.consent_logs = json.dumps(consent_logs)

			# Update consent status
			self.update_consent_status(data_subject_id, consent_type, action)

			self.log_privacy_event("consent_updated",
				f"Consent {action} for {consent_type} by data subject {data_subject_id}",
				"INFO", data_subject_id)

			return {"success": True, "message": f"Consent {action} recorded"}

		except Exception as e:
			frappe.logger().error(f"Consent management error: {str(e)}")
			return {"success": False, "error": str(e)}

	def detect_privacy_violation(self, violation_type, data, context=None):
		"""Detect privacy violations"""
		try:
			violation_detected = False
			severity = "low"

			if violation_type == "unauthorized_access":
				violation_detected, severity = self.detect_unauthorized_access(data)
			elif violation_type == "consent_violation":
				violation_detected, severity = self.detect_consent_violation(data)
			elif violation_type == "retention_violation":
				violation_detected, severity = self.detect_retention_violation(data)
			elif violation_type == "data_breach":
				violation_detected, severity = self.detect_data_breach_violation(data)

			if violation_detected:
				# Log violation
				self.log_privacy_violation(violation_type, data, severity, context)

				# Trigger response
				self.respond_to_privacy_violation(violation_type, data, severity)

				# Update violation metrics
				self.update_violation_metrics(violation_type, severity)

			return violation_detected, severity

		except Exception as e:
			frappe.logger().error(f"Privacy violation detection error: {str(e)}")
			return False, "unknown"

	def handle_data_breach(self, breach_data):
		"""Handle data breach incident"""
		try:
			# Assess breach impact
			impact_assessment = self.assess_breach_impact(breach_data)

			# Determine notification requirements
			notification_required = self.determine_breach_notification(impact_assessment)

			if notification_required:
				# Notify supervisory authority
				self.notify_supervisory_authority(breach_data, impact_assessment)

				# Notify affected data subjects
				self.notify_data_subjects(breach_data, impact_assessment)

			# Log breach
			breach_record = {
				"breach_id": str(uuid.uuid4()),
				"timestamp": now(),
				"data_affected": breach_data,
				"impact_assessment": impact_assessment,
				"notification_sent": notification_required,
				"containment_actions": self.get_containment_actions(breach_data),
				"status": "reported"
			}

			breach_log = json.loads(self.breach_notification_log or "[]")
			breach_log.append(breach_record)
			self.breach_notification_log = json.dumps(breach_log)

			self.log_privacy_event("data_breach",
				f"Data breach incident handled: {breach_record['breach_id']}",
				"CRITICAL")

			return {"success": True, "breach_id": breach_record["breach_id"]}

		except Exception as e:
			frappe.logger().error(f"Data breach handling error: {str(e)}")
			return {"success": False, "error": str(e)}

	def update_compliance_metrics(self):
		"""Update privacy compliance metrics"""
		try:
			# Calculate compliance score
			self.compliance_score = self.calculate_compliance_score()

			# Count violations
			violations = json.loads(self.violation_reports or "[]")
			self.open_violations = len([v for v in violations if v.get("status") == "open"])
			self.resolved_violations = len([v for v in violations if v.get("status") == "resolved"])

			# Update performance metrics
			performance_metrics = json.loads(self.performance_metrics or "{}")
			performance_metrics["last_updated"] = now()
			self.performance_metrics = json.dumps(performance_metrics)

		except Exception as e:
			frappe.logger().error(f"Compliance metrics update error: {str(e)}")

	def calculate_compliance_score(self):
		"""Calculate privacy compliance score"""
		try:
			score = 0
			max_score = 100

			# GDPR compliance (40 points)
			gdpr_config = json.loads(self.gdpr_compliance or "{}")
			if gdpr_config.get("enabled"):
				score += 40

			# CCPA compliance (20 points)
			ccpa_config = json.loads(self.ccpa_compliance or "{}")
			if ccpa_config.get("enabled"):
				score += 20

			# Data inventory (10 points)
			data_inventory = json.loads(self.data_inventory or "{}")
			if data_inventory.get("personal_data_categories"):
				score += 10

			# Consent management (10 points)
			consent_config = json.loads(self.consent_management or "{}")
			if consent_config.get("consent_required"):
				score += 10

			# Data subject rights (10 points)
			rights_config = json.loads(self.access_rights or "{}")
			if rights_config.get("enabled"):
				score += 10

			# Breach response (10 points)
			breach_config = json.loads(self.breach_response_plan or "{}")
			if breach_config:
				score += 10

			return min(score, max_score)

		except Exception as e:
			return 0.0

	# Helper methods
	def initialize_data_inventory(self):
		"""Initialize data inventory"""
		pass

	def setup_consent_mechanisms(self):
		"""Set up consent mechanisms"""
		pass

	def configure_data_subject_rights(self):
		"""Configure data subject rights"""
		pass

	def setup_breach_notification_system(self):
		"""Set up breach notification system"""
		pass

	def initialize_privacy_monitoring(self):
		"""Initialize privacy monitoring"""
		pass

	def setup_gdpr_data_protection_officer(self):
		"""Set up GDPR data protection officer"""
		pass

	def initialize_records_of_processing(self):
		"""Initialize records of processing"""
		pass

	def setup_data_processing_register(self):
		"""Set up data processing register"""
		pass

	def setup_ccpa_privacy_notice(self):
		"""Set up CCPA privacy notice"""
		pass

	def configure_do_not_sell_mechanism(self):
		"""Configure do not sell mechanism"""
		pass

	def setup_ccpa_data_request_handling(self):
		"""Set up CCPA data request handling"""
		pass

	def setup_consent_collection(self):
		"""Set up consent collection"""
		pass

	def configure_consent_withdrawal(self):
		"""Configure consent withdrawal"""
		pass

	def initialize_consent_audit_trail(self):
		"""Initialize consent audit trail"""
		pass

	def collect_personal_data(self, data_subject_id):
		"""Collect personal data for access request"""
		return {}

	def get_processing_purposes(self, data_subject_id):
		"""Get processing purposes"""
		return []

	def get_legal_basis(self, data_subject_id):
		"""Get legal basis"""
		return {}

	def get_data_recipients(self, data_subject_id):
		"""Get data recipients"""
		return []

	def get_retention_period(self, data_subject_id):
		"""Get retention period"""
		return {}

	def update_personal_data(self, data_subject_id, data):
		"""Update personal data"""
		pass

	def can_erase_data(self, data_subject_id):
		"""Check if data can be erased"""
		return True

	def erase_personal_data(self, data_subject_id):
		"""Erase personal data"""
		pass

	def stop_processing(self, data_subject_id, objection_type):
		"""Stop processing for objection"""
		pass

	def restrict_processing(self, data_subject_id, restriction_type):
		"""Restrict processing"""
		pass

	def log_data_access(self, data_subject_id, access_type, result):
		"""Log data access"""
		pass

	def update_consent_status(self, data_subject_id, consent_type, action):
		"""Update consent status"""
		pass

	def detect_unauthorized_access(self, data):
		"""Detect unauthorized access"""
		return False, "low"

	def detect_consent_violation(self, data):
		"""Detect consent violation"""
		return False, "low"

	def detect_retention_violation(self, data):
		"""Detect retention violation"""
		return False, "low"

	def detect_data_breach_violation(self, data):
		"""Detect data breach violation"""
		return False, "low"

	def log_privacy_violation(self, violation_type, data, severity, context):
		"""Log privacy violation"""
		pass

	def respond_to_privacy_violation(self, violation_type, data, severity):
		"""Respond to privacy violation"""
		pass

	def update_violation_metrics(self, violation_type, severity):
		"""Update violation metrics"""
		pass

	def assess_breach_impact(self, breach_data):
		"""Assess breach impact"""
		return {}

	def determine_breach_notification(self, impact_assessment):
		"""Determine if breach notification is required"""
		return True

	def notify_supervisory_authority(self, breach_data, impact_assessment):
		"""Notify supervisory authority"""
		pass

	def notify_data_subjects(self, breach_data, impact_assessment):
		"""Notify data subjects"""
		pass

	def get_containment_actions(self, breach_data):
		"""Get containment actions"""
		return []


@frappe.whitelist()
def handle_data_subject_request(framework_id, request_type, data_subject_id, request_data=None):
	"""Handle data subject rights request"""
	try:
		framework = frappe.get_doc("Data Privacy Framework", framework_id)
		result = framework.handle_data_subject_request(request_type, data_subject_id, json.loads(request_data or "{}"))
		return result

	except Exception as e:
		frappe.log_error(f"Data subject request handling error: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def manage_data_consent(framework_id, data_subject_id, consent_type, action, scope=None):
	"""Manage data subject consent"""
	try:
		framework = frappe.get_doc("Data Privacy Framework", framework_id)
		result = framework.manage_consent(data_subject_id, consent_type, action, scope)
		return result

	except Exception as e:
		frappe.log_error(f"Consent management error: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def report_data_breach(framework_id, breach_data):
	"""Report data breach"""
	try:
		framework = frappe.get_doc("Data Privacy Framework", breach_data)
		result = framework.handle_data_breach(json.loads(breach_data))
		return result

	except Exception as e:
		frappe.log_error(f"Data breach reporting error: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_privacy_metrics(framework_id):
	"""Get privacy compliance metrics"""
	try:
		framework = frappe.get_doc("Data Privacy Framework", framework_id)
		framework.update_compliance_metrics()

		return {
			"success": True,
			"compliance_score": framework.compliance_score,
			"open_violations": framework.open_violations,
			"resolved_violations": framework.resolved_violations,
			"metrics": json.loads(framework.performance_metrics or "{}")
		}

	except Exception as e:
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def detect_privacy_violation(framework_id, violation_type, data):
	"""Detect privacy violation"""
	try:
		framework = frappe.get_doc("Data Privacy Framework", framework_id)
		detected, severity = framework.detect_privacy_violation(violation_type, json.loads(data))
		return {
			"success": True,
			"violation_detected": detected,
			"severity": severity
		}

	except Exception as e:
		return {"success": False, "error": str(e)}