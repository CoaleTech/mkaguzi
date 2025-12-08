# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

class ActionPlanProgress(Document):
	def validate(self):
		"""Validate progress entry"""
		self.validate_progress_percentage()
		self.set_updated_by()

	def validate_progress_percentage(self):
		"""Validate progress percentage is between 0 and 100"""
		if self.progress_percentage < 0 or self.progress_percentage > 100:
			frappe.throw(_("Progress percentage must be between 0 and 100"))

	def set_updated_by(self):
		"""Set the user who updated the progress"""
		if not self.updated_by:
			self.updated_by = frappe.session.user