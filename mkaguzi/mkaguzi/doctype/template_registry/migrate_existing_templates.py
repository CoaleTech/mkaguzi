# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute():
	"""Migrate existing templates to new template system"""
	frappe.reload_doc("mkaguzi", "doctype", "template_registry")
	frappe.reload_doc("mkaguzi", "doctype", "template_version")

	migrate_existing_templates()
	create_default_templates()

def migrate_existing_templates():
	"""Migrate existing templates from various sources"""
	# This function would migrate templates from existing DocTypes or files
	# For now, we'll create some example migrations

	migrated_count = 0

	# Example: Migrate VAT report templates
	vat_templates = [
		{
			"template_name": "Standard VAT Report",
			"template_type": "Report",
			"category": "Compliance",
			"description": "Standard VAT compliance report template",
			"template_engine": "Jinja2",
			"template_content": """
# VAT Compliance Report

**Report Period:** {{ period }}
**Generated:** {{ now }}

## Summary
- Total VAT Collected: ${{ total_vat }}
- Total Transactions: {{ transaction_count }}
- Compliance Status: {{ compliance_status }}

## Details
{% for transaction in transactions %}
### Transaction {{ transaction.id }}
- Date: {{ transaction.date }}
- Amount: ${{ transaction.amount }}
- VAT: ${{ transaction.vat_amount }}
- Status: {{ transaction.status }}
{% endfor %}

## Compliance Notes
{{ compliance_notes }}
			""",
			"template_config": '{"variables": ["period", "total_vat", "transaction_count", "compliance_status", "transactions", "compliance_notes"]}'
		},
		{
			"template_name": "Audit Finding Report",
			"template_type": "Report",
			"category": "Audit Report",
			"description": "Template for documenting audit findings",
			"template_engine": "Jinja2",
			"template_content": """
# Audit Finding Report

**Finding ID:** {{ finding_id }}
**Date:** {{ finding_date }}
**Auditor:** {{ auditor_name }}

## Finding Details
**Title:** {{ finding_title }}
**Severity:** {{ severity }}
**Status:** {{ status }}

## Description
{{ finding_description }}

## Impact
{{ impact_description }}

## Recommendations
{{ recommendations }}

## Management Response
{{ management_response }}
			""",
			"template_config": '{"variables": ["finding_id", "finding_date", "auditor_name", "finding_title", "severity", "status", "finding_description", "impact_description", "recommendations", "management_response"]}'
		}
	]

	for template_data in vat_templates:
		if not frappe.db.exists("Template Registry", {"template_name": template_data["template_name"]}):
			template = frappe.new_doc("Template Registry")
			template.update(template_data)
			template.save()
			migrated_count += 1
			frappe.msgprint(_("Migrated template: {0}").format(template_data["template_name"]))

	return migrated_count

def create_default_templates():
	"""Create additional default templates for common use cases"""
	default_templates = [
		{
			"template_name": "Risk Assessment Matrix",
			"template_type": "Report",
			"category": "Risk Assessment",
			"description": "Matrix format for risk assessment documentation",
			"template_engine": "Jinja2",
			"template_content": """
# Risk Assessment Matrix

**Assessment Date:** {{ assessment_date }}
**Assessed By:** {{ assessor_name }}
**Department:** {{ department }}

## Executive Summary
{{ executive_summary }}

## Risk Matrix

| Risk | Probability | Impact | Risk Level | Mitigation |
|------|-------------|--------|------------|------------|
{% for risk in risks %}
| {{ risk.description }} | {{ risk.probability }} | {{ risk.impact }} | {{ risk.level }} | {{ risk.mitigation }} |
{% endfor %}

## Key Findings
{{ key_findings }}

## Recommendations
{{ recommendations }}
			""",
			"template_config": '{"variables": ["assessment_date", "assessor_name", "department", "executive_summary", "risks", "key_findings", "recommendations"]}'
		},
		{
			"template_name": "Compliance Checklist Template",
			"template_type": "Component",
			"category": "Compliance",
			"description": "Reusable compliance checklist component",
			"template_engine": "Vue",
			"template_content": """
<template>
  <div class="compliance-checklist">
    <h3>{{ title }}</h3>
    <div class="checklist-items">
      <div
        v-for="item in items"
        :key="item.id"
        class="checklist-item"
        :class="{ 'completed': item.completed }"
      >
        <input
          type="checkbox"
          v-model="item.completed"
          @change="updateProgress"
        />
        <span>{{ item.text }}</span>
        <span v-if="item.notes" class="notes">{{ item.notes }}</span>
      </div>
    </div>
    <div class="progress">
      Progress: {{ completedCount }}/{{ totalCount }} ({{ progressPercentage }}%)
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  title: String,
  items: Array
})

const emit = defineEmits(['progress-update'])

const completedCount = computed(() => {
  return props.items.filter(item => item.completed).length
})

const totalCount = computed(() => {
  return props.items.length
})

const progressPercentage = computed(() => {
  return totalCount.value > 0 ? Math.round((completedCount.value / totalCount.value) * 100) : 0
})

const updateProgress = () => {
  emit('progress-update', {
    completed: completedCount.value,
    total: totalCount.value,
    percentage: progressPercentage.value
  })
}

onMounted(() => {
  updateProgress()
})
</script>

<style scoped>
.compliance-checklist {
  max-width: 600px;
}

.checklist-item {
  display: flex;
  align-items: center;
  padding: 8px;
  margin: 4px 0;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
}

.checklist-item.completed {
  background-color: #f0fdf4;
  border-color: #bbf7d0;
}

.checklist-item input {
  margin-right: 12px;
}

.notes {
  margin-left: auto;
  font-size: 0.875rem;
  color: #6b7280;
}

.progress {
  margin-top: 16px;
  padding: 8px;
  background-color: #f9fafb;
  border-radius: 4px;
  text-align: center;
  font-weight: 500;
}
</style>
			""",
			"template_config": '{"props": ["title", "items"], "events": ["progress-update"]}'
		},
		{
			"template_name": "Email Notification Template",
			"template_type": "Email",
			"category": "Email Notification",
			"description": "Template for audit-related email notifications",
			"template_engine": "Jinja2",
			"template_content": """
Subject: {{ subject }}

Dear {{ recipient_name }},

{{ greeting }}

{{ message_body }}

{% if action_required %}
## Action Required
{{ action_details }}
{% endif %}

{% if attachments %}
## Attachments
{% for attachment in attachments %}
- {{ attachment.name }}
{% endfor %}
{% endif %}

Best regards,
{{ sender_name }}
{{ sender_position }}
{{ organization_name }}

---
This is an automated message from the Internal Audit System.
Please do not reply to this email.
			""",
			"template_config": '{"variables": ["subject", "recipient_name", "greeting", "message_body", "action_required", "action_details", "attachments", "sender_name", "sender_position", "organization_name"]}'
		}
	]

	created_count = 0
	for template_data in default_templates:
		if not frappe.db.exists("Template Registry", {"template_name": template_data["template_name"]}):
			template = frappe.new_doc("Template Registry")
			template.update(template_data)
			template.save()
			created_count += 1
			frappe.msgprint(_("Created default template: {0}").format(template_data["template_name"]))

	return created_count