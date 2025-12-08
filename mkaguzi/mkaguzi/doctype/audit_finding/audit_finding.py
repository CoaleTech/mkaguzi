import frappe
from frappe import _
from frappe.model.document import Document
from datetime import datetime, date
import re

class AuditFinding(Document):
	def autoname(self):
		"""Generate unique finding ID with format: F-YYYY-####"""
		if not self.finding_id:
			current_year = datetime.now().year
			# Get the last finding for this year
			last_finding = frappe.db.sql("""
				SELECT finding_id FROM `tabAudit Finding`
				WHERE finding_id LIKE 'F-%%-%s-%%' ORDER BY finding_id DESC LIMIT 1
			""", current_year, as_dict=True)

			if last_finding:
				# Extract the sequence number from the last finding
				last_id = last_finding[0].finding_id
				try:
					sequence = int(last_id.split('-')[-1])
					next_sequence = sequence + 1
				except (ValueError, IndexError):
					next_sequence = 1
			else:
				next_sequence = 1

			self.finding_id = f"F-{current_year}-{next_sequence:04d}"

	def validate(self):
		"""Validate the audit finding"""
		self.validate_risk_score()
		self.validate_dates()
		self.validate_status_transitions()
		self.validate_repeat_finding()
		self.update_calculated_fields()
		self.set_audit_trail()

	def validate_risk_score(self):
		"""Calculate risk score based on likelihood and impact"""
		if self.likelihood and self.impact:
			likelihood_map = {
				"Rare": 1,
				"Unlikely": 2,
				"Possible": 3,
				"Likely": 4,
				"Almost Certain": 5
			}

			impact_map = {
				"Insignificant": 1,
				"Minor": 2,
				"Moderate": 3,
				"Major": 4,
				"Catastrophic": 5
			}

			likelihood_score = likelihood_map.get(self.likelihood, 0)
			impact_score = impact_map.get(self.impact, 0)

			self.risk_score = likelihood_score * impact_score

			# Set risk rating based on score
			if self.risk_score >= 16:
				self.risk_rating = "Critical"
			elif self.risk_score >= 10:
				self.risk_rating = "High"
			elif self.risk_score >= 5:
				self.risk_rating = "Medium"
			else:
				self.risk_rating = "Low"

	def validate_dates(self):
		"""Validate date relationships"""
		if self.target_completion_date and self.response_date:
			if self.target_completion_date < self.response_date:
				frappe.throw(_("Target completion date cannot be before management response date"))

		if self.closure_date and self.verification_date:
			if self.closure_date < self.verification_date:
				frappe.throw(_("Closure date cannot be before verification date"))

	def validate_status_transitions(self):
		"""Validate status transition logic"""
		valid_transitions = {
			"Open": ["Action in Progress", "Accepted as Risk", "Management Override"],
			"Action in Progress": ["Pending Verification", "Open", "Accepted as Risk"],
			"Pending Verification": ["Closed", "Action in Progress"],
			"Closed": [],  # Closed findings cannot be reopened
			"Accepted as Risk": [],
			"Management Override": []
		}

		if self.has_value_changed("finding_status"):
			old_status = self.get_doc_before_save().finding_status if self.get_doc_before_save() else None
			if old_status and self.finding_status not in valid_transitions.get(old_status, []):
				frappe.throw(_(f"Invalid status transition from '{old_status}' to '{self.finding_status}'"))

	def validate_repeat_finding(self):
		"""Validate repeat finding logic"""
		if self.repeat_finding:
			if not self.previous_finding_reference:
				frappe.throw(_("Previous finding reference is required for repeat findings"))
			if not self.previous_finding_date:
				frappe.throw(_("Previous finding date is required for repeat findings"))

			# Auto-calculate repeat count
			if self.previous_finding_reference:
				previous_repeat_count = frappe.db.get_value("Audit Finding",
					self.previous_finding_reference, "repeat_count") or 0
				self.repeat_count = previous_repeat_count + 1

	def update_calculated_fields(self):
		"""Update calculated fields"""
		# Calculate exception rate
		if self.sample_size and self.sample_size > 0:
			self.exception_rate = (self.exceptions_found / self.sample_size) * 100

		# Calculate overdue days
		if self.target_completion_date and self.follow_up_required:
			today = date.today()
			if self.target_completion_date < today and self.finding_status != "Closed":
				self.overdue_days = (today - self.target_completion_date).days
				if self.overdue_days > 30:
					self.escalation_required = 1
			else:
				self.overdue_days = 0
				self.escalation_required = 0

		# Set next follow-up date based on frequency
		if self.follow_up_required and self.follow_up_frequency and not self.next_follow_up_date:
			if self.follow_up_frequency == "Monthly":
				# Next month same day
				next_date = date.today().replace(day=min(date.today().day, 28))
				if next_date.month == 12:
					next_date = next_date.replace(year=next_date.year + 1, month=1)
				else:
					next_date = next_date.replace(month=next_date.month + 1)
				self.next_follow_up_date = next_date
			elif self.follow_up_frequency == "Quarterly":
				# Next quarter
				current_month = date.today().month
				if current_month <= 3:
					next_date = date.today().replace(month=4, day=1)
				elif current_month <= 6:
					next_date = date.today().replace(month=7, day=1)
				elif current_month <= 9:
					next_date = date.today().replace(month=10, day=1)
				else:
					next_date = date.today().replace(year=date.today().year + 1, month=1, day=1)
				self.next_follow_up_date = next_date
			elif self.follow_up_frequency == "Semi-Annual":
				current_month = date.today().month
				if current_month <= 6:
					next_date = date.today().replace(month=7, day=1)
				else:
					next_date = date.today().replace(year=date.today().year + 1, month=1, day=1)
				self.next_follow_up_date = next_date
			elif self.follow_up_frequency == "Annual":
				next_date = date.today().replace(year=date.today().year + 1, month=1, day=1)
				self.next_follow_up_date = next_date

	def set_audit_trail(self):
		"""Set audit trail fields"""
		if not self.created_by:
			self.created_by = frappe.session.user
		if not self.created_on:
			self.created_on = datetime.now()
		self.last_modified = datetime.now()

	def before_save(self):
		"""Actions before saving"""
		self.track_status_change()

	def track_status_change(self):
		"""Track status changes in history"""
		if self.has_value_changed("finding_status"):
			old_status = self.get_doc_before_save().finding_status if self.get_doc_before_save() else None
			if old_status != self.finding_status:
				# Add to status history
				self.append("status_history", {
					"previous_status": old_status,
					"new_status": self.finding_status,
					"changed_on": datetime.now(),
					"changed_by": frappe.session.user,
					"reason": "Status updated"
				})

	def on_update(self):
		"""Actions after updating"""
		self.update_engagement_finding_count()
		self.create_notification()

	def update_engagement_finding_count(self):
		"""Update finding count in related audit engagement"""
		if self.engagement_reference:
			finding_count = frappe.db.count("Audit Finding",
				filters={"engagement_reference": self.engagement_reference})
			frappe.db.set_value("Audit Engagement", self.engagement_reference,
				"finding_count", finding_count)

	def create_notification(self):
		"""Create notifications for status changes"""
		if self.has_value_changed("finding_status"):
			# Create notification for responsible person
			if self.responsible_person:
				frappe.get_doc({
					"doctype": "Notification Log",
					"subject": f"Audit Finding Status Updated: {self.finding_title}",
					"email_content": f"""
						<p>The status of audit finding <strong>{self.finding_title}</strong> has been updated to <strong>{self.finding_status}</strong>.</p>
						<p><strong>Finding ID:</strong> {self.finding_id}</p>
						<p><strong>Risk Rating:</strong> {self.risk_rating}</p>
						<p>Please review and take appropriate action.</p>
					""",
					"document_type": "Audit Finding",
					"document_name": self.name,
					"for_user": self.responsible_person,
					"type": "Alert"
				}).insert(ignore_permissions=True)

	def on_trash(self):
		"""Actions when deleting"""
		self.update_engagement_finding_count()