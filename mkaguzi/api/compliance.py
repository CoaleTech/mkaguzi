# API module for Internal Audit Management System

# =============================================================================
# COMPLIANCE MODULE APIs
# =============================================================================

import frappe
from frappe import _
from datetime import datetime, timedelta

@frappe.whitelist()
def create_compliance_check(check_data):
    """
    Create a new compliance check
    """
    try:
        data = frappe.parse_json(check_data) if isinstance(check_data, str) else check_data

        # Create compliance check document
        check = frappe.get_doc({
            'doctype': 'Compliance Check',
            'check_name': data.get('check_name'),
            'description': data.get('description'),
            'compliance_type': data.get('compliance_type'),
            'regulation_reference': data.get('regulation_reference'),
            'frequency': data.get('frequency'),
            'next_due_date': data.get('next_due_date'),
            'responsible_person': data.get('responsible_person'),
            'status': 'Scheduled',
            'created_by': frappe.session.user
        })

        # Add check criteria
        for criterion in data.get('check_criteria', []):
            check.append('check_criteria', {
                'criterion_name': criterion.get('criterion_name'),
                'description': criterion.get('description'),
                'expected_value': criterion.get('expected_value'),
                'mandatory': criterion.get('mandatory', True)
            })

        check.insert()
        frappe.db.commit()

        return {
            'success': True,
            'check_id': check.name,
            'message': 'Compliance check created successfully'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Compliance Check Creation Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def execute_compliance_check(check_id, execution_data):
    """
    Execute a compliance check
    """
    try:
        check = frappe.get_doc('Compliance Check', check_id)
        data = frappe.parse_json(execution_data) if isinstance(execution_data, str) else execution_data

        # Create execution record
        execution = frappe.get_doc({
            'doctype': 'Compliance Execution',
            'compliance_check': check_id,
            'execution_date': datetime.now(),
            'executed_by': frappe.session.user,
            'status': 'In Progress'
        })

        # Add execution results
        for result in data.get('results', []):
            execution.append('execution_results', {
                'criterion': result.get('criterion'),
                'actual_value': result.get('actual_value'),
                'compliance_status': result.get('compliance_status'),
                'notes': result.get('notes'),
                'evidence': result.get('evidence')
            })

        # Calculate overall compliance
        results = data.get('results', [])
        total_criteria = len(results)
        compliant_criteria = len([r for r in results if r.get('compliance_status') == 'Compliant'])

        execution.overall_compliance = (compliant_criteria / total_criteria * 100) if total_criteria > 0 else 0
        execution.compliant_criteria = compliant_criteria
        execution.total_criteria = total_criteria

        # Determine overall status
        if execution.overall_compliance == 100:
            execution.status = 'Passed'
        elif execution.overall_compliance >= 80:
            execution.status = 'Passed with Exceptions'
        else:
            execution.status = 'Failed'

        execution.insert()
        frappe.db.commit()

        # Update check next due date
        if execution.status in ['Passed', 'Passed with Exceptions']:
            check.last_execution_date = execution.execution_date
            check.status = 'Completed'
            # Calculate next due date based on frequency
            next_date = calculate_next_due_date(check.last_execution_date, check.frequency)
            check.next_due_date = next_date
            check.status = 'Scheduled'
        else:
            check.status = 'Overdue'

        check.save()

        return {
            'success': True,
            'execution_id': execution.name,
            'overall_compliance': execution.overall_compliance,
            'status': execution.status,
            'message': 'Compliance check executed successfully'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Compliance Check Execution Error"))
        frappe.throw(str(e))


def calculate_next_due_date(last_date, frequency):
    """
    Calculate next due date based on frequency
    """
    if frequency == 'Daily':
        return last_date + timedelta(days=1)
    elif frequency == 'Weekly':
        return last_date + timedelta(weeks=1)
    elif frequency == 'Monthly':
        # Add one month
        if last_date.month == 12:
            return last_date.replace(year=last_date.year + 1, month=1)
        else:
            return last_date.replace(month=last_date.month + 1)
    elif frequency == 'Quarterly':
        # Add three months
        month = last_date.month + 3
        year = last_date.year
        if month > 12:
            month -= 12
            year += 1
        return last_date.replace(year=year, month=month)
    elif frequency == 'Annually':
        return last_date.replace(year=last_date.year + 1)
    else:
        return last_date + timedelta(days=30)  # Default to monthly


@frappe.whitelist()
def get_compliance_dashboard():
    """
    Get compliance dashboard data
    """
    try:
        # Overall compliance statistics
        total_checks = frappe.db.count('Compliance Check')
        completed_checks = frappe.db.count('Compliance Check', filters={'status': 'Completed'})
        overdue_checks = frappe.db.count('Compliance Check', filters={'status': 'Overdue'})

        # Recent executions
        recent_executions = frappe.get_all('Compliance Execution',
            fields=['name', 'compliance_check', 'execution_date', 'overall_compliance', 'status'],
            order_by='execution_date desc',
            limit=10)

        # Compliance by type
        compliance_by_type = frappe.db.sql("""
            SELECT
                compliance_type,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
                AVG(
                    SELECT AVG(overall_compliance)
                    FROM `tabCompliance Execution`
                    WHERE compliance_check = cc.name
                    ORDER BY execution_date DESC
                    LIMIT 1
                ) as avg_compliance
            FROM `tabCompliance Check` cc
            GROUP BY compliance_type
        """, as_dict=True)

        # Upcoming due dates
        upcoming_checks = frappe.get_all('Compliance Check',
            filters={
                'next_due_date': ['<=', datetime.now() + timedelta(days=30)],
                'status': 'Scheduled'
            },
            fields=['name', 'check_name', 'next_due_date', 'compliance_type'],
            order_by='next_due_date',
            limit=10)

        # Compliance trends (last 12 months)
        trends = frappe.db.sql("""
            SELECT
                DATE_FORMAT(execution_date, '%Y-%m') as avg_compliance,
                AVG(overall_compliance) as avg_compliance,
                COUNT(*) as execution_count
            FROM `tabCompliance Execution`
            WHERE execution_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(execution_date, '%Y-%m')
            ORDER BY month
        """, as_dict=True)

        return {
            'summary': {
                'total_checks': total_checks,
                'completed_checks': completed_checks,
                'overdue_checks': overdue_checks,
                'completion_rate': (completed_checks / total_checks * 100) if total_checks > 0 else 0
            },
            'compliance_by_type': compliance_by_type,
            'recent_executions': recent_executions,
            'upcoming_checks': upcoming_checks,
            'trends': trends
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Compliance Dashboard Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_compliance_checks(filters=None, page=1, page_size=50):
    """
    Get compliance checks with filtering and pagination
    """
    try:
        filter_conditions = {}
        if filters:
            data = frappe.parse_json(filters) if isinstance(filters, str) else filters

            if data.get('status'):
                filter_conditions['status'] = data['status']
            if data.get('compliance_type'):
                filter_conditions['compliance_type'] = data['compliance_type']
            if data.get('responsible_person'):
                filter_conditions['responsible_person'] = data['responsible_person']

        # Calculate offset
        offset = (page - 1) * page_size

        # Get checks with last execution in single query (FIX N+1)
        checks = frappe.db.sql("""
            SELECT
                cc.name,
                cc.check_name,
                cc.description,
                cc.compliance_type,
                cc.frequency,
                cc.next_due_date,
                cc.status,
                cc.responsible_person,
                cc.last_execution_date,
                ce.overall_compliance as last_compliance_score,
                ce.status as last_execution_status
            FROM `tabCompliance Check` cc
            LEFT JOIN `tabCompliance Execution` ce
                ON cc.name = ce.compliance_check
                AND ce.execution_date = (
                    SELECT MAX(execution_date)
                    FROM `tabCompliance Execution`
                    WHERE compliance_check = cc.name
                )
            WHERE {where_clause}
            ORDER BY cc.next_due_date
            LIMIT %s
            OFFSET %s
        """.format(
            where_clause=" AND ".join([f"cc.{k} = %s" for k in filter_conditions]) if filter_conditions else "1=1"
        ), tuple(filter_conditions.values()) + (page_size, offset), as_dict=True)

        # Get total count
        total_count = frappe.db.count('Compliance Check', filters=filter_conditions)

        # Calculate days until due for each check
        for check in checks:
            if check['next_due_date']:
                try:
                    due_date = datetime.strptime(str(check['next_due_date']), '%Y-%m-%d').date()
                    today = datetime.now().date()
                    check['days_until_due'] = (due_date - today).days
                except (ValueError, TypeError):
                    check['days_until_due'] = None
            else:
                check['days_until_due'] = None

        return {
            'checks': checks,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Compliance Checks Retrieval Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_compliance_details(check_id):
    """
    Get detailed information about a compliance check
    """
    try:
        check = frappe.get_doc('Compliance Check', check_id)

        # Get execution history
        executions = frappe.get_all('Compliance Execution',
            filters={'compliance_check': check_id},
            fields=['name', 'execution_date', 'overall_compliance', 'status',
                   'executed_by', 'compliant_criteria', 'total_criteria'],
            order_by='execution_date desc')

        # Get detailed execution results
        execution_details = []
        for execution in executions:
            exec_doc = frappe.get_doc('Compliance Execution', execution.name)
            results = [r.as_dict() for r in exec_doc.execution_results]
            execution_details.append({
                'execution': execution,
                'results': results
            })

        # Calculate compliance trend
        compliance_scores = [e['overall_compliance'] for e in executions if e['overall_compliance']]
        trend = 'stable'
        if len(compliance_scores) >= 2:
            recent_avg = sum(compliance_scores[:3]) / min(3, len(compliance_scores))
            older_avg = sum(compliance_scores[3:]) / max(1, len(compliance_scores[3:]))
            if recent_avg > older_avg + 5:
                trend = 'improving'
            elif recent_avg < older_avg - 5:
                trend = 'declining'

        return {
            'check': check.as_dict(),
            'executions': executions,
            'execution_details': execution_details,
            'compliance_trend': trend,
            'average_compliance': sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Compliance Details Retrieval Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def create_regulatory_requirement(requirement_data):
    """
    Create a regulatory requirement
    """
    try:
        data = frappe.parse_json(requirement_data) if isinstance(requirement_data, str) else requirement_data

        requirement = frappe.get_doc({
            'doctype': 'Regulatory Requirement',
            'requirement_name': data.get('requirement_name'),
            'description': data.get('description'),
            'regulatory_body': data.get('regulatory_body'),
            'regulation_reference': data.get('regulation_reference'),
            'effective_date': data.get('effective_date'),
            'compliance_deadline': data.get('compliance_deadline'),
            'requirement_type': data.get('requirement_type'),
            'applicable_to': data.get('applicable_to'),
            'status': 'Active',
            'created_by': frappe.session.user
        })

        # Add requirement details
        for detail in data.get('requirement_details', []):
            requirement.append('requirement_details', {
                'detail_type': detail.get('detail_type'),
                'description': detail.get('description'),
                'mandatory': detail.get('mandatory', True)
            })

        requirement.insert()
        frappe.db.commit()

        return {
            'success': True,
            'requirement_id': requirement.name,
            'message': 'Regulatory requirement created successfully'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Regulatory Requirement Creation Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_regulatory_requirements(filters=None):
    """
    Get regulatory requirements
    """
    try:
        filter_conditions = {}
        if filters:
            data = frappe.parse_json(filters) if isinstance(filters, str) else filters

            if data.get('status'):
                filter_conditions['status'] = data['status']
            if data.get('regulatory_body'):
                filter_conditions['regulatory_body'] = data['regulatory_body']
            if data.get('requirement_type'):
                filter_conditions['requirement_type'] = data['requirement_type']

        requirements = frappe.get_all('Regulatory Requirement',
            filters=filter_conditions,
            fields=['name', 'requirement_name', 'description', 'regulatory_body',
                   'regulation_reference', 'effective_date', 'compliance_deadline',
                   'requirement_type', 'status'],
            order_by='compliance_deadline')

        # Add compliance status
        for req in requirements:
            if req['compliance_deadline']:
                deadline = datetime.strptime(str(req['compliance_deadline']), '%Y-%m-%d').date()
                today = datetime.now().date()
                if deadline < today:
                    req['compliance_status'] = 'Overdue'
                elif (deadline - today).days <= 30:
                    req['compliance_status'] = 'Due Soon'
                else:
                    req['compliance_status'] = 'On Track'
            else:
                req['compliance_status'] = 'Not Set'

        return {
            'requirements': requirements
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Regulatory Requirements Retrieval Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def generate_compliance_report(report_type='summary', filters=None):
    """
    Generate compliance report
    """
    try:
        # Get compliance data based on report type
        if report_type == 'summary':
            return generate_compliance_summary_report(filters)
        elif report_type == 'detailed':
            return generate_detailed_compliance_report(filters)
        elif report_type == 'trends':
            return generate_compliance_trends_report(filters)
        else:
            frappe.throw(_("Invalid report type"))

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Compliance Report Generation Error"))
        frappe.throw(str(e))


def generate_compliance_summary_report(filters=None):
    """
    Generate compliance summary report
    """
    filter_conditions = {}
    if filters:
        data = frappe.parse_json(filters) if isinstance(filters, str) else filters
        # Apply filters as needed

    # Overall statistics
    total_checks = frappe.db.count('Compliance Check')
    executed_checks = frappe.db.count('Compliance Execution')
    passed_checks = frappe.db.count('Compliance Execution', filters={'status': 'Passed'})
    failed_checks = frappe.db.count('Compliance Execution', filters={'status': 'Failed'})

    # Compliance by type
    compliance_by_type = frappe.db.sql("""
        SELECT
            cc.compliance_type,
            COUNT(DISTINCT cc.name) as total_checks,
            COUNT(DISTINCT ce.name) as executed_checks,
            AVG(ce.overall_compliance) as avg_compliance
        FROM `tabCompliance Check` cc
        LEFT JOIN `tabCompliance Execution` ce ON cc.name = ce.compliance_check
        GROUP BY cc.compliance_type
    """, as_dict=True)

    # Recent executions
    recent_executions = frappe.get_all('Compliance Execution',
        fields=['compliance_check', 'execution_date', 'overall_compliance', 'status'],
        order_by='execution_date desc',
        limit=20)

    report_data = {
        'report_type': 'Compliance Summary',
        'generated_date': datetime.now(),
        'summary': {
            'total_compliance_checks': total_checks,
            'executed_checks': executed_checks,
            'passed_checks': passed_checks,
            'failed_checks': failed_checks,
            'overall_pass_rate': (passed_checks / executed_checks * 100) if executed_checks > 0 else 0
        },
        'compliance_by_type': compliance_by_type,
        'recent_executions': recent_executions
    }

    return report_data


def generate_detailed_compliance_report(filters=None):
    """
    Generate detailed compliance report
    """
    # Get all compliance checks with their latest execution
    checks = frappe.db.sql("""
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

    report_data = {
        'report_type': 'Detailed Compliance Report',
        'generated_date': datetime.now(),
        'checks': checks
    }

    return report_data


def generate_compliance_trends_report(filters=None):
    """
    Generate compliance trends report
    """
    # Monthly compliance trends
    trends = frappe.db.sql("""
        SELECT
            DATE_FORMAT(execution_date, '%Y-%m') as month,
            COUNT(*) as execution_count,
            AVG(overall_compliance) as avg_compliance,
            MIN(overall_compliance) as min_compliance,
            MAX(overall_compliance) as max_compliance
        FROM `tabCompliance Execution`
        WHERE execution_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY DATE_FORMAT(execution_date, '%Y-%m')
        ORDER BY month
    """, as_dict=True)

    report_data = {
        'report_type': 'Compliance Trends Report',
        'generated_date': datetime.now(),
        'trends': trends
    }

    return report_data