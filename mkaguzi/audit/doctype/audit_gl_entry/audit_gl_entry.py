# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, now


class AuditGLEntry(Document):
	def validate(self):
		"""Validate the audit GL entry"""
		self.validate_gl_entry()
		self.validate_risk_score()
		self.set_analysis_date()
		self.validate_status_transitions()

	def validate_gl_entry(self):
		"""Validate that the GL entry exists and is accessible"""
		if self.gl_entry_link:
			# Check if GL Entry exists
			if not frappe.db.exists("GL Entry", self.gl_entry_link):
				frappe.throw(_("GL Entry {0} does not exist").format(self.gl_entry_link))

			# Prevent duplicate audit entries for the same GL entry
			existing_audit = frappe.db.exists("Audit GL Entry", {
				"gl_entry_link": self.gl_entry_link,
				"docstatus": ("!=", 2),
				"name": ("!=", self.name) if self.name else ("!=", "")
			})

			if existing_audit:
				frappe.throw(_("An Audit GL Entry already exists for GL Entry {0}").format(self.gl_entry_link))

	def validate_risk_score(self):
		"""Validate that risk score is between 0 and 100"""
		if self.risk_score is not None:
			if self.risk_score < 0 or self.risk_score > 100:
				frappe.throw(_("Risk Score must be between 0 and 100"))

	def set_analysis_date(self):
		"""Set analysis date if not set"""
		if not self.analysis_date:
			self.analysis_date = now()

	def validate_status_transitions(self):
		"""Validate status transitions and set appropriate dates"""
		if self.status == "Reviewed" and not self.reviewed_by:
			self.reviewed_by = frappe.session.user
			if not self.reviewed_date:
				self.reviewed_date = now()

		if self.status == "Acknowledged" and not self.acknowledged_by:
			self.acknowledged_by = frappe.session.user
			if not self.acknowledged_date:
				self.acknowledged_date = now()

	def on_submit(self):
		"""Actions when audit entry is submitted"""
		self.update_gl_entry_audit_status()
		self.create_notification()

	def on_cancel(self):
		"""Actions when audit entry is cancelled"""
		self.clear_gl_entry_audit_status()

	def update_gl_entry_audit_status(self):
		"""Update the GL Entry with audit information"""
		# This could be used to update custom fields on GL Entry
		# or update related audit status
		pass

	def clear_gl_entry_audit_status(self):
		"""Clear audit status from GL Entry on cancellation"""
		pass

	def create_notification(self):
		"""Create notification for reviewed status if needed"""
		if self.status == "Reviewed":
			# Create notification for acknowledge action
			pass


@frappe.whitelist()
def get_gl_entry_details(gl_entry_name):
	"""Get GL Entry details for audit"""
	frappe.has_permission("GL Entry", "read", throw=True)

	gl_entry = frappe.get_doc("GL Entry", gl_entry_name)

	return {
		"posting_date": gl_entry.posting_date,
		"account": gl_entry.account,
		"debit_amount": gl_entry.debit,
		"credit_amount": gl_entry.credit,
		"voucher_type": gl_entry.voucher_type,
		"voucher_no": gl_entry.voucher_no,
		"party": gl_entry.party,
		"cost_center": gl_entry.cost_center,
		"reference_type": gl_entry.reference_type,
		"reference_name": gl_entry.reference_name
	}


@frappe.whitelist()
def analyze_gl_entry(gl_entry_name, agent_config, anomaly_type=None):
	"""Analyze a GL Entry and create an Audit GL Entry"""
	frappe.has_permission("Audit GL Entry", "create", throw=True)

	# Check if GL Entry exists
	if not frappe.db.exists("GL Entry", gl_entry_name):
		frappe.throw(_("GL Entry {0} does not exist").format(gl_entry_name))

	# Check if audit already exists
	existing_audit = frappe.db.exists("Audit GL Entry", {
		"gl_entry_link": gl_entry_name,
		"docstatus": ("!=", 2)
	})

	if existing_audit:
		return {
			"success": False,
			"message": _("Audit GL Entry already exists for this GL Entry"),
			"audit_entry": existing_audit
		}

	# Create Audit GL Entry
	audit_entry = frappe.get_doc({
		"doctype": "Audit GL Entry",
		"gl_entry_link": gl_entry_name,
		"analyzed_by": agent_config,
		"analysis_date": now(),
		"status": "Pending",
		"anomaly_type": anomaly_type,
		"risk_score": 50  # Default risk score
	})

	audit_entry.insert()

	return {
		"success": True,
		"message": _("Audit GL Entry created successfully"),
		"audit_entry": audit_entry.name
	}


@frappe.whitelist()
def bulk_analyze_gl_entries(gl_entries, agent_config):
	"""Bulk analyze multiple GL entries"""
	frappe.has_permission("Audit GL Entry", "create", throw=True)

	results = []
	for gl_entry_name in gl_entries:
		try:
			result = analyze_gl_entry(gl_entry_name, agent_config)
			results.append({
				"gl_entry": gl_entry_name,
				"success": result.get("success", False),
				"message": result.get("message", ""),
				"audit_entry": result.get("audit_entry", "")
			})
		except Exception as e:
			results.append({
				"gl_entry": gl_entry_name,
				"success": False,
				"message": str(e),
				"audit_entry": ""
			})

	return results


@frappe.whitelist()
def get_high_risk_audit_entries(threshold=70):
	"""Get all high risk audit entries"""
	frappe.has_permission("Audit GL Entry", "read", throw=True)

	return frappe.get_all("Audit GL Entry",
		filters={
			"risk_score": (">=", threshold),
			"docstatus": ("!=", 2)
		},
		fields=["name", "gl_entry_link", "posting_date", "account", "risk_score", "anomaly_type", "status"],
		order_by="risk_score desc"
	)


@frappe.whitelist()
def get_audit_summary_by_account(from_date=None, to_date=None):
	"""Get audit summary grouped by account"""
	frappe.has_permission("Audit GL Entry", "read", throw=True)

	filters = {"docstatus": ("!=", 2)}

	if from_date:
		filters["posting_date"] = (">=", from_date)
	if to_date:
		if "posting_date" in filters:
			filters["posting_date"] = (filters["posting_date"], "<=", to_date)
		else:
			filters["posting_date"] = ("<=", to_date)

	audit_entries = frappe.get_all("Audit GL Entry",
		filters=filters,
		fields=["account", "risk_score", "debit_amount", "credit_amount"]
	)

	summary = {}
	for entry in audit_entries:
		account = entry.account
		if account not in summary:
			summary[account] = {
				"account": account,
				"total_entries": 0,
				"total_risk_score": 0,
				"avg_risk_score": 0,
				"total_debit": 0,
				"total_credit": 0
			}

		summary[account]["total_entries"] += 1
		summary[account]["total_risk_score"] += entry.risk_score or 0
		summary[account]["total_debit"] += entry.debit_amount or 0
		summary[account]["total_credit"] += entry.credit_amount or 0

	# Calculate averages
	for account in summary:
		if summary[account]["total_entries"] > 0:
			summary[account]["avg_risk_score"] = \
				summary[account]["total_risk_score"] / summary[account]["total_entries"]

	return list(summary.values())


@frappe.whitelist()
def update_audit_status(audit_entry_name, status, remarks=None):
	"""Update audit status"""
	frappe.has_permission("Audit GL Entry", "write", throw=True)

	doc = frappe.get_doc("Audit GL Entry", audit_entry_name)

	# Validate status
	if status not in ["Pending", "Reviewed", "Acknowledged"]:
		frappe.throw(_("Invalid status"))

	doc.status = status
	if remarks:
		doc.audit_remarks = remarks

	doc.save()

	return {
		"success": True,
		"message": _("Audit status updated successfully")
	}
