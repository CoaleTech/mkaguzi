# -*- coding: utf-8 -*-
# Copyright (c) 2024, Coale Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import now, get_datetime, add_days, cint
import json
from datetime import datetime, timedelta
from mkaguzi.risk.anomaly_detection_engine import anomaly_engine


class RiskSynchronizationManager:
	"""Manages real-time risk data synchronization and monitoring"""

	def __init__(self):
		self.controllers = {}
		self.indicators = {}
		self.active_monitors = set()

	def register_controller(self, doctype, controller_class):
		"""Register a controller for real-time monitoring"""
		self.controllers[doctype] = controller_class

	def register_indicator(self, indicator_name, indicator_config):
		"""Register a risk indicator for monitoring"""
		self.indicators[indicator_name] = indicator_config

	def start_monitoring(self, doctype, docname=None):
		"""Start real-time monitoring for a doctype/document"""
		monitor_key = f"{doctype}:{docname}" if docname else doctype
		self.active_monitors.add(monitor_key)

	def stop_monitoring(self, doctype, docname=None):
		"""Stop monitoring for a doctype/document"""
		monitor_key = f"{doctype}:{docname}" if docname else doctype
		self.active_monitors.discard(monitor_key)

	def process_event(self, doctype, docname, event_type, event_data):
		"""
		Process real-time events and update risk indicators

		Args:
			doctype: Document type
			docname: Document name
			event_type: Type of event (create, update, delete, etc.)
			event_data: Event data including changes
		"""
		try:
			# Check if this doctype is being monitored
			monitor_key = f"{doctype}:{docname}"
			if doctype not in self.active_monitors and monitor_key not in self.active_monitors:
				return

			# Get the controller for this doctype
			controller = self.controllers.get(doctype)
			if not controller:
				return

			# Process the event
			risk_updates = controller.process_event(docname, event_type, event_data)

			# Update risk indicators
			if risk_updates:
				self.update_risk_indicators(risk_updates)

			# Check for anomalies
			anomalies = self.detect_anomalies(doctype, docname, event_data)
			if anomalies:
				self.create_anomaly_alerts(anomalies, doctype, docname)

			# Update real-time assessments
			self.update_real_time_assessments(doctype, risk_updates)

		except Exception as e:
			frappe.log_error(f"Risk Event Processing Error: {str(e)}")

	def update_risk_indicators(self, risk_updates):
		"""Update risk indicators based on event data"""
		try:
			for update in risk_updates:
				indicator_name = update.get('indicator')
				if indicator_name in self.indicators:
					indicator_config = self.indicators[indicator_name]

					# Update indicator value
					new_value = update.get('value')
					if new_value is not None:
						self.update_indicator_value(indicator_name, new_value)

					# Check thresholds
					self.check_indicator_thresholds(indicator_name, new_value)

		except Exception as e:
			frappe.log_error(f"Risk Indicator Update Error: {str(e)}")

	def update_indicator_value(self, indicator_name, new_value):
		"""Update a risk indicator's current value"""
		try:
			indicator = frappe.get_doc("Risk Indicator", indicator_name)
			indicator.current_value = new_value
			indicator.last_updated = now()

			# Update historical data
			historical_data = indicator.get('historical_data', [])
			if isinstance(historical_data, str):
				historical_data = json.loads(historical_data)

			historical_data.append({
				'timestamp': now(),
				'value': new_value
			})

			# Keep only last 100 entries
			historical_data = historical_data[-100:]

			indicator.historical_data = json.dumps(historical_data)
			indicator.save()

			# Trigger real-time updates
			self.trigger_indicator_alerts(indicator)

		except Exception as e:
			frappe.log_error(f"Indicator Value Update Error: {str(e)}")

	def check_indicator_thresholds(self, indicator_name, value):
		"""Check if indicator value breaches thresholds"""
		try:
			indicator = frappe.get_doc("Risk Indicator", indicator_name)

			alert_triggered = False

			# Check upper threshold
			if (indicator.upper_threshold and
				value > indicator.upper_threshold and
				not indicator.upper_threshold_breached):

				indicator.upper_threshold_breached = 1
				alert_triggered = True

			# Check lower threshold
			if (indicator.lower_threshold and
				value < indicator.lower_threshold and
				not indicator.lower_threshold_breached):

				indicator.lower_threshold_breached = 1
				alert_triggered = True

			if alert_triggered:
				indicator.save()
				self.create_threshold_alert(indicator, value)

		except Exception as e:
			frappe.log_error(f"Threshold Check Error: {str(e)}")

	def trigger_indicator_alerts(self, indicator):
		"""Trigger alerts based on indicator custom triggers"""
		try:
			if indicator.custom_triggers:
				triggers = json.loads(indicator.custom_triggers)

				for trigger in triggers:
					if self.evaluate_trigger_condition(indicator, trigger):
						self.create_custom_trigger_alert(indicator, trigger)

		except Exception as e:
			frappe.log_error(f"Custom Trigger Alert Error: {str(e)}")

	def evaluate_trigger_condition(self, indicator, trigger):
		"""Evaluate custom trigger conditions"""
		try:
			condition = trigger.get('condition', '')
			threshold = trigger.get('threshold', 0)

			current_value = indicator.current_value or 0

			if '>' in condition:
				return current_value > threshold
			elif '<' in condition:
				return current_value < threshold
			elif '>=' in condition:
				return current_value >= threshold
			elif '<=' in condition:
				return current_value <= threshold

			return False

		except:
			return False

	def detect_anomalies(self, doctype, docname, event_data):
		"""Detect anomalies in event data"""
		try:
			# Prepare data for anomaly detection
			data_source = {
				'doctype': doctype,
				'docname': docname,
				'event_data': event_data,
				'timestamp': now()
			}

			# Use pattern recognition for event-based anomalies
			anomalies = anomaly_engine.detect_anomalies(
				data_source,
				'pattern_recognition',
				min_confidence=70.0
			)

			return anomalies

		except Exception as e:
			frappe.log_error(f"Anomaly Detection Error: {str(e)}")
			return []

	def create_anomaly_alerts(self, anomalies, doctype, docname):
		"""Create anomaly alerts for detected anomalies"""
		try:
			from mkaguzi.risk.doctype.anomaly_alert.anomaly_alert import create_anomaly_alert

			for anomaly in anomalies:
				alert_data = {
					'alert_type': f"{doctype} Anomaly",
					'severity': anomaly.get('severity', 'Medium'),
					'description': f"Anomaly detected in {doctype}: {anomaly.get('anomaly_type', 'unknown')}",
					'source_doctype': doctype,
					'source_document': docname,
					'detection_method': anomaly.get('detection_method', 'Pattern Recognition'),
					'confidence_score': anomaly.get('confidence_score', 75.0),
					'anomaly_details': anomaly
				}

				create_anomaly_alert(alert_data)

		except Exception as e:
			frappe.log_error(f"Anomaly Alert Creation Error: {str(e)}")

	def create_threshold_alert(self, indicator, value):
		"""Create alert for threshold breach"""
		try:
			from mkaguzi.risk.doctype.anomaly_alert.anomaly_alert import create_anomaly_alert

			severity = "High" if indicator.upper_threshold_breached else "Medium"

			alert_data = {
				'alert_type': 'Threshold Breach',
				'severity': severity,
				'description': f"Risk indicator {indicator.indicator_name} breached threshold. Value: {value}",
				'source_doctype': 'Risk Indicator',
				'source_document': indicator.name,
				'detection_method': 'Rule-based',
				'confidence_score': 95.0,
				'anomaly_details': {
					'indicator': indicator.indicator_name,
					'value': value,
					'upper_threshold': indicator.upper_threshold,
					'lower_threshold': indicator.lower_threshold
				}
			}

			create_anomaly_alert(alert_data)

		except Exception as e:
			frappe.log_error(f"Threshold Alert Creation Error: {str(e)}")

	def create_custom_trigger_alert(self, indicator, trigger):
		"""Create alert for custom trigger"""
		try:
			from mkaguzi.risk.doctype.anomaly_alert.anomaly_alert import create_anomaly_alert

			alert_data = {
				'alert_type': 'Custom Trigger',
				'severity': trigger.get('severity', 'Medium'),
				'description': f"Custom trigger activated for {indicator.indicator_name}: {trigger.get('description', '')}",
				'source_doctype': 'Risk Indicator',
				'source_document': indicator.name,
				'detection_method': 'Rule-based',
				'confidence_score': 90.0,
				'anomaly_details': {
					'indicator': indicator.indicator_name,
					'trigger': trigger,
					'value': indicator.current_value
				}
			}

			create_anomaly_alert(alert_data)

		except Exception as e:
			frappe.log_error(f"Custom Trigger Alert Creation Error: {str(e)}")

	def update_real_time_assessments(self, doctype, risk_updates):
		"""Update real-time risk assessments"""
		try:
			# Find active real-time assessments
			active_assessments = frappe.get_all('Risk Assessment',
				filters={
					'status': ['in', ['In Progress', 'Continuous Monitoring']],
					'assessment_type': ['in', ['Real-time', 'Predictive', 'Hybrid']]
				},
				fields=['name']
			)

			for assessment in active_assessments:
				try:
					assessment_doc = frappe.get_doc('Risk Assessment', assessment.name)

					# Trigger real-time assessment update
					from mkaguzi.risk.doctype.risk_assessment.risk_assessment import trigger_real_time_assessment
					trigger_real_time_assessment(assessment.name)

				except Exception as e:
					frappe.log_error(f"Real-time Assessment Update Error for {assessment.name}: {str(e)}")

		except Exception as e:
			frappe.log_error(f"Real-time Assessment Update Error: {str(e)}")

	def get_monitoring_status(self):
		"""Get current monitoring status"""
		return {
			'active_monitors': list(self.active_monitors),
			'registered_controllers': list(self.controllers.keys()),
			'registered_indicators': list(self.indicators.keys()),
			'total_monitors': len(self.active_monitors)
		}

	def schedule_batch_updates(self):
		"""Schedule batch updates for indicators and assessments"""
		try:
			# Update all active indicators
			active_indicators = frappe.get_all('Risk Indicator',
				filters={'monitoring_active': 1},
				fields=['name']
			)

			for indicator in active_indicators:
				try:
					self.update_indicator_batch(indicator.name)
				except Exception as e:
					frappe.log_error(f"Batch Indicator Update Error for {indicator.name}: {str(e)}")

			# Update continuous monitoring assessments
			continuous_assessments = frappe.get_all('Risk Assessment',
				filters={'status': 'Continuous Monitoring'},
				fields=['name']
			)

			for assessment in continuous_assessments:
				try:
					from mkaguzi.risk.doctype.risk_assessment.risk_assessment import trigger_real_time_assessment
					trigger_real_time_assessment(assessment.name)
				except Exception as e:
					frappe.log_error(f"Batch Assessment Update Error for {assessment.name}: {str(e)}")

		except Exception as e:
			frappe.log_error(f"Batch Update Scheduling Error: {str(e)}")

	def update_indicator_batch(self, indicator_name):
		"""Update indicator value in batch mode"""
		try:
			indicator = frappe.get_doc("Risk Indicator", indicator_name)

			# Calculate new value based on indicator type
			if indicator.calculation_method == "Count":
				new_value = self.calculate_count_indicator(indicator)
			elif indicator.calculation_method == "Sum":
				new_value = self.calculate_sum_indicator(indicator)
			elif indicator.calculation_method == "Average":
				new_value = self.calculate_average_indicator(indicator)
			else:
				return

			if new_value is not None:
				self.update_indicator_value(indicator_name, new_value)

		except Exception as e:
			frappe.log_error(f"Batch Indicator Update Error: {str(e)}")

	def calculate_count_indicator(self, indicator):
		"""Calculate count-based indicator"""
		try:
			if not indicator.source_doctype or not indicator.filter_criteria:
				return None

			filters = json.loads(indicator.filter_criteria)
			count = frappe.db.count(indicator.source_doctype, filters)

			return count

		except:
			return None

	def calculate_sum_indicator(self, indicator):
		"""Calculate sum-based indicator"""
		try:
			if not indicator.source_doctype or not indicator.value_field or not indicator.filter_criteria:
				return None

			filters = json.loads(indicator.filter_criteria)
			sum_value = frappe.db.sql(f"""
				SELECT SUM({indicator.value_field}) as total
				FROM `tab{indicator.source_doctype}`
				WHERE {self.build_filter_conditions(filters)}
			""", as_dict=True)

			return sum_value[0]['total'] if sum_value else 0

		except:
			return None

	def calculate_average_indicator(self, indicator):
		"""Calculate average-based indicator"""
		try:
			if not indicator.source_doctype or not indicator.value_field or not indicator.filter_criteria:
				return None

			filters = json.loads(indicator.filter_criteria)
			avg_value = frappe.db.sql(f"""
				SELECT AVG({indicator.value_field}) as average
				FROM `tab{indicator.source_doctype}`
				WHERE {self.build_filter_conditions(filters)}
			""", as_dict=True)

			return avg_value[0]['average'] if avg_value else 0

		except:
			return None

	def build_filter_conditions(self, filters):
		"""Build SQL filter conditions"""
		conditions = []
		for key, value in filters.items():
			if isinstance(value, str):
				conditions.append(f"{key} = '{value}'")
			else:
				conditions.append(f"{key} = {value}")
		return " AND ".join(conditions) if conditions else "1=1"


# Global synchronization manager instance
sync_manager = RiskSynchronizationManager()


def initialize_risk_monitoring():
	"""Initialize risk monitoring system"""
	try:
		# Register controllers for monitored doctypes
		from mkaguzi.controllers.financial_controller import FinancialController
		from mkaguzi.controllers.inventory_controller import InventoryController
		from mkaguzi.controllers.access_controller import AccessController
		from mkaguzi.controllers.hr_controller import HRController

		sync_manager.register_controller('Journal Entry', FinancialController())
		sync_manager.register_controller('Stock Entry', InventoryController())
		sync_manager.register_controller('User', AccessController())
		sync_manager.register_controller('Employee', HRController())

		# Register active risk indicators
		active_indicators = frappe.get_all('Risk Indicator',
			filters={'monitoring_active': 1},
			fields=['name', 'indicator_name', 'calculation_method', 'source_doctype', 'value_field', 'filter_criteria']
		)

		for indicator in active_indicators:
			config = {
				'calculation_method': indicator.calculation_method,
				'source_doctype': indicator.source_doctype,
				'value_field': indicator.value_field,
				'filter_criteria': indicator.filter_criteria
			}
			sync_manager.register_indicator(indicator.name, config)

		# Start monitoring for key doctypes
		monitored_doctypes = ['Journal Entry', 'Stock Entry', 'User', 'Employee']
		for doctype in monitored_doctypes:
			sync_manager.start_monitoring(doctype)

		frappe.logger().info("Risk monitoring system initialized successfully")

	except Exception as e:
		frappe.log_error(f"Risk Monitoring Initialization Error: {str(e)}")


@frappe.whitelist()
def process_audit_trail_event(docname, event_type, event_data=None):
	"""Process audit trail events for risk monitoring"""
	try:
		audit_entry = frappe.get_doc('Audit Trail Entry', docname)

		# Process the event through the sync manager
		sync_manager.process_event(
			audit_entry.source_doctype,
			audit_entry.source_document,
			event_type,
			{
				'audit_entry': audit_entry.name,
				'operation': audit_entry.operation,
				'changes': audit_entry.changes,
				'user': audit_entry.user,
				'risk_level': audit_entry.risk_level,
				'event_data': event_data
			}
		)

		return {'success': True}

	except Exception as e:
		frappe.log_error(f"Audit Trail Event Processing Error: {str(e)}")
		return {'success': False, 'error': str(e)}


@frappe.whitelist()
def get_monitoring_status():
	"""Get current risk monitoring status"""
	try:
		status = sync_manager.get_monitoring_status()

		# Add system health information
		status.update({
			'system_health': 'Active',
			'last_batch_update': frappe.db.get_single_value('System Settings', 'last_risk_batch_update'),
			'total_indicators': frappe.db.count('Risk Indicator'),
			'active_indicators': frappe.db.count('Risk Indicator', {'monitoring_active': 1}),
			'total_alerts_today': frappe.db.sql("""
				SELECT COUNT(*) as count
				FROM `tabAnomaly Alert`
				WHERE DATE(detected_date) = CURDATE()
			""", as_dict=True)[0]['count']
		})

		return status

	except Exception as e:
		frappe.log_error(f"Monitoring Status Error: {str(e)}")
		return {'error': str(e)}


@frappe.whitelist()
def trigger_batch_updates():
	"""Manually trigger batch updates for all indicators and assessments"""
	try:
		sync_manager.schedule_batch_updates()

		# Update last batch update timestamp
		frappe.db.set_single_value('System Settings', 'last_risk_batch_update', now())

		return {
			'success': True,
			'message': 'Batch updates completed successfully'
		}

	except Exception as e:
		frappe.log_error(f"Batch Update Trigger Error: {str(e)}")
		return {
			'success': False,
			'error': str(e)
		}


@frappe.whitelist()
def analyze_system_anomalies(time_window=7):
	"""Analyze system-wide anomalies over a time window"""
	try:
		from mkaguzi.risk.anomaly_detection_engine import analyze_audit_trail_anomalies

		# Analyze anomalies across all monitored doctypes
		results = {}

		monitored_doctypes = ['Journal Entry', 'Stock Entry', 'User', 'Employee']

		for doctype in monitored_doctypes:
			result = analyze_audit_trail_anomalies(
				doctype=doctype,
				time_window=time_window
			)
			results[doctype] = result

		# Generate system-wide summary
		total_anomalies = sum(len(result.get('anomalies', [])) for result in results.values())
		total_alerts = sum(len(result.get('alerts_created', [])) for result in results.values())

		return {
			'success': True,
			'summary': {
				'total_anomalies': total_anomalies,
				'total_alerts_created': total_alerts,
				'time_window_days': time_window,
				'analyzed_doctypes': monitored_doctypes
			},
			'details': results
		}

	except Exception as e:
		frappe.log_error(f"System Anomaly Analysis Error: {str(e)}")
		return {
			'success': False,
			'error': str(e)
		}