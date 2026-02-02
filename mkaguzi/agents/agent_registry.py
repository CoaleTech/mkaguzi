# Agent Registry for Multi-Agent System
# =============================================================================
# Registry for discovering and managing available agent types

import frappe
from typing import Any, Dict, List, Optional, Type
import importlib


class AgentRegistry:
    """
    Registry for discovering available agent types and their configurations.
    Allows dynamic agent discovery and instantiation.
    """

    # Built-in agent registry
    _registry = {
        'financial': {
            'class_path': 'mkaguzi.agents.financial_agent.FinancialAgent',
            'description': 'Financial transaction analysis and fraud detection',
            'category': 'audit',
            'default_config': {
                'max_batch_size': 1000,
                'timeout_seconds': 300,
                'retry_count': 3,
                'log_level': 'INFO'
            }
        },
        'risk': {
            'class_path': 'mkaguzi.agents.risk_agent.RiskAgent',
            'description': 'Predictive risk assessment and threshold adjustment',
            'category': 'analytics',
            'default_config': {
                'prediction_horizon_days': 30,
                'threshold_sensitivity': 0.5,
                'min_data_points': 100,
                'log_level': 'INFO'
            }
        },
        'compliance': {
            'class_path': 'mkaguzi.agents.compliance_agent.ComplianceAgent',
            'description': 'Regulatory compliance verification and gap analysis',
            'category': 'compliance',
            'default_config': {
                'auto_update_checks': True,
                'regulatory_sources': [],
                'severity_threshold': 'medium',
                'log_level': 'INFO'
            }
        },
        'discovery': {
            'class_path': 'mkaguzi.agents.discovery_agent.DiscoveryAgent',
            'description': 'Automatic doctype discovery and catalog updates',
            'category': 'discovery',
            'default_config': {
                'scan_interval_hours': 24,
                'auto_update_catalog': True,
                'detect_schema_changes': True,
                'log_level': 'INFO'
            }
        },
        'notification': {
            'class_path': 'mkaguzi.agents.notification_agent.NotificationAgent',
            'description': 'Intelligent alerting and notification management',
            'category': 'notification',
            'default_config': {
                'aggregation_window_minutes': 15,
                'max_digest_size': 50,
                'escalation_enabled': True,
                'log_level': 'INFO'
            }
        }
    }

    @classmethod
    def register(cls, agent_type: str, class_path: str, description: str,
                category: str, default_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a new agent type

        Args:
            agent_type: Agent type identifier
            class_path: Full Python path to agent class
            description: Agent description
            category: Agent category
            default_config: Default configuration

        Returns:
            True if successful
        """
        try:
            cls._registry[agent_type] = {
                'class_path': class_path,
                'description': description,
                'category': category,
                'default_config': default_config or {}
            }

            frappe.logger().info(f"Registered agent type: {agent_type}")
            return True

        except Exception as e:
            frappe.log_error(f"Register Agent Error [{agent_type}]: {str(e)}", "Agent Registry")
            return False

    @classmethod
    def unregister(cls, agent_type: str) -> bool:
        """
        Unregister an agent type

        Args:
            agent_type: Agent type identifier

        Returns:
            True if successful
        """
        if agent_type in cls._registry:
            del cls._registry[agent_type]
            frappe.logger().info(f"Unregistered agent type: {agent_type}")
            return True

        return False

    @classmethod
    def get_agent_class(cls, agent_type: str) -> Optional[Type]:
        """
        Get agent class by type (imports and returns the class)

        Args:
            agent_type: Agent type identifier

        Returns:
            Agent class or None
        """
        try:
            if agent_type not in cls._registry:
                return None

            class_path = cls._registry[agent_type]['class_path']

            # Split module path and class name
            parts = class_path.rsplit('.', 1)
            if len(parts) != 2:
                return None

            module_path, class_name = parts

            # Import module
            module = importlib.import_module(module_path)

            # Get class
            agent_class = getattr(module, class_name, None)

            return agent_class

        except Exception as e:
            frappe.log_error(f"Get Agent Class Error [{agent_type}]: {str(e)}", "Agent Registry")
            return None

    @classmethod
    def get_default_config(cls, agent_type: str) -> Optional[Dict[str, Any]]:
        """
        Get default configuration for agent type

        Args:
            agent_type: Agent type identifier

        Returns:
            Default configuration or None
        """
        agent_info = cls._registry.get(agent_type)
        return agent_info.get('default_config') if agent_info else None

    @classmethod
    def list_agents(cls, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all registered agent types

        Args:
            category: Optional category filter

        Returns:
            List of agent information dictionaries
        """
        agents = []

        for agent_type, info in cls._registry.items():
            if category is None or info.get('category') == category:
                agents.append({
                    'agent_type': agent_type,
                    'description': info.get('description'),
                    'category': info.get('category'),
                    'class_path': info.get('class_path')
                })

        return agents

    @classmethod
    def get_agent_info(cls, agent_type: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an agent type

        Args:
            agent_type: Agent type identifier

        Returns:
            Agent information or None
        """
        return cls._registry.get(agent_type)

    @classmethod
    def agent_exists(cls, agent_type: str) -> bool:
        """
        Check if agent type is registered

        Args:
            agent_type: Agent type identifier

        Returns:
            True if agent type exists
        """
        return agent_type in cls._registry

    @classmethod
    def get_categories(cls) -> List[str]:
        """
        Get list of all agent categories

        Returns:
            List of category names
        """
        categories = set()

        for info in cls._registry.values():
            category = info.get('category')
            if category:
                categories.add(category)

        return sorted(list(categories))

    @classmethod
    def load_from_db(cls) -> None:
        """
        Load agent configurations from database
        """
        try:
            if not frappe.db.table_exists('Agent Configuration'):
                return

            configs = frappe.get_all('Agent Configuration',
                filters={'enabled': 1},
                fields=['agent_type', 'config_json']
            )

            for config in configs:
                agent_type = config['agent_type']
                if agent_type in cls._registry:
                    try:
                        custom_config = frappe.parse_json(config['config_json'])
                        cls._registry[agent_type]['default_config'].update(custom_config)
                    except Exception:
                        pass

        except Exception as e:
            frappe.log_error(f"Load from DB Error: {str(e)}", "Agent Registry")
