# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AuditCalendarMilestone(Document):
	def validate(self):
		self.update_progress_based_on_status()

	def update_progress_based_on_status(self):
		"""Update progress percentage based on status"""
		status_progress = {
			"Not Started": 0,
			"In Progress": 50,
			"Completed": 100,
			"Delayed": 25,
			"Cancelled": 0
		}

		if self.status in status_progress:
			self.progress_percentage = status_progress[self.status]