# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class FollowupActivity(Document):
	def validate(self):
		"""Validate follow-up activity data"""
		self.validate_activity_date()

	def validate_activity_date(self):
		"""Validate activity date is not in the future"""
		from frappe.utils import getdate, now_datetime

		if self.activity_date and getdate(self.activity_date) > getdate():
			frappe.throw(_("Activity date cannot be in the future"))

	def before_save(self):
		"""Set performed by if not set"""
		if not self.performed_by:
			self.performed_by = frappe.session.user