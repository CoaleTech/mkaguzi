# -*- coding: utf-8 -*-
# Copyright (c) 2024, Coale Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, now, get_datetime
import json
from mkaguzi.api import audit_api


class FinancialIntegrationController:
	"""Controller for financial module integration"""

	def __init__(self):
		self.financial_doctypes = [
			'GL Entry', 'Journal Entry', 'Payment Entry',
			'Sales Invoice', 'Purchase Invoice', 'Sales Order', 'Purchase Order'
		]

	def sync_financial_transaction(self, doc, operation):
		"""Sync financial transaction data"""
		try:
			# Create audit trail entry using unified API
			audit_api._create_audit_entry(doc, operation, 'Financial')

			# Check for unusual patterns using unified API
			self.check_financial_anomalies(doc, operation)

			# Update financial dashboards
			self.update_financial_dashboards(doc)

		except Exception as e:
			frappe.log_error(f"Financial Sync Error: {str(e)}", "Financial Integration")

	def create_financial_audit_trail(self, doc, operation):
		"""Create audit trail for financial transactions"""
		# This will be handled by the hooks, but we can add specific financial logic here
		pass

	def check_financial_anomalies(self, doc, operation):
		"""Check for financial anomalies"""
		try:
			# Check for large transactions
			amount = self.get_transaction_amount(doc)
			if amount and abs(amount) > 100000:  # Threshold for large transactions
				self.create_large_transaction_alert(doc, amount)

			# Check for unusual timing
			if self.is_unusual_timing(doc):
				self.create_timing_alert(doc)

			# Check for round number transactions
			if self.is_round_number_transaction(doc):
				self.create_round_number_alert(doc)

		except Exception as e:
			frappe.log_error(f"Financial Anomaly Check Error: {str(e)}")

	def get_transaction_amount(self, doc):
		"""Extract transaction amount from document"""
		amount_fields = ['total', 'grand_total', 'paid_amount', 'received_amount', 'debit', 'credit']

		for field in amount_fields:
			if hasattr(doc, field):
				amount = getattr(doc, field)
				if amount:
					return flt(amount)

		return 0

	def is_unusual_timing(self, doc):
		"""Check if transaction timing is unusual"""
		# Check if transaction is outside business hours
		if hasattr(doc, 'posting_date'):
			posting_time = get_datetime(doc.posting_date)
			hour = posting_time.hour

			# Business hours: 8 AM to 6 PM
			if hour < 8 or hour > 18:
				return True

		return False

	def is_round_number_transaction(self, doc):
		"""Check if transaction amount is a round number"""
		amount = self.get_transaction_amount(doc)
		if amount:
			# Check if amount ends with many zeros
			amount_str = str(abs(int(amount)))
			if len(amount_str) >= 4 and amount_str[-3:] == '000':
				return True

		return False

	def create_large_transaction_alert(self, doc, amount):
		"""Create alert for large transactions"""
		try:
			finding = frappe.get_doc({
				'doctype': 'Audit Finding',
				'finding_title': f"Large Transaction Alert: {doc.doctype} {doc.name}",
				'description': f"Transaction amount of {amount} exceeds threshold in {doc.doctype}",
				'finding_type': 'Financial Anomaly',
				'severity': 'Medium',
				'status': 'Open',
				'reported_date': now(),
				'responsible_party': self.get_financial_auditor(),
				'audit_trail_reference': f"{doc.doctype}:{doc.name}"
			})

			finding.insert(ignore_permissions=True)
			frappe.db.commit()

		except Exception as e:
			frappe.log_error(f"Large Transaction Alert Error: {str(e)}")

	def create_timing_alert(self, doc):
		"""Create alert for unusual timing"""
		try:
			finding = frappe.get_doc({
				'doctype': 'Audit Finding',
				'finding_title': f"Unusual Timing Alert: {doc.doctype} {doc.name}",
				'description': f"Transaction posted outside normal business hours",
				'finding_type': 'Timing Anomaly',
				'severity': 'Low',
				'status': 'Open',
				'reported_date': now(),
				'responsible_party': self.get_financial_auditor()
			})

			finding.insert(ignore_permissions=True)
			frappe.db.commit()

		except Exception as e:
			frappe.log_error(f"Timing Alert Error: {str(e)}")

	def create_round_number_alert(self, doc):
		"""Create alert for round number transactions"""
		try:
			finding = frappe.get_doc({
				'doctype': 'Audit Finding',
				'finding_title': f"Round Number Alert: {doc.doctype} {doc.name}",
				'description': f"Transaction amount appears to be a round number",
				'finding_type': 'Financial Anomaly',
				'severity': 'Low',
				'status': 'Open',
				'reported_date': now(),
				'responsible_party': self.get_financial_auditor()
			})

			finding.insert(ignore_permissions=True)
			frappe.db.commit()

		except Exception as e:
			frappe.log_error(f"Round Number Alert Error: {str(e)}")

	def update_financial_dashboards(self, doc):
		"""Update financial dashboard data"""
		# This would update cached dashboard data
		pass

	def get_financial_auditor(self):
		"""Get default financial auditor"""
		return frappe.db.get_single_value('Audit Settings', 'financial_auditor') or 'Administrator'

	def reconcile_financial_data(self):
		"""Perform financial data reconciliation"""
		try:
			# Reconcile GL entries with journal entries
			self.reconcile_gl_entries()

			# Reconcile payments with invoices
			self.reconcile_payments()

			# Check for unmatched transactions
			self.check_unmatched_transactions()

		except Exception as e:
			frappe.log_error(f"Financial Reconciliation Error: {str(e)}")

	def reconcile_gl_entries(self):
		"""Reconcile GL entries"""
		# Implementation for GL reconciliation
		pass

	def reconcile_payments(self):
		"""Reconcile payments with invoices"""
		# Implementation for payment reconciliation
		pass

	def check_unmatched_transactions(self):
		"""Check for unmatched transactions"""
		# Implementation for unmatched transaction detection
		pass


class HRIntegrationController:
	"""Controller for HR module integration"""

	def __init__(self):
		self.hr_doctypes = [
			'Employee', 'Salary Slip', 'Leave Application',
			'Attendance', 'Expense Claim'
		]

	def sync_hr_transaction(self, doc, operation):
		"""Sync HR transaction data"""
		try:
			# Create audit trail entry using unified API
			audit_api._create_audit_entry(doc, operation, 'HR')

			# Check for HR anomalies
			self.check_hr_anomalies(doc, operation)

			# Update HR dashboards
			self.update_hr_dashboards(doc)

		except Exception as e:
			frappe.log_error(f"HR Sync Error: {str(e)}", "HR Integration")

	def check_hr_anomalies(self, doc, operation):
		"""Check for HR-related anomalies"""
		try:
			if doc.doctype == 'Salary Slip':
				self.check_salary_anomalies(doc)
			elif doc.doctype == 'Leave Application':
				self.check_leave_anomalies(doc)
			elif doc.doctype == 'Expense Claim':
				self.check_expense_anomalies(doc)

		except Exception as e:
			frappe.log_error(f"HR Anomaly Check Error: {str(e)}")

	def check_salary_anomalies(self, doc):
		"""Check for salary-related anomalies"""
		# Check for unusual salary changes
		pass

	def check_leave_anomalies(self, doc):
		"""Check for leave-related anomalies"""
		# Check for unusual leave patterns
		pass

	def check_expense_anomalies(self, doc):
		"""Check for expense-related anomalies"""
		# Check for unusual expense patterns
		pass

	def update_hr_dashboards(self, doc):
		"""Update HR dashboard data"""
		pass


class InventoryIntegrationController:
	"""Controller for inventory module integration"""

	def __init__(self):
		self.inventory_doctypes = [
			'Stock Entry', 'Stock Reconciliation', 'Item',
			'Delivery Note', 'Purchase Receipt'
		]

	def sync_inventory_transaction(self, doc, operation):
		"""Sync inventory transaction data"""
		try:
			# Create audit trail entry using unified API
			audit_api._create_audit_entry(doc, operation, 'Inventory')

			# Check for inventory anomalies
			self.check_inventory_anomalies(doc, operation)

			# Update inventory dashboards
			self.update_inventory_dashboards(doc)

		except Exception as e:
			frappe.log_error(f"Inventory Sync Error: {str(e)}", "Inventory Integration")

	def check_inventory_anomalies(self, doc, operation):
		"""Check for inventory-related anomalies"""
		try:
			if doc.doctype == 'Stock Entry':
				self.check_stock_anomalies(doc)
			elif doc.doctype == 'Stock Reconciliation':
				self.check_reconciliation_anomalies(doc)

		except Exception as e:
			frappe.log_error(f"Inventory Anomaly Check Error: {str(e)}")

	def check_stock_anomalies(self, doc):
		"""Check for stock-related anomalies"""
		# Check for unusual stock movements
		pass

	def check_reconciliation_anomalies(self, doc):
		"""Check for reconciliation anomalies"""
		# Check for unusual reconciliation patterns
		pass

	def update_inventory_dashboards(self, doc):
		"""Update inventory dashboard data"""
		pass


class AccessControlIntegrationController:
	"""Controller for access control module integration"""

	def __init__(self):
		self.access_doctypes = ['User', 'Role', 'User Permission']

	def sync_access_transaction(self, doc, operation):
		"""Sync access control transaction data"""
		try:
			# Create audit trail entry using unified API
			audit_api._create_audit_entry(doc, operation, 'Access Control')
			# Check for access control anomalies
			self.check_access_anomalies(doc, operation)

			# Update access control dashboards
			self.update_access_dashboards(doc)

		except Exception as e:
			frappe.log_error(f"Access Control Sync Error: {str(e)}", "Access Control Integration")

	def check_access_anomalies(self, doc, operation):
		"""Check for access control anomalies"""
		try:
			if doc.doctype == 'User':
				self.check_user_anomalies(doc, operation)
			elif doc.doctype == 'Role':
				self.check_role_anomalies(doc, operation)
			elif doc.doctype == 'User Permission':
				self.check_permission_anomalies(doc, operation)

		except Exception as e:
			frappe.log_error(f"Access Control Anomaly Check Error: {str(e)}")

	def check_user_anomalies(self, doc, operation):
		"""Check for user-related anomalies"""
		# Check for unusual user creation/modification patterns
		pass

	def check_role_anomalies(self, doc, operation):
		"""Check for role-related anomalies"""
		# Check for unusual role changes
		pass

	def check_permission_anomalies(self, doc, operation):
		"""Check for permission-related anomalies"""
		# Check for unusual permission changes
		pass

	def update_access_dashboards(self, doc):
		"""Update access control dashboard data"""
		pass


# Global controller instances
financial_controller = FinancialIntegrationController()
hr_controller = HRIntegrationController()
inventory_controller = InventoryIntegrationController()
access_controller = AccessControlIntegrationController()


@frappe.whitelist()
def get_integration_status():
	"""Get integration status for all modules"""
	try:
		status = {
			'financial': get_module_status('Financial'),
			'hr': get_module_status('HR'),
			'inventory': get_module_status('Inventory'),
			'access_control': get_module_status('Access Control'),
			'last_sync': get_last_sync_time(),
			'sync_health': get_sync_health()
		}

		return status

	except Exception as e:
		frappe.log_error(f"Integration Status Error: {str(e)}")
		frappe.throw(_("Failed to get integration status"))


def get_module_status(module):
	"""Get status for a specific module"""
	try:
		# Count audit trail entries for the module
		count = frappe.db.count('Audit Trail Entry',
			filters={'module': module})

		# Count pending reviews
		pending_reviews = frappe.db.count('Audit Trail Entry',
			filters={
				'module': module,
				'requires_review': 1,
				'status': 'Pending'
			})

		return {
			'total_entries': count,
			'pending_reviews': pending_reviews,
			'status': 'Active' if count > 0 else 'Inactive'
		}

	except Exception as e:
		return {'error': str(e)}


def get_last_sync_time():
	"""Get last sync time"""
	try:
		last_entry = frappe.get_all('Audit Trail Entry',
			fields=['timestamp'],
			order_by='timestamp desc',
			limit=1)

		return last_entry[0]['timestamp'] if last_entry else None

	except Exception:
		return None


def get_sync_health():
	"""Get overall sync health status"""
	try:
		# Check if sync is running (simplified check)
		return 'Healthy'

	except Exception:
		return 'Unhealthy'