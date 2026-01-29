# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, now, get_datetime, add_days
import json
import statistics
from datetime import datetime, timedelta


class RiskAssessment(Document):
	def validate(self):
		self.validate_assessment_id()
		self.calculate_overall_risk()
		self.calculate_real_time_risk_score()
		self.analyze_risk_trends()
		self.generate_heat_map_data()
		self.validate_approval_workflow()
		self.integrate_anomaly_alerts()
		self.update_ml_insights()

	def validate_assessment_id(self):
		"""Auto-generate assessment ID if not provided"""
		if not self.assessment_id:
			# Format: RA-{Year}-{Sequence}
			year = str(getdate().year)
			sequence = self.get_next_sequence()
			self.assessment_id = f"RA-{year}-{sequence:03d}"

	def get_next_sequence(self):
		"""Get next sequence number for assessment ID"""
		year = str(getdate().year)
		existing = frappe.db.sql("""
			SELECT assessment_id FROM `tabRisk Assessment`
			WHERE assessment_id LIKE %s
			ORDER BY assessment_id DESC LIMIT 1
		""", f"RA-%-{year}-%")

		if existing:
			last_id = existing[0][0]
			try:
				sequence = int(last_id.split('-')[-1])
				return sequence + 1
			except (ValueError, IndexError):
				pass
		return 1

	def calculate_overall_risk(self):
		"""Calculate overall risk rating and score from risk register"""
		if self.risk_register:
			total_score = 0
			risk_count = 0
			critical_count = 0
			high_count = 0

			for risk in self.risk_register:
				if risk.inherent_risk_score:
					total_score += risk.inherent_risk_score
					risk_count += 1

					if risk.inherent_risk_rating == "Very High":
						critical_count += 1
					elif risk.inherent_risk_rating == "High":
						high_count += 1

			if risk_count > 0:
				average_score = total_score / risk_count
				self.overall_risk_score = round(average_score)

				# Determine overall rating based on highest individual risk or average
				if critical_count > 0:
					self.overall_risk_rating = "Very High"
				elif high_count > 0 or average_score >= 12:
					self.overall_risk_rating = "High"
				elif average_score >= 8:
					self.overall_risk_rating = "Medium"
				else:
					self.overall_risk_rating = "Low"

	def calculate_real_time_risk_score(self):
		"""Calculate real-time risk score based on indicators and anomalies"""
		if self.assessment_type in ["Real-time", "Predictive", "Hybrid"]:
			base_score = self.overall_risk_score or 0

			# Factor in risk indicators
			indicator_score = self.get_risk_indicators_score()
			anomaly_score = self.get_anomaly_alerts_score()

			# Weighted calculation
			self.real_time_risk_score = round(
				(base_score * 0.4) + (indicator_score * 0.4) + (anomaly_score * 0.2)
			)

	def get_risk_indicators_score(self):
		"""Get risk score from associated indicators"""
		if not self.risk_indicators:
			return 0

		total_score = 0
		count = 0

		for indicator_link in self.risk_indicators:
			try:
				indicator = frappe.get_doc("Risk Indicator", indicator_link.risk_indicator)
				if indicator.current_value and indicator.upper_threshold:
					# Calculate deviation from threshold
					deviation = abs(indicator.current_value - indicator.upper_threshold)
					score = min(deviation * 2, 25)  # Max 25 points for indicators
					total_score += score
					count += 1
			except:
				continue

		return total_score / count if count > 0 else 0

	def get_anomaly_alerts_score(self):
		"""Get risk score from active anomaly alerts"""
		if not self.anomaly_alerts:
			return 0

		score = 0
		severity_weights = {
			"Low": 5,
			"Medium": 10,
			"High": 20,
			"Critical": 25
		}

		for alert_link in self.anomaly_alerts:
			try:
				alert = frappe.get_doc("Anomaly Alert", alert_link.anomaly_alert)
				if alert.status in ["Open", "Investigating"]:
					score += severity_weights.get(alert.severity, 5)
			except:
				continue

		return min(score, 25)  # Cap at 25 points

	def analyze_risk_trends(self):
		"""Analyze risk trend direction"""
		if self.assessment_type in ["Real-time", "Predictive", "Hybrid"]:
			# Get historical assessments for trend analysis
			historical_scores = self.get_historical_risk_scores()

			if len(historical_scores) >= 3:
				try:
					# Calculate trend using linear regression slope
					slope = self.calculate_trend_slope(historical_scores)

					if slope > 0.5:
						self.risk_trend_direction = "Deteriorating"
					elif slope < -0.5:
						self.risk_trend_direction = "Improving"
					else:
						self.risk_trend_direction = "Stable"
				except:
					self.risk_trend_direction = "Unknown"
			else:
				self.risk_trend_direction = "Unknown"

	def get_historical_risk_scores(self):
		"""Get historical risk scores for trend analysis"""
		scores = []

		# Get last 6 assessments
		historical = frappe.db.sql("""
			SELECT overall_risk_score, assessment_date
			FROM `tabRisk Assessment`
			WHERE fiscal_year = %s AND status = 'Approved'
			ORDER BY assessment_date DESC
			LIMIT 6
		""", (self.fiscal_year,), as_dict=True)

		for assessment in reversed(historical):  # Reverse to get chronological order
			if assessment.overall_risk_score:
				scores.append(assessment.overall_risk_score)

		return scores

	def calculate_trend_slope(self, scores):
		"""Calculate slope of risk score trend"""
		if len(scores) < 2:
			return 0

		x = list(range(len(scores)))
		y = scores

		# Simple linear regression slope calculation
		n = len(x)
		sum_x = sum(x)
		sum_y = sum(y)
		sum_xy = sum(xi * yi for xi, yi in zip(x, y))
		sum_xx = sum(xi * xi for xi in x)

		slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
		return slope

	def integrate_anomaly_alerts(self):
		"""Integrate active anomaly alerts into assessment"""
		if self.assessment_type in ["Real-time", "Predictive", "Hybrid"]:
			# Get recent anomaly alerts (last 30 days)
			recent_alerts = frappe.db.sql("""
				SELECT name, alert_type, severity, confidence_score
				FROM `tabAnomaly Alert`
				WHERE detected_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
				AND status IN ('Open', 'Investigating')
				ORDER BY detected_date DESC
			""", as_dict=True)

			# Clear existing anomaly alerts table
			self.set("anomaly_alerts", [])

			# Add recent alerts
			for alert in recent_alerts[:10]:  # Limit to top 10
				self.append("anomaly_alerts", {
					"anomaly_alert": alert.name,
					"alert_type": alert.alert_type,
					"severity": alert.severity,
					"confidence_score": alert.confidence_score
				})

	def update_ml_insights(self):
		"""Update machine learning insights"""
		if self.assessment_type in ["Predictive", "Hybrid"]:
			insights = self.generate_ml_insights()
			self.ml_insights = json.dumps(insights)

			forecasting = self.generate_risk_forecasting()
			self.risk_forecasting = json.dumps(forecasting)

	def generate_ml_insights(self):
		"""Generate machine learning insights"""
		insights = {
			"risk_patterns": [],
			"predictive_indicators": [],
			"anomaly_clusters": [],
			"confidence_level": 0.0,
			"generated_at": now()
		}

		try:
			# Analyze risk patterns
			patterns = self.analyze_risk_patterns()
			insights["risk_patterns"] = patterns

			# Identify predictive indicators
			predictors = self.identify_predictive_indicators()
			insights["predictive_indicators"] = predictors

			# Cluster anomalies
			clusters = self.cluster_anomalies()
			insights["anomaly_clusters"] = clusters

			# Calculate confidence
			insights["confidence_level"] = self.calculate_ml_confidence()

		except Exception as e:
			frappe.log_error(f"ML Insights Generation Error: {str(e)}")

		return insights

	def analyze_risk_patterns(self):
		"""Analyze risk patterns using statistical methods"""
		patterns = []

		try:
			# Get risk register data
			if self.risk_register:
				risk_scores = [r.inherent_risk_score for r in self.risk_register if r.inherent_risk_score]

				if len(risk_scores) >= 5:
					# Calculate statistical measures
					mean_score = statistics.mean(risk_scores)
					std_dev = statistics.stdev(risk_scores) if len(risk_scores) > 1 else 0

					patterns.append({
						"type": "distribution_analysis",
						"mean_risk_score": round(mean_score, 2),
						"standard_deviation": round(std_dev, 2),
						"risk_concentration": "High" if std_dev < 2 else "Medium" if std_dev < 5 else "Low"
					})

					# Identify outliers
					outliers = self.identify_outliers(risk_scores)
					if outliers:
						patterns.append({
							"type": "outlier_detection",
							"outlier_risks": len(outliers),
							"outlier_threshold": round(mean_score + 2 * std_dev, 2)
						})

		except Exception as e:
			frappe.log_error(f"Risk Pattern Analysis Error: {str(e)}")

		return patterns

	def identify_predictive_indicators(self):
		"""Identify predictive indicators from risk data"""
		indicators = []

		try:
			# Analyze correlation between risk indicators and risk scores
			if self.risk_indicators and self.risk_register:
				for indicator_link in self.risk_indicators:
					try:
						indicator = frappe.get_doc("Risk Indicator", indicator_link.risk_indicator)
						correlation = self.calculate_indicator_correlation(indicator)

						if correlation > 0.7:  # Strong correlation
							indicators.append({
								"indicator": indicator.indicator_name,
								"correlation": round(correlation, 3),
								"predictive_power": "High"
							})
						elif correlation > 0.5:
							indicators.append({
								"indicator": indicator.indicator_name,
								"correlation": round(correlation, 3),
								"predictive_power": "Medium"
							})
					except:
						continue

		except Exception as e:
			frappe.log_error(f"Predictive Indicator Analysis Error: {str(e)}")

		return indicators

	def cluster_anomalies(self):
		"""Cluster anomalies for pattern recognition"""
		clusters = []

		try:
			if self.anomaly_alerts:
				# Simple clustering by alert type and severity
				cluster_data = {}

				for alert_link in self.anomaly_alerts:
					try:
						alert = frappe.get_doc("Anomaly Alert", alert_link.anomaly_alert)
						key = f"{alert.alert_type}_{alert.severity}"

						if key not in cluster_data:
							cluster_data[key] = {
								"type": alert.alert_type,
								"severity": alert.severity,
								"count": 0,
								"alerts": []
							}

						cluster_data[key]["count"] += 1
						cluster_data[key]["alerts"].append(alert.alert_id)

					except:
						continue

				# Convert to clusters
				for cluster in cluster_data.values():
					if cluster["count"] >= 2:  # Only include clusters with multiple alerts
						clusters.append(cluster)

		except Exception as e:
			frappe.log_error(f"Anomaly Clustering Error: {str(e)}")

		return clusters

	def calculate_ml_confidence(self):
		"""Calculate confidence level for ML insights"""
		confidence = 0.0

		try:
			# Base confidence on data quality and quantity
			data_factors = 0

			if self.risk_register and len(self.risk_register) >= 5:
				data_factors += 0.3

			if self.risk_indicators and len(self.risk_indicators) >= 3:
				data_factors += 0.3

			if self.anomaly_alerts and len(self.anomaly_alerts) >= 5:
				data_factors += 0.2

			# Historical data factor
			historical_count = frappe.db.count("Risk Assessment",
				{"fiscal_year": self.fiscal_year, "status": "Approved"})
			if historical_count >= 3:
				data_factors += 0.2

			confidence = min(data_factors, 1.0)

		except Exception as e:
			frappe.log_error(f"ML Confidence Calculation Error: {str(e)}")

		return confidence

	def generate_risk_forecasting(self):
		"""Generate risk forecasting data"""
		forecasting = {
			"forecast_periods": [],
			"predicted_risk_scores": [],
			"confidence_intervals": [],
			"forecast_method": "linear_trend",
			"generated_at": now()
		}

		try:
			# Get historical data for forecasting
			historical_scores = self.get_historical_risk_scores()

			if len(historical_scores) >= 3:
				# Simple linear forecasting
				forecasts = self.generate_linear_forecast(historical_scores, periods=6)
				forecasting["predicted_risk_scores"] = forecasts

				# Generate forecast periods (next 6 months)
				base_date = get_datetime(self.assessment_date or now())
				for i in range(1, 7):
					forecast_date = add_days(base_date, i * 30)  # Monthly intervals
					forecasting["forecast_periods"].append(forecast_date.strftime("%Y-%m"))

				# Calculate confidence intervals
				forecasting["confidence_intervals"] = self.calculate_forecast_intervals(forecasts)

		except Exception as e:
			frappe.log_error(f"Risk Forecasting Error: {str(e)}")

		return forecasting

	def generate_linear_forecast(self, historical_scores, periods=6):
		"""Generate linear forecast from historical data"""
		if len(historical_scores) < 2:
			return [historical_scores[-1] if historical_scores else 10] * periods

		# Calculate trend
		slope = self.calculate_trend_slope(historical_scores)
		last_score = historical_scores[-1]

		forecasts = []
		for i in range(1, periods + 1):
			forecast = last_score + (slope * i)
			forecast = max(1, min(25, forecast))  # Bound between 1-25
			forecasts.append(round(forecast, 2))

		return forecasts

	def calculate_forecast_intervals(self, forecasts):
		"""Calculate confidence intervals for forecasts"""
		intervals = []
		for forecast in forecasts:
			# Simple interval calculation (±15% of forecast)
			margin = forecast * 0.15
			intervals.append({
				"lower": round(max(1, forecast - margin), 2),
				"upper": round(min(25, forecast + margin), 2)
			})
		return intervals

	def identify_outliers(self, scores):
		"""Identify outlier risk scores"""
		if len(scores) < 4:
			return []

		try:
			mean_score = statistics.mean(scores)
			std_dev = statistics.stdev(scores)

			outliers = []
			for i, score in enumerate(scores):
				if abs(score - mean_score) > 2 * std_dev:
					outliers.append({"index": i, "score": score, "deviation": abs(score - mean_score)})

			return outliers

		except:
			return []

	def calculate_indicator_correlation(self, indicator):
		"""Calculate correlation between indicator and risk scores"""
		try:
			# This is a simplified correlation calculation
			# In practice, you'd use more sophisticated statistical methods
			if not indicator.historical_data:
				return 0

			historical = json.loads(indicator.historical_data)
			values = [entry.get("value", 0) for entry in historical if entry.get("value")]

			if len(values) < 3:
				return 0

			# Get corresponding risk scores (simplified)
			risk_scores = [self.overall_risk_score] * len(values)

			# Calculate Pearson correlation coefficient
			return self.pearson_correlation(values, risk_scores)

		except:
			return 0

	def pearson_correlation(self, x, y):
		"""Calculate Pearson correlation coefficient"""
		try:
			n = len(x)
			if n != len(y) or n < 2:
				return 0

			sum_x = sum(x)
			sum_y = sum(y)
			sum_xy = sum(xi * yi for xi, yi in zip(x, y))
			sum_xx = sum(xi * xi for xi in x)
			sum_yy = sum(yi * yi for yi in y)

			numerator = n * sum_xy - sum_x * sum_y
			denominator = ((n * sum_xx - sum_x * sum_x) * (n * sum_yy - sum_y * sum_y)) ** 0.5

			if denominator == 0:
				return 0

			return numerator / denominator

		except:
			return 0

	def generate_heat_map_data(self):
		"""Generate JSON data for risk heat map visualization"""
		if self.risk_register:
			heat_map = {
				"categories": ["Very Low", "Low", "Medium", "High", "Very High"],
				"likelihood": ["Very Low", "Low", "Medium", "High", "Very High"],
				"data": []
			}

			# Initialize matrix
			matrix = {}
			for impact in heat_map["categories"]:
				matrix[impact] = {}
				for likelihood in heat_map["likelihood"]:
					matrix[impact][likelihood] = 0

			# Populate matrix with risk counts
			for risk in self.risk_register:
				impact = risk.inherent_risk_rating
				likelihood = self.get_likelihood_rating(risk.likelihood_score)
				if impact in matrix and likelihood in matrix[impact]:
					matrix[impact][likelihood] += 1

			# Convert to data points
			for impact in heat_map["categories"]:
				for likelihood in heat_map["likelihood"]:
					count = matrix[impact][likelihood]
					if count > 0:
						heat_map["data"].append({
							"impact": impact,
							"likelihood": likelihood,
							"count": count,
							"color": self.get_heat_map_color(impact, likelihood)
						})

			self.risk_heat_map_data = json.dumps(heat_map)

	def get_likelihood_rating(self, score):
		"""Convert likelihood score to rating"""
		if score == 1:
			return "Very Low"
		elif score == 2:
			return "Low"
		elif score == 3:
			return "Medium"
		elif score == 4:
			return "High"
		else:
			return "Very High"

	def get_heat_map_color(self, impact, likelihood):
		"""Get color code for heat map based on risk level"""
		impact_score = {"Very Low": 1, "Low": 2, "Medium": 3, "High": 4, "Very High": 5}.get(impact, 1)
		likelihood_score = {"Very Low": 1, "Low": 2, "Medium": 3, "High": 4, "Very High": 5}.get(likelihood, 1)

		risk_level = impact_score * likelihood_score

		if risk_level >= 16:
			return "#dc3545"  # Red - Very High
		elif risk_level >= 12:
			return "#fd7e14"  # Orange - High
		elif risk_level >= 6:
			return "#ffc107"  # Yellow - Medium
		else:
			return "#28a745"  # Green - Low

	def validate_approval_workflow(self):
		"""Validate approval workflow transitions"""
		if self.status == "Approved":
			if not self.approved_by:
				frappe.throw(_("Approved By is required when status is Approved"))
			if not self.approval_date:
				self.approval_date = getdate()
		elif self.status == "Rejected":
			if not self.approved_by:
				frappe.throw(_("Rejected By is required when status is Rejected"))

	def on_submit(self):
		"""Update status and perform post-submission actions"""
		if self.assessment_type in ["Real-time", "Continuous Monitoring"]:
			# Schedule continuous monitoring
			self.schedule_continuous_monitoring()

	def schedule_continuous_monitoring(self):
		"""Schedule continuous monitoring tasks"""
		try:
			# Create a scheduled task for continuous monitoring
			task_data = {
				"assessment": self.name,
				"frequency": "daily",
				"next_run": add_days(now(), 1),
				"active": 1
			}

			frappe.get_doc({
				"doctype": "Scheduled Task",
				"task_name": f"Continuous Risk Monitoring - {self.assessment_id}",
				"task_type": "Custom",
				"frequency": "Daily",
				"next_execution": add_days(now(), 1),
				"task_data": json.dumps(task_data)
			}).insert()

		except Exception as e:
			frappe.log_error(f"Continuous Monitoring Scheduling Error: {str(e)}")


@frappe.whitelist()
def get_risk_heat_map(assessment_id):
	"""Get heat map data for a specific assessment"""
	assessment = frappe.get_doc("Risk Assessment", assessment_id)
	return assessment.risk_heat_map_data


@frappe.whitelist()
def get_risk_trends(limit=12):
	"""Get risk trend data for dashboard"""
	data = frappe.db.sql("""
		SELECT
			assessment_date,
			overall_risk_score,
			overall_risk_rating,
			real_time_risk_score,
			risk_trend_direction
		FROM `tabRisk Assessment`
		WHERE status = 'Approved'
		ORDER BY assessment_date DESC
		LIMIT %s
	""", (limit,), as_dict=True)

	return data


@frappe.whitelist()
def get_ml_insights(assessment_id):
	"""Get ML insights for a specific assessment"""
	assessment = frappe.get_doc("Risk Assessment", assessment_id)
	return assessment.ml_insights


@frappe.whitelist()
def get_risk_forecasting(assessment_id):
	"""Get risk forecasting data for a specific assessment"""
	assessment = frappe.get_doc("Risk Assessment", assessment_id)
	return assessment.risk_forecasting


@frappe.whitelist()
def trigger_real_time_assessment(assessment_id):
	"""Trigger real-time risk assessment update"""
	try:
		assessment = frappe.get_doc("Risk Assessment", assessment_id)

		# Update real-time components
		assessment.calculate_real_time_risk_score()
		assessment.analyze_risk_trends()
		assessment.integrate_anomaly_alerts()
		assessment.update_ml_insights()

		assessment.save()
		frappe.db.commit()

		return {
			"success": True,
			"real_time_score": assessment.real_time_risk_score,
			"trend_direction": assessment.risk_trend_direction
		}

	except Exception as e:
		frappe.log_error(f"Real-time Assessment Trigger Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def get_assessment_dashboard_data(assessment_id):
	"""Get comprehensive dashboard data for assessment"""
	try:
		assessment = frappe.get_doc("Risk Assessment", assessment_id)

		dashboard_data = {
			"assessment_info": {
				"id": assessment.assessment_id,
				"name": assessment.assessment_name,
				"type": assessment.assessment_type,
				"status": assessment.status,
				"overall_score": assessment.overall_risk_score,
				"real_time_score": assessment.real_time_risk_score,
				"trend_direction": assessment.risk_trend_direction
			},
			"risk_indicators": [],
			"anomaly_alerts": [],
			"ml_insights": json.loads(assessment.ml_insights or "{}"),
			"forecasting": json.loads(assessment.risk_forecasting or "{}")
		}

		# Get risk indicators data
		if assessment.risk_indicators:
			for indicator_link in assessment.risk_indicators:
				try:
					indicator = frappe.get_doc("Risk Indicator", indicator_link.risk_indicator)
					dashboard_data["risk_indicators"].append({
						"name": indicator.indicator_name,
						"current_value": indicator.current_value,
						"threshold": indicator.upper_threshold,
						"status": "Normal" if indicator.current_value <= indicator.upper_threshold else "Alert"
					})
				except:
					continue

		# Get anomaly alerts data
		if assessment.anomaly_alerts:
			for alert_link in assessment.anomaly_alerts:
				try:
					alert = frappe.get_doc("Anomaly Alert", alert_link.anomaly_alert)
					dashboard_data["anomaly_alerts"].append({
						"id": alert.alert_id,
						"type": alert.alert_type,
						"severity": alert.severity,
						"status": alert.status,
						"detected_date": alert.detected_date
					})
				except:
					continue

		return dashboard_data

	except Exception as e:
		frappe.log_error(f"Assessment Dashboard Data Error: {str(e)}")
		return {
			"error": str(e)
		}