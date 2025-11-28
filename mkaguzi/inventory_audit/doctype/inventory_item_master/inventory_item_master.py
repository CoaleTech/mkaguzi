# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InventoryItemMaster(Document):
	def validate(self):
		if self.item_code:
			self.item_code = self.item_code.strip().upper()
