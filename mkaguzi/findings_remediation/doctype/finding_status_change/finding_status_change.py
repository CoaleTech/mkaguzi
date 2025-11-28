# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class FindingStatusChange(Document):
	def validate(self):
		"""Validate status change entry"""
		if not self.reason and self.new_status != self.previous_status:
			frappe.msgprint(_("Please provide a reason for the status change"))

		# Ensure changed_on is set
		if not self.changed_on:
			from frappe.utils import now
			self.changed_on = now()

		# Ensure changed_by is set
		if not self.changed_by:
			self.changed_by = frappe.session.user