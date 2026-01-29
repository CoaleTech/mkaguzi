# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, getdate
from datetime import datetime

class AuditUniverse(Document):
	def validate(self):
		self.validate_universe_id()
		self.calculate_residual_risk()
		self.calculate_next_scheduled_audit()
		self.validate_risk_factors()
		self.validate_key_controls()

	def validate_universe_id(self):
		"""Ensure universe ID is unique and follows naming convention"""
		if not self.universe_id:
			# Auto-generate universe ID if not provided
			entity_type_code = {
				"Process": "PROC",
				"Function": "FUNC",
				"Department": "DEPT",
				"Location": "LOC",
				"System": "SYS",
				"Compliance Area": "COMP"
			}.get(self.entity_type, "GEN")

			# Get next sequence number
			existing_count = frappe.db.count("Audit Universe", {"entity_type": self.entity_type})
			sequence = str(existing_count + 1).zfill(3)

			self.universe_id = f"{entity_type_code}-{sequence}"

	def calculate_residual_risk(self):
		"""Calculate residual risk based on inherent risk and control effectiveness"""
		if self.inherent_risk_score and self.control_effectiveness_score:
			# Residual risk = Inherent risk - Control effectiveness
			residual_score = self.inherent_risk_score - self.control_effectiveness_score

			# Ensure residual score doesn't go below 1
			residual_score = max(1, residual_score)

			self.residual_risk_score = residual_score

			# Determine residual risk rating based on score
			if residual_score >= 15:
				self.residual_risk_rating = "Critical"
			elif residual_score >= 10:
				self.residual_risk_rating = "High"
			elif residual_score >= 5:
				self.residual_risk_rating = "Medium"
			else:
				self.residual_risk_rating = "Low"

	def calculate_next_scheduled_audit(self):
		"""Calculate next scheduled audit date based on frequency and last audit date"""
		if self.audit_frequency and self.last_audit_date:
			frequency_days = {
				"Quarterly": 90,
				"Semi-Annual": 180,
				"Annual": 365,
				"Bi-Annual": 730,
				"Tri-Annual": 1095
			}

			days = frequency_days.get(self.audit_frequency)
			if days:
				self.next_scheduled_audit = add_days(self.last_audit_date, days)

	def validate_risk_factors(self):
		"""Validate risk factors table"""
		if self.risk_factors:
			total_weight = sum([factor.risk_weight for factor in self.risk_factors if factor.risk_weight])
			if total_weight > 100:
				frappe.throw(_("Total risk factor weights cannot exceed 100%"))

			# Calculate inherent risk score from risk factors
			if self.risk_factors:
				inherent_score = 0
				for factor in self.risk_factors:
					if factor.risk_impact and factor.risk_likelihood:
						impact_score = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}.get(factor.risk_impact, 1)
						likelihood_score = {"Low": 1, "Medium": 2, "High": 3, "Very High": 4}.get(factor.risk_likelihood, 1)
						factor_score = impact_score * likelihood_score
						weighted_score = factor_score * (factor.risk_weight / 100) if factor.risk_weight else factor_score
						inherent_score += weighted_score

				self.inherent_risk_score = min(20, round(inherent_score))

				# Set inherent risk rating based on score
				if self.inherent_risk_score >= 15:
					self.inherent_risk_rating = "Critical"
				elif self.inherent_risk_score >= 10:
					self.inherent_risk_rating = "High"
				elif self.inherent_risk_score >= 5:
					self.inherent_risk_rating = "Medium"
				else:
					self.inherent_risk_rating = "Low"

	def validate_key_controls(self):
		"""Validate key controls table"""
		if self.key_controls:
			# Calculate control effectiveness score
			total_effectiveness = 0
			control_count = 0

			for control in self.key_controls:
				if control.control_effectiveness:
					effectiveness_score = {
						"Very Effective": 4,
						"Effective": 3,
						"Partially Effective": 2,
						"Ineffective": 1
					}.get(control.control_effectiveness, 0)
					total_effectiveness += effectiveness_score
					control_count += 1

			if control_count > 0:
				average_effectiveness = total_effectiveness / control_count
				self.control_effectiveness_score = round(average_effectiveness)

				# Set control environment rating based on average effectiveness
				if average_effectiveness >= 3.5:
					self.control_environment_rating = "Strong"
				elif average_effectiveness >= 2.5:
					self.control_environment_rating = "Adequate"
				else:
					self.control_environment_rating = "Weak"

	def on_update(self):
		"""Update related audit plans when universe changes"""
		if self.has_value_changed("residual_risk_rating"):
			self.update_related_audit_plans()

	def update_related_audit_plans(self):
		"""Update audit plans that reference this universe"""
		audit_plans = frappe.get_all("Annual Audit Plan",
			filters={"audit_universe": self.name},
			fields=["name"]
		)

		for plan in audit_plans:
			frappe.get_doc("Annual Audit Plan", plan.name).save()

@frappe.whitelist()
def get_audit_universe_summary():
	"""Get summary of audit universe for dashboard"""
	data = frappe.db.sql("""
		SELECT
			entity_type,
			COUNT(*) as count,
			SUM(CASE WHEN residual_risk_rating = 'Critical' THEN 1 ELSE 0 END) as critical_risks,
			SUM(CASE WHEN residual_risk_rating = 'High' THEN 1 ELSE 0 END) as high_risks,
			SUM(CASE WHEN residual_risk_rating = 'Medium' THEN 1 ELSE 0 END) as medium_risks,
			SUM(CASE WHEN residual_risk_rating = 'Low' THEN 1 ELSE 0 END) as low_risks
		FROM `tabAudit Universe`
		WHERE is_active = 1
		GROUP BY entity_type
	""", as_dict=True)

	return data