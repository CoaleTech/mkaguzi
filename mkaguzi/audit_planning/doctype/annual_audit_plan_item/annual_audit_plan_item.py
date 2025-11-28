# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import date_diff

class AnnualAuditPlanItem(Document):
	def validate(self):
		self.validate_dates()
		self.calculate_planned_days()

	def validate_dates(self):
		"""Validate that end date is after start date"""
		if self.planned_start_date and self.planned_end_date:
			if self.planned_end_date < self.planned_start_date:
				frappe.throw("Planned end date cannot be before planned start date")

	def calculate_planned_days(self):
		"""Auto-calculate planned days based on date range if not provided"""
		if self.planned_start_date and self.planned_end_date and not self.planned_days:
			# Calculate working days (excluding weekends)
			days_diff = date_diff(self.planned_end_date, self.planned_start_date) + 1
			# Simple approximation - could be enhanced with working days calculation
			self.planned_days = max(1, days_diff)