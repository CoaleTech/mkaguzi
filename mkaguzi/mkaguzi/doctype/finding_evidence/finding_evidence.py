# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class FindingEvidence(Document):
	def validate(self):
		"""Validate evidence entry"""
		if self.evidence_type == "Data Analysis" and not self.source_reference:
			frappe.throw(_("Source Reference is required for Data Analysis evidence"))

		if self.evidence_type == "Document" and not self.attachment:
			frappe.msgprint(_("Consider attaching the document for Document evidence type"))