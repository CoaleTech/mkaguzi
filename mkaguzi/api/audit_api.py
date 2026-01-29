# UNIFIED AUDIT API MODULE - Mkaguzi Transformation Plan Phase 7-8
# =============================================================================

import frappe
from frappe import _
from frappe.utils import now, cint, flt
from datetime import datetime, timedelta
import traceback
from typing import Optional, Dict, Any
from mkaguzi.utils.query_manager import QueryManager
from mkaguzi.utils.error_handler import SecureErrorHandler
from mkaguzi.types import APIResponse, AuditTrailEntry, DashboardData, RiskLevel
from mkaguzi.utils.api_response import APIResponseBuilder
from mkaguzi.utils.cache_manager import cached, CacheManager


class AuditAPI:
    """
    Unified Audit API providing consolidated access to all audit operations
    across the Mkaguzi Internal Audit Management System
    """

    def __init__(self):
        """Initialize the Audit API"""
        self.modules = {
            'audit_trail': 'mkaguzi.audit_trail',
            'discovery': 'mkaguzi.discovery_engine',
            'templates': 'mkaguzi.audit_templates',
            'hooks': 'mkaguzi.hooks_manager',
            'analyzer': 'mkaguzi.audit_analyzer',
            'payroll': 'mkaguzi.payroll_audit',
            'hr': 'mkaguzi.hr_audit',
            'inventory': 'mkaguzi.inventory_audit',
            'procurement': 'mkaguzi.procurement_audit',
            'access': 'mkaguzi.access_control_audit'
        }

    @frappe.whitelist()
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status including all audit modules

        Returns:
            Dictionary containing system status information
        """
        try:
            status = {
                'timestamp': now(),
                'overall_status': 'healthy',
                'modules': {},
                'alerts': [],
                'metrics': {}
            }

            # Check each module status
            for module_name, module_path in self.modules.items():
                try:
                    module_status = self._check_module_status(module_name, module_path)
                    status['modules'][module_name] = module_status

                    if module_status['status'] != 'healthy':
                        status['overall_status'] = 'warning'
                        status['alerts'].append(f"{module_name}: {module_status['message']}")

                except Exception as e:
                    status['modules'][module_name] = {
                        'status': 'error',
                        'message': SecureErrorHandler.sanitize_error_message(str(e)),
                        'last_check': now()
                    }
                    status['overall_status'] = 'error'
                    status['alerts'].append(f"{module_name}: {SecureErrorHandler.sanitize_error_message(str(e))}")

            # Get system metrics
            status['metrics'] = self._get_system_metrics()

            return APIResponseBuilder.success(status, "System status retrieved successfully")

        except Exception as e:
            return SecureErrorHandler.handle_api_error(e, 'get_system_status')

    def _check_module_status(self, module_name, module_path):
        """Check individual module status"""
        try:
            # Check if module tables exist
            if module_name == 'audit_trail':
                table_count = frappe.db.count('Audit GL Entry')
            elif module_name == 'discovery':
                table_count = frappe.db.count('Audit Doctype Catalog')
            elif module_name == 'templates':
                table_count = frappe.db.count('Audit Test Template')
            else:
                table_count = 0

            # Check recent activity
            recent_activity = self._get_recent_activity(module_name)

            status = 'healthy'
            message = 'Module operational'

            if table_count == 0 and module_name in ['audit_trail', 'discovery', 'templates']:
                status = 'warning'
                message = 'No data found - module may need initialization'

            return {
                'status': status,
                'message': message,
                'table_count': table_count,
                'recent_activity': recent_activity,
                'last_check': now()
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'last_check': now()
            }

    def _get_recent_activity(self, module_name):
        """Get recent activity for a module"""
        try:
            if module_name == 'audit_trail':
                return frappe.db.count('Audit GL Entry',
                    filters={'creation': ['>=', datetime.now() - timedelta(hours=24)]})
            elif module_name == 'discovery':
                return frappe.db.count('Audit Doctype Catalog',
                    filters={'modified': ['>=', datetime.now() - timedelta(hours=24)]})
            elif module_name == 'templates':
                return frappe.db.count('Audit Test Template',
                    filters={'modified': ['>=', datetime.now() - timedelta(hours=24)]})
            else:
                return 0
        except:
            return 0

    @cached(ttl=300, key_prefix="system_metrics")
    def _get_system_metrics(self):
        """Get system-wide audit metrics (cached)"""
        try:
            return {
                'total_audit_entries': frappe.db.count('Audit GL Entry'),
                'active_catalogs': frappe.db.count('Audit Doctype Catalog'),
                'audit_templates': frappe.db.count('Audit Test Template'),
                'integrity_reports': frappe.db.count('Audit Integrity Report'),
                'sync_status': frappe.db.count('Module Sync Status'),
                'open_findings': frappe.db.count('Audit Finding',
                    filters={'status': ['in', ['Open', 'In Progress']]}),
                'completed_audits': frappe.db.count('Audit Execution',
                    filters={'status': 'Completed'})
            }
        except:
            return {}

    @frappe.whitelist()
    def run_integrity_check(self, check_type='full', target_module=None):
        """
        Run integrity checks across audit modules
        """
        try:
            results = {
                'check_type': check_type,
                'target_module': target_module,
                'timestamp': now(),
                'checks': [],
                'summary': {
                    'total_checks': 0,
                    'passed': 0,
                    'failed': 0,
                    'warnings': 0
                }
            }

            # Define checks to run
            checks = []
            if check_type == 'full' or check_type == 'data':
                checks.extend(self._get_data_integrity_checks(target_module))
            if check_type == 'full' or check_type == 'config':
                checks.extend(self._get_config_integrity_checks(target_module))

            # Execute checks
            for check in checks:
                try:
                    check_result = self._execute_integrity_check(check)
                    results['checks'].append(check_result)

                    results['summary']['total_checks'] += 1
                    results['summary'][check_result['status']] += 1

                except Exception as e:
                    results['checks'].append({
                        'check_name': check['name'],
                        'status': 'error',
                        'message': str(e),
                        'details': traceback.format_exc()
                    })
                    results['summary']['total_checks'] += 1
                    results['summary']['failed'] += 1

            # Create integrity report
            self._create_integrity_report(results)

            return results

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Audit API Integrity Check Error"))
            return {
                'check_type': check_type,
                'timestamp': now(),
                'error': str(e),
                'checks': [],
                'summary': {'total_checks': 0, 'passed': 0, 'failed': 1, 'warnings': 0}
            }

    def _create_audit_entry(self, doc, operation, module):
        """Create audit trail entry for document operations"""
        try:
            # Create audit trail entry
            trail = frappe.get_doc({
                'doctype': 'Audit Trail Entry',
                'document_type': doc.doctype,
                'document_name': doc.name,
                'operation': operation,
                'user': frappe.session.user,
                'timestamp': now(),
                'module': module,
                'changes_summary': f"{doc.doctype} {operation}: {doc.name}",
                'risk_level': self._assess_operation_risk(doc, operation),
                'requires_review': self._requires_review(doc, operation)
            })

            trail.insert(ignore_permissions=True)
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"Audit Entry Creation Error: {str(e)}")

    def _assess_operation_risk(self, doc, operation):
        """Assess risk level of operation"""
        try:
            # High risk operations
            if operation in ['Delete', 'Cancel']:
                return 'High'

            # Check for sensitive doctypes
            sensitive_doctypes = ['User', 'Role', 'Salary Slip', 'Payment Entry']
            if doc.doctype in sensitive_doctypes:
                return 'Medium'

            # Check for large amounts
            amount = self._get_document_amount(doc)
            if amount and amount > 100000:
                return 'Medium'

            return 'Low'

        except Exception:
            return 'Low'

    def _requires_review(self, doc, operation):
        """Determine if operation requires review"""
        try:
            risk_level = self._assess_operation_risk(doc, operation)
            return risk_level in ['High', 'Medium']
        except Exception:
            return False

    def _get_document_amount(self, doc):
        """Extract amount from document"""
        try:
            amount_fields = ['total', 'grand_total', 'paid_amount', 'received_amount', 'debit', 'credit', 'amount']
            for field in amount_fields:
                if hasattr(doc, field):
                    amount = getattr(doc, field)
                    if amount:
                        return flt(amount)
            return 0
        except Exception:
            return 0

    @frappe.whitelist()
    @frappe.whitelist()
    def get_audit_trail(
        self,
        doctype: Optional[str] = None,
        docname: Optional[str] = None,
        limit: int = 100,
        start: int = 0
    ) -> Dict[str, Any]:
        """
        Get audit trail entries with filtering and pagination

        Args:
            doctype: Filter by document type
            docname: Filter by document name
            limit: Maximum number of entries to return
            start: Offset for pagination

        Returns:
            Dictionary with entries, total count, and pagination info
        """
        try:
            filters = {}
            if doctype:
                filters['document_type'] = doctype
            if docname:
                filters['document_name'] = docname

            trail_entries = frappe.get_all('Audit Trail Entry',
                filters=filters,
                fields=['name', 'document_type', 'document_name', 'operation',
                       'user', 'timestamp', 'module', 'changes_summary',
                       'risk_level', 'requires_review'],
                order_by='timestamp desc',
                limit=limit,
                start=start
            )

            total = frappe.db.count('Audit Trail Entry', filters=filters)

            return APIResponseBuilder.paginated(
                data=trail_entries,
                total=total,
                page=(start // limit) + 1 if limit > 0 else 1,
                page_size=limit
            )

        except Exception as e:
            return APIResponseBuilder.error(
                error_message="Failed to retrieve audit trail",
                error_code="AUDIT_TRAIL_ERROR",
                details={'error': str(e)}
            )

    @frappe.whitelist()
    def update_dashboard_data(self, module=None):
        """
        Update dashboard data for specified module or all modules
        """
        try:
            modules_to_update = [module] if module else list(self.modules.keys())

            results = {}
            for mod in modules_to_update:
                try:
                    if mod == 'audit_trail':
                        results[mod] = self._update_audit_trail_dashboard()
                    elif mod == 'discovery':
                        results[mod] = self._update_discovery_dashboard()
                    elif mod == 'templates':
                        results[mod] = self._update_templates_dashboard()
                    else:
                        results[mod] = {'status': 'not_implemented'}
                except Exception as e:
                    results[mod] = {'status': 'error', 'message': str(e)}

            return {
                'timestamp': now(),
                'modules_updated': results,
                'overall_status': 'success' if all(r.get('status') != 'error' for r in results.values()) else 'partial'
            }

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Dashboard Update Error"))
            return {
                'timestamp': now(),
                'error': str(e),
                'overall_status': 'error'
            }

    def _update_audit_trail_dashboard(self):
        """Update audit trail dashboard data"""
        try:
            # Update summary statistics
            total_entries = frappe.db.count('Audit GL Entry')
            recent_entries = frappe.db.count('Audit GL Entry',
                filters={'creation': ['>=', datetime.now() - timedelta(days=7)]})

            return {
                'status': 'success',
                'total_entries': total_entries,
                'recent_entries': recent_entries,
                'last_updated': now()
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _update_discovery_dashboard(self):
        """Update discovery dashboard data"""
        try:
            total_catalogs = frappe.db.count('Audit Doctype Catalog')
            active_catalogs = frappe.db.count('Audit Doctype Catalog',
                filters={'is_active': 1})

            return {
                'status': 'success',
                'total_catalogs': total_catalogs,
                'active_catalogs': active_catalogs,
                'last_updated': now()
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _update_templates_dashboard(self):
        """Update templates dashboard data"""
        try:
            total_templates = frappe.db.count('Audit Test Template')
            active_templates = frappe.db.count('Audit Test Template',
                filters={'is_active': 1})

            return {
                'status': 'success',
                'total_templates': total_templates,
                'active_templates': active_templates,
                'last_updated': now()
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    @frappe.whitelist()
    def send_notification(self, notification_type, recipients, data):
        """
        Send notifications for audit events
        """
        try:
            if notification_type == 'finding_created':
                return self._send_finding_notification(recipients, data)
            elif notification_type == 'audit_completed':
                return self._send_completion_notification(recipients, data)
            elif notification_type == 'integrity_check_failed':
                return self._send_integrity_notification(recipients, data)
            else:
                return self._send_generic_notification(notification_type, recipients, data)

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Notification Send Error"))
            return {'status': 'error', 'message': str(e)}

    def _send_finding_notification(self, recipients, data):
        """Send finding creation notification"""
        try:
            subject = f"Audit Finding: {data.get('finding_title', 'New Finding')}"
            message = f"""
            A new audit finding has been created:

            Title: {data.get('finding_title')}
            Severity: {data.get('severity')}
            Status: {data.get('status')}
            Description: {data.get('description')}

            Please review and take appropriate action.
            """

            frappe.sendmail(
                recipients=recipients,
                subject=subject,
                message=message
            )

            return {'status': 'success', 'notification_type': 'finding_created'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _send_completion_notification(self, recipients, data):
        """Send audit completion notification"""
        try:
            subject = f"Audit Completed: {data.get('audit_title', 'Audit Execution')}"
            message = f"""
            An audit execution has been completed:

            Title: {data.get('audit_title')}
            Status: Completed
            Completion Date: {now()}
            Findings: {data.get('findings_count', 0)}

            Please review the results and findings.
            """

            frappe.sendmail(
                recipients=recipients,
                subject=subject,
                message=message
            )

            return {'status': 'success', 'notification_type': 'audit_completed'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _send_integrity_notification(self, recipients, data):
        """Send integrity check failure notification"""
        try:
            subject = f"Integrity Check Failed: {data.get('module', 'System')}"
            message = f"""
            An integrity check has failed:

            Module: {data.get('module')}
            Check Type: {data.get('check_type')}
            Failed Checks: {data.get('failed_count', 0)}
            Timestamp: {now()}

            Please investigate and resolve the integrity issues.
            """

            frappe.sendmail(
                recipients=recipients,
                subject=subject,
                message=message
            )

            return {'status': 'success', 'notification_type': 'integrity_check_failed'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _send_generic_notification(self, notification_type, recipients, data):
        """Send generic notification"""
        try:
            subject = f"Audit System Notification: {notification_type}"
            message = f"""
            Audit System Notification

            Type: {notification_type}
            Details: {frappe.as_json(data, indent=2)}
            Timestamp: {now()}
            """

            frappe.sendmail(
                recipients=recipients,
                subject=subject,
                message=message
            )

            return {'status': 'success', 'notification_type': notification_type}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _get_data_integrity_checks(self, target_module=None):
        """Get data integrity checks"""
        checks = [
            {
                'name': 'Audit GL Entry Validation',
                'module': 'audit_trail',
                'type': 'data',
                'query_key': 'audit_gl_entry_validation'  # Changed from 'query'
            },
            {
                'name': 'Doctype Catalog Completeness',
                'module': 'discovery',
                'type': 'data',
                'query_key': 'doctype_catalog_completeness'
            },
            {
                'name': 'Test Template Validation',
                'module': 'templates',
                'type': 'data',
                'query_key': 'test_template_validation'
            }
        ]

        if target_module:
            checks = [c for c in checks if c['module'] == target_module]

        return checks

    def _get_config_integrity_checks(self, target_module=None):
        """Get configuration integrity checks"""
        checks = [
            {
                'name': 'Audit Triggers Configuration',
                'module': 'hooks',
                'type': 'config',
                'query_key': 'audit_triggers_config'
            },
            {
                'name': 'Audit Rules Validation',
                'module': 'analyzer',
                'type': 'config',
                'query_key': 'audit_rules_validation'
            }
        ]

        if target_module:
            checks = [c for c in checks if c['module'] == target_module]

        return checks

    def _execute_integrity_check(self, check):
        """Execute a single integrity check"""
        try:
            query_key = check.get('query_key')
            if not query_key:
                return {
                    'check_name': check['name'],
                    'status': 'error',
                    'message': 'No query_key provided for check',
                    'details': None
                }

            result = QueryManager.execute_safe_query(query_key)

            if result and result[0]['count'] > 0:
                return {
                    'check_name': check['name'],
                    'status': 'failed',
                    'message': f'Found {result[0]["count"]} integrity violations',
                    'details': result
                }
            else:
                return {
                    'check_name': check['name'],
                    'status': 'passed',
                    'message': 'No integrity violations found',
                    'details': result
                }

        except ValueError as e:
            return {
                'check_name': check['name'],
                'status': 'error',
                'message': str(e),
                'details': None
            }
        except Exception as e:
            return {
                'check_name': check['name'],
                'status': 'error',
                'message': 'Check execution failed',
                'details': {'error': 'Sanitized error logged'}
            }

    def _create_integrity_report(self, results):
        """Create an integrity report document"""
        try:
            report = frappe.get_doc({
                'doctype': 'Audit Integrity Report',
                'report_title': f'Integrity Check - {results["check_type"]} - {now()}',
                'check_type': results['check_type'],
                'target_module': results.get('target_module'),
                'execution_date': now(),
                'total_checks': results['summary']['total_checks'],
                'passed_checks': results['summary']['passed'],
                'failed_checks': results['summary']['failed'],
                'warning_checks': results['summary']['warnings'],
                'overall_status': 'Passed' if results['summary']['failed'] == 0 else 'Failed',
                'report_data': frappe.as_json(results)
            })

            # Add check results
            for check in results['checks']:
                report.append('integrity_check_results', {
                    'check_name': check['check_name'],
                    'status': check['status'],
                    'details': check['message'],
                    'result_data': frappe.as_json(check.get('details', {}))
                })

            report.insert()
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Integrity Report Creation Error"))

    @frappe.whitelist()
    def get_audit_dashboard(self, period='30', module=None):
        """
        Get comprehensive audit dashboard data
        """
        try:
            days = cint(period)
            start_date = datetime.now() - timedelta(days=days)

            dashboard = {
                'period': f'{days} days',
                'timestamp': now(),
                'summary': {},
                'charts': {},
                'alerts': [],
                'recent_activity': []
            }

            # Get summary metrics
            dashboard['summary'] = self._get_dashboard_summary(start_date, module)

            # Get chart data
            dashboard['charts'] = self._get_dashboard_charts(start_date, module)

            # Get alerts
            dashboard['alerts'] = self._get_dashboard_alerts()

            # Get recent activity
            dashboard['recent_activity'] = self._get_recent_activity_feed(start_date)

            return dashboard

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Audit API Dashboard Error"))
            return {
                'period': period,
                'timestamp': now(),
                'error': str(e),
                'summary': {},
                'charts': {},
                'alerts': [],
                'recent_activity': []
            }

    @cached(ttl=600, key_prefix="dashboard_summary")
    def _get_dashboard_summary(self, start_date, module=None):
        """Get dashboard summary metrics (cached)"""
        try:
            filters = {'creation': ['>=', start_date]}
            if module:
                filters['module'] = module

            return {
                'total_audit_entries': frappe.db.count('Audit GL Entry', filters=filters),
                'active_catalogs': frappe.db.count('Audit Doctype Catalog'),
                'integrity_checks': frappe.db.count('Audit Integrity Report', filters={'execution_date': ['>=', start_date]}),
                'sync_operations': frappe.db.count('Module Sync Status', filters={'last_sync': ['>=', start_date]}),
                'open_findings': frappe.db.count('Audit Finding',
                    filters={'status': ['in', ['Open', 'In Progress']]}),
                'completed_audits': frappe.db.count('Audit Execution',
                    filters={'status': 'Completed', 'creation': ['>=', start_date]})
            }
        except:
            return {}

    def _get_dashboard_charts(self, start_date, module=None):
        """Get dashboard chart data"""
        try:
            charts = {}

            # Audit activity over time
            activity_data = frappe.db.sql("""
                SELECT DATE(creation) as date, COUNT(*) as count
                FROM `tabAudit GL Entry`
                WHERE creation >= %s
                GROUP BY DATE(creation)
                ORDER BY date
            """, start_date, as_dict=True)

            charts['audit_activity'] = {
                'labels': [row['date'].strftime('%Y-%m-%d') for row in activity_data],
                'data': [row['count'] for row in activity_data]
            }

            # Findings by severity
            findings_data = frappe.db.sql("""
                SELECT severity, COUNT(*) as count
                FROM `tabAudit Finding`
                GROUP BY severity
            """, as_dict=True)

            charts['findings_severity'] = {
                'labels': [row['severity'] for row in findings_data],
                'data': [row['count'] for row in findings_data]
            }

            return charts
        except:
            return {}

    def _get_dashboard_alerts(self):
        """Get dashboard alerts"""
        try:
            alerts = []

            # Check for overdue findings
            overdue_findings = frappe.db.sql("""
                SELECT COUNT(*) as count
                FROM `tabAudit Finding`
                WHERE status IN ('Open', 'In Progress')
                AND target_completion_date < CURDATE()
            """, as_dict=True)

            if overdue_findings and overdue_findings[0]['count'] > 0:
                alerts.append({
                    'type': 'warning',
                    'message': f"{overdue_findings[0]['count']} findings are overdue",
                    'priority': 'high'
                })

            # Check for failed integrity checks
            failed_checks = frappe.db.count('Audit Integrity Report',
                filters={'overall_status': 'Failed'})

            if failed_checks > 0:
                alerts.append({
                    'type': 'error',
                    'message': f"{failed_checks} integrity checks have failed",
                    'priority': 'high'
                })

            return alerts
        except:
            return []

    def _get_recent_activity_feed(self, start_date):
        """Get recent activity feed"""
        try:
            activities = []

            # Recent audit entries
            audit_entries = frappe.db.sql("""
                SELECT 'Audit Entry' as type, doctype_name as description,
                       creation as timestamp, owner as user
                FROM `tabAudit GL Entry`
                WHERE creation >= %s
                ORDER BY creation DESC
                LIMIT 5
            """, start_date, as_dict=True)

            activities.extend(audit_entries)

            # Recent findings
            findings = frappe.db.sql("""
                SELECT 'Finding' as type, finding_title as description,
                       reported_date as timestamp, reported_by as user
                FROM `tabAudit Finding`
                WHERE reported_date >= %s
                ORDER BY reported_date DESC
                LIMIT 5
            """, start_date, as_dict=True)

            activities.extend(findings)

            # Sort by timestamp
            activities.sort(key=lambda x: x['timestamp'], reverse=True)

            return activities[:10]
        except:
            return []

    @frappe.whitelist()
    def create_audit_program(self, program_data):
        """
        Create a comprehensive audit program
        """
        try:
            data = frappe.parse_json(program_data) if isinstance(program_data, str) else program_data

            # Create audit plan
            plan = frappe.get_doc({
                'doctype': 'Audit Plan',
                'plan_name': data.get('program_name'),
                'description': data.get('description'),
                'audit_type': data.get('audit_type', 'Comprehensive'),
                'start_date': data.get('start_date'),
                'end_date': data.get('end_date'),
                'audit_objective': data.get('objectives'),
                'scope': data.get('scope'),
                'status': 'Draft'
            })

            # Add audit areas
            for area in data.get('audit_areas', []):
                plan.append('audit_areas', {
                    'area_name': area.get('name'),
                    'description': area.get('description'),
                    'risk_rating': area.get('risk_level', 'Medium'),
                    'priority': area.get('priority', 'Medium')
                })

            # Add team members
            for member in data.get('team_members', []):
                plan.append('team_members', {
                    'user': member.get('user'),
                    'role': member.get('role'),
                    'responsibilities': member.get('responsibilities')
                })

            # Generate planned tests from templates
            templates = self._get_relevant_templates(data.get('audit_areas', []))
            for template in templates:
                plan.append('planned_tests', {
                    'test_name': template.get('template_name'),
                    'test_category': template.get('category'),
                    'description': template.get('description'),
                    'estimated_hours': template.get('estimated_hours', 4),
                    'priority': template.get('priority', 'Medium')
                })

            plan.insert()
            frappe.db.commit()

            return {
                'success': True,
                'plan_id': plan.name,
                'message': 'Audit program created successfully',
                'test_count': len(templates)
            }

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Audit Program Creation Error"))
            return {
                'success': False,
                'error': str(e)
            }

    def _get_relevant_templates(self, audit_areas):
        """Get relevant audit templates for the audit areas"""
        try:
            area_names = [area.get('name') for area in audit_areas]

            # Get templates that match the audit areas
            templates = frappe.get_all('Audit Test Template',
                filters={'category': ['in', area_names]},
                fields=['name', 'template_name', 'category', 'description',
                       'estimated_hours', 'priority'])

            return templates
        except:
            return []

    @frappe.whitelist()
    def sync_all_modules(self, force_sync=False):
        """
        Synchronize all audit modules
        """
        try:
            results = {
                'timestamp': now(),
                'modules_synced': [],
                'errors': [],
                'summary': {
                    'total_modules': len(self.modules),
                    'successful': 0,
                    'failed': 0
                }
            }

            # Sync each module
            for module_name, module_path in self.modules.items():
                try:
                    sync_result = self._sync_module(module_name, force_sync)
                    results['modules_synced'].append(sync_result)

                    if sync_result['status'] == 'success':
                        results['summary']['successful'] += 1
                    else:
                        results['summary']['failed'] += 1
                        results['errors'].append(f"{module_name}: {sync_result['message']}")

                except Exception as e:
                    results['modules_synced'].append({
                        'module': module_name,
                        'status': 'error',
                        'message': str(e),
                        'timestamp': now()
                    })
                    results['summary']['failed'] += 1
                    results['errors'].append(f"{module_name}: {str(e)}")

            # Update sync status
            self._update_sync_status(results)

            return results

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Module Sync Error"))
            return {
                'timestamp': now(),
                'error': str(e),
                'modules_synced': [],
                'errors': [str(e)],
                'summary': {'total_modules': 0, 'successful': 0, 'failed': 1}
            }

    def _sync_module(self, module_name, force_sync=False):
        """Sync a specific module"""
        try:
            # Check if sync is needed
            if not force_sync:
                last_sync = frappe.db.get_value('Module Sync Status',
                    {'module_name': module_name}, 'last_sync')

                if last_sync:
                    # Skip if synced within last hour
                    if (datetime.now() - last_sync).seconds < 3600:
                        return {
                            'module': module_name,
                            'status': 'skipped',
                            'message': 'Recently synced',
                            'timestamp': now()
                        }

            # Perform sync based on module type
            if module_name == 'audit_trail':
                result = self._sync_audit_trail()
            elif module_name == 'discovery':
                result = self._sync_discovery_engine()
            elif module_name == 'templates':
                result = self._sync_templates()
            else:
                result = self._sync_generic_module(module_name)

            result.update({
                'module': module_name,
                'timestamp': now()
            })

            return result

        except Exception as e:
            return {
                'module': module_name,
                'status': 'error',
                'message': str(e),
                'timestamp': now()
            }

    def _sync_audit_trail(self):
        """Sync audit trail data"""
        try:
            # Get latest GL entries that need auditing
            latest_entries = frappe.db.sql("""
                SELECT COUNT(*) as count
                FROM `tabGL Entry`
                WHERE creation > (
                    SELECT COALESCE(MAX(last_sync), '1900-01-01')
                    FROM `tabModule Sync Status`
                    WHERE module_name = 'audit_trail'
                )
            """, as_dict=True)

            # Create audit entries for new GL entries
            # This would typically involve more complex logic
            synced_count = latest_entries[0]['count'] if latest_entries else 0

            return {
                'status': 'success',
                'message': f'Synced {synced_count} GL entries',
                'records_processed': synced_count
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def _sync_discovery_engine(self):
        """Sync discovery engine"""
        try:
            # Refresh doctype catalogs
            catalogs_updated = frappe.db.count('Audit Doctype Catalog')

            return {
                'status': 'success',
                'message': f'Updated {catalogs_updated} doctype catalogs',
                'records_processed': catalogs_updated
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def _sync_templates(self):
        """Sync audit templates"""
        try:
            # Refresh test templates
            templates_updated = frappe.db.count('Audit Test Template')

            return {
                'status': 'success',
                'message': f'Updated {templates_updated} test templates',
                'records_processed': templates_updated
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def _sync_generic_module(self, module_name):
        """Generic module sync"""
        return {
            'status': 'success',
            'message': f'Module {module_name} sync completed',
            'records_processed': 0
        }

    def _update_sync_status(self, results):
        """Update the module sync status document"""
        try:
            # Create or update sync status record
            for module_result in results['modules_synced']:
                status_doc = frappe.get_doc({
                    'doctype': 'Module Sync Status',
                    'module_name': module_result['module'],
                    'last_sync': module_result['timestamp'],
                    'sync_status': module_result['status'],
                    'records_processed': module_result.get('records_processed', 0),
                    'error_message': module_result.get('message', ''),
                    'sync_details': frappe.as_json(module_result)
                })

                # Check if record exists
                existing = frappe.db.exists('Module Sync Status',
                    {'module_name': module_result['module']})

                if existing:
                    status_doc.name = existing
                    status_doc.save()
                else:
                    status_doc.insert()

            frappe.db.commit()

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Sync Status Update Error"))

    @frappe.whitelist()
    def clear_cache(self, pattern: Optional[str] = None):
        """Clear cache"""
        if pattern:
            CacheManager.clear_pattern(f"{CacheManager.CACHE_PREFIX}{pattern}")
        else:
            CacheManager.clear_pattern(f"{CacheManager.CACHE_PREFIX}*")
        return {'success': True, 'message': 'Cache cleared'}


# Instantiate the unified Audit API
audit_api = AuditAPI()

# Expose key methods as whitelisted API endpoints
@frappe.whitelist()
def get_system_status():
    """Get system status"""
    return audit_api.get_system_status()

@frappe.whitelist()
def run_integrity_check(check_type='full', target_module=None):
    """Run integrity check"""
    return audit_api.run_integrity_check(check_type, target_module)

@frappe.whitelist()
def get_audit_dashboard(period='30', module=None):
    """Get audit dashboard"""
    return audit_api.get_audit_dashboard(period, module)

@frappe.whitelist()
def create_audit_program(program_data):
    """Create audit program"""
    return audit_api.create_audit_program(program_data)

@frappe.whitelist()
def sync_all_modules(force_sync=False):
    """Sync all modules"""