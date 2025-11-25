# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, date_diff

class FindingActionMilestone(Document):
	def validate(self):
		"""Validate milestone dates"""
		if self.due_date and self.due_date < getdate(nowdate()):
			if self.status not in ["Completed", "Cancelled"]:
				frappe.msgprint(_("Milestone is overdue"))

		if self.status == "Completed" and not self.completion_date:
			self.completion_date = getdate(nowdate())

		if self.completion_date and self.due_date:
			if self.completion_date > self.due_date:
				self.delayed_days = date_diff(self.completion_date, self.due_date)
			else:
				self.delayed_days = 0