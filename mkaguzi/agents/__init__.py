# Mkaguzi Multi-Agent System
# =============================================================================
# This package provides intelligent, adaptive agents for audit automation

from .agent_base import AuditAgent
from .agent_manager import AgentManager
from .message_bus import MessageBus
from .state_manager import StateManager

__all__ = [
    'AuditAgent',
    'AgentManager',
    'MessageBus',
    'StateManager'
]

__version__ = '1.0.0'
