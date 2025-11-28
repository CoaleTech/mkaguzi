# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, time_diff_in_hours


class StockTakeSession(Document):
	def validate(self):
		self.calculate_duration()
		self.calculate_summary()
		self.record_signoffs()

	def calculate_duration(self):
		if self.start_datetime and self.end_datetime:
			self.duration_hours = time_diff_in_hours(self.end_datetime, self.start_datetime)

	def calculate_summary(self):
		if not self.count_items:
			return

		self.total_items_counted = len(self.count_items)
		self.total_variance_qty = sum(abs(float(item.variance_qty or 0)) for item in self.count_items)
		self.total_variance_value = sum(abs(float(item.variance_value or 0)) for item in self.count_items)
		self.material_variance_count = sum(1 for item in self.count_items if item.is_material)

	def record_signoffs(self):
		now = now_datetime()
		user = frappe.session.user

		if self.team_signoff and not self.team_signoff_by:
			self.team_signoff_by = user
			self.team_signoff_date = now

		if self.supervisor_signoff and not self.supervisor_signoff_by:
			self.supervisor_signoff_by = user
			self.supervisor_signoff_date = now

		if self.auditor_signoff and not self.auditor_signoff_by:
			self.auditor_signoff_by = user
			self.auditor_signoff_date = now

	def on_submit(self):
		self.db_set("status", "Counting Complete")
		# Create variance cases for material variances
		self.create_variance_cases()

	def create_variance_cases(self):
		"""Create variance reconciliation cases for material variances"""
		for item in self.count_items:
			if item.is_material:
				# Check if case already exists
				existing = frappe.db.exists("Variance Reconciliation Case", {
					"stock_take_session": self.name,
					"item_code": item.item_code
				})
				if not existing:
					case = frappe.new_doc("Variance Reconciliation Case")
					case.stock_take_session = self.name
					case.item_code = item.item_code
					case.item_description = item.item_description
					case.system_qty = item.system_qty
					case.counted_qty = item.counted_qty
					case.variance_qty = item.variance_qty
					case.variance_value = item.variance_value
					case.variance_percent = item.variance_percent
					case.insert(ignore_permissions=True)

	def before_cancel(self):
		self.db_set("status", "Cancelled")
