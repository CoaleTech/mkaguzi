# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime

class CorrectiveActionItem(Document):
	def validate(self):
		"""Validate action item data"""
		self.validate_dates()
		self.update_completion_status()

	def validate_dates(self):
		"""Validate date relationships"""
		if self.target_date and getdate(self.target_date) < getdate():
			if self.status not in ["Completed", "Cancelled"]:
				self.status = "Overdue"

	def update_completion_status(self):
		"""Update completion date when status changes to completed"""
		if self.status == "Completed" and not self.completion_date:
			self.completion_date = getdate()
		elif self.status != "Completed":
			self.completion_date = None

	def before_save(self):
		"""Generate action item ID if not present"""
		if not self.action_item_id:
			parent = frappe.get_doc("Corrective Action Plan", self.parent)
			sequence = len(parent.action_items) + 1
			self.action_item_id = f"AI-{parent.action_plan_id}-{sequence:02d}"