import frappe
from frappe import _
import json
from datetime import datetime, timedelta

@frappe.whitelist()
def get_findings(filters=None, page=1, page_size=50):
    """
    Get audit findings with filtering and pagination
    """
    try:
        filter_conditions = {}
        if filters:
            data = frappe.parse_json(filters) if isinstance(filters, str) else filters

            if data.get('audit_execution'):
                filter_conditions['audit_execution'] = data['audit_execution']
            if data.get('status'):
                filter_conditions['status'] = data['status']
            if data.get('severity'):
                filter_conditions['severity'] = data['severity']
            if data.get('finding_type'):
                filter_conditions['finding_type'] = data['finding_type']
            if data.get('responsible_party'):
                filter_conditions['responsible_party'] = data['responsible_party']

        # Calculate offset
        offset = (page - 1) * page_size

        # Get findings
        findings = frappe.get_all('Audit Finding',
            filters=filter_conditions,
            fields=['name', 'finding_title', 'description', 'finding_type', 'severity',
                   'impact', 'status', 'responsible_party', 'target_completion_date',
                   'actual_completion_date', 'reported_date', 'reported_by'],
            order_by='reported_date desc',
            limit_page_length=page_size,
            limit_start=offset)

        # Get total count
        total_count = frappe.db.count('Audit Finding', filters=filter_conditions)

        # Add additional data
        for finding in findings:
            finding_doc = frappe.get_doc('Audit Finding', finding.name)

            # Add evidence count
            finding['evidence_count'] = len(finding_doc.supporting_evidence)

            # Add action items count
            finding['action_items_count'] = len(finding_doc.action_items)

            # Add days overdue
            if finding['target_completion_date'] and finding['status'] in ['Open', 'In Progress']:
                target_date = datetime.strptime(str(finding['target_completion_date']), '%Y-%m-%d').date()
                today = datetime.now().date()
                finding['days_overdue'] = (today - target_date).days if today > target_date else 0
            else:
                finding['days_overdue'] = 0

        return {
            'findings': findings,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Findings Retrieval Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_finding_details(finding_id):
    """
    Get detailed information about a specific finding
    """
    try:
        finding = frappe.get_doc('Audit Finding', finding_id)

        # Get related data
        evidence = [ev.as_dict() for ev in finding.supporting_evidence]
        action_items = [ai.as_dict() for ai in finding.action_items]

        # Get audit execution details
        execution = None
        if finding.audit_execution:
            execution = frappe.get_doc('Audit Execution', finding.audit_execution)
            execution_data = {
                'name': execution.name,
                'audit_plan': execution.audit_plan,
                'status': execution.status,
                'start_date': execution.execution_start_date,
                'end_date': execution.execution_end_date
            }
        else:
            execution_data = None

        # Get related findings (same audit execution)
        related_findings = []
        if finding.audit_execution:
            related = frappe.get_all('Audit Finding',
                filters={
                    'audit_execution': finding.audit_execution,
                    'name': ['!=', finding_id]
                },
                fields=['name', 'finding_title', 'severity', 'status'],
                limit=5)
            related_findings = related

        return {
            'finding': finding.as_dict(),
            'evidence': evidence,
            'action_items': action_items,
            'audit_execution': execution_data,
            'related_findings': related_findings
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Finding Details Retrieval Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def update_finding(finding_id, updates):
    """
    Update finding details
    """
    try:
        finding = frappe.get_doc('Audit Finding', finding_id)
        data = frappe.parse_json(updates) if isinstance(updates, str) else updates

        # Update basic fields
        for field, value in data.items():
            if field not in ['supporting_evidence', 'action_items']:
                setattr(finding, field, value)

        # Update child tables if provided
        if 'supporting_evidence' in data:
            finding.set('supporting_evidence', [])
            for evidence in data['supporting_evidence']:
                finding.append('supporting_evidence', evidence)

        if 'action_items' in data:
            finding.set('action_items', [])
            for action in data['action_items']:
                finding.append('action_items', action)

        finding.save()
        frappe.db.commit()

        return {
            'success': True,
            'message': 'Finding updated successfully'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Finding Update Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def add_evidence(finding_id, evidence_data):
    """
    Add supporting evidence to a finding
    """
    try:
        finding = frappe.get_doc('Audit Finding', finding_id)
        data = frappe.parse_json(evidence_data) if isinstance(evidence_data, str) else evidence_data

        finding.append('supporting_evidence', {
            'evidence_type': data.get('evidence_type'),
            'description': data.get('description'),
            'document_reference': data.get('document_reference'),
            'file_attachment': data.get('file_attachment'),
            'date_collected': data.get('date_collected', datetime.now())
        })

        finding.save()
        frappe.db.commit()

        return {
            'success': True,
            'message': 'Evidence added successfully'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Evidence Addition Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def add_action_item(finding_id, action_data):
    """
    Add action item to a finding
    """
    try:
        finding = frappe.get_doc('Audit Finding', finding_id)
        data = frappe.parse_json(action_data) if isinstance(action_data, str) else action_data

        finding.append('action_items', {
            'action_description': data.get('action_description'),
            'responsible_person': data.get('responsible_person'),
            'target_date': data.get('target_date'),
            'priority': data.get('priority', 'Medium'),
            'status': 'Open'
        })

        finding.save()
        frappe.db.commit()

        return {
            'success': True,
            'message': 'Action item added successfully'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Action Item Addition Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def update_action_item_status(finding_id, action_item_id, status, notes=None):
    """
    Update action item status
    """
    try:
        finding = frappe.get_doc('Audit Finding', finding_id)

        # Find the action item
        action_item = None
        for ai in finding.action_items:
            if ai.name == action_item_id:
                action_item = ai
                break

        if not action_item:
            frappe.throw(_("Action item not found"))

        action_item.status = status
        if notes:
            action_item.notes = notes

        if status == 'Completed':
            action_item.completion_date = datetime.now()

        finding.save()
        frappe.db.commit()

        return {
            'success': True,
            'message': f'Action item status updated to {status}'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Action Item Status Update Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_findings_summary(filters=None):
    """
    Get summary statistics for findings
    """
    try:
        filter_conditions = {}
        if filters:
            data = frappe.parse_json(filters) if isinstance(filters, str) else filters
            if data.get('audit_execution'):
                filter_conditions['audit_execution'] = data['audit_execution']

        # Status breakdown
        status_counts = frappe.db.get_all('Audit Finding',
            filters=filter_conditions,
            fields=['status', 'count(*) as count'],
            group_by='status')

        # Severity breakdown
        severity_counts = frappe.db.get_all('Audit Finding',
            filters=filter_conditions,
            fields=['severity', 'count(*) as count'],
            group_by='severity')

        # Type breakdown
        type_counts = frappe.db.get_all('Audit Finding',
            filters=filter_conditions,
            fields=['finding_type', 'count(*) as count'],
            group_by='finding_type')

        # Overdue findings
        overdue_count = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabAudit Finding`
            WHERE status IN ('Open', 'In Progress')
            AND target_completion_date < CURDATE()
            {conditions}
        """.format(conditions=" AND " + " AND ".join([f"{k} = '{v}'" for k, v in filter_conditions.items()]) if filter_conditions else ""))

        overdue_count = overdue_count[0][0] if overdue_count else 0

        # Recent findings (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_count = frappe.db.count('Audit Finding',
            filters=dict(filter_conditions, reported_date=['>=', thirty_days_ago]))

        # High severity findings
        high_severity_count = frappe.db.count('Audit Finding',
            filters=dict(filter_conditions, severity='High'))

        return {
            'total_findings': sum([s['count'] for s in status_counts]),
            'status_breakdown': {s['status']: s['count'] for s in status_counts},
            'severity_breakdown': {s['severity']: s['count'] for s in severity_counts},
            'type_breakdown': {s['finding_type']: s['count'] for s in type_counts},
            'overdue_findings': overdue_count,
            'recent_findings': recent_count,
            'high_severity_findings': high_severity_count
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Findings Summary Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def bulk_update_findings(finding_ids, updates):
    """
    Bulk update multiple findings
    """
    try:
        ids = frappe.parse_json(finding_ids) if isinstance(finding_ids, str) else finding_ids
        data = frappe.parse_json(updates) if isinstance(updates, str) else updates

        updated_count = 0
        for finding_id in ids:
            finding = frappe.get_doc('Audit Finding', finding_id)

            for field, value in data.items():
                setattr(finding, field, value)

            finding.save()
            updated_count += 1

        frappe.db.commit()

        return {
            'success': True,
            'message': f'Successfully updated {updated_count} findings'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Bulk Findings Update Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def export_findings(filters=None, export_format='csv'):
    """
    Export findings to CSV or Excel
    """
    try:
        filter_conditions = {}
        if filters:
            data = frappe.parse_json(filters) if isinstance(filters, str) else filters
            for key, value in data.items():
                filter_conditions[key] = value

        # Get findings data
        findings = frappe.get_all('Audit Finding',
            filters=filter_conditions,
            fields=['finding_title', 'description', 'finding_type', 'severity',
                   'impact', 'status', 'responsible_party', 'target_completion_date',
                   'actual_completion_date', 'reported_date', 'reported_by'],
            order_by='reported_date desc')

        if export_format == 'csv':
            # Convert to CSV format
            import csv
            import io

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=findings[0].keys() if findings else [])
            writer.writeheader()
            writer.writerows(findings)

            return {
                'success': True,
                'data': output.getvalue(),
                'filename': f'audit_findings_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }

        elif export_format == 'excel':
            # For Excel export, we'd need to use a library like openpyxl
            # This is a placeholder - actual implementation would require additional setup
            return {
                'success': False,
                'message': 'Excel export not yet implemented'
            }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Findings Export Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_finding_trends(period='month', months=12):
    """
    Get finding trends over time
    """
    try:
        # Generate date ranges
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months*30)

        # Query for findings by period
        if period == 'month':
            date_format = '%Y-%m'
            group_by = "DATE_FORMAT(reported_date, '%Y-%m')"
        elif period == 'quarter':
            date_format = '%Y-Q%q'
            group_by = "CONCAT(YEAR(reported_date), '-Q', QUARTER(reported_date))"
        else:  # week
            date_format = '%Y-%U'
            group_by = "DATE_FORMAT(reported_date, '%Y-%U')"

        trends = frappe.db.sql(f"""
            SELECT
                {group_by} as period,
                COUNT(*) as total_findings,
                SUM(CASE WHEN severity = 'High' THEN 1 ELSE 0 END) as high_severity,
                SUM(CASE WHEN severity = 'Medium' THEN 1 ELSE 0 END) as medium_severity,
                SUM(CASE WHEN severity = 'Low' THEN 1 ELSE 0 END) as low_severity,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_findings,
                SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved_findings
            FROM `tabAudit Finding`
            WHERE reported_date BETWEEN '{start_date.date()}' AND '{end_date.date()}'
            GROUP BY {group_by}
            ORDER BY period
        """, as_dict=True)

        return {
            'trends': trends,
            'period': period,
            'start_date': start_date.date(),
            'end_date': end_date.date()
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Finding Trends Error"))
        frappe.throw(str(e))