# TEST LIBRARY MODULE APIs
# =============================================================================

import frappe
from frappe import _
from frappe.utils import now, get_datetime
import json


@frappe.whitelist()
def get_tests(filters=None, search=None):
    """Get all audit tests with optional filtering"""
    try:
        # Build the query
        conditions = []
        values = {}

        # Apply filters
        if filters:
            filters_dict = json.loads(filters) if isinstance(filters, str) else filters

            if filters_dict.get('category'):
                conditions.append("test_category = %(category)s")
                values['category'] = filters_dict['category']

            if filters_dict.get('test_type'):
                conditions.append("test_logic_type = %(test_type)s")
                values['test_type'] = filters_dict['test_type']

            if filters_dict.get('status'):
                conditions.append("status = %(status)s")
                values['status'] = filters_dict['status']

        # Apply search
        if search:
            search_condition = """
                (test_name LIKE %(search)s OR
                 description LIKE %(search)s OR
                 objective LIKE %(search)s OR
                 test_category LIKE %(search)s)
            """
            conditions.append(search_condition)
            values['search'] = f"%{search}%"

        # Build the final query
        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
            SELECT
                name,
                test_id,
                test_name,
                test_category,
                sub_category,
                description,
                objective,
                risk_area,
                data_source_type,
                test_logic_type,
                status,
                usage_count,
                success_rate,
                creation,
                modified,
                owner
            FROM `tabAudit Test Library`
            WHERE {where_clause}
            ORDER BY test_category, test_name
        """

        tests = frappe.db.sql(query, values, as_dict=True)

        # Get test parameters and expected results for each test
        for test in tests:
            # Get test parameters
            test_parameters = frappe.db.sql("""
                SELECT parameter_name, parameter_type, default_value, description
                FROM `tabTest Parameter`
                WHERE parent = %s
                ORDER BY idx
            """, test.name, as_dict=True)
            test['test_parameters'] = test_parameters

            # Get expected results
            expected_results = frappe.db.sql("""
                SELECT condition, expected_value, severity, description
                FROM `tabTest Expected Result`
                WHERE parent = %s
                ORDER BY idx
            """, test.name, as_dict=True)
            test['expected_results'] = expected_results

            # Get recent executions (last 3)
            recent_executions = frappe.db.sql("""
                SELECT actual_start_date as execution_date, status as result, created_by as executed_by
                FROM `tabTest Execution`
                WHERE test_library_reference = %s
                ORDER BY actual_start_date DESC
                LIMIT 3
            """, test.name, as_dict=True)
            test['recent_executions'] = recent_executions

        return tests

    except Exception as e:
        frappe.log_error(f"Error fetching tests: {str(e)}")
        frappe.throw(_("Failed to fetch audit tests"))


@frappe.whitelist()
def create_test(test_data):
    """Create a new audit test"""
    try:
        if isinstance(test_data, str):
            test_data = json.loads(test_data)

        # Create the test document
        test = frappe.get_doc({
            'doctype': 'Audit Test Library',
            'test_id': test_data.get('test_id') or frappe.generate_hash(length=8).upper(),
            'test_name': test_data.get('test_name'),
            'test_category': test_data.get('category'),
            'sub_category': test_data.get('sub_category'),
            'description': test_data.get('description'),
            'objective': test_data.get('objective'),
            'risk_area': test_data.get('risk_area'),
            'data_source_type': test_data.get('data_source_type', 'Database Table'),
            'test_logic_type': test_data.get('test_type', 'SQL Query'),
            'status': test_data.get('status', 'Active'),
            'is_template': 1
        })

        test.insert()
        frappe.db.commit()

        return {
            'name': test.name,
            'test_id': test.test_id,
            'test_name': test.test_name,
            'category': test.test_category,
            'test_type': test.test_logic_type,
            'description': test.description,
            'objective': test.objective,
            'status': test.status,
            'creation': test.creation,
            'modified': test.modified
        }

    except Exception as e:
        frappe.log_error(f"Error creating test: {str(e)}")
        frappe.throw(_("Failed to create audit test"))


@frappe.whitelist()
def update_test(test_id, test_data):
    """Update an existing audit test"""
    try:
        if isinstance(test_data, str):
            test_data = json.loads(test_data)

        # Get the test document
        test = frappe.get_doc('Audit Test Library', test_id)

        # Update fields
        field_mapping = {
            'test_name': 'test_name',
            'category': 'test_category',
            'test_type': 'test_logic_type',
            'description': 'description',
            'objective': 'objective',
            'status': 'status'
        }

        for field, value in test_data.items():
            if field in field_mapping:
                test.set(field_mapping[field], value)

        test.save()
        frappe.db.commit()

        return {
            'name': test.name,
            'test_id': test.test_id,
            'test_name': test.test_name,
            'category': test.test_category,
            'test_type': test.test_logic_type,
            'description': test.description,
            'objective': test.objective,
            'status': test.status,
            'creation': test.creation,
            'modified': test.modified
        }

    except Exception as e:
        frappe.log_error(f"Error updating test: {str(e)}")
        frappe.throw(_("Failed to update audit test"))


@frappe.whitelist()
def delete_test(test_id):
    """Delete an audit test"""
    try:
        frappe.delete_doc('Audit Test Library', test_id)
        frappe.db.commit()
        return {'success': True}

    except Exception as e:
        frappe.log_error(f"Error deleting test: {str(e)}")
        frappe.throw(_("Failed to delete audit test"))


@frappe.whitelist()
def execute_test(test_name, parameters=None):
    """Execute an audit test"""
    try:
        # Get the test
        test = frappe.get_doc('Audit Test Library', test_name)

        # Create execution record
        execution = frappe.get_doc({
            'doctype': 'Test Execution',
            'execution_id': f"EXEC-{frappe.generate_hash(length=8).upper()}",
            'test_library_reference': test_name,
            'execution_name': f"Execution of {test.test_name}",
            'execution_type': 'Manual',
            'status': 'Running',
            'actual_start_date': now()
        })

        execution.insert()
        frappe.db.commit()

        # Update test usage count
        test.usage_count = (test.usage_count or 0) + 1
        test.save()

        return {
            'execution_id': execution.name,
            'status': 'started',
            'message': 'Test execution started'
        }

    except Exception as e:
        frappe.log_error(f"Error executing test: {str(e)}")
        frappe.throw(_("Failed to execute audit test"))


@frappe.whitelist()
def get_test_details(test_id):
    """Get detailed information about a specific test"""
    try:
        test = frappe.get_doc('Audit Test Library', test_id)

        # Get test parameters
        test_parameters = frappe.db.sql("""
            SELECT parameter_name, parameter_type, default_value, description
            FROM `tabTest Parameter`
            WHERE parent = %s
            ORDER BY idx
        """, test_id, as_dict=True)

        # Get expected results
        expected_results = frappe.db.sql("""
            SELECT condition, expected_value, severity, description
            FROM `tabTest Expected Result`
            WHERE parent = %s
            ORDER BY idx
        """, test_id, as_dict=True)

        # Get execution history
        executions = frappe.db.sql("""
            SELECT actual_start_date as execution_date, status as result, created_by as executed_by
            FROM `tabTest Execution`
            WHERE test_library_reference = %s
            ORDER BY actual_start_date DESC
        """, test_id, as_dict=True)

        return {
            'name': test.name,
            'test_id': test.test_id,
            'test_name': test.test_name,
            'category': test.test_category,
            'test_type': test.test_logic_type,
            'description': test.description,
            'objective': test.objective,
            'data_source_type': test.data_source_type,
            'status': test.status,
            'usage_count': test.usage_count,
            'creation': test.creation,
            'modified': test.modified,
            'test_parameters': test_parameters,
            'expected_results': expected_results,
            'executions': executions
        }

    except Exception as e:
        frappe.log_error(f"Error fetching test details: {str(e)}")
        frappe.throw(_("Failed to fetch test details"))


@frappe.whitelist()
def get_test_history(test_name):
    """Get execution history for a test"""
    try:
        executions = frappe.db.sql("""
            SELECT
                name,
                execution_id,
                actual_start_date as execution_date,
                status as result,
                created_by as executed_by,
                notes
            FROM `tabTest Execution`
            WHERE test_library_reference = %s
            ORDER BY actual_start_date DESC
        """, test_name, as_dict=True)

        return executions

    except Exception as e:
        frappe.log_error(f"Error fetching test history: {str(e)}")
        frappe.throw(_("Failed to fetch test history"))


@frappe.whitelist()
def import_tests(file_data):
    """Import tests from file"""
    try:
        # This would handle file import logic
        # For now, return a placeholder response
        return {
            'success': True,
            'message': 'Import functionality not yet implemented',
            'imported_count': 0
        }

    except Exception as e:
        frappe.log_error(f"Error importing tests: {str(e)}")
        frappe.throw(_("Failed to import tests"))


@frappe.whitelist()
def export_tests(filters=None):
    """Export tests to file"""
    try:
        # Get tests based on filters
        tests = get_tests(filters)

        # Convert to export format
        export_data = []
        for test in tests:
            export_data.append({
                'test_id': test.get('test_id'),
                'test_name': test.get('test_name'),
                'category': test.get('test_category'),
                'test_type': test.get('test_logic_type'),
                'description': test.get('description'),
                'objective': test.get('objective'),
                'status': test.get('status')
            })

        return {
            'data': export_data,
            'count': len(export_data)
        }

    except Exception as e:
        frappe.log_error(f"Error exporting tests: {str(e)}")
        frappe.throw(_("Failed to export tests"))


@frappe.whitelist()
def get_test_categories():
    """
    Get all test categories for frontend filter

    Returns:
        list: List of unique test categories
    """
    try:
        categories = frappe.db.sql("""
            SELECT DISTINCT test_category
            FROM `tabAudit Test Library`
            WHERE test_category IS NOT NULL
            AND test_category != ''
            ORDER BY test_category
        """, as_dict=True)

        return [cat['test_category'] for cat in categories]

    except Exception as e:
        frappe.log_error(f"Error fetching test categories: {str(e)}")
        return []


@frappe.whitelist()
def get_test_statistics():
    """
    Get test statistics for dashboard analytics

    Returns:
        dict: Test statistics including totals, by status, by category, execution stats
    """
    try:
        # Total tests
        total_tests = frappe.db.count("Audit Test Library")

        # Tests by status
        status_stats = frappe.db.sql("""
            SELECT status, COUNT(*) as count
            FROM `tabAudit Test Library`
            GROUP BY status
        """, as_dict=True)

        # Tests by category
        category_stats = frappe.db.sql("""
            SELECT test_category, COUNT(*) as count
            FROM `tabAudit Test Library`
            WHERE test_category IS NOT NULL
            GROUP BY test_category
            ORDER BY count DESC
        """, as_dict=True)

        # Execution statistics
        execution_stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total_executions,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status = 'Running' THEN 1 ELSE 0 END) as running
            FROM `tabTest Execution`
        """, as_dict=True)[0]

        # Average success rate
        avg_success_rate = frappe.db.sql("""
            SELECT AVG(success_rate) as avg_rate
            FROM `tabAudit Test Library`
            WHERE success_rate IS NOT NULL
        """, as_dict=True)[0]['avg_rate'] or 0

        # Most used tests
        most_used = frappe.db.sql("""
            SELECT test_id, test_name, usage_count
            FROM `tabAudit Test Library`
            WHERE usage_count > 0
            ORDER BY usage_count DESC
            LIMIT 5
        """, as_dict=True)

        # Recent executions
        recent_executions = frappe.db.sql("""
            SELECT
                te.name,
                te.execution_id,
                te.test_library_reference,
                at.test_name,
                te.status,
                te.actual_start_date
            FROM `tabTest Execution` te
            LEFT JOIN `tabAudit Test Library` at ON te.test_library_reference = at.name
            ORDER BY te.actual_start_date DESC
            LIMIT 10
        """, as_dict=True)

        return {
            'total_tests': total_tests,
            'by_status': {s['status']: s['count'] for s in status_stats},
            'by_category': category_stats,
            'execution_stats': {
                'total': execution_stats['total_executions'] or 0,
                'completed': execution_stats['completed'] or 0,
                'failed': execution_stats['failed'] or 0,
                'running': execution_stats['running'] or 0,
                'success_rate': round(avg_success_rate, 2)
            },
            'most_used': most_used,
            'recent_executions': recent_executions
        }

    except Exception as e:
        frappe.log_error(f"Error fetching test statistics: {str(e)}")
        return {
            'total_tests': 0,
            'by_status': {},
            'by_category': [],
            'execution_stats': {
                'total': 0,
                'completed': 0,
                'failed': 0,
                'running': 0,
                'success_rate': 0
            },
            'most_used': [],
            'recent_executions': []
        }


@frappe.whitelist()
def bulk_test_operations(operation, test_ids, **kwargs):
    """
    Perform bulk operations on multiple tests

    Args:
        operation (str): Operation to perform (activate, deactivate, delete, export, clone)
        test_ids (list): List of test IDs to operate on
        **kwargs: Additional operation-specific parameters

    Returns:
        dict: Operation results
    """
    try:
        if isinstance(test_ids, str):
            test_ids = json.loads(test_ids)

        results = {
            'success': [],
            'failed': [],
            'operation': operation
        }

        for test_id in test_ids:
            try:
                if operation == 'activate':
                    test = frappe.get_doc('Audit Test Library', test_id)
                    test.status = 'Active'
                    test.save()
                    results['success'].append(test_id)

                elif operation == 'deactivate':
                    test = frappe.get_doc('Audit Test Library', test_id)
                    test.status = 'Inactive'
                    test.save()
                    results['success'].append(test_id)

                elif operation == 'delete':
                    frappe.delete_doc('Audit Test Library', test_id)
                    results['success'].append(test_id)

                elif operation == 'clone':
                    original = frappe.get_doc('Audit Test Library', test_id)
                    clone = frappe.copy_doc(original, ignore_no_copy=True)
                    clone.test_name = f"{original.test_name} (Copy)"
                    clone.test_id = frappe.generate_hash(length=8).upper()
                    clone.usage_count = 0
                    clone.insert()
                    results['success'].append({
                        'original': test_id,
                        'clone': clone.name,
                        'clone_id': clone.test_id
                    })

                elif operation == 'export':
                    test = frappe.get_doc('Audit Test Library', test_id)
                    results['success'].append({
                        'test_id': test.test_id,
                        'test_name': test.test_name,
                        'category': test.test_category,
                        'test_type': test.test_logic_type,
                        'description': test.description,
                        'objective': test.objective,
                        'status': test.status
                    })

                elif operation == 'archive':
                    test = frappe.get_doc('Audit Test Library', test_id)
                    test.status = 'Archived'
                    test.save()
                    results['success'].append(test_id)

                else:
                    results['failed'].append({
                        'test_id': test_id,
                        'reason': f"Unknown operation: {operation}"
                    })

            except Exception as e:
                results['failed'].append({
                    'test_id': test_id,
                    'reason': str(e)
                })

        results['total'] = len(test_ids)
        results['success_count'] = len(results['success'])
        results['failed_count'] = len(results['failed'])

        return results

    except Exception as e:
        frappe.log_error(f"Error in bulk test operations: {str(e)}")
        frappe.throw(_("Failed to perform bulk operations"))