# -*- coding: utf-8 -*-
# Copyright (c) 2024, Coale Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import now, get_datetime, add_days
import json
import statistics
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, Counter


class AnomalyDetectionEngine:
	"""Advanced anomaly detection engine for real-time risk monitoring"""

	def __init__(self):
		self.detection_methods = {
			'statistical': self.statistical_anomaly_detection,
			'pattern_recognition': self.pattern_recognition_detection,
			'machine_learning': self.machine_learning_detection,
			'rule_based': self.rule_based_detection
		}

	def detect_anomalies(self, data_source, detection_method='statistical', **kwargs):
		"""
		Main anomaly detection method

		Args:
			data_source: Source data for analysis (dict, list, or doctype data)
			detection_method: Detection algorithm to use
			**kwargs: Additional parameters for detection

		Returns:
			List of detected anomalies
		"""
		try:
			if detection_method not in self.detection_methods:
				frappe.throw(f"Unknown detection method: {detection_method}")

			detection_function = self.detection_methods[detection_method]
			anomalies = detection_function(data_source, **kwargs)

			# Filter and score anomalies
			filtered_anomalies = self.filter_anomalies(anomalies, **kwargs)

			return filtered_anomalies

		except Exception as e:
			frappe.log_error(f"Anomaly Detection Error: {str(e)}")
			return []

	def statistical_anomaly_detection(self, data_source, **kwargs):
		"""
		Statistical anomaly detection using Z-score and modified Z-score methods
		"""
		anomalies = []

		try:
			# Extract numerical data
			if isinstance(data_source, dict) and 'values' in data_source:
				values = data_source['values']
			elif isinstance(data_source, list):
				values = [item.get('value', 0) for item in data_source if isinstance(item, dict)]
			else:
				return anomalies

			if len(values) < 5:  # Need minimum data points
				return anomalies

			# Calculate Z-scores
			mean_val = statistics.mean(values)
			std_dev = statistics.stdev(values) if len(values) > 1 else 0

			if std_dev == 0:
				return anomalies

			z_scores = [(val - mean_val) / std_dev for val in values]

			# Calculate modified Z-scores (more robust to outliers)
			median_val = statistics.median(values)
			mad = statistics.median([abs(val - median_val) for val in values])
			modified_z_scores = []

			for val in values:
				if mad == 0:
					modified_z_scores.append(0)
				else:
					modified_z_scores.append(0.6745 * (val - median_val) / mad)

			# Detect anomalies (Z-score > 3 or modified Z-score > 3.5)
			threshold = kwargs.get('z_threshold', 3.0)
			modified_threshold = kwargs.get('modified_z_threshold', 3.5)

			for i, (val, z_score, mod_z_score) in enumerate(zip(values, z_scores, modified_z_scores)):
				if abs(z_score) > threshold or abs(mod_z_score) > modified_threshold:
					anomaly = {
						'index': i,
						'value': val,
						'expected_value': mean_val,
						'z_score': z_score,
						'modified_z_score': mod_z_score,
						'deviation': abs(val - mean_val),
						'confidence_score': min(95.0, 50 + abs(z_score) * 10),
						'detection_method': 'Statistical',
						'anomaly_type': 'outlier',
						'severity': self.calculate_severity(abs(z_score), abs(mod_z_score))
					}
					anomalies.append(anomaly)

		except Exception as e:
			frappe.log_error(f"Statistical Anomaly Detection Error: {str(e)}")

		return anomalies

	def pattern_recognition_detection(self, data_source, **kwargs):
		"""
		Pattern recognition anomaly detection using time series analysis
		"""
		anomalies = []

		try:
			# Extract time series data
			if isinstance(data_source, dict) and 'time_series' in data_source:
				time_series = data_source['time_series']
			elif isinstance(data_source, list) and len(data_source) > 0:
				# Assume list of dicts with timestamp and value
				time_series = sorted(data_source, key=lambda x: x.get('timestamp', ''))
			else:
				return anomalies

			if len(time_series) < 10:  # Need sufficient historical data
				return anomalies

			values = [item.get('value', 0) for item in time_series]

			# Calculate moving averages and standard deviations
			window_size = min(7, len(values) // 3)  # Adaptive window size
			moving_avg = self.calculate_moving_average(values, window_size)
			moving_std = self.calculate_moving_std(values, window_size)

			# Detect pattern anomalies
			for i in range(window_size, len(values)):
				current_val = values[i]
				expected_val = moving_avg[i - window_size]
				expected_std = moving_std[i - window_size]

				if expected_std > 0:
					z_score = (current_val - expected_val) / expected_std

					if abs(z_score) > 2.5:  # Pattern deviation threshold
						anomaly = {
							'index': i,
							'value': current_val,
							'expected_value': expected_val,
							'z_score': z_score,
							'deviation': abs(current_val - expected_val),
							'confidence_score': min(90.0, 60 + abs(z_score) * 8),
							'detection_method': 'Pattern Recognition',
							'anomaly_type': 'pattern_deviation',
							'severity': self.calculate_severity(abs(z_score), 0),
							'pattern_context': {
								'moving_average': expected_val,
								'moving_std': expected_std,
								'window_size': window_size
							}
						}
						anomalies.append(anomaly)

			# Detect seasonal anomalies if enough data
			if len(time_series) >= 30:
				seasonal_anomalies = self.detect_seasonal_anomalies(time_series)
				anomalies.extend(seasonal_anomalies)

		except Exception as e:
			frappe.log_error(f"Pattern Recognition Detection Error: {str(e)}")

		return anomalies

	def machine_learning_detection(self, data_source, **kwargs):
		"""
		Machine learning based anomaly detection using Isolation Forest concept
		"""
		anomalies = []

		try:
			# Simplified ML-based detection (Isolation Forest inspired)
			if isinstance(data_source, dict) and 'features' in data_source:
				features = data_source['features']
			elif isinstance(data_source, list):
				# Extract features from data
				features = self.extract_features(data_source)
			else:
				return anomalies

			if len(features) < 10:
				return anomalies

			# Calculate anomaly scores using simplified isolation forest approach
			anomaly_scores = self.isolation_forest_scoring(features)

			# Threshold for anomaly detection
			threshold = kwargs.get('ml_threshold', 0.6)

			for i, score in enumerate(anomaly_scores):
				if score > threshold:
					anomaly = {
						'index': i,
						'value': features[i] if isinstance(features[i], (int, float)) else features[i].get('value', 0),
						'anomaly_score': score,
						'confidence_score': min(85.0, 50 + score * 35),
						'detection_method': 'Machine Learning',
						'anomaly_type': 'ml_detected',
						'severity': 'High' if score > 0.8 else 'Medium' if score > 0.7 else 'Low',
						'ml_features': features[i] if isinstance(features[i], dict) else {}
					}
					anomalies.append(anomaly)

		except Exception as e:
			frappe.log_error(f"Machine Learning Detection Error: {str(e)}")

		return anomalies

	def rule_based_detection(self, data_source, **kwargs):
		"""
		Rule-based anomaly detection using predefined business rules
		"""
		anomalies = []

		try:
			rules = kwargs.get('rules', self.get_default_rules())

			if isinstance(data_source, dict):
				data = data_source
			else:
				return anomalies

			for rule in rules:
				rule_anomalies = self.apply_rule(data, rule)
				anomalies.extend(rule_anomalies)

		except Exception as e:
			frappe.log_error(f"Rule-based Detection Error: {str(e)}")

		return anomalies

	def filter_anomalies(self, anomalies, **kwargs):
		"""
		Filter and prioritize detected anomalies
		"""
		if not anomalies:
			return []

		# Remove duplicates based on index and value proximity
		filtered = []
		seen_indices = set()

		for anomaly in sorted(anomalies, key=lambda x: x.get('confidence_score', 0), reverse=True):
			index = anomaly.get('index')
			if index not in seen_indices:
				filtered.append(anomaly)
				seen_indices.add(index)

		# Apply minimum confidence threshold
		min_confidence = kwargs.get('min_confidence', 60.0)
		filtered = [a for a in filtered if a.get('confidence_score', 0) >= min_confidence]

		# Limit number of anomalies
		max_anomalies = kwargs.get('max_anomalies', 10)
		filtered = filtered[:max_anomalies]

		return filtered

	def calculate_severity(self, z_score, modified_z_score):
		"""Calculate anomaly severity based on statistical measures"""
		max_z = max(abs(z_score), abs(modified_z_score))

		if max_z >= 5.0:
			return "Critical"
		elif max_z >= 3.5:
			return "High"
		elif max_z >= 2.5:
			return "Medium"
		else:
			return "Low"

	def calculate_moving_average(self, values, window_size):
		"""Calculate moving average"""
		moving_avg = []
		for i in range(len(values)):
			start = max(0, i - window_size + 1)
			window = values[start:i + 1]
			moving_avg.append(sum(window) / len(window))
		return moving_avg

	def calculate_moving_std(self, values, window_size):
		"""Calculate moving standard deviation"""
		moving_std = []
		for i in range(len(values)):
			start = max(0, i - window_size + 1)
			window = values[start:i + 1]
			if len(window) > 1:
				std = statistics.stdev(window)
			else:
				std = 0
			moving_std.append(std)
		return moving_std

	def detect_seasonal_anomalies(self, time_series):
		"""Detect seasonal pattern anomalies"""
		anomalies = []

		try:
			# Group by day of week or month
			values_by_period = defaultdict(list)

			for item in time_series:
				timestamp = item.get('timestamp')
				if timestamp:
					try:
						dt = get_datetime(timestamp)
						period = dt.weekday()  # Day of week (0-6)
						values_by_period[period].append(item.get('value', 0))
					except:
						continue

			# Calculate expected values for each period
			period_stats = {}
			for period, values in values_by_period.items():
				if len(values) >= 3:
					period_stats[period] = {
						'mean': statistics.mean(values),
						'std': statistics.stdev(values) if len(values) > 1 else 0
					}

			# Check recent values against seasonal expectations
			if time_series:
				recent_item = time_series[-1]
				timestamp = recent_item.get('timestamp')
				if timestamp:
					try:
						dt = get_datetime(timestamp)
						period = dt.weekday()

						if period in period_stats:
							current_val = recent_item.get('value', 0)
							expected = period_stats[period]['mean']
							expected_std = period_stats[period]['std']

							if expected_std > 0:
								z_score = (current_val - expected) / expected_std

								if abs(z_score) > 2.0:  # Seasonal anomaly threshold
									anomaly = {
										'index': len(time_series) - 1,
										'value': current_val,
										'expected_value': expected,
										'z_score': z_score,
										'deviation': abs(current_val - expected),
										'confidence_score': min(80.0, 55 + abs(z_score) * 7),
										'detection_method': 'Pattern Recognition',
										'anomaly_type': 'seasonal_anomaly',
										'severity': self.calculate_severity(abs(z_score), 0),
										'seasonal_context': {
											'period': period,
											'expected_mean': expected,
											'expected_std': expected_std
										}
									}
									anomalies.append(anomaly)
					except:
						pass

		except Exception as e:
			frappe.log_error(f"Seasonal Anomaly Detection Error: {str(e)}")

		return anomalies

	def isolation_forest_scoring(self, features):
		"""Simplified isolation forest anomaly scoring"""
		scores = []

		try:
			# Convert features to numerical values for scoring
			if isinstance(features[0], dict):
				# Extract numerical features
				numerical_features = []
				for feature in features:
					if 'value' in feature:
						numerical_features.append(feature['value'])
					else:
						# Use first numerical value found
						numerical_vals = [v for v in feature.values() if isinstance(v, (int, float))]
						numerical_features.append(numerical_vals[0] if numerical_vals else 0)
				values = numerical_features
			else:
				values = features

			# Calculate anomaly scores based on isolation principles
			for i, val in enumerate(values):
				# Simplified scoring: distance from median and uniqueness
				median_val = statistics.median(values)
				mad = statistics.median([abs(v - median_val) for v in values])

				if mad == 0:
					score = 0.5  # Neutral score
				else:
					# Modified Z-score for anomaly scoring
					mod_z = 0.6745 * (val - median_val) / mad
					score = min(1.0, abs(mod_z) / 3.5)  # Normalize to 0-1

				scores.append(score)

		except Exception as e:
			frappe.log_error(f"Isolation Forest Scoring Error: {str(e)}")
			scores = [0.5] * len(features)  # Default neutral scores

		return scores

	def extract_features(self, data):
		"""Extract features from raw data for ML analysis"""
		features = []

		try:
			for item in data:
				if isinstance(item, dict):
					feature = {
						'value': item.get('value', 0),
						'timestamp': item.get('timestamp'),
						'category': item.get('category', 'unknown'),
						'source': item.get('source', 'unknown')
					}
					features.append(feature)
				else:
					features.append({'value': item})

		except Exception as e:
			frappe.log_error(f"Feature Extraction Error: {str(e)}")

		return features

	def apply_rule(self, data, rule):
		"""Apply a single rule for anomaly detection"""
		anomalies = []

		try:
			field = rule.get('field')
			operator = rule.get('operator')
			threshold = rule.get('threshold')
			severity = rule.get('severity', 'Medium')

			if not all([field, operator, threshold is not None]):
				return anomalies

			value = self.get_nested_value(data, field)

			if value is None:
				return anomalies

			is_anomaly = self.evaluate_condition(value, operator, threshold)

			if is_anomaly:
				anomaly = {
					'field': field,
					'value': value,
					'expected_value': threshold,
					'rule': rule.get('name', 'Custom Rule'),
					'confidence_score': 95.0,  # Rule-based detection is highly confident
					'detection_method': 'Rule-based',
					'anomaly_type': 'rule_violation',
					'severity': severity
				}
				anomalies.append(anomaly)

		except Exception as e:
			frappe.log_error(f"Rule Application Error: {str(e)}")

		return anomalies

	def get_default_rules(self):
		"""Get default business rules for anomaly detection"""
		return [
			{
				'name': 'High Value Transaction',
				'field': 'amount',
				'operator': '>',
				'threshold': 10000,
				'severity': 'High'
			},
			{
				'name': 'Unusual Frequency',
				'field': 'frequency',
				'operator': '>',
				'threshold': 100,
				'severity': 'Medium'
			},
			{
				'name': 'Negative Value',
				'field': 'value',
				'operator': '<',
				'threshold': 0,
				'severity': 'High'
			}
		]

	def get_nested_value(self, data, field_path):
		"""Get value from nested dictionary using dot notation"""
		try:
			keys = field_path.split('.')
			value = data
			for key in keys:
				if isinstance(value, dict):
					value = value.get(key)
				else:
					return None
			return value
		except:
			return None

	def evaluate_condition(self, value, operator, threshold):
		"""Evaluate condition based on operator"""
		try:
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
			elif operator == '!=':
				return value != threshold
			else:
				return False
		except:
			return False


# Global anomaly detection engine instance
anomaly_engine = AnomalyDetectionEngine()


@frappe.whitelist()
def detect_anomalies_api(data_source, detection_method='statistical', **kwargs):
	"""API endpoint for anomaly detection"""
	try:
		if isinstance(data_source, str):
			data_source = json.loads(data_source)

		if isinstance(kwargs, str):
			kwargs = json.loads(kwargs)

		anomalies = anomaly_engine.detect_anomalies(data_source, detection_method, **kwargs)

		return {
			'success': True,
			'anomalies': anomalies,
			'count': len(anomalies),
			'detection_method': detection_method
		}

	except Exception as e:
		frappe.log_error(f"Anomaly Detection API Error: {str(e)}")
		return {
			'success': False,
			'error': str(e)
		}


@frappe.whitelist()
def analyze_audit_trail_anomalies(doctype=None, docname=None, time_window=30):
	"""Analyze audit trail data for anomalies"""
	try:
		# Get audit trail data
		filters = {}
		if doctype:
			filters['source_doctype'] = doctype
		if docname:
			filters['source_document'] = docname

		# Get data from last N days
		start_date = add_days(now(), -time_window)

		audit_entries = frappe.get_all('Audit Trail Entry',
			filters=filters,
			fields=['name', 'timestamp', 'operation', 'user', 'risk_level', 'source_doctype', 'source_document'],
			order_by='timestamp desc',
			limit=1000
		)

		if not audit_entries:
			return {'anomalies': [], 'message': 'No audit trail data found'}

		# Prepare data for anomaly detection
		time_series_data = []
		for entry in audit_entries:
			time_series_data.append({
				'timestamp': entry.timestamp,
				'value': entry.risk_level or 1,  # Use risk level as value
				'operation': entry.operation,
				'user': entry.user,
				'doctype': entry.source_doctype
			})

		data_source = {
			'time_series': time_series_data,
			'values': [item['value'] for item in time_series_data]
		}

		# Detect anomalies
		anomalies = anomaly_engine.detect_anomalies(data_source, 'pattern_recognition')

		# Create anomaly alerts for detected anomalies
		alerts_created = []
		for anomaly in anomalies:
			if anomaly.get('confidence_score', 0) >= 70:  # High confidence threshold
				alert_data = {
					'alert_type': 'Audit Trail Anomaly',
					'severity': anomaly.get('severity', 'Medium'),
					'description': f"Anomalous activity detected in audit trail: {anomaly.get('anomaly_type', 'unknown')}",
					'source_doctype': doctype or 'Audit Trail',
					'source_document': docname,
					'detection_method': anomaly.get('detection_method', 'Pattern Recognition'),
					'confidence_score': anomaly.get('confidence_score', 75.0),
					'anomaly_details': anomaly
				}

				alert = create_anomaly_alert(alert_data)
				if alert.get('success'):
					alerts_created.append(alert)

		return {
			'success': True,
			'anomalies': anomalies,
			'alerts_created': alerts_created,
			'analyzed_records': len(audit_entries)
		}

	except Exception as e:
		frappe.log_error(f"Audit Trail Anomaly Analysis Error: {str(e)}")
		return {
			'success': False,
			'error': str(e)
		}


@frappe.whitelist()
def create_anomaly_alert(alert_data):
	"""Create anomaly alert from detection results"""
	try:
		from mkaguzi.risk.doctype.anomaly_alert.anomaly_alert import create_anomaly_alert
		return create_anomaly_alert(alert_data)
	except Exception as e:
		frappe.log_error(f"Anomaly Alert Creation Error: {str(e)}")
		return {'success': False, 'error': str(e)}