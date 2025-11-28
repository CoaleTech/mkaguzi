# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, time_diff_in_hours


class StockTakeIssueLog(Document):
	def validate(self):
		self.check_sla_breach()

	def check_sla_breach(self):
		if self.sla_hours and self.status not in ["Resolved", "Closed"]:
			if self.issue_date and self.due_date:
				if getdate(nowdate()) > getdate(self.due_date):
					self.is_sla_breached = 1
				else:
					self.is_sla_breached = 0

	def before_save(self):
		if self.status == "Resolved" and not self.resolved_date:
			self.resolved_date = nowdate()
