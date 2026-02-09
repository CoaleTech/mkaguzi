# License: MIT

import json
import requests
from datetime import datetime, timedelta
import frappe
from frappe import _


@frappe.whitelist()
def fetch_available_models():
	"""Fetch available models from OpenRouter API and cache them"""
	
	if not frappe.has_permission("Mkaguzi Settings", "write"):
		frappe.throw("Not enough permissions to fetch models")
	
	try:
		settings = frappe.get_single("Mkaguzi Settings")
		
		if not settings.api_key:
			frappe.throw("OpenRouter API key not configured")
		
		# Check if we have recent cached data (less than 24 hours old)
		if settings.models_last_fetched:
			last_fetch = frappe.utils.get_datetime(settings.models_last_fetched)
			if datetime.now() - last_fetch < timedelta(hours=24):
				# Return cached data
				free_models = json.loads(settings.available_free_models or "[]")
				paid_models = json.loads(settings.available_paid_models or "[]")
				
				return {
					"success": True,
					"free_models": free_models,
					"paid_models": paid_models,
					"cached": True,
					"last_fetched": settings.models_last_fetched
				}
		
		# Fetch fresh data from OpenRouter
		headers = {
			"Authorization": f"Bearer {settings.get_password('api_key')}",
			"HTTP-Referer": frappe.utils.get_url(),
			"X-Title": "Mkaguzi Audit System"
		}
		
		response = requests.get(
			"https://openrouter.ai/api/v1/models",
			headers=headers,
			timeout=30
		)
		
		if response.status_code != 200:
			frappe.throw(f"OpenRouter API error: {response.status_code} - {response.text}")
		
		models_data = response.json()
		models = models_data.get("data", [])
		
		# Separate free and paid models
		free_models = []
		paid_models = []
		
		for model in models:
			model_info = {
				"id": model.get("id"),
				"name": model.get("name", model.get("id")),
				"context_length": model.get("context_length"),
				"pricing": model.get("pricing", {})
			}
			
			# Check if model is free (prompt cost is 0)
			prompt_cost = float(model.get("pricing", {}).get("prompt", "1"))
			
			if prompt_cost == 0:
				free_models.append(model_info)
			else:
				paid_models.append(model_info)
		
		# Sort models by name
		free_models.sort(key=lambda x: x["name"])
		paid_models.sort(key=lambda x: x["name"])
		
		# Update cached data
		settings.available_free_models = json.dumps(free_models)
		settings.available_paid_models = json.dumps(paid_models)
		settings.models_last_fetched = datetime.now()
		settings.save(ignore_permissions=True)
		
		frappe.db.commit()
		
		return {
			"success": True,
			"free_models": free_models,
			"paid_models": paid_models,
			"cached": False,
			"total_models": len(models),
			"free_count": len(free_models),
			"paid_count": len(paid_models)
		}
		
	except requests.RequestException as e:
		frappe.log_error(f"Failed to fetch OpenRouter models: {str(e)}", "OpenRouter Models Fetch")
		frappe.throw(f"Failed to connect to OpenRouter: {str(e)}")
		
	except Exception as e:
		frappe.log_error(f"Error fetching OpenRouter models: {str(e)}", "OpenRouter Models Fetch")
		frappe.throw(f"Error fetching models: {str(e)}")


@frappe.whitelist()
def get_model_recommendations():
	"""Get recommended model configurations"""
	
	try:
		settings = frappe.get_single("Mkaguzi Settings")
		
		# Get cached models
		free_models = json.loads(settings.available_free_models or "[]")
		paid_models = json.loads(settings.available_paid_models or "[]")
		
		# Recommend top free models
		recommended_free = [
			model for model in free_models 
			if any(name in model["id"].lower() for name in ["llama-3.1", "gemma-2", "qwen"])
		][:5]  # Top 5 free models
		
		# Recommend top paid models
		recommended_paid = [
			model for model in paid_models
			if any(name in model["id"].lower() for name in ["claude", "gpt-4", "gemini"])
		][:5]  # Top 5 paid models
		
		return {
			"success": True,
			"recommended_free": recommended_free,
			"recommended_paid": recommended_paid
		}
		
	except Exception as e:
		frappe.log_error(f"Error getting model recommendations: {str(e)}", "OpenRouter Models")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def test_openrouter_connection():
	"""Test OpenRouter API connection and return account info"""
	
	if not frappe.has_permission("Mkaguzi Settings", "read"):
		frappe.throw("Not enough permissions to test connection")
	
	try:
		settings = frappe.get_single("Mkaguzi Settings")
		
		if not settings.api_key:
			frappe.throw("OpenRouter API key not configured")
		
		# Call the auth endpoint
		headers = {
			"Authorization": f"Bearer {settings.get_password('api_key')}",
			"HTTP-Referer": frappe.utils.get_url(),
			"X-Title": "Mkaguzi Audit System"
		}
		
		response = requests.get(
			"https://openrouter.ai/api/v1/auth/key",
			headers=headers,
			timeout=10
		)
		
		if response.status_code == 200:
			data = response.json()
			credit_data = data.get("data", {})
			credit_limit = credit_data.get("limit")  # None = unlimited (free tier)
			credit_used = credit_data.get("usage") or 0
			credit_remaining = (credit_limit - credit_used) if credit_limit is not None else None
			return {
				"success": True,
				"message": "✓ Connection successful",
				"credits_limit": credit_limit if credit_limit is not None else "Unlimited",
				"credits_used": credit_used,
				"credits_remaining": credit_remaining if credit_remaining is not None else "Unlimited"
			}
		elif response.status_code == 401:
			return {
				"success": False,
				"error": "Invalid API key (401 Unauthorized)"
			}
		else:
			return {
				"success": False,
				"error": f"Connection failed ({response.status_code}): {response.text[:200]}"
			}
			
	except requests.Timeout:
		return {
			"success": False,
			"error": "Connection timed out. Check your network or OpenRouter API status."
		}
	except requests.RequestException as e:
		return {
			"success": False,
			"error": f"Network error: {str(e)[:200]}"
		}
	except Exception as e:
		frappe.log_error(f"Error testing OpenRouter connection: {str(e)}", "OpenRouter Connection Test")
		return {
			"success": False,
			"error": f"Error: {str(e)[:200]}"
		}