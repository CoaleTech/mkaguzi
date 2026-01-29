# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class TaxComplianceTracker(Document):
	def autoname(self):
		if not self.tracker_id:
			# Generate tracker ID based on tax period
			if self.tax_period:
				period_name = frappe.get_value("Data Period", self.tax_period, "name")
				self.tracker_id = f"TCT-{period_name}"
			else:
				# Fallback to timestamp-based ID
				from frappe.utils import now
				self.tracker_id = f"TCT-{now().replace(' ', '').replace(':', '').replace('-', '')}"

	def validate(self):
		self.calculate_totals()
		self.calculate_compliance_score()
		self.validate_dates()

	def calculate_totals(self):
		"""Calculate computed total fields"""
		# Net VAT Payable = VAT on Sales - VAT on Purchases
		if self.vat_on_sales is not None and self.vat_on_purchases is not None:
			self.net_vat_payable = self.vat_on_sales - self.vat_on_purchases

		# Total WHT = sum of all WHT components
		wht_components = [
			self.wht_on_services or 0,
			self.wht_on_rent or 0,
			self.wht_on_professional_fees or 0,
			self.other_wht or 0
		]
		self.total_wht = sum(wht_components)

		# Total NSSF = Employee + Employer contributions
		if self.employee_contributions is not None and self.employer_contributions is not None:
			self.total_nssf = self.employee_contributions + self.employer_contributions

	def calculate_compliance_score(self):
		"""Calculate overall compliance score based on filing and payment status"""
		score_components = []

		# VAT Compliance (25% weight)
		vat_score = 0
		if self.vat_return_filed:
			vat_score += 50  # Return filed
		if self.vat_payment_date and self.vat_payment_amount:
			vat_score += 50  # Payment made
		score_components.append(vat_score * 0.25)

		# PAYE Compliance (25% weight)
		paye_score = 0
		if self.paye_return_filed:
			paye_score += 50  # Return filed
		if self.paye_payment_date:
			paye_score += 50  # Payment made
		score_components.append(paye_score * 0.25)

		# WHT Compliance (20% weight)
		wht_score = 0
		if self.wht_return_filed:
			wht_score += 50  # Return filed
		if self.wht_payment_date:
			wht_score += 50  # Payment made
		score_components.append(wht_score * 0.20)

		# NSSF Compliance (15% weight)
		nssf_score = 0
		if self.nssf_return_filed:
			nssf_score += 50  # Return filed
		if self.nssf_payment_date:
			nssf_score += 50  # Payment made
		score_components.append(nssf_score * 0.15)

		# NHIF Compliance (15% weight)
		nhif_score = 0
		if self.nhif_return_filed:
			nhif_score += 50  # Return filed
		if self.nhif_payment_date:
			nhif_score += 50  # Payment made
		score_components.append(nhif_score * 0.15)

		# Calculate final score
		self.compliance_score = sum(score_components)

		# Adjust for issues (reduce score by 10% per unresolved critical issue)
		if self.issues_identified:
			unresolved_issues = [issue for issue in self.issues_identified
							   if issue.resolution_status == "Open"]
			critical_issues = [issue for issue in unresolved_issues
							 if issue.issue_type in ["Late Filing", "Late Payment", "Underpayment"]]
			score_reduction = len(critical_issues) * 10
			self.compliance_score = max(0, self.compliance_score - score_reduction)

	def validate_dates(self):
		"""Validate date relationships"""
		# VAT: Filing date should be before or same as payment date
		if self.vat_filing_date and self.vat_payment_date:
			if self.vat_filing_date > self.vat_payment_date:
				frappe.msgprint(_("VAT filing date should be before or same as payment date"))

		# PAYE: Similar validation
		if self.paye_filing_date and self.paye_payment_date:
			if self.paye_filing_date > self.paye_payment_date:
				frappe.msgprint(_("PAYE filing date should be before or same as payment date"))

		# WHT: Similar validation
		if self.wht_filing_date and self.wht_payment_date:
			if self.wht_filing_date > self.wht_payment_date:
				frappe.msgprint(_("WHT filing date should be before or same as payment date"))

@frappe.whitelist()
def create_tax_tracker_for_period(period_name):
	"""Create a tax compliance tracker for a specific period"""
	# Check if tracker already exists for this period
	existing = frappe.db.exists("Tax Compliance Tracker", {"tax_period": period_name})
	if existing:
		frappe.throw(_("Tax Compliance Tracker already exists for this period"))

	tracker = frappe.new_doc("Tax Compliance Tracker")
	tracker.tax_period = period_name
	tracker.save()

	return tracker

@frappe.whitelist()
def get_compliance_summary_by_period(period_name=None):
	"""Get compliance summary for a period or overall"""
	filters = {}
	if period_name:
		filters["tax_period"] = period_name

	trackers = frappe.get_all("Tax Compliance Tracker",
		filters=filters,
		fields=["name", "compliance_score", "vat_return_filed", "paye_return_filed",
				"wht_return_filed", "nssf_return_filed", "nhif_return_filed"]
	)

	if not trackers:
		return {"total_trackers": 0, "avg_compliance_score": 0}

	total_score = sum(tracker.compliance_score or 0 for tracker in trackers)
	avg_score = total_score / len(trackers)

	# Count filings
	filings = {
		"vat_returns": sum(1 for t in trackers if t.vat_return_filed),
		"paye_returns": sum(1 for t in trackers if t.paye_return_filed),
		"wht_returns": sum(1 for t in trackers if t.wht_return_filed),
		"nssf_returns": sum(1 for t in trackers if t.nssf_return_filed),
		"nhif_returns": sum(1 for t in trackers if t.nhif_return_filed)
	}

	return {
		"total_trackers": len(trackers),
		"avg_compliance_score": avg_score,
		"filings": filings
	}

@frappe.whitelist()
def generate_compliance_report(tracker_name):
	"""Generate a detailed compliance report"""
	tracker = frappe.get_doc("Tax Compliance Tracker", tracker_name)

	report_data = {
		"tracker_id": tracker.tracker_id,
		"tax_period": tracker.tax_period,
		"compliance_score": tracker.compliance_score,
		"sections": {
			"vat": {
				"return_filed": tracker.vat_return_filed,
				"payment_made": bool(tracker.vat_payment_date and tracker.vat_payment_amount),
				"amount": tracker.net_vat_payable
			},
			"paye": {
				"return_filed": tracker.paye_return_filed,
				"payment_made": bool(tracker.paye_payment_date),
				"amount": tracker.total_paye
			},
			"wht": {
				"return_filed": tracker.wht_return_filed,
				"payment_made": bool(tracker.wht_payment_date),
				"amount": tracker.total_wht
			},
			"nssf": {
				"return_filed": tracker.nssf_return_filed,
				"payment_made": bool(tracker.nssf_payment_date),
				"amount": tracker.total_nssf
			},
			"nhif": {
				"return_filed": tracker.nhif_return_filed,
				"payment_made": bool(tracker.nhif_payment_date),
				"amount": tracker.total_nhif
			}
		},
		"issues": []
	}

	if tracker.issues_identified:
		for issue in tracker.issues_identified:
			report_data["issues"].append({
				"type": issue.issue_type,
				"description": issue.description,
				"financial_impact": issue.financial_impact,
				"status": issue.resolution_status
			})

	return report_data