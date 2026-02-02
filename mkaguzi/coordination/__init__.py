# Multi-Agent Coordination Layer
# =============================================================================
# This package provides coordination mechanisms for multi-agent workflows

from .workflow_engine import WorkflowEngine, WorkflowDefinition
from .task_scheduler import TaskScheduler
from .consensus_manager import ConsensusManager

__all__ = [
    'WorkflowEngine',
    'WorkflowDefinition',
    'TaskScheduler',
    'ConsensusManager'
]

__version__ = '1.0.0'
