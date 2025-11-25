# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class RiskArea(Document):
	def validate(self):
		self.validate_risk_rating()
		self.generate_procedures_addressing_risk()

	def validate_risk_rating(self):
		"""Validate risk rating is appropriate"""
		valid_ratings = ["High", "Medium", "Low"]
		if self.risk_rating not in valid_ratings:
			frappe.throw(_("Risk rating must be one of: {0}").format(", ".join(valid_ratings)))

	def generate_procedures_addressing_risk(self):
		"""Auto-generate procedures addressing this risk if empty"""
		if not self.procedures_addressing_risk and self.risk_description:
			# Generate default procedures based on risk description
			risk_lower = self.risk_description.lower()

			default_procedures = []

			if "control" in risk_lower or "authorization" in risk_lower:
				default_procedures.append("Test segregation of duties")
				default_procedures.append("Review approval processes")
				default_procedures.append("Verify access controls")

			if "valuation" in risk_lower or "inventory" in risk_lower:
				default_procedures.append("Perform inventory count")
				default_procedures.append("Test valuation calculations")
				default_procedures.append("Review cost accounting methods")

			if "completeness" in risk_lower or "occurrence" in risk_lower:
				default_procedures.append("Test transaction cut-off")
				default_procedures.append("Verify recording of transactions")
				default_procedures.append("Review period-end procedures")

			if "accuracy" in risk_lower or "measurement" in risk_lower:
				default_procedures.append("Recalculate balances")
				default_procedures.append("Test mathematical accuracy")
				default_procedures.append("Review calculation methods")

			if default_procedures:
				self.procedures_addressing_risk = "\n".join(f"• {proc}" for proc in default_procedures)
			else:
				self.procedures_addressing_risk = "• Assess risk controls\n• Test operating effectiveness\n• Evaluate residual risk"
