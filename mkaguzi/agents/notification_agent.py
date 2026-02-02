# Notification Agent for Multi-Agent System
# =============================================================================
# Agent for intelligent alerting and notification management

import frappe
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

from .agent_base import AuditAgent


class NotificationPriority(Enum):
    """Notification priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class NotificationChannel(Enum):
    """Notification channels"""
    EMAIL = "email"
    SYSTEM = "system"
    SMS = "sms"
    WEBHOOK = "webhook"


@dataclass
class NotificationMessage:
    """Notification message structure"""
    title: str
    message: str
    priority: NotificationPriority
    channels: List[NotificationChannel]
    recipients: List[str]
    data: Optional[Dict[str, Any]] = None
    source_agent: Optional[str] = None
    escalation_rules: Optional[Dict[str, Any]] = None


class NotificationAgent(AuditAgent):
    """
    Agent for intelligent alerting, notification prioritization,
    smart routing, and escalation management.
    """

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize the Notification Agent"""
        super().__init__(agent_id, config)
        self.agent_type = 'NotificationAgent'

        # Configuration
        self.aggregation_window_minutes = config.get('aggregation_window_minutes', 15) if config else 15
        self.max_digest_size = config.get('max_digest_size', 50) if config else 50
        self.escalation_enabled = config.get('escalation_enabled', True) if config else True

        # Notification tracking
        self.pending_notifications: Dict[str, List[NotificationMessage]] = defaultdict(list)
        self.sent_notifications: Dict[str, List[str]] = defaultdict(list)

        # Subscribe to relevant message types
        self.subscribe(['notification_request', 'alert_generated', 'finding_created'])

    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a notification task

        Args:
            task_data: Task data dictionary

        Returns:
            Task result dictionary
        """
        task_type = task_data.get('task_type')

        if task_type == 'send_notification':
            return self.send_notification(task_data)
        elif task_type == 'aggregate_alerts':
            return self.aggregate_alerts(task_data.get('timeframe_minutes'))
        elif task_type == 'escalate':
            return self.escalate_alert(task_data.get('alert_id'))
        elif task_type == 'send_digest':
            return self.send_digest(task_data.get('recipient_type'))
        elif task_type == 'process_pending':
            return self.process_pending_notifications()
        elif task_type == 'configure_routing':
            return self.configure_routing(task_data.get('routing_rules'))
        else:
            return {
                'status': 'error',
                'error': f'Unknown task type: {task_type}'
            }

    def send_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send notification with intelligent routing

        Args:
            notification_data: Notification data

        Returns:
            Send results
        """
        try:
            # Create notification message
            message = NotificationMessage(
                title=notification_data.get('title', 'Notification'),
                message=notification_data.get('message', ''),
                priority=NotificationPriority(notification_data.get('priority', 'normal')),
                channels=[NotificationChannel(c) for c in notification_data.get('channels', ['system'])],
                recipients=notification_data.get('recipients', []),
                data=notification_data.get('data'),
                source_agent=notification_data.get('source_agent'),
                escalation_rules=notification_data.get('escalation_rules')
            )

            # Check if aggregation is needed
            if self._should_aggregate(message):
                return self._queue_for_aggregation(message)

            # Send immediately
            results = self._send_message(message)

            return {
                'status': 'success',
                'notification_id': f"notif_{datetime.now().timestamp()}",
                'sent': results.get('sent', 0),
                'failed': results.get('failed', 0),
                'channels': results.get('channels', [])
            }

        except Exception as e:
            frappe.log_error(f"Send Notification Error: {str(e)}", "Notification Agent")
            return {'status': 'error', 'error': str(e)}

    def aggregate_alerts(self, timeframe_minutes: Optional[int] = None) -> Dict[str, Any]:
        """
        Aggregate similar alerts to reduce noise

        Args:
            timeframe_minutes: Time window for aggregation

        Returns:
            Aggregation results
        """
        try:
            timeframe_minutes = timeframe_minutes or self.aggregation_window_minutes
            cutoff = datetime.now() - timedelta(minutes=timeframe_minutes)

            # Get pending notifications in time window
            recent_notifications = []

            for recipient, messages in list(self.pending_notifications.items()):
                for msg in messages[:]:  # Copy to avoid modification during iteration
                    # Check timestamp from data
                    msg_time = msg.data.get('created_at') if msg.data else None
                    if msg_time:
                        msg_dt = datetime.fromisoformat(msg_time) if isinstance(msg_time, str) else msg_time
                        if msg_dt >= cutoff:
                            recent_notifications.append((recipient, msg))
                            # Remove from pending
                            self.pending_notifications[recipient].remove(msg)

            if not recent_notifications:
                return {
                    'status': 'success',
                    'message': 'No notifications to aggregate',
                    'aggregated_count': 0
                }

            # Group by priority and type
            groups = self._group_notifications(recent_notifications)

            # Create digests
            digests = []
            for group_key, group_messages in groups.items():
                digest = self._create_digest(group_messages)
                digests.append(digest)

            # Send digests
            sent = 0
            for digest in digests:
                result = self._send_message(digest)
                sent += result.get('sent', 0)

            return {
                'status': 'success',
                'timeframe_minutes': timeframe_minutes,
                'aggregated_count': len(recent_notifications),
                'digests_created': len(digests),
                'digests_sent': sent
            }

        except Exception as e:
            frappe.log_error(f"Alert Aggregation Error: {str(e)}", "Notification Agent")
            return {'status': 'error', 'error': str(e)}

    def escalate_alert(self, alert_id: str) -> Dict[str, Any]:
        """
        Escalate alert based on severity/time

        Args:
            alert_id: Alert to escalate

        Returns:
            Escalation results
        """
        try:
            if not self.escalation_enabled:
                return {
                    'status': 'success',
                    'message': 'Escalation is disabled',
                    'escalated': False
                }

            # Get alert details
            alert = self._get_alert(alert_id)

            if not alert:
                return {'status': 'error', 'error': f'Alert {alert_id} not found'}

            # Check escalation rules
            escalation_level = self._calculate_escalation_level(alert)

            if escalation_level == 0:
                return {
                    'status': 'success',
                    'message': 'No escalation needed',
                    'escalated': False
                }

            # Get escalation recipients
            escalation_recipients = self._get_escalation_recipients(alert, escalation_level)

            # Create escalated notification
            escalated_message = NotificationMessage(
                title=f"ESCALATED: {alert.get('title', 'Alert')}",
                message=f"This alert has been escalated to level {escalation_level}",
                priority=NotificationPriority.CRITICAL,
                channels=[NotificationChannel.EMAIL, NotificationChannel.SYSTEM],
                recipients=escalation_recipients,
                data={'original_alert': alert, 'escalation_level': escalation_level},
                source_agent=self.agent_type
            )

            # Send escalation
            result = self._send_message(escalated_message)

            # Update alert status
            self._update_alert_escalation(alert_id, escalation_level)

            return {
                'status': 'success',
                'escalated': True,
                'escalation_level': escalation_level,
                'recipients': escalation_recipients,
                'sent': result.get('sent', 0)
            }

        except Exception as e:
            frappe.log_error(f"Alert Escalation Error: {str(e)}", "Notification Agent")
            return {'status': 'error', 'error': str(e)}

    def send_digest(self, recipient_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Send digest notification

        Args:
            recipient_type: Type of recipients (admin, auditor, etc.)

        Returns:
            Digest send results
        """
        try:
            # Get recipients based on type
            recipients = self._get_digest_recipients(recipient_type)

            # Collect pending notifications
            digest_notifications = []

            for recipient in recipients:
                if recipient in self.pending_notifications:
                    digest_notifications.extend([
                        (recipient, msg) for msg in self.pending_notifications[recipient]
                    ])
                    # Clear pending
                    self.pending_notifications[recipient] = []

            if not digest_notifications:
                return {
                    'status': 'success',
                    'message': 'No notifications for digest',
                    'sent': 0
                }

            # Create digest by recipient
            recipient_digests = defaultdict(list)
            for recipient, message in digest_notifications:
                recipient_digests[recipient].append(message)

            # Send digests
            sent = 0
            for recipient, messages in recipient_digests.items():
                digest = self._create_digest(messages, recipient)
                result = self._send_message(digest)
                sent += result.get('sent', 0)

            return {
                'status': 'success',
                'digests_sent': sent,
                'recipients': len(recipient_digests)
            }

        except Exception as e:
            frappe.log_error(f"Digest Send Error: {str(e)}", "Notification Agent")
            return {'status': 'error', 'error': str(e)}

    def process_pending_notifications(self) -> Dict[str, Any]:
        """Process all pending notifications"""
        try:
            total_pending = sum(len(msgs) for msgs in self.pending_notifications.values())

            if total_pending == 0:
                return {
                    'status': 'success',
                    'message': 'No pending notifications',
                    'processed': 0
                }

            # Process aggregation for all pending
            result = self.aggregate_alerts(self.aggregation_window_minutes)

            # If still pending after aggregation, send individually
            remaining = sum(len(msgs) for msgs in self.pending_notifications.values())

            if remaining > 0:
                sent = 0
                for recipient, messages in list(self.pending_notifications.items()):
                    for message in messages[:]:
                        send_result = self._send_message(message)
                        sent += send_result.get('sent', 0)
                        self.pending_notifications[recipient].remove(message)

                return {
                    'status': 'success',
                    'processed': total_pending,
                    'sent': sent
                }

            return {
                'status': 'success',
                'processed': total_pending,
                'result': result
            }

        except Exception as e:
            frappe.log_error(f"Process Pending Error: {str(e)}", "Notification Agent")
            return {'status': 'error', 'error': str(e)}

    def configure_routing(self, routing_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Configure notification routing rules

        Args:
            routing_rules: List of routing rules

        Returns:
            Configuration results
        """
        try:
            # Store routing rules in state
            self.set_state('routing_rules', routing_rules)

            return {
                'status': 'success',
                'rules_configured': len(routing_rules)
            }

        except Exception as e:
            frappe.log_error(f"Configure Routing Error: {str(e)}", "Notification Agent")
            return {'status': 'error', 'error': str(e)}

    def _should_aggregate(self, message: NotificationMessage) -> bool:
        """Determine if message should be aggregated"""
        # Low priority messages should be aggregated
        if message.priority == NotificationPriority.LOW:
            return True

        # Check if similar recent messages exist
        for pending_msg in self.pending_notifications.get(message.recipients[0] if message.recipients else [], []):
            if pending_msg.title == message.title:
                return True

        return False

    def _queue_for_aggregation(self, message: NotificationMessage) -> Dict[str, Any]:
        """Queue message for aggregation"""
        for recipient in message.recipients:
            self.pending_notifications[recipient].append(message)

        return {
            'status': 'success',
            'queued': True,
            'message': 'Queued for aggregation'
        }

    def _send_message(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send message through specified channels"""
        results = {
            'sent': 0,
            'failed': 0,
            'channels': []
        }

        for channel in message.channels:
            try:
                if channel == NotificationChannel.EMAIL:
                    sent = self._send_email(message)
                elif channel == NotificationChannel.SYSTEM:
                    sent = self._send_system_notification(message)
                elif channel == NotificationChannel.SMS:
                    sent = self._send_sms(message)
                elif channel == NotificationChannel.WEBHOOK:
                    sent = self._send_webhook(message)
                else:
                    sent = False

                if sent:
                    results['sent'] += 1
                    results['channels'].append(channel.value)
                else:
                    results['failed'] += 1

            except Exception as e:
                frappe.log_error(f"Failed to send via {channel}: {str(e)}", "Notification Agent")
                results['failed'] += 1

        return results

    def _send_email(self, message: NotificationMessage) -> bool:
        """Send email notification"""
        try:
            frappe.sendmail(
                recipients=message.recipients,
                subject=message.title,
                message=message.message,
                delayed=False
            )
            return True
        except Exception:
            return False

    def _send_system_notification(self, message: NotificationMessage) -> bool:
        """Send system notification"""
        try:
            if not frappe.db.table_exists('Notification Log'):
                return False

            for recipient in message.recipients:
                notification = frappe.get_doc({
                    'doctype': 'Notification Log',
                    'for_user': recipient,
                    'type': 'Alert',
                    'subject': message.title,
                    'payload': frappe.as_json(message.data or {}),
                    'read': 0
                })
                notification.insert()

            frappe.db.commit()
            return True

        except Exception:
            return False

    def _send_sms(self, message: NotificationMessage) -> bool:
        """Send SMS notification (placeholder)"""
        # Would integrate with SMS gateway
        return False

    def _send_webhook(self, message: NotificationMessage) -> bool:
        """Send webhook notification (placeholder)"""
        # Would make HTTP request to webhook URL
        return False

    def _group_notifications(self, notifications: List) -> Dict[str, List]:
        """Group notifications by type and priority"""
        groups = defaultdict(list)

        for recipient, message in notifications:
            key = f"{message.priority.value}_{message.title}"
            groups[key].append((recipient, message))

        return groups

    def _create_digest(self, messages: List, recipient: Optional[str] = None) -> NotificationMessage:
        """Create digest from multiple messages"""
        if not messages:
            return None

        # Extract recipients
        recipients = set()
        for msg in messages:
            recipients.update(msg.recipients)

        # Count by type
        message_types = defaultdict(int)
        for msg in messages:
            message_types[msg.title] += 1

        # Build digest message
        summary_lines = [f"{count}x {title}" for title, count in message_types.items()]
        digest_message = f"Summary:\n" + "\n".join(summary_lines)

        return NotificationMessage(
            title=f"Notification Digest ({len(messages)} items)",
            message=digest_message,
            priority=NotificationPriority.NORMAL,
            channels=[NotificationChannel.EMAIL],
            recipients=list(recipients),
            data={'digest_count': len(messages), 'items': message_types},
            source_agent=self.agent_type
        )

    def _get_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Get alert details"""
        # Would fetch from appropriate DocType
        return None

    def _calculate_escalation_level(self, alert: Dict[str, Any]) -> int:
        """Calculate escalation level for an alert"""
        severity = alert.get('severity', 'Low')
        created_at = alert.get('created_at')

        if not created_at:
            return 0

        # Calculate age
        alert_age = (datetime.now() - created_at).total_seconds() / 3600  # hours

        # Escalation rules
        if severity == 'Critical' and alert_age > 1:
            return 3
        elif severity == 'High' and alert_age > 4:
            return 2
        elif severity == 'Medium' and alert_age > 24:
            return 1

        return 0

    def _get_escalation_recipients(self, alert: Dict, level: int) -> List[str]:
        """Get escalation recipients based on level"""
        # Level 1: Team Lead
        # Level 2: Manager
        # Level 3: Director/Admin

        if level == 1:
            return self._get_users_with_role('Audit Manager')
        elif level == 2:
            return self._get_users_with_role('Audit Administrator')
        elif level >= 3:
            return self._get_users_with_role('System Manager')

        return []

    def _get_users_with_role(self, role: str) -> List[str]:
        """Get users with a specific role"""
        try:
            return frappe.get_all('Has Role',
                filters={'role': role, 'parenttype': 'User'},
                pluck='parent'
            )
        except Exception:
            return []

    def _update_alert_escalation(self, alert_id: str, level: int) -> None:
        """Update alert with escalation level"""
        # Would update the alert document
        pass

    def _get_digest_recipients(self, recipient_type: Optional[str]) -> List[str]:
        """Get recipients for digest based on type"""
        if recipient_type == 'admin':
            return self._get_users_with_role('System Manager')
        elif recipient_type == 'auditor':
            return self._get_users_with_role('Auditor')
        else:
            # Get all audit users
            return self._get_users_with_role('Audit Manager') + self._get_users_with_role('Lead Auditor')
