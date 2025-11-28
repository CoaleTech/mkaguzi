# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class InventoryAuditPlan(Document):
	def validate(self):
		self.validate_dates()
		self.check_overdue()

	def validate_dates(self):
		if self.planned_start_date and self.planned_end_date:
			if getdate(self.planned_start_date) > getdate(self.planned_end_date):
				frappe.throw(_("Planned Start Date cannot be after Planned End Date"))

		if self.actual_start_date and self.actual_end_date:
			if getdate(self.actual_start_date) > getdate(self.actual_end_date):
				frappe.throw(_("Actual Start Date cannot be after Actual End Date"))

	def check_overdue(self):
		if self.sla_due_date and self.status not in ["Completed", "Closed", "Cancelled"]:
			if getdate(self.sla_due_date) < getdate(nowdate()):
				self.is_overdue = 1
			else:
				self.is_overdue = 0
		else:
			self.is_overdue = 0

	def on_submit(self):
		if not self.actual_start_date:
			self.db_set("actual_start_date", nowdate())
		self.db_set("status", "In Progress")

	def before_cancel(self):
		self.db_set("status", "Cancelled")
