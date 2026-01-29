"""
Migration script to add database indexes for performance
"""
import frappe

def migrate():
    """Add indexes for frequently queried fields"""

    indexes = [
        # Audit Trail Entry indexes
        {
            'table': 'tabAudit Trail Entry',
            'index_name': 'idx_audit_trail_document',
            'fields': ['document_type', 'document_name']
        },
        {
            'table': 'tabAudit Trail Entry',
            'index_name': 'idx_audit_trail_timestamp',
            'fields': ['timestamp']
        },
        {
            'table': 'tabAudit Trail Entry',
            'index_name': 'idx_audit_trail_module',
            'fields': ['module']
        },

        # Audit GL Entry indexes
        {
            'table': 'tabAudit GL Entry',
            'index_name': 'idx_audit_gl_account',
            'fields': ['account_no']
        },
        {
            'table': 'tabAudit GL Entry',
            'index_name': 'idx_audit_gl_posting_date',
            'fields': ['posting_date']
        },
        {
            'table': 'tabAudit GL Entry',
            'index_name': 'idx_audit_gl_risk_level',
            'fields': ['risk_level']
        },

        # Compliance Check indexes
        {
            'table': 'tabCompliance Check',
            'index_name': 'idx_compliance_check_status',
            'fields': ['status']
        },
        {
            'table': 'tabCompliance Check',
            'index_name': 'idx_compliance_check_next_due',
            'fields': ['next_due_date']
        },
        {
            'table': 'tabCompliance Check',
            'index_name': 'idx_compliance_check_type',
            'fields': ['compliance_type']
        },

        # Compliance Execution indexes
        {
            'table': 'tabCompliance Execution',
            'index_name': 'idx_compliance_exec_check',
            'fields': ['compliance_check', 'execution_date']
        },

        # Audit Finding indexes
        {
            'table': 'tabAudit Finding',
            'index_name': 'idx_finding_status',
            'fields': ['status']
        },
        {
            'table': 'tabAudit Finding',
            'index_name': 'idx_finding_severity',
            'fields': ['severity']
        },
        {
            'table': 'tabAudit Finding',
            'index_name': 'idx_finding_target_date',
            'fields': ['target_completion_date']
        }
    ]

    for idx in indexes:
        try:
            field_list = ', '.join(idx['fields'])
            index_sql = f"""
                CREATE INDEX IF NOT EXISTS {idx['index_name']}
                ON {idx['table']} ({field_list})
            """
            frappe.db.sql(index_sql)
            frappe.db.commit()
            print(f"Created index: {idx['index_name']}")

        except Exception as e:
            frappe.log_error(f"Index creation failed: {idx['index_name']} - {str(e)}")
            print(f"Failed to create index: {idx['index_name']}")

    print("Database indexes migration completed")

def rollback():
    """Rollback indexes if needed"""
    indexes_to_drop = [
        'idx_audit_trail_document', 'idx_audit_trail_timestamp', 'idx_audit_trail_module',
        'idx_audit_gl_account', 'idx_audit_gl_posting_date', 'idx_audit_gl_risk_level',
        'idx_compliance_check_status', 'idx_compliance_check_next_due', 'idx_compliance_check_type',
        'idx_compliance_exec_check',
        'idx_finding_status', 'idx_finding_severity', 'idx_finding_target_date'
    ]

    for index_name in indexes_to_drop:
        try:
            frappe.db.sql(f"DROP INDEX IF EXISTS {index_name}")
            frappe.db.commit()
            print(f"Dropped index: {index_name}")
        except Exception as e:
            print(f"Failed to drop index: {index_name}")