# License: MIT

import json
import requests
from datetime import datetime
from typing import List, Dict, Optional
import frappe
from frappe import _
from frappe.core.doctype.sms_settings.sms_settings import send_sms


class AIFindingReviewer:
	"""OpenRouter AI service for reviewing and enriching audit findings"""
	
	def __init__(self):
		self.settings = self._get_settings()
		
	def _get_settings(self):
		"""Get AI settings from Mkaguzi Settings singleton"""
		settings = frappe.get_single("Mkaguzi Settings")
		if not settings.ai_enabled:
			raise frappe.ValidationError("OpenRouter AI Review is disabled")
		if not settings.api_key:
			raise frappe.ValidationError("OpenRouter API key not configured")
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
			
			# Build the review prompt
			prompt = self._build_prompt(finding)
			
			# Call OpenRouter API
			response = self._call_openrouter_api(prompt)
			
			# Parse and update the finding
			self._update_finding_with_ai_review(finding, response)
			
			# Check for severity mismatch and notify if needed
			if finding.severity_mismatch and self.settings.severity_mismatch_notify:
				self._send_severity_mismatch_notification(finding)
			
			return True
			
		except Exception as e:
			frappe.log_error(f"AI Review failed for finding {finding_name}: {str(e)}", "AI Finding Review Error")
			
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
		
		# Format the template with finding data
		return template.format(
			finding_title=finding.finding_title or "",
			finding_type=finding.finding_category or "",
			severity=finding.risk_rating or "",
			condition=finding.condition or "",
			criteria=finding.criteria or "",
			cause=finding.cause or "",
			consequence=finding.consequence or "",
			recommendation=finding.recommendation or "",
			financial_impact=finding.financial_impact or 0
		)
	
	def _get_default_prompt(self) -> str:
		"""Get the default AI review prompt template"""
		return """You are an expert internal auditor. Analyze this audit finding and return ONLY valid JSON with these keys: `severity_assessment` (object: `rating` one of Critical/High/Medium/Low, `justification` string), `root_cause_analysis` (string — deeper analysis beyond what's stated), `recommendation_refinement` (string — improved recommendations), `risk_narrative` (string — 2-3 sentence executive summary). Finding: Title: {finding_title}, Type: {finding_type}, Severity: {severity}, Condition: {condition}, Criteria: {criteria}, Cause: {cause}, Consequence: {consequence}, Recommendation: {recommendation}, Financial Impact: {financial_impact}."""
	
	def _call_openrouter_api(self, prompt: str) -> dict:
		"""Call the OpenRouter API with the review prompt"""
		
		# Prepare the request
		headers = {
			"Authorization": f"Bearer {self.settings.api_key}",
			"HTTP-Referer": frappe.utils.get_url(),
			"X-Title": "Mkaguzi Audit System",
			"Content-Type": "application/json"
		}
		
		# Build model configuration with fallback if enabled
		if self.settings.use_paid_model and self.settings.paid_model:
			# Use fallback routing: free model first, then paid model
			payload = {
				"models": [self.settings.free_model, self.settings.paid_model],
				"route": "fallback",
				"messages": [{"role": "user", "content": prompt}],
				"response_format": {"type": "json_object"},
				"max_tokens": self.settings.max_tokens or 1024,
				"temperature": self.settings.temperature or 0.3
			}
		else:
			# Use only free model
			payload = {
				"model": self.settings.free_model,
				"messages": [{"role": "user", "content": prompt}],
				"response_format": {"type": "json_object"},
				"max_tokens": self.settings.max_tokens or 1024,
				"temperature": self.settings.temperature or 0.3
			}
		
		# Make the API call
		response = requests.post(
			"https://openrouter.ai/api/v1/chat/completions",
			headers=headers,
			json=payload,
			timeout=60
		)
		
		if response.status_code != 200:
			raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
		
		return response.json()
	
	def _update_finding_with_ai_review(self, finding, api_response: dict):
		"""Parse API response and update the finding document"""
		
		try:
			# Extract the AI response content
			content = api_response["choices"][0]["message"]["content"]
			ai_analysis = json.loads(content)
			
			# Map AI analysis to finding fields
			finding.ai_review_status = "Reviewed"
			finding.ai_review_notes = content  # Store raw JSON response
			finding.ai_reviewed_on = datetime.now()
			finding.ai_model_used = api_response.get("model", self.settings.free_model)
			
			# Extract structured analysis
			severity_assessment = ai_analysis.get("severity_assessment", {})
			if isinstance(severity_assessment, dict):
				finding.ai_severity_suggestion = severity_assessment.get("rating")
			else:
				finding.ai_severity_suggestion = severity_assessment
			
			finding.ai_root_cause_analysis = ai_analysis.get("root_cause_analysis", "")
			finding.ai_recommendation_refinement = ai_analysis.get("recommendation_refinement", "")
			finding.ai_risk_narrative = ai_analysis.get("risk_narrative", "")
			
			# Check for severity mismatch
			if (finding.ai_severity_suggestion and 
				finding.risk_rating and 
				finding.ai_severity_suggestion.lower() != finding.risk_rating.lower()):
				finding.severity_mismatch = 1
			else:
				finding.severity_mismatch = 0
			
			# Save the finding
			finding.save(ignore_permissions=True)
			
		except (json.JSONDecodeError, KeyError) as e:
			# Handle malformed AI response
			finding.ai_review_status = "Failed"
			finding.ai_review_notes = f"Failed to parse AI response: {str(e)}\\n\\nRaw response: {content}"
			finding.ai_reviewed_on = datetime.now()
			finding.ai_model_used = api_response.get("model", self.settings.free_model)
			finding.save(ignore_permissions=True)
			raise Exception(f"Failed to parse AI response: {str(e)}")
	
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
		execution_log.execution_details += f"\\n\\nAI Review: {successful_reviews}/{len(finding_names)} findings reviewed successfully"
		execution_log.save(ignore_permissions=True)
		
	except Exception as e:
		frappe.log_error(f"Failed to review agent findings for execution {execution_log_name}: {str(e)}", "AI Review Error")