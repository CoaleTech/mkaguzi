# =============================================================================
# REPORTING MODULE APIs
# =============================================================================

import frappe
from frappe import _
import json
from datetime import datetime, timedelta
import pandas as pd

@frappe.whitelist()
def generate_audit_report(report_type, filters=None):
    """
    Generate various audit reports
    """
    try:
        if report_type == 'executive_summary':
            return generate_executive_summary_report(filters)
        elif report_type == 'detailed_findings':
            return generate_detailed_findings_report(filters)
        elif report_type == 'compliance_status':
            return generate_compliance_status_report(filters)
        elif report_type == 'risk_assessment':
            return generate_risk_assessment_report(filters)
        elif report_type == 'trend_analysis':
            return generate_trend_analysis_report(filters)
        else:
            frappe.throw(_("Invalid report type"))

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Report Generation Error"))
        frappe.throw(str(e))


def generate_executive_summary_report(filters=None):
    """
    Generate executive summary report
    """
    try:
        filter_conditions = {}
        if filters:
            data = frappe.parse_json(filters) if isinstance(filters, str) else filters
            if data.get('audit_execution'):
                filter_conditions['audit_execution'] = data['audit_execution']

        # Get audit execution details
        executions = frappe.get_all('Audit Execution',
            filters=filter_conditions,
            fields=['name', 'audit_plan', 'execution_start_date', 'execution_end_date', 'status'])

        if not executions:
            frappe.throw(_("No audit executions found for the specified filters"))

        execution = executions[0]  # Assuming one execution for now

        # Get findings summary
        findings_summary = frappe.db.sql("""
            SELECT
                COUNT(*) as total_findings,
                SUM(CASE WHEN severity = 'High' THEN 1 ELSE 0 END) as high_severity,
                SUM(CASE WHEN severity = 'Medium' THEN 1 ELSE 0 END) as medium_severity,
                SUM(CASE WHEN severity = 'Low' THEN 1 ELSE 0 END) as low_severity,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_findings,
                SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved_findings
            FROM `tabAudit Finding`
            WHERE audit_execution = %s
        """, (execution.name,), as_dict=True)[0]

        # Get compliance summary
        compliance_summary = frappe.db.sql("""
            SELECT
                AVG(overall_compliance) as overall_compliance,
                COUNT(*) as total_checks
            FROM `tabCompliance Execution`
            WHERE DATE(execution_date) BETWEEN %s AND %s
        """, (execution.execution_start_date, execution.execution_end_date or datetime.now()), as_dict=True)[0]

        # Calculate key metrics
        resolution_rate = (findings_summary.resolved_findings / findings_summary.total_findings * 100) if findings_summary.total_findings > 0 else 0

        report_data = {
            'report_type': 'Executive Summary',
            'generated_date': datetime.now(),
            'audit_period': {
                'start_date': execution.execution_start_date,
                'end_date': execution.execution_end_date
            },
            'key_metrics': {
                'total_findings': findings_summary.total_findings,
                'high_severity_findings': findings_summary.high_severity,
                'medium_severity_findings': findings_summary.medium_severity,
                'low_severity_findings': findings_summary.low_severity,
                'open_findings': findings_summary.open_findings,
                'resolved_findings': findings_summary.resolved_findings,
                'finding_resolution_rate': round(resolution_rate, 1),
                'average_compliance_score': round(compliance_summary.overall_compliance or 0, 1),
            },
            'findings_breakdown': {
                'high': findings_summary.high_severity,
                'medium': findings_summary.medium_severity,
                'low': findings_summary.low_severity
            },
            'status_summary': {
                'open_findings': findings_summary.open_findings,
                'resolved_findings': findings_summary.resolved_findings
            }
        }

        return report_data

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Executive Summary Report Error"))
        raise


def generate_detailed_findings_report(filters=None):
    """
    Generate detailed findings report
    """
    try:
        filter_conditions = {}
        if filters:
            data = frappe.parse_json(filters) if isinstance(filters, str) else filters
            for key, value in data.items():
                filter_conditions[key] = value

        # Get all findings with details
        findings = frappe.get_all('Audit Finding',
            filters=filter_conditions,
            fields=['name', 'finding_title', 'description', 'finding_type', 'severity',
                   'impact', 'recommendation', 'status', 'responsible_party',
                   'target_completion_date', 'actual_completion_date', 'reported_date'],
            order_by='severity desc, reported_date desc')

        # Add additional details for each finding
        for finding in findings:
            finding_doc = frappe.get_doc('Audit Finding', finding.name)

            # Add evidence count
            finding['evidence_count'] = len(finding_doc.supporting_evidence)

            # Add action items
            finding['action_items'] = [ai.as_dict() for ai in finding_doc.action_items]

            # Calculate days overdue
            if finding['target_completion_date'] and finding['status'] in ['Open', 'In Progress']:
                target_date = datetime.strptime(str(finding['target_completion_date']), '%Y-%m-%d').date()
                today = datetime.now().date()
                finding['days_overdue'] = (today - target_date).days if today > target_date else 0
            else:
                finding['days_overdue'] = 0

        # Summary statistics
        summary = {
            'total_findings': len(findings),
            'severity_breakdown': {
                'High': len([f for f in findings if f['severity'] == 'High']),
                'Medium': len([f for f in findings if f['severity'] == 'Medium']),
                'Low': len([f for f in findings if f['severity'] == 'Low'])
            },
            'status_breakdown': {
                'Open': len([f for f in findings if f['status'] == 'Open']),
                'In Progress': len([f for f in findings if f['status'] == 'In Progress']),
                'Resolved': len([f for f in findings if f['status'] == 'Resolved']),
                'Closed': len([f for f in findings if f['status'] == 'Closed'])
            },
            'overdue_findings': len([f for f in findings if f['days_overdue'] > 0])
        }

        report_data = {
            'report_type': 'Detailed Findings Report',
            'generated_date': datetime.now(),
            'summary': summary,
            'findings': findings
        }

        return report_data

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Detailed Findings Report Error"))
        raise


def generate_compliance_status_report(filters=None):
    """
    Generate compliance status report
    """
    try:
        # Get compliance checks and their latest execution
        compliance_data = frappe.db.sql("""
            SELECT
                cc.name,
                cc.check_name,
                cc.compliance_type,
                cc.frequency,
                cc.responsible_person,
                cc.next_due_date,
                le.execution_date as last_execution_date,
                le.overall_compliance as last_compliance_score,
                le.status as last_execution_status
            FROM `tabCompliance Check` cc
            LEFT JOIN `tabCompliance Execution` le ON cc.name = le.compliance_check
            AND le.execution_date = (
                SELECT MAX(execution_date)
                FROM `tabCompliance Execution`
                WHERE compliance_check = cc.name
            )
            ORDER BY cc.next_due_date
        """, as_dict=True)

        # Calculate summary statistics
        total_checks = len(compliance_data)
        executed_checks = len([c for c in compliance_data if c['last_execution_date']])
        passed_checks = len([c for c in compliance_data if c['last_execution_status'] == 'Passed'])
        failed_checks = len([c for c in compliance_data if c['last_execution_status'] == 'Failed'])

        overdue_checks = 0
        due_soon_checks = 0
        for check in compliance_data:
            if check['next_due_date']:
                due_date = datetime.strptime(str(check['next_due_date']), '%Y-%m-%d').date()
                today = datetime.now().date()
                days_until_due = (due_date - today).days
                if days_until_due < 0:
                    overdue_checks += 1
                elif days_until_due <= 30:
                    due_soon_checks += 1

        # Compliance by type
        type_summary = {}
        for check in compliance_data:
            ctype = check['compliance_type']
            if ctype not in type_summary:
                type_summary[ctype] = {
                    'total': 0,
                    'executed': 0,
                    'passed': 0,
                    'avg_compliance': 0,
                    'scores': []
                }
            type_summary[ctype]['total'] += 1
            if check['last_execution_date']:
                type_summary[ctype]['executed'] += 1
                if check['last_execution_status'] == 'Passed':
                    type_summary[ctype]['passed'] += 1
                if check['last_compliance_score']:
                    type_summary[ctype]['scores'].append(check['last_compliance_score'])

        # Calculate averages
        for ctype, data in type_summary.items():
            if data['scores']:
                data['avg_compliance'] = sum(data['scores']) / len(data['scores'])
            del data['scores']  # Remove scores array from output

        report_data = {
            'report_type': 'Compliance Status Report',
            'generated_date': datetime.now(),
            'summary': {
                'total_checks': total_checks,
                'executed_checks': executed_checks,
                'passed_checks': passed_checks,
                'failed_checks': failed_checks,
                'overdue_checks': overdue_checks,
                'due_soon_checks': due_soon_checks,
                'execution_rate': (executed_checks / total_checks * 100) if total_checks > 0 else 0,
                'pass_rate': (passed_checks / executed_checks * 100) if executed_checks > 0 else 0
            },
            'compliance_by_type': type_summary,
            'checks': compliance_data
        }

        return report_data

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Compliance Status Report Error"))
        raise


def generate_risk_assessment_report(filters=None):
    """
    Generate risk assessment report
    """
    try:
        # Get all findings and assess risk levels
        findings = frappe.get_all('Audit Finding',
            fields=['finding_title', 'severity', 'impact', 'status', 'finding_type'],
            order_by='severity desc')

        # Risk matrix calculation
        risk_levels = {
            'Critical': 0,
            'High': 0,
            'Medium': 0,
            'Low': 0
        }

        for finding in findings:
            # Simple risk calculation based on severity and impact
            severity_score = {'High': 3, 'Medium': 2, 'Low': 1}.get(finding.severity, 1)
            impact_score = {'High': 3, 'Medium': 2, 'Low': 1}.get(finding.impact, 1)
            risk_score = severity_score * impact_score

            if risk_score >= 9:
                risk_levels['Critical'] += 1
            elif risk_score >= 6:
                risk_levels['High'] += 1
            elif risk_score >= 3:
                risk_levels['Medium'] += 1
            else:
                risk_levels['Low'] += 1

        # Risk by category
        risk_by_category = {}
        for finding in findings:
            category = finding.finding_type
            if category not in risk_by_category:
                risk_by_category[category] = {'High': 0, 'Medium': 0, 'Low': 0}

            risk_by_category[category][finding.severity] += 1

        # Top risks
        top_risks = sorted(findings, key=lambda x: (
            {'High': 3, 'Medium': 2, 'Low': 1}.get(x.severity, 1) *
            {'High': 3, 'Medium': 2, 'Low': 1}.get(x.impact, 1)
        ), reverse=True)[:10]

        report_data = {
            'report_type': 'Risk Assessment Report',
            'generated_date': datetime.now(),
            'risk_summary': risk_levels,
            'risk_by_category': risk_by_category,
            'top_risks': top_risks,
            'total_findings': len(findings)
        }

        return report_data

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Risk Assessment Report Error"))
        raise


def generate_trend_analysis_report(filters=None):
    """
    Generate trend analysis report
    """
    try:
        # Findings trends over time
        findings_trends = frappe.db.sql("""
            SELECT
                DATE_FORMAT(reported_date, '%Y-%m') as month,
                COUNT(*) as total_findings,
                SUM(CASE WHEN severity = 'High' THEN 1 ELSE 0 END) as high_severity,
                SUM(CASE WHEN severity = 'Medium' THEN 1 ELSE 0 END) as medium_severity,
                SUM(CASE WHEN severity = 'Low' THEN 1 ELSE 0 END) as low_severity
            FROM `tabAudit Finding`
            WHERE reported_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(reported_date, '%Y-%m')
            ORDER BY month
        """, as_dict=True)

        # Compliance trends
        compliance_trends = frappe.db.sql("""
            SELECT
                DATE_FORMAT(execution_date, '%Y-%m') as month,
                AVG(overall_compliance) as avg_compliance,
                COUNT(*) as execution_count
            FROM `tabCompliance Execution`
            WHERE execution_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(execution_date, '%Y-%m')
            ORDER BY month
        """, as_dict=True)

        report_data = {
            'report_type': 'Trend Analysis Report',
            'generated_date': datetime.now(),
            'findings_trends': findings_trends,
            'compliance_trends': compliance_trends
        }

        return report_data

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Trend Analysis Report Error"))
        raise


@frappe.whitelist()
def export_report(report_type, format='pdf', filters=None):
    """
    Export report in specified format
    """
    try:
        # Generate the report data
        report_data = generate_audit_report(report_type, filters)

        # For now, return JSON data - in a real implementation,
        # this would generate PDF/Excel files
        if format == 'json':
            return report_data
        elif format == 'pdf':
            # Placeholder for PDF generation
            return {
                'success': False,
                'message': 'PDF export not yet implemented',
                'data': report_data
            }
        elif format == 'excel':
            # Placeholder for Excel generation
            return {
                'success': False,
                'message': 'Excel export not yet implemented',
                'data': report_data
            }
        else:
            frappe.throw(_("Unsupported export format"))

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Report Export Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def schedule_report(report_config):
    """
    Schedule automated report generation
    """
    try:
        data = frappe.parse_json(report_config) if isinstance(report_config, str) else report_config

        schedule = frappe.get_doc({
            'doctype': 'Report Schedule',
            'report_type': data.get('report_type'),
            'schedule_name': data.get('schedule_name'),
            'frequency': data.get('frequency'),
            'next_run_date': data.get('next_run_date'),
            'recipients': data.get('recipients'),
            'filters': frappe.as_json(data.get('filters', {})),
            'status': 'Active',
            'created_by': frappe.session.user
        })

        schedule.insert()
        frappe.db.commit()

        return {
            'success': True,
            'schedule_id': schedule.name,
            'message': 'Report schedule created successfully'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Report Scheduling Error"))
        frappe.throw(str(e))