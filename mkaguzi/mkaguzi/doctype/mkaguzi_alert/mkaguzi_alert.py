# Copyright (c) 2026, mkaguzi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MkaguziAlert(Document):
	"""
	Mkaguzi Alert DocType for audit and compliance alerts.
	Replaces the broken Compliance Alert child-table usage.
	"""

	def before_insert(self):
		"""Set defaults before insert"""
		if not self.naming_series:
			self.naming_series = "MKAG-ALERT-.YYYY.-"

	def after_insert(self):
		"""Log alert creation"""
		frappe.log(f"Alert created: {self.name} ({self.severity})", "Mkaguzi Alert")

	def on_update(self):
		"""Handle status changes"""
		if self.status == 'Acknowledged' and not self.acknowledged_by:
			self.acknowledged_by = frappe.session.user
			self.acknowledged_on = frappe.utils.now()
		elif self.status == 'Resolved' and not self.resolved_on:
			self.resolved_on = frappe.utils.now()

	def validate(self):
		"""Validate alert data"""
		if self.status == 'Acknowledged' and not self.acknowledged_by:
			self.acknowledged_by = frappe.session.user
			self.acknowledged_on = frappe.utils.now()

		if self.status == 'Resolved' and not self.resolved_on:
			self.resolved_on = frappe.utils.now()
