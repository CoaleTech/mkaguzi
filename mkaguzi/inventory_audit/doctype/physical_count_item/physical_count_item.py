# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PhysicalCountItem(Document):
	def validate(self):
		self.calculate_variance()

	def calculate_variance(self):
		self.variance_qty = (self.counted_qty or 0) - (self.system_qty or 0)
		
		if self.system_qty and self.system_qty != 0:
			self.variance_percent = (self.variance_qty / self.system_qty) * 100
		else:
			self.variance_percent = 100 if self.variance_qty != 0 else 0

		# Get valuation rate from item master if available
		valuation_rate = 0
		if self.item_code:
			item = frappe.db.get_value("Inventory Item Master", self.item_code, "valuation_rate")
			if item:
				valuation_rate = item

		self.variance_value = self.variance_qty * valuation_rate

		# Check materiality - this should be based on parent's thresholds
		# For now, flag if variance > 5% or value > 1000
		if abs(self.variance_percent or 0) > 5 or abs(self.variance_value or 0) > 1000:
			self.is_material = 1
		else:
			self.is_material = 0
