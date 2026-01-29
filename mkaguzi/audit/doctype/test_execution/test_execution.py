# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, now_datetime, getdate, time_diff_in_seconds, cint
import json
import time
import psutil
import os
from frappe.utils.background_jobs import enqueue

class TestExecution(Document):
	def autoname(self):
		"""Generate unique Execution ID"""
		if not self.execution_id:
			# Generate TEX-YYYY-NNNN format
			current_year = str(getdate(nowdate()).year)
			prefix = f"TEX-{current_year}-"

			# Get the last TEX number for this year
			last_execution = frappe.db.sql("""
				SELECT execution_id
				FROM `tabTest Execution`
				WHERE execution_id LIKE %s
				ORDER BY execution_id DESC
				LIMIT 1
			""", (prefix + "%",))

			if last_execution:
				# Extract the number from the last ID
				last_num = int(last_execution[0][0].split('-')[-1])
				next_num = last_num + 1
			else:
				next_num = 1

			# Format with leading zeros
			self.execution_id = f"{prefix}{next_num:04d}"

	def validate(self):
		"""Validate test execution data"""
		self.validate_test_library()
		self.validate_parameters()
		self.set_metadata()

	def validate_test_library(self):
		"""Validate test library reference"""
		if self.test_library_reference:
			test_lib = frappe.get_doc("Audit Test Library", self.test_library_reference)
			if test_lib.status != "Active":
				frappe.throw(_("Cannot execute inactive test: {0}").format(test_lib.test_name))

	def validate_parameters(self):
		"""Validate execution parameters"""
		if self.execution_parameters:
			param_names = []
			for param in self.execution_parameters:
				if param.parameter_name in param_names:
					frappe.throw(_("Duplicate parameter name: {0}").format(param.parameter_name))
				param_names.append(param.parameter_name)

	def set_metadata(self):
		"""Set creation and modification metadata"""
		if not self.created_by:
			self.created_by = frappe.session.user
		if not self.creation_date:
			self.creation_date = now_datetime()

		self.last_modified_by = frappe.session.user
		self.last_modified_date = now_datetime()

	def before_save(self):
		"""Handle status changes and validation"""
		if self.status == "Running" and not self.actual_start_date:
			self.actual_start_date = now_datetime()

		if self.status in ["Completed", "Failed", "Cancelled"] and not self.actual_end_date:
			self.actual_end_date = now_datetime()
			if self.actual_start_date:
				self.duration_seconds = time_diff_in_seconds(self.actual_end_date, self.actual_start_date)

	def on_update(self):
		"""Handle updates and trigger actions"""
		if self.status == "Queued":
			self.enqueue_execution()
		elif self.status == "Running":
			self.start_execution()
		elif self.status in ["Completed", "Failed"]:
			self.finalize_execution()

	def enqueue_execution(self):
		"""Enqueue the test execution for background processing"""
		if self.execution_type in ["Scheduled", "Batch"]:
			enqueue(
				"mkaguzi.mkaguzi.doctype.test_execution.test_execution.execute_test_background",
				queue="long",
				timeout=3600,  # 1 hour timeout
				execution_id=self.name
			)

	def start_execution(self):
		"""Start the test execution"""
		try:
			self.log_execution("INFO", "Starting test execution", "Initialization")

			# Get test library
			test_lib = frappe.get_doc("Audit Test Library", self.test_library_reference)

			# Prepare parameters
			execution_params = {}
			if self.execution_parameters:
				for param in self.execution_parameters:
					execution_params[param.parameter_name] = param.parameter_value

			# Execute test
			start_time = time.time()
			result = self.execute_test(test_lib, execution_params)
			end_time = time.time()

			# Update performance metrics
			self.execution_time_ms = int((end_time - start_time) * 1000)
			self.records_per_second = self.total_records_processed / ((end_time - start_time) or 1)
			self.memory_usage_mb = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
			self.cpu_usage_percent = psutil.cpu_percent(interval=1)

			# Process results
			self.process_test_results(result)

			# Update status
			if self.failed_tests > 0:
				self.status = "Failed"
			else:
				self.status = "Completed"

			self.log_execution("INFO", f"Test execution completed in {self.execution_time_ms}ms", "Completion")

		except Exception as e:
			self.status = "Failed"
			self.error_details = str(e)
			self.log_execution("ERROR", f"Test execution failed: {str(e)}", "Error Handling")
			frappe.log_error(f"Test execution failed: {str(e)}", "Test Execution")

		self.save()

	def execute_test(self, test_lib, parameters):
		"""Execute the test using the test library"""
		from mkaguzi.mkaguzi.doctype.audit_test_library.audit_test_library import execute_test

		# Execute the test
		result = execute_test(test_lib.name, parameters)

		return result

	def process_test_results(self, result):
		"""Process and store test results"""
		if not result:
			return

		# Clear existing results
		self.test_results = []

		# Add test result
		test_result = {
			"test_name": result.get("test_name", "Unknown Test"),
			"test_status": result.get("status", "Unknown"),
			"execution_time_ms": result.get("execution_time_ms", 0),
			"records_processed": len(result.get("result", [])) if isinstance(result.get("result"), list) else 0,
			"result_data": json.dumps(result.get("result", {})),
			"threshold_breached": result.get("status") in ["Fail", "Warning"]
		}

		self.append("test_results", test_result)

		# Update summary
		self.total_tests = 1
		if result.get("status") == "Pass":
			self.passed_tests = 1
			self.failed_tests = 0
			self.warning_tests = 0
		elif result.get("status") == "Fail":
			self.passed_tests = 0
			self.failed_tests = 1
			self.warning_tests = 0
		elif result.get("status") == "Warning":
			self.passed_tests = 0
			self.failed_tests = 0
			self.warning_tests = 1
		else:
			self.passed_tests = 0
			self.failed_tests = 0
			self.warning_tests = 0

		# Update records processed
		if isinstance(result.get("result"), list):
			self.total_records_processed = len(result.get("result"))
			# Count exceptions (simplified logic)
			self.exceptions_found = sum(1 for r in result.get("result", []) if isinstance(r, dict) and r.get("exception_found"))

	def finalize_execution(self):
		"""Finalize the execution and update related records"""
		# Update test library usage statistics
		if self.test_library_reference:
			test_lib = frappe.get_doc("Audit Test Library", self.test_library_reference)
			test_lib.usage_count = (test_lib.usage_count or 0) + 1

			if self.status == "Completed":
				current_success = test_lib.success_rate or 0
				test_lib.success_rate = ((current_success * (test_lib.usage_count - 1)) + 100) / test_lib.usage_count
			else:
				current_success = test_lib.success_rate or 0
				test_lib.success_rate = (current_success * (test_lib.usage_count - 1)) / test_lib.usage_count

			test_lib.save()

	def log_execution(self, level, message, step_name=None, duration_ms=None):
		"""Log execution steps"""
		if not self.execution_logs:
			self.execution_logs = []

		log_entry = {
			"timestamp": now_datetime(),
			"log_level": level,
			"message": message,
			"step_name": step_name,
			"duration_ms": duration_ms
		}

		self.append("execution_logs", log_entry)

@frappe.whitelist()
def execute_test_background(execution_id):
	"""Background job to execute test"""
	try:
		execution = frappe.get_doc("Test Execution", execution_id)
		execution.start_execution()
	except Exception as e:
		frappe.log_error(f"Background test execution failed: {str(e)}", "Test Execution Background")

@frappe.whitelist()
def create_test_execution(test_library_id, execution_name=None, parameters=None, execution_type="Manual"):
	"""Create a new test execution"""
	try:
		# Validate test library
		test_lib = frappe.get_doc("Audit Test Library", test_library_id)
		if test_lib.status != "Active":
			frappe.throw(_("Cannot execute inactive test"))

		# Create execution
		execution = frappe.new_doc("Test Execution")
		execution.test_library_reference = test_library_id
		execution.execution_name = execution_name or f"Execution of {test_lib.test_name}"
		execution.execution_type = execution_type
		execution.status = "Pending"

		# Add default parameters from test library
		if test_lib.test_parameters:
			for param in test_lib.test_parameters:
				execution.append("execution_parameters", {
					"parameter_name": param.parameter_name,
					"parameter_value": param.default_value or "",
					"parameter_type": param.parameter_type,
					"description": param.description
				})

		# Override with provided parameters
		if parameters:
			if isinstance(parameters, str):
				parameters = json.loads(parameters)

			for param_name, param_value in parameters.items():
				# Find existing parameter or add new one
				found = False
				for param in execution.execution_parameters:
					if param.parameter_name == param_name:
						param.parameter_value = param_value
						found = True
						break

				if not found:
					execution.append("execution_parameters", {
						"parameter_name": param_name,
						"parameter_value": param_value
					})

		execution.insert()

		# Auto-start if manual execution
		if execution_type == "Manual":
			execution.status = "Running"
			execution.save()

		return execution.name

	except Exception as e:
		frappe.throw(_("Failed to create test execution: {0}").format(str(e)))

@frappe.whitelist()
def get_execution_status(execution_id):
	"""Get current execution status"""
	execution = frappe.get_doc("Test Execution", execution_id)
	return {
		"status": execution.status,
		"progress_percentage": execution.progress_percentage,
		"total_tests": execution.total_tests,
		"passed_tests": execution.passed_tests,
		"failed_tests": execution.failed_tests,
		"duration_seconds": execution.duration_seconds
	}

@frappe.whitelist()
def cancel_execution(execution_id):
	"""Cancel a running execution"""
	execution = frappe.get_doc("Test Execution", execution_id)
	if execution.status in ["Pending", "Queued", "Running"]:
		execution.status = "Cancelled"
		execution.actual_end_date = now_datetime()
		execution.log_execution("INFO", "Execution cancelled by user", "Cancellation")
		execution.save()
		return True
	else:
		frappe.throw(_("Cannot cancel execution with status: {0}").format(execution.status))

@frappe.whitelist()
def retry_execution(execution_id):
	"""Retry a failed execution"""
	execution = frappe.get_doc("Test Execution", execution_id)
	if execution.status == "Failed":
		# Reset execution
		execution.status = "Pending"
		execution.actual_start_date = None
		execution.actual_end_date = None
		execution.duration_seconds = 0
		execution.progress_percentage = 0
		execution.error_details = ""
		execution.test_results = []
		execution.execution_logs = []

		execution.log_execution("INFO", "Execution retry initiated", "Retry")
		execution.save()
		return True
	else:
		frappe.throw(_("Can only retry failed executions"))

@frappe.whitelist()
def get_execution_history(test_library_id=None, limit=50):
	"""Get execution history"""
	filters = {}
	if test_library_id:
		filters["test_library_reference"] = test_library_id

	return frappe.get_all("Test Execution",
		filters=filters,
		fields=[
			"name", "execution_id", "execution_name", "status",
			"actual_start_date", "duration_seconds", "total_tests",
			"passed_tests", "failed_tests", "created_by"
		],
		order_by="creation desc",
		limit=limit
	)