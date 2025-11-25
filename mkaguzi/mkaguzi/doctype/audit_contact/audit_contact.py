# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class AuditContact(Document):
	def validate(self):
		self.validate_primary_contact()
		self.validate_contact_info()

	def validate_primary_contact(self):
		"""Ensure only one primary contact per type"""
		if self.is_primary:
			parent = frappe.get_doc("Audit Engagement", self.parent)
			primary_contacts = [contact for contact in parent.audit_contacts
				if contact.is_primary and contact.contact_type == self.contact_type
				and contact.name != self.name]
			if primary_contacts:
				frappe.throw(_("Only one primary contact allowed per contact type"))

	def validate_contact_info(self):
		"""Validate contact information"""
		if self.email and not frappe.utils.validate_email_address(self.email):
			frappe.throw(_("Invalid email address"))

		if self.phone:
			# Basic phone validation - should contain digits and common phone characters
			import re
			if not re.match(r'^[\d\s\-\+\(\)\.]+$', self.phone):
				frappe.throw(_("Invalid phone number format"))