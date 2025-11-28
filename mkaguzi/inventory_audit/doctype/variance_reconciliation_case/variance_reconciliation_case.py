# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, getdate, nowdate


class VarianceReconciliationCase(Document):
	def validate(self):
		self.set_sla_dates()
		self.check_sla_breach()
		self.determine_materiality_level()

	def set_sla_dates(self):
		if not self.sla_start_date:
			self.sla_start_date = nowdate()
		
		if not self.sla_due_date and self.sla_start_date:
			# Default SLA of 7 days
			self.sla_due_date = add_days(self.sla_start_date, 7)

	def check_sla_breach(self):
		if self.sla_due_date and self.status not in ["Approved", "Closed"]:
			if getdate(nowdate()) > getdate(self.sla_due_date):
				self.is_sla_breached = 1
			else:
				self.is_sla_breached = 0

	def determine_materiality_level(self):
		abs_variance = abs(self.variance_value or 0)
		abs_percent = abs(self.variance_percent or 0)

		if abs_variance >= 100000 or abs_percent >= 50:
			self.materiality_level = "Critical"
		elif abs_variance >= 50000 or abs_percent >= 25:
			self.materiality_level = "High"
		elif abs_variance >= 10000 or abs_percent >= 10:
			self.materiality_level = "Medium"
		else:
			self.materiality_level = "Low"

	def before_save(self):
		if self.status == "Resolved" and not self.resolved_date:
			self.resolved_date = nowdate()
			self.resolved_by = frappe.session.user

		if self.status == "Approved" and not self.approval_date:
			self.approval_date = nowdate()
			self.approved_by = frappe.session.user
