# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class MkaguziChatMessage(Document):
	"""
	Chat Message for Mkaguzi Internal Audit System.
	
	Supports:
	- User messages
	- AI-generated responses with context tracking
	- System messages
	- Reply threading
	"""
	
	def before_insert(self):
		"""Set defaults before creating the message."""
		if not self.created_at:
			self.created_at = now_datetime()
		
		if not self.sender and self.message_type == "User":
			self.sender = frappe.session.user
		
		if self.message_type == "AI":
			self.is_ai_generated = 1
		
		# Set reply preview if this is a reply
		if self.is_reply and self.reply_to_message:
			self.set_reply_preview()
	
	def after_insert(self):
		"""Update room statistics after message is created."""
		self.update_room_stats()
	
	def set_reply_preview(self):
		"""Set a preview of the message being replied to."""
		if not self.reply_to_message:
			return
		
		try:
			original = frappe.get_doc("Mkaguzi Chat Message", self.reply_to_message)
			# Get first 100 chars of the original message
			preview = (original.content or "")[:100]
			if len(original.content or "") > 100:
				preview += "..."
			self.reply_preview = preview
		except Exception:
			pass
	
	def update_room_stats(self):
		"""Update the room's message statistics."""
		try:
			room = frappe.get_doc("Mkaguzi Chat Room", self.room)
			room.update_message_stats(is_ai_message=(self.message_type == "AI"))
		except Exception as e:
			frappe.log_error(f"Failed to update room stats: {str(e)}")
	
	def validate(self):
		"""Validate message data."""
		self.validate_room_access()
		self.validate_content()
	
	def validate_room_access(self):
		"""Ensure sender is a participant in the room."""
		if self.message_type == "System":
			return  # System messages don't need participant check
		
		if self.message_type == "AI":
			return  # AI messages don't need participant check
		
		room = frappe.get_doc("Mkaguzi Chat Room", self.room)
		if not room.is_participant(self.sender):
			frappe.throw(_("You are not a participant in this chat room"))
	
	def validate_content(self):
		"""Ensure content is not empty."""
		if not self.content or not self.content.strip():
			frappe.throw(_("Message content cannot be empty"))
	
	def edit_content(self, new_content):
		"""Edit the message content."""
		if self.message_type == "AI":
			frappe.throw(_("AI messages cannot be edited"))
		
		if self.sender != frappe.session.user:
			frappe.throw(_("You can only edit your own messages"))
		
		self.content = new_content
		self.is_edited = 1
		self.edited_at = now_datetime()
		self.save()
	
	def soft_delete(self):
		"""Soft delete the message."""
		if self.sender != frappe.session.user and not frappe.has_permission("Mkaguzi Chat Message", "delete"):
			frappe.throw(_("You can only delete your own messages"))
		
		self.is_deleted = 1
		self.deleted_at = now_datetime()
		self.content = "[Message deleted]"
		self.save()


@frappe.whitelist()
def get_room_messages(room, limit=50, offset=0, before_timestamp=None):
	"""Get messages for a chat room."""
	# Verify user has access to room
	room_doc = frappe.get_doc("Mkaguzi Chat Room", room)
	if not room_doc.is_participant():
		frappe.throw(_("You are not a participant in this chat room"))
	
	filters = {
		"room": room,
		"is_deleted": 0
	}
	
	if before_timestamp:
		filters["created_at"] = ["<", before_timestamp]
	
	messages = frappe.get_all(
		"Mkaguzi Chat Message",
		filters=filters,
		fields=[
			"name", "room", "message_type", "sender", "sender_name",
			"content", "created_at", "is_ai_generated", "ai_model_used",
			"is_edited", "is_reply", "reply_to_message", "reply_preview",
			"context_chunks_used"
		],
		order_by="created_at desc",
		limit_page_length=limit,
		start=offset
	)
	
	# Reverse to get chronological order
	messages.reverse()
	
	return messages


@frappe.whitelist()
def send_message(room, content, request_ai_response=False, reply_to=None):
	"""Send a message to a chat room."""
	# Verify user has access
	room_doc = frappe.get_doc("Mkaguzi Chat Room", room)
	if not room_doc.is_participant():
		frappe.throw(_("You are not a participant in this chat room"))
	
	# Create user message
	message = frappe.get_doc({
		"doctype": "Mkaguzi Chat Message",
		"room": room,
		"message_type": "User",
		"content": content,
		"sender": frappe.session.user,
		"is_reply": 1 if reply_to else 0,
		"reply_to_message": reply_to
	})
	message.insert()
	
	result = {
		"message": message.as_dict(),
		"ai_response": None
	}
	
	# Request AI response if enabled
	if request_ai_response and room_doc.is_ai_enabled:
		try:
			from mkaguzi.chat_system.chat_service import get_ai_response
			ai_response = get_ai_response(room, content, message.name)
			result["ai_response"] = ai_response
		except Exception as e:
			frappe.log_error(f"AI response error: {str(e)}")
			result["ai_error"] = str(e)
	
	return result
