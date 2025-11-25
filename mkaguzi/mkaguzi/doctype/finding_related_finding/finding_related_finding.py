# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class FindingRelatedFinding(Document):
	def validate(self):
		"""Validate related finding relationship"""
		if self.related_finding:
			# Check if the related finding exists and is not the same as parent
			parent_finding = frappe.get_value("Audit Finding",
				{"name": ["!=", self.parent], "name": self.related_finding})

			if not parent_finding:
				frappe.throw(_("Related finding does not exist or cannot be the same as current finding"))

		if not self.description and self.relationship_type:
			frappe.msgprint(_("Consider adding a description for the relationship type: {0}").format(
				self.relationship_type))