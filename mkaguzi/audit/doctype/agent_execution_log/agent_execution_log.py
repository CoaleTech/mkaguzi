# Copyright (c) 2025, mkaguzi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import json
from datetime import datetime


class AgentExecutionLog(Document):
    """Agent Execution Log Document Controller"""

    def validate(self):
        """Validate the document before saving"""
        self.validate_dates()
        self.validate_status()
        self.calculate_duration()
        self.set_agent_name()
        self.calculate_test_summary()

    def before_save(self):
        """Actions before saving"""
        self.update_audit_fields()
        self.calculate_performance_metrics()

    def after_insert(self):
        """Actions after insertion"""
        frappe.publish_realtime(
            'agent_execution_started',
            {'agent_id': self.agent_id, 'status': self.status}
        )

    def on_update(self):
        """Actions on update"""
        if self.status in ['Completed', 'Failed', 'Cancelled', 'Timeout']:
            frappe.publish_realtime(
                'agent_execution_completed',
                {
                    'agent_id': self.agent_id,
                    'status': self.status,
                    'name': self.name
                }
            )

    def validate_dates(self):
        """Validate that end time is after start time"""
        if self.start_time and self.end_time:
            if self.end_time < self.start_time:
                frappe.throw(_("End Time cannot be before Start Time"))

    def validate_status(self):
        """Validate status transitions"""
        valid_statuses = ['Pending', 'Running', 'Completed', 'Failed', 'Cancelled', 'Timeout']

        if self.status not in valid_statuses:
            frappe.throw(_("Invalid Status. Must be one of: {0}").format(', '.join(valid_statuses)))

        # Validate retry count
        if self.retry_count > self.max_retries:
            frappe.throw(_("Retry count cannot exceed max retries"))

    def calculate_duration(self):
        """Calculate duration based on start and end time"""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            self.duration_seconds = duration.total_seconds()

    def set_agent_name(self):
        """Set agent name based on agent type"""
        if self.agent_type and not self.agent_name:
            agent_names = {
                'Financial': 'Financial Agent',
                'Risk': 'Risk Assessment Agent',
                'Compliance': 'Compliance Verification Agent',
                'Discovery': 'Discovery Agent',
                'Notification': 'Notification Agent'
            }
            self.agent_name = agent_names.get(self.agent_type, self.agent_type)

    def update_audit_fields(self):
        """Update audit trail fields"""
        if not self.created_by:
            self.created_by = frappe.session.user

        if not self.creation_date:
            self.creation_date = datetime.now()

        self.modified_by = frappe.session.user
        self.modified_date = datetime.now()

    def calculate_performance_metrics(self):
        """Calculate performance metrics"""
        if self.records_processed and self.duration_seconds and self.duration_seconds > 0:
            self.records_per_second = round(self.records_processed / self.duration_seconds, 2)

    def mark_as_running(self):
        """Mark the execution as running"""
        self.status = 'Running'
        self.start_time = datetime.now()
        self.save()

    def mark_as_completed(self, result_data=None, findings=None):
        """Mark the execution as completed"""
        self.status = 'Completed'
        self.end_time = datetime.now()
        self.calculate_duration()

        if result_data:
            self.output_data = json.dumps(result_data, indent=2)

        if findings:
            self.findings_generated = 1
            self.total_findings = len(findings)
            self.critical_findings = sum(1 for f in findings if f.get('severity') == 'Critical')
            self.high_severity_findings = sum(1 for f in findings if f.get('severity') == 'High')
            finding_ids = [f.get('name') for f in findings if f.get('name')]
            self.finding_ids = ','.join(finding_ids)

        self.calculate_performance_metrics()
        self.calculate_test_summary()
        self.link_to_working_paper()
        self.save()

    def mark_as_failed(self, error_message=None, error_type=None, error_traceback=None):
        """Mark the execution as failed"""
        self.status = 'Failed'
        self.end_time = datetime.now()
        self.error_occurred = 1

        if error_message:
            self.error_message = error_message

        if error_type:
            self.error_type = error_type

        if error_traceback:
            self.error_traceback = error_traceback

        self.calculate_duration()
        self.save()

    def update_progress(self, progress_pct, records_processed=None):
        """Update execution progress"""
        self.progress_percentage = progress_pct

        if records_processed is not None:
            self.records_processed = records_processed
            if self.duration_seconds and self.duration_seconds > 0:
                self.records_per_second = round(records_processed / self.duration_seconds, 2)

        self.save()

    def calculate_test_summary(self):
        """Auto-calculate pass/fail counts from test_evidence child table"""
        if not self.test_evidence:
            return

        self.total_tests = len(self.test_evidence)
        self.passed_tests = sum(1 for t in self.test_evidence if t.test_status == 'Pass')
        self.failed_tests = sum(1 for t in self.test_evidence if t.test_status == 'Fail')

        if self.total_tests > 0:
            self.exception_rate = round((self.failed_tests / self.total_tests) * 100, 2)
        else:
            self.exception_rate = 0

    def link_to_working_paper(self):
        """Create or update associated Working Paper on completion"""
        if self.status != 'Completed' or not self.engagement_reference:
            return

        if self.working_paper_reference:
            return  # Already linked

        try:
            # Determine working paper type based on agent type
            wp_type_map = {
                'Financial': 'Data Analytics',
                'Compliance': 'Test of Controls',
                'Risk': 'Risk Assessment',
                'Discovery': 'Inquiry',
                'Notification': 'Other',
                'Asset': 'Inspection'
            }
            wp_type = wp_type_map.get(self.agent_type, 'Other')

            # Build evidence summary from test_evidence
            evidence_summary = []
            if self.test_evidence:
                for t in self.test_evidence:
                    evidence_summary.append(f"- {t.test_name}: {t.test_status}")

            description = (
                f"Auto-generated from {self.agent_name or self.agent_type} agent execution.\n"
                f"Task: {self.task_name or self.task_type}\n"
                f"Records Processed: {self.records_processed or 0}\n"
                f"Findings Generated: {self.total_findings or 0}\n"
            )
            if evidence_summary:
                description += "\nTest Evidence:\n" + "\n".join(evidence_summary)

            wp = frappe.get_doc({
                'doctype': 'Working Paper',
                'engagement_reference': self.engagement_reference,
                'wp_type': wp_type,
                'title': f"{self.agent_name or self.agent_type} - {self.task_name or self.task_type}",
                'description': description,
                'prepared_by': self.created_by or frappe.session.user,
                'preparation_date': self.end_time or datetime.now(),
                'status': 'Draft',
            })
            wp.insert(ignore_permissions=True)
            frappe.db.commit()

            self.working_paper_reference = wp.name

            # Link generated findings to the Working Paper
            if self.finding_ids:
                for fid in self.finding_ids.split(','):
                    fid = fid.strip()
                    if fid and frappe.db.exists('Audit Finding', fid):
                        frappe.db.set_value('Audit Finding', fid, 'working_paper_reference', wp.name)

        except Exception as e:
            frappe.log_error(
                message=f"Failed to create Working Paper for execution {self.name}: {str(e)}",
                title="Agent Working Paper Creation Error"
            )


# whitelisted functions for API access

@frappe.whitelist()
def get_agent_execution_logs(filters=None, limit=50, offset=0):
    """
    Get agent execution logs with optional filters

    Args:
        filters: Dictionary of filters
        limit: Maximum number of records to return
        offset: Offset for pagination

    Returns:
        List of agent execution logs
    """
    try:
        filter_conditions = {}

        if filters:
            filters = json.loads(filters) if isinstance(filters, str) else filters

            if filters.get('agent_type'):
                filter_conditions['agent_type'] = filters['agent_type']

            if filters.get('agent_id'):
                filter_conditions['agent_id'] = filters['agent_id']

            if filters.get('status'):
                filter_conditions['status'] = filters['status']

            if filters.get('task_type'):
                filter_conditions['task_type'] = filters['task_type']

        logs = frappe.get_all('Agent Execution Log',
            filters=filter_conditions,
            fields=['name', 'agent_id', 'agent_type', 'agent_name', 'task_type',
                   'task_name', 'status', 'start_time', 'end_time',
                   'duration_seconds', 'total_findings', 'critical_findings',
                   'records_processed', 'error_occurred'],
            order_by='creation desc',
            limit_page_length=limit,
            limit_start=offset
        )

        return {'logs': logs}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _('Agent Execution Log Retrieval Error'))
        frappe.throw(str(e))


@frappe.whitelist()
def get_agent_execution_stats(agent_type=None, days=30):
    """
    Get execution statistics for agents

    Args:
        agent_type: Filter by agent type (optional)
        days: Number of days to look back (default: 30)

    Returns:
        Dictionary with execution statistics
    """
    try:
        from datetime import timedelta

        date_filter = datetime.now() - timedelta(days=days)

        filters = {'creation': ['>=', date_filter]}
        if agent_type:
            filters['agent_type'] = agent_type

        # Total executions
        total = frappe.db.count('Agent Execution Log', filters=filters)

        # Status breakdown
        status_stats = frappe.db.get_all('Agent Execution Log',
            filters=filters,
            fields=['status', 'count(*) as count'],
            group_by='status'
        )

        # Agent type breakdown
        agent_stats = frappe.db.get_all('Agent Execution Log',
            filters={'creation': ['>=', date_filter]},
            fields=['agent_type', 'count(*) as count'],
            group_by='agent_type'
        )

        # Average duration
        avg_duration = frappe.db.sql("""
            SELECT AVG(duration_seconds) as avg_duration
            FROM `tabAgent Execution Log`
            WHERE creation >= %s
            AND status = 'Completed'
            {agent_type_condition}
        """.format(
            agent_type_condition=f"AND agent_type = '{agent_type}'" if agent_type else ""
        ), (date_filter,), as_dict=True)

        # Total findings
        total_findings = frappe.db.sql("""
            SELECT SUM(total_findings) as findings
            FROM `tabAgent Execution Log`
            WHERE creation >= %s
            {agent_type_condition}
        """.format(
            agent_type_condition=f"AND agent_type = '{agent_type}'" if agent_type else ""
        ), (date_filter,), as_dict=True)

        return {
            'total_executions': total,
            'status_breakdown': {s['status']: s['count'] for s in status_stats},
            'agent_type_breakdown': {a['agent_type']: a['count'] for a in agent_stats},
            'average_duration': round(avg_duration[0]['avg_duration'] or 0, 2),
            'total_findings_generated': total_findings[0]['findings'] or 0,
            'period_days': days
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _('Agent Execution Stats Error'))
        frappe.throw(str(e))


@frappe.whitelist()
def retry_agent_execution(log_name):
    """
    Retry a failed agent execution

    Args:
        log_name: Name of the Agent Execution Log to retry

    Returns:
        Result of the retry operation
    """
    try:
        log = frappe.get_doc('Agent Execution Log', log_name)

        if log.status != 'Failed':
            frappe.throw(_('Only failed executions can be retried'))

        if log.retry_count >= log.max_retries:
            frappe.throw(_('Maximum retry attempts reached'))

        # Import and use agent executor
        from mkaguzi.agents.agent_executor import AgentExecutor

        # Parse input data
        input_data = json.loads(log.input_data) if log.input_data else {}

        # Retry the execution
        result = AgentExecutor.execute_agent_task(log.agent_type, input_data)

        return {
            'success': True,
            'message': 'Agent execution retried successfully',
            'result': result
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _('Agent Execution Retry Error'))
        frappe.throw(str(e))


@frappe.whitelist()
def cancel_agent_execution(log_name):
    """
    Cancel a running or pending agent execution

    Args:
        log_name: Name of the Agent Execution Log to cancel

    Returns:
        Result of the cancel operation
    """
    try:
        log = frappe.get_doc('Agent Execution Log', log_name)

        if log.status not in ['Pending', 'Running']:
            frappe.throw(_('Only Pending or Running executions can be cancelled'))

        log.status = 'Cancelled'
        log.end_time = datetime.now()
        log.calculate_duration()
        log.save()

        # Publish real-time event
        frappe.publish_realtime(
            'agent_execution_cancelled',
            {'agent_id': log.agent_id, 'name': log.name}
        )

        return {
            'success': True,
            'message': 'Agent execution cancelled successfully'
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _('Agent Execution Cancel Error'))
        frappe.throw(str(e))
