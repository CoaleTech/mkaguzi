# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, date_diff

class FindingFollowupActivity(Document):
	def validate(self):
		"""Validate follow-up activity"""
		if self.next_follow_up_date and self.next_follow_up_date < getdate(nowdate()):
			if self.status != "Completed":
				self.status = "Overdue"
				frappe.msgprint(_("Follow-up activity is overdue"))

		if self.status == "Completed" and not self.findings:
			frappe.msgprint(_("Please document findings/observations for completed follow-up"))

		# Auto-set follow_up_by if not set
		if not self.follow_up_by:
			self.follow_up_by = frappe.session.user