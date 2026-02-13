# Base Agent Class for Multi-Agent System
# =============================================================================
# Abstract base class for all audit agents

import frappe
from typing import Any, Dict, Optional, Callable
from datetime import datetime
import threading
import uuid
from abc import ABC, abstractmethod

from .state_manager import StateManager
from .message_bus import MessageBus, Message


class AuditAgent(ABC):
    """
    Abstract base class for all audit agents.
    Provides common functionality for agent lifecycle, messaging, and state management.
    """

    # Agent states
    STATE_IDLE = 'idle'
    STATE_RUNNING = 'running'
    STATE_PAUSED = 'paused'
    STATE_STOPPED = 'stopped'
    STATE_ERROR = 'error'

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent

        Args:
            agent_id: Unique agent identifier (auto-generated if not provided)
            config: Agent configuration dictionary
        """
        self.id = agent_id or f"agent_{uuid.uuid4().hex[:12]}"
        self.config = config or {}
        self.state = self.STATE_IDLE
        self.state_manager = StateManager()
        self.message_bus = MessageBus()

        # Message handlers registry
        self.message_handlers = {}

        # Threading support
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

        # Agent metadata
        self.agent_type = self.__class__.__name__
        self.created_at = datetime.now()
        self.started_at = None
        self.stopped_at = None

        # Statistics
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.messages_sent = 0
        self.messages_received = 0

    @abstractmethod
    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task (must be implemented by subclasses)

        Args:
            task_data: Task data dictionary

        Returns:
            Task result dictionary
        """
        pass

    def start(self) -> bool:
        """
        Start the agent

        Returns:
            True if successful
        """
        try:
            with self._lock:
                if self.state == self.STATE_RUNNING:
                    return True

                self.state = self.STATE_RUNNING
                self.started_at = datetime.now()
                self._stop_event.clear()

                # Initialize agent state
                self.state_manager.set_state(self.id, 'status', self.state)
                self.state_manager.set_state(self.id, 'started_at', self.started_at.isoformat())
                self.state_manager.set_state(self.id, 'config', self.config)

                frappe.logger().info(f"Agent {self.id} ({self.agent_type}) started")

            return True

        except Exception as e:
            self.state = self.STATE_ERROR
            frappe.log_error(f"Agent Start Error [{self.id}]: {str(e)}", "Agent Manager")
            return False

    def stop(self) -> bool:
        """
        Stop the agent gracefully

        Returns:
            True if successful
        """
        try:
            with self._lock:
                if self.state == self.STATE_STOPPED:
                    return True

                self._stop_event.set()
                self.state = self.STATE_STOPPED
                self.stopped_at = datetime.now()

                # Update agent state
                self.state_manager.set_state(self.id, 'status', self.state)
                self.state_manager.set_state(self.id, 'stopped_at', self.stopped_at.isoformat())

                # Unsubscribe from all messages
                self.message_bus.unsubscribe(self.id)

                # Clear message queue
                self.message_bus.clear_queue(self.id)

                frappe.logger().info(f"Agent {self.id} ({self.agent_type}) stopped")

            return True

        except Exception as e:
            frappe.log_error(f"Agent Stop Error [{self.id}]: {str(e)}", "Agent Manager")
            return False

    def pause(self) -> bool:
        """
        Pause the agent

        Returns:
            True if successful
        """
        try:
            with self._lock:
                if self.state == self.STATE_RUNNING:
                    self.state = self.STATE_PAUSED
                    self.state_manager.set_state(self.id, 'status', self.state)
                    return True

            return False

        except Exception as e:
            frappe.log_error(f"Agent Pause Error [{self.id}]: {str(e)}", "Agent Manager")
            return False

    def resume(self) -> bool:
        """
        Resume a paused agent

        Returns:
            True if successful
        """
        try:
            with self._lock:
                if self.state == self.STATE_PAUSED:
                    self.state = self.STATE_RUNNING
                    self.state_manager.set_state(self.id, 'status', self.state)
                    return True

            return False

        except Exception as e:
            frappe.log_error(f"Agent Resume Error [{self.id}]: {str(e)}", "Agent Manager")
            return False

    def process_message(self, message: Message) -> Optional[Dict[str, Any]]:
        """
        Handle incoming message

        Args:
            message: Incoming message

        Returns:
            Response message data if applicable
        """
        try:
            self.messages_received += 1

            # Get message handler
            handler = self.message_handlers.get(message.message_type)

            if handler:
                # Call handler with message data
                response = handler(message.data, message.source)

                # Update stats
                self.state_manager.increment_counter(self.id, 'messages_received')

                return response
            else:
                frappe.logger().warning(
                    f"Agent {self.id}: No handler for message type: {message.message_type}"
                )

        except Exception as e:
            frappe.log_error(
                f"Message Processing Error [{self.id}:{message.message_type}]: {str(e)}",
                "Agent Manager"
            )

        return None

    def send_message(self, target: str, message_type: str, data: Any) -> bool:
        """
        Send message to another agent

        Args:
            target: Target agent ID
            message_type: Type of message
            data: Message data

        Returns:
            True if successful
        """
        try:
            success = self.message_bus.send_direct(target, message_type, data, self.id)

            if success:
                self.messages_sent += 1
                self.state_manager.increment_counter(self.id, 'messages_sent')

            return success

        except Exception as e:
            frappe.log_error(f"Send Message Error [{self.id}->{target}]: {str(e)}", "Agent Manager")
            return False

    def publish(self, message_type: str, data: Any) -> bool:
        """
        Publish message to all subscribers

        Args:
            message_type: Type of message
            data: Message data

        Returns:
            True if successful
        """
        try:
            success = self.message_bus.publish(message_type, data, self.id)

            if success:
                self.messages_sent += 1
                self.state_manager.increment_counter(self.id, 'messages_sent')

            return success

        except Exception as e:
            frappe.log_error(f"Publish Error [{self.id}:{message_type}]: {str(e)}", "Agent Manager")
            return False

    def subscribe(self, message_types: list, handler: Optional[Callable] = None) -> bool:
        """
        Subscribe to message types

        Args:
            message_types: List of message types to subscribe to
            handler: Optional handler function for these messages

        Returns:
            True if successful
        """
        try:
            success = self.message_bus.subscribe(self.id, message_types)

            if success and handler:
                for message_type in message_types:
                    self.message_handlers[message_type] = handler

            return success

        except Exception as e:
            frappe.log_error(f"Subscribe Error [{self.id}]: {str(e)}", "Agent Manager")
            return False

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get state value

        Args:
            key: State key
            default: Default value

        Returns:
            State value
        """
        return self.state_manager.get_state(self.id, key, default)

    def set_state(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Set state value

        Args:
            key: State key
            value: State value
            ttl: Time to live in seconds (reads from settings if None)

        Returns:
            True if successful
        """
        if ttl is None:
            ttl = self.state_manager._default_ttl()
        return self.state_manager.set_state(self.id, key, value, ttl)

    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status

        Returns:
            Status dictionary
        """
        return {
            'agent_id': self.id,
            'agent_type': self.agent_type,
            'state': self.state,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'stopped_at': self.stopped_at.isoformat() if self.stopped_at else None,
            'config': self.config,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'messages_sent': self.messages_sent,
            'messages_received': self.messages_received
        }

    def is_running(self) -> bool:
        """Check if agent is running"""
        return self.state == self.STATE_RUNNING

    def is_stopped(self) -> bool:
        """Check if agent is stopped"""
        return self.state == self.STATE_STOPPED

    def should_stop(self) -> bool:
        """Check if stop event is set"""
        return self._stop_event.is_set()

    # Valid finding_category options from DocType definition
    VALID_FINDING_CATEGORIES = [
        "Control Deficiency", "Non-Compliance", "Inefficiency",
        "Error", "Fraud Indicator", "Best Practice Opportunity"
    ]

    # Map agent-provided finding types to valid DocType categories
    FINDING_CATEGORY_MAP = {
        # Financial Agent mappings
        "Accounts Receivable Issue": "Inefficiency",
        "Sales Transaction Review": "Control Deficiency",
        "Accounts Payable Issue": "Inefficiency",
        "Vendor Invoice Review": "Error",
        "Payment Review": "Control Deficiency",
        "Payment Anomaly": "Fraud Indicator",
        "Journal Entry Review": "Control Deficiency",
        "Timing Anomaly": "Fraud Indicator",
        # Asset Agent mappings
        "Asset Management": "Control Deficiency",
        "Asset Control": "Control Deficiency",
        "Depreciation Review": "Inefficiency",
        "Asset Disposal Review": "Control Deficiency",
        "Asset Verification": "Control Deficiency",
        "Asset Utilization": "Inefficiency",
    }

    def _normalize_finding_category(self, finding_type: str) -> str:
        """Map agent finding type to valid Audit Finding category."""
        if finding_type in self.VALID_FINDING_CATEGORIES:
            return finding_type
        mapped = self.FINDING_CATEGORY_MAP.get(finding_type)
        if mapped:
            return mapped
        # Fallback: try keyword matching
        lower = finding_type.lower()
        if "fraud" in lower or "anomaly" in lower or "suspicious" in lower:
            return "Fraud Indicator"
        if "compliance" in lower or "regulatory" in lower:
            return "Non-Compliance"
        if "error" in lower or "duplicate" in lower:
            return "Error"
        if "inefficien" in lower or "delay" in lower or "overdue" in lower:
            return "Inefficiency"
        return "Control Deficiency"  # Safe default

    def record_test_evidence(self, execution_log_name: str, test_name: str,
                            test_status: str, severity: str = None,
                            execution_time_ms: int = 0, records_processed: int = 0,
                            result_data: str = None, error_message: str = None,
                            threshold_breached: bool = False) -> None:
        """
        Record per-test evidence on an Agent Execution Log.

        Args:
            execution_log_name: Name of the Agent Execution Log document
            test_name: Name/description of the test
            test_status: Pass, Fail, Warning, Error, or Skipped
            severity: Low, Medium, High, or Critical
            execution_time_ms: Execution time in milliseconds
            records_processed: Number of records processed
            result_data: Textual result data
            error_message: Error message if test failed
            threshold_breached: Whether a threshold was breached
        """
        try:
            log = frappe.get_doc('Agent Execution Log', execution_log_name)
            log.append('test_evidence', {
                'test_name': test_name,
                'test_status': test_status,
                'severity': severity,
                'execution_time_ms': execution_time_ms,
                'records_processed': records_processed,
                'result_data': result_data,
                'error_message': error_message,
                'threshold_breached': 1 if threshold_breached else 0,
            })
            log.save(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(
                message=f"Failed to record test evidence: {str(e)}",
                title=f"Test Evidence Error [{self.agent_type}]"
            )

    def create_audit_finding(self, finding_title: str, finding_type: str, severity: str,
                           condition: str, criteria: str, cause: str = None,
                           consequence: str = None, recommendation: str = None,
                           risk_category: str = None, engagement_reference: str = None,
                           financial_impact: float = None, working_paper_reference: str = None,
                           **kwargs) -> Dict[str, str]:
        """
        Create an Audit Finding document from agent analysis

        Args:
            finding_title: Title/summary of the finding
            finding_type: Finding category (Control Deficiency, Non-Compliance, etc.)
            severity: Risk rating (Critical, High, Medium, Low)
            condition: What was found/observed
            criteria: What should have been in place
            cause: Why the condition occurred
            consequence: Impact/consequence of the condition
            recommendation: Recommended corrective action
            risk_category: Risk category (Financial, Operational, Compliance, IT, etc.)
            engagement_reference: Link to Audit Engagement if available
            financial_impact: Financial impact amount
            working_paper_reference: Link to Working Paper if available
            **kwargs: Additional field values

        Returns:
            dict: {"name": finding_doc_name, "severity": severity} for executor tracking
        """
        try:
            # Normalize finding_type to valid category
            finding_category = self._normalize_finding_category(finding_type)

            # Build the finding document data
            finding_data = {
                'doctype': 'Audit Finding',
                'finding_title': finding_title,
                'finding_category': finding_category,
                'severity': severity,
                'risk_rating': severity,  # Also set risk_rating for backward compatibility
                'risk_category': risk_category,
                'condition': condition,
                'criteria': criteria,
                'cause': cause,
                'consequence': consequence,
                'recommendation': recommendation,
                'financial_impact': financial_impact,
                'engagement_reference': engagement_reference,
                'finding_status': 'Open',

                # Agent tracking fields
                'source_agent': self.agent_type,
                'auto_generated': 1,
                'ai_review_status': 'Pending',

                # Add any additional kwargs
                **kwargs
            }

            # Set working_paper_reference if provided
            if working_paper_reference:
                finding_data['working_paper_reference'] = working_paper_reference

            # Create the finding document
            finding_doc = frappe.get_doc(finding_data)
            
            # Insert the document (this triggers the autoname for finding_id)
            finding_doc.insert(ignore_permissions=True)
            
            # Commit the transaction
            frappe.db.commit()
            
            return {
                "name": finding_doc.name,
                "severity": severity
            }
            
        except Exception as e:
            # Truncate title to 140 chars to avoid CharacterLengthExceededError
            error_title = f"Finding Error [{self.agent_type}]"
            try:
                frappe.log_error(
                    message=f"Failed to create audit finding: {str(e)}\nTitle: {finding_title}\nType: {finding_type}",
                    title=error_title
                )
            except Exception:
                pass  # Don't let error logging crash the agent
            raise e

    def __repr__(self) -> str:
        return f"<{self.agent_type} id={self.id} state={self.state}>"
