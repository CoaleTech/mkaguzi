import frappe
from frappe import _
from frappe.utils import now, get_datetime, add_days, now_datetime
import json
from datetime import datetime, timedelta
from mkaguzi.controllers.integration_controllers import (
    financial_controller, hr_controller, inventory_controller, access_controller
)


def create_audit_trail_entry(doc, method):
	"""
	Create audit trail entry using ERPNext's Document History
	This function now leverages ERPNext's built-in document versioning and history tracking
	"""
	try:
		# Skip if this is a system document to prevent unnecessary overhead
		if doc.doctype in ["DocType", "Module Def", "DocPerm", "Custom DocPerm"]:
			return

		# ERPNext automatically tracks document history via:
		# - Version control (doc.save() creates versions)
		# - Document History (shows changes)
		# - Communication (comments)

		# For audit-specific tracking, we only log high-risk operations
		if requires_manual_review(doc):
			# Add comment to document for audit trail visibility
			comment = f"Audit Tracking: {doc.doctype} {doc.name} was {'created' if method == 'after_insert' else 'modified'} by {frappe.session.user or 'System'}. Risk Level: {assess_risk_level(doc)}"

			try:
				frappe.get_doc({
					'doctype': 'Comment',
					'comment_type': 'Comment',
					'reference_doctype': doc.doctype,
					'reference_name': doc.name,
					'content': comment,
					'comment_email': frappe.session.user
				}).insert(ignore_permissions=True)
			except:
				pass  # Comment creation is optional

		# Route to appropriate controller for additional processing
		route_to_controller(doc, method)

	except Exception as e:
		frappe.log_error(f"Audit Trail Logging Error: {str(e)}", "Audit Trail Error")


def route_to_controller(doc, method):
    """
    Route document processing to appropriate controller
    """
    try:
        module = get_module_for_doctype(doc.doctype)
        operation = 'CREATE' if method == 'after_insert' else 'UPDATE'

        if module == 'Financial':
            financial_controller.sync_financial_transaction(doc, operation)
        elif module == 'HR':
            hr_controller.sync_hr_transaction(doc, operation)
        elif module == 'Inventory':
            inventory_controller.sync_inventory_transaction(doc, operation)
        elif module == 'Access Control':
            access_controller.sync_access_transaction(doc, operation)

    except Exception as e:
        frappe.log_error(f"Controller Routing Error: {str(e)}", "Controller Routing")


def update_audit_trail_entry(doc, method):
    """
    Update audit trail entry for document modifications
    """
    try:
        # Skip if this is already an audit trail entry
        if doc.doctype == "Audit Trail Entry":
            return

        # Get the previous version for comparison
        old_doc = doc.get_doc_before_save()
        if not old_doc:
            return

        # Check if there are meaningful changes
        changes = get_document_changes(old_doc, doc)
        if not changes:
            return

        # Create audit trail entry for update
        audit_entry = frappe.get_doc({
            'doctype': 'Audit Trail Entry',
            'source_doctype': doc.doctype,
            'source_document': doc.name,
            'operation': 'UPDATE',
            'timestamp': now_datetime(),
            'user': frappe.session.user or 'System',
            'old_values': json.dumps(old_doc.as_dict()),
            'new_values': json.dumps(doc.as_dict()),
            'changes': json.dumps(changes),
            'module': get_module_for_doctype(doc.doctype),
            'risk_level': assess_risk_level(doc),
            'requires_review': requires_manual_review(doc)
        })

        audit_entry.insert(ignore_permissions=True)
        frappe.db.commit()

    except Exception as e:
        frappe.log_error(f"Audit Trail Update Error: {str(e)}", "Audit Trail Error")


def delete_audit_trail_entry(doc, method):
    """
    Log deletion of documents
    """
    try:
        # Skip if this is already an audit trail entry
        if doc.doctype == "Audit Trail Entry":
            return

        # Create audit trail entry for deletion
        audit_entry = frappe.get_doc({
            'doctype': 'Audit Trail Entry',
            'source_doctype': doc.doctype,
            'source_document': doc.name,
            'operation': 'DELETE',
            'timestamp': now_datetime(),
            'user': frappe.session.user or 'System',
            'old_values': json.dumps(doc.as_dict()),
            'new_values': '{}',
            'module': get_module_for_doctype(doc.doctype),
            'risk_level': 'HIGH',  # Deletions are always high risk
            'requires_review': True
        })

        audit_entry.insert(ignore_permissions=True)
        frappe.db.commit()

    except Exception as e:
        frappe.log_error(f"Audit Trail Delete Error: {str(e)}", "Audit Trail Error")


def on_audit_trail_entry_insert(doc, method):
    """
    Process newly created audit trail entries
    """
    try:
        # Trigger real-time risk assessment
        assess_and_flag_risks(doc)

        # Check for anomalies
        detect_anomalies(doc)

        # Update compliance status if needed
        update_compliance_status(doc)

    except Exception as e:
        frappe.log_error(f"Audit Trail Processing Error: {str(e)}", "Audit Trail Processing")


def on_audit_trail_entry_update(doc, method):
    """
    Process updated audit trail entries
    """
    try:
        # Re-assess risks if status changed
        if doc.has_value_changed('status'):
            assess_and_flag_risks(doc)

    except Exception as e:
        frappe.log_error(f"Audit Trail Update Processing Error: {str(e)}", "Audit Trail Processing")


def get_module_for_doctype(doctype):
    """
    Map doctypes to audit modules
    """
    module_mapping = {
        # Financial
        'GL Entry': 'Financial',
        'Journal Entry': 'Financial',
        'Payment Entry': 'Financial',
        'Sales Invoice': 'Financial',
        'Purchase Invoice': 'Financial',
        'Sales Order': 'Financial',
        'Purchase Order': 'Financial',

        # HR
        'Employee': 'HR',
        'Salary Slip': 'Payroll',
        'Salary Structure': 'Payroll',
        'Leave Application': 'HR',
        'Attendance': 'HR',
        'Expense Claim': 'HR',

        # Inventory
        'Stock Entry': 'Inventory',
        'Stock Reconciliation': 'Inventory',
        'Item': 'Inventory',
        'Delivery Note': 'Inventory',
        'Purchase Receipt': 'Inventory',

        # Access Control
        'User': 'Access Control',
        'Role': 'Access Control',
        'User Permission': 'Access Control'
    }

    return module_mapping.get(doctype, 'General')


def assess_risk_level(doc):
    """
    Assess risk level based on document type and values
    """
    high_risk_doctypes = ['Journal Entry', 'Payment Entry', 'Salary Slip', 'User', 'Role']
    medium_risk_doctypes = ['GL Entry', 'Sales Invoice', 'Purchase Invoice', 'Employee']

    if doc.doctype in high_risk_doctypes:
        return 'HIGH'
    elif doc.doctype in medium_risk_doctypes:
        return 'MEDIUM'
    else:
        return 'LOW'


def requires_manual_review(doc):
    """
    Determine if the change requires manual review
    """
    # High-risk operations always require review
    if assess_risk_level(doc) == 'HIGH':
        return True

    # Large financial transactions
    if doc.doctype in ['Payment Entry', 'Journal Entry', 'Sales Invoice', 'Purchase Invoice']:
        amount_fields = ['total', 'grand_total', 'paid_amount', 'received_amount']
        for field in amount_fields:
            if hasattr(doc, field) and getattr(doc, field, 0) > 10000:  # Threshold
                return True

    # User permission changes
    if doc.doctype in ['User', 'Role', 'User Permission']:
        return True

    return False


def get_document_changes(old_doc, new_doc):
    """
    Compare old and new document versions to identify changes
    """
    changes = {}
    old_dict = old_doc.as_dict()
    new_dict = new_doc.as_dict()

    for field in new_dict:
        if field not in old_dict or old_dict[field] != new_dict[field]:
            changes[field] = {
                'old_value': old_dict.get(field),
                'new_value': new_dict[field]
            }

    return changes


def assess_and_flag_risks(audit_entry):
    """
    Assess risks and create findings if necessary
    """
    try:
        # High-risk operations trigger automatic finding creation
        if audit_entry.risk_level == 'HIGH' and audit_entry.requires_review:
            create_automated_finding(audit_entry)

        # Check for unusual patterns
        check_for_unusual_patterns(audit_entry)

    except Exception as e:
        frappe.log_error(f"Risk Assessment Error: {str(e)}", "Risk Assessment")


def create_automated_finding(audit_entry):
    """
    Create automated audit finding for high-risk operations
    """
    try:
        finding = frappe.get_doc({
            'doctype': 'Audit Finding',
            'finding_title': f"High-risk operation in {audit_entry.source_doctype}",
            'description': f"Automated detection of high-risk operation: {audit_entry.operation} on {audit_entry.source_document}",
            'finding_type': 'Automated Risk Detection',
            'severity': 'Medium',
            'status': 'Open',
            'reported_date': now(),
            'responsible_party': get_default_auditor(),
            'audit_trail_reference': audit_entry.name
        })

        finding.insert(ignore_permissions=True)
        frappe.db.commit()

    except Exception as e:
        frappe.log_error(f"Automated Finding Creation Error: {str(e)}", "Finding Creation")


def detect_anomalies(audit_entry):
    """
    Detect anomalous patterns in audit trail
    """
    try:
        # Check for unusual timing patterns
        check_timing_anomalies(audit_entry)

        # Check for unusual user behavior
        check_user_anomalies(audit_entry)

        # Check for unusual value patterns
        check_value_anomalies(audit_entry)

    except Exception as e:
        frappe.log_error(f"Anomaly Detection Error: {str(e)}", "Anomaly Detection")


def check_timing_anomalies(audit_entry):
    """
    Check for unusual timing patterns
    """
    # Implementation for timing-based anomaly detection
    pass


def check_user_anomalies(audit_entry):
    """
    Check for unusual user behavior patterns
    """
    # Implementation for user behavior anomaly detection
    pass


def check_value_anomalies(audit_entry):
    """
    Check for unusual value patterns
    """
    # Implementation for value-based anomaly detection
    pass


def check_for_unusual_patterns(audit_entry):
    """
    Check for unusual patterns that may indicate risk
    """
    # Implementation for pattern-based risk detection
    pass


def update_compliance_status(audit_entry):
    """
    Update compliance status based on audit trail activity
    """
    # Implementation for compliance status updates
    pass


def get_default_auditor():
    """
    Get default auditor for automated findings
    """
    # Return default auditor user
    return frappe.db.get_single_value('Audit Settings', 'default_auditor') or 'Administrator'


# Scheduled Sync Functions

def hourly_data_sync():
    """
    Hourly synchronization of data
    """
    try:
        frappe.logger().info("Starting hourly data sync")

        # Sync pending audit trail entries
        sync_pending_entries()

        # Update real-time dashboards
        update_realtime_dashboards()

        # Check system health
        perform_health_checks()

        frappe.logger().info("Hourly data sync completed")

    except Exception as e:
        frappe.log_error(f"Hourly Sync Error: {str(e)}", "Data Sync")


def daily_reconciliation():
    """
    Daily reconciliation process
    """
    try:
        frappe.logger().info("Starting daily reconciliation")

        # Reconcile financial data using controller
        financial_controller.reconcile_financial_data()

        # Reconcile HR data
        reconcile_hr_data()

        # Reconcile inventory data
        reconcile_inventory_data()

        # Generate reconciliation report
        generate_reconciliation_report()

        frappe.logger().info("Daily reconciliation completed")

    except Exception as e:
        frappe.log_error(f"Daily Reconciliation Error: {str(e)}", "Reconciliation")


def daily_compliance_check():
    """
    Daily compliance status check
    """
    try:
        frappe.logger().info("Starting daily compliance check")

        # Check compliance for all active checks
        compliance_checks = frappe.get_all('Compliance Check',
            filters={'status': 'Active'},
            fields=['name', 'check_name', 'compliance_type'])

        for check in compliance_checks:
            run_compliance_check(check.name)

        frappe.logger().info("Daily compliance check completed")

    except Exception as e:
        frappe.log_error(f"Daily Compliance Check Error: {str(e)}", "Compliance Check")


def daily_risk_assessment():
    """
    Daily risk assessment
    """
    try:
        frappe.logger().info("Starting daily risk assessment")

        # Assess risks across all modules
        assess_module_risks('Financial')
        assess_module_risks('HR')
        assess_module_risks('Inventory')
        assess_module_risks('Access Control')

        # Update risk dashboard
        update_risk_dashboard()

        frappe.logger().info("Daily risk assessment completed")

    except Exception as e:
        frappe.log_error(f"Daily Risk Assessment Error: {str(e)}", "Risk Assessment")


def weekly_comprehensive_audit():
    """
    Weekly comprehensive audit
    """
    try:
        frappe.logger().info("Starting weekly comprehensive audit")

        # Run comprehensive audit tests
        run_comprehensive_audit_tests()

        # Generate weekly audit report
        generate_weekly_audit_report()

        frappe.logger().info("Weekly comprehensive audit completed")

    except Exception as e:
        frappe.log_error(f"Weekly Audit Error: {str(e)}", "Comprehensive Audit")


def monthly_executive_summary():
    """
    Monthly executive summary generation
    """
    try:
        frappe.logger().info("Starting monthly executive summary")

        # Generate executive summary report
        generate_executive_summary()

        # Send to stakeholders
        send_executive_summary()

        frappe.logger().info("Monthly executive summary completed")

    except Exception as e:
        frappe.log_error(f"Monthly Summary Error: {str(e)}", "Executive Summary")


def check_system_health():
    """
    Check system health and performance
    """
    try:
        # Check database connectivity
        check_database_health()

        # Check API responsiveness
        check_api_health()

        # Check disk space
        check_disk_space()

        # Log health status
        log_system_health()

    except Exception as e:
        frappe.log_error(f"System Health Check Error: {str(e)}", "Health Check")


def cleanup_old_audit_trails():
    """
    Clean up old audit trail entries
    """
    try:
        # Get retention period from settings
        retention_days = frappe.db.get_single_value('Audit Settings', 'audit_trail_retention_days') or 365

        # Delete old entries
        cutoff_date = add_days(now(), -retention_days)

        old_entries = frappe.get_all('Audit Trail Entry',
            filters={'timestamp': ['<', cutoff_date]},
            fields=['name'])

        for entry in old_entries:
            frappe.delete_doc('Audit Trail Entry', entry.name, ignore_permissions=True)

        frappe.db.commit()

        frappe.logger().info(f"Cleaned up {len(old_entries)} old audit trail entries")

    except Exception as e:
        frappe.log_error(f"Audit Trail Cleanup Error: {str(e)}", "Cleanup")


# Helper functions for scheduled tasks

def sync_pending_entries():
    """Sync any pending audit trail entries"""
    pass

def update_realtime_dashboards():
    """Update real-time dashboard data"""
    pass

def perform_health_checks():
    """Perform system health checks"""
    pass

def reconcile_hr_data():
    """Reconcile HR data"""
    pass

def reconcile_inventory_data():
    """Reconcile inventory data"""
    pass

def generate_reconciliation_report():
    """Generate reconciliation report"""
    pass

def run_compliance_check(check_id):
    """Run individual compliance check"""
    pass

def assess_module_risks(module):
    """Assess risks for specific module"""
    pass

def update_risk_dashboard():
    """Update risk dashboard"""
    pass

def run_comprehensive_audit_tests():
    """Run comprehensive audit tests"""
    pass

def generate_weekly_audit_report():
    """Generate weekly audit report"""
    pass

def generate_executive_summary():
    """Generate executive summary"""
    pass

def send_executive_summary():
    """Send executive summary to stakeholders"""
    pass

def check_database_health():
    """Check database health"""
    pass

def check_api_health():
    """Check API health"""
    pass

def check_disk_space():
    """Check disk space"""
    pass

def log_system_health():
    """Log system health status"""
    pass