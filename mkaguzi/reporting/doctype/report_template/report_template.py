# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, get_datetime

class ReportTemplate(Document):
	def autoname(self):
		if not self.template_id:
			# Generate template ID in format RT-YYYY-####
			current_year = getdate().year

			last_template = frappe.db.sql("""
				SELECT template_id FROM `tabReport Template`
				WHERE template_id LIKE 'RT-{}-%'
				ORDER BY CAST(SUBSTRING_INDEX(template_id, '-', -1) AS UNSIGNED) DESC
				LIMIT 1
			""".format(current_year), as_dict=True)

			if last_template:
				last_num = int(last_template[0].template_id.split('-')[-1])
				next_num = last_num + 1
			else:
				next_num = 1

			self.template_id = f"RT-{current_year}-{next_num:04d}"

	def validate(self):
		self.validate_default_template()
		self.validate_specialized_fields()

	def validate_default_template(self):
		"""Ensure only one default template per type"""
		if self.is_default:
			existing_default = frappe.db.exists("Report Template", {
				"template_type": self.template_type,
				"is_default": 1,
				"name": ["!=", self.name]
			})

			if existing_default:
				frappe.throw(_("A default template already exists for {0}. Please uncheck 'Is Default Template' for the existing template first.").format(self.template_type))

	def validate_specialized_fields(self):
		"""Validate specialized audit fields based on template type and category"""
		# Skip validation for basic templates - only validate when specialized fields are intentionally configured
		if not self.audit_category or self.audit_category not in ["Financial", "IT Security", "Compliance", "Fraud"]:
			return

		# Validate required fields for specialized categories only when relevant fields are set
		if self.audit_category == "Compliance" and self.compliance_standards and not self.documentation_standards:
			frappe.throw(_("Documentation Standards is required when Compliance Standards are specified"))

		if self.audit_category == "IT Security" and self.security_framework and not any([self.access_control_review, self.data_protection_measures, self.incident_response_plan]):
			frappe.throw(_("At least one security control must be enabled when Security Framework is specified"))

		if self.audit_category == "Financial" and self.financial_standards and not any([self.revenue_recognition, self.asset_valuation_methods, self.financial_ratios_analysis]):
			frappe.throw(_("At least one financial analysis component must be enabled when Financial Standards are specified"))

		if self.audit_category == "Fraud" and self.investigation_methodology and not self.evidence_collection:
			frappe.throw(_("Evidence Collection must be enabled when Investigation Methodology is specified"))

		# Validate regulatory framework selection
		if self.regulatory_framework and self.regulatory_framework != "Other":
			valid_frameworks = ["SOX", "COSO", "COBIT", "ISO 27001", "NIST", "GDPR", "HIPAA", "PCI DSS"]
			if self.regulatory_framework not in valid_frameworks:
				frappe.throw(_("Invalid regulatory framework selected"))
		"""Set audit trail fields"""
		if not self.created_by:
			self.created_by = frappe.session.user
		if not self.creation_date:
			self.creation_date = getdate()

		self.modified_by = frappe.session.user
		self.last_modified = get_datetime()

	def on_update(self):
		"""Handle template updates"""
		if self.has_value_changed("is_default") and self.is_default:
			# Clear default flag from other templates of same type
			frappe.db.sql("""
				UPDATE `tabReport Template`
				SET is_default = 0
				WHERE template_type = %s AND name != %s
			""", (self.template_type, self.name))

@frappe.whitelist()
def get_default_template(template_type):
	"""Get the default template for a given type"""
	template = frappe.get_all("Report Template",
		filters={
			"template_type": template_type,
			"is_default": 1,
			"is_active": 1
		},
		fields=["name", "template_name"]
	)

	if template:
		return template[0]
	else:
		# Return first active template if no default
		template = frappe.get_all("Report Template",
			filters={
				"template_type": template_type,
				"is_active": 1
			},
			fields=["name", "template_name"],
			limit=1
		)
		return template[0] if template else None

@frappe.whitelist()
def get_template_config(template_name):
	"""Get template configuration for report generation"""
	template = frappe.get_doc("Report Template", template_name)

	config = {
		"header": {
			"include_header": template.header_section,
			"logo": template.logo_attachment,
			"company_name": template.company_name,
			"title_format": template.report_title_format,
			"background_color": template.header_background_color,
			"text_color": template.header_text_color,
			"font_size": template.header_font_size
		},
		"body": {
			"font_family": template.font_family,
			"font_size": template.font_size,
			"line_height": template.line_height,
			"margins": template.page_margins,
			"orientation": template.page_orientation,
			"paper_size": template.paper_size
		},
		"content": {
			"executive_summary": template.include_executive_summary,
			"background": template.include_background,
			"scope": template.include_audit_scope,
			"objectives": template.include_audit_objectives,
			"findings_summary": template.include_findings_summary,
			"detailed_findings": template.include_detailed_findings,
			"recommendations": template.include_recommendations,
			"appendices": template.include_appendices
		},
		"styling": {
			"table_border": template.table_border_style,
			"table_header_bg": template.table_header_background,
			"alternate_rows": template.table_alternate_rows,
			"critical_highlight": template.highlight_critical_findings,
			"high_highlight": template.highlight_high_findings,
			"medium_highlight": template.highlight_medium_findings
		},
		"specialized": {
			"audit_category": template.audit_category,
			"industry_specific": template.industry_specific,
			"regulatory_framework": template.regulatory_framework,
			"risk_assessment_matrix": template.risk_assessment_matrix,
			"control_testing_methodology": template.control_testing_methodology,
			"sampling_method": template.sampling_method,
			"compliance": {
				"standards": template.compliance_standards,
				"certification_requirements": template.certification_requirements,
				"regulatory_deadlines": template.regulatory_deadlines,
				"evidence_requirements": template.audit_evidence_requirements,
				"documentation_standards": template.documentation_standards,
				"reporting_frequency": template.reporting_frequency
			},
			"it_security": {
				"framework": template.security_framework,
				"vulnerability_scanning": template.vulnerability_scanning,
				"penetration_testing": template.penetration_testing,
				"access_control_review": template.access_control_review,
				"data_protection_measures": template.data_protection_measures,
				"incident_response_plan": template.incident_response_plan
			},
			"financial": {
				"standards": template.financial_standards,
				"accounting_framework": template.accounting_framework,
				"revenue_recognition": template.revenue_recognition,
				"asset_valuation_methods": template.asset_valuation_methods,
				"liability_assessment": template.liability_assessment,
				"financial_ratios_analysis": template.financial_ratios_analysis
			},
			"operational": {
				"process_efficiency_metrics": template.process_efficiency_metrics,
				"control_effectiveness": template.control_effectiveness,
				"performance_indicators": template.performance_indicators,
				"benchmarking_criteria": template.benchmarking_criteria,
				"best_practice_comparison": template.best_practice_comparison,
				"improvement_recommendations": template.improvement_recommendations
			},
			"fraud": {
				"risk_indicators": template.fraud_risk_indicators,
				"investigation_methodology": template.investigation_methodology,
				"evidence_collection": template.evidence_collection,
				"whistleblower_protection": template.whistleblower_protection,
				"legal_compliance_review": template.legal_compliance_review,
				"recovery_recommendations": template.recovery_recommendations
			}
		},
		"footer": {
			"include_footer": template.footer_section,
			"text": template.footer_text,
			"page_numbering": template.page_numbering,
			"font_size": template.footer_font_size,
			"alignment": template.footer_alignment
		}
	}

	return config

@frappe.whitelist()
def create_default_templates():
	"""Create default report templates for each type"""
	template_types = [
		"Full Audit Report",
		"Executive Summary",
		"Management Report",
		"Board Report",
		"Compliance Report",
		"Risk Assessment Report",
		"IT Security Audit",
		"Financial Audit",
		"Operational Audit",
		"Compliance Monitoring",
		"Fraud Investigation",
		"Special Projects Audit",
		"Follow-up Audit",
		"Agreed-Upon Procedures",
		"Performance Audit"
	]

	for template_type in template_types:
		# Check if default template already exists
		existing = frappe.db.exists("Report Template", {
			"template_type": template_type,
			"is_default": 1
		})

		if not existing:
			template = frappe.new_doc("Report Template")
			template.template_name = f"Default {template_type}"
			template.template_type = template_type
			template.description = f"Default template for {template_type.lower()}"
			template.is_default = 1
			template.is_active = 1

			# Set type-specific defaults
			if template_type == "Executive Summary":
				template.include_detailed_findings = 0
				template.include_appendices = 0
				template.page_orientation = "Landscape"
			elif template_type == "Board Report":
				template.header_background_color = "#2E4057"
				template.header_text_color = "#FFFFFF"
				template.highlight_critical_findings = "#DC143C"
			elif template_type == "Compliance Report":
				template.template_name = "Default Compliance Report"
				template.include_executive_summary = 0
				template.include_background = 0
			elif template_type == "Risk Assessment Report":
				template.audit_category = "Risk Assessment"
				template.risk_assessment_matrix = 1
			elif template_type == "IT Security Audit":
				template.audit_category = "IT Security"
				template.security_framework = "ISO 27001"
				template.vulnerability_scanning = 1
				template.access_control_review = 1
				template.data_protection_measures = 1
			elif template_type == "Financial Audit":
				template.audit_category = "Financial"
				template.financial_standards = "GAAP"
				template.accounting_framework = "Accrual Basis"
				template.revenue_recognition = 1
				template.financial_ratios_analysis = 1
			elif template_type == "Operational Audit":
				template.audit_category = "Operational"
				template.process_efficiency_metrics = 1
				template.control_effectiveness = 1
				template.performance_indicators = 1
				template.improvement_recommendations = 1
			elif template_type == "Fraud Investigation":
				template.audit_category = "Fraud"
				template.fraud_risk_indicators = 1
				template.investigation_methodology = "Combined Approach"
				template.evidence_collection = 1
				template.legal_compliance_review = 1
			elif template_type == "Compliance Monitoring":
				template.audit_category = "Compliance"
				template.regulatory_framework = "SOX"
				template.certification_requirements = 1
				template.regulatory_deadlines = 1
				template.documentation_standards = "Detailed"

			template.save()
			frappe.msgprint(_("Created default template: {0}").format(template.template_name))

	return {"message": "Default templates created successfully"}