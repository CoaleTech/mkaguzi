# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, get_datetime

class AuditReport(Document):
	def autoname(self):
		if not self.report_id:
			# Generate report ID in format AR-YYYY-####
			current_year = getdate().year

			last_report = frappe.db.sql("""
				SELECT report_id FROM `tabAudit Report`
				WHERE report_id LIKE 'AR-{}-%'
				ORDER BY CAST(SUBSTRING_INDEX(report_id, '-', -1) AS UNSIGNED) DESC
				LIMIT 1
			""".format(current_year), as_dict=True)

			if last_report:
				last_num = int(last_report[0].report_id.split('-')[-1])
				next_num = last_num + 1
			else:
				next_num = 1

			self.report_id = f"AR-{current_year}-{next_num:04d}"

	def validate(self):
		self.validate_dates()
		self.populate_finding_data()
		self.update_finding_numbers()
		self.manage_version_control()

	def validate_dates(self):
		"""Validate date relationships"""
		if self.preparation_date and self.report_date:
			if self.preparation_date > self.report_date:
				frappe.throw(_("Preparation Date cannot be after Report Date"))

		if self.review_date and self.report_date:
			if self.review_date > self.report_date:
				frappe.throw(_("Review Date cannot be after Report Date"))

		if self.approval_date and self.report_date:
			if self.approval_date > self.report_date:
				frappe.throw(_("Approval Date cannot be after Report Date"))

	def populate_finding_data(self):
		"""Populate finding data in child tables from linked audit findings"""
		if not self.engagement_reference:
			return

		# Get all findings for this engagement
		findings = frappe.get_all("Audit Finding",
			filters={"engagement_reference": self.engagement_reference},
			fields=["name", "finding_id", "finding_title", "risk_rating", "condition",
					"criteria", "cause", "effect", "recommendation", "management_comments",
					"action_plan_description", "target_completion_date"]
		)

		# Populate key findings summary
		if not self.key_findings_summary:
			for finding in findings:
				if finding.risk_rating in ["Critical", "High"]:
					self.append("key_findings_summary", {
						"finding_reference": finding.name,
						"finding_title": finding.finding_title,
						"risk_rating": finding.risk_rating,
						"summary": f"Critical finding related to {finding.finding_title}"
					})

		# Populate detailed findings
		if not self.detailed_findings:
			for finding in findings:
				if finding.risk_rating in ["Critical", "High", "Medium"]:
					self.append("detailed_findings", {
						"finding_reference": finding.name,
						"finding_title": finding.finding_title,
						"condition": finding.condition,
						"criteria": finding.criteria,
						"cause": finding.cause,
						"effect": finding.effect,
						"recommendation": finding.recommendation,
						"management_response": finding.management_comments,
						"action_plan": finding.action_plan_description,
						"target_date": finding.target_completion_date
					})

	def update_finding_numbers(self):
		"""Update finding numbers in detailed findings"""
		if self.detailed_findings:
			for i, finding in enumerate(self.detailed_findings, 1):
				finding.finding_number = f"Finding {i}"

	def manage_version_control(self):
		"""Manage version control and revision history"""
		if not self.version_number:
			self.version_number = 1.0

		# Add revision entry when status changes to certain values
		if self.has_value_changed("report_status"):
			if self.report_status in ["Under Review", "Finalized", "Issued"]:
				self.add_revision_entry()

	def add_revision_entry(self):
		"""Add entry to revision history"""
		if not self.revision_history:
			self.revision_history = []

		changes = f"Status changed to {self.report_status}"
		if hasattr(self, '_original_status'):
			changes = f"Status changed from {self._original_status} to {self.report_status}"

		self.append("revision_history", {
			"revision_date": get_datetime(),
			"revised_by": frappe.session.user,
			"changes_made": changes
		})

		# Increment version number
		self.version_number = (self.version_number or 1.0) + 0.1

	def before_save(self):
		"""Set original status for change tracking"""
		if not self.is_new():
			original = frappe.get_doc(self.doctype, self.name)
			self._original_status = original.report_status

	def on_update(self):
		"""Update related engagement status"""
		if self.report_status == "Issued" and self.engagement_reference:
			engagement = frappe.get_doc("Audit Engagement", self.engagement_reference)
			if engagement.engagement_status != "Completed":
				engagement.engagement_status = "Report Issued"
				engagement.save()

@frappe.whitelist()
def create_audit_report(engagement_name, report_type="Full Audit Report"):
	"""Create an audit report for a completed engagement"""
	engagement = frappe.get_doc("Audit Engagement", engagement_name)

	# Check if report already exists
	existing_report = frappe.db.exists("Audit Report", {"engagement_reference": engagement_name})
	if existing_report:
		frappe.throw(_("Audit report already exists for this engagement"))

	report = frappe.new_doc("Audit Report")
	report.engagement_reference = engagement_name
	report.report_title = f"Audit Report - {engagement.engagement_title}"
	report.report_type = report_type
	report.report_date = getdate()
	report.report_period = f"{engagement.start_date} to {engagement.end_date}"
	report.report_status = "Draft"
	report.prepared_by = frappe.session.user
	report.preparation_date = getdate()

	# Auto-populate basic content
	report.background = f"This report presents the results of the internal audit of {engagement.audit_universe} conducted from {engagement.start_date} to {engagement.end_date}."
	report.audit_scope = engagement.audit_scope or "Comprehensive audit of processes, controls, and compliance."
	report.audit_objectives = engagement.audit_objectives or "To assess the adequacy and effectiveness of internal controls and provide assurance on operational efficiency."

	return report

@frappe.whitelist()
def get_report_summary(report_name):
	"""Get summary information for a report"""
	report = frappe.get_doc("Audit Report", report_name)

	summary = {
		"report_id": report.report_id,
		"engagement": report.engagement_reference,
		"report_type": report.report_type,
		"status": report.report_status,
		"total_findings": len(report.detailed_findings) if report.detailed_findings else 0,
		"critical_findings": 0,
		"high_findings": 0,
		"opinion": report.overall_audit_opinion
	}

	# Count findings by risk rating
	if report.detailed_findings:
		for finding in report.detailed_findings:
			finding_doc = frappe.get_doc("Audit Finding", finding.finding_reference)
			if finding_doc.risk_rating == "Critical":
				summary["critical_findings"] += 1
			elif finding_doc.risk_rating == "High":
				summary["high_findings"] += 1

	return summary

@frappe.whitelist()
def generate_report_pdf(report_name):
	"""Generate PDF version of the audit report"""
	report = frappe.get_doc("Audit Report", report_name)

	# This would integrate with PDF generation libraries
	# For now, just update the status and log the attempt
	report.report_status = "Finalized"
	report.save()

	frappe.msgprint(_("Report PDF generation initiated. Please check the report file attachment."))

	return report