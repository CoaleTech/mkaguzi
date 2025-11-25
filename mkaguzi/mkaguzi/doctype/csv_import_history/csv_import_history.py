# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CSVImportHistory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from mkaguzi.mkaguzi.doctype.execution_log.execution_log import ExecutionLog

		completed_at: DF.Datetime | None
		duration: DF.Data | None
		error_message: DF.Text | None
		execution_logs: DF.Table[ExecutionLog]
		file_name: DF.Data | None
		import_type: DF.Link
		import_type_name: DF.Data | None
		records_failed: DF.Int
		records_processed: DF.Int
		started_at: DF.Datetime
		status: DF.Literal["Pending", "Processing", "Success", "Failed", "Cancelled"]
		success_rate: DF.Percent
		total_records: DF.Int

	# end: auto-generated types

	def before_save(self):
		# Calculate duration if completed_at is set
		if self.completed_at and self.started_at:
			from datetime import datetime
			start = datetime.fromisoformat(str(self.started_at).replace('Z', '+00:00'))
			end = datetime.fromisoformat(str(self.completed_at).replace('Z', '+00:00'))
			duration_seconds = (end - start).total_seconds()

			if duration_seconds < 60:
				self.duration = f"{int(duration_seconds)}s"
			elif duration_seconds < 3600:
				minutes = int(duration_seconds // 60)
				seconds = int(duration_seconds % 60)
				self.duration = f"{minutes}m {seconds}s"
			else:
				hours = int(duration_seconds // 3600)
				minutes = int((duration_seconds % 3600) // 60)
				self.duration = f"{hours}h {minutes}m"

		# Calculate success rate
		if self.total_records and self.total_records > 0:
			if self.records_processed is None:
				self.records_processed = 0
			if self.records_failed is None:
				self.records_failed = 0

			successful_records = self.records_processed - self.records_failed
			self.success_rate = (successful_records / self.total_records) * 100

	def validate(self):
		# Set import_type_name from the linked import type
		if self.import_type and not self.import_type_name:
			import_type_doc = frappe.get_doc("CSV Import Type", self.import_type)
			self.import_type_name = import_type_doc.import_name

		# Validate records
		if self.records_processed and self.total_records:
			if self.records_processed > self.total_records:
				frappe.throw("Records processed cannot be greater than total records")

		if self.records_failed and self.records_processed:
			if self.records_failed > self.records_processed:
				frappe.throw("Records failed cannot be greater than records processed")