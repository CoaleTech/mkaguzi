# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AnnualAuditPlanResource(Document):
	def validate(self):
		self.set_auditor_name()
		self.calculate_utilization()
		self.calculate_total_cost()

	def set_auditor_name(self):
		"""Set auditor name from Employee Master"""
		if self.auditor and not self.auditor_name:
			employee = frappe.get_doc("Employee Master", self.auditor)
			self.auditor_name = employee.employee_name

	def calculate_utilization(self):
		"""Calculate utilization percentage"""
		if self.available_days and self.available_days > 0:
			self.utilization_percentage = (self.allocated_days / self.available_days) * 100
		else:
			self.utilization_percentage = 0

	def calculate_total_cost(self):
		"""Calculate total cost based on allocated days and rate"""
		if self.allocated_days and self.cost_rate_per_day:
			self.total_cost = self.allocated_days * self.cost_rate_per_day