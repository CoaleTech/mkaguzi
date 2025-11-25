# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class ErrorException(Document):
	def validate(self):
		"""Validate error/exception data"""
		if self.severity == "Critical" and not self.corrective_action:
			frappe.throw(_("Corrective Action is required for Critical severity errors"))

		if self.status == "Resolved" and not self.corrective_action:
			frappe.throw(_("Corrective Action is required to mark error as Resolved"))