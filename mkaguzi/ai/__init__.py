# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

"""
AI Module for Mkaguzi

Provides AI capabilities including:
- OpenRouter LLM client for chat completions
- RAG (Retrieval-Augmented Generation) pipeline
- Document embeddings and vector storage
"""

from mkaguzi.ai.openrouter_client import OpenRouterClient

__all__ = ["OpenRouterClient"]
