# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, add_days

class EnvironmentalAudit(Document):
	def autoname(self):
		if not self.audit_id:
			# Generate audit ID: ENV-YYYY-sequencenumber
			year = getdate(self.start_date or nowdate()).year
			count = frappe.db.count("Environmental Audit", {
				"start_date": (">=", f"{year}-01-01"),
				"start_date": ("<", f"{year + 1}-01-01")
			})
			sequence = count + 1
			self.audit_id = f"ENV-{year}-{sequence:03d}"

	def validate(self):
		self.validate_dates()
		self.calculate_esg_score()
		self.calculate_improvement()
		self.set_compliance_status()

	def validate_dates(self):
		"""Validate date relationships"""
		if self.start_date and self.end_date:
			if self.end_date < self.start_date:
				frappe.throw(_("End Date cannot be before Start Date"))

		if self.target_completion_date and self.actual_completion_date:
			if self.actual_completion_date > self.target_completion_date:
				frappe.msgprint(_("Audit completed after target date"))

	def calculate_esg_score(self):
		"""Calculate overall ESG score based on metrics and ratings"""
		score_map = {
			"Excellent": 90,
			"Good": 75,
			"Satisfactory": 60,
			"Needs Improvement": 40,
			"Poor": 20
		}

		if self.sustainability_rating:
			self.esg_score = score_map.get(self.sustainability_rating, 50)

	def calculate_improvement(self):
		"""Calculate improvement percentage vs baseline"""
		if self.target_reduction and self.actual_reduction is not None:
			self.improvement_percentage = (self.actual_reduction / self.target_reduction) * 100
		elif self.actual_reduction is not None:
			self.improvement_percentage = self.actual_reduction

	def set_compliance_status(self):
		"""Set compliance status based on ESG score"""
		if not self.compliance_status:
			if self.esg_score >= 90:
				self.compliance_status = "Fully Compliant"
			elif self.esg_score >= 70:
				self.compliance_status = "Mostly Compliant"
			elif self.esg_score >= 50:
				self.compliance_status = "Partially Compliant"
			elif self.esg_score >= 30:
				self.compliance_status = "Non-Compliant"
			else:
				self.compliance_status = "Not Assessed"

	def before_save(self):
		"""Set status to In Progress on start date"""
		if self.start_date and getdate(self.start_date) <= getdate() and self.status == "Planned":
			self.status = "In Progress"

	def on_update(self):
		"""Handle status changes"""
		if self.status == "Completed" and not self.actual_completion_date:
			self.actual_completion_date = getdate()

@frappe.whitelist()
def get_esg_summary(year=None):
	"""Get ESG audit summary for a year"""
	if not year:
		year = getdate().year

	audits = frappe.get_all("Environmental Audit",
		filters={
			"start_date": (">=", f"{year}-01-01"),
			"start_date": ("<", f"{year + 1}-01-01")
		},
		fields=["audit_type", "status", "compliance_status", "esg_score", "risk_level"]
	)

	summary = {
		"total_audits": len(audits),
		"by_type": {},
		"by_status": {},
		"by_compliance": {},
		"average_esg_score": 0,
		"risk_distribution": {}
	}

	total_score = 0
	for audit in audits:
		# Count by type
		audit_type = audit.audit_type or "Other"
		summary["by_type"][audit_type] = summary["by_type"].get(audit_type, 0) + 1

		# Count by status
		status = audit.status or "Planned"
		summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

		# Count by compliance
		compliance = audit.compliance_status or "Not Assessed"
		summary["by_compliance"][compliance] = summary["by_compliance"].get(compliance, 0) + 1

		# Sum ESG scores
		if audit.esg_score:
			total_score += audit.esg_score

		# Count by risk level
		risk = audit.risk_level or "Low"
		summary["risk_distribution"][risk] = summary["risk_distribution"].get(risk, 0) + 1

	if audits:
		summary["average_esg_score"] = total_score / len(audits)

	return summary

@frappe.whitelist()
def get_carbon_footprint_summary(year=None):
	"""Get carbon footprint summary for a year"""
	if not year:
		year = getdate().year

	audits = frappe.get_all("Environmental Audit",
		filters={
			"start_date": (">=", f"{year}-01-01"),
			"start_date": ("<", f"{year + 1}-01-01"),
			"carbon_emissions": (">", 0)
		},
		fields=["carbon_emissions", "energy_consumption", "water_usage", "waste_generation"]
	)

	summary = {
		"total_carbon_emissions": 0,
		"total_energy_consumption": 0,
		"total_water_usage": 0,
		"total_waste_generation": 0,
		"audit_count": len(audits)
	}

	for audit in audits:
		if audit.carbon_emissions:
			summary["total_carbon_emissions"] += audit.carbon_emissions
		if audit.energy_consumption:
			summary["total_energy_consumption"] += audit.energy_consumption
		if audit.water_usage:
			summary["total_water_usage"] += audit.water_usage
		if audit.waste_generation:
			summary["total_waste_generation"] += audit.waste_generation

	return summary
