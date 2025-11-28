# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class RiskAssessmentRegister(Document):
	def validate(self):
		self.calculate_risk_score()
		self.calculate_residual_risk()

	def calculate_risk_score(self):
		"""Calculate inherent risk score based on impact and likelihood"""
		if self.impact_score and self.likelihood_score:
			impact_score = self.impact_score
			likelihood_score = self.likelihood_score

			self.inherent_risk_score = impact_score * likelihood_score

			# Determine risk rating based on score
			if self.inherent_risk_score >= 16:
				self.inherent_risk_rating = "Very High"
			elif self.inherent_risk_score >= 12:
				self.inherent_risk_rating = "High"
			elif self.inherent_risk_score >= 8:
				self.inherent_risk_rating = "Medium"
			elif self.inherent_risk_score >= 4:
				self.inherent_risk_rating = "Low"
			else:
				self.inherent_risk_rating = "Very Low"

	def calculate_residual_risk(self):
		"""Calculate residual risk after considering control effectiveness"""
		if self.inherent_risk_score and self.control_effectiveness:
			effectiveness_multiplier = {
				"Very Effective": 0.2,
				"Effective": 0.4,
				"Partially Effective": 0.7,
				"Ineffective": 1.0
			}.get(self.control_effectiveness, 1.0)

			residual_score = self.inherent_risk_score * effectiveness_multiplier
			self.residual_risk_score = round(residual_score)

			# Determine residual risk rating
			if residual_score >= 12:
				self.residual_risk_rating = "Very High"
			elif residual_score >= 8:
				self.residual_risk_rating = "High"
			elif residual_score >= 4:
				self.residual_risk_rating = "Medium"
			elif residual_score >= 2:
				self.residual_risk_rating = "Low"
			else:
				self.residual_risk_rating = "Very Low"