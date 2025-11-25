# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import json

class DashboardChart(Document):
	def validate(self):
		"""Validate chart configuration"""
		self.validate_chart_type()
		self.validate_data_mapping()
		self.set_default_properties()

	def validate_chart_type(self):
		"""Validate chart type and required fields"""
		valid_types = ["Bar Chart", "Line Chart", "Pie Chart", "Area Chart", "Scatter Plot", "Heat Map", "Gauge", "Table"]

		if self.chart_type not in valid_types:
			frappe.throw(_("Invalid chart type. Valid types: {0}").format(", ".join(valid_types)))

		# Validate required fields based on chart type
		if self.chart_type in ["Bar Chart", "Line Chart", "Area Chart", "Scatter Plot"]:
			if not self.x_axis_field or not self.y_axis_field:
				frappe.throw(_("X-axis and Y-axis fields are required for {0}").format(self.chart_type))

		if self.chart_type == "Pie Chart":
			if not self.value_field:
				frappe.throw(_("Value field is required for Pie Chart"))

	def validate_data_mapping(self):
		"""Validate data field mappings"""
		if self.data_mapping:
			try:
				mapping = json.loads(self.data_mapping)
				# Basic validation - could be enhanced
			except json.JSONDecodeError:
				frappe.throw(_("Invalid JSON in data mapping"))

	def set_default_properties(self):
		"""Set default chart properties"""
		if not self.width:
			self.width = 6  # Default half width
		if not self.height:
			self.height = 4  # Default height

		# Set default color scheme if not specified
		if not self.color_scheme:
			self.color_scheme = "Default"

	def before_save(self):
		"""Handle before save operations"""
		if not self.chart_id:
			# Generate unique chart ID
			import uuid
			self.chart_id = str(uuid.uuid4())[:8].upper()

@frappe.whitelist()
def get_chart_types():
	"""Get available chart types"""
	return [
		{"value": "Bar Chart", "label": "Bar Chart"},
		{"value": "Line Chart", "label": "Line Chart"},
		{"value": "Pie Chart", "label": "Pie Chart"},
		{"value": "Area Chart", "label": "Area Chart"},
		{"value": "Scatter Plot", "label": "Scatter Plot"},
		{"value": "Heat Map", "label": "Heat Map"},
		{"value": "Gauge", "label": "Gauge"},
		{"value": "Table", "label": "Data Table"}
	]

@frappe.whitelist()
def get_color_schemes():
	"""Get available color schemes"""
	return [
		{"value": "Default", "label": "Default"},
		{"value": "Blue", "label": "Blue Theme"},
		{"value": "Green", "label": "Green Theme"},
		{"value": "Red", "label": "Red Theme"},
		{"value": "Purple", "label": "Purple Theme"},
		{"value": "Orange", "label": "Orange Theme"},
		{"value": "Gray", "label": "Gray Theme"}
	]

@frappe.whitelist()
def preview_chart(chart_name):
	"""Generate chart preview data"""
	try:
		chart = frappe.get_doc("Dashboard Chart", chart_name)

		# Generate sample data based on chart type
		if chart.chart_type == "Bar Chart":
			sample_data = [
				{"label": "Category A", "value": 45},
				{"label": "Category B", "value": 32},
				{"label": "Category C", "value": 67},
				{"label": "Category D", "value": 23}
			]
		elif chart.chart_type == "Line Chart":
			sample_data = [
				{"date": "2024-01-01", "value": 10},
				{"date": "2024-01-02", "value": 15},
				{"date": "2024-01-03", "value": 8},
				{"date": "2024-01-04", "value": 22}
			]
		elif chart.chart_type == "Pie Chart":
			sample_data = [
				{"label": "Passed", "value": 75},
				{"label": "Failed", "value": 15},
				{"label": "Pending", "value": 10}
			]
		else:
			sample_data = []

		return {
			"chart_type": chart.chart_type,
			"title": chart.chart_title,
			"data": sample_data,
			"config": {
				"show_legend": chart.show_legend,
				"show_grid": chart.show_grid,
				"color_scheme": chart.color_scheme
			}
		}

	except Exception as e:
		frappe.throw(_("Chart preview failed: {0}").format(str(e)))