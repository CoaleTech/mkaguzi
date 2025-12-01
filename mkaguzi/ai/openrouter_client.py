# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

"""
OpenRouter Client for Mkaguzi Chat System

Provides integration with OpenRouter API for accessing free-tier LLMs:
- meta-llama/llama-3.1-8b-instruct:free
- google/gemma-2-9b-it:free
- qwen/qwen-2.5-7b-instruct:free
- mistralai/mistral-7b-instruct:free
- microsoft/phi-3-mini-128k-instruct:free
"""

import json
from typing import Generator, Optional
from dataclasses import dataclass

import frappe
import httpx


# OpenRouter API Configuration
OPENROUTER_API_URL = "https://openrouter.ai/api/v1"
OPENROUTER_CHAT_ENDPOINT = f"{OPENROUTER_API_URL}/chat/completions"
OPENROUTER_MODELS_ENDPOINT = f"{OPENROUTER_API_URL}/models"


@dataclass
class ChatMessage:
	"""Represents a chat message for the API."""
	role: str  # "system", "user", or "assistant"
	content: str


@dataclass
class ChatResponse:
	"""Represents a chat completion response."""
	content: str
	model: str
	tokens_used: int
	finish_reason: str
	response_time_ms: int


class OpenRouterClient:
	"""
	Client for OpenRouter API integration.
	
	Supports:
	- Chat completions with context
	- Streaming responses
	- Model fallback on failure
	- Token tracking
	"""
	
	def __init__(self):
		"""Initialize the OpenRouter client with settings from Mkaguzi Chat Settings."""
		self.settings = None
		self._load_settings()
	
	def _load_settings(self):
		"""Load settings from Mkaguzi Chat Settings."""
		try:
			self.settings = frappe.get_single("Mkaguzi Chat Settings")
		except Exception:
			# Settings might not exist yet during installation
			self.settings = None
	
	def _get_api_key(self) -> str:
		"""Get the OpenRouter API key from settings."""
		if not self.settings:
			self._load_settings()
		
		if not self.settings or not self.settings.openrouter_api_key:
			frappe.throw("OpenRouter API key is not configured. Please configure it in Mkaguzi Chat Settings.")
		
		return self.settings.get_password("openrouter_api_key")
	
	def _get_headers(self) -> dict:
		"""Get headers for API requests."""
		return {
			"Authorization": f"Bearer {self._get_api_key()}",
			"Content-Type": "application/json",
			"HTTP-Referer": frappe.utils.get_url(),
			"X-Title": "Mkaguzi Internal Audit System"
		}
	
	def _get_model(self, model_override: Optional[str] = None) -> str:
		"""Get the model to use for the request."""
		if model_override:
			return model_override
		
		if self.settings:
			return self.settings.default_model or "meta-llama/llama-3.1-8b-instruct:free"
		
		return "meta-llama/llama-3.1-8b-instruct:free"
	
	def _get_fallback_model(self) -> str:
		"""Get the fallback model."""
		if self.settings and self.settings.fallback_model:
			return self.settings.fallback_model
		
		return "qwen/qwen-2.5-7b-instruct:free"
	
	def test_connection(self) -> dict:
		"""Test the API connection and return available models info."""
		try:
			with httpx.Client(timeout=30) as client:
				response = client.get(
					OPENROUTER_MODELS_ENDPOINT,
					headers=self._get_headers()
				)
				
				if response.status_code == 200:
					data = response.json()
					models = data.get("data", [])
					free_models = [m for m in models if ":free" in m.get("id", "")]
					
					return {
						"success": True,
						"models_count": len(models),
						"free_models_count": len(free_models)
					}
				else:
					return {
						"success": False,
						"error": f"API returned status {response.status_code}: {response.text}"
					}
					
		except Exception as e:
			return {
				"success": False,
				"error": str(e)
			}
	
	def chat_completion(
		self,
		messages: list[ChatMessage],
		model_override: Optional[str] = None,
		temperature: Optional[float] = None,
		max_tokens: Optional[int] = None,
		top_p: Optional[float] = None
	) -> ChatResponse:
		"""
		Get a chat completion from OpenRouter.
		
		Args:
			messages: List of ChatMessage objects
			model_override: Optional model to use instead of default
			temperature: Optional temperature override
			max_tokens: Optional max tokens override
			top_p: Optional top_p override
		
		Returns:
			ChatResponse with the completion
		"""
		import time
		start_time = time.time()
		
		# Build request payload
		model = self._get_model(model_override)
		payload = {
			"model": model,
			"messages": [{"role": m.role, "content": m.content} for m in messages],
			"temperature": temperature or (self.settings.temperature if self.settings else 0.7),
			"max_tokens": max_tokens or (self.settings.max_tokens if self.settings else 2048),
			"top_p": top_p or (self.settings.top_p if self.settings else 0.9)
		}
		
		try:
			with httpx.Client(timeout=120) as client:
				response = client.post(
					OPENROUTER_CHAT_ENDPOINT,
					headers=self._get_headers(),
					json=payload
				)
				
				response_time_ms = int((time.time() - start_time) * 1000)
				
				if response.status_code == 200:
					data = response.json()
					choice = data.get("choices", [{}])[0]
					usage = data.get("usage", {})
					
					return ChatResponse(
						content=choice.get("message", {}).get("content", ""),
						model=data.get("model", model),
						tokens_used=usage.get("total_tokens", 0),
						finish_reason=choice.get("finish_reason", "unknown"),
						response_time_ms=response_time_ms
					)
				
				elif response.status_code == 429:
					# Rate limited, try fallback model
					frappe.log_error(f"Rate limited on {model}, trying fallback")
					return self._try_fallback(messages, temperature, max_tokens, top_p)
				
				else:
					frappe.throw(f"OpenRouter API error: {response.status_code} - {response.text}")
					
		except httpx.TimeoutException:
			# Timeout, try fallback model
			frappe.log_error(f"Timeout on {model}, trying fallback")
			return self._try_fallback(messages, temperature, max_tokens, top_p)
		
		except Exception as e:
			frappe.throw(f"OpenRouter API error: {str(e)}")
	
	def _try_fallback(
		self,
		messages: list[ChatMessage],
		temperature: Optional[float] = None,
		max_tokens: Optional[int] = None,
		top_p: Optional[float] = None
	) -> ChatResponse:
		"""Try the fallback model."""
		fallback_model = self._get_fallback_model()
		
		return self.chat_completion(
			messages=messages,
			model_override=fallback_model,
			temperature=temperature,
			max_tokens=max_tokens,
			top_p=top_p
		)
	
	def chat_completion_stream(
		self,
		messages: list[ChatMessage],
		model_override: Optional[str] = None,
		temperature: Optional[float] = None,
		max_tokens: Optional[int] = None
	) -> Generator[str, None, None]:
		"""
		Stream a chat completion from OpenRouter.
		
		Args:
			messages: List of ChatMessage objects
			model_override: Optional model to use
			temperature: Optional temperature override
			max_tokens: Optional max tokens override
		
		Yields:
			Content chunks as they arrive
		"""
		model = self._get_model(model_override)
		payload = {
			"model": model,
			"messages": [{"role": m.role, "content": m.content} for m in messages],
			"temperature": temperature or (self.settings.temperature if self.settings else 0.7),
			"max_tokens": max_tokens or (self.settings.max_tokens if self.settings else 2048),
			"stream": True
		}
		
		try:
			with httpx.Client(timeout=120) as client:
				with client.stream(
					"POST",
					OPENROUTER_CHAT_ENDPOINT,
					headers=self._get_headers(),
					json=payload
				) as response:
					
					if response.status_code != 200:
						frappe.throw(f"OpenRouter API error: {response.status_code}")
					
					for line in response.iter_lines():
						if line.startswith("data: "):
							data_str = line[6:]  # Remove "data: " prefix
							
							if data_str == "[DONE]":
								break
							
							try:
								data = json.loads(data_str)
								delta = data.get("choices", [{}])[0].get("delta", {})
								content = delta.get("content", "")
								
								if content:
									yield content
									
							except json.JSONDecodeError:
								continue
								
		except Exception as e:
			frappe.log_error(f"Streaming error: {str(e)}")
			raise


def get_openrouter_client() -> OpenRouterClient:
	"""Get a configured OpenRouter client instance."""
	return OpenRouterClient()
