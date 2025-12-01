# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

"""
ChromaDB Indexer for Mkaguzi RAG System

Handles document indexing into ChromaDB vector store:
- Document chunking and embedding
- Metadata storage for filtering
- Incremental and full index rebuilds
- Engagement-scoped collections
"""

import json
from typing import Optional
from datetime import datetime

import frappe
from frappe.utils import now_datetime

from mkaguzi.ai.rag.embeddings import get_embedding_model
from mkaguzi.ai.rag.chunker import get_chunker, DocumentChunk


# Global ChromaDB client (lazy loaded)
_chroma_client = None
_collection = None


class DocumentIndexer:
	"""
	Indexes audit documents into ChromaDB for RAG retrieval.
	
	Supports:
	- Audit Finding, Working Paper, Audit Program
	- Test Execution, Risk Assessment, Compliance Requirement
	- Engagement-scoped filtering
	- Incremental updates
	"""
	
	def __init__(self, collection_name: Optional[str] = None):
		"""
		Initialize the indexer.
		
		Args:
			collection_name: ChromaDB collection name (defaults from settings)
		"""
		self.collection_name = collection_name or self._get_collection_name()
		self.embedding_model = get_embedding_model()
		self.chunker = get_chunker()
		self._client = None
		self._collection = None
	
	def _get_collection_name(self) -> str:
		"""Get collection name from settings."""
		try:
			settings = frappe.get_single("Mkaguzi Chat Settings")
			return settings.chromadb_collection_name or "mkaguzi_audit_docs"
		except Exception:
			return "mkaguzi_audit_docs"
	
	def _get_client(self):
		"""Get or create ChromaDB client."""
		if self._client is None:
			try:
				import chromadb
				from chromadb.config import Settings
				
				# Use persistent storage in site directory
				persist_dir = frappe.get_site_path("private", "chromadb")
				
				self._client = chromadb.PersistentClient(
					path=persist_dir,
					settings=Settings(
						anonymized_telemetry=False,
						allow_reset=True
					)
				)
				
				frappe.logger().info(f"ChromaDB client initialized at {persist_dir}")
				
			except ImportError:
				frappe.throw(
					"chromadb is not installed. "
					"Please run: pip install chromadb"
				)
			except Exception as e:
				frappe.throw(f"Failed to initialize ChromaDB: {str(e)}")
		
		return self._client
	
	def _get_collection(self):
		"""Get or create the document collection."""
		if self._collection is None:
			client = self._get_client()
			
			# Create or get collection with cosine similarity
			self._collection = client.get_or_create_collection(
				name=self.collection_name,
				metadata={"hnsw:space": "cosine"}
			)
			
			frappe.logger().info(
				f"ChromaDB collection '{self.collection_name}' loaded with "
				f"{self._collection.count()} documents"
			)
		
		return self._collection
	
	def index_document(self, doc: "frappe.model.document.Document") -> int:
		"""
		Index a single document.
		
		Args:
			doc: Frappe document to index
		
		Returns:
			Number of chunks indexed
		"""
		collection = self._get_collection()
		
		# Delete existing chunks for this document
		self._delete_document_chunks(doc.doctype, doc.name)
		
		# Chunk the document
		chunks = self.chunker.chunk_document(doc)
		
		if not chunks:
			return 0
		
		# Generate embeddings
		texts = [chunk.content for chunk in chunks]
		embeddings = self.embedding_model.embed_texts(texts)
		
		# Prepare data for ChromaDB
		ids = []
		documents = []
		metadatas = []
		
		for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
			chunk_id = f"{chunk.doctype}:{chunk.docname}:{chunk.chunk_index}"
			ids.append(chunk_id)
			documents.append(chunk.content)
			
			metadata = {
				"doctype": chunk.doctype,
				"docname": chunk.docname,
				"section": chunk.section,
				"chunk_index": chunk.chunk_index,
				"indexed_at": now_datetime().isoformat(),
				**{k: str(v) if v else "" for k, v in chunk.metadata.items()}
			}
			metadatas.append(metadata)
		
		# Add to collection
		collection.add(
			ids=ids,
			documents=documents,
			embeddings=embeddings,
			metadatas=metadatas
		)
		
		frappe.logger().info(
			f"Indexed {len(chunks)} chunks for {doc.doctype} {doc.name}"
		)
		
		return len(chunks)
	
	def _delete_document_chunks(self, doctype: str, docname: str):
		"""Delete all chunks for a document."""
		collection = self._get_collection()
		
		try:
			# Query for existing chunks
			results = collection.get(
				where={"$and": [
					{"doctype": {"$eq": doctype}},
					{"docname": {"$eq": docname}}
				]}
			)
			
			if results and results.get("ids"):
				collection.delete(ids=results["ids"])
				frappe.logger().debug(
					f"Deleted {len(results['ids'])} existing chunks for {doctype} {docname}"
				)
		except Exception as e:
			# Collection might be empty or document might not exist
			frappe.logger().debug(f"No existing chunks to delete: {str(e)}")
	
	def delete_document(self, doctype: str, docname: str):
		"""Delete a document from the index."""
		self._delete_document_chunks(doctype, docname)
	
	def index_doctype(self, doctype: str, filters: Optional[dict] = None) -> int:
		"""
		Index all documents of a given type.
		
		Args:
			doctype: DocType to index
			filters: Optional filters for document selection
		
		Returns:
			Total chunks indexed
		"""
		total_chunks = 0
		
		# Get all documents
		docs = frappe.get_all(doctype, filters=filters or {}, pluck="name")
		
		for docname in docs:
			try:
				doc = frappe.get_doc(doctype, docname)
				chunks_indexed = self.index_document(doc)
				total_chunks += chunks_indexed
			except Exception as e:
				frappe.log_error(
					f"Error indexing {doctype} {docname}: {str(e)}",
					"RAG Indexing Error"
				)
		
		return total_chunks
	
	def get_index_stats(self) -> dict:
		"""Get statistics about the index."""
		collection = self._get_collection()
		
		total_count = collection.count()
		
		# Get counts by doctype
		doctype_counts = {}
		for doctype in ["Audit Finding", "Working Paper", "Audit Program", 
						"Test Execution", "Risk Assessment", "Compliance Requirement"]:
			try:
				result = collection.get(where={"doctype": {"$eq": doctype}})
				doctype_counts[doctype] = len(result.get("ids", []))
			except Exception:
				doctype_counts[doctype] = 0
		
		return {
			"total_chunks": total_count,
			"by_doctype": doctype_counts,
			"collection_name": self.collection_name
		}
	
	def reset_index(self):
		"""Clear and reset the entire index."""
		client = self._get_client()
		
		try:
			client.delete_collection(self.collection_name)
			self._collection = None
			frappe.logger().info(f"Reset ChromaDB collection: {self.collection_name}")
		except Exception as e:
			frappe.logger().warning(f"Error resetting collection: {str(e)}")
		
		# Recreate empty collection
		self._get_collection()


def get_indexer() -> DocumentIndexer:
	"""Get a configured indexer instance."""
	return DocumentIndexer()


def index_document_by_name(doctype: str, docname: str):
	"""Index a document by its type and name."""
	doc = frappe.get_doc(doctype, docname)
	indexer = get_indexer()
	return indexer.index_document(doc)


def delete_document_from_index(doctype: str, docname: str):
	"""Delete a document from the index."""
	indexer = get_indexer()
	indexer.delete_document(doctype, docname)


def rebuild_full_index():
	"""
	Rebuild the entire RAG index.
	
	This is a long-running task that should be queued.
	"""
	settings = frappe.get_single("Mkaguzi Chat Settings")
	indexer = get_indexer()
	
	# Reset the index
	indexer.reset_index()
	
	total_chunks = 0
	total_docs = 0
	
	# Get enabled doctypes from settings
	doctypes_to_index = settings.get_enabled_doctypes()
	
	for doctype in doctypes_to_index:
		try:
			# Check if doctype exists
			if not frappe.db.exists("DocType", doctype):
				frappe.logger().warning(f"DocType {doctype} does not exist, skipping")
				continue
			
			doc_count = frappe.db.count(doctype)
			frappe.logger().info(f"Indexing {doc_count} documents of type {doctype}")
			
			chunks = indexer.index_doctype(doctype)
			total_chunks += chunks
			total_docs += doc_count
			
		except Exception as e:
			frappe.log_error(
				f"Error indexing {doctype}: {str(e)}",
				"RAG Full Index Error"
			)
	
	# Update settings with index status
	settings.db_set("last_full_index", now_datetime())
	settings.db_set("total_documents_indexed", total_docs)
	settings.db_set("index_status", "Completed")
	
	frappe.logger().info(
		f"Full index rebuild complete: {total_docs} documents, {total_chunks} chunks"
	)
	
	return {
		"documents_indexed": total_docs,
		"chunks_created": total_chunks
	}


# Document event hooks
def on_document_update(doc, method):
	"""Hook to update index when a document is updated."""
	settings = frappe.get_single("Mkaguzi Chat Settings")
	
	if not settings.enable_rag:
		return
	
	# Check if this doctype should be indexed
	enabled_doctypes = settings.get_enabled_doctypes()
	
	if doc.doctype in enabled_doctypes:
		# Queue the indexing to avoid slowing down the save
		frappe.enqueue(
			"mkaguzi.ai.rag.indexer.index_document_by_name",
			doctype=doc.doctype,
			docname=doc.name,
			queue="short",
			now=frappe.flags.in_test
		)


def on_document_delete(doc, method):
	"""Hook to remove document from index when deleted."""
	settings = frappe.get_single("Mkaguzi Chat Settings")
	
	if not settings.enable_rag:
		return
	
	enabled_doctypes = settings.get_enabled_doctypes()
	
	if doc.doctype in enabled_doctypes:
		frappe.enqueue(
			"mkaguzi.ai.rag.indexer.delete_document_from_index",
			doctype=doc.doctype,
			docname=doc.name,
			queue="short",
			now=frappe.flags.in_test
		)
