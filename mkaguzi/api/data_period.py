# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, today


@frappe.whitelist()
def get_data_periods(filters=None):
	"""
	Get all data periods with optional filters

	Args:
		filters (dict): Optional filters like fiscal_year, is_active, is_closed

	Returns:
		list: List of data period documents
	"""
	default_filters = {"docstatus": 1}
	if filters:
		default_filters.update(filters)

	return frappe.get_all("Data Period",
		filters=default_filters,
		fields=["name", "period_name", "start_date", "end_date", "fiscal_year",
			"period_type", "is_active", "is_closed", "description", "creation", "modified"],
		order_by="start_date desc"
	)


@frappe.whitelist()
def get_data_period_details(period_name):
	"""
	Get detailed information about a specific data period

	Args:
		period_name (str): Name of the data period

	Returns:
		dict: Data period details
	"""
	frappe.has_permission("Data Period", "read", throw=True)

	doc = frappe.get_doc("Data Period", period_name)
	return {
		"name": doc.name,
		"period_name": doc.period_name,
		"start_date": doc.start_date,
		"end_date": doc.end_date,
		"fiscal_year": doc.fiscal_year,
		"period_type": doc.period_type,
		"is_active": doc.is_active,
		"is_closed": doc.is_closed,
		"description": doc.description,
		"docstatus": doc.docstatus,
		"owner": doc.owner,
		"creation": doc.creation,
		"modified": doc.modified
	}


@frappe.whitelist()
def create_data_period(period_name, start_date, end_date, fiscal_year=None, period_type=None, description=""):
	"""
	Create a new data period

	Args:
		period_name (str): Name of the period
		start_date (str): Start date
		end_date (str): End date
		fiscal_year (str): Optional fiscal year
		period_type (str): Optional period type
		description (str): Optional description

	Returns:
		dict: Success status and message
	"""
	frappe.has_permission("Data Period", "create", throw=True)

	doc = frappe.get_doc({
		"doctype": "Data Period",
		"period_name": period_name,
		"start_date": start_date,
		"end_date": end_date,
		"fiscal_year": fiscal_year,
		"period_type": period_type,
		"description": description,
		"is_active": 1
	})
	doc.insert()

	return {
		"success": True,
		"message": _("Data Period created successfully"),
		"name": doc.name
	}


@frappe.whitelist()
def update_data_period(period_name, **kwargs):
	"""
	Update an existing data period

	Args:
		period_name (str): Name of the period to update
		**kwargs: Fields to update

	Returns:
		dict: Success status and message
	"""
	frappe.has_permission("Data Period", "write", throw=True)

	doc = frappe.get_doc("Data Period", period_name)

	for field, value in kwargs.items():
		if hasattr(doc, field):
			setattr(doc, field, value)

	doc.save()

	return {
		"success": True,
		"message": _("Data Period updated successfully"),
		"name": doc.name
	}


@frappe.whitelist()
def delete_data_period(period_name):
	"""
	Delete a data period

	Args:
		period_name (str): Name of the period to delete

	Returns:
		dict: Success status and message
	"""
	frappe.has_permission("Data Period", "delete", throw=True)

	frappe.delete_doc("Data Period", period_name)

	return {
		"success": True,
		"message": _("Data Period deleted successfully")
	}


@frappe.whitelist()
def get_fiscal_years():
	"""
	Get all available fiscal years

	Returns:
		list: List of fiscal years
	"""
	return frappe.get_all("Fiscal Year",
		fields=["name", "year_start_date", "year_end_date"],
		order_by="year_start_date desc"
	)


@frappe.whitelist()
def create_fiscal_year(year, start_date, end_date):
	"""
	Create a new fiscal year

	Args:
		year (str): Year name (e.g., "2025")
		start_date (str): Start date
		end_date (str): End date

	Returns:
		dict: Success status and message
	"""
	frappe.has_permission("Fiscal Year", "create", throw=True)

	# Check if fiscal year already exists
	existing = frappe.db.exists("Fiscal Year", str(year))
	if existing:
		return {
			"success": False,
			"message": _("Fiscal Year already exists"),
			"name": str(year)
		}

	# Create fiscal year
	fy = frappe.get_doc({
		"doctype": "Fiscal Year",
		"year_name": str(year),
		"year_start_date": start_date,
		"year_end_date": end_date,
	})
	fy.insert()

	return {
		"success": True,
		"message": _("Fiscal Year created successfully"),
		"name": fy.name
	}


@frappe.whitelist()
def get_period_types():
	"""
	Get all available period types

	Returns:
		list: List of period types
	"""
	return frappe.get_all("Period Type",
		fields=["name", "period_type_name", "description"],
		order_by="name"
	)


@frappe.whitelist()
def create_period_type(name, description=""):
	"""
	Create a new period type

	Args:
		name (str): Period type name
		description (str): Optional description

	Returns:
		dict: Success status and message
	"""
	frappe.has_permission("Period Type", "create", throw=True)

	# Check if period type already exists
	existing = frappe.db.exists("Period Type", str(name))
	if existing:
		return {
			"success": False,
			"message": _("Period Type already exists"),
			"name": str(name)
		}

	# Create period type
	pt = frappe.get_doc({
		"doctype": "Period Type",
		"period_type_name": str(name),
		"description": description
	})
	pt.insert()

	return {
		"success": True,
		"message": _("Period Type created successfully"),
		"name": pt.name
	}


@frappe.whitelist()
def get_period_settings():
	"""
	Get data period system settings

	Returns:
		dict: System settings for data periods
	"""
	return {
		"allow_overlapping_periods": frappe.db.get_single_value("Mkaguzi Settings", "allow_overlapping_periods") or 0,
		"auto_close_previous": frappe.db.get_single_value("Mkaguzi Settings", "auto_close_previous_period") or 0,
		"default_period_type": frappe.db.get_single_value("Mkaguzi Settings", "default_period_type")
	}


@frappe.whitelist()
def save_period_settings(settings):
	"""
	Save data period system settings

	Args:
		settings (dict): Settings to save

	Returns:
		dict: Success status and message
	"""
	frappe.has_permission("Mkaguzi Settings", "write", throw=True)

	doc = frappe.get_single("Mkaguzi Settings")
	if "allow_overlapping_periods" in settings:
		doc.allow_overlapping_periods = settings["allow_overlapping_periods"]
	if "auto_close_previous" in settings:
		doc.auto_close_previous_period = settings["auto_close_previous"]
	if "default_period_type" in settings:
		doc.default_period_type = settings["default_period_type"]

	doc.save()

	return {
		"success": True,
		"message": _("Settings saved successfully")
	}


@frappe.whitelist()
def export_data_periods(filters=None):
	"""
	Export data periods to CSV

	Args:
		filters (dict): Optional filters

	Returns:
		dict: Export data
	"""
	frappe.has_permission("Data Period", "export", throw=True)

	periods = get_data_periods(filters)

	return {
		"data": periods,
		"columns": ["name", "period_name", "start_date", "end_date", "fiscal_year",
			"period_type", "is_active", "is_closed"]
	}
