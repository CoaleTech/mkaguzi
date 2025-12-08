# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

"""
Chat Service Layer for Mkaguzi

Orchestrates the chat functionality:
- Message handling
- RAG context retrieval
- AI response generation
- Response storage
"""

import json
import time
from typing import Optional

import frappe
from frappe import _
from frappe.utils import now_datetime

from mkaguzi.ai.openrouter_client import OpenRouterClient, ChatMessage
from mkaguzi.ai.rag.retriever import get_retriever


class ChatService:
	"""
	Service class for chat operations.
	
	Handles:
	- Sending messages
	- Getting AI responses with RAG context
	- Message history management
	"""
	
	def __init__(self, room_name: str):
		"""
		Initialize the chat service for a room.
		
		Args:
			room_name: Name of the Mkaguzi Chat Room
		"""
		self.room_name = room_name
		self.room = None
		self.settings = None
		self._load_room()
		self._load_settings()
	
	def _load_room(self):
		"""Load the chat room document."""
		self.room = frappe.get_doc("Mkaguzi Chat Room", self.room_name)
	
	def _load_settings(self):
		"""Load chat settings."""
		self.settings = frappe.get_single("Mkaguzi Chat Settings")
	
	def get_ai_response_with_prompt(
		self,
		user_message: str,
		system_prompt: str = None,
		include_history: bool = False,
		max_history_messages: int = 10
	) -> dict:
		"""
		Get an AI response with optional custom system prompt.
		
		Args:
			user_message: The user's message
			system_prompt: Optional custom system prompt to override room default
			include_history: Whether to include conversation history
			max_history_messages: Max history messages to include
		
		Returns:
			Dict with response content and metadata
		"""
		if not self.settings.enable_ai_chat:
			return {"error": "AI chat is not enabled"}
		
		if not self.room.is_ai_enabled:
			return {"error": "AI is not enabled for this room"}
		
		start_time = time.time()
		
		# Build messages for the AI with custom system prompt
		messages = self._build_messages_with_prompt(
			user_message,
			system_prompt,
			include_history,
			max_history_messages
		)
		
		# Get AI response
		client = OpenRouterClient()
		model = self.room.get_ai_model()
		
		try:
			response = client.chat_completion(
				messages=messages,
				model_override=model
			)
			
			response_time = int((time.time() - start_time) * 1000)
			
			return {
				"response": response.content,
				"model": response.model,
				"tokens_used": response.tokens_used,
				"response_time_ms": response_time,
				"success": True
			}
			
		except Exception as e:
			frappe.log_error(f"AI Response Error: {str(e)}", "Chat Service")
			return {
				"error": f"Failed to get AI response: {str(e)}",
				"success": False
			}
		"""
		Get an AI response to a user message.
		
		Args:
			user_message: The user's message
			user_message_id: Optional ID of the user message (for reply linking)
			include_history: Whether to include conversation history
			max_history_messages: Max history messages to include
		
		Returns:
			Dict with response content and metadata
		"""
		if not self.settings.enable_ai_chat:
			return {"error": "AI chat is not enabled"}
		
		if not self.room.is_ai_enabled:
			return {"error": "AI is not enabled for this room"}
		
		start_time = time.time()
		
		# Build messages for the AI
		messages = self._build_messages(
			user_message,
			include_history,
			max_history_messages
		)
		
		# Get AI response
		client = OpenRouterClient()
		model = self.room.get_ai_model()
		
		try:
			response = client.chat_completion(
				messages=messages,
				model_override=model
			)
			
			response_time = int((time.time() - start_time) * 1000)
			
			# Get context sources for storage
			retriever = get_retriever()
			contexts = retriever.retrieve_for_room(user_message, self.room_name)
			context_sources = retriever.get_context_sources_json(contexts)
			
			# Create AI message
			ai_message = self._create_ai_message(
				content=response.content,
				model_used=response.model,
				tokens_used=response.tokens_used,
				response_time_ms=response_time,
				context_sources=context_sources,
				context_chunks_used=len(contexts),
				reply_to=user_message_id
			)
			
			return {
				"success": True,
				"content": response.content,
				"message_id": ai_message.name,
				"model": response.model,
				"tokens_used": response.tokens_used,
				"response_time_ms": response_time,
				"context_chunks_used": len(contexts)
			}
			
		except Exception as e:
			frappe.log_error(f"AI response error: {str(e)}", "Chat AI Error")
			return {
				"success": False,
				"error": str(e)
			}
	
	def _build_messages(
		self,
		user_message: str,
		include_history: bool,
		max_history_messages: int
	) -> list[ChatMessage]:
		"""Build the message list for the AI."""
		messages = []
		
		# System prompt
		system_prompt = self.room.get_system_prompt()
		
		# Add RAG context if enabled
		if self.settings.enable_rag:
			retriever = get_retriever()
			contexts = retriever.retrieve_for_room(user_message, self.room_name)
			
			if contexts:
				context_text = retriever.format_context_for_prompt(contexts)
				system_prompt += f"\n\n{context_text}"
		
		messages.append(ChatMessage(role="system", content=system_prompt))
		
		# Add conversation history
		if include_history:
			history = self._get_conversation_history(max_history_messages)
			messages.extend(history)
		
		# Add current user message
		messages.append(ChatMessage(role="user", content=user_message))
		
		return messages
	
	def _build_messages_with_prompt(
		self,
		user_message: str,
		system_prompt: str = None,
		include_history: bool = False,
		max_history_messages: int = 10
	) -> list[ChatMessage]:
		"""Build the message list for the AI with optional custom system prompt."""
		messages = []
		
		# Use custom system prompt or default room prompt
		if system_prompt:
			final_system_prompt = system_prompt
		else:
			final_system_prompt = self.room.get_system_prompt()
		
		# Add RAG context if enabled and no custom system prompt (to avoid conflicts)
		if self.settings.enable_rag and not system_prompt:
			retriever = get_retriever()
			contexts = retriever.retrieve_for_room(user_message, self.room_name)
			
			if contexts:
				context_text = retriever.format_context_for_prompt(contexts)
				final_system_prompt += f"\n\n{context_text}"
		
		messages.append(ChatMessage(role="system", content=final_system_prompt))
		
		# Add conversation history (only if requested and no custom system prompt)
		if include_history and not system_prompt:
			history = self._get_conversation_history(max_history_messages)
			messages.extend(history)
		
		# Add current user message
		messages.append(ChatMessage(role="user", content=user_message))
		
		return messages
	
	def _get_conversation_history(self, max_messages: int) -> list[ChatMessage]:
		"""Get recent conversation history."""
		# Get recent messages from this room
		recent_messages = frappe.get_all(
			"Mkaguzi Chat Message",
			filters={
				"room": self.room_name,
				"is_deleted": 0,
				"message_type": ["in", ["User", "AI"]]
			},
			fields=["message_type", "content", "sender"],
			order_by="created_at desc",
			limit=max_messages
		)
		
		# Reverse to get chronological order
		recent_messages.reverse()
		
		history = []
		for msg in recent_messages:
			if msg.message_type == "User":
				history.append(ChatMessage(role="user", content=msg.content))
			elif msg.message_type == "AI":
				history.append(ChatMessage(role="assistant", content=msg.content))
		
		return history
	
	def _create_ai_message(
		self,
		content: str,
		model_used: str,
		tokens_used: int,
		response_time_ms: int,
		context_sources: str,
		context_chunks_used: int,
		reply_to: Optional[str] = None
	) -> "frappe.model.document.Document":
		"""Create an AI message document."""
		message = frappe.get_doc({
			"doctype": "Mkaguzi Chat Message",
			"room": self.room_name,
			"message_type": "AI",
			"content": content,
			"is_ai_generated": 1,
			"ai_model_used": model_used,
			"tokens_used": tokens_used,
			"response_time_ms": response_time_ms,
			"context_sources": context_sources,
			"context_chunks_used": context_chunks_used,
			"is_reply": 1 if reply_to else 0,
			"reply_to_message": reply_to
		})
		message.insert(ignore_permissions=True)
		
		return message
	
	def send_system_message(self, content: str) -> "frappe.model.document.Document":
		"""Send a system message to the room."""
		message = frappe.get_doc({
			"doctype": "Mkaguzi Chat Message",
			"room": self.room_name,
			"message_type": "System",
			"content": content
		})
		message.insert(ignore_permissions=True)
		
		return message


def get_ai_response(room_name: str, user_message: str, user_message_id: Optional[str] = None) -> dict:
	"""
	Get an AI response for a chat room.
	
	Args:
		room_name: Name of the chat room
		user_message: The user's message
		user_message_id: Optional ID of the user message
	
	Returns:
		Dict with response details
	"""
	service = ChatService(room_name)
	return service.get_ai_response(user_message, user_message_id)


@frappe.whitelist()
def send_chat_message(
	room: str,
	content: str,
	request_ai_response: bool = False,
	reply_to: Optional[str] = None,
	message_type: str = "Text"
) -> dict:
	"""
	Send a message to a chat room.
	
	Args:
		room: Room name
		content: Message content
		request_ai_response: Whether to request an AI response
		reply_to: Optional message to reply to
		message_type: Type of message (Text, Image, File, etc.)
	
	Returns:
		Dict with message and optional AI response
	"""
	# Verify user has access
	room_doc = frappe.get_doc("Mkaguzi Chat Room", room)
	if not room_doc.is_participant():
		frappe.throw(_("You are not a participant in this chat room"))
	
	# Create user message
	message = frappe.get_doc({
		"doctype": "Mkaguzi Chat Message",
		"room": room,
		"message_type": message_type,
		"content": content,
		"sender": frappe.session.user,
		"is_reply": 1 if reply_to else 0,
		"reply_to_message": reply_to
	})
	message.insert()
	
	# Publish real-time event
	frappe.publish_realtime(
		'mkaguzi_chat_message',
		{
			'room': room,
			'message': message.as_dict()
		},
		user=frappe.session.user
	)
	
	result = {
		"success": True,
		"message": message.as_dict(),
		"ai_response": None
	}
	
	# Request AI response if enabled
	if request_ai_response and room_doc.is_ai_enabled:
		try:
			ai_result = get_ai_response(room, content, message.name)
			result["ai_response"] = ai_result
		except Exception as e:
			frappe.log_error(f"AI response error: {str(e)}")
			result["ai_error"] = str(e)
	
	return result


@frappe.whitelist()
def get_ai_chat_response(room: str, message: str, system_prompt: str = None) -> dict:
	"""
	Get an AI response without sending a user message first.
	
	Useful for asking the AI questions directly.
	
	Args:
		room: Room name
		message: The question/message for the AI
		system_prompt: Optional custom system prompt to override room default
	
	Returns:
		Dict with AI response details
	"""
	# Special handling for AI specialist - bypass room verification
	if room == "ai-specialist":
		return get_ai_response_with_prompt(room, message, system_prompt)
	
	# Verify user has access for regular rooms
	room_doc = frappe.get_doc("Mkaguzi Chat Room", room)
	if not room_doc.is_participant():
		frappe.throw(_("You are not a participant in this chat room"))
	
	if not room_doc.is_ai_enabled:
		frappe.throw(_("AI is not enabled for this room"))
	
	return get_ai_response_with_prompt(room, message, system_prompt)


def get_ai_response_with_prompt(room_name: str, user_message: str, system_prompt: str = None) -> dict:
	"""
	Get an AI response with optional custom system prompt.
	
	Args:
		room_name: Name of the chat room
		user_message: The user's message
		system_prompt: Optional custom system prompt
	
	Returns:
		Dict with response details
	"""
	# Special handling for AI specialist
	if room_name == "ai-specialist":
		return get_ai_specialist_response(user_message, system_prompt)
	
	service = ChatService(room_name)
	return service.get_ai_response_with_prompt(user_message, system_prompt)


def get_ai_specialist_response(user_message: str, system_prompt: str = None) -> dict:
	"""
	Get an AI response for AI specialist queries without requiring a room.
	
	Args:
		user_message: The user's message
		system_prompt: Custom system prompt for the specialist
	
	Returns:
		Dict with response details
	"""
	from mkaguzi.ai.openrouter_client import OpenRouterClient
	
	# Check if AI chat is enabled globally
	settings = frappe.get_single("Mkaguzi Chat Settings")
	if not settings.enable_ai_chat:
		return {"error": "AI chat is not enabled", "success": False}
	
	start_time = time.time()
	
	# Build messages
	messages = []
	
	# Use provided system prompt or default
	if system_prompt:
		messages.append(ChatMessage(role="system", content=system_prompt))
	else:
		messages.append(ChatMessage(role="system", content="You are an AI assistant specializing in internal audit and compliance. Provide helpful, accurate responses."))
	
	messages.append(ChatMessage(role="user", content=user_message))
	
	# Get AI response
	client = OpenRouterClient()
	
	try:
		response = client.chat_completion(
			messages=messages,
			model_override=settings.default_model or "meta-llama/llama-3.1-8b-instruct:free"
		)
		
		response_time = int((time.time() - start_time) * 1000)
		
		return {
			"response": response.content,
			"model": response.model,
			"tokens_used": response.tokens_used,
			"response_time_ms": response_time,
			"success": True
		}
		
	except Exception as e:
		frappe.log_error(f"AI Specialist Response Error: {str(e)}", "Chat Service")
		return {
			"error": f"Failed to get AI response: {str(e)}",
			"success": False
		}
