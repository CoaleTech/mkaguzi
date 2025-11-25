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