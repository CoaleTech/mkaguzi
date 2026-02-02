# State Manager for Multi-Agent System
# =============================================================================
# Centralized state management for sharing data between agents

import frappe
from typing import Any, Optional, Dict
import json


class StateManager:
    """
    Centralized state management using Frappe cache for inter-agent communication
    and state persistence.
    """

    CACHE_PREFIX = "mkaguzi:agent_state:"
    DEFAULT_TTL = 3600  # 1 hour default TTL

    def __init__(self):
        """Initialize the State Manager"""
        self.cache = frappe.cache()

    def set_state(self, agent_id: str, key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
        """
        Set state value for an agent

        Args:
            agent_id: Agent identifier
            key: State key
            value: State value (will be JSON serialized)
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
        try:
            cache_key = f"{self.CACHE_PREFIX}{agent_id}:{key}"

            # Serialize value if it's not a string
            if not isinstance(value, str):
                value = json.dumps(value)

            self.cache.set(cache_key, value, expiry=ttl)
            return True

        except Exception as e:
            frappe.log_error(f"State Set Error [{agent_id}:{key}]: {str(e)}", "Agent State Manager")
            return False

    def get_state(self, agent_id: str, key: str, default: Any = None) -> Any:
        """
        Get state value for an agent

        Args:
            agent_id: Agent identifier
            key: State key
            default: Default value if key doesn't exist

        Returns:
            State value or default
        """
        try:
            cache_key = f"{self.CACHE_PREFIX}{agent_id}:{key}"
            value = self.cache.get(cache_key)

            if value is None:
                return default

            # Try to deserialize as JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value

        except Exception as e:
            frappe.log_error(f"State Get Error [{agent_id}:{key}]: {str(e)}", "Agent State Manager")
            return default

    def delete_state(self, agent_id: str, key: Optional[str] = None) -> bool:
        """
        Delete state for an agent

        Args:
            agent_id: Agent identifier
            key: State key (if None, deletes all state for agent)

        Returns:
            True if successful
        """
        try:
            if key:
                cache_key = f"{self.CACHE_PREFIX}{agent_id}:{key}"
                self.cache.delete(cache_key)
            else:
                # Delete all state for agent
                pattern = f"{self.CACHE_PREFIX}{agent_id}:*"
                self.cache.delete_keys(pattern)

            return True

        except Exception as e:
            frappe.log_error(f"State Delete Error [{agent_id}:{key}]: {str(e)}", "Agent State Manager")
            return False

    def get_all_agent_state(self, agent_id: str) -> Dict[str, Any]:
        """
        Get all state for an agent

        Args:
            agent_id: Agent identifier

        Returns:
            Dictionary of all state keys and values
        """
        try:
            # Get all keys for this agent
            pattern = f"{self.CACHE_PREFIX}{agent_id}:*"
            keys = self.cache.get_keys(pattern)

            state = {}
            for key in keys:
                # Extract the state key from the full cache key
                state_key = key.replace(f"{self.CACHE_PREFIX}{agent_id}:", "")
                state[state_key] = self.get_state(agent_id, state_key)

            return state

        except Exception as e:
            frappe.log_error(f"Get All State Error [{agent_id}]: {str(e)}", "Agent State Manager")
            return {}

    def increment_counter(self, agent_id: str, key: str, delta: int = 1) -> int:
        """
        Increment a counter value atomically

        Args:
            agent_id: Agent identifier
            key: Counter key
            delta: Increment amount

        Returns:
            New counter value
        """
        try:
            current = self.get_state(agent_id, key, 0)
            new_value = current + delta
            self.set_state(agent_id, key, new_value)
            return new_value

        except Exception as e:
            frappe.log_error(f"Counter Increment Error [{agent_id}:{key}]: {str(e)}", "Agent State Manager")
            return 0

    def list_agents(self) -> list:
        """
        List all agents that have state

        Returns:
            List of agent IDs
        """
        try:
            pattern = f"{self.CACHE_PREFIX}*"
            keys = self.cache.get_keys(pattern)

            # Extract unique agent IDs from keys
            agent_ids = set()
            for key in keys:
                # Extract agent ID from key
                parts = key.replace(self.CACHE_PREFIX, "").split(":")
                if parts:
                    agent_ids.add(parts[0])

            return list(agent_ids)

        except Exception as e:
            frappe.log_error(f"List Agents Error: {str(e)}", "Agent State Manager")
            return []

    def clear_agent_state(self, agent_id: str) -> bool:
        """
        Clear all state for an agent

        Args:
            agent_id: Agent identifier

        Returns:
            True if successful
        """
        return self.delete_state(agent_id)
