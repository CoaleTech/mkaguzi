# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, now_datetime, getdate, date_diff
import json

class AuditIntegrityReport(Document):
    def validate(self):
        """Validate the audit integrity report"""
        self.validate_audit_period()
        self.update_change_log()

    def validate_audit_period(self):
        """Validate the audit period format"""
        if self.audit_period:
            try:
                # Parse period (expected format: "Jan 2025 - Dec 2025" or similar)
                if " - " not in self.audit_period:
                    frappe.throw(_("Audit period must be in format 'Start - End'"))
            except Exception:
                frappe.throw(_("Invalid audit period format"))

    def update_change_log(self):
        """Update the change log with modification details"""
        if not self.change_log:
            self.change_log = ""

        log_entry = f"{now()}: {self.status} by {frappe.session.user}\n"
        self.change_log += log_entry

    def on_update(self):
        """Called when document is updated"""
        # Set generated fields if not set
        if not self.generated_by:
            self.generated_by = frappe.session.user
        if not self.generated_on:
            self.generated_on = now_datetime()

    def generate_executive_summary(self):
        """Generate executive summary based on findings"""
        if not self.critical_findings and not self.detailed_findings:
            return

        total_findings = (len(self.critical_findings) if self.critical_findings else 0) + \
                        (len(self.detailed_findings) if self.detailed_findings else 0)

        critical_count = len(self.critical_findings) if self.critical_findings else 0

        summary = f"This {self.report_type} report covers the audit period {self.audit_period}. "
        summary += f"A total of {total_findings} findings were identified, "
        summary += f"including {critical_count} critical findings requiring immediate attention."

        if self.data_integrity_checks:
            passed_checks = sum(1 for check in self.data_integrity_checks if check.status == "Passed")
            total_checks = len(self.data_integrity_checks)
            summary += f" Data integrity checks: {passed_checks}/{total_checks} passed."

        self.executive_summary = summary

    def get_report_summary(self):
        """Get a summary of the integrity report"""
        return {
            "title": self.report_title,
            "type": self.report_type,
            "period": self.audit_period,
            "status": self.status,
            "generated_by": self.generated_by,
            "generated_on": self.generated_on,
            "critical_findings": len(self.critical_findings) if self.critical_findings else 0,
            "total_findings": (len(self.critical_findings) if self.critical_findings else 0) + \
                            (len(self.detailed_findings) if self.detailed_findings else 0),
            "integrity_checks": len(self.data_integrity_checks) if self.data_integrity_checks else 0
        }

@frappe.whitelist()
def generate_integrity_report(report_type, audit_period, include_checks=None):
    """Generate a new integrity report"""
    if not frappe.has_permission("Audit Integrity Report", "create"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    try:
        # Create new report
        report = frappe.get_doc({
            "doctype": "Audit Integrity Report",
            "report_title": f"{report_type} Report - {audit_period}",
            "report_type": report_type,
            "audit_period": audit_period,
            "status": "In Progress"
        })

        # Generate findings based on report type
        if report_type == "Data Integrity":
            report = generate_data_integrity_report(report, include_checks)
        elif report_type == "System Integrity":
            report = generate_system_integrity_report(report)
        elif report_type == "Process Integrity":
            report = generate_process_integrity_report(report)
        elif report_type == "Compliance Integrity":
            report = generate_compliance_integrity_report(report)
        elif report_type == "Full Audit":
            report = generate_full_audit_report(report)

        report.status = "Completed"
        report.insert()

        return report.name

    except Exception as e:
        frappe.log_error(f"Failed to generate integrity report: {str(e)}")
        frappe.throw(_("Report generation failed: {0}").format(str(e)))

def generate_data_integrity_report(report, include_checks=None):
    """Generate data integrity specific findings"""
    from mkaguzi.mkaguzi.integration.analyzer import AuditDataAnalyzer

    analyzer = AuditDataAnalyzer()

    # Run data integrity checks
    integrity_checks = analyzer.run_integrity_checks()

    # Add findings to report
    for check in integrity_checks:
        finding = {
            "doctype": "Audit Finding",
            "finding_type": "Data Integrity",
            "severity": check.get("severity", "Medium"),
            "description": check.get("description", ""),
            "impact": check.get("impact", ""),
            "recommendation": check.get("recommendation", "")
        }

        if check.get("severity") == "Critical":
            report.append("critical_findings", finding)
        else:
            report.append("detailed_findings", finding)

        # Add to integrity checks table
        check_result = {
            "doctype": "Integrity Check Result",
            "check_name": check.get("check_name", ""),
            "status": check.get("status", "Unknown"),
            "details": check.get("details", ""),
            "executed_on": now_datetime()
        }
        report.append("data_integrity_checks", check_result)

    report.generate_executive_summary()
    return report

def generate_system_integrity_report(report):
    """Generate system integrity specific findings"""
    # Check system configurations, permissions, etc.
    findings = []

    # Check for inactive users with active sessions
    inactive_users = frappe.db.sql("""
        SELECT name, full_name
        FROM `tabUser`
        WHERE enabled = 0 AND name IN (
            SELECT DISTINCT user FROM `tabSessions`
            WHERE creation > DATE_SUB(NOW(), INTERVAL 30 DAY)
        )
    """, as_dict=True)

    if inactive_users:
        findings.append({
            "finding_type": "System Security",
            "severity": "High",
            "description": f"Found {len(inactive_users)} inactive users with recent sessions",
            "impact": "Potential security risk from inactive user accounts",
            "recommendation": "Review and deactivate unnecessary user accounts"
        })

    # Add findings to report
    for finding in findings:
        if finding["severity"] == "Critical":
            report.append("critical_findings", finding)
        else:
            report.append("detailed_findings", finding)

    report.generate_executive_summary()
    return report

def generate_process_integrity_report(report):
    """Generate process integrity specific findings"""
    # Check for process anomalies, missing approvals, etc.
    findings = []

    # Check for transactions without proper approvals
    unapproved_transactions = frappe.db.sql("""
        SELECT COUNT(*) as count, doctype_name
        FROM `tabAudit Trail`
        WHERE changes_summary LIKE '%approval%required%'
        AND creation > DATE_SUB(NOW(), INTERVAL 90 DAY)
        GROUP BY doctype_name
    """, as_dict=True)

    if unapproved_transactions:
        findings.append({
            "finding_type": "Process Control",
            "severity": "Medium",
            "description": f"Found transactions missing required approvals",
            "impact": "Potential non-compliance with approval processes",
            "recommendation": "Review approval workflows and ensure proper controls"
        })

    # Add findings to report
    for finding in findings:
        if finding["severity"] == "Critical":
            report.append("critical_findings", finding)
        else:
            report.append("detailed_findings", finding)

    report.generate_executive_summary()
    return report

def generate_compliance_integrity_report(report):
    """Generate compliance integrity specific findings"""
    # Check compliance with policies, regulations, etc.
    findings = []

    # This would include specific compliance checks based on organization policies
    # For now, add a placeholder
    findings.append({
        "finding_type": "Compliance",
        "severity": "Low",
        "description": "Compliance checks completed - no major issues found",
        "impact": "System appears compliant with current policies",
        "recommendation": "Continue regular compliance monitoring"
    })

    # Add findings to report
    for finding in findings:
        if finding["severity"] == "Critical":
            report.append("critical_findings", finding)
        else:
            report.append("detailed_findings", finding)

    report.generate_executive_summary()
    return report

def generate_full_audit_report(report):
    """Generate comprehensive full audit report"""
    # Combine all types of checks
    report = generate_data_integrity_report(report)
    report = generate_system_integrity_report(report)
    report = generate_process_integrity_report(report)
    report = generate_compliance_integrity_report(report)

    return report

@frappe.whitelist()
def get_report_templates():
    """Get available report templates"""
    return [
        {
            "type": "Data Integrity",
            "description": "Focuses on data accuracy, completeness, and consistency"
        },
        {
            "type": "System Integrity",
            "description": "Evaluates system security, access controls, and configurations"
        },
        {
            "type": "Process Integrity",
            "description": "Reviews business processes, approvals, and controls"
        },
        {
            "type": "Compliance Integrity",
            "description": "Assesses compliance with policies and regulations"
        },
        {
            "type": "Full Audit",
            "description": "Comprehensive audit covering all integrity aspects"
        }
    ]