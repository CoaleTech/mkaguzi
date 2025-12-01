# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

"""
Context Retriever for Mkaguzi RAG System

Retrieves relevant document chunks from ChromaDB based on:
- Semantic similarity to query
- Engagement scope filtering
- Document type filtering
- Minimum similarity threshold
"""

import json
from typing import Optional
from dataclasses import dataclass

import frappe

from mkaguzi.ai.rag.embeddings import get_embedding_model
from mkaguzi.ai.rag.indexer import DocumentIndexer


@dataclass
class RetrievedContext:
	"""Represents a retrieved context chunk."""
	content: str
	doctype: str
	docname: str
	section: str
	similarity_score: float
	metadata: dict
	
	def to_dict(self) -> dict:
		"""Convert to dictionary."""
		return {
			"content": self.content,
			"doctype": self.doctype,
			"docname": self.docname,
			"section": self.section,
			"similarity_score": self.similarity_score,
			"metadata": self.metadata
		}
	
	def get_source_reference(self) -> str:
		"""Get a human-readable source reference."""
		return f"{self.doctype}: {self.docname} ({self.section})"


class ContextRetriever:
	"""
	Retrieves relevant context from the vector store.
	
	Features:
	- Semantic similarity search
	- Engagement-scoped filtering
	- Document type filtering
	- Configurable thresholds
	"""
	
	def __init__(
		self,
		max_chunks: Optional[int] = None,
		similarity_threshold: Optional[float] = None,
		scope_to_engagement: Optional[bool] = None
	):
		"""
		Initialize the retriever.
		
		Args:
			max_chunks: Maximum chunks to retrieve
			similarity_threshold: Minimum similarity score
			scope_to_engagement: Whether to filter by engagement
		"""
		self.embedding_model = get_embedding_model()
		self.indexer = DocumentIndexer()
		
		# Load settings
		self._load_settings(max_chunks, similarity_threshold, scope_to_engagement)
	
	def _load_settings(
		self,
		max_chunks: Optional[int],
		similarity_threshold: Optional[float],
		scope_to_engagement: Optional[bool]
	):
		"""Load settings with overrides."""
		try:
			settings = frappe.get_single("Mkaguzi Chat Settings")
			self.max_chunks = max_chunks or settings.max_context_chunks or 5
			self.similarity_threshold = similarity_threshold or settings.similarity_threshold or 0.7
			self.scope_to_engagement = (
				scope_to_engagement if scope_to_engagement is not None 
				else settings.scope_to_engagement
			)
		except Exception:
			self.max_chunks = max_chunks or 5
			self.similarity_threshold = similarity_threshold or 0.7
			self.scope_to_engagement = scope_to_engagement if scope_to_engagement is not None else True
	
	def retrieve(
		self,
		query: str,
		engagement: Optional[str] = None,
		doctype_filter: Optional[list[str]] = None,
		max_chunks: Optional[int] = None
	) -> list[RetrievedContext]:
		"""
		Retrieve relevant context chunks for a query.
		
		Args:
			query: The search query
			engagement: Optional engagement to scope to
			doctype_filter: Optional list of doctypes to filter
			max_chunks: Optional override for max chunks
		
		Returns:
			List of RetrievedContext objects sorted by relevance
		"""
		max_results = max_chunks or self.max_chunks
		
		# Generate query embedding
		query_embedding = self.embedding_model.embed_text(query)
		
		# Build where filter
		where_filter = self._build_where_filter(engagement, doctype_filter)
		
		# Query ChromaDB
		collection = self.indexer._get_collection()
		
		try:
			results = collection.query(
				query_embeddings=[query_embedding],
				n_results=max_results * 2,  # Get extra to filter by threshold
				where=where_filter if where_filter else None,
				include=["documents", "metadatas", "distances"]
			)
		except Exception as e:
			frappe.log_error(f"Context retrieval error: {str(e)}")
			return []
		
		# Process results
		contexts = []
		
		if results and results.get("ids") and results["ids"][0]:
			ids = results["ids"][0]
			documents = results["documents"][0]
			metadatas = results["metadatas"][0]
			distances = results["distances"][0]
			
			for i, (doc_id, content, metadata, distance) in enumerate(
				zip(ids, documents, metadatas, distances)
			):
				# Convert distance to similarity (ChromaDB uses cosine distance)
				# Cosine distance = 1 - cosine similarity
				similarity = 1 - distance
				
				# Filter by threshold
				if similarity < self.similarity_threshold:
					continue
				
				context = RetrievedContext(
					content=content,
					doctype=metadata.get("doctype", ""),
					docname=metadata.get("docname", ""),
					section=metadata.get("section", ""),
					similarity_score=similarity,
					metadata=metadata
				)
				contexts.append(context)
		
		# Sort by similarity and limit
		contexts.sort(key=lambda x: x.similarity_score, reverse=True)
		return contexts[:max_results]
	
	def _build_where_filter(
		self,
		engagement: Optional[str],
		doctype_filter: Optional[list[str]]
	) -> Optional[dict]:
		"""Build the where filter for ChromaDB query."""
		conditions = []
		
		# Add engagement filter if scoping is enabled and engagement is provided
		if self.scope_to_engagement and engagement:
			conditions.append({"engagement": {"$eq": engagement}})
		
		# Add doctype filter if provided
		if doctype_filter and len(doctype_filter) > 0:
			if len(doctype_filter) == 1:
				conditions.append({"doctype": {"$eq": doctype_filter[0]}})
			else:
				conditions.append({"doctype": {"$in": doctype_filter}})
		
		if not conditions:
			return None
		elif len(conditions) == 1:
			return conditions[0]
		else:
			return {"$and": conditions}
	
	def retrieve_for_room(
		self,
		query: str,
		room_name: str,
		max_chunks: Optional[int] = None
	) -> list[RetrievedContext]:
		"""
		Retrieve context for a chat room query.
		
		Automatically scopes to the room's linked engagement if any.
		
		Args:
			query: The search query
			room_name: Name of the chat room
			max_chunks: Optional override for max chunks
		
		Returns:
			List of RetrievedContext objects
		"""
		# Get room details
		try:
			room = frappe.get_doc("Mkaguzi Chat Room", room_name)
			engagement = room.linked_engagement
		except Exception:
			engagement = None
		
		return self.retrieve(
			query=query,
			engagement=engagement,
			max_chunks=max_chunks
		)
	
	def format_context_for_prompt(
		self,
		contexts: list[RetrievedContext],
		include_sources: bool = True
	) -> str:
		"""
		Format retrieved contexts for inclusion in LLM prompt.
		
		Args:
			contexts: List of retrieved contexts
			include_sources: Whether to include source references
		
		Returns:
			Formatted context string
		"""
		if not contexts:
			return ""
		
		formatted_parts = ["### Relevant Context from Audit Documents:\n"]
		
		for i, ctx in enumerate(contexts, 1):
			part = f"**[{i}] {ctx.doctype} - {ctx.docname}**"
			if ctx.section:
				part += f" ({ctx.section})"
			part += f"\n{ctx.content}\n"
			
			formatted_parts.append(part)
		
		if include_sources:
			formatted_parts.append("\n### Sources:")
			for i, ctx in enumerate(contexts, 1):
				formatted_parts.append(f"[{i}] {ctx.get_source_reference()}")
		
		return "\n".join(formatted_parts)
	
	def get_context_sources_json(self, contexts: list[RetrievedContext]) -> str:
		"""
		Get context sources as JSON for storage.
		
		Args:
			contexts: List of retrieved contexts
		
		Returns:
			JSON string of source references
		"""
		sources = []
		
		for ctx in contexts:
			sources.append({
				"doctype": ctx.doctype,
				"docname": ctx.docname,
				"section": ctx.section,
				"similarity": round(ctx.similarity_score, 3)
			})
		
		return json.dumps(sources)


def get_retriever(**kwargs) -> ContextRetriever:
	"""Get a configured retriever instance."""
	return ContextRetriever(**kwargs)


def retrieve_context(
	query: str,
	engagement: Optional[str] = None,
	max_chunks: Optional[int] = None
) -> list[RetrievedContext]:
	"""
	Convenience function to retrieve context.
	
	Args:
		query: The search query
		engagement: Optional engagement to scope to
		max_chunks: Optional max chunks
	
	Returns:
		List of RetrievedContext objects
	"""
	retriever = get_retriever()
	return retriever.retrieve(query, engagement=engagement, max_chunks=max_chunks)
