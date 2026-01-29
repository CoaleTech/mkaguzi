# -*- coding: utf-8 -*-
# Copyright (c) 2024, Coale Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, get_datetime, add_days, flt
import json
from datetime import datetime, timedelta


class RiskIndicator(Document):
	def validate(self):
		"""Validate the risk indicator"""
		self.validate_thresholds()
		self.validate_calculation_method()
		self.update_status_based_on_value()

	def validate_thresholds(self):
		"""Validate threshold values"""
		if self.threshold_value is not None and self.current_value is not None:
			# Basic threshold validation - can be enhanced based on indicator type
			pass

	def validate_calculation_method(self):
		"""Validate calculation method configuration"""
		if self.calculation_method == "Custom Formula" and not self.data_source:
			frappe.throw(_("Data Source is required for Custom Formula calculation method"))

	def update_status_based_on_value(self):
		"""Update status based on current value vs threshold"""
		if self.current_value is not None and self.threshold_value is not None:
			if self.indicator_type in ["Risk Metric", "Anomaly Detection"]:
				# For risk metrics, higher values indicate higher risk
				if self.current_value >= self.threshold_value:
					if self.current_value >= self.threshold_value * 1.5:
						self.status = "Critical"
					else:
						self.status = "Alert"
				else:
					self.status = "Active"
			else:
				# For KPIs and compliance scores, lower values might indicate issues
				if self.current_value <= self.threshold_value:
					if self.current_value <= self.threshold_value * 0.5:
						self.status = "Critical"
					else:
						self.status = "Alert"
				else:
					self.status = "Active"

	def calculate_next_check_date(self):
		"""Calculate next check date based on frequency"""
		if self.frequency and self.last_updated:
			frequency_map = {
				"Real-time": 0,
				"Hourly": 1/24,
				"Daily": 1,
				"Weekly": 7,
				"Monthly": 30
			}

			days = frequency_map.get(self.frequency, 1)
			self.next_check_date = add_days(self.last_updated, days)

	def update_value(self, new_value, update_timestamp=True):
		"""Update the current value and recalculate status"""
		old_value = self.current_value
		self.current_value = flt(new_value)

		if update_timestamp:
			self.last_updated = now()

		self.update_status_based_on_value()
		self.update_historical_data(old_value)
		self.calculate_next_check_date()
		self.save()

	def update_historical_data(self, old_value):
		"""Update historical data for trend analysis"""
		try:
			historical = []
			if self.historical_data:
				historical = json.loads(self.historical_data)

			# Keep last 30 data points
			historical.append({
				"timestamp": now(),
				"value": self.current_value,
				"old_value": old_value
			})

			if len(historical) > 30:
				historical = historical[-30:]

			self.historical_data = json.dumps(historical)
			self.update_trend_direction(historical)

		except Exception as e:
			frappe.log_error(f"Historical Data Update Error: {str(e)}")

	def update_trend_direction(self, historical_data):
		"""Update trend direction based on historical data"""
		if len(historical_data) < 3:
			self.trend_direction = "Stable"
			return

		# Simple trend analysis - compare first half with second half
		midpoint = len(historical_data) // 2
		first_half = [d['value'] for d in historical_data[:midpoint]]
		second_half = [d['value'] for d in historical_data[midpoint:]]

		if not first_half or not second_half:
			self.trend_direction = "Stable"
			return

		first_avg = sum(first_half) / len(first_half)
		second_avg = sum(second_half) / len(second_half)

		change_percent = ((second_avg - first_avg) / first_avg) * 100 if first_avg != 0 else 0

		if abs(change_percent) < 5:
			self.trend_direction = "Stable"
		elif change_percent > 10:
			self.trend_direction = "Declining" if self.indicator_type in ["Risk Metric", "Anomaly Detection"] else "Improving"
		elif change_percent < -10:
			self.trend_direction = "Improving" if self.indicator_type in ["Risk Metric", "Anomaly Detection"] else "Declining"
		else:
			self.trend_direction = "Volatile"

	def get_trend_analysis(self):
		"""Get trend analysis data"""
		if not self.historical_data:
			return {}

		try:
			historical = json.loads(self.historical_data)
			values = [d['value'] for d in historical]

			if not values:
				return {}

			return {
				"current_value": self.current_value,
				"average": sum(values) / len(values),
				"min": min(values),
				"max": max(values),
				"trend": self.trend_direction,
				"data_points": len(values),
				"volatility": self.calculate_volatility(values)
			}

		except Exception as e:
			frappe.log_error(f"Trend Analysis Error: {str(e)}")
			return {}

	def calculate_volatility(self, values):
		"""Calculate volatility (standard deviation)"""
		if len(values) < 2:
			return 0

		mean = sum(values) / len(values)
		variance = sum((x - mean) ** 2 for x in values) / len(values)
		return variance ** 0.5

	def should_trigger_alert(self):
		"""Check if this indicator should trigger an alert"""
		if self.status in ["Alert", "Critical"]:
			return True

		# Check custom alert triggers
		if self.alert_triggers:
			try:
				triggers = json.loads(self.alert_triggers)
				for trigger in triggers:
					if self.evaluate_trigger(trigger):
						return True
			except:
				pass

		return False

	def evaluate_trigger(self, trigger):
		"""Evaluate a custom alert trigger"""
		try:
			condition = trigger.get('condition', '')
			threshold = trigger.get('threshold', 0)
			operator = trigger.get('operator', '>')

			if condition == 'value':
				value = self.current_value
			elif condition == 'change':
				# Calculate recent change
				historical = json.loads(self.historical_data) if self.historical_data else []
				if len(historical) >= 2:
					value = historical[-1]['value'] - historical[-2]['value']
				else:
					value = 0
			else:
				return False

			if operator == '>':
				return value > threshold
			elif operator == '<':
				return value < threshold
			elif operator == '>=':
				return value >= threshold
			elif operator == '<=':
				return value <= threshold
			elif operator == '==':
				return value == threshold

		except Exception as e:
			frappe.log_error(f"Trigger Evaluation Error: {str(e)}")

		return False


@frappe.whitelist()
def calculate_indicator_value(indicator_name, data_source=None):
	"""Calculate indicator value based on data source"""
	try:
		indicator = frappe.get_doc('Risk Indicator', indicator_name)

		if indicator.calculation_method == "Custom Formula":
			# For custom formulas, we'd need a formula engine
			value = calculate_custom_formula(indicator, data_source)
		else:
			# Use predefined calculation methods
			value = calculate_standard_value(indicator, data_source)

		# Update the indicator
		indicator.update_value(value)

		return {
			'success': True,
			'value': value,
			'status': indicator.status
		}

	except Exception as e:
		frappe.log_error(f"Indicator Calculation Error: {str(e)}")
		return {
			'success': False,
			'error': str(e)
		}


def calculate_standard_value(indicator, data_source):
	"""Calculate value using standard methods"""
	# This would implement various calculation methods
	# For now, return a placeholder
	return 0


def calculate_custom_formula(indicator, data_source):
	"""Calculate value using custom formula"""
	# This would implement custom formula evaluation
	# For now, return a placeholder
	return 0


@frappe.whitelist()
def get_risk_dashboard_data(module=None):
	"""Get risk dashboard data for indicators"""
	try:
		filters = {}
		if module:
			filters['module'] = module

		indicators = frappe.get_all('Risk Indicator',
			filters=filters,
			fields=['indicator_name', 'module', 'current_value', 'status', 'trend_direction', 'indicator_type'])

		# Group by status
		status_summary = {}
		for indicator in indicators:
			status = indicator.status
			if status not in status_summary:
				status_summary[status] = 0
			status_summary[status] += 1

		# Group by module
		module_summary = {}
		for indicator in indicators:
			module_name = indicator.module
			if module_name not in module_summary:
				module_summary[module_name] = {'total': 0, 'alerts': 0, 'critical': 0}
			module_summary[module_name]['total'] += 1
			if indicator.status == 'Alert':
				module_summary[module_name]['alerts'] += 1
			if indicator.status == 'Critical':
				module_summary[module_name]['critical'] += 1

		return {
			'indicators': indicators,
			'status_summary': status_summary,
			'module_summary': module_summary,
			'total_indicators': len(indicators)
		}

	except Exception as e:
		frappe.log_error(f"Dashboard Data Error: {str(e)}")
		return {
			'error': str(e)
		}


@frappe.whitelist()
def bulk_update_indicators(indicator_ids, updates):
	"""Bulk update multiple indicators"""
	try:
		if isinstance(indicator_ids, str):
			indicator_ids = json.loads(indicator_ids)
		if isinstance(updates, str):
			updates = json.loads(updates)

		updated_count = 0
		for indicator_id in updates:
			if indicator_id in indicator_ids:
				indicator = frappe.get_doc('Risk Indicator', indicator_id)
				for field, value in updates[indicator_id].items():
					if hasattr(indicator, field):
						setattr(indicator, field, value)
				indicator.save()
				updated_count += 1

		return {'success': True, 'updated_count': updated_count}

	except Exception as e:
		frappe.log_error(f"Bulk Update Error: {str(e)}")
		frappe.throw(_("Failed to update indicators"))