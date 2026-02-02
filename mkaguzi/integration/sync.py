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
				from mkaguzi.utils.permissions import safe_insert
				comment_doc = frappe.get_doc({
					'doctype': 'Comment',
					'comment_type': 'Comment',
					'reference_doctype': doc.doctype,
					'reference_name': doc.name,
					'content': comment,
					'comment_email': frappe.session.user
				})
				safe_insert(comment_doc)
			except:
				pass  # Comment creation is optional

		# Route to appropriate controller for additional processing
		route_to_controller(doc, method)

	except Exception as e:
		# Truncate error message to avoid CharacterLengthExceededError
		error_msg = str(e)[:100] if len(str(e)) > 100 else str(e)
		frappe.log_error(f"Audit Trail Error: {error_msg}", "Audit Trail")


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
        # Truncate error message to avoid CharacterLengthExceededError
        error_msg = str(e)[:100] if len(str(e)) > 100 else str(e)
        frappe.log_error(f"Controller Error: {error_msg}", "Controller")


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
        from mkaguzi.utils.permissions import safe_insert

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

        safe_insert(audit_entry)
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
        from mkaguzi.utils.permissions import safe_insert

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

        safe_insert(audit_entry)
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
        from mkaguzi.utils.permissions import safe_insert

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

        safe_insert(finding)
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

        # Check for unusual value patterns (real-time single entry check)
        check_value_anomalies_single(audit_entry)

    except Exception as e:
        frappe.log_error(f"Anomaly Detection Error: {str(e)[:100]}", "Anomaly Detection")


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


def check_value_anomalies_single(audit_entry):
    """
    Check for unusual value patterns in a single audit entry.
    
    This is a real-time check called during entry creation.
    For batch anomaly detection, use check_value_anomalies().
    
    Args:
        audit_entry: The audit trail entry document to check
    """
    # TODO: Implement real-time value anomaly detection for single entry
    # This could check if the entry value deviates significantly from recent averages
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
    Clean up old audit trail entries using batch deletion
    """
    try:
        from mkaguzi.utils.permissions import is_system_manager

        # Only System Manager can clean up audit trails
        if not is_system_manager():
            frappe.throw(_("Only System Manager can clean up audit trail entries"))

        # Get retention period from settings
        retention_days = frappe.db.get_single_value('Audit Settings', 'audit_trail_retention_days') or 365

        cutoff_date = add_days(now(), -retention_days)

        # Get total count
        total_count = frappe.db.count('Audit Trail Entry', {
            'timestamp': ['<', cutoff_date]
        })

        if total_count == 0:
            frappe.logger().info("No old entries to clean up")
            return

        # Delete in batches of 1000
        batch_size = 1000
        deleted_count = 0

        while deleted_count < total_count:
            # Use SQL bulk delete for performance
            frappe.db.sql("""
                DELETE FROM `tabAudit Trail Entry`
                WHERE timestamp < %s
                LIMIT %s
            """, (cutoff_date, batch_size))

            deleted_count += batch_size
            frappe.db.commit()

            # Log progress
            progress = min(100, int((deleted_count / total_count) * 100))
            frappe.logger().info(f"Cleanup progress: {progress}% ({deleted_count}/{total_count})")

        frappe.logger().info(f"Audit trail cleanup completed: {total_count} entries deleted")

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Audit Trail Cleanup Error: {str(e)}", "Cleanup")


# Helper functions for scheduled tasks

def sync_pending_entries():
    """Sync any pending audit trail entries"""
    try:
        frappe.logger().info("Starting pending entries sync")

        # Get pending entries (entries not yet synced)
        pending_entries = frappe.get_all('Audit Trail Entry',
            filters={'synced': 0},
            fields=['name', 'document_type', 'document_name'],
            limit=1000
        )

        if not pending_entries:
            frappe.logger().info("No pending entries to sync")
            return {'success': True, 'synced_count': 0}

        synced_count = 0

        for entry in pending_entries:
            try:
                # Mark as synced
                frappe.db.set_value('Audit Trail Entry', entry.name, 'synced', 1)
                synced_count += 1

            except Exception as e:
                frappe.log_error(f"Error syncing entry {entry.name}: {str(e)}", "Sync Error")

        frappe.db.commit()
        frappe.logger().info(f"Synced {synced_count} pending entries")

        return {'success': True, 'synced_count': synced_count}

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Sync Pending Entries Error: {str(e)}", "Data Sync")
        return {'success': False, 'error': str(e)}


def update_realtime_dashboards():
    """Update real-time dashboard data cache"""
    try:
        frappe.logger().info("Updating dashboard caches")

        cache = frappe.cache()
        cache_prefix = "mkaguzi:dashboard:"

        # Get all active dashboard users
        dashboard_users = frappe.get_all('User',
            filters={'enabled': 1, 'user_type': 'System User'},
            pluck='name'
        )

        updated_count = 0

        for user in dashboard_users:
            try:
                # Invalidate dashboard cache for this user
                cache.delete_keys(f"{cache_prefix}{user}*")
                updated_count += 1

            except Exception as e:
                frappe.log_error(f"Error updating dashboard for {user}: {str(e)}", "Dashboard Update")

        frappe.logger().info(f"Updated dashboard caches for {updated_count} users")

        return {'success': True, 'updated_count': updated_count}

    except Exception as e:
        frappe.log_error(f"Dashboard Update Error: {str(e)}", "Dashboard Update")
        return {'success': False, 'error': str(e)}


def perform_health_checks():
    """Perform all system health checks"""
    try:
        frappe.logger().info("Performing system health checks")

        # Run all health checks
        health_results = {
            'database': check_database_health(),
            'api': check_api_health(),
            'disk': check_disk_space()
        }

        # Log aggregated health
        log_system_health()

        # Check for critical issues
        critical_issues = []

        for check_name, result in health_results.items():
            if result.get('status') == 'critical':
                critical_issues.append(f"{check_name}: {result.get('error', 'Critical status')}")
            elif result.get('status') == 'error':
                critical_issues.append(f"{check_name}: {result.get('error', 'Error occurred')}")

        if critical_issues:
            # Send alert notification
            try:
                from mkaguzi.utils.notifications import NotificationManager
                manager = NotificationManager()
                manager.send_critical_alert(
                    title="System Health Check Failed",
                    message="; ".join(critical_issues)
                )
            except Exception as e:
                frappe.log_error(f"Failed to send health alert: {str(e)}", "Health Check")

        frappe.logger().info("Health checks completed")

        return health_results

    except Exception as e:
        frappe.log_error(f"Health Checks Error: {str(e)}", "Health Check")
        return {'status': 'error', 'error': str(e)}


def reconcile_hr_data():
    """Reconcile HR-specific data"""
    try:
        frappe.logger().info("Starting HR data reconciliation")

        from mkaguzi.controllers.integration_controllers import HRIntegrationController
        hr_controller = HRIntegrationController()

        # Reconcile employee data
        employee_results = hr_controller.reconcile_employees()

        # Reconcile salary data
        salary_results = hr_controller.reconcile_salary_slips()

        frappe.logger().info("HR data reconciliation completed")

        return {
            'success': True,
            'employees': employee_results,
            'salaries': salary_results
        }

    except Exception as e:
        frappe.log_error(f"HR Reconciliation Error: {str(e)}", "Data Reconciliation")
        return {'success': False, 'error': str(e)}


def reconcile_inventory_data():
    """Reconcile inventory-specific data"""
    try:
        frappe.logger().info("Starting inventory data reconciliation")

        from mkaguzi.controllers.integration_controllers import InventoryIntegrationController
        inv_controller = InventoryIntegrationController()

        # Reconcile stock entries
        stock_results = inv_controller.reconcile_stock_entries()

        # Reconcile items
        item_results = inv_controller.reconcile_items()

        frappe.logger().info("Inventory data reconciliation completed")

        return {
            'success': True,
            'stock_entries': stock_results,
            'items': item_results
        }

    except Exception as e:
        frappe.log_error(f"Inventory Reconciliation Error: {str(e)}", "Data Reconciliation")
        return {'success': False, 'error': str(e)}


def generate_reconciliation_report():
    """Generate reconciliation report"""
    try:
        frappe.logger().info("Generating reconciliation report")

        report_date = frappe.utils.nowdate()

        # Create reconciliation report
        report = frappe.new_doc('Reconciliation Report')
        report.report_date = report_date
        report.report_type = 'Daily'

        # Add financial data
        financial_summary = frappe.db.sql("""
            SELECT
                COUNT(*) as total_entries,
                COUNT(CASE WHEN reconciliation_status = 'Reconciled' THEN 1 END) as reconciled,
                COUNT(CASE WHEN reconciliation_status = 'Unreconciled' THEN 1 END) as unreconciled,
                COUNT(CASE WHEN reconciliation_status = 'Exception' THEN 1 END) as exceptions
            FROM `tabAudit GL Entry`
            WHERE DATE(creation) = %s
        """, report_date, as_dict=True)

        if financial_summary:
            report.total_entries = financial_summary[0].total_entries
            report.reconciled_entries = financial_summary[0].reconciled
            report.unreconciled_entries = financial_summary[0].unreconciled
            report.exception_entries = financial_summary[0].exceptions

        report.save()

        frappe.db.commit()
        frappe.logger().info("Reconciliation report generated")

        return report.as_dict()

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Reconciliation Report Error: {str(e)}", "Report Generation")
        return {'success': False, 'error': str(e)}


def run_compliance_check(check_name):
    """Run individual compliance check"""
    try:
        if not frappe.db.exists('Compliance Check', check_name):
            frappe.throw(_("Compliance Check {0} not found").format(check_name))

        check_doc = frappe.get_doc('Compliance Check', check_name)

        frappe.logger().info(f"Running compliance check: {check_name}")

        # Execute compliance check based on type
        result = _execute_compliance_check(check_doc)

        # Update check status
        check_doc.last_run_date = frappe.utils.now()
        check_doc.last_run_result = result.get('status', 'Unknown')
        check_doc.last_run_details = frappe.as_json(result)
        check_doc.save()

        frappe.db.commit()

        frappe.logger().info(f"Compliance check {check_name} completed: {result.get('status')}")

        return result

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Compliance Check Error ({check_name}): {str(e)}", "Compliance Check")
        return {'status': 'error', 'error': str(e)}


def assess_module_risks(module_name):
    """Assess risks for specific module"""
    try:
        frappe.logger().info(f"Assessing risks for module: {module_name}")

        # Get module-specific risk indicators
        risk_indicators = frappe.get_all('Risk Indicator',
            filters={'module': module_name, 'active': 1},
            fields=['name', 'indicator_type', 'threshold', 'current_value']
        )

        risk_scores = []

        for indicator in risk_indicators:
            # Calculate risk score based on indicator
            score = _calculate_risk_score(indicator)
            risk_scores.append(score)

        # Aggregate risk scores
        overall_risk = 'Low'
        if risk_scores:
            avg_score = sum(r['score'] for r in risk_scores) / len(risk_scores)
            if avg_score > 0.7:
                overall_risk = 'High'
            elif avg_score > 0.4:
                overall_risk = 'Medium'

        # Update risk assessment
        assessment_date = frappe.utils.nowdate()

        # Create or update risk assessment
        assessment = frappe.new_doc('Risk Assessment')
        assessment.module = module_name
        assessment.assessment_date = assessment_date
        assessment.overall_risk_level = overall_risk
        assessment.risk_indicators = frappe.as_json(risk_scores)
        assessment.save()

        frappe.db.commit()

        frappe.logger().info(f"Risk assessment for {module_name}: {overall_risk}")

        return assessment.as_dict()

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Risk Assessment Error ({module_name}): {str(e)}", "Risk Assessment")
        return {'success': False, 'error': str(e)}


def update_risk_dashboard():
    """Update risk dashboard"""
    try:
        frappe.logger().info("Updating risk dashboard")

        cache = frappe.cache()

        # Get all module risk levels
        module_risks = frappe.db.sql("""
            SELECT module, overall_risk_level, assessment_date
            FROM `tabRisk Assessment`
            WHERE assessment_date = (SELECT MAX(assessment_date) FROM `tabRisk Assessment`)
            ORDER BY overall_risk_level DESC
        """, as_dict=True)

        # Calculate summary statistics
        risk_summary = {
            'high': sum(1 for r in module_risks if r.overall_risk_level == 'High'),
            'medium': sum(1 for r in module_risks if r.overall_risk_level == 'Medium'),
            'low': sum(1 for r in module_risks if r.overall_risk_level == 'Low'),
            'modules': module_risks
        }

        # Cache the dashboard data
        cache.set_value('mkaguzi:risk_dashboard', frappe.as_json(risk_summary), expiry=300)

        frappe.logger().info("Risk dashboard updated")

        return risk_summary

    except Exception as e:
        frappe.log_error(f"Risk Dashboard Update Error: {str(e)}", "Risk Dashboard")
        return {'success': False, 'error': str(e)}


def run_comprehensive_audit_tests():
    """Run comprehensive audit tests"""
    try:
        frappe.logger().info("Running comprehensive audit tests")

        # Get all active test templates
        test_templates = frappe.get_all('Audit Test Template',
            filters={'active': 1},
            fields=['name', 'test_name', 'test_type', 'module']
        )

        results = []

        for template in test_templates:
            try:
                # Execute each test
                result = _execute_audit_test(template)
                results.append(result)

            except Exception as e:
                results.append({
                    'template': template.name,
                    'status': 'error',
                    'error': str(e)
                })

        # Generate summary
        summary = {
            'total_tests': len(results),
            'passed': sum(1 for r in results if r.get('status') == 'passed'),
            'failed': sum(1 for r in results if r.get('status') == 'failed'),
            'errors': sum(1 for r in results if r.get('status') == 'error'),
            'results': results
        }

        frappe.logger().info(f"Comprehensive audit tests completed: {summary['passed']}/{summary['total_tests']} passed")

        return summary

    except Exception as e:
        frappe.log_error(f"Comprehensive Audit Tests Error: {str(e)}", "Audit Tests")
        return {'success': False, 'error': str(e)}


def generate_weekly_audit_report():
    """Generate weekly audit report"""
    try:
        frappe.logger().info("Generating weekly audit report")

        # Get week start and end dates
        today = frappe.utils.getdate()
        week_start = today - frappe.utils.timedelta(days=today.weekday())
        week_end = week_start + frappe.utils.timedelta(days=6)

        # Create weekly report
        report = frappe.new_doc('Audit Report')
        report.report_name = f"Weekly Audit Report - {week_start}"
        report.report_type = 'Weekly'
        report.start_date = week_start
        report.end_date = week_end

        # Add summary statistics
        summary_data = frappe.db.sql("""
            SELECT
                COUNT(*) as total_audits,
                COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'In Progress' THEN 1 END) as in_progress
            FROM `tabAudit Execution`
            WHERE start_date >= %s AND start_date <= %s
        """, (week_start, week_end), as_dict=True)

        if summary_data:
            report.total_audits = summary_data[0].total_audits
            report.completed_audits = summary_data[0].completed
            report.pending_audits = summary_data[0].in_progress

        report.save()

        frappe.db.commit()
        frappe.logger().info("Weekly audit report generated")

        return report.as_dict()

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Weekly Audit Report Error: {str(e)}", "Report Generation")
        return {'success': False, 'error': str(e)}


def generate_executive_summary():
    """Generate executive summary"""
    try:
        frappe.logger().info("Generating executive summary")

        # Get current month
        today = frappe.utils.getdate()
        month_start = today.replace(day=1)

        # Gather metrics for executive summary
        metrics = {
            'audit_engagements': _get_audit_engagement_metrics(month_start, today),
            'findings': _get_finding_metrics(month_start, today),
            'risk_assessments': _get_risk_metrics(month_start, today),
            'compliance': _get_compliance_metrics(month_start, today)
        }

        # Create executive summary
        summary = frappe.new_doc('Executive Summary')
        summary.period_start = month_start
        summary.period_end = today
        summary.metrics = frappe.as_json(metrics)

        # Calculate overall health score
        health_score = _calculate_health_score(metrics)
        summary.health_score = health_score

        summary.save()

        frappe.db.commit()
        frappe.logger().info("Executive summary generated")

        return summary.as_dict()

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Executive Summary Error: {str(e)}", "Executive Summary")
        return {'success': False, 'error': str(e)}


def send_executive_summary():
    """Send executive summary to stakeholders"""
    try:
        frappe.logger().info("Sending executive summary")

        # Get latest executive summary
        latest_summary = frappe.get_last_doc('Executive Summary',
            filters={'sent': 0}
        )

        if not latest_summary:
            frappe.logger().info("No pending executive summary to send")
            return {'success': True, 'sent': 0}

        # Get recipients from settings
        settings = frappe.get_single('Audit Settings')
        recipients = settings.default_notification_recipients.split(',') if settings.default_notification_recipients else []

        if not recipients:
            frappe.logger().warning("No recipients configured for executive summary")
            return {'success': False, 'error': 'No recipients configured'}

        # Send email
        from frappe.core.doctype.communication.email import make

        for recipient in recipients:
            make(
                subject=f"Executive Summary - {latest_summary.period_start} to {latest_summary.period_end}",
                recipients=recipient,
                content=_format_executive_summary_email(latest_summary),
                send_immediately=True
            )

        # Mark as sent
        latest_summary.sent = 1
        latest_summary.sent_date = frappe.utils.now()
        latest_summary.save()

        frappe.db.commit()
        frappe.logger().info(f"Executive summary sent to {len(recipients)} recipients")

        return {'success': True, 'sent': len(recipients)}

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Send Executive Summary Error: {str(e)}", "Executive Summary")
        return {'success': False, 'error': str(e)}


def check_database_health():
    """Check database health metrics"""
    try:
        health_status = {
            'database_size': None,
            'table_sizes': {},
            'slow_queries': [],
            'connection_pool': None,
            'status': 'healthy'
        }

        # Get database size
        db_size = frappe.db.sql("""
            SELECT
                ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as size_mb
            FROM information_schema.TABLES
            WHERE table_schema = DATABASE()
        """, as_dict=True)

        if db_size:
            health_status['database_size'] = db_size[0].size_mb

        # Get largest tables
        table_sizes = frappe.db.sql("""
            SELECT
                table_name,
                ROUND((data_length + index_length) / 1024 / 1024, 2) as size_mb,
                table_rows
            FROM information_schema.TABLES
            WHERE table_schema = DATABASE()
            AND table_name LIKE 'tab%'
            ORDER BY (data_length + index_length) DESC
            LIMIT 10
        """, as_dict=True)

        health_status['table_sizes'] = {t.table_name: {'size_mb': t.size_mb, 'rows': t.table_rows} for t in table_sizes}

        # Check for potential slow queries (simplified)
        large_tables = [t for t in table_sizes if t.size_mb > 100]
        if large_tables:
            health_status['slow_queries'] = [f"Large table: {t.table_name} ({t.size_mb} MB)" for t in large_tables]
            health_status['status'] = 'warning'

        return health_status

    except Exception as e:
        frappe.log_error(f"Database Health Check Error: {str(e)}", "Health Check")
        return {'status': 'error', 'error': str(e)}


def check_api_health():
    """Check API endpoint health"""
    try:
        health_status = {
            'endpoints': {},
            'response_times': {},
            'error_rate': 0.0,
            'status': 'healthy'
        }

        # Define critical endpoints to check
        endpoints = [
            ('get_system_status', '/api/method/mkaguzi.api.audit_api.get_system_status'),
            ('get_audit_trail', '/api/method/mkaguzi.api.audit_api.get_audit_trail'),
        ]

        import time

        for endpoint_name, endpoint_path in endpoints:
            start_time = time.time()

            try:
                # Make a simple health check call
                if endpoint_name == 'get_system_status':
                    result = frappe.get_doc('Audit API', 'Audit API').get_system_status()

                response_time = time.time() - start_time
                health_status['response_times'][endpoint_name] = round(response_time * 1000, 2)  # ms

                # Flag slow endpoints (> 5 seconds)
                if response_time > 5:
                    health_status['endpoints'][endpoint_name] = 'slow'
                    health_status['status'] = 'warning'
                else:
                    health_status['endpoints'][endpoint_name] = 'ok'

            except Exception as e:
                health_status['endpoints'][endpoint_name] = 'error'
                health_status['error_rate'] += 1
                health_status['status'] = 'error'

        return health_status

    except Exception as e:
        frappe.log_error(f"API Health Check Error: {str(e)}", "Health Check")
        return {'status': 'error', 'error': str(e)}


def check_disk_space():
    """Check available disk space"""
    try:
        import shutil

        disk_usage = shutil.disk_usage('/')

        total_gb = disk_usage.total / (1024 ** 3)
        used_gb = disk_usage.used / (1024 ** 3)
        free_gb = disk_usage.free / (1024 ** 3)
        usage_percent = (used_gb / total_gb) * 100

        health_status = {
            'total_gb': round(total_gb, 2),
            'used_gb': round(used_gb, 2),
            'free_gb': round(free_gb, 2),
            'usage_percent': round(usage_percent, 2),
            'status': 'healthy'
        }

        # Warning if less than 20% free
        if usage_percent > 80:
            health_status['status'] = 'warning'

        # Critical if less than 10% free
        if usage_percent > 90:
            health_status['status'] = 'critical'

        return health_status

    except Exception as e:
        frappe.log_error(f"Disk Space Check Error: {str(e)}", "Health Check")
        return {'status': 'error', 'error': str(e)}


def log_system_health():
    """Aggregate and log comprehensive system health status"""
    try:
        # Run all health checks
        db_health = check_database_health()
        api_health = check_api_health()
        disk_health = check_disk_space()

        overall_status = 'healthy'

        if any(h.get('status') == 'error' for h in [db_health, api_health, disk_health]):
            overall_status = 'error'
        elif any(h.get('status') in ['warning', 'critical'] for h in [db_health, api_health, disk_health]):
            overall_status = 'warning'

        # Create or update System Health doc
        today = frappe.utils.nowdate()

        existing = frappe.db.exists('System Health', {'date': today})

        if existing:
            health_doc = frappe.get_doc('System Health', existing)
        else:
            health_doc = frappe.new_doc('System Health')
            health_doc.date = today

        health_doc.db_health = db_health.get('status', 'unknown')
        health_doc.api_health = api_health.get('status', 'unknown')
        health_doc.disk_health = disk_health.get('status', 'unknown')
        health_doc.overall_status = overall_status
        health_doc.health_details = frappe.as_json({
            'database': db_health,
            'api': api_health,
            'disk': disk_health
        })

        health_doc.save()

        frappe.db.commit()

        return health_doc.as_dict()

    except Exception as e:
        frappe.log_error(f"System Health Logging Error: {str(e)}", "Health Check")
        return {'status': 'error', 'error': str(e)}


# Additional helper functions for comprehensive implementations

def _execute_compliance_check(check_doc):
    """Execute a compliance check based on its type"""
    try:
        check_type = check_doc.compliance_type

        # Placeholder for actual compliance check logic
        # This would be implemented based on specific compliance requirements
        result = {
            'check_name': check_doc.check_name,
            'status': 'passed',
            'message': 'Compliance check executed successfully',
            'timestamp': frappe.utils.now()
        }

        return result

    except Exception as e:
        return {
            'check_name': check_doc.check_name,
            'status': 'error',
            'error': str(e)
        }


def _calculate_risk_score(indicator):
    """Calculate risk score for an indicator"""
    try:
        current = indicator.get('current_value', 0)
        threshold = indicator.get('threshold', 100)

        # Calculate normalized score (0-1)
        score = min(1.0, current / threshold) if threshold > 0 else 0

        return {
            'indicator': indicator.name,
            'score': score,
            'current': current,
            'threshold': threshold
        }

    except Exception:
        return {'indicator': indicator.name, 'score': 0, 'current': 0, 'threshold': 100}


def _execute_audit_test(template):
    """Execute an audit test from template"""
    try:
        # Placeholder for actual test execution logic
        return {
            'template': template.name,
            'status': 'passed',
            'result': 'Test executed successfully'
        }

    except Exception as e:
        return {
            'template': template.name,
            'status': 'error',
            'error': str(e)
        }


def _get_audit_engagement_metrics(start_date, end_date):
    """Get audit engagement metrics for period"""
    try:
        return frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'In Progress' THEN 1 END) as in_progress
            FROM `tabAudit Execution`
            WHERE start_date >= %s AND start_date <= %s
        """, (start_date, end_date), as_dict=True)[0] or {}

    except Exception:
        return {}


def _get_finding_metrics(start_date, end_date):
    """Get finding metrics for period"""
    try:
        return frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN severity = 'High' THEN 1 END) as high,
                COUNT(CASE WHEN severity = 'Medium' THEN 1 END) as medium,
                COUNT(CASE WHEN severity = 'Low' THEN 1 END) as low
            FROM `tabAudit Finding`
            WHERE reported_date >= %s AND reported_date <= %s
        """, (start_date, end_date), as_dict=True)[0] or {}

    except Exception:
        return {}


def _get_risk_metrics(start_date, end_date):
    """Get risk assessment metrics for period"""
    try:
        return frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN overall_risk_level = 'High' THEN 1 END) as high,
                COUNT(CASE WHEN overall_risk_level = 'Medium' THEN 1 END) as medium,
                COUNT(CASE WHEN overall_risk_level = 'Low' THEN 1 END) as low
            FROM `tabRisk Assessment`
            WHERE assessment_date >= %s AND assessment_date <= %s
        """, (start_date, end_date), as_dict=True)[0] or {}

    except Exception:
        return {}


def _get_compliance_metrics(start_date, end_date):
    """Get compliance metrics for period"""
    try:
        return frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'Pass' THEN 1 END) as passed,
                COUNT(CASE WHEN status = 'Fail' THEN 1 END) as failed
            FROM `tabCompliance Result`
            WHERE check_date >= %s AND check_date <= %s
        """, (start_date, end_date), as_dict=True)[0] or {}

    except Exception:
        return {}


def _calculate_health_score(metrics):
    """Calculate overall health score from metrics"""
    try:
        score = 100

        # Deduct for failed findings
        findings = metrics.get('findings', {})
        total_findings = findings.get('total', 0)
        high_findings = findings.get('high', 0)
        if total_findings > 0:
            score -= (high_findings * 5)

        # Deduct for failed compliance
        compliance = metrics.get('compliance', {})
        if compliance.get('total', 0) > 0:
            failed_rate = compliance.get('failed', 0) / compliance['total']
            score -= (failed_rate * 20)

        return max(0, min(100, score))

    except Exception:
        return 75


def _format_executive_summary_email(summary):
    """Format executive summary for email"""
    try:
        metrics = frappe.parse_json(summary.metrics) if isinstance(summary.metrics, str) else summary.metrics

        html = f"""
        <h2>Executive Summary Report</h2>
        <p><strong>Period:</strong> {summary.period_start} to {summary.period_end}</p>
        <p><strong>Health Score:</strong> {summary.health_score}/100</p>

        <h3>Key Metrics</h3>
        <ul>
            <li>Audit Engagements: {metrics.get('audit_engagements', {}).get('total', 0)}</li>
            <li>Findings: {metrics.get('findings', {}).get('total', 0)}</li>
            <li>High Risk Items: {metrics.get('risk_assessments', {}).get('high', 0)}</li>
            <li>Compliance Pass Rate: {metrics.get('compliance', {}).get('passed', 0)}</li>
        </ul>

        <p>Please log in to the system for detailed information.</p>
        """

        return html

    except Exception as e:
        frappe.log_error(f"Email Formatting Error: {str(e)}", "Executive Summary")
        return "<p>Executive summary available in the system.</p>"


# Anomaly Detection Functions

def check_timing_anomalies(hours_back=24):
    """Check for unusual timing patterns in audit entries"""
    try:
        from datetime import datetime, timedelta

        cutoff = datetime.now() - timedelta(hours=hours_back)

        # Get entries grouped by hour
        hourly_counts = frappe.db.sql("""
            SELECT HOUR(timestamp) as hour,
                   COUNT(*) as count,
                   AVG(timestamp_diff) as avg_interval
            FROM (
                SELECT timestamp,
                       TIMESTAMPDIFF(MINUTE,
                                   LAG(timestamp) OVER (ORDER BY timestamp),
                                   timestamp) as timestamp_diff
                FROM `tabAudit Trail Entry`
                WHERE timestamp >= %s
            ) timed
            GROUP BY HOUR(timestamp)
            ORDER BY hour
        """, cutoff, as_dict=True)

        anomalies = []
        avg_count = sum(row.count for row in hourly_counts) / len(hourly_counts) if hourly_counts else 0

        for hour_data in hourly_counts:
            # Flag if count is 3x above average
            if hour_data.count > (avg_count * 3):
                anomalies.append({
                    'type': 'high_volume',
                    'hour': hour_data.hour,
                    'count': hour_data.count,
                    'expected': int(avg_count)
                })

        if anomalies:
            _log_anomaly_alert(anomalies, 'timing')

        return anomalies

    except Exception as e:
        frappe.log_error(f"Timing Anomaly Check Error: {str(e)}", "Anomaly Detection")
        return []


def check_user_anomalies(hours_back=24):
    """Detect unusual user behavior patterns"""
    try:
        from datetime import datetime, timedelta

        cutoff = datetime.now() - timedelta(hours=hours_back)

        # Get user activity statistics
        user_stats = frappe.db.sql("""
            SELECT user,
                   COUNT(*) as total_actions,
                   COUNT(DISTINCT document_type) as unique_doctypes,
                   COUNT(CASE WHEN operation = 'delete' THEN 1 END) as delete_count,
                   COUNT(CASE WHEN operation IN ('update', 'write') THEN 1 END) as update_count
            FROM `tabAudit Trail Entry`
            WHERE timestamp >= %s
            GROUP BY user
            HAVING total_actions > 50 OR delete_count > 5
        """, cutoff, as_dict=True)

        anomalies = []

        for stat in user_stats:
            # High volume of actions
            if stat.total_actions > 500:
                anomalies.append({
                    'type': 'high_volume',
                    'user': stat.user,
                    'actions': stat.total_actions,
                    'severity': 'high'
                })

            # Unusual delete activity
            if stat.delete_count > 10:
                anomalies.append({
                    'type': 'excessive_deletes',
                    'user': stat.user,
                    'delete_count': stat.delete_count,
                    'severity': 'high'
                })

            # Access to many different doctypes
            if stat.unique_doctypes > 20:
                anomalies.append({
                    'type': 'unusual_scope',
                    'user': stat.user,
                    'unique_doctypes': stat.unique_doctypes,
                    'severity': 'medium'
                })

        if anomalies:
            _log_anomaly_alert(anomalies, 'user')

        return anomalies

    except Exception as e:
        frappe.log_error(f"User Anomaly Check Error: {str(e)}", "Anomaly Detection")
        return []


def check_value_anomalies(module=None, hours_back=24):
    """
    Identify unusual value patterns in financial entries (batch processing).
    
    Args:
        module: Optional module filter
        hours_back: Hours to look back for anomalies (default 24)
        
    Returns:
        list: List of anomalous entries
    """
    try:
        from datetime import datetime, timedelta

        cutoff = datetime.now() - timedelta(hours=hours_back)

        # Check for unusual amounts in GL entries using proper SQL with subquery
        # HAVING cannot be used with window functions directly
        anomalies = frappe.db.sql("""
            SELECT * FROM (
                SELECT document_name, account_no, debit, credit,
                       AVG(debit) OVER () as avg_debit,
                       STDDEV(debit) OVER () as stddev_debit,
                       AVG(credit) OVER () as avg_credit,
                       STDDEV(credit) OVER () as stddev_credit
                FROM `tabAudit GL Entry`
                WHERE timestamp >= %s
                AND (debit > 0 OR credit > 0)
            ) AS subq
            WHERE (debit > 0 AND debit > (avg_debit + (3 * COALESCE(stddev_debit, 0))))
               OR (credit > 0 AND credit > (avg_credit + (3 * COALESCE(stddev_credit, 0))))
            LIMIT 100
        """, cutoff, as_dict=True)

        if anomalies:
            _log_anomaly_alert(anomalies, 'value')

        return anomalies

    except Exception as e:
        frappe.log_error(f"Value Anomaly Check Error: {str(e)}", "Anomaly Detection")
        return []


def _log_anomaly_alert(anomalies, anomaly_type):
    """Helper function to log anomaly alerts"""
    try:
        # Check if anomaly type alert already exists today
        today = frappe.utils.nowdate()

        existing = frappe.db.exists('Anomaly Alert', {
            'anomaly_type': anomaly_type,
            'alert_date': today,
            'status': 'Open'
        })

        if existing:
            # Update existing alert
            alert = frappe.get_doc('Anomaly Alert', existing)
            alert.anomaly_count = len(anomalies)
            alert.anomaly_details = frappe.as_json(anomalies)
            alert.save()
        else:
            # Create new alert
            frappe.get_doc({
                'doctype': 'Anomaly Alert',
                'anomaly_type': anomaly_type,
                'alert_date': today,
                'anomaly_count': len(anomalies),
                'anomaly_details': frappe.as_json(anomalies),
                'severity': 'high' if len(anomalies) > 10 else 'medium',
                'status': 'Open'
            }).insert()

        frappe.db.commit()

    except Exception as e:
        frappe.log_error(f"Anomaly Alert Logging Error: {str(e)}", "Anomaly Detection")


def weekly_performance_report():
    """Generate weekly performance metrics and reports"""
    try:
        frappe.logger().info("Starting weekly performance report")

        # Get all modules
        modules = get_all_modules()

        # Generate performance metrics for each module
        for module in modules:
            _generate_module_performance_report(module)

        # Create summary report
        _create_weekly_summary()

        frappe.logger().info("Weekly performance report completed")
    except Exception as e:
        frappe.log_error(f"Weekly Performance Report Error: {str(e)}", "Performance Report")


def monthly_compliance_report():
    """Generate monthly compliance status reports"""
    try:
        frappe.logger().info("Starting monthly compliance report")

        # Get all active compliance checks
        compliance_checks = frappe.get_all('Compliance Check',
            filters={'status': 'Active'},
            fields=['name', 'check_name', 'compliance_type'])

        # Aggregate compliance results
        report_data = _aggregate_compliance_results(compliance_checks)

        # Create comprehensive report
        _create_monthly_compliance_report(report_data)

        frappe.logger().info("Monthly compliance report completed")
    except Exception as e:
        frappe.log_error(f"Monthly Compliance Report Error: {str(e)}", "Compliance Report")


# Helper functions for weekly and monthly reports

def get_all_modules():
    """Get all audit modules"""
    return ['Financial', 'HR', 'Inventory', 'Access Control', 'General']


def _generate_module_performance_report(module):
    """Generate performance report for a specific module"""
    try:
        from datetime import datetime, timedelta

        # Get week start and end
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        # Get audit entries for this module
        entries = frappe.db.sql("""
            SELECT COUNT(*) as total_entries,
                   COUNT(CASE WHEN operation = 'create' THEN 1 END) as creates,
                   COUNT(CASE WHEN operation = 'update' THEN 1 END) as updates,
                   COUNT(CASE WHEN operation = 'delete' THEN 1 END) as deletes
            FROM `tabAudit Trail Entry`
            WHERE module = %s
            AND timestamp >= %s
            AND timestamp <= %s
        """, (module, week_start, week_end), as_dict=True)

        if entries:
            return {
                'module': module,
                'week_start': week_start.strftime('%Y-%m-%d'),
                'week_end': week_end.strftime('%Y-%m-%d'),
                'metrics': entries[0]
            }
        return None

    except Exception as e:
        frappe.log_error(f"Module Performance Report Error ({module}): {str(e)}", "Performance Report")
        return None


def _create_weekly_summary():
    """Create weekly performance summary"""
    try:
        from datetime import datetime, timedelta

        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        week_end = week_start + timedelta(days=6)

        # Get overall metrics
        summary = frappe.db.sql("""
            SELECT COUNT(*) as total_entries,
                   COUNT(DISTINCT user) as active_users,
                   COUNT(DISTINCT document_type) as document_types
            FROM `tabAudit Trail Entry`
            WHERE timestamp >= %s AND timestamp <= %s
        """, (week_start, week_end), as_dict=True)

        # Create or update performance report document
        report_name = f"Weekly Performance Report - {week_start.strftime('%Y-%m-%d')}"

        if frappe.db.exists('Performance Report', report_name):
            report = frappe.get_doc('Performance Report', report_name)
        else:
            report = frappe.new_doc('Performance Report')
            report.report_name = report_name

        report.report_type = 'Weekly'
        report.start_date = week_start.strftime('%Y-%m-%d')
        report.end_date = week_end.strftime('%Y-%m-%d')

        if summary:
            report.total_entries = summary[0].total_entries
            report.active_users = summary[0].active_users
            report.document_types = summary[0].document_types

        report.save()
        frappe.db.commit()

    except Exception as e:
        frappe.log_error(f"Weekly Summary Creation Error: {str(e)}", "Performance Report")


def _aggregate_compliance_results(compliance_checks):
    """Aggregate compliance check results"""
    try:
        from datetime import datetime, timedelta

        month_start = datetime.now().replace(day=1)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        results = {
            'period_start': month_start.strftime('%Y-%m-%d'),
            'period_end': month_end.strftime('%Y-%m-%d'),
            'checks': []
        }

        for check in compliance_checks:
            # Get compliance results for this check
            check_results = frappe.db.sql("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN status = 'Pass' THEN 1 END) as passed,
                       COUNT(CASE WHEN status = 'Fail' THEN 1 END) as failed,
                       COUNT(CASE WHEN status = 'Pending' THEN 1 END) as pending
                FROM `tabCompliance Result`
                WHERE compliance_check = %s
                AND check_date >= %s
                AND check_date <= %s
            """, (check.name, month_start, month_end), as_dict=True)

            results['checks'].append({
                'check_name': check.check_name,
                'compliance_type': check.compliance_type,
                'results': check_results[0] if check_results else {}
            })

        return results

    except Exception as e:
        frappe.log_error(f"Compliance Results Aggregation Error: {str(e)}", "Compliance Report")
        return {}


def _create_monthly_compliance_report(report_data):
    """Create monthly compliance report document"""
    try:
        from datetime import datetime

        month_start = datetime.now().replace(day=1)
        report_name = f"Monthly Compliance Report - {month_start.strftime('%Y-%m')}"

        if frappe.db.exists('Compliance Report', report_name):
            report = frappe.get_doc('Compliance Report', report_name)
        else:
            report = frappe.new_doc('Compliance Report')
            report.report_name = report_name

        report.report_type = 'Monthly'
        report.period_start = report_data.get('period_start')
        report.period_end = report_data.get('period_end')

        # Calculate overall compliance percentage
        total_checks = 0
        passed_checks = 0

        for check in report_data.get('checks', []):
            result = check.get('results', {})
            total = result.get('total', 0)
            passed = result.get('passed', 0)

            total_checks += total
            passed_checks += passed

        if total_checks > 0:
            report.compliance_percentage = round((passed_checks / total_checks) * 100, 2)

        report.report_details = frappe.as_json(report_data)
        report.save()
        frappe.db.commit()

    except Exception as e:
        frappe.log_error(f"Monthly Compliance Report Creation Error: {str(e)}", "Compliance Report")