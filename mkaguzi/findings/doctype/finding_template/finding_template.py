# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class FindingTemplate(Document):
	def validate(self):
		"""Validate template data"""
		if not self.condition_template and not self.criteria_template:
			frappe.throw(_("At least Condition or Criteria template must be provided"))

	def on_update(self):
		"""Update usage statistics"""
		pass  # Will be updated when template is used to create findings

@frappe.whitelist()
def apply_finding_template(template_name, finding_doc=None):
	"""Apply finding template to create or update an audit finding"""
	template = frappe.get_doc("Finding Template", template_name)

	if not finding_doc:
		# Create new finding from template
		finding = frappe.new_doc("Audit Finding")
	else:
		finding = frappe.get_doc("Audit Finding", finding_doc)

	# Apply template fields
	if template.condition_template:
		finding.condition = template.condition_template
	if template.criteria_template:
		finding.criteria = template.criteria_template
	if template.cause_template:
		finding.cause = template.cause_template
	if template.consequence_template:
		finding.consequence = template.consequence_template
	if template.recommendation_template:
		finding.recommendation = template.recommendation_template

	finding.finding_category = template.finding_category
	finding.risk_category = template.risk_category

	# Update usage count
	template.usage_count = (template.usage_count or 0) + 1
	template.last_used = frappe.utils.nowdate()
	template.save()

	return finding

@frappe.whitelist()
def get_template_suggestions(finding_category=None, risk_category=None):
	"""Get template suggestions based on finding characteristics"""
	filters = {"is_active": 1}

	if finding_category:
		filters["finding_category"] = finding_category
	if risk_category:
		filters["risk_category"] = risk_category

	templates = frappe.get_all("Finding Template",
		filters=filters,
		fields=["name", "template_name", "description", "usage_count"],
		order_by="usage_count desc, modified desc",
		limit=10
	)

	return templates

@frappe.whitelist()
def create_common_finding_templates():
	"""Create the four common finding templates identified by AuditBoard"""
	templates = [
		{
			"template_name": "Segregation of Duties Violation",
			"finding_category": "Control Deficiency",
			"risk_category": "Financial",
			"description": "Template for segregation of duties violations where one person has incompatible responsibilities",
			"condition_template": "A single individual is responsible for [describe incompatible tasks - e.g., initiating payments, approving payments, and reconciling bank statements]. This creates a lack of proper checks and balances.",
			"criteria_template": "Proper segregation of duties requires that key business processes be divided among multiple individuals to prevent any single person from having control over all aspects of a transaction. Incompatible duties should be separated, including: authorization, custody, and record-keeping.",
			"cause_template": "The segregation of duties violation exists because: [select root cause - e.g., insufficient staff to separate duties, lack of role documentation, inadequate review of internal controls, management override of controls].",
			"consequence_template": "This lack of segregation creates the following risks: unauthorized transactions, fraud, errors that may go undetected, inaccurate financial reporting, and potential regulatory non-compliance.",
			"recommendation_template": "Recommend implementing proper segregation of duties as follows: 1) Identify incompatible duties in the process, 2) Reassign responsibilities to different individuals, 3) Implement mandatory reviews and approvals, 4) Document roles and responsibilities, 5) Periodically review and update segregation matrix.",
			"evidence_types": "Organization charts, Job descriptions, Transaction logs, Access reviews",
			"verification_methods": "Review organizational structure, Interview staff, Test access rights"
		},
		{
			"template_name": "Lack of Detailed Policy and Procedures",
			"finding_category": "Control Deficiency",
			"risk_category": "Operational",
			"description": "Template for findings related to missing or inadequate policies and procedures",
			"condition_template": "[Department/Process] lacks detailed written policies and procedures. Current processes are based on informal practices and individual knowledge rather than documented standards.",
			"criteria_template": "Departmental operations should be governed by documented policies and procedures that: define responsibilities, establish clear processes, ensure consistency, facilitate training, and support business continuity.",
			"cause_template": "The lack of documentation is due to: [select cause - e.g., historical reliance on tribal knowledge, lack of time/resources, rapid organizational growth, assumption that procedures are well-known, absence of documentation standards].",
			"consequence_template": "Operating without documented policies creates risks: process inconsistency between shifts/individuals, knowledge loss when staff leave, training difficulties for new employees, inability to demonstrate controls to auditors/regulators, and operational inefficiencies.",
			"recommendation_template": "Recommend developing comprehensive policies and procedures: 1) Document current processes, 2) Establish standard operating procedures (SOPs), 3) Create process flows and decision matrices, 4) Implement version control and regular reviews, 5) Train staff on documented procedures, 6) Establish process owner responsibilities.",
			"evidence_types": "Policy documents, Procedure manuals, Process maps, Training records",
			"verification_methods": "Review documentation completeness, Interview staff on procedures, Test process consistency"
		},
		{
			"template_name": "Lack of Formal Approvals",
			"finding_category": "Control Deficiency",
			"risk_category": "Financial",
			"description": "Template for findings related to missing or inadequate formal approval processes",
			"condition_template": "Transactions in [process/area] are being processed without documented evidence of proper review and approval. [Describe specific examples - e.g., payments over $X, journal entries, contract awards].",
			"criteria_template": "All material transactions should be subject to independent review and approval before execution. Approvals must be: documented (electronic or physical signature), from authorized personnel, based on established authority limits, and evidenced in transaction records.",
			"cause_template": "The lack of formal approvals is due to: [select cause - e.g., absence of approval workflow systems, incomplete delegation of authority matrix, lack of management awareness, process circumvention for expediency, inadequate review of transaction logs].",
			"consequence_template": "Missing approvals create risks: unauthorized or inappropriate transactions, failure to detect errors, fraud opportunities, inability to hold individuals accountable, and weakened control environment.",
			"recommendation_template": "Recommend implementing formal approval controls: 1) Establish and document authority limits matrix, 2) Implement approval workflow in systems, 3) Require electronic or physical signatures, 4) Regularly review transaction approval logs, 5) Train staff on approval requirements, 6) Enforce consequences for bypassing controls.",
			"evidence_types": "Approval logs, Delegation of authority documents, Transaction records, Email approvals",
			"verification_methods": "Inspect approval records, Test transaction approval trails, Confirm authority limits"
		},
		{
			"template_name": "Absence of Supporting Documentation",
			"finding_category": "Error",
			"risk_category": "Compliance",
			"description": "Template for findings related to missing supporting documentation for transactions",
			"condition_template": "[Transaction type/area] lacks adequate supporting documentation. [Describe specific findings - e.g., payments without invoices, journal entries without backup, contracts without supporting calculations, inventory adjustments without reconciliation].",
			"criteria_template": "All transactions must be supported by complete and accurate documentation that: substantiates the business purpose, provides audit trail, demonstrates compliance with policies, enables independent verification, and meets regulatory requirements.",
			"cause_template": "The absence of documentation is due to: [select cause - e.g., lack of documentation requirements, incomplete vendor onboarding, inadequate training, poor filing systems, rush processing without proper review, acceptance of undocumented explanations].",
			"consequence_template": "Missing documentation creates risks: inability to verify transaction validity, difficulty responding to audits/inquiries, potential for unauthorized or fraudulent transactions, regulatory non-compliance, and financial statement misstatement.",
			"recommendation_template": "Recommend strengthening documentation controls: 1) Define minimum documentation requirements for each transaction type, 2) Implement system validation to require attachments, 3) Train staff on documentation standards, 4) Conduct pre- and post-transaction reviews, 5) Establish secure document retention systems, 6) Implement periodic compliance testing.",
			"evidence_types": "Transaction documents, Invoice copies, Contracts, Calculations, Approvals",
			"verification_methods": "Inspect sample transactions, Verify documentation completeness, Test controls"
		}
	]

	created_templates = []
	for template_data in templates:
		# Check if template already exists
		existing = frappe.db.exists("Finding Template", {"template_name": template_data["template_name"]})
		if existing:
			continue

		# Create new template
		template = frappe.get_doc({
			"doctype": "Finding Template",
			**template_data,
			"is_active": 1,
			"usage_count": 0
		})
		template.insert()
		created_templates.append(template.name)

	return created_templates