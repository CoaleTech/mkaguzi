# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class AuditDataRequirement(Document):
	def validate(self):
		self.validate_dates()
		self.set_requested_date()
		self.update_status_dates()

	def validate_dates(self):
		"""Validate date ranges"""
		if self.period_start and self.period_end:
			if self.period_end < self.period_start:
				frappe.throw(_("Period end date cannot be before period start date"))

	def set_requested_date(self):
		"""Set requested date if not provided"""
		if not self.requested_date:
			self.requested_date = getdate()

	def update_status_dates(self):
		"""Update dates based on status changes"""
		if self.status == "Received" and not self.received_date:
			self.received_date = getdate()