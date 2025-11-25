# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class AnalyticalProcedureResult(Document):
	def validate(self):
		"""Calculate variance and variance percentage"""
		if self.expected_result is not None and self.actual_result is not None:
			self.variance = self.actual_result - self.expected_result

			if self.expected_result != 0:
				self.variance_percentage = (self.variance / self.expected_result) * 100
			else:
				self.variance_percentage = 0

			# Determine result status based on threshold
			if self.threshold:
				if abs(self.variance_percentage) > self.threshold:
					self.result_status = "Above Threshold" if self.variance_percentage > 0 else "Below Threshold"
				else:
					self.result_status = "Within Threshold"
			else:
				self.result_status = "Within Threshold"