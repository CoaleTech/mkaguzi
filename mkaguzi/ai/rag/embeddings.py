# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

"""
Embedding Module for Mkaguzi RAG System

Uses sentence-transformers with all-MiniLM-L6-v2 model for generating
document embeddings. This model provides:
- 384-dimensional embeddings
- Fast inference
- Good quality for semantic similarity
"""

from typing import Optional
import frappe


# Global model instance (lazy loaded)
_embedding_model = None


class EmbeddingModel:
	"""
	Wrapper for sentence-transformers embedding model.
	
	Uses all-MiniLM-L6-v2 by default for good balance of speed and quality.
	"""
	
	def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
		"""
		Initialize the embedding model.
		
		Args:
			model_name: Name of the sentence-transformers model to use
		"""
		self.model_name = model_name
		self._model = None
	
	def _load_model(self):
		"""Lazy load the model on first use."""
		if self._model is None:
			try:
				from sentence_transformers import SentenceTransformer
				self._model = SentenceTransformer(self.model_name)
				frappe.logger().info(f"Loaded embedding model: {self.model_name}")
			except ImportError:
				frappe.throw(
					"sentence-transformers is not installed. "
					"Please run: pip install sentence-transformers"
				)
			except Exception as e:
				frappe.throw(f"Failed to load embedding model: {str(e)}")
	
	def embed_text(self, text: str) -> list[float]:
		"""
		Generate embedding for a single text.
		
		Args:
			text: Text to embed
		
		Returns:
			List of floats representing the embedding vector
		"""
		self._load_model()
		
		if not text or not text.strip():
			# Return zero vector for empty text
			return [0.0] * self.embedding_dimension
		
		embedding = self._model.encode(text, convert_to_numpy=True)
		return embedding.tolist()
	
	def embed_texts(self, texts: list[str]) -> list[list[float]]:
		"""
		Generate embeddings for multiple texts.
		
		Args:
			texts: List of texts to embed
		
		Returns:
			List of embedding vectors
		"""
		self._load_model()
		
		# Filter out empty texts and track their positions
		valid_texts = []
		valid_indices = []
		
		for i, text in enumerate(texts):
			if text and text.strip():
				valid_texts.append(text)
				valid_indices.append(i)
		
		if not valid_texts:
			return [[0.0] * self.embedding_dimension for _ in texts]
		
		# Batch encode valid texts
		embeddings = self._model.encode(valid_texts, convert_to_numpy=True)
		
		# Reconstruct full list with zero vectors for empty texts
		result = []
		valid_idx = 0
		
		for i in range(len(texts)):
			if i in valid_indices:
				result.append(embeddings[valid_idx].tolist())
				valid_idx += 1
			else:
				result.append([0.0] * self.embedding_dimension)
		
		return result
	
	@property
	def embedding_dimension(self) -> int:
		"""Get the dimension of embeddings produced by this model."""
		# all-MiniLM-L6-v2 produces 384-dimensional embeddings
		model_dimensions = {
			"all-MiniLM-L6-v2": 384,
			"all-mpnet-base-v2": 768,
			"paraphrase-MiniLM-L6-v2": 384
		}
		return model_dimensions.get(self.model_name, 384)


def get_embedding_model(model_name: Optional[str] = None) -> EmbeddingModel:
	"""
	Get the embedding model instance.
	
	Uses a global singleton for efficiency. The model is loaded
	from settings or defaults to all-MiniLM-L6-v2.
	
	Args:
		model_name: Optional model name override
	
	Returns:
		EmbeddingModel instance
	"""
	global _embedding_model
	
	# Get model name from settings if not provided
	if model_name is None:
		try:
			settings = frappe.get_single("Mkaguzi Chat Settings")
			model_name = settings.embedding_model or "all-MiniLM-L6-v2"
		except Exception:
			model_name = "all-MiniLM-L6-v2"
	
	# Create or return cached model
	if _embedding_model is None or _embedding_model.model_name != model_name:
		_embedding_model = EmbeddingModel(model_name)
	
	return _embedding_model


def embed_text(text: str) -> list[float]:
	"""
	Convenience function to embed a single text.
	
	Args:
		text: Text to embed
	
	Returns:
		Embedding vector as list of floats
	"""
	model = get_embedding_model()
	return model.embed_text(text)


def embed_texts(texts: list[str]) -> list[list[float]]:
	"""
	Convenience function to embed multiple texts.
	
	Args:
		texts: List of texts to embed
	
	Returns:
		List of embedding vectors
	"""
	model = get_embedding_model()
	return model.embed_texts(texts)
