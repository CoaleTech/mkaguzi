# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, getdate

class DashboardUserPermission(Document):
	def validate(self):
		"""Validate user permission configuration"""
		self.validate_user_or_role()
		self.validate_permissions()
		self.validate_expiry()

	def validate_user_or_role(self):
		"""Ensure either user or role is specified"""
		if not self.user and not self.user_role:
			frappe.throw(_("Either User or User Role must be specified"))

		if self.user and self.user_role:
			frappe.throw(_("Cannot specify both User and User Role. Choose one."))

	def validate_permissions(self):
		"""Validate permission settings"""
		if not self.can_view and not self.can_edit and not self.can_delete and not self.can_share:
			frappe.throw(_("At least one permission must be granted"))

	def validate_expiry(self):
		"""Validate permission expiry"""
		if self.expiry_date and getdate(self.expiry_date) < getdate(nowdate()):
			frappe.throw(_("Expiry date cannot be in the past"))

	def before_save(self):
		"""Handle before save operations"""
		if not self.permission_id:
			# Generate unique permission ID
			import uuid
			self.permission_id = str(uuid.uuid4())[:8].upper()

		# Set permission type based on user/role
		if self.user:
			self.permission_type = "User"
		elif self.user_role:
			self.permission_type = "Role"

@frappe.whitelist()
def get_user_permissions(dashboard_id, user=None):
	"""Get permissions for a user on a dashboard"""
	if not user:
		user = frappe.session.user

	try:
		dashboard = frappe.get_doc("Data Analytics Dashboard", dashboard_id)

		# Check if user is the creator
		if dashboard.created_by == user:
			return {
				"can_view": True,
				"can_edit": True,
				"can_delete": True,
				"can_share": True,
				"is_owner": True
			}

		# Check user permissions
		permissions = frappe.get_all("Dashboard User Permission",
			filters={"parent": dashboard_id},
			fields=["user", "user_role", "can_view", "can_edit", "can_delete", "can_share", "expiry_date"]
		)

		user_permissions = {
			"can_view": False,
			"can_edit": False,
			"can_delete": False,
			"can_share": False,
			"is_owner": False
		}

		user_roles = frappe.get_roles(user)

		for perm in permissions:
			# Check expiry
			if perm.expiry_date and getdate(perm.expiry_date) < getdate(nowdate()):
				continue

			# Check user match
			if perm.user == user:
				user_permissions["can_view"] = user_permissions["can_view"] or perm.can_view
				user_permissions["can_edit"] = user_permissions["can_edit"] or perm.can_edit
				user_permissions["can_delete"] = user_permissions["can_delete"] or perm.can_delete
				user_permissions["can_share"] = user_permissions["can_share"] or perm.can_share

			# Check role match
			elif perm.user_role and perm.user_role in user_roles:
				user_permissions["can_view"] = user_permissions["can_view"] or perm.can_view
				user_permissions["can_edit"] = user_permissions["can_edit"] or perm.can_edit
				user_permissions["can_delete"] = user_permissions["can_delete"] or perm.can_delete
				user_permissions["can_share"] = user_permissions["can_share"] or perm.can_share

		return user_permissions

	except Exception as e:
		frappe.throw(_("Failed to get user permissions: {0}").format(str(e)))

@frappe.whitelist()
def grant_dashboard_access(dashboard_id, user_or_role, permission_type, permissions):
	"""Grant dashboard access to user or role"""
	try:
		dashboard = frappe.get_doc("Data Analytics Dashboard", dashboard_id)

		# Check if current user can share
		current_permissions = get_user_permissions(dashboard_id)
		if not current_permissions.get("can_share"):
			frappe.throw(_("You don't have permission to share this dashboard"))

		# Create permission entry
		permission = frappe.new_doc("Dashboard User Permission")
		permission.parent = dashboard_id
		permission.parenttype = "Data Analytics Dashboard"
		permission.parentfield = "user_permissions"

		if permission_type == "User":
			permission.user = user_or_role
		else:
			permission.user_role = user_or_role

		permission.can_view = permissions.get("can_view", False)
		permission.can_edit = permissions.get("can_edit", False)
		permission.can_delete = permissions.get("can_delete", False)
		permission.can_share = permissions.get("can_share", False)

		permission.insert()
		return {"status": "success", "message": "Access granted successfully"}

	except Exception as e:
		frappe.throw(_("Failed to grant access: {0}").format(str(e)))

@frappe.whitelist()
def revoke_dashboard_access(dashboard_id, permission_id):
	"""Revoke dashboard access"""
	try:
		dashboard = frappe.get_doc("Data Analytics Dashboard", dashboard_id)

		# Check if current user can share
		current_permissions = get_user_permissions(dashboard_id)
		if not current_permissions.get("can_share"):
			frappe.throw(_("You don't have permission to manage access"))

		# Delete permission
		frappe.delete_doc("Dashboard User Permission", permission_id)
		return {"status": "success", "message": "Access revoked successfully"}

	except Exception as e:
		frappe.throw(_("Failed to revoke access: {0}").format(str(e)))

@frappe.whitelist()
def get_dashboard_users(dashboard_id):
	"""Get all users with access to a dashboard"""
	try:
		dashboard = frappe.get_doc("Data Analytics Dashboard", dashboard_id)

		users = []

		# Add creator
		users.append({
			"user": dashboard.created_by,
			"role": "Owner",
			"permissions": ["View", "Edit", "Delete", "Share"],
			"type": "owner"
		})

		# Add permission entries
		permissions = frappe.get_all("Dashboard User Permission",
			filters={"parent": dashboard_id},
			fields=["user", "user_role", "can_view", "can_edit", "can_delete", "can_share"]
		)

		for perm in permissions:
			if perm.user:
				user_perms = []
				if perm.can_view: user_perms.append("View")
				if perm.can_edit: user_perms.append("Edit")
				if perm.can_delete: user_perms.append("Delete")
				if perm.can_share: user_perms.append("Share")

				users.append({
					"user": perm.user,
					"role": "User",
					"permissions": user_perms,
					"type": "user"
				})
			elif perm.user_role:
				user_perms = []
				if perm.can_view: user_perms.append("View")
				if perm.can_edit: user_perms.append("Edit")
				if perm.can_delete: user_perms.append("Delete")
				if perm.can_share: user_perms.append("Share")

				users.append({
					"user": perm.user_role,
					"role": "Role",
					"permissions": user_perms,
					"type": "role"
				})

		return users

	except Exception as e:
		frappe.throw(_("Failed to get dashboard users: {0}").format(str(e)))