# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, getdate
import re
import json

class AuditTestLibrary(Document):
	def autoname(self):
		"""Generate unique Test ID"""
		if not self.test_id:
			# Generate ATL-YYYY-NNNN format
			current_year = str(getdate(nowdate()).year)
			prefix = f"ATL-{current_year}-"

			# Get the last ATL number for this year
			last_test = frappe.db.sql("""
				SELECT test_id
				FROM `tabAudit Test Library`
				WHERE test_id LIKE %s
				ORDER BY test_id DESC
				LIMIT 1
			""", (prefix + "%",))

			if last_test:
				# Extract the number from the last ID
				last_num = int(last_test[0][0].split('-')[-1])
				next_num = last_num + 1
			else:
				next_num = 1

			# Format with leading zeros
			self.test_id = f"{prefix}{next_num:04d}"

	def validate(self):
		"""Validate test library data"""
		self.validate_test_logic()
		self.validate_parameters()
		self.validate_thresholds()
		self.set_metadata()

	def validate_test_logic(self):
		"""Validate test logic based on type"""
		if self.test_logic_type == "SQL Query" and not self.sql_query:
			frappe.throw(_("SQL Query is required for SQL Query test logic type"))

		if self.test_logic_type == "Python Script" and not self.python_script:
			frappe.throw(_("Python Script is required for Python Script test logic type"))

		if self.test_logic_type == "SQL Query":
			self.validate_sql_query()

		if self.test_logic_type == "Python Script":
			self.validate_python_script()

	def validate_sql_query(self):
		"""Basic SQL query validation"""
		if self.sql_query:
			# Check for basic SQL injection patterns (basic validation)
			dangerous_patterns = [
				r';\s*(drop|delete|update|insert|alter)\s',
				r'--\s*(drop|delete|update|insert|alter)',
				r'/\*\s*(drop|delete|update|insert|alter)'
			]

			for pattern in dangerous_patterns:
				if re.search(pattern, self.sql_query, re.IGNORECASE):
					frappe.throw(_("SQL Query contains potentially dangerous operations"))

	def validate_python_script(self):
		"""Basic Python script validation"""
		if self.python_script:
			# Check for dangerous imports
			dangerous_imports = [
				'import os', 'import sys', 'import subprocess',
				'from os import', 'from sys import', 'from subprocess import'
			]

			for imp in dangerous_imports:
				if imp in self.python_script:
					frappe.throw(_("Python script contains potentially dangerous imports"))

	def validate_parameters(self):
		"""Validate test parameters"""
		if self.test_parameters:
			param_names = []
			for param in self.test_parameters:
				if param.parameter_name in param_names:
					frappe.throw(_("Duplicate parameter name: {0}").format(param.parameter_name))
				param_names.append(param.parameter_name)

	def validate_thresholds(self):
		"""Validate threshold settings"""
		if self.threshold_settings:
			for threshold in self.threshold_settings:
				if not threshold.threshold_value and threshold.threshold_value != 0:
					frappe.throw(_("Threshold value is required for all thresholds"))

	def set_metadata(self):
		"""Set creation and modification metadata"""
		if not self.created_by:
			self.created_by = frappe.session.user
		if not self.creation_date:
			self.creation_date = nowdate()

		self.last_modified_by = frappe.session.user
		self.last_modified_date = nowdate()

	def on_update(self):
		"""Handle updates"""
		self.update_usage_stats()

	def update_usage_stats(self):
		"""Update usage statistics"""
		# This would be called when the test is executed
		pass

@frappe.whitelist()
def execute_test(test_id, parameters=None, data_source=None):
	"""Execute a test from the library"""
	try:
		test = frappe.get_doc("Audit Test Library", test_id)

		if test.status != "Active":
			frappe.throw(_("Test is not active"))

		# Prepare parameters
		test_params = {}
		if parameters:
			if isinstance(parameters, str):
				test_params = json.loads(parameters)
			else:
				test_params = parameters

		# Execute based on test logic type
		if test.test_logic_type == "SQL Query":
			result = execute_sql_test(test, test_params, data_source)
		elif test.test_logic_type == "Python Script":
			result = execute_python_test(test, test_params, data_source)
		else:
			result = execute_builtin_test(test, test_params, data_source)

		# Update usage count
		test.usage_count = (test.usage_count or 0) + 1
		test.save()

		return result

	except Exception as e:
		frappe.log_error(f"Test execution failed: {str(e)}", "Audit Test Execution")
		frappe.throw(_("Test execution failed: {0}").format(str(e)))

def execute_sql_test(test, parameters, data_source):
	"""Execute SQL-based test"""
	try:
		sql_query = test.sql_query

		# Replace parameters in query
		for param_name, param_value in parameters.items():
			placeholder = f"{{{param_name}}}"
			if placeholder in sql_query:
				sql_query = sql_query.replace(placeholder, str(param_value))

		# Execute query
		result = frappe.db.sql(sql_query, as_dict=True)

		# Apply thresholds and determine status
		status = evaluate_thresholds(test, result)

		return {
			"test_id": test.test_id,
			"test_name": test.test_name,
			"result": result,
			"status": status,
			"execution_time": frappe.utils.now()
		}

	except Exception as e:
		frappe.throw(_("SQL test execution failed: {0}").format(str(e)))

def execute_python_test(test, parameters, data_source):
	"""Execute Python script test"""
	try:
		# This would require careful sandboxing in production
		# For now, we'll just validate the script exists
		if not test.python_script:
			frappe.throw(_("Python script not found"))

		# In a real implementation, this would execute the script in a sandbox
		return {
			"test_id": test.test_id,
			"test_name": test.test_name,
			"result": "Python execution not implemented in sandbox",
			"status": "Pending",
			"execution_time": frappe.utils.now()
		}

	except Exception as e:
		frappe.throw(_("Python test execution failed: {0}").format(str(e)))

def execute_builtin_test(test, parameters, data_source):
	"""Execute built-in test function"""
	try:
		# Map test categories to built-in functions
		builtin_functions = {
			"Duplicate Detection": detect_duplicates,
			"Outlier Analysis": analyze_outliers,
			"Trend Analysis": analyze_trends,
			"Completeness Check": check_completeness,
			"Validity Check": check_validity
		}

		if test.test_category in builtin_functions:
			func = builtin_functions[test.test_category]
			result = func(test, parameters, data_source)
		else:
			frappe.throw(_("Built-in function not found for category: {0}").format(test.test_category))

		# Apply thresholds
		status = evaluate_thresholds(test, result)

		return {
			"test_id": test.test_id,
			"test_name": test.test_name,
			"result": result,
			"status": status,
			"execution_time": frappe.utils.now()
		}

	except Exception as e:
		frappe.throw(_("Built-in test execution failed: {0}").format(str(e)))

def evaluate_thresholds(test, result):
	"""Evaluate test results against thresholds"""
	if not test.threshold_settings:
		return "Pass"

	status = "Pass"
	highest_severity = "Low"

	for threshold in test.threshold_settings:
		# Get the value to compare (this would depend on result structure)
		actual_value = extract_threshold_value(result, threshold.threshold_name)

		if actual_value is None:
			continue

		threshold_value = threshold.threshold_value

		# Compare based on operator
		comparison_result = False
		if threshold.comparison_operator == ">":
			comparison_result = actual_value > threshold_value
		elif threshold.comparison_operator == "<":
			comparison_result = actual_value < threshold_value
		elif threshold.comparison_operator == ">=":
			comparison_result = actual_value >= threshold_value
		elif threshold.comparison_operator == "<=":
			comparison_result = actual_value <= threshold_value
		elif threshold.comparison_operator == "==":
			comparison_result = actual_value == threshold_value

		if comparison_result:
			status = "Fail"
			if threshold.notification_level == "Critical":
				highest_severity = "Critical"
			elif threshold.notification_level == "Error" and highest_severity != "Critical":
				highest_severity = "High"
			elif threshold.notification_level == "Warning" and highest_severity not in ["Critical", "High"]:
				highest_severity = "Medium"

	return status

def extract_threshold_value(result, threshold_name):
	"""Extract value from result for threshold comparison"""
	# This is a simplified implementation
	# In reality, this would need to parse the result structure
	if isinstance(result, list) and len(result) > 0:
		if threshold_name.lower() == "count":
			return len(result)
		elif threshold_name.lower() == "percentage":
			# Calculate percentage based on result structure
			return 0
		else:
			# Try to find the value in the first result row
			if isinstance(result[0], dict):
				return result[0].get(threshold_name)

	return None

# Built-in test functions
def detect_duplicates(test, parameters, data_source):
	"""Built-in duplicate detection"""
	# This would implement duplicate detection logic
	return []

def analyze_outliers(test, parameters, data_source):
	"""Built-in outlier analysis"""
	# This would implement outlier detection logic
	return []

def analyze_trends(test, parameters, data_source):
	"""Built-in trend analysis"""
	# This would implement trend analysis logic
	return []

def check_completeness(test, parameters, data_source):
	"""Built-in completeness check"""
	# This would implement completeness checking logic
	return []

def check_validity(test, parameters, data_source):
	"""Built-in validity check"""
	# This would implement validity checking logic
	return []

@frappe.whitelist()
def get_tests_by_category(category=None, risk_area=None):
	"""Get tests filtered by category and risk area"""
	filters = {"status": "Active"}

	if category:
		filters["test_category"] = category
	if risk_area:
		filters["risk_area"] = risk_area

	return frappe.get_all("Audit Test Library",
		filters=filters,
		fields=["name", "test_id", "test_name", "test_category", "description", "usage_count"],
		order_by="usage_count desc"
	)

@frappe.whitelist()
def create_sample_templates():
	"""Create sample audit test templates"""
	test_templates = [
		{
			"test_name": "Duplicate Invoice Detection",
			"test_category": "Duplicate Detection",
			"sub_category": "Invoice Processing",
			"description": "Detects duplicate invoices based on invoice number, amount, and vendor",
			"objective": "Identify potential duplicate payments or invoice processing errors",
			"risk_area": "Accounts Payable",
			"data_source_type": "Database Table",
			"test_logic_type": "SQL Query",
			"sql_query": """
				SELECT
					invoice_number,
					vendor_id,
					invoice_amount,
					invoice_date,
					COUNT(*) as duplicate_count
				FROM `tabPurchase Invoice`
				WHERE invoice_date BETWEEN '{{start_date}}' AND '{{end_date}}'
				GROUP BY invoice_number, vendor_id, invoice_amount
				HAVING COUNT(*) > 1
				ORDER BY duplicate_count DESC
			""",
			"result_interpretation": "Any records returned indicate potential duplicate invoices that should be investigated for validity."
		},
		{
			"test_name": "Journal Entry Outlier Analysis",
			"test_category": "Outlier Analysis",
			"sub_category": "Financial Transactions",
			"description": "Identifies unusual journal entries based on amount thresholds",
			"objective": "Detect potentially fraudulent or erroneous journal entries",
			"risk_area": "General Ledger",
			"data_source_type": "Database Table",
			"test_logic_type": "SQL Query",
			"sql_query": """
				SELECT
					name,
					posting_date,
					total_debit,
					total_credit,
					user_remark
				FROM `tabJournal Entry`
				WHERE docstatus = 1
				AND posting_date BETWEEN '{{start_date}}' AND '{{end_date}}'
				AND (total_debit > {{threshold_amount}} OR total_credit > {{threshold_amount}})
				ORDER BY GREATEST(total_debit, total_credit) DESC
			""",
			"result_interpretation": "Review high-value journal entries for proper authorization and business justification."
		},
		{
			"test_name": "Vendor Master Completeness Check",
			"test_category": "Completeness Check",
			"sub_category": "Master Data",
			"description": "Checks vendor master data for missing required fields",
			"objective": "Ensure vendor data completeness for accurate processing",
			"risk_area": "Accounts Payable",
			"data_source_type": "Database Table",
			"test_logic_type": "SQL Query",
			"sql_query": """
				SELECT
					name,
					supplier_name,
					CASE WHEN tax_id IS NULL OR tax_id = '' THEN 'Missing Tax ID' ELSE 'OK' END as tax_id_status,
					CASE WHEN supplier_group IS NULL OR supplier_group = '' THEN 'Missing Supplier Group' ELSE 'OK' END as group_status
				FROM `tabSupplier`
				WHERE disabled = 0
				AND (tax_id IS NULL OR tax_id = '' OR supplier_group IS NULL OR supplier_group = '')
			""",
			"result_interpretation": "Records with missing required fields should be updated to ensure proper vendor management."
		}
	]

	created_count = 0
	for template_data in test_templates:
		try:
			# Check if test already exists
			existing = frappe.db.exists("Audit Test Library", {"test_name": template_data["test_name"]})
			if existing:
				continue

			# Create new test
			test = frappe.new_doc("Audit Test Library")

			# Set basic fields
			for key, value in template_data.items():
				setattr(test, key, value)

			# Set metadata
			test.is_template = 1
			test.status = "Active"

			# Save the test
			test.insert()
			created_count += 1

		except Exception as e:
			frappe.log_error(f"Error creating test template: {str(e)}", "Sample Template Creation")
			continue

	return f"Created {created_count} sample test templates"