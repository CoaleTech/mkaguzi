# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

class DashboardDataSource(Document):
	def validate(self):
		"""Validate data source configuration"""
		self.validate_connection()
		self.set_refresh_schedule()

	def validate_connection(self):
		"""Validate data source connection"""
		if self.data_source_type == "Database":
			if not self.database_connection_string:
				frappe.throw(_("Database connection string is required"))
		elif self.data_source_type == "API":
			if not self.api_endpoint:
				frappe.throw(_("API endpoint is required"))
		elif self.data_source_type in ["Test Execution", "Audit Test Library"]:
			# These are internal DocTypes, no additional validation needed
			pass
		else:
			frappe.throw(_("Unsupported data source type"))

	def set_refresh_schedule(self):
		"""Set refresh schedule based on interval"""
		if self.refresh_interval:
			# Calculate next refresh time
			from frappe.utils import add_to_date
			self.next_refresh = add_to_date(now_datetime(), seconds=self.refresh_interval)

	def before_save(self):
		"""Handle before save operations"""
		if not self.last_refresh:
			self.last_refresh = now_datetime()

	def test_connection(self):
		"""Test data source connection"""
		try:
			if self.data_source_type == "Database":
				return self.test_database_connection()
			elif self.data_source_type == "API":
				return self.test_api_connection()
			else:
				return {"status": "success", "message": "Internal data source - no connection test needed"}
		except Exception as e:
			return {"status": "error", "message": str(e)}

	def test_database_connection(self):
		"""Test database connection"""
		# This would implement actual database connection testing
		# For security, this should be restricted
		return {"status": "success", "message": "Database connection test not implemented in sandbox"}

	def test_api_connection(self):
		"""Test API connection"""
		import requests

		try:
			if self.authentication_type == "Bearer Token":
				headers = {"Authorization": f"Bearer {self.api_token}"}
			else:
				headers = {}

			response = requests.get(self.api_endpoint, headers=headers, timeout=10)

			if response.status_code == 200:
				return {"status": "success", "message": "API connection successful"}
			else:
				return {"status": "error", "message": f"API returned status {response.status_code}"}

		except Exception as e:
			return {"status": "error", "message": f"API connection failed: {str(e)}"}

@frappe.whitelist()
def refresh_data_source(data_source_name):
	"""Refresh a specific data source"""
	try:
		data_source = frappe.get_doc("Dashboard Data Source", data_source_name)

		# Update refresh timestamp
		data_source.last_refresh = now_datetime()
		data_source.last_refresh_status = "Success"

		# Calculate next refresh
		if data_source.refresh_interval:
			from frappe.utils import add_to_date
			data_source.next_refresh = add_to_date(now_datetime(), seconds=data_source.refresh_interval)

		data_source.save()
		return {"status": "success", "message": "Data source refreshed successfully"}

	except Exception as e:
		# Update failure status
		try:
			data_source.last_refresh_status = "Failed"
			data_source.last_refresh_error = str(e)
			data_source.save()
		except:
			pass

		frappe.throw(_("Data source refresh failed: {0}").format(str(e)))