import frappe
from frappe import _
import json
from datetime import datetime, timedelta

@frappe.whitelist()
def create_audit_plan(plan_data):
    """
    Create a new audit plan
    """
    try:
        data = frappe.parse_json(plan_data) if isinstance(plan_data, str) else plan_data

        # Create audit plan document
        plan = frappe.get_doc({
            'doctype': 'Audit Plan',
            'plan_name': data.get('plan_name'),
            'description': data.get('description'),
            'audit_type': data.get('audit_type'),
            'start_date': data.get('start_date'),
            'end_date': data.get('end_date'),
            'audit_objective': data.get('audit_objective'),
            'scope': data.get('scope'),
            'risk_assessment': data.get('risk_assessment'),
            'created_by': frappe.session.user,
            'status': 'Draft'
        })

        # Add audit areas
        for area in data.get('audit_areas', []):
            plan.append('audit_areas', {
                'area_name': area.get('area_name'),
                'description': area.get('description'),
                'risk_rating': area.get('risk_rating'),
                'priority': area.get('priority')
            })

        # Add team members
        for member in data.get('team_members', []):
            plan.append('team_members', {
                'user': member.get('user'),
                'role': member.get('role'),
                'responsibilities': member.get('responsibilities')
            })

        # Add planned tests
        for test in data.get('planned_tests', []):
            plan.append('planned_tests', {
                'test_name': test.get('test_name'),
                'test_category': test.get('test_category'),
                'description': test.get('description'),
                'estimated_hours': test.get('estimated_hours'),
                'priority': test.get('priority')
            })

        plan.insert()
        frappe.db.commit()

        return {
            'success': True,
            'plan_id': plan.name,
            'message': 'Audit plan created successfully'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Audit Plan Creation Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def update_audit_plan(plan_id, updates):
    """
    Update an existing audit plan
    """
    try:
        plan = frappe.get_doc('Audit Plan', plan_id)
        data = frappe.parse_json(updates) if isinstance(updates, str) else updates

        # Update basic fields
        for field, value in data.items():
            if field not in ['audit_areas', 'team_members', 'planned_tests']:
                setattr(plan, field, value)

        # Update child tables if provided
        if 'audit_areas' in data:
            plan.set('audit_areas', [])
            for area in data['audit_areas']:
                plan.append('audit_areas', area)

        if 'team_members' in data:
            plan.set('team_members', [])
            for member in data['team_members']:
                plan.append('team_members', member)

        if 'planned_tests' in data:
            plan.set('planned_tests', [])
            for test in data['planned_tests']:
                plan.append('planned_tests', test)

        plan.save()
        frappe.db.commit()

        return {
            'success': True,
            'message': 'Audit plan updated successfully'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Audit Plan Update Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def start_audit_execution(plan_id):
    """
    Start audit execution for a plan
    """
    try:
        plan = frappe.get_doc('Audit Plan', plan_id)

        if plan.status != 'Approved':
            frappe.throw(_("Audit plan must be approved before execution can start"))

        # Create audit execution record
        execution = frappe.get_doc({
            'doctype': 'Audit Execution',
            'audit_plan': plan_id,
            'execution_start_date': datetime.now(),
            'status': 'In Progress',
            'executed_by': frappe.session.user
        })

        # Copy planned tests to execution
        for test in plan.planned_tests:
            execution.append('executed_tests', {
                'test_name': test.test_name,
                'test_category': test.test_category,
                'description': test.description,
                'planned_hours': test.estimated_hours,
                'status': 'Not Started'
            })

        # Copy team members
        for member in plan.team_members:
            execution.append('execution_team', {
                'user': member.user,
                'role': member.role,
                'responsibilities': member.responsibilities
            })

        execution.insert()
        frappe.db.commit()

        # Update plan status
        plan.status = 'In Execution'
        plan.save()

        return {
            'success': True,
            'execution_id': execution.name,
            'message': 'Audit execution started successfully'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Audit Execution Start Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def update_test_status(execution_id, test_id, status, notes=None, actual_hours=None):
    """
    Update the status of a specific test in audit execution
    """
    try:
        execution = frappe.get_doc('Audit Execution', execution_id)

        # Find the test
        test = None
        for t in execution.executed_tests:
            if t.name == test_id:
                test = t
                break

        if not test:
            frappe.throw(_("Test not found in execution"))

        # Update test status
        test.status = status
        if notes:
            test.notes = notes
        if actual_hours:
            test.actual_hours = actual_hours

        # Set completion date if completed
        if status == 'Completed':
            test.completion_date = datetime.now()

        execution.save()
        frappe.db.commit()

        # Check if all tests are completed
        all_completed = all(t.status == 'Completed' for t in execution.executed_tests)
        if all_completed:
            execution.status = 'Completed'
            execution.execution_end_date = datetime.now()
            execution.save()

        return {
            'success': True,
            'message': f'Test status updated to {status}'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Test Status Update Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def create_finding(execution_id, finding_data):
    """
    Create a new audit finding
    """
    try:
        data = frappe.parse_json(finding_data) if isinstance(finding_data, str) else finding_data

        # Create finding document
        finding = frappe.get_doc({
            'doctype': 'Audit Finding',
            'audit_execution': execution_id,
            'finding_title': data.get('finding_title'),
            'description': data.get('description'),
            'finding_type': data.get('finding_type'),
            'severity': data.get('severity'),
            'impact': data.get('impact'),
            'recommendation': data.get('recommendation'),
            'responsible_party': data.get('responsible_party'),
            'target_completion_date': data.get('target_completion_date'),
            'status': 'Open',
            'reported_by': frappe.session.user,
            'reported_date': datetime.now()
        })

        # Add supporting evidence
        for evidence in data.get('evidence', []):
            finding.append('supporting_evidence', {
                'evidence_type': evidence.get('evidence_type'),
                'description': evidence.get('description'),
                'document_reference': evidence.get('document_reference')
            })

        finding.insert()
        frappe.db.commit()

        return {
            'success': True,
            'finding_id': finding.name,
            'message': 'Finding created successfully'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Finding Creation Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def update_finding_status(finding_id, status, updates=None):
    """
    Update finding status and details
    """
    try:
        finding = frappe.get_doc('Audit Finding', finding_id)

        finding.status = status

        if updates:
            data = frappe.parse_json(updates) if isinstance(updates, str) else updates
            for field, value in data.items():
                setattr(finding, field, value)

        # Set completion date if resolved
        if status in ['Resolved', 'Closed']:
            finding.actual_completion_date = datetime.now()

        finding.save()
        frappe.db.commit()

        return {
            'success': True,
            'message': f'Finding status updated to {status}'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Finding Status Update Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_audit_progress(execution_id):
    """
    Get progress summary for audit execution
    """
    try:
        execution = frappe.get_doc('Audit Execution', execution_id)

        total_tests = len(execution.executed_tests)
        completed_tests = len([t for t in execution.executed_tests if t.status == 'Completed'])
        in_progress_tests = len([t for t in execution.executed_tests if t.status == 'In Progress'])

        # Calculate planned vs actual hours
        planned_hours = sum([t.planned_hours or 0 for t in execution.executed_tests])
        actual_hours = sum([t.actual_hours or 0 for t in execution.executed_tests])

        # Get findings count
        findings_count = frappe.db.count('Audit Finding',
            filters={'audit_execution': execution_id})

        # Get open findings
        open_findings = frappe.db.count('Audit Finding',
            filters={'audit_execution': execution_id, 'status': ['in', ['Open', 'In Progress']]})

        progress_percent = (completed_tests / total_tests * 100) if total_tests > 0 else 0

        return {
            'execution_id': execution_id,
            'status': execution.status,
            'progress_percent': round(progress_percent, 1),
            'total_tests': total_tests,
            'completed_tests': completed_tests,
            'in_progress_tests': in_progress_tests,
            'planned_hours': planned_hours,
            'actual_hours': actual_hours,
            'findings_count': findings_count,
            'open_findings': open_findings,
            'start_date': execution.execution_start_date,
            'end_date': execution.execution_end_date
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Audit Progress Retrieval Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def generate_audit_report(execution_id, report_type='summary'):
    """
    Generate audit report
    """
    try:
        execution = frappe.get_doc('Audit Execution', execution_id)
        plan = frappe.get_doc('Audit Plan', execution.audit_plan)

        # Get all findings
        findings = frappe.get_all('Audit Finding',
            filters={'audit_execution': execution_id},
            fields=['finding_title', 'description', 'finding_type', 'severity',
                   'impact', 'recommendation', 'status', 'reported_date'])

        # Get test results
        test_results = []
        for test in execution.executed_tests:
            test_results.append({
                'test_name': test.test_name,
                'status': test.status,
                'planned_hours': test.planned_hours,
                'actual_hours': test.actual_hours,
                'notes': test.notes
            })

        # Calculate summary statistics
        severity_counts = {}
        for finding in findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1

        status_counts = {}
        for finding in findings:
            status_counts[finding.status] = status_counts.get(finding.status, 0) + 1

        report_data = {
            'report_type': report_type,
            'audit_plan': {
                'name': plan.plan_name,
                'description': plan.description,
                'audit_type': plan.audit_type,
                'period': f"{plan.start_date} to {plan.end_date}"
            },
            'execution': {
                'start_date': execution.execution_start_date,
                'end_date': execution.execution_end_date,
                'status': execution.status
            },
            'summary': {
                'total_findings': len(findings),
                'severity_breakdown': severity_counts,
                'status_breakdown': status_counts,
                'tests_completed': len([t for t in test_results if t['status'] == 'Completed']),
                'total_tests': len(test_results)
            },
            'findings': findings,
            'test_results': test_results,
            'generated_date': datetime.now(),
            'generated_by': frappe.session.user
        }

        # Create report document
        report = frappe.get_doc({
            'doctype': 'Audit Report',
            'audit_execution': execution_id,
            'report_type': report_type,
            'report_data': frappe.as_json(report_data),
            'generated_date': datetime.now(),
            'generated_by': frappe.session.user
        })

        report.insert()
        frappe.db.commit()

        return {
            'success': True,
            'report_id': report.name,
            'report_data': report_data,
            'message': 'Audit report generated successfully'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Audit Report Generation Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_execution_timeline(execution_id):
    """
    Get timeline of audit execution activities
    """
    try:
        # Get execution document
        execution = frappe.get_doc('Audit Execution', execution_id)

        timeline = []

        # Add execution start
        timeline.append({
            'date': execution.execution_start_date,
            'event': 'Audit Execution Started',
            'type': 'execution',
            'user': execution.executed_by
        })

        # Add test completions
        for test in execution.executed_tests:
            if test.completion_date:
                timeline.append({
                    'date': test.completion_date,
                    'event': f"Test '{test.test_name}' completed",
                    'type': 'test',
                    'status': test.status
                })

        # Add findings
        findings = frappe.get_all('Audit Finding',
            filters={'audit_execution': execution_id},
            fields=['finding_title', 'reported_date', 'status', 'reported_by'],
            order_by='reported_date')

        for finding in findings:
            timeline.append({
                'date': finding.reported_date,
                'event': f"Finding reported: {finding.finding_title}",
                'type': 'finding',
                'status': finding.status,
                'user': finding.reported_by
            })

        # Add execution completion
        if execution.execution_end_date:
            timeline.append({
                'date': execution.execution_end_date,
                'event': 'Audit Execution Completed',
                'type': 'execution',
                'status': execution.status
            })

        # Sort by date
        timeline.sort(key=lambda x: x['date'])

        return {
            'execution_id': execution_id,
            'timeline': timeline
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Timeline Retrieval Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def assign_task(execution_id, task_data):
    """
    Assign a task to team member
    """
    try:
        data = frappe.parse_json(task_data) if isinstance(task_data, str) else task_data

        # Create task document
        task = frappe.get_doc({
            'doctype': 'Audit Task',
            'audit_execution': execution_id,
            'task_title': data.get('task_title'),
            'description': data.get('description'),
            'assigned_to': data.get('assigned_to'),
            'priority': data.get('priority', 'Medium'),
            'due_date': data.get('due_date'),
            'status': 'Open',
            'assigned_by': frappe.session.user,
            'assigned_date': datetime.now()
        })

        task.insert()
        frappe.db.commit()

        return {
            'success': True,
            'task_id': task.name,
            'message': 'Task assigned successfully'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Task Assignment Error"))
        frappe.throw(str(e))


@frappe.whitelist()
def update_task_status(task_id, status, notes=None):
    """
    Update task status
    """
    try:
        task = frappe.get_doc('Audit Task', task_id)

        task.status = status
        if notes:
            task.notes = notes

        if status == 'Completed':
            task.completion_date = datetime.now()

        task.save()
        frappe.db.commit()

        return {
            'success': True,
            'message': f'Task status updated to {status}'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Task Status Update Error"))
        frappe.throw(str(e))