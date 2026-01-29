# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, add_days, date_diff, today


class DataPeriod(Document):
	def validate(self):
		"""Validate the data period"""
		self.validate_dates()
		self.validate_overlapping_periods()
		self.set_default_values()

	def validate_dates(self):
		"""Validate that end date is after start date"""
		if self.end_date and self.start_date and getdate(self.end_date) < getdate(self.start_date):
			frappe.throw(_("End Date must be after Start Date"))

	def validate_overlapping_periods(self):
		"""Validate that periods don't overlap for the same fiscal year"""
		if not self.fiscal_year or not self.start_date or not self.end_date:
			return

		existing_periods = frappe.get_all("Data Period",
			filters={
				"fiscal_year": self.fiscal_year,
				"name": ("!=", self.name) if self.name else ("!=", ""),
				"docstatus": ("!=", 2)
			},
			fields=["name", "start_date", "end_date"]
		)

		for period in existing_periods:
			if self.periods_overlap(
				getdate(self.start_date), getdate(self.end_date),
				getdate(period.start_date), getdate(period.end_date)
			):
				frappe.throw(_("This period overlaps with existing period {0}").format(period.name))

	def periods_overlap(self, start1, end1, start2, end2):
		"""Check if two date ranges overlap"""
		return not (end1 < start2 or end2 < start1)

	def set_default_values(self):
		"""Set default values"""
		if not self.period_name and self.start_date:
			# Auto-generate period name from dates if not set
			self.period_name = f"{getdate(self.start_date).strftime('%b %Y')}"

	def on_submit(self):
		"""Actions when period is submitted"""
		self.is_active = 1

	def on_cancel(self):
		"""Actions when period is cancelled"""
		pass

	def before_save(self):
		"""Actions before saving"""
		# Ensure is_closed is set properly
		if self.docstatus == 2 and not self.is_closed:
			self.is_closed = 0


@frappe.whitelist()
def get_active_data_periods(fiscal_year=None):
	"""Get all active data periods, optionally filtered by fiscal year"""
	filters = {"is_active": 1, "docstatus": 1}
	if fiscal_year:
		filters["fiscal_year"] = fiscal_year

	return frappe.get_all("Data Period",
		filters=filters,
		fields=["name", "period_name", "start_date", "end_date", "fiscal_year", "period_type", "is_closed"],
		order_by="start_date"
	)


@frappe.whitelist()
def get_current_data_period():
	"""Get the data period that contains today's date"""
	today_date = today()
	periods = frappe.get_all("Data Period",
		filters={
			"is_active": 1,
			"is_closed": 0,
			"docstatus": 1
		},
		fields=["name", "period_name", "start_date", "end_date"]
	)

	for period in periods:
		if getdate(period.start_date) <= today_date <= getdate(period.end_date):
			return period

	return None


@frappe.whitelist()
def close_data_period(period_name):
	"""Close a data period"""
	frappe.has_permission("Data Period", "write", throw=True)
	doc = frappe.get_doc("Data Period", period_name)
	doc.is_closed = 1
	doc.save()
	return {"success": True, "message": _("Data Period closed successfully")}


@frappe.whitelist()
def reopen_data_period(period_name):
	"""Reopen a closed data period"""
	frappe.has_permission("Data Period", "write", throw=True)
	doc = frappe.get_doc("Data Period", period_name)
	doc.is_closed = 0
	doc.save()
	return {"success": True, "message": _("Data Period reopened successfully")}


@frappe.whitelist()
def create_fiscal_year(year, start_date, end_date):
	"""Create a new fiscal year if it doesn't exist"""
	frappe.has_permission("Fiscal Year", "create", throw=True)

	# Check if fiscal year already exists
	existing = frappe.db.exists("Fiscal Year", year)
	if existing:
		return {"success": False, "message": _("Fiscal Year already exists"), "name": year}

	# Create fiscal year
	fy = frappe.get_doc({
		"doctype": "Fiscal Year",
		"year_name": str(year),
		"year_start_date": start_date,
		"year_end_date": end_date,
	})
	fy.insert()

	return {"success": True, "message": _("Fiscal Year created successfully"), "name": fy.name}


@frappe.whitelist()
def create_period_type(name, description=""):
	"""Create a new period type if it doesn't exist"""
	frappe.has_permission("Period Type", "create", throw=True)

	# Check if period type already exists
	existing = frappe.db.exists("Period Type", name)
	if existing:
		return {"success": False, "message": _("Period Type already exists"), "name": name}

	# Create period type
	pt = frappe.get_doc({
		"doctype": "Period Type",
		"period_type_name": name,
		"description": description
	})
	pt.insert()

	return {"success": True, "message": _("Period Type created successfully"), "name": pt.name}
