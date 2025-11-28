# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate
import json

class RiskAssessment(Document):
	def validate(self):
		self.validate_assessment_id()
		self.calculate_overall_risk()
		self.generate_heat_map_data()
		self.validate_approval_workflow()

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
		pass

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
			overall_risk_rating
		FROM `tabRisk Assessment`
		WHERE status = 'Approved'
		ORDER BY assessment_date DESC
		LIMIT %s
	""", (limit,), as_dict=True)

	return data