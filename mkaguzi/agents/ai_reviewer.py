# License: MIT

import json
import requests
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import frappe
from frappe import _
from frappe.core.doctype.sms_settings.sms_settings import send_sms


class AIFindingReviewer:
	"""OpenRouter AI service for reviewing and enriching audit findings"""
	
	def __init__(self):
		self.settings = self._get_settings()
		self.rate_limit_reset = None  # Timestamp when rate limit expires
		
	def _get_settings(self):
		"""Get AI settings from Mkaguzi Settings singleton"""
		settings = frappe.get_single("Mkaguzi Settings")
		if not settings.ai_enabled:
			raise frappe.ValidationError("AI Review is disabled")
		
		provider = settings.ai_provider or "OpenRouter"
		if provider == "OpenRouter" and not settings.api_key:
			raise frappe.ValidationError("OpenRouter API key not configured")
		if provider == "Z.AI" and not settings.z_ai_api_key:
			raise frappe.ValidationError("Z.AI API key not configured")
		
		# Map ai_enabled to enabled for backward compatibility
		settings.enabled = settings.ai_enabled
		return settings
	
	def review_finding(self, finding_name: str) -> bool:
		"""Review a single audit finding using OpenRouter AI
		
		Args:
			finding_name: Name of the Audit Finding doc
			
		Returns:
			bool: True if review succeeded, False if failed
		"""
		try:
			# Fetch the finding document
			finding = frappe.get_doc("Audit Finding", finding_name)
			
			# Generate cache key from finding content
			cache_key = f"mkaguzi:ai_review:{frappe.generate_hash(
				(finding.finding_title or '') + (finding.condition or '') + (finding.criteria or ''), 10
			)}"
			
			# Check cache first
			cached_response = frappe.cache().get_value(cache_key)
			if cached_response:
				self._update_finding_with_ai_review(finding, cached_response)
				if finding.severity_mismatch and self.settings.severity_mismatch_notify:
					self._send_severity_mismatch_notification(finding)
				return True
			
			# Check quota before making API call
			from mkaguzi.utils.settings import check_ai_quota
			if not check_ai_quota():
				raise frappe.ValidationError("Daily AI quota exceeded. Review will be scheduled for next day.")
			
			# Build the review prompt with compression
			prompt = self._build_prompt(finding)
			
			# Call OpenRouter API
			response = self._call_openrouter_api(prompt, finding)
			
			# Cache the response
			from mkaguzi.utils.settings import get_ai_cache_ttl
			cache_ttl = get_ai_cache_ttl()
			frappe.cache().set_value(cache_key, response, expires_in_sec=cache_ttl)
			
			# Parse and update the finding
			self._update_finding_with_ai_review(finding, response)
			
			# Increment quota counter
			from mkaguzi.utils.settings import increment_ai_quota
			increment_ai_quota()
			
			# Check for severity mismatch and notify if needed
			if finding.severity_mismatch and self.settings.severity_mismatch_notify:
				self._send_severity_mismatch_notification(finding)
			
			return True
			
		except Exception as e:
			self._safe_log_error(f"AI Review failed for finding {finding_name}: {str(e)}", "AI Finding Review Error")
			
			# Update finding with failure status
			try:
				finding = frappe.get_doc("Audit Finding", finding_name)
				finding.ai_review_status = "Failed"
				finding.ai_review_notes = f"AI Review failed: {str(e)}"
				finding.save(ignore_permissions=True)
			except:
				pass
				
			return False
	
	def review_batch(self, finding_names: List[str]) -> Dict[str, bool]:
		"""Review multiple findings in batch
		
		Args:
			finding_names: List of Audit Finding doc names
			
		Returns:
			dict: Map of finding_name -> success_status
		"""
		results = {}
		for finding_name in finding_names:
			results[finding_name] = self.review_finding(finding_name)
		return results
	
	def _build_prompt(self, finding) -> str:
		"""Build the AI review prompt from finding data"""
		template = self.settings.review_prompt_template or self._get_default_prompt()
		
		# Compress finding context before building prompt
		compressed = self._compress_finding_context(finding)
		
		# Build comprehensive context dict so custom templates work
		# Use collections.defaultdict via format_map so missing keys return ''
		from collections import defaultdict
		context = defaultdict(str, compressed)
		
		# Add extra aliases that custom templates may reference
		context.update({
			'corrective_action': compressed.get('recommendation', ''),
			'current_severity': compressed.get('severity', ''),
			'risk_score': str(finding.risk_score or 0),
			'finding_description': compressed.get('condition', ''),
			'impact': compressed.get('consequence', ''),
			'title': compressed.get('finding_title', ''),
		})
		
		# format_map won't raise KeyError for unknown placeholders
		return template.format_map(context)
	
	def _get_default_prompt(self) -> str:
		"""Get the default AI review prompt template"""
		return """You are an expert internal auditor. Analyze this audit finding and return ONLY valid JSON with these keys: `severity_assessment` (object: `rating` one of Critical/High/Medium/Low, `justification` string), `root_cause_analysis` (string — deeper analysis beyond what's stated), `recommendation_refinement` (string — improved recommendations), `risk_narrative` (string — 2-3 sentence executive summary). Finding: Title: {finding_title}, Type: {finding_type}, Severity: {severity}, Condition: {condition}, Criteria: {criteria}, Cause: {cause}, Consequence: {consequence}, Recommendation: {recommendation}, Financial Impact: {financial_impact}."""
	
	def _compress_finding_context(self, finding) -> dict:
		"""Compress finding data for AI review prompt - truncate and strip HTML
		
		Returns: dict with truncated finding fields, max 10KB total
		"""
		max_field_length = 2000
		max_total_length = 10240
		
		def truncate_html(text, max_len):
			if not text:
				return ""
			# Strip HTML tags
			text = frappe.utils.strip_html_tags(text) if hasattr(frappe.utils, 'strip_html_tags') else re.sub(r'<[^>]+>', '', text)
			# Truncate
			return text[:max_len]
		
		compressed = {
			'finding_title': truncate_html(finding.finding_title or '', max_field_length),
			'finding_type': truncate_html(finding.finding_category or '', max_field_length),
			'severity': truncate_html(finding.risk_rating or '', max_field_length),
			'condition': truncate_html(finding.condition or '', max_field_length),
			'criteria': truncate_html(finding.criteria or '', max_field_length),
			'cause': truncate_html(finding.cause or '', max_field_length),
			'consequence': truncate_html(finding.consequence or '', max_field_length),
			'recommendation': truncate_html(finding.recommendation or '', max_field_length),
			'financial_impact': finding.financial_impact or 0
		}
		
		# Check total size
		total_size = sum(len(str(v)) for v in compressed.values())
		if total_size > max_total_length:
			# Aggressive truncation if needed
			for key in compressed:
				if key != 'financial_impact':
					compressed[key] = compressed[key][:500]
		
		return compressed
	
	def _safe_log_error(self, message: str, error_type: str = "Error"):
		"""Log error with truncation to prevent CharacterLengthExceededError
		
		Args:
			message: Error message to log (will be truncated to 5000 chars)
			error_type: Error category (will be truncated to 100 chars)
		"""
		try:
			title = error_type[:100]
			msg = message[:5000]
			frappe.log_error(msg, title)
		except:
			# Fallback - use print if logging fails
			import sys
			print(f"[{error_type}] {message}", file=sys.stderr)
	
	def _select_model(self, finding) -> tuple:
		"""Select free or paid model based on finding severity and keywords
		
		Returns: (model_id, is_paid)
			- Critical/High severity -> paid model
			- Keywords (fraud, regulatory, misstatement) -> paid model
			- Others -> free model
			- Respects 80/20 free/paid quota split
		"""
		provider = self.settings.ai_provider or "OpenRouter"
		
		# Get current quota usage
		from mkaguzi.utils.settings import get_mkaguzi_settings
		settings = get_mkaguzi_settings()
		quota_used = settings.ai_quota_used or 0
		max_quota = settings.max_findings_per_run or 20
		
		# 80/20 split: 16 free, 4 paid (for 20/day default)
		paid_limit = int(max_quota * 0.2)
		paid_count = quota_used - int(quota_used * 0.8)  # Estimate of paid calls
		
		# Check keyword triggers for paid model
		keywords = ['fraud', 'regulatory', 'misstatement', 'material', 'violation', 'breac']
		full_text = (
			f"{finding.finding_title or ''} {finding.condition or ''} {finding.cause or ''}"
		).lower()
		has_keyword = any(kw in full_text for kw in keywords)
		
		# Determine model
		severity = (finding.risk_rating or 'Low').lower()
		use_paid = (
			severity in ['critical', 'high'] or
			has_keyword
		) and paid_count < paid_limit
		
		if provider == "Z.AI":
			if use_paid:
				return (self.settings.z_ai_paid_model or "glm-4.7", True)
			else:
				return (self.settings.z_ai_model or "glm-4.7-flash", False)
		else:
			if use_paid:
				return (self.settings.paid_model or "anthropic/claude-sonnet-4", True)
			else:
				return (self.settings.free_model or "google/gemma-3-27b-it:free", False)
	
	def _call_openrouter_api(self, prompt: str, finding=None) -> dict:
		"""Call the AI API (OpenRouter or Z.AI) with the review prompt, with rate-limit handling and retries"""
		
		provider = self.settings.ai_provider or "OpenRouter"
		
		# Check rate limit gate
		if self.rate_limit_reset and datetime.now() < self.rate_limit_reset:
			raise frappe.ValidationError(
				f"Rate limited by {provider}. Retry after {self.rate_limit_reset.isoformat()}"
			)
		
		# Prepare provider-specific config
		if provider == "Z.AI":
			api_url = "https://api.z.ai/api/paas/v4/chat/completions"
			api_key = self.settings.get_password('z_ai_api_key')
			headers = {
				"Authorization": f"Bearer {api_key}",
				"Content-Type": "application/json",
				"Accept-Language": "en-US,en"
			}
		else:
			api_url = "https://openrouter.ai/api/v1/chat/completions"
			api_key = self.settings.get_password('api_key')
			headers = {
				"Authorization": f"Bearer {api_key}",
				"HTTP-Referer": frappe.utils.get_url(),
				"X-Title": "Mkaguzi Audit System",
				"Content-Type": "application/json"
			}
		
		# Retry loop with exponential backoff
		retry_delays = [5, 10, 20]  # seconds
		last_error = None
		
		for attempt in range(3):
			try:
				# Select model - use finding severity if available, otherwise free/default model
				if finding:
					model_id, _ = self._select_model(finding)
				else:
					if provider == "Z.AI":
						model_id = self.settings.z_ai_model or "glm-4.7-flash"
					else:
						model_id = self.settings.free_model or "google/gemma-3-27b-it:free"
				
				# Build model configuration
				payload = {
					"model": model_id,
					"messages": [{"role": "user", "content": prompt}],
					"max_tokens": self.settings.max_tokens or 1024,
					"temperature": self.settings.temperature or 0.3
				}
				
				# Make the API call
				response = requests.post(
					api_url,
					headers=headers,
					json=payload,
					timeout=60
				)
				
				# Handle rate limiting (HTTP 429)
				if response.status_code == 429:
					retry_after = int(response.headers.get("Retry-After", retry_delays[attempt]))
					self.rate_limit_reset = datetime.now() + timedelta(seconds=retry_after)
					last_error = f"Rate limited (429). Retry after {retry_after}s"
					
					if attempt < 2:  # Don't sleep on last attempt
						time.sleep(retry_after)
						continue
					else:
						raise Exception(last_error)
				
				# Handle other errors
				if response.status_code != 200:
					raise Exception(f"{provider} API error: {response.status_code} - {response.text}")
				
				return response.json()
				
			except requests.RequestException as e:
				last_error = f"Request error (attempt {attempt + 1}): {str(e)}"
				if attempt < 2:
					time.sleep(retry_delays[attempt])
					continue
				else:
					raise Exception(last_error)
		
		raise Exception(f"Failed after 3 retries: {last_error}")
	
	def _update_finding_with_ai_review(self, finding, api_response: dict):
		"""Parse API response and update the finding document.
		
		Handles both structured JSON responses and free-text responses
		from custom prompt templates.
		"""
		content = ""
		try:
			# Extract the AI response content
			msg = api_response["choices"][0]["message"]
			content = msg.get("content") or ""
			
			# Some models (e.g. nvidia/nemotron) put output in reasoning field
			if not content.strip() and msg.get("reasoning"):
				content = msg["reasoning"]
			
			if not content.strip():
				raise ValueError("Empty AI response content")
			
			# Try to parse as JSON first
			# Sometimes the model wraps JSON in markdown code blocks
			json_text = content
			if "```json" in json_text:
				json_text = json_text.split("```json")[1].split("```")[0].strip()
			elif "```" in json_text:
				json_text = json_text.split("```")[1].split("```")[0].strip()
			
			ai_analysis = json.loads(json_text)
			
			# Normalize keys: "Severity Assessment" → "severity_assessment"
			normalized = {}
			for key, val in ai_analysis.items():
				norm_key = key.lower().replace(" ", "_").replace("-", "_")
				normalized[norm_key] = val
			
			# Structured JSON response path
			finding.ai_review_status = "Reviewed"
			finding.ai_review_notes = content
			finding.ai_reviewed_on = datetime.now()
			finding.ai_model_used = api_response.get("model", self.settings.free_model)
			
			# Extract severity — try multiple key patterns
			severity_assessment = (
				normalized.get("severity_assessment") or 
				normalized.get("severity") or
				normalized.get("current_severity") or
				{}
			)
			if isinstance(severity_assessment, dict):
				finding.ai_severity_suggestion = severity_assessment.get("rating") or severity_assessment.get("level")
			elif isinstance(severity_assessment, str):
				# Extract just the severity level word
				for sev in ["Critical", "High", "Medium", "Low"]:
					if sev.lower() in severity_assessment.lower():
						finding.ai_severity_suggestion = sev
						break
				else:
					finding.ai_severity_suggestion = severity_assessment[:50]
			
			# Extract analysis fields — try multiple key patterns
			finding.ai_root_cause_analysis = (
				normalized.get("root_cause_analysis") or
				normalized.get("risk_analysis") or
				normalized.get("cause_analysis") or
				""
			)
			finding.ai_recommendation_refinement = (
				normalized.get("recommendation_refinement") or
				normalized.get("action_priority") or
				normalized.get("corrective_action") or
				""
			)
			finding.ai_risk_narrative = (
				normalized.get("risk_narrative") or
				normalized.get("additional_context") or
				normalized.get("completeness_check") or
				""
			)
			
		except (json.JSONDecodeError, KeyError, IndexError):
			# Free-text response — still save it as review notes
			finding.ai_review_status = "Reviewed"
			finding.ai_review_notes = content or str(api_response)
			finding.ai_reviewed_on = datetime.now()
			finding.ai_model_used = api_response.get("model", self.settings.free_model)
			
			# Try to extract severity from free text
			for sev in ["Critical", "High", "Medium", "Low"]:
				if sev.lower() in content.lower():
					finding.ai_severity_suggestion = sev
					break
			
			# Store full text in risk narrative
			finding.ai_risk_narrative = content[:2000] if content else ""
		
		# Check for severity mismatch (common to both paths)
		if (finding.ai_severity_suggestion and 
			finding.risk_rating and 
			finding.ai_severity_suggestion.lower() != finding.risk_rating.lower()):
			finding.severity_mismatch = 1
		else:
			finding.severity_mismatch = 0
		
		# Save the finding
		finding.save(ignore_permissions=True)
	
	def _send_severity_mismatch_notification(self, finding):
		"""Send notifications when AI suggests different severity than agent"""
		
		if not self.settings.mismatch_notification_roles:
			return
		
		# Get notification recipients
		roles = [role.strip() for role in self.settings.mismatch_notification_roles.split(",")]
		recipients_email = []
		recipients_mobile = []
		
		for role in roles:
			users = frappe.get_all(
				"Has Role",
				filters={"role": role, "parenttype": "User"},
				fields=["parent"]
			)
			
			for user_doc in users:
				user = frappe.get_doc("User", user_doc.parent)
				if user.email and user.enabled:
					recipients_email.append(user.email)
				if user.mobile_no and user.enabled:
					recipients_mobile.append(user.mobile_no)
		
		# Send email notification
		if recipients_email:
			subject = f"⚠️ AI Severity Mismatch: {finding.finding_id}"
			message = f"""
			<p>An AI review has identified a potential severity mismatch for audit finding <strong>{finding.finding_id}</strong>:</p>
			<ul>
				<li><strong>Finding Title:</strong> {finding.finding_title}</li>
				<li><strong>Agent Severity:</strong> {finding.risk_rating}</li>
				<li><strong>AI Suggested Severity:</strong> {finding.ai_severity_suggestion}</li>
				<li><strong>Source Agent:</strong> {finding.source_agent}</li>
			</ul>
			<p>Please review the finding details and AI analysis to determine the appropriate severity level.</p>
			<p><a href="{frappe.utils.get_url()}/app/audit-finding/{finding.name}">View Finding</a></p>
			"""
			
			try:
				frappe.sendmail(
					recipients=recipients_email,
					subject=subject,
					message=message,
					delayed=False
				)
			except Exception as e:
				frappe.log_error(f"Failed to send severity mismatch email: {str(e)}", "AI Notification Error")
		
		# Send SMS notification
		if recipients_mobile:
			sms_message = f"Mkaguzi Alert: Finding {finding.finding_id} severity mismatch - Agent: {finding.risk_rating}, AI: {finding.ai_severity_suggestion}. Review required."
			
			try:
				send_sms(receiver_list=recipients_mobile, msg=sms_message)
			except Exception as e:
				frappe.log_error(f"Failed to send severity mismatch SMS: {str(e)}", "AI Notification Error")


@frappe.whitelist()
def rerun_ai_review(finding_name):
	"""Manually trigger AI review for a specific finding"""
	if not frappe.has_permission("Audit Finding", "write"):
		frappe.throw("Not enough permissions to trigger AI review")
	
	# Enqueue the AI review
	frappe.enqueue(
		"mkaguzi.agents.ai_reviewer.review_single_finding",
		finding_name=finding_name,
		queue="long",
		timeout=300
	)
	
	frappe.msgprint(f"AI review queued for finding {finding_name}")


def review_single_finding(finding_name):
	"""Background job function for single finding review"""
	reviewer = AIFindingReviewer()
	reviewer.review_finding(finding_name)


def review_agent_findings(execution_log_name):
	"""Background job function for reviewing findings from an agent execution
	
	Args:
		execution_log_name: Name of the Agent Execution Log doc
	"""
	try:
		# Get the execution log
		execution_log = frappe.get_doc("Agent Execution Log", execution_log_name)
		
		# Check if OpenRouter is enabled
		settings = frappe.get_single("Mkaguzi Settings")
		if not settings.ai_enabled:
			return
		
		# Get finding names from the execution log
		if not execution_log.finding_ids:
			return
			
		finding_names = [name.strip() for name in execution_log.finding_ids.split(",") if name.strip()]
		
		if not finding_names:
			return
		
		# Filter findings by minimum severity if configured
		if settings.min_severity_for_review != "All":
			filtered_findings = []
			severity_filter = settings.min_severity_for_review
			
			for finding_name in finding_names:
				try:
					finding = frappe.get_doc("Audit Finding", finding_name)
					if finding.risk_rating == severity_filter or (
						severity_filter == "Medium" and finding.risk_rating in ["Medium", "High", "Critical"]
					) or (
						severity_filter == "High" and finding.risk_rating in ["High", "Critical"]
					) or (
						severity_filter == "Critical" and finding.risk_rating == "Critical"
					):
						filtered_findings.append(finding_name)
				except:
					continue
			
			finding_names = filtered_findings
		
		# Cap at max findings per run
		max_findings = settings.max_findings_per_run or 20
		if len(finding_names) > max_findings:
			finding_names = finding_names[:max_findings]
		
		# Review the findings
		reviewer = AIFindingReviewer()
		results = reviewer.review_batch(finding_names)
		
		# Update execution log with AI review results
		successful_reviews = sum(1 for success in results.values() if success)
		execution_log.execution_details = execution_log.execution_details or ""
		execution_log.execution_details += f"\n\nAI Review: {successful_reviews}/{len(finding_names)} findings reviewed successfully"
		execution_log.save(ignore_permissions=True)
		
	except Exception as e:
		frappe.log_error(f"Failed to review agent findings for execution {execution_log_name}: {str(e)}", "AI Review Error")