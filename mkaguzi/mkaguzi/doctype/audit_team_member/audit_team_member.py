# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class AuditTeamMember(Document):
	def validate(self):
		self.set_team_member_name()
		self.validate_dates()
		self.validate_lead_role()

	def set_team_member_name(self):
		"""Set team member name from User record"""
		if self.team_member and not self.team_member_name:
			user = frappe.get_doc("User", self.team_member)
			self.team_member_name = user.full_name

	def validate_dates(self):
		"""Validate start and end dates"""
		if self.start_date and self.end_date:
			if self.end_date < self.start_date:
				frappe.throw(_("End date cannot be before start date"))

	def validate_lead_role(self):
		"""Ensure only one lead per engagement"""
		if self.is_lead:
			parent = frappe.get_doc("Audit Engagement", self.parent)
			leads = [member for member in parent.audit_team if member.is_lead and member.name != self.name]
			if leads:
				frappe.throw(_("Only one team member can be designated as lead"))