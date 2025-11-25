# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AnnualAuditPlanBudget(Document):
	def validate(self):
		self.calculate_variance()

	def calculate_variance(self):
		"""Calculate budget variance"""
		if self.planned_amount is not None and self.actual_amount is not None:
			self.variance = self.actual_amount - self.planned_amount
			if self.planned_amount > 0:
				self.variance_percentage = (self.variance / self.planned_amount) * 100
			else:
				self.variance_percentage = 0