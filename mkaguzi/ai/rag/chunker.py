# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

"""
Semantic Chunker for Mkaguzi RAG System

Implements semantic chunking strategies for audit documents:
- Section-based chunking for structured documents (Audit Finding, Working Paper)
- Field-based chunking for table-like documents (Test Execution, Risk Assessment)
- Fallback character-based chunking for unstructured content
"""

import re
from dataclasses import dataclass
from typing import Optional
from bs4 import BeautifulSoup
import frappe


@dataclass
class DocumentChunk:
	"""Represents a chunk of a document for indexing."""
	content: str
	doctype: str
	docname: str
	section: str  # e.g., "condition", "criteria", "recommendation"
	chunk_index: int
	metadata: dict
	
	def to_dict(self) -> dict:
		"""Convert to dictionary for storage."""
		return {
			"content": self.content,
			"doctype": self.doctype,
			"docname": self.docname,
			"section": self.section,
			"chunk_index": self.chunk_index,
			**self.metadata
		}


class SemanticChunker:
	"""
	Semantic document chunker for audit documents.
	
	Implements document-type-specific chunking strategies:
	- Audit Finding: condition, criteria, cause, effect, recommendation sections
	- Working Paper: procedures_performed, findings_summary, conclusion sections
	- Audit Program: per-procedure chunking
	- Test Execution: per-result chunking
	- Risk Assessment: per-risk-item chunking
	- Compliance Requirement: full-document with headers
	"""
	
	def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
		"""
		Initialize the chunker.
		
		Args:
			chunk_size: Maximum characters per chunk (for fallback)
			chunk_overlap: Overlap between chunks
		"""
		self.chunk_size = chunk_size
		self.chunk_overlap = chunk_overlap
	
	def chunk_document(self, doc: "frappe.model.document.Document") -> list[DocumentChunk]:
		"""
		Chunk a Frappe document based on its type.
		
		Args:
			doc: Frappe document to chunk
		
		Returns:
			List of DocumentChunk objects
		"""
		doctype = doc.doctype
		
		# Route to appropriate chunker
		chunker_map = {
			"Audit Finding": self._chunk_audit_finding,
			"Working Paper": self._chunk_working_paper,
			"Audit Program": self._chunk_audit_program,
			"Test Execution": self._chunk_test_execution,
			"Risk Assessment": self._chunk_risk_assessment,
			"Compliance Requirement": self._chunk_compliance_requirement
		}
		
		chunker = chunker_map.get(doctype, self._chunk_generic)
		return chunker(doc)
	
	def _strip_html(self, html_content: str) -> str:
		"""Strip HTML tags and clean up content."""
		if not html_content:
			return ""
		
		try:
			soup = BeautifulSoup(html_content, "html.parser")
			text = soup.get_text(separator="\n")
			# Clean up extra whitespace
			text = re.sub(r'\n\s*\n', '\n\n', text)
			return text.strip()
		except Exception:
			# Fallback: simple regex-based HTML stripping
			text = re.sub(r'<[^>]+>', '', html_content)
			return text.strip()
	
	def _create_chunk(
		self,
		content: str,
		doctype: str,
		docname: str,
		section: str,
		chunk_index: int,
		engagement: Optional[str] = None,
		**extra_metadata
	) -> DocumentChunk:
		"""Create a DocumentChunk with standard metadata."""
		metadata = {
			"engagement": engagement or "",
			**extra_metadata
		}
		
		return DocumentChunk(
			content=content,
			doctype=doctype,
			docname=docname,
			section=section,
			chunk_index=chunk_index,
			metadata=metadata
		)
	
	def _chunk_audit_finding(self, doc) -> list[DocumentChunk]:
		"""
		Chunk an Audit Finding document by section.
		
		Sections: condition, criteria, cause, effect, recommendation, management_comments
		"""
		chunks = []
		chunk_index = 0
		
		# Get engagement reference for scoping
		engagement = doc.get("engagement_reference") or ""
		risk_rating = doc.get("risk_rating") or ""
		finding_category = doc.get("finding_category") or ""
		
		# Define sections to chunk
		sections = [
			("condition", "Condition (What was found)"),
			("criteria", "Criteria (What should be)"),
			("cause", "Cause (Why it happened)"),
			("effect", "Effect (Impact/Consequences)"),
			("recommendation", "Recommendation"),
			("management_comments", "Management Response")
		]
		
		# Add title/summary chunk
		title = doc.get("finding_title") or ""
		if title:
			header = f"Finding: {title}\nCategory: {finding_category}\nRisk Rating: {risk_rating}"
			chunks.append(self._create_chunk(
				content=header,
				doctype="Audit Finding",
				docname=doc.name,
				section="summary",
				chunk_index=chunk_index,
				engagement=engagement,
				risk_rating=risk_rating,
				finding_category=finding_category
			))
			chunk_index += 1
		
		# Chunk each section
		for field_name, section_label in sections:
			content = self._strip_html(doc.get(field_name) or "")
			
			if content and len(content) > 20:  # Skip very short content
				# Add section header for context
				full_content = f"{section_label}:\n{content}"
				
				# Split if too long
				if len(full_content) > self.chunk_size:
					sub_chunks = self._split_text(full_content)
					for sub_chunk in sub_chunks:
						chunks.append(self._create_chunk(
							content=sub_chunk,
							doctype="Audit Finding",
							docname=doc.name,
							section=field_name,
							chunk_index=chunk_index,
							engagement=engagement,
							risk_rating=risk_rating,
							finding_category=finding_category
						))
						chunk_index += 1
				else:
					chunks.append(self._create_chunk(
						content=full_content,
						doctype="Audit Finding",
						docname=doc.name,
						section=field_name,
						chunk_index=chunk_index,
						engagement=engagement,
						risk_rating=risk_rating,
						finding_category=finding_category
					))
					chunk_index += 1
		
		return chunks
	
	def _chunk_working_paper(self, doc) -> list[DocumentChunk]:
		"""Chunk a Working Paper document by section."""
		chunks = []
		chunk_index = 0
		
		engagement = doc.get("engagement") or doc.get("audit_engagement") or ""
		
		# Working paper sections
		sections = [
			("objective", "Objective"),
			("scope", "Scope"),
			("procedures_performed", "Procedures Performed"),
			("findings_summary", "Findings Summary"),
			("conclusion", "Conclusion"),
			("recommendations", "Recommendations")
		]
		
		# Add header chunk
		title = doc.get("working_paper_title") or doc.get("title") or ""
		wp_type = doc.get("working_paper_type") or ""
		
		if title:
			header = f"Working Paper: {title}\nType: {wp_type}"
			chunks.append(self._create_chunk(
				content=header,
				doctype="Working Paper",
				docname=doc.name,
				section="header",
				chunk_index=chunk_index,
				engagement=engagement,
				wp_type=wp_type
			))
			chunk_index += 1
		
		# Chunk each section
		for field_name, section_label in sections:
			content = self._strip_html(doc.get(field_name) or "")
			
			if content and len(content) > 20:
				full_content = f"{section_label}:\n{content}"
				
				if len(full_content) > self.chunk_size:
					for sub_chunk in self._split_text(full_content):
						chunks.append(self._create_chunk(
							content=sub_chunk,
							doctype="Working Paper",
							docname=doc.name,
							section=field_name,
							chunk_index=chunk_index,
							engagement=engagement
						))
						chunk_index += 1
				else:
					chunks.append(self._create_chunk(
						content=full_content,
						doctype="Working Paper",
						docname=doc.name,
						section=field_name,
						chunk_index=chunk_index,
						engagement=engagement
					))
					chunk_index += 1
		
		return chunks
	
	def _chunk_audit_program(self, doc) -> list[DocumentChunk]:
		"""Chunk an Audit Program by procedure."""
		chunks = []
		chunk_index = 0
		
		engagement = doc.get("audit_engagement") or ""
		program_name = doc.get("program_name") or ""
		audit_area = doc.get("audit_area") or ""
		
		# Add program header
		header = f"Audit Program: {program_name}\nAudit Area: {audit_area}"
		chunks.append(self._create_chunk(
			content=header,
			doctype="Audit Program",
			docname=doc.name,
			section="header",
			chunk_index=chunk_index,
			engagement=engagement,
			audit_area=audit_area
		))
		chunk_index += 1
		
		# Chunk each procedure from child table
		procedures = doc.get("program_procedures") or []
		
		for proc in procedures:
			proc_name = proc.get("procedure_name") or proc.get("description") or ""
			proc_desc = proc.get("detailed_steps") or proc.get("procedure_description") or ""
			expected_result = proc.get("expected_result") or ""
			status = proc.get("status") or ""
			
			content = f"Procedure: {proc_name}\n"
			if proc_desc:
				content += f"Steps: {self._strip_html(proc_desc)}\n"
			if expected_result:
				content += f"Expected Result: {self._strip_html(expected_result)}\n"
			if status:
				content += f"Status: {status}"
			
			if len(content.strip()) > 20:
				chunks.append(self._create_chunk(
					content=content.strip(),
					doctype="Audit Program",
					docname=doc.name,
					section="procedure",
					chunk_index=chunk_index,
					engagement=engagement,
					audit_area=audit_area,
					procedure_status=status
				))
				chunk_index += 1
		
		return chunks
	
	def _chunk_test_execution(self, doc) -> list[DocumentChunk]:
		"""Chunk a Test Execution document."""
		chunks = []
		chunk_index = 0
		
		engagement = doc.get("audit_engagement") or ""
		test_name = doc.get("test_name") or ""
		result = doc.get("result") or ""
		
		# Main test info
		content = f"Test: {test_name}\nResult: {result}\n"
		
		# Add test details
		methodology = doc.get("methodology") or doc.get("test_methodology") or ""
		if methodology:
			content += f"Methodology: {self._strip_html(methodology)}\n"
		
		conclusion = doc.get("conclusion") or ""
		if conclusion:
			content += f"Conclusion: {self._strip_html(conclusion)}\n"
		
		exceptions = doc.get("exceptions_description") or ""
		if exceptions:
			content += f"Exceptions: {self._strip_html(exceptions)}"
		
		chunks.append(self._create_chunk(
			content=content.strip(),
			doctype="Test Execution",
			docname=doc.name,
			section="test_result",
			chunk_index=chunk_index,
			engagement=engagement,
			test_result=result
		))
		
		return chunks
	
	def _chunk_risk_assessment(self, doc) -> list[DocumentChunk]:
		"""Chunk a Risk Assessment document."""
		chunks = []
		chunk_index = 0
		
		# Risk assessment header
		assessment_name = doc.get("assessment_name") or doc.get("title") or ""
		assessment_type = doc.get("assessment_type") or ""
		overall_rating = doc.get("overall_risk_rating") or ""
		
		header = f"Risk Assessment: {assessment_name}\nType: {assessment_type}\nOverall Rating: {overall_rating}"
		chunks.append(self._create_chunk(
			content=header,
			doctype="Risk Assessment",
			docname=doc.name,
			section="header",
			chunk_index=chunk_index,
			overall_rating=overall_rating
		))
		chunk_index += 1
		
		# Chunk risk register items
		risk_items = doc.get("risk_register") or []
		
		for item in risk_items:
			risk_desc = item.get("risk_description") or ""
			impact = item.get("impact") or item.get("impact_score") or ""
			likelihood = item.get("likelihood") or item.get("likelihood_score") or ""
			mitigation = item.get("mitigation_strategy") or item.get("existing_controls") or ""
			
			content = f"Risk: {self._strip_html(risk_desc)}\n"
			content += f"Impact: {impact}, Likelihood: {likelihood}\n"
			if mitigation:
				content += f"Mitigation: {self._strip_html(mitigation)}"
			
			if len(content.strip()) > 20:
				chunks.append(self._create_chunk(
					content=content.strip(),
					doctype="Risk Assessment",
					docname=doc.name,
					section="risk_item",
					chunk_index=chunk_index
				))
				chunk_index += 1
		
		return chunks
	
	def _chunk_compliance_requirement(self, doc) -> list[DocumentChunk]:
		"""Chunk a Compliance Requirement document."""
		chunks = []
		chunk_index = 0
		
		requirement_name = doc.get("requirement_name") or doc.get("title") or ""
		requirement_type = doc.get("requirement_type") or ""
		regulatory_body = doc.get("regulatory_body") or ""
		
		# Header with metadata
		header = f"Compliance Requirement: {requirement_name}\nType: {requirement_type}\nRegulator: {regulatory_body}"
		chunks.append(self._create_chunk(
			content=header,
			doctype="Compliance Requirement",
			docname=doc.name,
			section="header",
			chunk_index=chunk_index,
			requirement_type=requirement_type
		))
		chunk_index += 1
		
		# Requirement details
		description = self._strip_html(doc.get("description") or doc.get("requirement_description") or "")
		guidance = self._strip_html(doc.get("guidance") or doc.get("compliance_guidance") or "")
		penalties = self._strip_html(doc.get("penalties") or doc.get("non_compliance_penalties") or "")
		
		if description:
			content = f"Requirement Details:\n{description}"
			chunks.append(self._create_chunk(
				content=content,
				doctype="Compliance Requirement",
				docname=doc.name,
				section="description",
				chunk_index=chunk_index,
				requirement_type=requirement_type
			))
			chunk_index += 1
		
		if guidance:
			content = f"Compliance Guidance:\n{guidance}"
			chunks.append(self._create_chunk(
				content=content,
				doctype="Compliance Requirement",
				docname=doc.name,
				section="guidance",
				chunk_index=chunk_index
			))
			chunk_index += 1
		
		if penalties:
			content = f"Non-Compliance Penalties:\n{penalties}"
			chunks.append(self._create_chunk(
				content=content,
				doctype="Compliance Requirement",
				docname=doc.name,
				section="penalties",
				chunk_index=chunk_index
			))
			chunk_index += 1
		
		return chunks
	
	def _chunk_generic(self, doc) -> list[DocumentChunk]:
		"""Generic chunker for unknown document types."""
		chunks = []
		
		# Try to get any text content
		content_fields = ["description", "content", "text", "notes", "details"]
		content = ""
		
		for field in content_fields:
			if doc.get(field):
				content += self._strip_html(doc.get(field)) + "\n"
		
		if not content.strip():
			return chunks
		
		# Split into chunks
		text_chunks = self._split_text(content)
		
		for i, chunk in enumerate(text_chunks):
			chunks.append(self._create_chunk(
				content=chunk,
				doctype=doc.doctype,
				docname=doc.name,
				section="content",
				chunk_index=i
			))
		
		return chunks
	
	def _split_text(self, text: str) -> list[str]:
		"""
		Split text into chunks of appropriate size.
		
		Uses paragraph/sentence boundaries when possible.
		"""
		if len(text) <= self.chunk_size:
			return [text]
		
		chunks = []
		
		# First try to split by paragraphs
		paragraphs = text.split("\n\n")
		current_chunk = ""
		
		for para in paragraphs:
			if len(current_chunk) + len(para) + 2 <= self.chunk_size:
				current_chunk += para + "\n\n"
			else:
				if current_chunk:
					chunks.append(current_chunk.strip())
				
				# If paragraph is too long, split by sentences
				if len(para) > self.chunk_size:
					sentences = re.split(r'(?<=[.!?])\s+', para)
					current_chunk = ""
					
					for sentence in sentences:
						if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
							current_chunk += sentence + " "
						else:
							if current_chunk:
								chunks.append(current_chunk.strip())
							
							# If sentence is still too long, just split by size
							if len(sentence) > self.chunk_size:
								for i in range(0, len(sentence), self.chunk_size - self.chunk_overlap):
									chunks.append(sentence[i:i + self.chunk_size])
								current_chunk = ""
							else:
								current_chunk = sentence + " "
				else:
					current_chunk = para + "\n\n"
		
		if current_chunk:
			chunks.append(current_chunk.strip())
		
		return chunks


def get_chunker() -> SemanticChunker:
	"""Get a configured chunker instance."""
	try:
		settings = frappe.get_single("Mkaguzi Chat Settings")
		chunk_size = settings.chunk_size or 512
		chunk_overlap = settings.chunk_overlap or 50
	except Exception:
		chunk_size = 512
		chunk_overlap = 50
	
	return SemanticChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
