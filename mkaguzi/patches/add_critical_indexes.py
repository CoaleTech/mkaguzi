"""Add critical database indexes for performance

This patch adds indexes to frequently queried fields to improve
query performance across the mkaguzi audit system.
"""

import frappe
from frappe.database.schema import DBIndex


def execute():
    """Add indexes to frequently queried fields"""
    frappe.logger().info("Starting critical indexes installation")

    # Audit Trail Entry indexes
    if frappe.db.table_exists('Audit Trail Entry'):
        _add_index_if_not_exists('Audit Trail Entry',
            ['document_type', 'document_name'],
            'idx_audit_trail_doc')

        _add_index_if_not_exists('Audit Trail Entry',
            ['timestamp'],
            'idx_audit_trail_timestamp')

        _add_index_if_not_exists('Audit Trail Entry',
            ['operation', 'timestamp'],
            'idx_audit_trail_operation_time')

        _add_index_if_not_exists('Audit Trail Entry',
            ['user', 'timestamp'],
            'idx_audit_trail_user_time')

        _add_index_if_not_exists('Audit Trail Entry',
            ['module', 'timestamp'],
            'idx_audit_trail_module_time')

    # Audit Finding indexes
    if frappe.db.table_exists('Audit Finding'):
        _add_index_if_not_exists('Audit Finding',
            ['status'],
            'idx_audit_finding_status')

        _add_index_if_not_exists('Audit Finding',
            ['severity', 'status'],
            'idx_audit_finding_severity_status')

        _add_index_if_not_exists('Audit Finding',
            ['target_completion_date'],
            'idx_audit_finding_target_date')

        _add_index_if_not_exists('Audit Finding',
            ['responsible_party', 'status'],
            'idx_audit_finding_responsible_status')

        _add_index_if_not_exists('Audit Finding',
            ['reported_date'],
            'idx_audit_finding_reported_date')

    # Audit Execution indexes
    if frappe.db.table_exists('Audit Execution'):
        _add_index_if_not_exists('Audit Execution',
            ['status', 'creation'],
            'idx_audit_execution_status_creation')

        _add_index_if_not_exists('Audit Execution',
            ['audit_engagement'],
            'idx_audit_execution_engagement')

    # Audit GL Entry indexes
    if frappe.db.table_exists('Audit GL Entry'):
        _add_index_if_not_exists('Audit GL Entry',
            ['posting_date'],
            'idx_audit_gl_posting_date')

        _add_index_if_not_exists('Audit GL Entry',
            ['account_no', 'posting_date'],
            'idx_audit_gl_account_date')

        _add_index_if_not_exists('Audit GL Entry',
            ['creation'],
            'idx_audit_gl_creation')

    # Compliance Check indexes
    if frappe.db.table_exists('Compliance Check'):
        _add_index_if_not_exists('Compliance Check',
            ['status', 'compliance_type'],
            'idx_compliance_check_status_type')

    # Compliance Result indexes
    if frappe.db.table_exists('Compliance Result'):
        _add_index_if_not_exists('Compliance Result',
            ['compliance_check', 'check_date'],
            'idx_compliance_result_check_date')

        _add_index_if_not_exists('Compliance Result',
            ['status', 'check_date'],
            'idx_compliance_result_status_date')

    # Risk Assessment indexes
    if frappe.db.table_exists('Risk Assessment'):
        _add_index_if_not_exists('Risk Assessment',
            ['module', 'assessment_date'],
            'idx_risk_assessment_module_date')

        _add_index_if_not_exists('Risk Assessment',
            ['overall_risk_level'],
            'idx_risk_assessment_level')

    # Module Sync Status indexes
    if frappe.db.table_exists('Module Sync Status'):
        _add_index_if_not_exists('Module Sync Status',
            ['module_name'],
            'idx_module_sync_name')

        _add_index_if_not_exists('Module Sync Status',
            ['last_sync'],
            'idx_module_sync_last_sync')

    # Audit Integrity Report indexes
    if frappe.db.table_exists('Audit Integrity Report'):
        _add_index_if_not_exists('Audit Integrity Report',
            ['execution_date', 'overall_status'],
            'idx_integrity_report_date_status')

        _add_index_if_not_exists('Audit Integrity Report',
            ['check_type'],
            'idx_integrity_report_type')

    # Audit Doctype Catalog indexes
    if frappe.db.table_exists('Audit Doctype Catalog'):
        _add_index_if_not_exists('Audit Doctype Catalog',
            ['is_active', 'module'],
            'idx_catalog_active_module')

        _add_index_if_not_exists('Audit Doctype Catalog',
            ['doctype_name'],
            'idx_catalog_doctype')

    # Audit Test Template indexes
    if frappe.db.table_exists('Audit Test Template'):
        _add_index_if_not_exists('Audit Test Template',
            ['category', 'is_active'],
            'idx_template_category_active')

        _add_index_if_not_exists('Audit Test Template',
            ['priority'],
            'idx_template_priority')

    frappe.db.commit()
    frappe.logger().info("Critical indexes installation completed")


def _add_index_if_not_exists(doctype, fields, index_name):
    """Add index to table if it doesn't already exist

    Args:
        doctype: The doctype name
        fields: List of fields to index
        index_name: Name for the index
    """
    try:
        table_name = f"tab{doctype}"

        # Check if index already exists
        existing_indexes = frappe.db.sql("""
            SELECT INDEX_NAME
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = %s
            AND INDEX_NAME = %s
        """, (table_name, index_name), as_dict=True)

        if existing_indexes:
            frappe.logger().debug(f"Index {index_name} already exists on {doctype}")
            return

        # Create the index
        field_list = ', '.join([f"`{f}`" for f in fields])
        frappe.db.sql(f"""
            CREATE INDEX `{index_name}`
            ON `{table_name}` ({field_list})
        """)

        frappe.logger().info(f"Created index {index_name} on {doctype} ({', '.join(fields)})")

    except Exception as e:
        frappe.logger().error(f"Error creating index {index_name} on {doctype}: {str(e)}")
        # Don't fail the entire patch if one index fails


def get_revert_query():
    """Return queries to revert this patch if needed"""
    # This is optional but can help with rollback
    return "DROP INDEX statements would go here if needed"
