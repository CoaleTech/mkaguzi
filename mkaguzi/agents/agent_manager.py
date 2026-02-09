# Agent Manager for Multi-Agent System
# =============================================================================
# Central manager for spawning, tracking, and terminating agents

import frappe
from typing import Any, Dict, List, Optional
from datetime import datetime
import threading

from .agent_base import AuditAgent
from .message_bus import MessageBus
from .state_manager import StateManager
from .agent_registry import AgentRegistry


class AgentManager:
    """
    Central manager for all agents. Handles agent lifecycle, coordination,
    and communication. Implements singleton pattern.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the Agent Manager"""
        # Prevent re-initialization
        if hasattr(self, '_initialized'):
            return

        self.agents: Dict[str, AuditAgent] = {}
        self.message_bus = MessageBus()
        self.state_manager = StateManager()
        self.registry = AgentRegistry()

        self._lock = threading.Lock()
        self._initialized = True

        frappe.logger().info("Agent Manager initialized")

    def spawn_agent(self, agent_type: str, config: Optional[Dict[str, Any]] = None,
                    agent_id: Optional[str] = None) -> Optional[AuditAgent]:
        """
        Create and start a new agent

        Args:
            agent_type: Type of agent to spawn (e.g., 'financial', 'risk')
            config: Agent configuration
            agent_id: Optional custom agent ID

        Returns:
            Agent instance if successful, None otherwise
        """
        try:
            # Get agent class from registry
            agent_class = self.registry.get_agent_class(agent_type)

            if not agent_class:
                frappe.throw(f"Unknown agent type: {agent_type}")

            # Merge with default config
            default_config = self.registry.get_default_config(agent_type)
            if default_config:
                merged_config = {**default_config, **(config or {})}
            else:
                merged_config = config or {}

            # Create agent instance
            agent = agent_class(agent_id=agent_id, config=merged_config)

            # Start the agent
            if not agent.start():
                frappe.throw(f"Failed to start agent: {agent.id}")

            # Register agent
            with self._lock:
                self.agents[agent.id] = agent

            # Log spawn event
            self._log_agent_event(agent.id, 'spawned', {
                'agent_type': agent_type,
                'config': merged_config
            })

            frappe.logger().info(f"Agent spawned: {agent.id} ({agent_type})")

            return agent

        except Exception as e:
            frappe.log_error(f"Spawn Agent Error [{agent_type}]: {str(e)}", "Agent Manager")
            return None

    def terminate_agent(self, agent_id: str) -> bool:
        """
        Stop and remove an agent

        Args:
            agent_id: Agent identifier

        Returns:
            True if successful
        """
        try:
            agent = self.agents.get(agent_id)

            if not agent:
                frappe.logger().warning(f"Agent not found: {agent_id}")
                return False

            # Stop the agent
            agent.stop()

            # Remove from registry
            with self._lock:
                self.agents.pop(agent_id, None)

            # Clear agent state
            self.state_manager.clear_agent_state(agent_id)

            # Log termination event
            self._log_agent_event(agent_id, 'terminated')

            frappe.logger().info(f"Agent terminated: {agent_id}")

            return True

        except Exception as e:
            frappe.log_error(f"Terminate Agent Error [{agent_id}]: {str(e)}", "Agent Manager")
            return False

    def get_agent(self, agent_id: str) -> Optional[AuditAgent]:
        """
        Get agent by ID

        Args:
            agent_id: Agent identifier

        Returns:
            Agent instance or None
        """
        return self.agents.get(agent_id)

    def list_agents(self, agent_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all agents, optionally filtered by type

        Args:
            agent_type: Optional agent type filter

        Returns:
            List of agent status dictionaries
        """
        agents = []

        with self._lock:
            for agent_id, agent in self.agents.items():
                if agent_type is None or agent.agent_type.lower() == agent_type.lower():
                    agents.append(agent.get_status())

        return agents

    def broadcast(self, message_type: str, data: Any, source: Optional[str] = None) -> bool:
        """
        Send message to all agents

        Args:
            message_type: Type of message
            data: Message data
            source: Source agent ID

        Returns:
            True if successful
        """
        try:
            return self.message_bus.publish(message_type, data, source)
        except Exception as e:
            frappe.log_error(f"Broadcast Error: {str(e)}", "Agent Manager")
            return False

    def get_agent_count(self) -> Dict[str, int]:
        """
        Get count of agents by type

        Returns:
            Dictionary mapping agent types to counts
        """
        counts = {}

        with self._lock:
            for agent in self.agents.values():
                agent_type = agent.agent_type.lower()
                counts[agent_type] = counts.get(agent_type, 0) + 1

        return counts

    def get_active_agents(self) -> List[str]:
        """
        Get list of active (running) agent IDs

        Returns:
            List of agent IDs
        """
        return [
            agent_id for agent_id, agent in self.agents.items()
            if agent.is_running()
        ]

    def stop_all_agents(self) -> int:
        """
        Stop all running agents

        Returns:
            Number of agents stopped
        """
        stopped = 0

        agent_ids = list(self.agents.keys())
        for agent_id in agent_ids:
            if self.terminate_agent(agent_id):
                stopped += 1

        return stopped

    def pause_all_agents(self) -> int:
        """
        Pause all running agents

        Returns:
            Number of agents paused
        """
        paused = 0

        with self._lock:
            for agent in self.agents.values():
                if agent.pause():
                    paused += 1

        return paused

    def resume_all_agents(self) -> int:
        """
        Resume all paused agents

        Returns:
            Number of agents resumed
        """
        resumed = 0

        with self._lock:
            for agent in self.agents.values():
                if agent.resume():
                    resumed += 1

        return resumed

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status

        Returns:
            System status dictionary
        """
        active_agents = self.get_active_agents()
        agent_counts = self.get_agent_count()

        return {
            'total_agents': len(self.agents),
            'active_agents': len(active_agents),
            'agent_counts': agent_counts,
            'message_bus_subscribers': self.message_bus.get_all_subscriptions(),
            'timestamp': datetime.now().isoformat()
        }

    def _log_agent_event(self, agent_id: str, event: str,
                        details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log agent lifecycle event

        Args:
            agent_id: Agent identifier
            event: Event type (spawned, terminated, etc.)
            details: Optional event details
        """
        try:
            # Check if Agent Execution Log doctype exists
            if frappe.db.table_exists('Agent Execution Log'):
                log_entry = {
                    'doctype': 'Agent Execution Log',
                    'agent_id': agent_id,
                    'agent_type': 'Unknown',
                    'task_type': event,
                    'task_name': event.replace('_', ' ').title(),
                    'start_time': datetime.now(),
                    'status': 'Pending',
                    'output_data': frappe.as_json(details) if details else None
                }

                try:
                    frappe.get_doc(log_entry).insert()
                    frappe.db.commit()
                except Exception:
                    # Log may fail if doctype doesn't have required fields
                    pass

        except Exception as e:
            frappe.logger().error(f"Agent Event Logging Error: {str(e)}")

    @staticmethod
    def start_manager():
        """
        Start the agent manager (for scheduler/external calls)

        Returns:
            AgentManager instance
        """
        manager = AgentManager()
        frappe.logger().info("Agent Manager started via static method")
        return manager

    @staticmethod
    def stop_manager():
        """
        Stop the agent manager and all agents

        Returns:
            Number of agents stopped
        """
        manager = AgentManager()
        stopped = manager.stop_all_agents()
        frappe.logger().info(f"Agent Manager stopped. Agents terminated: {stopped}")
        return stopped

    @staticmethod
    def get_manager() -> 'AgentManager':
        """
        Get the Agent Manager singleton instance

        Returns:
            AgentManager instance
        """
        return AgentManager()

    # Scheduled task methods
    @staticmethod
    def hourly_agent_health_check():
        """Hourly health check for all agents (scheduled task)"""
        try:
            frappe.logger().info("Running hourly agent health check")

            manager = AgentManager()
            status = manager.get_system_status()

            # Check for stuck agents
            for agent_status in manager.list_agents():
                if agent_status['state'] == 'error':
                    frappe.logger().error(f"Agent in error state: {agent_status['agent_id']}")

            return status

        except Exception as e:
            frappe.log_error(f"Agent Health Check Error: {str(e)}", "Agent Manager")
            return {'status': 'error', 'error': str(e)}

    @staticmethod
    def daily_agent_cleanup():
        """Daily cleanup of old agent state (scheduled task)"""
        try:
            frappe.logger().info("Running daily agent cleanup")

            manager = AgentManager()

            # Clean up state for terminated agents
            state_manager = StateManager()
            all_agents = state_manager.list_agents()

            active_agents = set(manager.agents.keys())
            cleaned = 0

            for agent_id in all_agents:
                if agent_id not in active_agents:
                    state_manager.clear_agent_state(agent_id)
                    cleaned += 1

            frappe.logger().info(f"Agent cleanup completed. Cleaned {cleaned} agents")

            return {'cleaned': cleaned}

        except Exception as e:
            frappe.log_error(f"Agent Cleanup Error: {str(e)}", "Agent Manager")
            return {'status': 'error', 'error': str(e)}


# Global instance
_agent_manager_instance = None


def get_agent_manager() -> AgentManager:
    """
    Get the global Agent Manager instance

    Returns:
        AgentManager instance
    """
    global _agent_manager_instance

    if _agent_manager_instance is None:
        _agent_manager_instance = AgentManager()

    return _agent_manager_instance


def hourly_agent_health_check():
    """Module-level wrapper for hourly health check (scheduled task)"""
    return AgentManager.hourly_agent_health_check()


def daily_agent_cleanup():
    """Module-level wrapper for daily cleanup (scheduled task)"""
    return AgentManager.daily_agent_cleanup()