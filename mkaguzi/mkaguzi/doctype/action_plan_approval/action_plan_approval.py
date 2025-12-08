# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

class ActionPlanApproval(Document):
	def validate(self):
		"""Validate approval entry"""
		self.validate_approver_role()

	def validate_approver_role(self):
		"""Validate that approver has the required role"""
		if self.required_role:
			user_roles = frappe.get_roles(self.approver)
			if self.required_role not in user_roles:
				frappe.throw(_("Approver {0} does not have the required role: {1}").format(
					self.approver, self.required_role))

	def before_save(self):
		"""Set approval date when status changes"""
		if self.approval_status in ["Approved", "Rejected"] and not self.approval_date:
			self.approval_date = now_datetime()