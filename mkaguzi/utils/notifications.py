import frappe
from frappe import _
from frappe.utils import get_url, now_datetime
from datetime import datetime, timedelta
import json

class NotificationManager:
    """
    Notification manager for audit system
    """

    @staticmethod
    def send_notification(recipients, subject, message, notification_type='Info', related_document=None):
        """
        Send notification to users
        """
        try:
            # Create notification document
            notification = frappe.get_doc({
                'doctype': 'Audit Notification',
                'subject': subject,
                'message': message,
                'notification_type': notification_type,
                'related_document': related_document,
                'sent_date': now_datetime(),
                'status': 'Sent'
            })

            # Add recipients
            if isinstance(recipients, str):
                recipients = [recipients]

            for recipient in recipients:
                notification.append('recipients', {
                    'user': recipient,
                    'status': 'Pending'
                })

            notification.insert()
            frappe.db.commit()

            # Send actual notifications (email, in-app, etc.)
            NotificationManager._send_to_recipients(notification)

            return {
                'success': True,
                'notification_id': notification.name,
                'message': 'Notification sent successfully'
            }

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Notification Send Error"))
            return {'success': False, 'error': str(e)}

    @staticmethod
    def _send_to_recipients(notification):
        """
        Send notification to individual recipients
        """
        try:
            for recipient in notification.recipients:
                try:
                    # Send in-app notification
                    frappe.sendmail(
                        recipients=[recipient.user],
                        subject=notification.subject,
                        message=notification.message,
                        header=_('Internal Audit Notification')
                    )

                    # Mark as sent
                    recipient.status = 'Sent'

                except Exception as e:
                    frappe.log_error(f"Failed to send notification to {recipient.user}: {str(e)}")
                    recipient.status = 'Failed'

            notification.save()

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Recipient Notification Error"))

    @staticmethod
    def notify_finding_created(finding_id):
        """
        Notify relevant users when a finding is created
        """
        try:
            finding = frappe.get_doc('Audit Finding', finding_id)

            # Get responsible person
            responsible_person = finding.responsible_party

            # Get audit execution team members
            execution = frappe.get_doc('Audit Execution', finding.audit_execution)
            team_members = [member.user for member in execution.execution_team]

            # Combine recipients
            recipients = list(set([responsible_person] + team_members))

            subject = f"New Audit Finding: {finding.finding_title}"
            message = f"""
            A new audit finding has been created:

            Title: {finding.finding_title}
            Severity: {finding.severity}
            Description: {finding.description}

            Responsible Party: {responsible_person}
            Target Completion Date: {finding.target_completion_date}

            Please review and take appropriate action.

            View Finding: {get_url()}/app/audit-finding/{finding_id}
            """

            return NotificationManager.send_notification(
                recipients=recipients,
                subject=subject,
                message=message,
                notification_type='Finding Created',
                related_document=finding_id
            )

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Finding Creation Notification Error"))
            return {'success': False, 'error': str(e)}

    @staticmethod
    def notify_finding_overdue(finding_id):
        """
        Notify when a finding becomes overdue
        """
        try:
            finding = frappe.get_doc('Audit Finding', finding_id)

            recipients = [finding.responsible_party]

            subject = f"OVERDUE: Audit Finding {finding.finding_title}"
            message = f"""
            URGENT: The following audit finding is now overdue:

            Title: {finding.finding_title}
            Target Completion Date: {finding.target_completion_date}
            Days Overdue: {(datetime.now().date() - finding.target_completion_date).days}

            Immediate action is required to address this finding.

            View Finding: {get_url()}/app/audit-finding/{finding_id}
            """

            return NotificationManager.send_notification(
                recipients=recipients,
                subject=subject,
                message=message,
                notification_type='Overdue Finding',
                related_document=finding_id
            )

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Overdue Finding Notification Error"))
            return {'success': False, 'error': str(e)}

    @staticmethod
    def notify_compliance_due(compliance_check_id):
        """
        Notify when compliance check is due
        """
        try:
            check = frappe.get_doc('Compliance Check', compliance_check_id)

            recipients = [check.responsible_person]

            subject = f"Compliance Check Due: {check.check_name}"
            message = f"""
            The following compliance check is now due:

            Check Name: {check.check_name}
            Type: {check.compliance_type}
            Due Date: {check.next_due_date}

            Please complete this compliance check as soon as possible.

            View Check: {get_url()}/app/compliance-check/{compliance_check_id}
            """

            return NotificationManager.send_notification(
                recipients=recipients,
                subject=subject,
                message=message,
                notification_type='Compliance Due',
                related_document=compliance_check_id
            )

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Compliance Due Notification Error"))
            return {'success': False, 'error': str(e)}

    @staticmethod
    def notify_test_completed(execution_id, test_name, status):
        """
        Notify when an audit test is completed
        """
        try:
            execution = frappe.get_doc('Audit Execution', execution_id)
            team_members = [member.user for member in execution.execution_team]

            subject = f"Audit Test Completed: {test_name}"
            status_emoji = "✅" if status == 'Completed' else "⚠️"

            message = f"""
            {status_emoji} Audit test has been completed:

            Test: {test_name}
            Status: {status}
            Execution: {execution.name}

            View Results: {get_url()}/app/audit-execution/{execution_id}
            """

            return NotificationManager.send_notification(
                recipients=team_members,
                subject=subject,
                message=message,
                notification_type='Test Completed',
                related_document=execution_id
            )

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Test Completion Notification Error"))
            return {'success': False, 'error': str(e)}

    @staticmethod
    def notify_audit_completed(execution_id):
        """
        Notify when audit execution is completed
        """
        try:
            execution = frappe.get_doc('Audit Execution', execution_id)

            # Get all team members and audit plan creator
            team_members = [member.user for member in execution.execution_team]

            plan = frappe.get_doc('Audit Plan', execution.audit_plan)
            audit_manager = plan.created_by

            recipients = list(set(team_members + [audit_manager]))

            subject = f"Audit Execution Completed: {plan.plan_name}"
            message = f"""
            Audit execution has been completed:

            Plan: {plan.plan_name}
            Execution Period: {execution.execution_start_date} to {execution.execution_end_date}
            Status: {execution.status}

            Summary:
            - Tests Executed: {len(execution.executed_tests)}
            - Findings Identified: {frappe.db.count('Audit Finding', {'audit_execution': execution_id})}

            View Full Report: {get_url()}/app/audit-execution/{execution_id}
            """

            return NotificationManager.send_notification(
                recipients=recipients,
                subject=subject,
                message=message,
                notification_type='Audit Completed',
                related_document=execution_id
            )

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Audit Completion Notification Error"))
            return {'success': False, 'error': str(e)}

    @staticmethod
    def schedule_overdue_notifications():
        """
        Schedule notifications for overdue items
        """
        try:
            # Find overdue findings
            overdue_findings = frappe.db.sql("""
                SELECT name, finding_title, responsible_party, target_completion_date
                FROM `tabAudit Finding`
                WHERE status IN ('Open', 'In Progress')
                AND target_completion_date < CURDATE()
                AND (last_notification_date IS NULL OR last_notification_date < DATE_SUB(CURDATE(), INTERVAL 7 DAY))
            """, as_dict=True)

            # Send notifications for overdue findings
            for finding in overdue_findings:
                NotificationManager.notify_finding_overdue(finding.name)

                # Update last notification date
                frappe.db.set_value('Audit Finding', finding.name, 'last_notification_date', datetime.now())

            # Find overdue compliance checks
            overdue_compliance = frappe.db.sql("""
                SELECT name, check_name, responsible_person, next_due_date
                FROM `tabCompliance Check`
                WHERE status = 'Scheduled'
                AND next_due_date < CURDATE()
                AND (last_notification_date IS NULL OR last_notification_date < DATE_SUB(CURDATE(), INTERVAL 7 DAY))
            """, as_dict=True)

            # Send notifications for overdue compliance
            for check in overdue_compliance:
                NotificationManager.notify_compliance_due(check.name)

                # Update last notification date
                frappe.db.set_value('Compliance Check', check.name, 'last_notification_date', datetime.now())

            frappe.db.commit()

            return {
                'success': True,
                'overdue_findings_notified': len(overdue_findings),
                'overdue_compliance_notified': len(overdue_compliance)
            }

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Overdue Notifications Error"))
            return {'success': False, 'error': str(e)}

    @staticmethod
    def send_weekly_digest():
        """
        Send weekly digest of audit activities
        """
        try:
            # Calculate date range (last 7 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)

            # Get audit activities summary
            activities = {
                'new_findings': frappe.db.count('Audit Finding',
                    filters={'creation': ['between', [start_date, end_date]]}),
                'resolved_findings': frappe.db.count('Audit Finding',
                    filters={'status': 'Resolved', 'modified': ['between', [start_date, end_date]]}),
                'completed_tests': frappe.db.sql("""
                    SELECT COUNT(*) as count
                    FROM `tabExecuted Test`
                    WHERE status = 'Completed'
                    AND modified BETWEEN %s AND %s
                """, (start_date, end_date), as_dict=True)[0]['count'],
                'compliance_checks': frappe.db.count('Compliance Execution',
                    filters={'execution_date': ['between', [start_date, end_date]]})
            }

            # Get recipients (all audit users)
            audit_users = frappe.db.sql("""
                SELECT DISTINCT user
                FROM `tabAudit Execution Team`
                UNION
                SELECT DISTINCT responsible_party
                FROM `tabAudit Finding`
                WHERE responsible_party IS NOT NULL
            """, as_dict=True)

            recipients = [user['user'] for user in audit_users]

            subject = f"Weekly Audit Digest - {end_date.strftime('%B %d, %Y')}"
            message = f"""
            Weekly Audit Activities Summary ({start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}):

            📊 Key Metrics:
            • New Findings: {activities['new_findings']}
            • Resolved Findings: {activities['resolved_findings']}
            • Completed Tests: {activities['completed_tests']}
            • Compliance Checks: {activities['compliance_checks']}

            📈 Progress:
            • Finding Resolution Rate: {round(activities['resolved_findings'] / max(activities['new_findings'], 1) * 100, 1)}%

            View Full Dashboard: {get_url()}/app/audit-dashboard
            """

            return NotificationManager.send_notification(
                recipients=recipients,
                subject=subject,
                message=message,
                notification_type='Weekly Digest'
            )

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Weekly Digest Error"))
            return {'success': False, 'error': str(e)}


@frappe.whitelist()
def send_audit_notification(notification_type, **kwargs):
    """
    Send audit notification based on type
    """
    try:
        manager = NotificationManager()

        if notification_type == 'finding_created':
            return manager.notify_finding_created(kwargs.get('finding_id'))
        elif notification_type == 'finding_overdue':
            return manager.notify_finding_overdue(kwargs.get('finding_id'))
        elif notification_type == 'compliance_due':
            return manager.notify_compliance_due(kwargs.get('compliance_check_id'))
        elif notification_type == 'test_completed':
            return manager.notify_test_completed(
                kwargs.get('execution_id'),
                kwargs.get('test_name'),
                kwargs.get('status')
            )
        elif notification_type == 'audit_completed':
            return manager.notify_audit_completed(kwargs.get('execution_id'))
        else:
            return {'success': False, 'error': f'Unknown notification type: {notification_type}'}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Audit Notification Error"))
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def schedule_notifications():
    """
    Schedule periodic notifications
    """
    try:
        manager = NotificationManager()

        # Send overdue notifications
        overdue_result = manager.schedule_overdue_notifications()

        # Send weekly digest (if it's Monday)
        if datetime.now().weekday() == 0:  # Monday
            digest_result = manager.send_weekly_digest()
        else:
            digest_result = {'success': True, 'message': 'Not Monday - skipping weekly digest'}

        return {
            'success': True,
            'overdue_notifications': overdue_result,
            'weekly_digest': digest_result
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Notification Scheduling Error"))
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def send_weekly_digest():
    """
    Send weekly digest of audit activities (module-level function for hooks)
    """
    return NotificationManager.send_weekly_digest()


# Document event handlers for hooks
def on_audit_finding_insert(doc, method):
    """Handle audit finding creation"""
    send_audit_notification('finding_created', finding_id=doc.name)


def on_audit_finding_update(doc, method):
    """Handle audit finding updates"""
    # Check if finding became overdue
    if doc.target_completion_date and doc.status in ['Open', 'In Progress']:
        if doc.target_completion_date < datetime.now().date():
            send_audit_notification('finding_overdue', finding_id=doc.name)


def on_compliance_check_update(doc, method):
    """Handle compliance check updates"""
    # Check if compliance check is due
    if doc.next_due_date and doc.status == 'Scheduled':
        if doc.next_due_date <= datetime.now().date():
            send_audit_notification('compliance_due', compliance_check_id=doc.name)


def on_audit_execution_update(doc, method):
    """Handle audit execution updates"""
    # Check if execution was completed
    if doc.status == 'Completed':
        send_audit_notification('audit_completed', execution_id=doc.name)