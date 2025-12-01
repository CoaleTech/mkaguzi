# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

"""
RAG (Retrieval-Augmented Generation) Module

Components:
- embeddings: Sentence transformer embeddings using all-MiniLM-L6-v2
- chunker: Semantic document chunking for audit documents
- indexer: ChromaDB document indexing
- retriever: Context retrieval with engagement scope filtering
"""

from mkaguzi.ai.rag.embeddings import EmbeddingModel
from mkaguzi.ai.rag.chunker import SemanticChunker
from mkaguzi.ai.rag.indexer import DocumentIndexer
from mkaguzi.ai.rag.retriever import ContextRetriever

__all__ = ["EmbeddingModel", "SemanticChunker", "DocumentIndexer", "ContextRetriever"]
