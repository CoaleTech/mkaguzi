# Agent Executor for Multi-Agent System
# =============================================================================
# Execute agent tasks using Frappe background job queue

import frappe
from typing import Any, Dict, Optional
from datetime import datetime
import traceback

from .agent_manager import get_agent_manager
from .agent_registry import AgentRegistry


class AgentExecutor:
    """
    Execute agent tasks using Frappe's background job queue.
    Provides integration between agents and Frappe's task system.
    """

    @staticmethod
    def execute_agent_task(agent_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task immediately (synchronous)

        Args:
            agent_id: Agent identifier
            task_data: Task data dictionary

        Returns:
            Execution result dictionary
        """
        agent_manager = get_agent_manager()
        agent = agent_manager.get_agent(agent_id)

        if not agent:
            return {
                'status': 'error',
                'error': f'Agent {agent_id} not found',
                'timestamp': datetime.now().isoformat()
            }

        # Check if agent is running
        if not agent.is_running():
            return {
                'status': 'error',
                'error': f'Agent {agent_id} is not running',
                'timestamp': datetime.now().isoformat()
            }

        try:
            # Execute the task
            start_time = datetime.now()
            result = agent.execute_task(task_data)
            end_time = datetime.now()

            # Calculate duration
            duration = (end_time - start_time).total_seconds()

            # Update agent stats
            agent.tasks_completed += 1

            # Log execution
            AgentExecutor._log_execution(
                agent_id=agent_id,
                task_type=task_data.get('task_type', 'unknown'),
                status='success',
                duration=duration,
                result=result
            )

            return {
                'status': 'success',
                'result': result,
                'duration_seconds': duration,
                'timestamp': end_time.isoformat()
            }

        except Exception as e:
            # Update agent stats
            agent.tasks_failed += 1

            # Log execution
            AgentExecutor._log_execution(
                agent_id=agent_id,
                task_type=task_data.get('task_type', 'unknown'),
                status='error',
                error=str(e),
                traceback=traceback.format_exc()
            )

            return {
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            }

    @staticmethod
    def enqueue_agent_task(agent_type: str, task_data: Dict[str, Any],
                          priority: str = 'normal') -> str:
        """
        Enqueue agent task for background execution

        Args:
            agent_type: Type of agent to execute
            task_data: Task data dictionary
            priority: Job priority (high, normal, low)

        Returns:
            Job ID
        """
        try:
            # For background execution, we'll spawn a new agent
            # The agent will handle the task and then terminate

            job_id = frappe.enqueue(
                'mkaguzi.agents.agent_executor.execute_background_task',
                agent_type=agent_type,
                task_data=task_data,
                queue='long' if priority == 'low' else 'short',
                timeout=task_data.get('timeout', 300),
                enqueue_after_commit=False
            )

            return job_id

        except Exception as e:
            frappe.log_error(f"Enqueue Agent Task Error: {str(e)}", "Agent Executor")
            raise

    @staticmethod
    def execute_background_task(agent_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task in background (spawns temporary agent)

        Args:
            agent_type: Type of agent to spawn
            task_data: Task data dictionary

        Returns:
            Execution result dictionary
        """
        agent_manager = get_agent_manager()
        agent = None

        try:
            # Spawn agent for this task
            agent = agent_manager.spawn_agent(agent_type)

            if not agent:
                return {
                    'status': 'error',
                    'error': f'Failed to spawn agent of type: {agent_type}'
                }

            # Execute task
            result = agent.execute_task(task_data)

            return {
                'status': 'success',
                'result': result
            }

        except Exception as e:
            frappe.log_error(
                f"Background Task Error [{agent_type}]: {str(e)}",
                "Agent Executor"
            )
            return {
                'status': 'error',
                'error': str(e)
            }

        finally:
            # Clean up agent
            if agent:
                agent_manager.terminate_agent(agent.id)

    @staticmethod
    def schedule_agent_task(agent_type: str, task_data: Dict[str, Any],
                           execute_at: datetime) -> str:
        """
        Schedule agent task for future execution

        Args:
            agent_type: Type of agent to execute
            task_data: Task data dictionary
            execute_at: When to execute the task

        Returns:
            Job ID
        """
        try:
            job_id = frappe.enqueue(
                'mkaguzi.agents.agent_executor.execute_background_task',
                agent_type=agent_type,
                task_data=task_data,
                execute_at=execute_at,
                queue='default'
            )

            return job_id

        except Exception as e:
            frappe.log_error(f"Schedule Agent Task Error: {str(e)}", "Agent Executor")
            raise

    @staticmethod
    def _log_execution(agent_id: str, task_type: str, status: str,
                      duration: Optional[float] = None,
                      result: Optional[Dict] = None,
                      error: Optional[str] = None,
                      traceback: Optional[str] = None) -> None:
        """
        Log agent execution to database

        Args:
            agent_id: Agent identifier
            task_type: Type of task executed
            status: Execution status
            duration: Duration in seconds
            result: Task result
            error: Error message if failed
            traceback: Error traceback if failed
        """
        try:
            if not frappe.db.table_exists('Agent Execution Log'):
                return

            log_entry = frappe.get_doc({
                'doctype': 'Agent Execution Log',
                'agent_id': agent_id,
                'task_type': task_type,
                'start_time': datetime.now() - duration if duration else datetime.now(),
                'end_time': datetime.now(),
                'duration_seconds': duration,
                'status': status.title(),
                'result_json': frappe.as_json(result) if result else None,
                'error_message': error,
                'input_data': frappe.as_json({'task_type': task_type})
            })

            log_entry.insert()
            frappe.db.commit()

        except Exception as e:
            frappe.logger().error(f"Agent Execution Log Error: {str(e)}")

    @staticmethod
    def get_execution_logs(agent_id: Optional[str] = None,
                          limit: int = 100) -> list:
        """
        Get agent execution logs

        Args:
            agent_id: Optional agent ID filter
            limit: Maximum number of logs to return

        Returns:
            List of execution log dictionaries
        """
        try:
            if not frappe.db.table_exists('Agent Execution Log'):
                return []

            filters = {}
            if agent_id:
                filters['agent_id'] = agent_id

            logs = frappe.get_all('Agent Execution Log',
                filters=filters,
                fields=['name', 'agent_id', 'task_type', 'start_time', 'end_time',
                       'duration_seconds', 'status', 'error_message'],
                order_by='creation desc',
                limit=limit
            )

            return logs

        except Exception as e:
            frappe.log_error(f"Get Execution Logs Error: {str(e)}", "Agent Executor")
            return []

    @staticmethod
    def get_execution_stats(agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get execution statistics

        Args:
            agent_id: Optional agent ID filter

        Returns:
            Statistics dictionary
        """
        try:
            if not frappe.db.table_exists('Agent Execution Log'):
                return {}

            filters = {}
            if agent_id:
                filters['agent_id'] = agent_id

            # Get counts
            total = frappe.db.count('Agent Execution Log', filters=filters)

            success_count = frappe.db.count('Agent Execution Log',
                filters={**filters, 'status': 'Success'})

            failed_count = frappe.db.count('Agent Execution Log',
                filters={**filters, 'status': 'Failed'})

            # Get average duration
            avg_duration = frappe.db.sql("""
                SELECT AVG(duration_seconds) as avg_duration
                FROM `tabAgent Execution Log`
                WHERE status = 'Success'
                AND (%s = '' OR agent_id = %s)
            """, (agent_id or '', agent_id or ''), as_dict=True)

            return {
                'total_executions': total,
                'successful': success_count,
                'failed': failed_count,
                'success_rate': round((success_count / total * 100) if total > 0 else 0, 2),
                'average_duration': round(avg_duration[0]['avg_duration'], 2) if avg_duration and avg_duration[0]['avg_duration'] else 0
            }

        except Exception as e:
            frappe.log_error(f"Get Execution Stats Error: {str(e)}", "Agent Executor")
            return {}
