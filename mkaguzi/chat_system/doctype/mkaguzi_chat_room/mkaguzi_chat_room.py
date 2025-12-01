# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class MkaguziChatRoom(Document):
	"""
	Chat Room for Mkaguzi Internal Audit System.
	
	Features:
	- Linkable to Audit Engagements for context-aware AI responses
	- Configurable AI settings per room
	- Participant management
	- Message statistics tracking
	"""
	
	def before_insert(self):
		"""Set defaults before creating the room."""
		if not self.created_by:
			self.created_by = frappe.session.user
		
		# Auto-add creator as participant (skip for DM rooms which handle this separately)
		if not self.flags.get("skip_auto_participant"):
			self.add_participant(frappe.session.user, "Admin")
	
	def validate(self):
		"""Validate room data."""
		self.validate_engagement_link()
		self.validate_participants()
	
	def validate_engagement_link(self):
		"""Validate engagement link for engagement-type rooms."""
		if self.room_type in ["Engagement", "Finding Discussion"]:
			if not self.linked_engagement:
				frappe.msgprint(
					_("Consider linking an audit engagement to enable context-aware AI responses."),
					indicator="blue"
				)
	
	def validate_participants(self):
		"""Ensure at least one participant exists."""
		if not self.participants:
			self.add_participant(frappe.session.user, "Admin")
	
	def add_participant(self, user, role="Member"):
		"""Add a participant to the room."""
		# Check if user already exists
		existing = [p for p in self.participants if p.user == user]
		if existing:
			return existing[0]
		
		self.append("participants", {
			"user": user,
			"role": role,
			"joined_at": now_datetime(),
			"is_active": 1
		})
		
		return self.participants[-1]
	
	def remove_participant(self, user):
		"""Remove a participant from the room."""
		self.participants = [p for p in self.participants if p.user != user]
	
	def is_participant(self, user=None):
		"""Check if a user is a participant in the room."""
		user = user or frappe.session.user
		return any(p.user == user and p.is_active for p in self.participants)
	
	def get_participant_role(self, user=None):
		"""Get the role of a participant."""
		user = user or frappe.session.user
		for p in self.participants:
			if p.user == user:
				return p.role
		return None
	
	def update_message_stats(self, is_ai_message=False):
		"""Update message statistics for the room."""
		self.message_count = (self.message_count or 0) + 1
		self.last_message_at = now_datetime()
		
		if is_ai_message:
			self.ai_message_count = (self.ai_message_count or 0) + 1
			self.last_ai_response_at = now_datetime()
		
		self.db_update()
	
	def get_ai_model(self):
		"""Get the AI model to use for this room."""
		if self.ai_model_override:
			return self.ai_model_override
		
		settings = frappe.get_single("Mkaguzi Chat Settings")
		return settings.default_model
	
	def get_system_prompt(self):
		"""Get the full system prompt for this room."""
		settings = frappe.get_single("Mkaguzi Chat Settings")
		base_prompt = settings.system_prompt or ""
		
		# Add engagement context if linked
		if self.linked_engagement:
			engagement = frappe.get_doc("Audit Engagement", self.linked_engagement)
			context_prompt = f"\n\nCurrent Audit Context:\n- Engagement: {engagement.engagement_title}\n- Type: {engagement.audit_type}\n- Status: {engagement.status}"
			base_prompt += context_prompt
		
		# Add custom prompt if set
		if self.custom_system_prompt:
			base_prompt += f"\n\nAdditional Instructions:\n{self.custom_system_prompt}"
		
		return base_prompt


@frappe.whitelist()
def get_user_rooms(user=None):
	"""Get all chat rooms for a user."""
	user = user or frappe.session.user
	
	# Get rooms where user is a participant
	rooms = frappe.db.sql("""
		SELECT DISTINCT cr.name, cr.room_name, cr.room_type, cr.is_ai_enabled,
			   cr.linked_engagement, cr.engagement_title, cr.message_count,
			   cr.last_message_at, cr.is_active
		FROM `tabMkaguzi Chat Room` cr
		INNER JOIN `tabMkaguzi Chat Participant` cp ON cp.parent = cr.name
		WHERE cp.user = %s AND cp.is_active = 1 AND cr.is_active = 1
		ORDER BY cr.last_message_at DESC
	""", (user,), as_dict=True)
	
	return rooms


@frappe.whitelist()
def create_engagement_room(engagement_name):
	"""Create a chat room linked to an audit engagement."""
	engagement = frappe.get_doc("Audit Engagement", engagement_name)
	
	# Check if room already exists
	existing = frappe.db.exists("Mkaguzi Chat Room", {
		"linked_engagement": engagement_name,
		"room_type": "Engagement"
	})
	
	if existing:
		return frappe.get_doc("Mkaguzi Chat Room", existing)
	
	# Create new room
	room = frappe.get_doc({
		"doctype": "Mkaguzi Chat Room",
		"room_name": f"Audit: {engagement.engagement_title}",
		"room_type": "Engagement",
		"linked_engagement": engagement_name,
		"description": f"Discussion room for {engagement.engagement_id}: {engagement.engagement_title}",
		"is_ai_enabled": 1
	})
	
	# Add audit team as participants
	if engagement.lead_auditor:
		room.add_participant(engagement.lead_auditor, "Admin")
	
	room.insert()
	
	return room
