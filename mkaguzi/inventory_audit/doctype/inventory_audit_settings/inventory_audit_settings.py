# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


# ============================================================
# Standalone whitelisted functions for API access
# ============================================================

@frappe.whitelist()
def get_settings():
	"""Get inventory audit settings for frontend"""
	try:
		settings = frappe.get_single("Inventory Audit Settings")
		return {
			"enable_auto_warehouse_creation": settings.enable_auto_warehouse_creation,
			"default_warehouse_type": settings.default_warehouse_type,
			"auto_generate_warehouse_code": settings.auto_generate_warehouse_code,
			"warehouse_code_prefix": settings.warehouse_code_prefix,
			"default_counting_method": settings.default_counting_method,
			"allow_negative_variance": settings.allow_negative_variance,
			"enable_batch_processing": settings.enable_batch_processing,
			"max_batch_size": settings.max_batch_size,
			"notify_on_variance_threshold": settings.notify_on_variance_threshold,
			"variance_notification_threshold": settings.variance_notification_threshold,
			"notify_store_manager": settings.notify_store_manager,
			"notify_hod_inventory": settings.notify_hod_inventory,
			"require_hod_approval": settings.require_hod_approval,
			"approval_workflow": settings.approval_workflow,
			"auto_approve_below_threshold": settings.auto_approve_below_threshold,
			"approval_threshold_amount": settings.approval_threshold_amount,
			"audit_retention_days": settings.audit_retention_days,
			"enable_audit_trail": settings.enable_audit_trail,
			"auto_archive_completed_audits": settings.auto_archive_completed_audits,
			"archive_after_days": settings.archive_after_days,
		}
	except Exception as e:
		frappe.log_error(f"Error getting inventory audit settings: {str(e)}")
		return {}


@frappe.whitelist()
def create_warehouse(warehouse_code, warehouse_name, warehouse_type=None, branch=None, city=None, county=None):
	"""Create a new warehouse"""
	if not frappe.has_permission("Warehouse Master", "create"):
		frappe.throw(_("You don't have permission to create warehouses"))

	# Validate required fields
	if not warehouse_code:
		frappe.throw(_("Warehouse Code is required"))

	if not warehouse_name:
		frappe.throw(_("Warehouse Name is required"))

	# Check if warehouse code already exists
	if frappe.db.exists("Warehouse Master", warehouse_code):
		frappe.throw(_("Warehouse with code '{0}' already exists").format(warehouse_code))

	# Use default warehouse type if not provided
	if not warehouse_type:
		settings = frappe.get_single("Inventory Audit Settings")
		warehouse_type = settings.default_warehouse_type or "Store"

	# Create warehouse
	warehouse = frappe.get_doc({
		"doctype": "Warehouse Master",
		"warehouse_code": warehouse_code,
		"warehouse_name": warehouse_name,
		"warehouse_type": warehouse_type,
		"is_active": 1,
		"branch": branch,
		"city": city,
		"county": county
	})

	warehouse.insert()
	frappe.msgprint(_("Warehouse '{0}' created successfully").format(warehouse_code))

	return {"warehouse_code": warehouse_code, "name": warehouse.name}


@frappe.whitelist()
def create_sample_warehouse():
	"""Create a sample warehouse for testing purposes"""
	if not frappe.has_permission("Warehouse Master", "create"):
		frappe.throw(_("You don't have permission to create warehouses"))

	# Get settings for default values
	settings = frappe.get_single("Inventory Audit Settings")

	# Generate warehouse code
	warehouse_code = generate_warehouse_code("Sample Warehouse")

	# Create warehouse
	warehouse = frappe.get_doc({
		"doctype": "Warehouse Master",
		"warehouse_code": warehouse_code,
		"warehouse_name": "Sample Warehouse",
		"warehouse_type": settings.default_warehouse_type or "Store",
		"is_active": 1,
		"branch": "Main Branch",
		"city": "Nairobi",
		"county": "Nairobi"
	})

	warehouse.insert()
	frappe.msgprint(_("Sample warehouse '{0}' created successfully").format(warehouse_code))

	return {"warehouse_code": warehouse_code, "name": warehouse.name}


@frappe.whitelist()
def create_team_assignment(warehouse, team_lead, team_members=None):
	"""Create a team assignment for a warehouse"""
	if not frappe.has_permission("Warehouse Master", "write"):
		frappe.throw(_("You don't have permission to manage warehouse assignments"))

	# Parse team_members if it's a string (JSON)
	if isinstance(team_members, str):
		import json
		team_members = json.loads(team_members)

	# Validate required fields
	if not warehouse:
		frappe.throw(_("Warehouse is required"))

	if not team_lead:
		frappe.throw(_("Team Lead is required"))

	if not team_members or len(team_members) == 0:
		frappe.throw(_("At least one team member is required"))

	# Check if warehouse exists
	if not frappe.db.exists("Warehouse Master", warehouse):
		frappe.throw(_("Warehouse '{0}' does not exist").format(warehouse))

	# Check if team lead exists and is active
	if not frappe.db.exists("User", {"name": team_lead, "enabled": 1}):
		frappe.throw(_("Team Lead '{0}' does not exist or is not active").format(team_lead))

	# Validate team members
	for member in team_members:
		if not member.get("user"):
			frappe.throw(_("All team members must have a user assigned"))

		if not frappe.db.exists("User", {"name": member["user"], "enabled": 1}):
			frappe.throw(_("Team member '{0}' does not exist or is not active").format(member["user"]))

		if not member.get("role"):
			member["role"] = "Counter"  # Default role

	# Create team assignment data
	team_assignment_data = {
		"warehouse": warehouse,
		"team_lead": team_lead,
		"team_members": team_members,
		"assigned_date": frappe.utils.nowdate(),
		"assigned_by": frappe.session.user
	}

	# Store in cache
	frappe.cache().set_value(f"warehouse_team_{warehouse}", team_assignment_data)

	# Update warehouse with team assignment info (if fields exist)
	warehouse_doc = frappe.get_doc("Warehouse Master", warehouse)
	if hasattr(warehouse_doc, 'default_stock_analyst'):
		warehouse_doc.default_stock_analyst = team_lead
	warehouse_doc.save()

	frappe.msgprint(_("Team assignment created successfully for warehouse '{0}'").format(warehouse))

	return {
		"warehouse": warehouse,
		"team_lead": team_lead,
		"member_count": len(team_members)
	}


def generate_warehouse_code(warehouse_name):
	"""Generate warehouse code based on settings"""
	settings = frappe.get_single("Inventory Audit Settings")
	if settings.auto_generate_warehouse_code and settings.warehouse_code_prefix:
		# Get the next sequence number
		last_warehouse = frappe.db.sql("""
			SELECT warehouse_code FROM `tabWarehouse Master`
			WHERE warehouse_code LIKE %s
			ORDER BY warehouse_code DESC
			LIMIT 1
		""", (f"{settings.warehouse_code_prefix}%",))

		if last_warehouse:
			# Extract number from last code
			last_code = last_warehouse[0][0]
			try:
				# Find the numeric part after prefix
				prefix_len = len(settings.warehouse_code_prefix)
				number_part = last_code[prefix_len:]
				next_number = int(number_part) + 1
				return f"{settings.warehouse_code_prefix}{next_number:03d}"
			except (ValueError, IndexError):
				pass

		# Default to 001 if no existing warehouses or parsing fails
		return f"{settings.warehouse_code_prefix}001"
	else:
		# Fallback to using warehouse name initials
		return warehouse_name.replace(" ", "").upper()[:10]


# ============================================================
# DocType class
# ============================================================

class InventoryAuditSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		allow_negative_variance: DF.Check
		approval_threshold_amount: DF.Currency
		approval_workflow: DF.Literal["", "Single Level", "Multi Level"]
		archive_after_days: DF.Int
		audit_retention_days: DF.Int
		auto_approve_below_threshold: DF.Check
		auto_archive_completed_audits: DF.Check
		auto_generate_warehouse_code: DF.Check
		default_counting_method: DF.Literal["", "Manual Count", "Barcode Scan", "RFID", "System Integration"]
		default_warehouse_type: DF.Literal["", "Store", "Warehouse", "Distribution Center", "Returns Center"]
		enable_audit_trail: DF.Check
		enable_auto_warehouse_creation: DF.Check
		enable_batch_processing: DF.Check
		max_batch_size: DF.Int
		notify_hod_inventory: DF.Check
		notify_on_variance_threshold: DF.Check
		notify_store_manager: DF.Check
		require_hod_approval: DF.Check
		variance_notification_threshold: DF.Percent
		warehouse_code_prefix: DF.Data
	# end: auto-generated types

	def validate(self):
		"""Validate the settings"""
		self.validate_warehouse_settings()
		self.validate_notification_settings()
		self.validate_approval_settings()

	def validate_warehouse_settings(self):
		"""Validate warehouse-related settings"""
		if self.enable_auto_warehouse_creation:
			if not self.default_warehouse_type:
				frappe.throw(_("Default Warehouse Type is required when auto warehouse creation is enabled"))

		if self.auto_generate_warehouse_code:
			if not self.warehouse_code_prefix:
				frappe.throw(_("Warehouse Code Prefix is required when auto generation is enabled"))

	def validate_notification_settings(self):
		"""Validate notification settings"""
		if self.notify_on_variance_threshold:
			if not self.variance_notification_threshold:
				frappe.throw(_("Variance Notification Threshold is required when notifications are enabled"))

			if self.variance_notification_threshold <= 0:
				frappe.throw(_("Variance Notification Threshold must be greater than 0"))

	def validate_approval_settings(self):
		"""Validate approval workflow settings"""
		if self.require_hod_approval and self.auto_approve_below_threshold:
			if not self.approval_threshold_amount or self.approval_threshold_amount <= 0:
				frappe.throw(_("Approval Threshold Amount must be set and greater than 0 when auto approval is enabled"))

	@staticmethod
	def get_settings_doc():
		"""Get inventory audit settings document"""
		return frappe.get_single("Inventory Audit Settings")

	@staticmethod
	def is_auto_warehouse_creation_enabled():
		"""Check if auto warehouse creation is enabled"""
		settings = frappe.get_single("Inventory Audit Settings")
		return settings.enable_auto_warehouse_creation

	@staticmethod
	def get_default_warehouse_type():
		"""Get default warehouse type"""
		settings = frappe.get_single("Inventory Audit Settings")
		return settings.default_warehouse_type or "Store"

	@staticmethod
	def should_notify_on_variance(variance_percentage):
		"""Check if notification should be sent for variance"""
		settings = frappe.get_single("Inventory Audit Settings")
		if not settings.notify_on_variance_threshold:
			return False

		threshold = settings.variance_notification_threshold or 0
		return abs(variance_percentage) >= threshold

	@staticmethod
	def requires_hod_approval():
		"""Check if HOD approval is required"""
		settings = frappe.get_single("Inventory Audit Settings")
		return settings.require_hod_approval

	@staticmethod
	def can_auto_approve_variance(amount):
		"""Check if variance can be auto-approved"""
		settings = frappe.get_single("Inventory Audit Settings")
		if not settings.require_hod_approval or not settings.auto_approve_below_threshold:
			return False

		threshold = settings.approval_threshold_amount or 0
		return amount <= threshold