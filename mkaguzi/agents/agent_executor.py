# Agent Executor for Multi-Agent System
# =============================================================================
# Execute agent tasks using Frappe background job queue

import frappe
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import traceback

from .agent_manager import get_agent_manager
from .agent_registry import AgentRegistry


class AgentExecutor:
    """
    Execute agent tasks using Frappe's background job queue.
    Provides integration between agents and Frappe's task system.
    """

    @staticmethod
    def _get_default_timeout() -> int:
        """Read default_agent_timeout from Mkaguzi Settings (fallback 300)."""
        try:
            from mkaguzi.utils.settings import get_agent_defaults
            return get_agent_defaults().get("timeout_seconds", 300)
        except Exception:
            return 300

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
                traceback_str=traceback.format_exc()
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
                timeout=task_data.get('timeout', AgentExecutor._get_default_timeout()),
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
        task_type = task_data.get('task_type', 'background_task')
        agent_id = f"{agent_type.lower()}_bg_{datetime.now().timestamp()}"
        duration = 0
        start_time = datetime.now()

        try:
            # Spawn agent for this task
            agent = agent_manager.spawn_agent(agent_type)

            if not agent:
                AgentExecutor._log_execution(agent_id, task_type, 'error', 
                                           error=f'Failed to spawn agent of type: {agent_type}')
                return {
                    'status': 'error',
                    'error': f'Failed to spawn agent of type: {agent_type}'
                }

            # Execute task
            result = agent.execute_task(task_data)
            duration = (datetime.now() - start_time).total_seconds()

            # Log execution
            AgentExecutor._log_execution(agent_id, task_type, 'success', 
                                       duration=duration, result=result)

            # Enqueue AI review if findings were generated
            if result and result.get('findings'):
                try:
                    frappe.enqueue(
                        'mkaguzi.agents.ai_reviewer.review_background_findings',
                        agent_type=agent_type,
                        findings=result.get('findings', []),
                        queue='long',
                        timeout=600,
                        enqueue_after_commit=True
                    )
                except Exception as ai_error:
                    frappe.logger().error(f"Failed to enqueue AI review for background task: {str(ai_error)}")

            return {
                'status': 'success',
                'result': result
            }

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            AgentExecutor._log_execution(agent_id, task_type, 'error', 
                                       duration=duration, error=str(e), 
                                       traceback_str=frappe.get_traceback())
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
                      traceback_str: Optional[str] = None) -> None:
        """
        Log agent execution to database

        Args:
            agent_id: Agent identifier
            task_type: Type of task executed
            status: Execution status
            duration: Duration in seconds
            result: Task result
            error: Error message if failed
            traceback_str: Error traceback if failed
        """
        try:
            # Determine agent type from agent_id
            agent_type = 'Unknown'
            if 'financial' in agent_id.lower():
                agent_type = 'Financial'
            elif 'risk' in agent_id.lower():
                agent_type = 'Risk'
            elif 'compliance' in agent_id.lower():
                agent_type = 'Compliance'
            elif 'discovery' in agent_id.lower():
                agent_type = 'Discovery'
            elif 'notification' in agent_id.lower():
                agent_type = 'Notification'

            # Map status values
            status_map = {
                'success': 'Completed',
                'error': 'Failed',
                'running': 'Running',
                'pending': 'Pending'
            }
            doc_status = status_map.get(status.lower(), status.title())

            log_entry = frappe.get_doc({
                'doctype': 'Agent Execution Log',
                'agent_id': agent_id,
                'agent_type': agent_type,
                'task_type': task_type,
                'task_name': task_type.replace('_', ' ').title(),
                'task_category': 'Agent Task',
                'execution_mode': 'Synchronous',
                'start_time': datetime.now() - timedelta(seconds=duration) if duration else datetime.now(),
                'end_time': datetime.now() if status != 'running' else None,
                'duration_seconds': duration,
                'status': doc_status,
                'result_json': frappe.as_json(result) if result else None,
                'output_data': frappe.as_json(result) if result else None,
                'error_occurred': 1 if status == 'error' else 0,
                'error_message': error,
                'error_traceback': traceback_str,
                'error_type': 'Exception' if error else None,
                'input_data': frappe.as_json({'task_type': task_type}),
                'triggered_by': frappe.session.user if frappe.session.user else 'System',
                'priority': 'Medium',
                'progress_percentage': 100 if status == 'success' else (0 if status == 'error' else 50)
            })

            # Handle findings from result
            if result and isinstance(result, dict):
                if result.get('findings'):
                    log_entry.findings_generated = 1
                    log_entry.total_findings = len(result.get('findings', []))

                    critical_count = sum(1 for f in result.get('findings', []) if f.get('severity') == 'Critical')
                    high_count = sum(1 for f in result.get('findings', []) if f.get('severity') == 'High')

                    log_entry.critical_findings = critical_count
                    log_entry.high_severity_findings = high_count

                    finding_ids = [f.get('name') for f in result.get('findings', []) if f.get('name')]
                    if finding_ids:
                        log_entry.finding_ids = ','.join(finding_ids)

                if result.get('records_processed'):
                    log_entry.records_processed = result.get('records_processed')

            log_entry.insert()
            frappe.db.commit()

            # Enqueue AI review if findings were generated
            if result and result.get('findings') and log_entry.finding_ids:
                try:
                    frappe.enqueue(
                        'mkaguzi.agents.ai_reviewer.review_agent_findings',
                        execution_log_name=log_entry.name,
                        queue='long',
                        timeout=600,
                        enqueue_after_commit=True
                    )
                except Exception as ai_error:
                    frappe.logger().error(f"Failed to enqueue AI review for {log_entry.name}: {str(ai_error)}")

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
            filters = {}
            if agent_id:
                filters['agent_id'] = agent_id

            logs = frappe.get_all('Agent Execution Log',
                filters=filters,
                fields=['name', 'agent_id', 'agent_type', 'task_type', 'task_name',
                       'start_time', 'end_time', 'duration_seconds', 'status',
                       'error_occurred', 'total_findings', 'critical_findings',
                       'records_processed'],
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
            filters = {}
            if agent_id:
                filters['agent_id'] = agent_id

            # Get counts
            total = frappe.db.count('Agent Execution Log', filters=filters)

            success_count = frappe.db.count('Agent Execution Log',
                filters={**filters, 'status': 'Completed'})

            failed_count = frappe.db.count('Agent Execution Log',
                filters={**filters, 'status': 'Failed'})

            running_count = frappe.db.count('Agent Execution Log',
                filters={**filters, 'status': 'Running'})

            # Get average duration
            avg_duration = frappe.db.sql("""
                SELECT AVG(duration_seconds) as avg_duration
                FROM `tabAgent Execution Log`
                WHERE status = 'Completed'
                AND (%s = '' OR agent_id = %s)
            """, (agent_id or '', agent_id or ''), as_dict=True)

            # Get total findings generated
            total_findings = frappe.db.sql("""
                SELECT SUM(total_findings) as findings
                FROM `tabAgent Execution Log`
                WHERE (%s = '' OR agent_id = %s)
            """, (agent_id or '', agent_id or ''), as_dict=True)

            return {
                'total_executions': total,
                'successful': success_count,
                'failed': failed_count,
                'running': running_count,
                'success_rate': round((success_count / total * 100) if total > 0 else 0, 2),
                'average_duration': round(avg_duration[0]['avg_duration'], 2) if avg_duration and avg_duration[0]['avg_duration'] else 0,
                'total_findings_generated': total_findings[0]['findings'] or 0
            }

        except Exception as e:
            frappe.log_error(f"Get Execution Stats Error: {str(e)}", "Agent Executor")
            return {}
