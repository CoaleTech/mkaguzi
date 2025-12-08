# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, get_datetime, nowdate
import json
import requests
import os

class TemplateMarketplace(Document):
	def autoname(self):
		"""Generate name as Marketplace-TemplateName-Version"""
		if not self.name:
			# Clean template name for use in autoname
			clean_name = "".join(c for c in self.template_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
			clean_name = clean_name.replace(' ', '-').upper()
			version_clean = self.version.replace('.', '-')
			self.name = f"MP-{clean_name}-{version_clean}"

	def validate(self):
		self.validate_template_content()
		self.validate_uniqueness()
		self.set_audit_fields()

	def validate_template_content(self):
		"""Validate template content based on engine"""
		if self.template_engine == "Jinja2" and self.template_content:
			try:
				from jinja2 import Template
				Template(self.template_content)
			except Exception as e:
				frappe.throw(_("Invalid Jinja2 template syntax: {0}").format(str(e)))

	def validate_uniqueness(self):
		"""Ensure template name and version combination is unique"""
		existing = frappe.db.exists("Template Marketplace", {
			"template_name": self.template_name,
			"version": self.version,
			"name": ["!=", self.name]
		})

		if existing:
			frappe.throw(_("Template '{0}' version '{1}' already exists in marketplace").format(
				self.template_name, self.version))

	def set_audit_fields(self):
		"""Set audit trail fields"""
		if not self.published_by:
			self.published_by = frappe.session.user
		if not self.published_date:
			self.published_date = nowdate()
		if not self.last_updated:
			self.last_updated = now()

	def on_update(self):
		"""Handle marketplace template updates"""
		self.last_updated = now()

@frappe.whitelist()
def publish_to_marketplace(template_name, marketplace_data):
	"""Publish a template from registry to marketplace"""
	template = frappe.get_doc("Template Registry", template_name)

	# Create marketplace entry
	marketplace_template = frappe.new_doc("Template Marketplace")
	marketplace_template.update({
		"template_name": marketplace_data.get("template_name", template.template_name),
		"template_type": template.template_type,
		"category": template.category,
		"version": marketplace_data.get("version", "1.0.0"),
		"author": marketplace_data.get("author", frappe.session.user),
		"description": marketplace_data.get("description", template.description or ""),
		"tags": marketplace_data.get("tags", ""),
		"template_content": template.template_content,
		"template_config": template.template_config,
		"file_path": template.file_path,
		"template_engine": template.template_engine,
		"is_public": marketplace_data.get("is_public", False),
		"is_featured": marketplace_data.get("is_featured", False),
		"compatibility": marketplace_data.get("compatibility", "ERPNext v14+"),
		"required_modules": marketplace_data.get("required_modules", ""),
		"license_type": marketplace_data.get("license_type", "MIT"),
		"price": marketplace_data.get("price", 0),
		"status": "Published" if marketplace_data.get("publish_now", False) else "Draft"
	})

	marketplace_template.save()

	return marketplace_template.name

@frappe.whitelist()
def import_from_marketplace(marketplace_template_name, target_category=None):
	"""Import a template from marketplace to local registry"""
	marketplace_template = frappe.get_doc("Template Marketplace", marketplace_template_name)

	# Check if template already exists locally
	existing = frappe.db.exists("Template Registry", {
		"template_name": marketplace_template.template_name,
		"template_type": marketplace_template.template_type
	})

	if existing:
		# Update existing template
		local_template = frappe.get_doc("Template Registry", existing)
		local_template.template_content = marketplace_template.template_content
		local_template.template_config = marketplace_template.template_config
		local_template.file_path = marketplace_template.file_path
		local_template.template_engine = marketplace_template.template_engine
		if target_category:
			local_template.category = target_category
		local_template.save()
		template_name = local_template.name
	else:
		# Create new local template
		local_template = frappe.new_doc("Template Registry")
		local_template.template_name = marketplace_template.template_name
		local_template.template_type = marketplace_template.template_type
		local_template.category = target_category or marketplace_template.category
		local_template.description = marketplace_template.description
		local_template.template_content = marketplace_template.template_content
		local_template.template_config = marketplace_template.template_config
		local_template.file_path = marketplace_template.file_path
		local_template.template_engine = marketplace_template.template_engine
		local_template.is_active = True
		local_template.save()
		template_name = local_template.name

	# Update download count
	marketplace_template.download_count = (marketplace_template.download_count or 0) + 1
	marketplace_template.save()

	return template_name

@frappe.whitelist()
def get_marketplace_templates(filters=None, search=None, limit=50):
	"""Get templates from marketplace with filtering"""
	query_filters = {"status": "Published", "is_public": 1}

	if filters:
		if filters.get("template_type"):
			query_filters["template_type"] = filters.get("template_type")
		if filters.get("category"):
			query_filters["category"] = filters.get("category")
		if filters.get("author"):
			query_filters["author"] = filters.get("author")

	fields = [
		"name", "template_name", "template_type", "category", "version",
		"author", "description", "tags", "download_count", "rating",
		"license_type", "price", "is_featured", "last_updated"
	]

	templates = frappe.get_all("Template Marketplace",
		filters=query_filters,
		fields=fields,
		order_by="is_featured desc, download_count desc, last_updated desc",
		limit=limit
	)

	# Apply search filter if provided
	if search:
		search_lower = search.lower()
		templates = [t for t in templates if
			search_lower in t.template_name.lower() or
			search_lower in (t.description or "").lower() or
			search_lower in (t.tags or "").lower() or
			search_lower in (t.author or "").lower()
		]

	return templates

@frappe.whitelist()
def rate_template(marketplace_template_name, rating):
	"""Rate a marketplace template"""
	if not 1 <= rating <= 5:
		frappe.throw(_("Rating must be between 1 and 5"))

	template = frappe.get_doc("Template Marketplace", marketplace_template_name)

	# Simple rating system - in production, you'd want a more sophisticated system
	# For now, just update the rating directly
	template.rating = rating
	template.save()

	return {"status": "success", "rating": rating}

@frappe.whitelist()
def sync_from_remote_marketplace(remote_url=None):
	"""Sync templates from a remote marketplace"""
	if not remote_url:
		# Default marketplace URL - in production, this would be configurable
		remote_url = "https://marketplace.mkaguzi.com/api/templates"

	try:
		response = requests.get(remote_url, timeout=30)
		response.raise_for_status()

		remote_templates = response.json()

		synced_count = 0
		for remote_template in remote_templates:
			# Check if template exists locally
			existing = frappe.db.exists("Template Marketplace", {
				"template_name": remote_template["template_name"],
				"version": remote_template["version"]
			})

			if not existing:
				# Create local copy
				local_template = frappe.new_doc("Template Marketplace")
				local_template.update(remote_template)
				local_template.status = "Published"  # Remote templates are published
				local_template.save()
				synced_count += 1

		return {"status": "success", "synced": synced_count}

	except Exception as e:
		frappe.log_error(f"Marketplace sync error: {str(e)}", "Template Marketplace")
		frappe.throw(_("Failed to sync from remote marketplace: {0}").format(str(e)))

@frappe.whitelist()
def export_template_for_marketplace(template_name, marketplace_data):
	"""Export a local template to marketplace format"""
	template = frappe.get_doc("Template Registry", template_name)

	export_data = {
		"template_name": marketplace_data.get("template_name", template.template_name),
		"template_type": template.template_type,
		"category": template.category,
		"version": marketplace_data.get("version", "1.0.0"),
		"author": marketplace_data.get("author", frappe.session.user),
		"description": marketplace_data.get("description", template.description or ""),
		"tags": marketplace_data.get("tags", ""),
		"template_content": template.template_content,
		"template_config": template.template_config,
		"file_path": template.file_path,
		"template_engine": template.template_engine,
		"compatibility": marketplace_data.get("compatibility", "ERPNext v14+"),
		"required_modules": marketplace_data.get("required_modules", ""),
		"license_type": marketplace_data.get("license_type", "MIT"),
		"price": marketplace_data.get("price", 0),
		"status": "Draft"
	}

	return export_data

@frappe.whitelist()
def get_featured_templates(limit=10):
	"""Get featured marketplace templates"""
	templates = frappe.get_all("Template Marketplace",
		filters={
			"status": "Published",
			"is_public": 1,
			"is_featured": 1
		},
		fields=[
			"name", "template_name", "template_type", "category",
			"author", "description", "download_count", "rating"
		],
		order_by="download_count desc, rating desc",
		limit=limit
	)

	return templates