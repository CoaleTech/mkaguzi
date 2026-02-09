# Message Bus for Multi-Agent System
# =============================================================================
# Inter-agent communication using publish/subscribe pattern

import frappe
from collections import defaultdict
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import threading
import queue
import json
import time


class Message:
    """Message object for inter-agent communication"""

    def __init__(self, message_type: str, data: Any, source: Optional[str] = None,
                 target: Optional[str] = None, timestamp: Optional[datetime] = None):
        self.message_type = message_type
        self.data = data
        self.source = source
        self.target = target
        self.timestamp = timestamp or datetime.now()
        self.message_id = f"{self.source or 'system'}:{int(time.time() * 1000000)}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'message_id': self.message_id,
            'message_type': self.message_type,
            'data': self.data,
            'source': self.source,
            'target': self.target,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        timestamp = data.get('timestamp')
        if timestamp and isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        return cls(
            message_type=data['message_type'],
            data=data['data'],
            source=data.get('source'),
            target=data.get('target'),
            timestamp=timestamp
        )


class MessageBus:
    """
    Message bus for inter-agent communication using publish/subscribe pattern.
    Supports both synchronous and asynchronous messaging.
    """

    CACHE_PREFIX = "mkaguzi:message_bus:"

    @staticmethod
    def _message_ttl() -> int:
        """Read message_bus_ttl from Mkaguzi Settings (fallback 86400)."""
        try:
            from mkaguzi.utils.settings import get_cache_config
            return get_cache_config().get("message_bus_ttl", 86400)
        except Exception:
            return 86400

    def __init__(self):
        """Initialize the Message Bus"""
        self.subscribers = defaultdict(list)  # In-memory subscribers
        self.message_queues = defaultdict(queue.Queue)  # Per-agent message queues
        self.lock = threading.Lock()
        self.cache = frappe.cache()
        self._load_subscriptions()

    def subscribe(self, agent_id: str, message_types: List[str]) -> bool:
        """
        Subscribe an agent to message types

        Args:
            agent_id: Agent identifier
            message_types: List of message types to subscribe to

        Returns:
            True if successful
        """
        try:
            with self.lock:
                for message_type in message_types:
                    # Remove existing subscription if present
                    self.subscribers[message_type] = [
                        sub for sub in self.subscribers[message_type]
                        if sub != agent_id
                    ]
                    # Add subscription
                    self.subscribers[message_type].append(agent_id)

                # Persist subscriptions to cache
                self._persist_subscriptions()

            return True

        except Exception as e:
            frappe.log_error(f"Subscribe Error [{agent_id}]: {str(e)}", "Agent Message Bus")
            return False

    def unsubscribe(self, agent_id: str, message_types: Optional[List[str]] = None) -> bool:
        """
        Unsubscribe an agent from message types

        Args:
            agent_id: Agent identifier
            message_types: List of message types (if None, unsubscribe from all)

        Returns:
            True if successful
        """
        try:
            with self.lock:
                if message_types is None:
                    # Unsubscribe from all
                    for message_type in list(self.subscribers.keys()):
                        self.subscribers[message_type] = [
                            sub for sub in self.subscribers[message_type]
                            if sub != agent_id
                        ]
                else:
                    for message_type in message_types:
                        if message_type in self.subscribers:
                            self.subscribers[message_type] = [
                                sub for sub in self.subscribers[message_type]
                                if sub != agent_id
                            ]

                # Persist subscriptions to cache
                self._persist_subscriptions()

            return True

        except Exception as e:
            frappe.log_error(f"Unsubscribe Error [{agent_id}]: {str(e)}", "Agent Message Bus")
            return False

    def publish(self, message_type: str, data: Any, source: Optional[str] = None) -> bool:
        """
        Publish message to all subscribers

        Args:
            message_type: Type of message
            data: Message data
            source: Source agent ID

        Returns:
            True if successful
        """
        try:
            message = Message(
                message_type=message_type,
                data=data,
                source=source
            )

            with self.lock:
                subscribers = self.subscribers.get(message_type, [])

                # Queue message for each subscriber
                for subscriber_id in subscribers:
                    self.message_queues[subscriber_id].put(message)

                # Persist message to cache for durability
                self._persist_message(message)

            return True

        except Exception as e:
            frappe.log_error(f"Publish Error [{message_type}]: {str(e)}", "Agent Message Bus")
            return False

    def send_direct(self, target_agent_id: str, message_type: str, data: Any,
                   source: Optional[str] = None) -> bool:
        """
        Send message directly to a specific agent

        Args:
            target_agent_id: Target agent identifier
            message_type: Type of message
            data: Message data
            source: Source agent ID

        Returns:
            True if successful
        """
        try:
            message = Message(
                message_type=message_type,
                data=data,
                source=source,
                target=target_agent_id
            )

            with self.lock:
                # Queue message for target agent
                self.message_queues[target_agent_id].put(message)

                # Persist message to cache
                self._persist_message(message)

            return True

        except Exception as e:
            frappe.log_error(f"Send Direct Error [{target_agent_id}]: {str(e)}", "Agent Message Bus")
            return False

    def get_messages(self, agent_id: str, timeout: float = 0.1,
                    limit: int = 100) -> List[Message]:
        """
        Get messages for an agent from queue

        Args:
            agent_id: Agent identifier
            timeout: Queue timeout in seconds
            limit: Maximum number of messages to retrieve

        Returns:
            List of messages
        """
        try:
            messages = []

            for _ in range(limit):
                try:
                    message = self.message_queues[agent_id].get(timeout=timeout)
                    messages.append(message)
                except queue.Empty:
                    break

            return messages

        except Exception as e:
            frappe.log_error(f"Get Messages Error [{agent_id}]: {str(e)}", "Agent Message Bus")
            return []

    def get_subscribers(self, message_type: str) -> List[str]:
        """
        Get list of subscribers for a message type

        Args:
            message_type: Message type

        Returns:
            List of agent IDs
        """
        with self.lock:
            return self.subscribers.get(message_type, []).copy()

    def get_all_subscriptions(self) -> Dict[str, List[str]]:
        """
        Get all subscriptions

        Returns:
            Dictionary mapping message types to subscribers
        """
        with self.lock:
            return {k: v.copy() for k, v in self.subscribers.items()}

    def clear_queue(self, agent_id: str) -> bool:
        """
        Clear message queue for an agent

        Args:
            agent_id: Agent identifier

        Returns:
            True if successful
        """
        try:
            with self.lock:
                while not self.message_queues[agent_id].empty():
                    try:
                        self.message_queues[agent_id].get_nowait()
                    except queue.Empty:
                        break

            return True

        except Exception as e:
            frappe.log_error(f"Clear Queue Error [{agent_id}]: {str(e)}", "Agent Message Bus")
            return False

    def _persist_subscriptions(self) -> None:
        """Persist subscriptions to cache"""
        try:
            cache_key = f"{self.CACHE_PREFIX}subscriptions"
            self.cache.set(cache_key, json.dumps(self.subscribers), expiry=self._message_ttl())
        except Exception as e:
            frappe.log_error(f"Persist Subscriptions Error: {str(e)}", "Agent Message Bus")

    def _load_subscriptions(self) -> None:
        """Load subscriptions from cache"""
        try:
            cache_key = f"{self.CACHE_PREFIX}subscriptions"
            data = self.cache.get(cache_key)
            if data:
                self.subscribers = defaultdict(list, json.loads(data))
        except Exception as e:
            frappe.log_error(f"Load Subscriptions Error: {str(e)}", "Agent Message Bus")

    def _persist_message(self, message: Message) -> None:
        """Persist message to cache"""
        try:
            cache_key = f"{self.CACHE_PREFIX}message:{message.message_id}"
            self.cache.set(cache_key, json.dumps(message.to_dict()), expiry=self._message_ttl())
        except Exception as e:
            frappe.log_error(f"Persist Message Error: {str(e)}", "Agent Message Bus")
