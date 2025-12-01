# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

"""
Chat API Endpoints for Mkaguzi

REST API for chat functionality:
- Room management (create, list, join, leave)
- Messaging (send, get, edit, delete)
- AI responses
- RAG operations
"""

import frappe
from frappe import _
from frappe.utils import now_datetime


# ============================================
# Room Management APIs
# ============================================

@frappe.whitelist()
def get_rooms(include_inactive: bool = False) -> dict:
	"""
	Get all chat rooms for the current user.
	
	Args:
		include_inactive: Whether to include inactive rooms
	
	Returns:
		Dict with rooms list
	"""
	user = frappe.session.user
	
	filters = {"is_active": 1} if not include_inactive else {}
	
	# Get rooms where user is a participant
	# Use COALESCE for NULL handling since MariaDB doesn't support NULLS LAST
	rooms = frappe.db.sql("""
		SELECT DISTINCT 
			cr.name,
			cr.room_name,
			cr.room_type,
			cr.description,
			cr.is_ai_enabled,
			cr.linked_engagement,
			cr.engagement_title,
			cr.audit_type,
			cr.message_count,
			cr.last_message_at,
			cr.is_active,
			cp.role as user_role,
			(SELECT COUNT(*) FROM `tabMkaguzi Chat Participant` WHERE parent = cr.name AND is_active = 1) as participant_count
		FROM `tabMkaguzi Chat Room` cr
		INNER JOIN `tabMkaguzi Chat Participant` cp ON cp.parent = cr.name
		WHERE cp.user = %s 
			AND cp.is_active = 1
			{active_filter}
		ORDER BY COALESCE(cr.last_message_at, '1970-01-01') DESC, cr.creation DESC
	""".format(
		active_filter="AND cr.is_active = 1" if not include_inactive else ""
	), (user,), as_dict=True)
	
	# Add is_dm flag and participants for Private/DM rooms
	for room in rooms:
		# Check if this is a DM (Private room with 2 participants)
		room["is_dm"] = room["room_type"] == "Private" and room.get("participant_count", 0) == 2
		
		# For DM rooms, include participant info for display
		if room["is_dm"]:
			participants = frappe.get_all(
				"Mkaguzi Chat Participant",
				filters={"parent": room["name"], "is_active": 1},
				fields=["user", "role"]
			)
			# Add user full names
			for p in participants:
				p["user_name"] = frappe.db.get_value("User", p["user"], "full_name") or p["user"]
			room["participants"] = participants
			
			# Add display name for DM rooms
			current_user = frappe.session.user
			other_participant = next((p for p in participants if p["user"] != current_user), None)
			if other_participant:
				room["display_name"] = other_participant["user_name"]
	
	return {"rooms": rooms}


@frappe.whitelist()
def create_room(
	room_name: str,
	room_type: str = "General",
	description: str = "",
	linked_engagement: str = None,
	is_ai_enabled: bool = True,
	participants: list = None
) -> dict:
	"""
	Create a new chat room.
	
	Args:
		room_name: Name of the room
		room_type: Type of room (General, Engagement, Finding Discussion, Team, Private)
		description: Room description
		linked_engagement: Optional engagement to link
		is_ai_enabled: Whether AI is enabled
		participants: Optional list of user emails to add
	
	Returns:
		Created room document as dict
	"""
	room = frappe.get_doc({
		"doctype": "Mkaguzi Chat Room",
		"room_name": room_name,
		"room_type": room_type,
		"description": description,
		"linked_engagement": linked_engagement,
		"is_ai_enabled": 1 if is_ai_enabled else 0
	})
	
	# Add additional participants
	if participants:
		for user_email in participants:
			if frappe.db.exists("User", user_email):
				room.add_participant(user_email, "Member")
	
	room.insert()
	
	return room.as_dict()


@frappe.whitelist()
def get_room_details(room_name: str) -> dict:
	"""
	Get details of a chat room.
	
	Args:
		room_name: Name of the room
	
	Returns:
		Room document as dict
	"""
	room = frappe.get_doc("Mkaguzi Chat Room", room_name)
	
	if not room.is_participant():
		frappe.throw(_("You are not a participant in this chat room"))
	
	return room.as_dict()


@frappe.whitelist()
def join_room(room_name: str) -> dict:
	"""
	Join a chat room.
	
	Args:
		room_name: Name of the room to join
	
	Returns:
		Updated room document
	"""
	room = frappe.get_doc("Mkaguzi Chat Room", room_name)
	
	# Check if room is joinable (not private)
	if room.room_type == "Private":
		frappe.throw(_("Cannot join private rooms without invitation"))
	
	room.add_participant(frappe.session.user, "Member")
	room.save()
	
	return room.as_dict()


@frappe.whitelist()
def leave_room(room_name: str) -> dict:
	"""
	Leave a chat room.
	
	Args:
		room_name: Name of the room to leave
	
	Returns:
		Success status
	"""
	room = frappe.get_doc("Mkaguzi Chat Room", room_name)
	
	# Check if user is a participant
	if not room.is_participant():
		frappe.throw(_("You are not a participant in this chat room"))
	
	# Check if user is the only admin
	admins = [p for p in room.participants if p.role == "Admin" and p.is_active]
	if len(admins) == 1 and admins[0].user == frappe.session.user:
		frappe.throw(_("Cannot leave: you are the only admin. Transfer ownership first."))
	
	room.remove_participant(frappe.session.user)
	room.save()
	
	return {"success": True}


@frappe.whitelist()
def add_participant(room_name: str, user_email: str, role: str = "Member") -> dict:
	"""
	Add a participant to a room.
	
	Args:
		room_name: Name of the room
		user_email: Email of user to add
		role: Role for the user (Admin, Member, Observer)
	
	Returns:
		Updated room document
	"""
	room = frappe.get_doc("Mkaguzi Chat Room", room_name)
	
	# Check if current user is admin
	if room.get_participant_role() != "Admin":
		frappe.throw(_("Only admins can add participants"))
	
	if not frappe.db.exists("User", user_email):
		frappe.throw(_("User does not exist"))
	
	room.add_participant(user_email, role)
	room.save()
	
	return room.as_dict()


@frappe.whitelist()
def get_or_create_dm(target_user: str) -> dict:
	"""
	Get existing DM room with a user or create a new one.
	
	DM rooms are Private rooms with exactly 2 participants.
	Room name is deterministic based on sorted user emails.
	
	Args:
		target_user: Email of user to DM
	
	Returns:
		DM room document as dict
	"""
	current_user = frappe.session.user
	
	if current_user == target_user:
		frappe.throw(_("Cannot start a DM with yourself"))
	
	if not frappe.db.exists("User", target_user):
		frappe.throw(_("User does not exist"))
	
	# Get user full names
	current_user_name = frappe.db.get_value("User", current_user, "full_name") or current_user
	other_user_name = frappe.db.get_value("User", target_user, "full_name") or target_user
	
	# Create deterministic room name by sorting emails
	sorted_users = sorted([current_user, target_user])
	dm_identifier = f"dm_{sorted_users[0]}_{sorted_users[1]}"
	
	# Check if DM room already exists
	existing_room = frappe.db.sql("""
		SELECT DISTINCT cr.name
		FROM `tabMkaguzi Chat Room` cr
		INNER JOIN `tabMkaguzi Chat Participant` cp1 ON cp1.parent = cr.name AND cp1.user = %s
		INNER JOIN `tabMkaguzi Chat Participant` cp2 ON cp2.parent = cr.name AND cp2.user = %s
		WHERE cr.room_type = 'Private'
			AND cr.is_active = 1
			AND (
				SELECT COUNT(*) FROM `tabMkaguzi Chat Participant` 
				WHERE parent = cr.name AND is_active = 1
			) = 2
		LIMIT 1
	""", (current_user, target_user), as_dict=True)
	
	if existing_room:
		room = frappe.get_doc("Mkaguzi Chat Room", existing_room[0].name)
		return room.as_dict()
	
	# Create new DM room
	room = frappe.get_doc({
		"doctype": "Mkaguzi Chat Room",
		"room_name": f"DM: {current_user_name} & {other_user_name}",
		"room_type": "Private",
		"description": f"Direct message between {current_user_name} and {other_user_name}",
		"is_ai_enabled": 1,
		"is_active": 1,
		"created_by": current_user
	})
	
	# Add both users as participants before insert to prevent auto-addition
	room.append("participants", {
		"user": current_user,
		"role": "Admin",
		"is_active": 1
	})
	room.append("participants", {
		"user": target_user,
		"role": "Admin", 
		"is_active": 1
	})
	
	# Don't trigger the default on_insert participant logic
	room.flags.skip_auto_participant = True
	room.insert(ignore_permissions=True)
	
	return room.as_dict()


@frappe.whitelist()
def get_user_dm_rooms() -> dict:
	"""
	Get all DM rooms for the current user.
	
	Returns:
		Dict with rooms list
	"""
	user = frappe.session.user
	
	rooms = frappe.db.sql("""
		SELECT DISTINCT 
			cr.name,
			cr.room_name,
			cr.room_type,
			cr.description,
			cr.is_ai_enabled,
			cr.message_count,
			cr.last_message_at,
			cr.is_active
		FROM `tabMkaguzi Chat Room` cr
		INNER JOIN `tabMkaguzi Chat Participant` cp ON cp.parent = cr.name
		WHERE cp.user = %s 
			AND cp.is_active = 1
			AND cr.room_type = 'Private'
			AND cr.is_active = 1
		ORDER BY COALESCE(cr.last_message_at, '1970-01-01') DESC
	""", (user,), as_dict=True)
	
	# For each DM room, get the other participant's info
	for room in rooms:
		other_participant = frappe.db.sql("""
			SELECT cp.user, u.full_name, u.user_image
			FROM `tabMkaguzi Chat Participant` cp
			LEFT JOIN `tabUser` u ON u.name = cp.user
			WHERE cp.parent = %s 
				AND cp.user != %s 
				AND cp.is_active = 1
			LIMIT 1
		""", (room.name, user), as_dict=True)
		
		if other_participant:
			room.dm_user = other_participant[0].user
			room.dm_user_name = other_participant[0].full_name or other_participant[0].user
			room.dm_user_image = other_participant[0].user_image
			# Override room_name to show other user's name
			room.display_name = other_participant[0].full_name or other_participant[0].user
	
	return {"rooms": rooms}


@frappe.whitelist()
def search_users(query: str = "", limit: int = 50) -> list[dict]:
	"""
	Search for users to start a DM with.
	
	Args:
		query: Search query (name or email). If empty, returns all users.
		limit: Max results
	
	Returns:
		List of user dictionaries
	"""
	current_user = frappe.session.user
	
	# If no query, return all enabled users (for DM list)
	if not query or query.strip() == "":
		users = frappe.db.sql("""
			SELECT 
				name as email,
				full_name,
				user_image
			FROM `tabUser`
			WHERE enabled = 1
				AND name != %s
			ORDER BY full_name
			LIMIT %s
		""", (current_user, limit), as_dict=True)
	else:
		# Search by name or email
		users = frappe.db.sql("""
			SELECT 
				name as email,
				full_name,
				user_image
			FROM `tabUser`
			WHERE enabled = 1
				AND name != %s
				AND (
					full_name LIKE %s
					OR name LIKE %s
				)
			ORDER BY full_name
			LIMIT %s
		""", (current_user, f"%{query}%", f"%{query}%", limit), as_dict=True)
	
	return users


# ============================================
# Messaging APIs
# ============================================

@frappe.whitelist()
def get_messages(
	room_name: str,
	limit: int = 50,
	offset: int = 0,
	before_timestamp: str = None
) -> list[dict]:
	"""
	Get messages for a chat room.
	
	Args:
		room_name: Room name
		limit: Max messages to return
		offset: Offset for pagination
		before_timestamp: Get messages before this timestamp
	
	Returns:
		List of message dictionaries
	"""
	# Verify user has access
	room_doc = frappe.get_doc("Mkaguzi Chat Room", room_name)
	if not room_doc.is_participant():
		frappe.throw(_("You are not a participant in this chat room"))
	
	filters = {
		"room": room_name,
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
			"is_edited", "edited_at", "is_reply", "reply_to_message",
			"reply_preview", "context_chunks_used", "tokens_used",
			"response_time_ms"
		],
		order_by="created_at desc",
		limit_page_length=limit,
		start=offset
	)
	
	# Reverse to get chronological order
	messages.reverse()
	
	return messages


@frappe.whitelist()
def send_message(
	room_name: str,
	content: str,
	message_type: str = 'User',
	reply_to: str = None
) -> dict:
	"""
	Send a message to a chat room.
	
	Args:
		room_name: Room name
		content: Message content
		message_type: Type of message (Text, Image, File, etc.)
		reply_to: Message to reply to
	
	Returns:
		Dict with message and optional AI response
	"""
	from mkaguzi.chat_system.chat_service import send_chat_message
	return send_chat_message(room_name, content, False, reply_to, message_type)


@frappe.whitelist()
def edit_message(message_name: str, new_content: str) -> dict:
	"""
	Edit a message.
	
	Args:
		message_name: Name of the message to edit
		new_content: New content
	
	Returns:
		Updated message
	"""
	message = frappe.get_doc("Mkaguzi Chat Message", message_name)
	message.edit_content(new_content)
	
	# Publish real-time event
	frappe.publish_realtime(
		'mkaguzi_message_updated',
		{
			'room': message.room,
			'message': message.as_dict()
		},
		user=frappe.session.user
	)
	
	return message.as_dict()


@frappe.whitelist()
def delete_message(message_name: str) -> dict:
	"""
	Soft delete a message.
	
	Args:
		message_name: Name of the message to delete
	
	Returns:
		Success status
	"""
	message = frappe.get_doc("Mkaguzi Chat Message", message_name)
	message.soft_delete()
	
	# Publish real-time event
	frappe.publish_realtime(
		'mkaguzi_message_deleted',
		{
			'room': message.room,
			'message_name': message_name
		},
		user=frappe.session.user
	)
	
	return {"success": True}


# ============================================
# Real-time APIs
# ============================================

@frappe.whitelist()
def start_typing(room_name: str) -> dict:
	"""
	Start typing indicator for a room.
	
	Args:
		room_name: Name of the room
	
	Returns:
		Success status
	"""
	# Verify user has access
	room_doc = frappe.get_doc("Mkaguzi Chat Room", room_name)
	if not room_doc.is_participant():
		frappe.throw(_("You are not a participant in this chat room"))
	
	user_fullname = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user
	
	# Publish real-time event
	frappe.publish_realtime(
		'mkaguzi_typing_start',
		{
			'room': room_name,
			'user': frappe.session.user,
			'full_name': user_fullname
		},
		user=frappe.session.user
	)
	
	return {"success": True}


@frappe.whitelist()
def stop_typing(room_name: str) -> dict:
	"""
	Stop typing indicator for a room.
	
	Args:
		room_name: Name of the room
	
	Returns:
		Success status
	"""
	# Verify user has access
	room_doc = frappe.get_doc("Mkaguzi Chat Room", room_name)
	if not room_doc.is_participant():
		frappe.throw(_("You are not a participant in this chat room"))
	
	# Publish real-time event
	frappe.publish_realtime(
		'mkaguzi_typing_stop',
		{
			'room': room_name,
			'user': frappe.session.user
		},
		user=frappe.session.user
	)
	
	return {"success": True}


@frappe.whitelist()
def join_room_realtime(room_name: str) -> dict:
	"""
	Join a room and publish presence event.
	
	Args:
		room_name: Name of the room
	
	Returns:
		Success status
	"""
	# This would be called when user switches to a room
	# Publish user joined event
	frappe.publish_realtime(
		'mkaguzi_user_joined',
		{
			'room': room_name,
			'user': frappe.session.user
		},
		user=frappe.session.user
	)
	
	return {"success": True}


@frappe.whitelist()
def leave_room_realtime(room_name: str) -> dict:
	"""
	Leave a room and publish presence event.
	
	Args:
		room_name: Name of the room
	
	Returns:
		Success status
	"""
	# Publish user left event
	frappe.publish_realtime(
		'mkaguzi_user_left',
		{
			'room': room_name,
			'user': frappe.session.user
		},
		user=frappe.session.user
	)
	
	return {"success": True}


# ============================================
# AI APIs
# ============================================

@frappe.whitelist()
def get_ai_response(room_name: str, user_message: str, include_context: bool = True) -> dict:
	"""
	Get an AI response for a message.
	
	Args:
		room_name: Room name
		user_message: Message to get AI response for
		include_context: Whether to include RAG context
	
	Returns:
		AI response details
	"""
	from mkaguzi.chat_system.chat_service import get_ai_chat_response
	return get_ai_chat_response(room_name, user_message)


@frappe.whitelist()
def ask_ai(room: str, question: str, include_context: bool = True) -> dict:
	"""
	Ask the AI a question without sending a user message.
	
	Args:
		room: Room name
		question: Question to ask
		include_context: Whether to include RAG context
	
	Returns:
		AI response
	"""
	from mkaguzi.chat_system.chat_service import ChatService
	
	# Verify access
	room_doc = frappe.get_doc("Mkaguzi Chat Room", room)
	if not room_doc.is_participant():
		frappe.throw(_("You are not a participant in this chat room"))
	
	if not room_doc.is_ai_enabled:
		frappe.throw(_("AI is not enabled for this room"))
	
	service = ChatService(room)
	return service.get_ai_response(question)


# ============================================
# RAG APIs
# ============================================

@frappe.whitelist()
def search_context(query: str, engagement: str = None, max_results: int = 5) -> list[dict]:
	"""
	Search for relevant context in the RAG index.
	
	Args:
		query: Search query
		engagement: Optional engagement to scope to
		max_results: Maximum results to return
	
	Returns:
		List of context chunks
	"""
	from mkaguzi.ai.rag.retriever import get_retriever
	
	retriever = get_retriever()
	contexts = retriever.retrieve(query, engagement=engagement, max_chunks=max_results)
	
	return [ctx.to_dict() for ctx in contexts]


@frappe.whitelist()
def get_rag_stats() -> dict:
	"""
	Get RAG index statistics.
	
	Returns:
		Dict with index statistics
	"""
	from mkaguzi.ai.rag.indexer import get_indexer
	
	indexer = get_indexer()
	return indexer.get_index_stats()


@frappe.whitelist()
def rebuild_rag_index() -> dict:
	"""
	Trigger a full RAG index rebuild.
	
	Returns:
		Status message
	"""
	# Check permission
	if not frappe.has_permission("Mkaguzi Chat Settings", "write"):
		frappe.throw(_("You don't have permission to rebuild the RAG index"))
	
	settings = frappe.get_single("Mkaguzi Chat Settings")
	settings.rebuild_index()
	
	return {"success": True, "message": "Index rebuild has been queued"}


@frappe.whitelist()
def index_document(doctype: str, docname: str) -> dict:
	"""
	Index a specific document.
	
	Args:
		doctype: Document type
		docname: Document name
	
	Returns:
		Indexing result
	"""
	from mkaguzi.ai.rag.indexer import index_document_by_name
	
	chunks = index_document_by_name(doctype, docname)
	
	return {
		"success": True,
		"chunks_indexed": chunks
	}


# ============================================
# Utility APIs
# ============================================

@frappe.whitelist()
def get_active_engagements() -> list[dict]:
	"""
	Get active audit engagements for room creation.
	
	Returns:
		List of active engagements
	"""
	from mkaguzi.audit_execution.doctype.audit_engagement.audit_engagement import get_active_audits
	
	result = get_active_audits()
	return result.get("audits", [])


@frappe.whitelist()
def test_ai_connection() -> dict:
	"""
	Test the OpenRouter API connection.
	
	Returns:
		Connection test result
	"""
	from mkaguzi.ai.openrouter_client import OpenRouterClient
	
	client = OpenRouterClient()
	return client.test_connection()


@frappe.whitelist()
def get_available_models() -> list[dict]:
	"""
	Get available AI models.
	
	Returns:
		List of available models
	"""
	models = [
		{
			"id": "meta-llama/llama-3.1-8b-instruct:free",
			"name": "Llama 3.1 8B",
			"provider": "Meta",
			"description": "Fast and capable general-purpose model"
		},
		{
			"id": "google/gemma-2-9b-it:free",
			"name": "Gemma 2 9B",
			"provider": "Google",
			"description": "Google's instruction-tuned model"
		},
		{
			"id": "qwen/qwen-2.5-7b-instruct:free",
			"name": "Qwen 2.5 7B",
			"provider": "Alibaba",
			"description": "Strong multilingual capabilities"
		},
		{
			"id": "mistralai/mistral-7b-instruct:free",
			"name": "Mistral 7B",
			"provider": "Mistral AI",
			"description": "Efficient and balanced model"
		},
		{
			"id": "microsoft/phi-3-mini-128k-instruct:free",
			"name": "Phi-3 Mini",
			"provider": "Microsoft",
			"description": "Compact model with long context"
		}
	]
	
	return models


@frappe.whitelist()
def get_chat_settings() -> dict:
	"""
	Get the Mkaguzi Chat Settings.
	
	Returns:
		Dict with chat settings
	"""
	settings = frappe.get_single("Mkaguzi Chat Settings")
	return settings.as_dict()


@frappe.whitelist()
def save_chat_settings(settings_data: dict) -> dict:
	"""
	Save the Mkaguzi Chat Settings.
	
	Args:
		settings_data: Dict with settings to save
	
	Returns:
		Success status
	"""
	# Check permissions
	if not frappe.has_permission("Mkaguzi Chat Settings", "write"):
		frappe.throw(_("You don't have permission to modify chat settings"))
	
	settings = frappe.get_single("Mkaguzi Chat Settings")
	
	# Update settings with provided data
	for key, value in settings_data.items():
		if hasattr(settings, key):
			setattr(settings, key, value)
	
	settings.save()
	
	return {"success": True, "message": "Settings saved successfully"}
