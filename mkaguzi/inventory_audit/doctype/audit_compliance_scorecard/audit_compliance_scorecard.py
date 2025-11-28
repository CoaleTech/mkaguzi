# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate


class AuditComplianceScorecard(Document):
	def validate(self):
		self.calculate_overall_score()
		self.determine_grade()
		self.determine_trend()

	def calculate_overall_score(self):
		# Weighted average of all metrics
		weights = {
			'completion_rate': 0.25,
			'timeliness_score': 0.20,
			'accuracy_score': 0.25,
			'sla_compliance_rate': 0.15,
			'variance_rate': 0.15  # Lower variance is better
		}

		total_score = 0
		total_weight = 0

		if self.completion_rate is not None:
			total_score += (self.completion_rate or 0) * weights['completion_rate']
			total_weight += weights['completion_rate']

		if self.timeliness_score is not None:
			total_score += (self.timeliness_score or 0) * weights['timeliness_score']
			total_weight += weights['timeliness_score']

		if self.accuracy_score is not None:
			total_score += (self.accuracy_score or 0) * weights['accuracy_score']
			total_weight += weights['accuracy_score']

		if self.sla_compliance_rate is not None:
			total_score += (self.sla_compliance_rate or 0) * weights['sla_compliance_rate']
			total_weight += weights['sla_compliance_rate']

		if self.variance_rate is not None:
			# Invert variance rate (lower is better)
			variance_score = max(0, 100 - (self.variance_rate or 0))
			total_score += variance_score * weights['variance_rate']
			total_weight += weights['variance_rate']

		if total_weight > 0:
			self.overall_score = total_score / total_weight
		else:
			self.overall_score = 0

	def determine_grade(self):
		score = self.overall_score or 0
		if score >= 90:
			self.grade = "A"
		elif score >= 80:
			self.grade = "B"
		elif score >= 70:
			self.grade = "C"
		elif score >= 60:
			self.grade = "D"
		else:
			self.grade = "F"

	def determine_trend(self):
		if self.previous_score:
			diff = (self.overall_score or 0) - self.previous_score
			if diff > 2:
				self.trend = "Improving"
			elif diff < -2:
				self.trend = "Declining"
			else:
				self.trend = "Stable"
		else:
			self.trend = "Stable"

	def before_save(self):
		# Create history snapshot
		if not self.is_new():
			self.create_history_snapshot()

	def create_history_snapshot(self):
		"""Create a historical snapshot of the scorecard"""
		history = frappe.new_doc("Scorecard History")
		history.scorecard = self.name
		history.snapshot_date = nowdate()
		history.completion_rate = self.completion_rate
		history.variance_rate = self.variance_rate
		history.material_variance_count = self.material_variance_count
		history.timeliness_score = self.timeliness_score
		history.accuracy_score = self.accuracy_score
		history.sla_compliance_rate = self.sla_compliance_rate
		history.overall_score = self.overall_score
		history.grade = self.grade
		history.insert(ignore_permissions=True)
