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

    def set_state(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set state value

        Args:
            key: State key
            value: State value
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
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

    def __repr__(self) -> str:
        return f"<{self.agent_type} id={self.id} state={self.state}>"
