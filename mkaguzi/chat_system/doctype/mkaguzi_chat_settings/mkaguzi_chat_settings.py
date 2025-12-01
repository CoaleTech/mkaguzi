# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MkaguziChatSettings(Document):
	"""
	Settings for Mkaguzi Chat System with RAG and OpenRouter integration.
	
	This is a Single DocType that stores global configuration for:
	- OpenRouter API settings and model selection
	- RAG pipeline configuration
	- Document indexing preferences
	- System prompt customization
	"""
	
	def validate(self):
		"""Validate settings before saving."""
		self.validate_temperature()
		self.validate_top_p()
		self.validate_similarity_threshold()
		self.validate_api_key()
	
	def validate_temperature(self):
		"""Ensure temperature is within valid range."""
		if self.temperature is not None:
			if self.temperature < 0 or self.temperature > 2:
				frappe.throw("Temperature must be between 0 and 2")
	
	def validate_top_p(self):
		"""Ensure top_p is within valid range."""
		if self.top_p is not None:
			if self.top_p < 0 or self.top_p > 1:
				frappe.throw("Top P must be between 0 and 1")
	
	def validate_similarity_threshold(self):
		"""Ensure similarity threshold is within valid range."""
		if self.similarity_threshold is not None:
			if self.similarity_threshold < 0 or self.similarity_threshold > 1:
				frappe.throw("Similarity Threshold must be between 0 and 1")
	
	def validate_api_key(self):
		"""Warn if AI is enabled but no API key is set."""
		if self.enable_ai_chat and not self.openrouter_api_key:
			frappe.msgprint(
				"AI Chat is enabled but no OpenRouter API key is configured. "
				"Please add your API key to enable AI features.",
				indicator="orange",
				title="API Key Required"
			)
	
	@frappe.whitelist()
	def test_connection(self):
		"""Test the OpenRouter API connection."""
		if not self.openrouter_api_key:
			frappe.throw("Please configure the OpenRouter API key first")
		
		try:
			from mkaguzi.ai.openrouter_client import OpenRouterClient
			client = OpenRouterClient()
			result = client.test_connection()
			
			if result.get("success"):
				frappe.msgprint(
					f"Successfully connected to OpenRouter. Available models: {result.get('models_count', 'Unknown')}",
					indicator="green",
					title="Connection Successful"
				)
			else:
				frappe.throw(f"Connection failed: {result.get('error', 'Unknown error')}")
				
		except Exception as e:
			frappe.throw(f"Connection test failed: {str(e)}")
	
	@frappe.whitelist()
	def rebuild_index(self):
		"""Trigger a full rebuild of the RAG index."""
		try:
			self.db_set("index_status", "Indexing")
			frappe.db.commit()
			
			# Queue the indexing job
			frappe.enqueue(
				"mkaguzi.ai.rag.indexer.rebuild_full_index",
				queue="long",
				timeout=3600,
				now=False
			)
			
			frappe.msgprint(
				"Index rebuild has been queued. This may take several minutes depending on the number of documents.",
				indicator="blue",
				title="Indexing Started"
			)
			
		except Exception as e:
			self.db_set("index_status", "Failed")
			frappe.throw(f"Failed to start indexing: {str(e)}")
	
	def get_enabled_doctypes(self):
		"""Get list of doctypes enabled for indexing."""
		doctypes = []
		
		if self.index_audit_findings:
			doctypes.append("Audit Finding")
		if self.index_working_papers:
			doctypes.append("Working Paper")
		if self.index_audit_programs:
			doctypes.append("Audit Program")
		if self.index_test_executions:
			doctypes.append("Test Execution")
		if self.index_risk_assessments:
			doctypes.append("Risk Assessment")
		if self.index_compliance_requirements:
			doctypes.append("Compliance Requirement")
		
		return doctypes


def get_chat_settings():
	"""Get the chat settings singleton."""
	return frappe.get_single("Mkaguzi Chat Settings")
