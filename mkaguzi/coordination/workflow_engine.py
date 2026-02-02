# Workflow Engine for Multi-Agent System
# =============================================================================
# Orchestrates multi-agent workflows for complex audits

import frappe
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import asyncio
import threading
from enum import Enum

from ..agents.agent_manager import get_agent_manager
from ..agents.message_bus import MessageBus, Message


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class StepStatus(Enum):
    """Step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStep:
    """A single step in a workflow"""

    def __init__(self, step_id: str, agent_type: str, action: str,
                 input_data: Optional[Dict[str, Any]] = None,
                 depends_on: Optional[List[str]] = None,
                 timeout: int = 300,
                 retry_count: int = 0,
                 parallel: bool = False):
        self.step_id = step_id
        self.agent_type = agent_type
        self.action = action
        self.input_data = input_data or {}
        self.depends_on = depends_on or []
        self.timeout = timeout
        self.retry_count = retry_count
        self.parallel = parallel
        self.status = StepStatus.PENDING
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary"""
        return {
            'step_id': self.step_id,
            'agent_type': self.agent_type,
            'action': self.action,
            'status': self.status.value,
            'result': self.result,
            'error': str(self.error) if self.error else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class WorkflowDefinition:
    """Definition of a workflow with steps"""

    def __init__(self, workflow_id: str, name: str,
                 description: Optional[str] = None):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.steps: Dict[str, WorkflowStep] = {}
        self.created_at = datetime.now()

    def add_step(self, step: WorkflowStep) -> 'WorkflowDefinition':
        """Add a step to the workflow"""
        self.steps[step.step_id] = step
        return self

    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get a step by ID"""
        return self.steps.get(step_id)

    def get_ready_steps(self) -> List[WorkflowStep]:
        """Get steps that are ready to execute (dependencies met)"""
        ready_steps = []

        for step in self.steps.values():
            if step.status != StepStatus.PENDING:
                continue

            # Check if all dependencies are completed
            dependencies_met = all(
                self.steps[dep_id].status == StepStatus.COMPLETED
                for dep_id in step.depends_on
                if dep_id in self.steps
            )

            if dependencies_met:
                ready_steps.append(step)

        return ready_steps

    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary"""
        return {
            'workflow_id': self.workflow_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'steps': {k: v.to_dict() for k, v in self.steps.items()}
        }


class WorkflowEngine:
    """
    Orchestrates multi-agent workflows with parallel and sequential execution.
    Supports error handling, rollback, and progress tracking.
    """

    def __init__(self):
        """Initialize the Workflow Engine"""
        self.agent_manager = get_agent_manager()
        self.message_bus = MessageBus()
        self.active_workflows: Dict[str, WorkflowDefinition] = {}
        self.workflow_status: Dict[str, WorkflowStatus] = {}
        self.workflow_results: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def create_workflow(self, workflow_id: str, name: str,
                       description: Optional[str] = None) -> WorkflowDefinition:
        """
        Create a new workflow definition

        Args:
            workflow_id: Unique workflow identifier
            name: Workflow name
            description: Optional description

        Returns:
            WorkflowDefinition object
        """
        workflow = WorkflowDefinition(workflow_id, name, description)

        with self.lock:
            self.active_workflows[workflow_id] = workflow
            self.workflow_status[workflow_id] = WorkflowStatus.PENDING

        return workflow

    def execute_workflow(self, workflow_id: str,
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a workflow

        Args:
            workflow_id: Workflow identifier
            context: Optional execution context

        Returns:
            Execution results dictionary
        """
        workflow = self.active_workflows.get(workflow_id)

        if not workflow:
            return {
                'status': 'error',
                'error': f'Workflow {workflow_id} not found'
            }

        try:
            with self.lock:
                self.workflow_status[workflow_id] = WorkflowStatus.RUNNING

            results = {
                'workflow_id': workflow_id,
                'name': workflow.name,
                'started_at': datetime.now().isoformat(),
                'steps': {},
                'summary': {
                    'total': len(workflow.steps),
                    'completed': 0,
                    'failed': 0,
                    'skipped': 0
                }
            }

            # Execute steps in dependency order
            while True:
                ready_steps = workflow.get_ready_steps()

                if not ready_steps:
                    # Check if any steps are still pending (circular dependency or failed dependency)
                    pending_steps = [
                        s for s in workflow.steps.values()
                        if s.status == StepStatus.PENDING
                    ]

                    if pending_steps:
                        # Has unmet dependencies - might be circular or failed
                        for step in pending_steps:
                            step.status = StepStatus.SKIPPED
                            results['summary']['skipped'] += 1
                    break

                # Group parallel and sequential steps
                parallel_steps = [s for s in ready_steps if s.parallel]
                sequential_steps = [s for s in ready_steps if not s.parallel]

                # Execute parallel steps together
                if parallel_steps:
                    parallel_results = self._execute_parallel_steps(parallel_steps, context)
                    for step_id, result in parallel_results.items():
                        workflow.steps[step_id].result = result
                        results['steps'][step_id] = result

                        if result['status'] == 'completed':
                            workflow.steps[step_id].status = StepStatus.COMPLETED
                            results['summary']['completed'] += 1
                        else:
                            workflow.steps[step_id].status = StepStatus.FAILED
                            results['summary']['failed'] += 1

                # Execute sequential steps one by one
                for step in sequential_steps:
                    result = self._execute_step(step, context)
                    step.result = result
                    results['steps'][step.step_id] = result

                    if result['status'] == 'completed':
                        step.status = StepStatus.COMPLETED
                        results['summary']['completed'] += 1
                    else:
                        step.status = StepStatus.FAILED
                        results['summary']['failed'] += 1
                        # Stop sequential execution on failure
                        break

            # Determine final workflow status
            completed_at = datetime.now()
            results['completed_at'] = completed_at.isoformat()

            if results['summary']['failed'] > 0:
                with self.lock:
                    self.workflow_status[workflow_id] = WorkflowStatus.FAILED
                results['status'] = 'failed'
            else:
                with self.lock:
                    self.workflow_status[workflow_id] = WorkflowStatus.COMPLETED
                results['status'] = 'completed'

            self.workflow_results[workflow_id] = results

            return results

        except Exception as e:
            frappe.log_error(
                f"Workflow Execution Error [{workflow_id}]: {str(e)}",
                "Workflow Engine"
            )

            with self.lock:
                self.workflow_status[workflow_id] = WorkflowStatus.FAILED

            return {
                'workflow_id': workflow_id,
                'status': 'error',
                'error': str(e)
            }

    def _execute_step(self, step: WorkflowStep,
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a single workflow step

        Args:
            step: WorkflowStep to execute
            context: Execution context

        Returns:
            Step result dictionary
        """
        try:
            step.status = StepStatus.RUNNING
            step.started_at = datetime.now()

            # Spawn agent for this step
            agent = self.agent_manager.spawn_agent(
                step.agent_type,
                config={'timeout': step.timeout}
            )

            if not agent:
                return {
                    'step_id': step.step_id,
                    'status': 'failed',
                    'error': f'Failed to spawn agent of type: {step.agent_type}'
                }

            # Prepare task data
            task_data = {
                'task_type': step.action,
                **step.input_data
            }

            if context:
                task_data['context'] = context

            # Execute task
            result = agent.execute_task(task_data)

            # Clean up agent
            self.agent_manager.terminate_agent(agent.id)

            step.completed_at = datetime.now()

            return {
                'step_id': step.step_id,
                'status': 'completed',
                'result': result,
                'duration_seconds': (step.completed_at - step.started_at).total_seconds()
            }

        except Exception as e:
            step.error = str(e)
            step.completed_at = datetime.now()

            return {
                'step_id': step.step_id,
                'status': 'failed',
                'error': str(e),
                'duration_seconds': (step.completed_at - step.started_at).total_seconds() if step.started_at else 0
            }

    def _execute_parallel_steps(self, steps: List[WorkflowStep],
                                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute multiple steps in parallel

        Args:
            steps: List of WorkflowSteps to execute
            context: Execution context

        Returns:
            Dictionary mapping step IDs to results
        """
        results = {}
        threads = []

        def execute_step_wrapper(step):
            results[step.step_id] = self._execute_step(step, context)

        # Start all steps
        for step in steps:
            thread = threading.Thread(target=execute_step_wrapper, args=(step,))
            thread.start()
            threads.append(thread)

        # Wait for all to complete
        for thread in threads:
            thread.join()

        return results

    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowStatus]:
        """
        Get the status of a workflow

        Args:
            workflow_id: Workflow identifier

        Returns:
            WorkflowStatus or None
        """
        return self.workflow_status.get(workflow_id)

    def get_workflow_results(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the results of a workflow

        Args:
            workflow_id: Workflow identifier

        Returns:
            Results dictionary or None
        """
        return self.workflow_results.get(workflow_id)

    def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Cancel a running workflow

        Args:
            workflow_id: Workflow identifier

        Returns:
            True if successful
        """
        with self.lock:
            if self.workflow_status.get(workflow_id) in [WorkflowStatus.RUNNING, WorkflowStatus.PENDING]:
                self.workflow_status[workflow_id] = WorkflowStatus.CANCELLED
                return True

        return False

    def pause_workflow(self, workflow_id: str) -> bool:
        """
        Pause a running workflow

        Args:
            workflow_id: Workflow identifier

        Returns:
            True if successful
        """
        with self.lock:
            if self.workflow_status.get(workflow_id) == WorkflowStatus.RUNNING:
                self.workflow_status[workflow_id] = WorkflowStatus.PAUSED
                return True

        return False

    def resume_workflow(self, workflow_id: str) -> bool:
        """
        Resume a paused workflow

        Args:
            workflow_id: Workflow identifier

        Returns:
            True if successful
        """
        with self.lock:
            if self.workflow_status.get(workflow_id) == WorkflowStatus.PAUSED:
                self.workflow_status[workflow_id] = WorkflowStatus.RUNNING
                return True

        return False

    def cleanup_workflow(self, workflow_id: str) -> bool:
        """
        Clean up a completed workflow from memory

        Args:
            workflow_id: Workflow identifier

        Returns:
            True if successful
        """
        with self.lock:
            self.active_workflows.pop(workflow_id, None)
            self.workflow_results.pop(workflow_id, None)

            status = self.workflow_status.get(workflow_id)
            if status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                self.workflow_status.pop(workflow_id, None)
                return True

        return False

    def get_active_workflows(self) -> List[str]:
        """
        Get list of active workflow IDs

        Returns:
            List of workflow IDs
        """
        with self.lock:
            return [
                wf_id for wf_id, status in self.workflow_status.items()
                if status in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]
            ]


# Predefined workflow templates

def create_comprehensive_audit_workflow(workflow_id: str) -> WorkflowDefinition:
    """
    Create a comprehensive audit workflow template

    Args:
        workflow_id: Unique workflow identifier

    Returns:
        WorkflowDefinition for comprehensive audit
    """
    engine = WorkflowEngine()
    workflow = engine.create_workflow(
        workflow_id,
        "Comprehensive Audit",
        "Multi-agent comprehensive audit workflow"
    )

    # Step 1: Discovery agent scans doctypes
    workflow.add_step(WorkflowStep(
        step_id='discovery',
        agent_type='discovery',
        action='discover_doctypes',
        parallel=False
    ))

    # Step 2: Risk agent predicts high-risk areas (depends on discovery)
    workflow.add_step(WorkflowStep(
        step_id='risk_assessment',
        agent_type='risk',
        action='assess_risks',
        depends_on=['discovery'],
        parallel=False
    ))

    # Step 3a: Financial agent audits (depends on risk assessment)
    workflow.add_step(WorkflowStep(
        step_id='financial_audit',
        agent_type='financial',
        action='audit_financial',
        depends_on=['risk_assessment'],
        parallel=True
    ))

    # Step 3b: HR agent audits (depends on risk assessment, parallel with financial)
    workflow.add_step(WorkflowStep(
        step_id='hr_audit',
        agent_type='hr',
        action='audit_hr',
        depends_on=['risk_assessment'],
        parallel=True
    ))

    # Step 4: Compliance agent verifies (depends on both audits)
    workflow.add_step(WorkflowStep(
        step_id='compliance_check',
        agent_type='compliance',
        action='verify_compliance',
        depends_on=['financial_audit', 'hr_audit'],
        parallel=False
    ))

    return workflow


def create_risk_assessment_workflow(workflow_id: str) -> WorkflowDefinition:
    """
    Create a risk assessment workflow template

    Args:
        workflow_id: Unique workflow identifier

    Returns:
        WorkflowDefinition for risk assessment
    """
    engine = WorkflowEngine()
    workflow = engine.create_workflow(
        workflow_id,
        "Risk Assessment",
        "Multi-module risk assessment workflow"
    )

    # Step 1: Aggregate data from all modules (parallel)
    workflow.add_step(WorkflowStep(
        step_id='financial_risk',
        agent_type='risk',
        action='assess_financial_risk',
        input_data={'module': 'financial'},
        parallel=True
    ))

    workflow.add_step(WorkflowStep(
        step_id='hr_risk',
        agent_type='risk',
        action='assess_hr_risk',
        input_data={'module': 'hr'},
        parallel=True
    ))

    workflow.add_step(WorkflowStep(
        step_id='inventory_risk',
        agent_type='risk',
        action='assess_inventory_risk',
        input_data={'module': 'inventory'},
        parallel=True
    ))

    # Step 2: Aggregate and analyze (depends on all risk assessments)
    workflow.add_step(WorkflowStep(
        step_id='aggregate_risks',
        agent_type='risk',
        action='aggregate_risks',
        depends_on=['financial_risk', 'hr_risk', 'inventory_risk'],
        parallel=False
    ))

    return workflow
