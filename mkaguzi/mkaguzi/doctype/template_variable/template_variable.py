# -*- coding: utf-8 -*-
# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, get_datetime
import json
import re

class TemplateVariable(Document):
	def validate(self):
		"""Validate template variable"""
		self.validate_variable_name()
		self.validate_default_value()
		self.validate_validation_rules()
		self.set_audit_fields()

	def validate_variable_name(self):
		"""Validate variable name format"""
		if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.variable_name):
			frappe.throw(_("Variable name must start with a letter or underscore and contain only letters, numbers, and underscores"))

		# Check for uniqueness (global variables must be unique across all, template-specific unique within template)
		if self.is_global:
			existing = frappe.db.exists("Template Variable", {
				"variable_name": self.variable_name,
				"is_global": 1,
				"name": ["!=", self.name]
			})
			if existing:
				frappe.throw(_("Global variable '{0}' already exists").format(self.variable_name))
		else:
			existing = frappe.db.exists("Template Variable", {
				"variable_name": self.variable_name,
				"template": self.template,
				"name": ["!=", self.name]
			})
			if existing:
				frappe.throw(_("Variable '{0}' already exists for this template").format(self.variable_name))

	def validate_default_value(self):
		"""Validate default value based on variable type"""
		if not self.default_value:
			return

		try:
			if self.variable_type == "Number":
				float(self.default_value)
			elif self.variable_type == "Boolean":
				if self.default_value.lower() not in ["true", "false", "1", "0"]:
					frappe.throw(_("Boolean default value must be 'true', 'false', '1', or '0'"))
			elif self.variable_type == "Date":
				# Basic date validation
				if not re.match(r'^\d{4}-\d{2}-\d{2}', self.default_value):
					frappe.throw(_("Date default value must be in YYYY-MM-DD format"))
			elif self.variable_type == "List":
				# Try to parse as JSON array
				parsed = json.loads(self.default_value)
				if not isinstance(parsed, list):
					frappe.throw(_("List default value must be a valid JSON array"))
			elif self.variable_type == "Object":
				# Try to parse as JSON object
				parsed = json.loads(self.default_value)
				if not isinstance(parsed, dict):
					frappe.throw(_("Object default value must be a valid JSON object"))
		except (ValueError, json.JSONDecodeError):
			frappe.throw(_("Invalid default value for variable type '{0}'").format(self.variable_type))

	def validate_validation_rules(self):
		"""Validate validation rules JSON"""
		if not self.validation_rules:
			return

		try:
			rules = json.loads(self.validation_rules)
			if not isinstance(rules, dict):
				frappe.throw(_("Validation rules must be a valid JSON object"))

			# Validate known rule types
			valid_rules = ["min", "max", "pattern", "required", "enum", "custom"]
			for rule in rules:
				if rule not in valid_rules:
					frappe.throw(_("Unknown validation rule: {0}").format(rule))

		except json.JSONDecodeError:
			frappe.throw(_("Validation rules must be valid JSON"))

	def set_audit_fields(self):
		"""Set audit trail fields"""
		if not self.created_by:
			self.created_by = frappe.session.user
		if not self.creation_date:
			self.creation_date = now()

		self.modified_by = frappe.session.user
		self.last_modified = get_datetime()

	def on_update(self):
		"""Handle variable updates"""
		# Update related templates if this is a global variable
		if self.has_value_changed("default_value") and self.is_global:
			self.update_global_variable_in_templates()

	def update_global_variable_in_templates(self):
		"""Update this global variable's default value in all templates that use it"""
		# This would be handled by the template rendering logic
		pass

@frappe.whitelist()
def get_template_variables(template_name=None, category=None, include_global=True):
	"""Get variables for a template or category"""
	filters = {}

	if template_name:
		filters["template"] = template_name
	if category:
		filters["category"] = category

	variables = []

	# Get template-specific variables
	if template_name:
		template_vars = frappe.get_all("Template Variable",
			filters={"template": template_name},
			fields=["name", "variable_name", "variable_type", "default_value", "description",
				   "is_required", "validation_rules", "is_global"]
		)
		variables.extend(template_vars)

	# Get category-specific variables
	if category:
		category_vars = frappe.get_all("Template Variable",
			filters={"category": category, "template": ["is", "not set"]},
			fields=["name", "variable_name", "variable_type", "default_value", "description",
				   "is_required", "validation_rules", "is_global"]
		)
		variables.extend(category_vars)

	# Get global variables
	if include_global:
		global_vars = frappe.get_all("Template Variable",
			filters={"is_global": 1},
			fields=["name", "variable_name", "variable_type", "default_value", "description",
				   "is_required", "validation_rules", "is_global"]
		)
		variables.extend(global_vars)

	# Remove duplicates (template-specific takes precedence over category and global)
	seen_names = set()
	unique_variables = []
	for var in variables:
		if var.variable_name not in seen_names:
			unique_variables.append(var)
			seen_names.add(var.variable_name)

	return unique_variables

@frappe.whitelist()
def validate_variable_value(variable_name, value, template_name=None):
	"""Validate a variable value against its rules"""
	variable = get_variable_definition(variable_name, template_name)
	if not variable:
		frappe.throw(_("Variable '{0}' not found").format(variable_name))

	# Check required
	if variable.get("is_required") and not value:
		frappe.throw(_("Variable '{0}' is required").format(variable_name))

	if not value:
		return True  # Optional variable with no value is OK

	# Type validation
	variable_type = variable.get("variable_type")
	try:
		if variable_type == "Number":
			float(value)
		elif variable_type == "Boolean":
			if str(value).lower() not in ["true", "false", "1", "0"]:
				frappe.throw(_("Variable '{0}' must be a boolean value").format(variable_name))
		elif variable_type == "Date":
			if not re.match(r'^\d{4}-\d{2}-\d{2}', str(value)):
				frappe.throw(_("Variable '{0}' must be a valid date").format(variable_name))
		elif variable_type == "List":
			parsed = json.loads(value)
			if not isinstance(parsed, list):
				frappe.throw(_("Variable '{0}' must be a valid JSON array").format(variable_name))
		elif variable_type == "Object":
			parsed = json.loads(value)
			if not isinstance(parsed, dict):
				frappe.throw(_("Variable '{0}' must be a valid JSON object").format(variable_name))
	except (ValueError, json.JSONDecodeError):
		frappe.throw(_("Invalid value for variable '{0}' of type '{1}'").format(variable_name, variable_type))

	# Custom validation rules
	if variable.get("validation_rules"):
		try:
			rules = json.loads(variable["validation_rules"])
			validate_against_rules(value, rules, variable_name)
		except json.JSONDecodeError:
			pass  # Skip if rules are malformed

	return True

def validate_against_rules(value, rules, variable_name):
	"""Validate value against custom rules"""
	if "min" in rules and isinstance(value, (int, float)):
		if float(value) < rules["min"]:
			frappe.throw(_("Variable '{0}' must be at least {1}").format(variable_name, rules["min"]))

	if "max" in rules and isinstance(value, (int, float)):
		if float(value) > rules["max"]:
			frappe.throw(_("Variable '{0}' must be at most {1}").format(variable_name, rules["max"]))

	if "pattern" in rules and isinstance(value, str):
		if not re.match(rules["pattern"], value):
			frappe.throw(_("Variable '{0}' does not match required pattern").format(variable_name))

	if "enum" in rules and isinstance(rules["enum"], list):
		if value not in rules["enum"]:
			frappe.throw(_("Variable '{0}' must be one of: {1}").format(variable_name, ", ".join(rules["enum"])))

def get_variable_definition(variable_name, template_name=None):
	"""Get variable definition by name"""
	# First try template-specific
	if template_name:
		variable = frappe.get_all("Template Variable",
			filters={"variable_name": variable_name, "template": template_name},
			fields=["name", "variable_name", "variable_type", "default_value", "description",
				   "is_required", "validation_rules", "is_global"]
		)
		if variable:
			return variable[0]

	# Then try category variables
	template = frappe.get_doc("Template Registry", template_name)
	if template.category:
		variable = frappe.get_all("Template Variable",
			filters={"variable_name": variable_name, "category": template.category, "template": ["is", "not set"]},
			fields=["name", "variable_name", "variable_type", "default_value", "description",
				   "is_required", "validation_rules", "is_global"]
		)
		if variable:
			return variable[0]

	# Finally try global variables
	variable = frappe.get_all("Template Variable",
		filters={"variable_name": variable_name, "is_global": 1},
		fields=["name", "variable_name", "variable_type", "default_value", "description",
			   "is_required", "validation_rules", "is_global"]
	)
	if variable:
		return variable[0]

	return None

@frappe.whitelist()
def create_default_variables():
	"""Create default variables for common use cases"""
	default_variables = [
		{
			"variable_name": "company_name",
			"variable_type": "Text",
			"default_value": "Your Company Name",
			"description": "Name of the company",
			"is_global": 1
		},
		{
			"variable_name": "report_date",
			"variable_type": "Date",
			"default_value": "{{ frappe.utils.today() }}",
			"description": "Date of the report",
			"is_global": 1
		},
		{
			"variable_name": "audit_period_start",
			"variable_type": "Date",
			"description": "Start date of audit period",
			"is_required": 1
		},
		{
			"variable_name": "audit_period_end",
			"variable_type": "Date",
			"description": "End date of audit period",
			"is_required": 1
		},
		{
			"variable_name": "auditor_name",
			"variable_type": "Text",
			"description": "Name of the auditor",
			"is_required": 1
		},
		{
			"variable_name": "total_findings",
			"variable_type": "Number",
			"default_value": "0",
			"description": "Total number of findings"
		},
		{
			"variable_name": "risk_level",
			"variable_type": "Select",
			"default_value": "Medium",
			"description": "Overall risk level",
			"validation_rules": json.dumps({"enum": ["Low", "Medium", "High", "Critical"]})
		}
	]

	created_variables = []

	for var_data in default_variables:
		# Check if variable already exists
		existing = frappe.db.exists("Template Variable", {
			"variable_name": var_data["variable_name"]
		})

		if not existing:
			variable = frappe.new_doc("Template Variable")
			variable.update(var_data)
			variable.save()
			created_variables.append(variable.variable_name)
			frappe.msgprint(_("Created default variable: {0}").format(variable.variable_name))

	return {"message": f"Created {len(created_variables)} default variables", "variables": created_variables}