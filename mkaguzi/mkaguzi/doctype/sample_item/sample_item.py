# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class SampleItem(Document):
	def validate(self):
		"""Validate sample item data"""
		if self.exception_found and not self.exception_details:
			frappe.throw(_("Exception Details are required when Exception Found is checked"))

		if self.test_result == "Fail" and not self.exception_found:
			self.exception_found = 1