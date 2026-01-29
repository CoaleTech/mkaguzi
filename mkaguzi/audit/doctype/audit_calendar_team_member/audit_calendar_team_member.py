# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import date_diff

class AuditCalendarTeamMember(Document):
	def validate(self):
		self.set_member_name()
		self.calculate_total_cost()

	def set_member_name(self):
		"""Set member name from Employee Master"""
		if self.team_member and not self.member_name:
			employee = frappe.get_doc("Employee Master", self.team_member)
			self.member_name = employee.employee_name

	def calculate_total_cost(self):
		"""Calculate total cost based on allocation and dates"""
		if self.cost_rate_per_day and self.start_date and self.end_date:
			days = date_diff(self.end_date, self.start_date) + 1
			daily_allocation = self.allocation_percentage / 100 if self.allocation_percentage else 1
			self.total_cost = days * self.cost_rate_per_day * daily_allocation