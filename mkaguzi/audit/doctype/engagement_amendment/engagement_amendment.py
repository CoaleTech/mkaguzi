# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class EngagementAmendment(Document):
	def validate(self):
		self.set_amendment_date()
		self.validate_approval()

	def set_amendment_date(self):
		"""Set amendment date if not provided"""
		if not self.amendment_date:
			self.amendment_date = getdate()

	def validate_approval(self):
		"""Validate approval requirements"""
		if self.status in ["Approved", "Implemented"] and not self.approved_by:
			frappe.throw(_("Approval required for status: {0}").format(self.status))