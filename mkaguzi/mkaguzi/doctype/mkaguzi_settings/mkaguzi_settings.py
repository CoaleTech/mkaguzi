# License: MIT
# Copyright (c) 2025, Coale Tech and contributors

import frappe
from frappe import _
from frappe.model.document import Document


class MkaguziSettings(Document):
	"""Centralized settings for the Mkaguzi audit system.

	Consolidates AI/OpenRouter config, agent defaults, thresholds,
	cache settings, rate limiting, and scheduling into one singleton.
	"""

	def validate(self):
		self._validate_ai_settings()
		self._validate_thresholds()
		self._validate_cache_settings()
		self._validate_rate_limits()

	def _validate_ai_settings(self):
		"""Validate AI provider fields (OpenRouter or Z.AI)"""
		if self.ai_enabled:
			provider = self.ai_provider or "OpenRouter"

			if provider == "OpenRouter":
				if not self.api_key:
					frappe.throw(_("OpenRouter API Key is required when AI Review is enabled with OpenRouter"))
			elif provider == "Z.AI":
				if not self.z_ai_api_key:
					frappe.throw(_("Z.AI API Key is required when AI Review is enabled with Z.AI"))
				if not self.z_ai_model:
					frappe.throw(_("Z.AI Model is required when using Z.AI provider"))

			if self.temperature is not None:
				if self.temperature < 0 or self.temperature > 2:
					frappe.throw(_("Temperature must be between 0 and 2"))

			if self.max_tokens and self.max_tokens <= 0:
				frappe.throw(_("Max Tokens must be greater than 0"))

			if self.max_findings_per_run and self.max_findings_per_run <= 0:
				frappe.throw(_("Max Findings per Run must be greater than 0"))

	def _validate_thresholds(self):
		"""Validate threshold values are within expected ranges"""
		# Financial thresholds
		for field in ('benford_deviation_threshold', 'duplicate_similarity_threshold'):
			val = getattr(self, field, None)
			if val is not None and val != 0:
				if val < 0 or val > 1:
					frappe.throw(_(f"{self.meta.get_label(field)} must be between 0 and 1"))

		# Risk thresholds - validate ordering
		high = self.risk_high_threshold or 0
		medium = self.risk_medium_threshold or 0
		low = self.risk_low_threshold or 0
		if high and medium and low:
			if not (high > medium > low):
				frappe.throw(_("Risk thresholds must be in order: High > Medium > Low"))

		# Risk threshold sensitivity
		if self.risk_threshold_sensitivity is not None and self.risk_threshold_sensitivity != 0:
			if self.risk_threshold_sensitivity < 0 or self.risk_threshold_sensitivity > 1:
				frappe.throw(_("Risk Threshold Sensitivity must be between 0 and 1"))

	def _validate_cache_settings(self):
		"""Validate cache TTL values"""
		for field in ('cache_default_ttl', 'agent_state_ttl', 'message_bus_ttl'):
			val = getattr(self, field, None)
			if val is not None and val < 0:
				frappe.throw(_(f"{self.meta.get_label(field)} cannot be negative"))

	def _validate_rate_limits(self):
		"""Validate rate limiting configuration"""
		if self.rate_limit_default_limit and self.rate_limit_default_limit <= 0:
			frappe.throw(_("Default Rate Limit must be greater than 0"))

		if self.rate_limit_default_window and self.rate_limit_default_window <= 0:
			frappe.throw(_("Default Rate Window must be greater than 0"))

		if self.rate_limit_burst_capacity and self.rate_limit_burst_capacity <= 0:
			frappe.throw(_("Token Bucket Capacity must be greater than 0"))

		if self.rate_limit_refill_rate and self.rate_limit_refill_rate <= 0:
			frappe.throw(_("Token Refill Rate must be greater than 0"))

	def on_update(self):
		"""Clear all Mkaguzi caches and reload agent registry on save"""
		self._clear_caches()
		self._reload_agent_registry()

	def _clear_caches(self):
		"""Invalidate all mkaguzi caches"""
		try:
			frappe.cache().delete_keys("mkaguzi:*")
			frappe.cache().delete_value("mkaguzi_settings")
		except Exception:
			pass

	def _reload_agent_registry(self):
		"""Reload agent registry with updated defaults"""
		try:
			from mkaguzi.agents.agent_registry import AgentRegistry
			AgentRegistry.load_from_db()
		except Exception:
			pass
